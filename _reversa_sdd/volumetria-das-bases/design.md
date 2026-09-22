# Volumetria das bases de dados, Design Técnico

> Unit `volumetria-das-bases`. Como os volumes nascem, onde são medidos e como se transformam em memória. 🟢 salvo indicação.

## Interface
Não há API própria. Os volumes aparecem em:

| Onde | Campo | Origem |
|---|---|---|
| `data/meta.json` | `n_contas`, `n_transacoes`, `hubs[]`, `quadrilhas[]` | `gerar_dados.rs:260` |
| cabeçalho de `transacoes.bin` | `n_contas`, `n_transacoes` | `data.rs:124-126` |
| evento `status` (rust) | `nodes`, `edges`, `load_ms`, `memory_mb` | `server.rs:149-156,179` |
| evento `status` (python) | idem | `worker.py:146-154,169-172` |
| stderr dos CLIs | `grafo: N contas, M transações, carga X ms` | `trace.rs:15`, `trace.py:247` |
| stdout do gerador | `gerado em <dir>: N contas, M transações, 40 quadrilhas, 1000 mensagens` | `gerar_dados.rs:265` |

## Fluxo Principal (como o volume é produzido)
1. Constantes (`N_CONTAS`, `N_HUBS`, `DIAS`, `N_TX_NORMAIS`, `N_QUADRILHAS`, `N_MSG_*`) definem a escala.
2. Fundo: exatamente `N_TX_NORMAIS` = 9.500.000 transações.
3. Lotes de hubs: `Σ_h Σ_dia (10 + ⌊1500 · peso_h/peso_0⌋)` = 466.110 transações (medido; hub 0 = 1.510/dia, hub 1999 ≈ 10/dia).
4. Quadrilhas: por quadrilha, `n_vitimas (20..40) + n_lar (12..18) × 2` transações; total ≈ 2.401 (= 9.968.511 − 9.500.000 − 466.110).
5. Escrita em 16 B por transação, sem compressão, ordenada por `ts`.

## Fluxo Principal (como o volume vira memória)
| Etapa | Rust | Python |
|---|---|---|
| Leitura | `fs::read` (152 MiB em `Vec<u8>`) → `Vec<Tx>` (152 MiB) | `handle.read()` (152 MiB bytes) → `struct.iter_unpack` |
| Estrutura | CSR: `start` (4 MB), `dst`/`val`/`ts` (3 × 39,9 MB), `in_deg` (4 MB) ≈ 168 MB | `saida`: 1 M listas + 9,97 M tuplas de 3 ints (≈ 1,6 GB medidos) + `grau_in_total` (1 M ints) |
| Liberação | `drop(txs)` após montar (`server.rs:152`, `trace.rs:14`) | `raw` sai de escopo; `gc.collect()` no worker |
| Por rastreio | ~10 vetores densos de 1 M (u32/u8/f64/bool) ≈ 40 a 50 MB alocados e zerados | dicts proporcionais aos visitados (≤ 40 k) |
| Medição | `memory_stats::memory_stats().physical_mem` | `psutil` → `GetProcessMemoryInfo` → `resource` |

## Fluxos Alternativos
- **Mudar a escala:** editar as constantes, regenerar `data/`, regenerar `trace_ref.jsonl`, atualizar SPEC/README/PDF e esta spec (ver `traceability/spec-impact-matrix.md`).
- **Escala 10× menor (100 k / 1,3 M):** era a escala do SPEC/PDF; memória Python cairia para ~200 MB e carga para < 1 s 🟡.
- **Arquivo corrompido:** Rust falha por tamanho; Python também por ordem/faixa.

## Dependências
- `gerar-dados` (produção), `data.rs`/`trace.py` (leitura), `server.rs`/`worker.py` (publicação no `status`), tela (exibição de memória).

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Binário fixo de 16 B em vez de JSON/CSV (10× menor, carga direta) | `data.rs:122-134` | 🟢 |
| Escala 10× acima do SPEC para tornar o rastreio Python visivelmente lento | constantes vs SPEC; brainstorm ("etapa pesada") | 🟡 |
| Grafo inteiro em memória, sem índice em disco | `graph.rs`, `trace.py` | 🟢 |
| `meta.json` com os 2.000 hubs listados (2/3 do arquivo) apesar de derivável de `N_HUBS` | `gerar_dados.rs:260` | 🟢 |
| Memória exibida na tela por lado | `status.memory_mb`, `MEMÓRIA` na lane | 🟢 |

## Estado Interno
Nenhum além dos arquivos.

## Observabilidade
`status` na tela (MEMÓRIA em MB/GB), logs de carga em stdout/stderr.

## Riscos e Lacunas
- 🟢 Escala oficial confirmada pelo usuário (1 M / 9.968.511 / 2.000); docs a corrigir.
- 🟡 Memória do Rust não medida diretamente nesta extração (o `server` mede, mas exige chave de API para subir).
- 🟢 Python a 1,67 GB pode não caber em máquinas modestas; nenhum aviso no código.
- 🟢 `trace_ref.jsonl` reproduzido byte a byte hoje com o binário atual.
