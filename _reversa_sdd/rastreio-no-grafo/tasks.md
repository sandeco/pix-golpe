# Rastreio no grafo, Tarefas de Implementação

> Unit `rastreio-no-grafo`. Reimplementação a partir de `src/graph.rs` e `py-worker/trace.py`.

## Pré-requisitos
- [ ] `data/transacoes.bin` gerado (unit `geracao-de-dados`) e `data/trace_ref.jsonl` como oráculo
- [ ] Constantes fixadas: 86400 / 5 / 2000 / 40000 / 10 / 800 / 1500

## Tarefas

- [ ] T-01, Carga do grafo em CSR (Rust) e listas por conta (Python), com `in_deg`
  - Origem no legado: `src/graph.rs:29-55`, `py-worker/trace.py:93-119`
  - Critério de pronto: `n = 1_000_000`, `n_edges = 9_968_511`; Python rejeita ts fora de ordem
  - Confiança: 🟢

- [ ] T-02, Passo A: BFS temporal com janela por chegada, valor mínimo, profundidade e teto
  - Origem no legado: `src/graph.rs:94-133`, `py-worker/trace.py:124-151`
  - Critério de pronto: `visitados` e `arestas_sub` batem com `trace_ref.jsonl` nas 40 chaves
  - Confiança: 🟢

- [ ] T-03, Passo B: suspeição com `saida_na_janela`, inteiros em centavos, pesos 0,4/0,5/0,1
  - Origem no legado: `src/graph.rs:62-85,135-158`, `py-worker/trace.py:153-184`
  - Critério de pronto: `soma_suspeita` bate a 4 casas
  - Confiança: 🟢

- [ ] T-04, Passo C: pares únicos, vizinhos ordenados, 10 iterações assíncronas com desempate pelo menor rótulo
  - Origem no legado: `src/graph.rs:160-221`, `py-worker/trace.py:186-210`
  - Critério de pronto: `laranjas` bate nas 40 chaves
  - Confiança: 🟢

- [ ] T-05, Passo D: laranjas e saques, ordenados por id
  - Origem no legado: `src/graph.rs:223-243`, `py-worker/trace.py:212-221`
  - Critério de pronto: `saque` bate nas 40 chaves
  - Confiança: 🟢

- [ ] T-06, `rust_round` e soma em ordem de id sem `sum()`
  - Origem no legado: `py-worker/trace.py:25-31,222-227`
  - Critério de pronto: `rust_round(2.5) == 3.0`, `rust_round(-2.5) == -3.0`; soma bate
  - Confiança: 🟢

- [ ] T-07, `resumo(chave)` e serialização compacta (`separators=(",", ":")` no Python)
  - Origem no legado: `src/graph.rs:282-307`, `py-worker/trace.py:46-52,267`
  - Critério de pronto: linha idêntica byte a byte entre lados
  - Confiança: 🟢

- [ ] T-08, `para_desenho`: 800 nós / 1.500 arestas com prioridades
  - Origem no legado: `src/graph.rs:309-364`, `py-worker/trace.py:54-82`
  - Critério de pronto: mesma lista de `nodes` e `edges` nos dois lados para as 40 chaves (comparar após `rust_round(s, 3)`)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Igualdade com `trace_ref.jsonl` nas 40 chaves (automatizar o `fc` do README)
- [ ] TT-02, Igualdade de `para_desenho` entre Rust e Python (hoje não coberta pelo `fc`)
- [ ] TT-03, Grafo mínimo sintético: chave → 3 laranjas → 1 saque, verificando suspeição e classificação à mão
- [ ] TT-04, Teto `MAX_NOS`: grafo em estrela com 50 000 folhas; `visitados == 40000`, `arestas_sub == 50000`
- [ ] TT-05, Hub alcançado (in_deg ≥ 50) não vira laranja mesmo repassando rápido se suspeita < 0,6 (0,4 + 0,5·rapidez < 0,6 exige rapidez < 0,4)

## Ordem Sugerida
1. T-01 → T-02 → T-03 → T-06 → T-04 → T-05 → T-07 (validar com TT-01 a cada passo) → T-08 (TT-02).

## Lacunas Pendentes (🔴)
Nenhuma; o algoritmo está integralmente confirmado no código.
