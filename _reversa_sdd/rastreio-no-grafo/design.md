# Rastreio no grafo, Design Técnico

> Unit `rastreio-no-grafo`. Fonte: `src/graph.rs`, `py-worker/trace.py`. 🟢 salvo indicação.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `Graph::from_txs` | `(n: u32, txs: &[Tx])` | `Graph` | `txs` ordenado por ts; counting sort por origem |
| `Graph::trace` | `(&self, no_chave: u32, t0: u32)` | `Trace` | passos A a D |
| `Graph::saida_na_janela` | `(&self, v, cv)` | `(u64, Option<u32>)` | `out_sum`, `primeiro_out` |
| `Trace::resumo` | `(&self, chave: &str)` | `TraceResumo` | serializável |
| `Trace::para_desenho` | `(&self)` | `(Vec<(id, prof, suspeita)>, Vec<(src, dst)>)` | 800 / 1.500 |
| `Graph.load` (py) | `(path)` | `Graph` | valida magic, tamanho, faixa, ordem |
| `Graph.trace` (py) | `(no_chave, t0)` | `Trace` | idem |
| `rust_round` (py) | `(value, places=0)` | `float` | replica `f64::round` |

Estruturas:

| Estrutura | Rust | Python |
|---|---|---|
| Grafo | CSR: `start[n+1]`, `dst[m]`, `val[m]`, `ts[m]`, `in_deg[n]` | `saida[n]: list[(dst, valor, ts)]`, `grau_in_total[n]` |
| Estado do rastreio | vetores densos `chegada[n]` (sentinela `u32::MAX`), `prof[n]: u8`, `visitados_ord`, `sub: Vec<(u32,u32,u32,u32)>` | dicts `chegada`, `prof`, `deque`, `sub: list` |
| Saída `Trace` | `no, t0, visitados, arestas_sub, laranjas, saque, soma_suspeita, nos: Vec<(id, prof, suspeita)>, sub` | dataclass com os mesmos campos |

## Fluxo Principal
1. **Carga**: Rust `read_transacoes` → `Graph::from_txs` (conta saídas por origem, prefix sum → `start`, preenche `dst/val/ts` na ordem do arquivo, acumula `in_deg`) (`graph.rs:31-55`). Python lê com `struct.iter_unpack("<IIII")`, valida e monta listas (`trace.py:94-119`).
2. **Passo A** (`graph.rs:94-133`, `trace.py:124-151`): ver regras em `requirements.md`. Ao final `ids` = visitados ordenados.
3. **Passo B** (`graph.rs:135-158`, `trace.py:153-184`): `in_sum` inteiro; para cada `v` em `ids`, chave → 1,0/1,0; senão `saida_na_janela` e fórmula.
4. **Passo C** (`graph.rs:160-221`, `trace.py:186-210`): pares únicos; Rust monta CSR local (`off`, `viz`, cada lista ordenada com `sort_unstable`); contagem por rótulo em `Vec<(rotulo, soma)>` na ordem de aparição, escolha do melhor por `soma > melhor || (soma == melhor && r < melhor_r)`. Python usa dict `contagem` e itera `items()` na ordem de inserção (mesma ordem, pois vizinhos estão ordenados).
5. **Passo D** (`graph.rs:223-243`, `trace.py:212-221`): filtros sobre `ids` já ordenados; `de_laranja` conta arestas.
6. **Soma** em ordem de id, `round` a 4 casas.
7. **Desenho** (`graph.rs:309-364`, `trace.py:54-82`): `nodes` especiais primeiro, `resto` ordenado por `(prof, id)`, corte em 800; `edges` únicas por `(src,dst)` na ordem de `sub`, prioritárias sem limite, demais até 1.500, `truncate(1500)`.

## Fluxos Alternativos
- **Teto de nós:** `visitados_ord.len() >= MAX_NOS` → destino não visitado, aresta preservada em `sub`; no passo C essas arestas são filtradas por `chegada[d] != NAO_VISITADO` / `d in chegada`.
- **Nó sem vizinhos no passo C:** mantém rótulo próprio; se for a chave, comunidade = só ela e não há laranjas.
- **`in_sum[v] == 0`:** impossível para `v ≠ chave` (foi alcançado por uma aresta de `sub`).
- **Arquivo inválido:** Rust falha no cabeçalho/tamanho; Python também valida ordem e faixa de ids.

## Dependências
- `data::Tx` e `read_transacoes` (Rust); `struct` (Python).
- `serde::Serialize` em `TraceResumo`.
- Chamado por `server.rs` (`spawn_blocking` sob `trace_lock`), `worker.py` (`to_thread` sob `trace_lock`), `trace.rs`, `trace.py`.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| CSR com counting sort e ordem de ts preservada (sem sort por vértice) | `graph.rs:31-55` | 🟢 |
| Vetores densos de tamanho `n` por rastreio (evita hash; custo fixo de zerar 1 M × ~10 vetores) | `graph.rs:89-92,136-141,169-196,229-233` | 🟢 |
| Sentinela `u32::MAX` para "não visitado" | `graph.rs:16` | 🟢 |
| Janela por chegada, não por `t0` global | `graph.rs:105-106` | 🟢 |
| Suspeição com 3 sinais e pesos fixos | `graph.rs:156` | 🟢 |
| Propagação de rótulos assíncrona em ordem de id (determinismo) | `graph.rs:198-220` | 🟢 |
| Contagem de arestas (não remetentes únicos) para saque | `graph.rs:234-238`, comentário `trace.py:212` | 🟢 |
| `rust_round` em vez de `round()` do Python (banker's rounding) | `trace.py:25-31` | 🟢 |
| Loop manual em vez de `sum()` (soma compensada no 3.12) | `trace.py:222-225` | 🟢 |
| Desenho: prioritárias sem limite, depois corte global em 1.500 | `graph.rs:355-362` | 🟢 |

## Estado Interno
`Graph` imutável após a carga; compartilhado por `Arc<App>` (Rust) ou atributo do `Worker` (Python). Nenhum cache de rastreios.

## Observabilidade
CLIs imprimem em stderr: contas, transações, ms de carga, e por chave: nós, arestas, laranjas acertadas (Rust), ms. Servidor/worker reportam `latency_ms`, `visitados`, `arestas_sub` no evento `trace`.

## Riscos e Lacunas
- 🟡 Complexidade do passo B é `O(Σ grau_out dos visitados)` na janela; hubs visitados com milhares de saídas dominam o tempo.
- 🟡 `MAX_NOS = 40 000` pode cortar comunidades em grafos mais densos; não há métrica exposta de "teto atingido".
- 🟢 Sem teste automatizado da igualdade; `trace_ref.jsonl` é a única referência.
- 🟢 Rust não valida ordem de ts; um arquivo desordenado produz resultados errados silenciosamente (Python detecta).
