"""Porte deterministico de src/graph.rs, usando somente a biblioteca padrao."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
import json
import math
from pathlib import Path
import struct
import sys
import time

JANELA = 86_400
PROF_MAX = 5
VALOR_MIN = 2_000
MAX_NOS = 40_000
ITER_LP = 10
MAX_NODES_DESENHO = 800
MAX_EDGES_DESENHO = 1_500
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def rust_round(value: float, places: int = 0) -> float:
    """f64::round: empates para longe de zero, sem round() de Python."""
    factor = 10.0 ** places
    scaled = abs(value * factor)
    whole = math.floor(scaled)
    rounded = whole + (scaled - whole >= 0.5)
    return math.copysign(rounded / factor, value)


@dataclass(slots=True)
class Trace:
    no: int
    t0: int
    visitados: int
    arestas_sub: int
    laranjas: list[int]
    saque: list[int]
    soma_suspeita: float
    nos: list[tuple[int, int, float]]
    sub: list[tuple[int, int, int, int]]

    def resumo(self, chave: str) -> dict:
        return {
            "chave": chave, "no": self.no, "t0": self.t0,
            "visitados": self.visitados, "arestas_sub": self.arestas_sub,
            "laranjas": self.laranjas, "saque": self.saque,
            "soma_suspeita": self.soma_suspeita,
        }

    def para_desenho(self) -> tuple[list[tuple[int, int, float]], list[tuple[int, int]]]:
        info = {v: (p, s) for v, p, s in self.nos}
        especiais = {self.no, *self.laranjas, *self.saque}
        # Igual ao Rust: o limite e aplicado ao acrescentar os demais nos.
        nodes = [(v, *info[v]) for v in [self.no, *self.laranjas, *self.saque]]
        resto = sorted((p, v) for v, p, _ in self.nos if v not in especiais)
        for _, v in resto:
            if len(nodes) >= MAX_NODES_DESENHO:
                break
            nodes.append((v, *info[v]))
        presentes = {v for v, _, _ in nodes}
        vistos = set()
        prioritarias = []
        demais = []
        for s, d, _, _ in self.sub:
            pair = (s, d)
            if s not in presentes or d not in presentes or pair in vistos:
                continue
            vistos.add(pair)
            if s in especiais or d in especiais:
                prioritarias.append(pair)
            else:
                demais.append(pair)
        edges = prioritarias
        for edge in demais:
            if len(edges) >= MAX_EDGES_DESENHO:
                break
            edges.append(edge)
        return nodes, edges[:MAX_EDGES_DESENHO]


class Graph:
    def __init__(self, n: int, n_edges: int, saida: list, grau_in_total: list[int]):
        self.n = n
        self.n_edges = n_edges
        self.saida = saida
        self.grau_in_total = grau_in_total
        self.in_deg = grau_in_total

    @classmethod
    def load(cls, path: str | Path) -> Graph:
        path = Path(path)
        if path.is_dir():
            path /= "transacoes.bin"
        with path.open("rb") as handle:
            header = handle.read(12)
            if len(header) != 12:
                raise ValueError("transacoes.bin: cabecalho incompleto")
            magic, n, n_edges = struct.unpack("<4sII", header)
            if magic != b"PIX1":
                raise ValueError("transacoes.bin: assinatura diferente de PIX1")
            raw = handle.read()
        if len(raw) != n_edges * 16:
            raise ValueError("transacoes.bin: tamanho diferente do cabecalho")
        saida = [[] for _ in range(n)]
        grau_in_total = [0] * n
        last_ts = 0
        for src, dst, valor, ts in struct.iter_unpack("<IIII", raw):
            if src >= n or dst >= n:
                raise ValueError("transacoes.bin: conta fora do intervalo")
            if ts < last_ts:
                raise ValueError("transacoes.bin: transacoes fora da ordem de ts")
            last_ts = ts
            saida[src].append((dst, valor, ts))
            grau_in_total[dst] += 1
        return cls(n, n_edges, saida, grau_in_total)

    def trace(self, no_chave: int, t0: int) -> Trace:
        if not 0 <= no_chave < self.n:
            raise ValueError(f"conta fora do grafo: {no_chave}")
        # A: BFS; inclusive as arestas cujo destino excede MAX_NOS sao
        # preservadas, exatamente como em graph.rs.
        saida = self.saida
        chegada = {no_chave: t0}
        prof = {no_chave: 0}
        fila = deque([no_chave])
        sub = []
        while fila:
            v = fila.popleft()
            pv = prof[v]
            if pv == PROF_MAX:
                continue
            cv = chegada[v]
            fim = cv + JANELA
            for d, valor, ts in saida[v]:
                if ts < cv:
                    continue
                if ts > fim:
                    break
                if valor < VALOR_MIN:
                    continue
                sub.append((v, d, valor, ts))
                if d not in chegada:
                    if len(chegada) >= MAX_NOS:
                        continue
                    chegada[d] = ts
                    prof[d] = pv + 1
                    fila.append(d)

        # B: acumular centavos em inteiros, converter somente na divisao.
        in_sum = {}
        for _, d, valor, _ in sub:
            in_sum[d] = in_sum.get(d, 0) + valor
        ids = sorted(chegada)
        suspeita = {}
        repasse = {}
        for v in ids:
            if v == no_chave:
                suspeita[v] = 1.0
                repasse[v] = 1.0
                continue
            cv = chegada[v]
            fim = cv + JANELA
            out_sum = 0
            primeiro_out = None
            for _, valor, ts in saida[v]:
                if ts < cv:
                    continue
                if ts > fim:
                    break
                if valor < VALOR_MIN:
                    continue
                out_sum += valor
                if primeiro_out is None:
                    primeiro_out = ts
            rep = min(1.0, float(out_sum) / float(in_sum[v]))
            rapidez = (0.0 if primeiro_out is None else
                       max(0.0, 1.0 - float(primeiro_out - cv) / 3600.0))
            pequeno = 1.0 if self.grau_in_total[v] < 50 else 0.0
            suspeita[v] = 0.4 * rep + 0.5 * rapidez + 0.1 * pequeno
            repasse[v] = rep

        # C: pares nao direcionados unicos, sem autoarestas, vizinhos por id.
        pares = {(min(s, d), max(s, d)) for s, d, _, _ in sub if s != d and d in chegada}
        vizinhos = {}
        for a, b in pares:
            vizinhos.setdefault(a, []).append(b)
            vizinhos.setdefault(b, []).append(a)
        for lista in vizinhos.values():
            lista.sort()
        rotulo = {v: v for v in ids}
        for _ in range(ITER_LP):
            for v in ids:
                viz = vizinhos.get(v, ())
                if not viz:
                    continue
                contagem = {}
                for u in viz:
                    r = rotulo[u]
                    contagem[r] = contagem.get(r, 0.0) + suspeita[u]
                melhor = None
                for r, soma in contagem.items():
                    if (melhor is None or soma > melhor[1]
                            or (soma == melhor[1] and r < melhor[0])):
                        melhor = (r, soma)
                rotulo[v] = melhor[0]
        rc = rotulo[no_chave]

        # D: ids ja estao ordenados; contar transacoes, nao pares unicos.
        laranjas = [v for v in ids if v != no_chave
                    and rotulo[v] == rc and suspeita[v] >= 0.6]
        set_laranjas = set(laranjas)
        de_laranja = {}
        for s, d, _, _ in sub:
            if s in set_laranjas:
                de_laranja[d] = de_laranja.get(d, 0) + 1
        saque = [v for v in ids if v != no_chave and v not in set_laranjas
                 and de_laranja.get(v, 0) >= 3 and repasse[v] < 0.3]
        # Nao usar sum(): Python 3.12 faz somatorio compensado de floats.
        soma = 0.0
        for v in ids:
            soma += suspeita[v]
        return Trace(no_chave, t0, len(ids), len(sub), laranjas, saque,
                     rust_round(soma, 4), [(v, prof[v], suspeita[v]) for v in ids], sub)


def para_desenho(result: Trace):
    return result.para_desenho()


def main() -> None:
    # JSONL permanece UTF-8 tambem quando redirecionado no Windows.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chave", nargs="?")
    parser.add_argument("--todas", action="store_true")
    args = parser.parse_args()
    if bool(args.chave) == args.todas:
        parser.error("informe uma chave ou --todas")
    data_dir = DEFAULT_DATA_DIR
    started = time.perf_counter()
    graph = Graph.load(data_dir)
    print(f"grafo: {graph.n} contas, {graph.n_edges} transacoes, "
          f"carga {(time.perf_counter() - started) * 1000:.3f} ms", file=sys.stderr)
    chaves = json.loads((data_dir / "chaves.json").read_text(encoding="utf-8"))
    meta = json.loads((data_dir / "meta.json").read_text(encoding="utf-8"))
    primeiros = {}
    with (data_dir / "mensagens.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                message = json.loads(line)
                primeiros.setdefault(message["chave"], message["ts"])
    quadrilhas = {q["chave"]: q for q in meta["quadrilhas"]}
    alvos = [q["chave"] for q in meta["quadrilhas"]] if args.todas else [args.chave]
    for chave in alvos:
        if chave not in chaves:
            parser.error(f"chave desconhecida: {chave}")
        q = quadrilhas.get(chave)
        t0 = primeiros.get(chave, q["inicio_ts"] - 300 if q else 0)
        started = time.perf_counter()
        result = graph.trace(chaves[chave], t0)
        latency_ms = (time.perf_counter() - started) * 1000.0
        print(json.dumps(result.resumo(chave), ensure_ascii=False, separators=(",", ":")))
        print(f"  {chave}: {result.visitados} nos, {result.arestas_sub} arestas, "
              f"{latency_ms:.3f} ms", file=sys.stderr)
        # A destruicao do resultado anterior fica fora da proxima medicao.
        del result


if __name__ == "__main__":
    main()
