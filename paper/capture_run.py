# -*- coding: utf-8 -*-
"""Captura uma corrida completa do servidor Pix Race como dado bruto para análise.

Conecta no WebSocket do navegador (ws://localhost:8080/ws), dispara a corrida no modo
pedido, grava TODOS os eventos recebidos (run, decision, trace, error, done, report) em
um JSONL e encerra quando os dois lados terminam e o relatório chega.

Uso:
    python paper/capture_run.py [burst|serial] [saida.jsonl]

Padrão: modo burst (8 mensagens em paralelo por lado, igual aos números do README) e
saída em paper/results/run-<data>-<modo>.jsonl.
"""
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import websockets

URL = "ws://localhost:8080/ws"


async def capture(mode: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    done = {"rust": False, "python": False}
    n_events = 0
    with out.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "capture", "mode": mode, "started_at": started, "url": URL}) + "\n")
        async with websockets.connect(URL, max_size=None) as ws:
            await ws.send(json.dumps({"type": "reset"}))
            await asyncio.sleep(0.5)
            await ws.send(json.dumps({"type": "start", "mode": mode}))
            t0 = time.perf_counter()
            async for raw in ws:
                ev = json.loads(raw)
                ev["_recv_s"] = round(time.perf_counter() - t0, 6)
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
                n_events += 1
                kind = ev.get("type")
                if kind == "done" and ev.get("side") in done:
                    done[ev["side"]] = True
                    print(f"{ev['side']} terminou em {ev.get('totals', {}).get('total_ms')} ms", flush=True)
                    if all(done.values()):
                        await ws.send(json.dumps({"type": "report"}))
                elif kind == "report":
                    break
                elif kind == "decision" and n_events % 100 == 0:
                    print(f"{n_events} eventos...", flush=True)
    print(f"salvo {out} ({n_events} eventos)")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "burst"
    default = Path(__file__).parent / "results" / f"run-{datetime.now():%Y%m%d-%H%M%S}-{mode}.jsonl"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else default
    asyncio.run(capture(mode, out))
