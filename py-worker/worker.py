"""Worker Python da demo: WebSocket, decisoes concorrentes e rastreio serial."""

from __future__ import annotations

import sys

# Executar este arquivo tambem nao deixa __pycache__ no diretorio compartilhado.
sys.dont_write_bytecode = True

import asyncio
import ctypes
import gc
from dataclasses import dataclass, field
import json
from pathlib import Path
import time

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from deepseek import DeepSeekClient, cost_usd, verdict


def memoria_mb() -> float | None:
    """Memoria residente deste processo em MB (working set no Windows, RSS no resto)."""
    try:
        import psutil
        return round(psutil.Process().memory_info().rss / 1048576, 1)
    except ImportError:
        pass
    if sys.platform == "win32":
        class Counters(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_uint32), ("PageFaultCount", ctypes.c_uint32),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        counters = Counters(cb=ctypes.sizeof(Counters))
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return round(counters.WorkingSetSize / 1048576, 1)
        return None
    try:
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    except Exception:
        return None
from trace import Graph, rust_round

WS_URL = "ws://127.0.0.1:8080/ws/worker"
CONCORRENCIA = 8
RECONNECT_SECONDS = 2.0


def parse_event(raw: str | bytes) -> dict:
    try:
        event = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError("evento WebSocket: JSON invalido") from exc
    if not isinstance(event, dict) or not isinstance(event.get("type"), str):
        raise ValueError("evento WebSocket deve ser objeto com campo type")
    required = {
        "hello": {"data_dir": str},
        "run": {"run_id": int, "total": int},
        "reset": {},
        "message": {"run_id": int, "id": int, "ts": int,
                    "remetente": str, "texto": str, "chave": str},
    }.get(event["type"], {})
    for name, kind in required.items():
        value = event.get(name)
        if type(value) is not kind or (kind is int and value < 0):
            raise ValueError(f"evento {event['type']}: campo {name} ausente ou invalido")
    if event["type"] == "hello" and not event["data_dir"]:
        raise ValueError("evento hello: data_dir vazio")
    return event


def percentil(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[round(p / 100.0 * (len(ordered) - 1))]


@dataclass
class Run:
    run_id: int
    total: int
    started: float = field(default_factory=time.perf_counter)
    seen: set[int] = field(default_factory=set)
    processed: int = 0
    golpes: int = 0
    erros: int = 0
    decision_ms: list[float] = field(default_factory=list)
    trace_ms: list[float] = field(default_factory=list)
    cost: float = 0.0
    done: bool = False

    def totals(self) -> dict:
        return {
            "messages": self.processed, "golpes": self.golpes, "erros": self.erros,
            "decision_p50_ms": percentil(self.decision_ms, 50),
            "decision_p95_ms": percentil(self.decision_ms, 95),
            "trace_p50_ms": percentil(self.trace_ms, 50),
            "trace_p95_ms": percentil(self.trace_ms, 95),
            "cost_usd": self.cost,
            "total_ms": (time.perf_counter() - self.started) * 1000.0,
        }


class Worker:
    def __init__(self, client: DeepSeekClient, url: str = WS_URL):
        self.client = client
        self.url = url
        self.ws = None
        self.graph = None
        self.chaves = {}
        self.load_ms = 0.0
        self.memory_mb = None
        self.model = None
        self.run: Run | None = None
        self.sem = asyncio.Semaphore(CONCORRENCIA)
        self.pace_ms = 0  # pausa por mensagem (ritmo narrado); 0 = normal
        self.trace_lock = asyncio.Lock()
        self.send_lock = asyncio.Lock()
        self.tasks: set[asyncio.Task] = set()

    async def emit(self, event: dict, run: Run | None = None) -> bool:
        async with self.send_lock:
            if self.ws is None or (run is not None and self.run is not run):
                return False
            payload = dict(event, side="python", run_id=(run or self.run).run_id
                           if (run or self.run) is not None else None)
            try:
                await self.ws.send(json.dumps(payload, ensure_ascii=False, allow_nan=False))
            except (ConnectionClosed, OSError):
                self.run = None
                self.ws = None
                return False
            detail = payload.get("state", payload.get("verdict", ""))
            print(f"python {payload['type']} run={payload['run_id']} "
                  f"id={payload.get('id', '-')} {detail}", flush=True)
            return True

    @staticmethod
    def load_data(data_dir: str):
        directory = Path(data_dir)
        started = time.perf_counter()
        graph = Graph.load(directory)
        load_ms = (time.perf_counter() - started) * 1000.0
        chaves = json.loads((directory / "chaves.json").read_text(encoding="utf-8"))
        gc.collect()
        return graph, chaves, load_ms, memoria_mb()

    async def hello(self, event: dict) -> None:
        if self.graph is None or self.model is None:
            await self.emit({"type": "status", "state": "loading"})
            try:
                if self.graph is None:
                    self.graph, self.chaves, self.load_ms, self.memory_mb = await asyncio.to_thread(
                        self.load_data, event["data_dir"])
                if self.model is None:
                    async with self.sem:
                        warmup = await self.client.classificar("teste", "Oi, tudo bem? Aquecimento.")
                    self.model = warmup["model"]
            except Exception as exc:
                await self.emit({"type": "error", "message": f"inicializacao: {exc}"})
                raise  # Reconectar e tentar de novo; preservar o grafo ja carregado.
        await self.emit({"type": "status", "state": "ready", "nodes": self.graph.n,
                         "edges": self.graph.n_edges, "load_ms": self.load_ms,
                         "memory_mb": self.memory_mb, "model": self.model})

    async def handle_raw(self, raw: str | bytes) -> None:
        try:
            event = parse_event(raw)
        except ValueError as exc:
            # Um message malformado tambem conclui sua unidade do run, se seu
            # id for identificavel. Assim um erro de entrada nao impede done.
            try:
                bad = json.loads(raw)
            except (ValueError, TypeError):
                bad = None
            run = self.run
            if isinstance(bad, dict) and bad.get("type") == "message":
                if run is None or bad.get("run_id") != run.run_id:
                    return
                mid = bad.get("id")
                if type(mid) is int and mid >= 0 and not run.done and mid not in run.seen:
                    run.seen.add(mid)
                    run.erros += 1
                    await self.emit({"type": "error", "id": mid, "message": str(exc)}, run)
                    await self.finish_message(run)
                    return
            await self.emit({"type": "error", "message": str(exc)})
            return
        await self.handle_event(event)

    async def handle_event(self, event: dict) -> None:
        kind = event["type"]
        if kind == "hello":
            await self.hello(event)
        elif kind == "reset":
            # Nao cancelar to_thread: a thread continuaria enquanto o lock
            # seria liberado. Invalidar a identidade descarta seus resultados.
            self.run = None
        elif kind == "stop":
            self.run = None
        elif kind == "pace":
            # Troca de ritmo no meio da corrida; vale a partir da proxima mensagem.
            self.pace_ms = int(event.get("ms") or 0)
        elif kind == "run":
            # Concorrencia por execucao: 1 nos modos passo a passo, 8 na rajada (igual ao lado Rust).
            self.sem = asyncio.Semaphore(int(event.get("concurrency") or CONCORRENCIA))
            self.pace_ms = int(event.get("pace_ms") or 0)
            self.run = Run(event["run_id"], event["total"])
            await self.maybe_done(self.run)
        elif kind == "message":
            run = self.run
            if (run is None or event["run_id"] != run.run_id or run.done
                    or event["id"] in run.seen):
                return
            run.seen.add(event["id"])
            task = asyncio.create_task(self.process_message(event, run))
            self.tasks.add(task)
            task.add_done_callback(self.task_finished)

    def task_finished(self, task: asyncio.Task) -> None:
        self.tasks.discard(task)
        if not task.cancelled() and (exc := task.exception()) is not None:
            print(f"python tarefa: {exc}", file=sys.stderr, flush=True)

    def trace_for_message(self, no: int, t0: int) -> dict:
        started = time.perf_counter()
        result = self.graph.trace(no, t0)
        latency_ms = (time.perf_counter() - started) * 1000.0
        # Desenho, arredondamento e espera do lock ficam fora da medicao.
        nodes, edges = result.para_desenho()
        return {
            "latency_ms": latency_ms, "visitados": result.visitados,
            "arestas_sub": result.arestas_sub, "laranjas": result.laranjas,
            "saque": result.saque,
            "nodes": [[v, p, rust_round(s, 3)] for v, p, s in nodes],
            "edges": edges,
        }

    async def process_message(self, message: dict, run: Run) -> None:
        try:
            async with self.sem:
                if self.run is not run:
                    return
                decision = await self.client.classificar(message["remetente"], message["texto"])
                if self.run is not run:
                    return
                result_verdict = verdict(decision["golpe"])
                cost = cost_usd(decision["tokens_in"], decision["tokens_out"])
                run.decision_ms.append(decision["latency_ms"])
                run.cost += cost
                if result_verdict == "golpe":
                    run.golpes += 1
                sent = await self.emit(dict(decision, type="decision", id=message["id"],
                                            verdict=result_verdict, cost_usd=cost), run)
                # Ritmo narrado: segura a vez antes da proxima mensagem deste lado (igual ao Rust).
                if self.pace_ms > 0:
                    await asyncio.sleep(self.pace_ms / 1000.0)
            if not sent or result_verdict != "golpe":
                return
            async with self.trace_lock:
                if self.run is not run:
                    return
                if self.graph is None:
                    raise ValueError("grafo ainda nao carregado")
                if message["chave"] not in self.chaves:
                    raise ValueError(f"chave desconhecida: {message['chave']}")
                result = await asyncio.to_thread(
                    self.trace_for_message, self.chaves[message["chave"]], message["ts"])
            if self.run is not run:
                return
            run.trace_ms.append(result["latency_ms"])
            await self.emit(dict(result, type="trace", id=message["id"], chave=message["chave"]), run)
        except Exception as exc:
            if self.run is run:
                run.erros += 1
                await self.emit({"type": "error", "id": message["id"], "message": str(exc)}, run)
        finally:
            await self.finish_message(run)

    async def finish_message(self, run: Run) -> None:
        if self.run is run:
            run.processed += 1
            await self.maybe_done(run)

    async def maybe_done(self, run: Run) -> None:
        if self.run is run and run.processed == run.total and not run.done:
            run.done = True
            await self.emit({"type": "done", "totals": run.totals()}, run)

    async def serve_forever(self) -> None:
        try:
            while True:
                try:
                    async with connect(self.url, proxy=None, open_timeout=10) as ws:
                        self.ws = ws
                        async for raw in ws:
                            await self.handle_raw(raw)
                except Exception as exc:
                    print(f"python conexao: {exc}; nova tentativa em 2 s", file=sys.stderr, flush=True)
                finally:
                    self.run = None
                    self.ws = None
                await asyncio.sleep(RECONNECT_SECONDS)
        finally:
            # So encerrar tarefas quando o proprio worker termina, nunca no reset.
            tasks = list(self.tasks)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


async def main() -> None:
    async with DeepSeekClient() as client:
        await Worker(client).serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
