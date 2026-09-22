# Volumetria das bases de dados

> Unit `volumetria-das-bases` (pedido do usuário). Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO (medido em disco ou no código), 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Registra o tamanho, a composição e o custo de carga das "bases" do pix-golpe. Não há SGBD: a base é o conjunto de arquivos em `data/`, gerado uma vez e carregado inteiro em memória por cada lado. Esta spec fixa os volumes vigentes (código e arquivos em disco), documenta a divergência com a documentação anterior e define os requisitos que qualquer regeneração ou reimplementação deve respeitar.

## Responsabilidades
- Declarar os volumes canônicos por arquivo e por entidade.
- Declarar a composição do grafo (fundo, hubs, quadrilhas) com contagens medidas.
- Declarar os custos de carga e memória por lado, medidos.
- Fixar invariantes verificáveis para regenerações.

## Regras de Negócio

### Volumes em disco (medidos em 2026-09-21, arquivos de 15:08) 🟢

| Arquivo | Bytes | Registros | Tamanho por registro |
|---|---|---|---|
| `data/transacoes.bin` | 159.496.188 (152,1 MiB) | 9.968.511 transações + cabeçalho 12 B | 16 B fixos |
| `data/mensagens.jsonl` | 188.934 | 1.000 linhas | ~189 B (texto médio 83 caracteres, máximo 182) |
| `data/chaves.json` | 26.999 | 965 pares chave → conta | ~28 B |
| `data/meta.json` | 35.665 | 2.000 hubs + 40 quadrilhas | hubs ocupam ~2/3 do arquivo |
| `data/trace_ref.jsonl` | 10.557 | 40 linhas | ~264 B |
| **Total `data/`** | **159.758.343 (152,4 MiB)** | | |

### Entidades 🟢

| Entidade | Quantidade | Fonte |
|---|---|---|
| Contas | 1.000.000 (ids 0..999.999) | `meta.json`, cabeçalho do binário |
| Hubs (comerciantes) | 2.000 (ids 0..1.999) | `meta.json.hubs` |
| Transações | 9.968.511 | cabeçalho, `meta.json` |
| Período | 10 dias, `ts` 0..863.999 s | medido |
| Valores | 500 a 1.126.555 centavos (R$ 5,00 a R$ 11.265,55) | medido |
| Quadrilhas | 40 | `meta.json` |
| Contas de chave (golpista) | 40 | |
| Laranjas | 606 (12 a 18 por quadrilha) | medido |
| Contas de saque | 80 (2 por quadrilha) | medido |
| Chaves Pix | 965 (40 de quadrilha + 925 legítimas) | medido |
| Mensagens | 1.000 (75 golpes, 925 legítimas), `ts` 87.010..775.348 | medido |
| Chaves distintas nas mensagens | 965 (golpes reutilizam as 40 chaves) | medido |

### Composição das transações (medida por varredura do binário) 🟢

| Categoria | Quantidade | Critério |
|---|---|---|
| Lotes de hubs (origem < 2.000) | 466.110 | `src < N_HUBS` |
| Com destino em hub | 4.749.905 (47,6 %) | `dst < N_HUBS` |
| Recebidas por contas de chave (vítimas + fundo) | 1.424 | `dst ∈ nos` |
| Recebidas por laranjas | 3.849 | `dst ∈ laranjas` |
| Enviadas por laranjas | 6.413 | `src ∈ laranjas` |
| Recebidas por contas de saque | 1.032 | `dst ∈ saque` |
| **Enviadas por contas de saque (transações de fundo)** | **807** | `src ∈ saque` |
| Fundo (normais) ≈ | 9.500.000 | `N_TX_NORMAIS` |

A última linha prova que contas de saque movimentam dinheiro no período (RN-55 do `domain.md`): o SPEC §1 afirma que "não movimentam nada nas 24 h seguintes", o gerador não garante isso. 🟢 Usuário confirmou em 2026-09-22 (Pergunta 3): vale o código; o SPEC §1 e o PDF p.4 devem ser corrigidos.

### Custos de carga e memória (medidos nesta máquina, 2026-09-21) 🟢

| Lado | Carga do grafo | Memória residente após carga | Rastreio nas 40 chaves (p50 / min / max) |
|---|---|---|---|
| Rust (`trace.exe`, release) | 328 ms | não medido pelo CLI; estimativa 🟡 ≈ 170 MB de CSR (4 vetores × 9,97 M × 4 B + `start` e `in_deg` de 1 M) + até ~50 MB temporários por rastreio | 14,9 ms / 4,3 ms / 24,9 ms |
| Python (`trace.py`, CPython 3.12) | 4.246 ms | 1.668 MB (working set; 44,6 MB antes) | 157,8 ms / 4,6 ms / 646,8 ms |

Pico transitório na carga Rust: dentro de `read_transacoes` coexistem o buffer do arquivo (152 MiB) e o `Vec<Tx>` (152 MiB); depois, em `from_txs`, coexistem o `Vec<Tx>` e o CSR (≈ 168 MB) até o `drop(txs)`; pico ≈ 320 MB 🟡 (`data.rs:104-119`, `server.rs:150-152`).

Números anteriores do README (1.000 mensagens, rajada 8): Rust rastreio p50 14 ms / p95 32 ms; Python p50 239 ms / p95 734 ms. Coerentes com a medição acima. 🟢

### Escala oficial 🟢 (confirmada pelo usuário em 2026-09-22, Pergunta 1)

| Fonte | Contas | Transações | Hubs |
|---|---|---|---|
| Código (`gerar_dados.rs:11-14`) e arquivos em disco | 1.000.000 | 9.968.511 | 2.000 |
| `SPEC.md` §1 | 100.000 | ~1.300.000 | ~200 |
| PDF `pix-golpe-explicacao.pdf` p.3-4 | 100.000 | 1.271.343 | 200 |
| `README.md` | (não cita) | "1,3 milhão" | |

Escala oficial: **1.000.000 contas, 9.968.511 transações, 2.000 hubs** (a do código e dos dados). SPEC, README e PDF estão desatualizados e devem ser corrigidos (T-04).

### Invariantes 🟢
- `tamanho(transacoes.bin) == 12 + 16 × n_transacoes`.
- `ts` não decrescente; `origem, destino < n_contas`.
- `meta.n_contas == cabeçalho.n_contas`; `meta.n_transacoes == cabeçalho.n_transacoes`.
- Toda `mensagem.chave` ∈ `chaves.json`; toda `quadrilha.chave` ∈ `chaves.json` com `chaves[chave] == quadrilha.no`.
- Contas de quadrilha (chave, laranjas, saque) são disjuntas entre quadrilhas e nunca são hubs (ids ≥ 2.000).
- `len(quadrilhas) == 40`; `12 ≤ len(laranjas) ≤ 18`; `len(saque) == 2`.
- `count(golpe_real) == 75`; `len(mensagens) == 1.000`.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Os arquivos gerados respeitam os volumes da tabela "Entidades" | Must | contagens iguais |
| RF-02 | Os invariantes acima são verificáveis por script | Must | script retorna 0 |
| RF-03 | A carga em Rust termina em < 1 s e em Python em < 10 s nesta classe de máquina 🟡 | Should | medição |
| RF-04 | O evento `status` publica `nodes`, `edges`, `load_ms`, `memory_mb` reais | Must | valores batem com esta spec |
| RF-05 | `data/` não é versionado; regenerável em segundos (README: 2 s) 🟡 | Should | `.gitignore` futuro |
| RF-06 | Documentação (SPEC, README, PDF) alinhada à escala vigente | Should | textos citam 1 M / 9.968.511 / 2.000 🟢 decisão tomada |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência | Confiança |
|------|--------------------|-----------|-----------|
| Armazenamento | 152,4 MiB em disco | medido | 🟢 |
| Memória | Rust ~170 MB estável; Python ~1,67 GB | medido/estimado | 🟢/🟡 |
| Performance | carga 0,3 s (Rust) e 4,2 s (Python) | medido | 🟢 |
| Reprodutibilidade | semente fixa; `trace_ref.jsonl` reproduzido byte a byte hoje | medido (`fc` sem diferenças) | 🟢 |

## Critérios de Aceitação

```gherkin
Dado data/transacoes.bin
Quando leio o cabeçalho
Então n_contas = 1000000, n_transacoes = 9968511 e o tamanho do arquivo é 159496188 bytes

Dado data/meta.json e data/chaves.json
Quando conto
Então há 2000 hubs, 40 quadrilhas, 606 laranjas, 80 contas de saque e 965 chaves

Dado o worker Python carregado
Quando o servidor repassa o status ready
Então nodes = 1000000, edges = 9968511, load_ms ≈ 4000 e memory_mb ≈ 1600 a 1700

Dado o grafo carregado no Rust
Quando rastreio as 40 chaves com o t0 da primeira mensagem
Então a saída é idêntica a data/trace_ref.jsonl
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Volumes e invariantes | Must | contrato de todos os consumidores |
| Status com números reais | Must | aparece na tela |
| Limites de carga | Should | conforto de gravação |
| Alinhar documentação | Should | depende de Q-001 |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/bin/gerar_dados.rs:11-17` | constantes | 🟢 |
| `src/data.rs:103-134` | formato binário | 🟢 |
| `src/graph.rs:19-55` | CSR (memória Rust) | 🟢 |
| `py-worker/trace.py:85-119` | listas (memória Python) | 🟢 |
| `src/bin/server.rs:149-156,179` | `load_ms`, `memory_mb`, `status` | 🟢 |
| `py-worker/worker.py:24-47,146-172` | `memoria_mb`, `status` | 🟢 |
| `data/*` | arquivos medidos | 🟢 |
