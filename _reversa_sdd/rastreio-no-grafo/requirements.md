# Rastreio no grafo

> Unit `rastreio-no-grafo`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
A partir da conta da chave Pix citada numa mensagem classificada como golpe e do instante da mensagem, segue o dinheiro no grafo de transações e classifica contas em laranjas (intermediárias) e saques (destinos finais). Algoritmo determinístico em quatro passos, com implementações Rust (`src/graph.rs`) e Python puro (`py-worker/trace.py`) que produzem saída idêntica.

## Responsabilidades
- Carregar `transacoes.bin` em listas de adjacência de saída ordenadas por tempo e grau de entrada total.
- Executar `trace(no_chave, t0)`: BFS temporal, suspeição, propagação de rótulos, classificação.
- Produzir o resumo (visitados, arestas, laranjas, saque, soma_suspeita) e a seleção para desenho (≤ 800 nós, ≤ 1.500 arestas).
- Garantir igualdade bit a bit entre Rust e Python.

## Regras de Negócio
- RN-21 Parâmetros: `JANELA = 86 400 s`, `PROF_MAX = 5`, `VALOR_MIN = 2 000` centavos, `MAX_NOS = 40 000`, `ITER_LP = 10`, desenho 800 / 1 500. 🟢 `graph.rs:8-14`, `trace.py:15-21`
- Passo A: a partir de `chegada[no] = t0`, para cada saída de `v` em ordem de ts: ignora `ts < chegada[v]`, para em `ts > chegada[v] + JANELA`, ignora `valor < VALOR_MIN`; a aresta entra em `sub` sempre; o destino entra na fila se inédito e `visitados < MAX_NOS`; nós com `prof == PROF_MAX` não expandem. 🟢 `graph.rs:94-131`
- Passo B: `in_sum[v]` = soma de `sub` com destino `v` (inteiro); `out_sum`/`primeiro_out` sobre as saídas de `v` na janela, independentemente de profundidade; `repasse = min(1, out/in)`; `rapidez = 0` se sem saída, senão `max(0, 1 − (primeiro_out − chegada)/3600)`; `pequeno = 1` se `in_deg < 50`; `suspeita = 0,4·repasse + 0,5·rapidez + 0,1·pequeno`; chave = 1,0. 🟢 `graph.rs:135-158`
- Passo C: grafo não direcionado dos pares `(min, max)` de `sub` sem autoarestas e com destino visitado, sem duplicatas; vizinhos ordenados por id; `rotulo[v] = v`; 10 iterações, `v` em ordem crescente, atualização in-place; novo rótulo = maior soma de suspeita dos vizinhos por rótulo, empate → menor rótulo; sem vizinhos → mantém. 🟢 `graph.rs:160-221`
- Passo D: `laranjas` = `v ≠ chave`, mesmo rótulo da chave, `suspeita ≥ 0,6`, ordenadas por id; `saque` = `v ≠ chave`, não laranja, ≥ 3 arestas de `sub` com origem laranja e destino `v`, `repasse < 0,3`, ordenadas por id. 🟢 `graph.rs:223-243`
- `soma_suspeita` = soma em ordem crescente de id, arredondada a 4 casas com `f64::round` (empate longe do zero). 🟢 `graph.rs:245-249`, `trace.py:25-31`
- Seleção para desenho: nós = chave, laranjas, saque, depois os demais por `(prof, id)` até 800; arestas = pares únicos `(src, dst)` de `sub` com ambos presentes, primeiro as que tocam nós especiais, depois as demais até 1.500, truncando em 1.500. 🟢 `graph.rs:309-364`
- RN-25 Aritmética f64 com a mesma ordem de operações nas duas linguagens; Python não usa `sum()`. 🟢
- RN-26 Tempo medido = passos A a D; carga, desenho e espera de lock fora. 🟢
- `t0` = `ts` da mensagem (servidor/worker) ou da primeira mensagem com a chave (CLIs). 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Carregar o grafo de `transacoes.bin` com listas de saída ordenadas por ts e `in_deg` | Must | `nodes = n_contas`, `edges = n_transacoes` no `status` |
| RF-02 | `trace(no, t0)` implementando os passos A a D | Must | 40 chaves reproduzem `data/trace_ref.jsonl` |
| RF-03 | Resumo JSON `{chave, no, t0, visitados, arestas_sub, laranjas, saque, soma_suspeita}` | Must | igualdade com `fc` |
| RF-04 | Seleção para desenho (800/1.500) com prioridade a nós especiais | Must | `nodes[0]` é a chave; `len(nodes) ≤ 800`; `len(edges) ≤ 1500` |
| RF-05 | Implementação Python sem bibliotecas de terceiros | Must | apenas stdlib em `trace.py` |
| RF-06 | Rejeitar `no_chave` fora do grafo (Python) | Could | `ValueError` |
| RF-07 | Validar ordem de ts e faixa de ids na carga (Python) | Should | `ValueError` em arquivo corrompido |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | Rust p50 ≈ 14 ms, Python p50 ≈ 239 ms por rastreio (medido em 2026-09-21) | README | 🟡 |
| Performance | CSR com 4 vetores contíguos; vetores densos por rastreio | `graph.rs:19-27,89-92` | 🟢 |
| Determinismo | ordem de soma e `rust_round` | `trace.py:25-31,222-225` | 🟢 |
| Memória | Rust ≈ 160 MB de CSR + ~50 MB temporários por rastreio; Python bem maior | inferido de tamanhos | 🟡 |
| Concorrência | um rastreio por vez por lado (lock) | `server.rs:379`, `worker.py:267` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado o grafo carregado de data/transacoes.bin
Quando executo trace para cada uma das 40 chaves de meta.json com t0 da primeira mensagem
Então o resumo JSON de cada uma é idêntico à linha correspondente de data/trace_ref.jsonl

Dado a chave 51942117050 (no 277265, t0 292041)
Quando executo trace
Então visitados = 10782, arestas_sub = 10908, laranjas tem 14 ids, saque = [231455, 285379], soma_suspeita = 2627.0042

Dado uma conta v alcançada cujo primeiro repasse ocorre 30 min após a chegada, repassando 99% e com 3 entradas no histórico
Quando calculo a suspeição
Então suspeita = 0,4·0,99 + 0,5·0,5 + 0,1·1 = 0,746

Dado um hub (in_deg >= 50) alcançado que não repassa nada na janela
Quando calculo a suspeição
Então rapidez = 0, pequeno = 0 e suspeita = 0,4·repasse com repasse = 0

Dado o teto MAX_NOS atingido
Quando uma aresta leva a um destino inédito
Então a aresta ainda entra em sub, mas o destino não é visitado
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Passos A a D idênticos | Must | núcleo da demo e da comparação |
| Carga CSR / listas | Must | pré-condição |
| Seleção para desenho | Must | contrato com a tela |
| Validações de carga (Python) | Should | robustez, não afeta saída |
| Rejeição de `no` inválido | Could | só CLI |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/graph.rs` | `Graph::from_txs`, `Graph::trace`, `saida_na_janela`, `Trace`, `TraceResumo`, `para_desenho` | 🟢 |
| `py-worker/trace.py` | `Graph.load`, `Graph.trace`, `Trace`, `para_desenho`, `rust_round` | 🟢 |
| `src/data.rs` | `read_transacoes` | 🟢 |
