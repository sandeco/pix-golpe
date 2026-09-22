# Arquitetura: pix-golpe

> Gerado pelo Architect (Reversa) em 2026-09-21. Nível: completo. 🟢 CONFIRMADO salvo indicação.
> Diagramas: `c4-context.md`, `c4-containers.md`, `c4-components.md`, `erd-complete.md`. Matriz: `traceability/spec-impact-matrix.md`.

## 1. Visão geral

Sistema de demonstração, local, single-user, sem banco de dados e sem autenticação. Três processos e dois serviços externos:

| Container | Tecnologia | Papel |
|---|---|---|
| **Servidor** (`server`) | Rust 1.88, axum 0.7, tokio | Serve a página, orquestra a corrida, executa o lado Rust (Jev + rastreio), relatório, truth, spawn do worker |
| **Worker Python** (`worker.py`) | Python 3.12, websockets 15, httpx | Lado Python: DeepSeek + rastreio puro-Python |
| **Browser** (`index.html`) | HTML/CSS/JS puro | Tela dividida, grafo em canvas, relatório, modal |
| **Gerador** (`gerar-dados`) | Rust, rand_chacha | Roda uma vez, escreve `data/` |
| **CLIs** (`trace`, `trace.py`, `deepseek.py`) | Rust / Python | Conferência de igualdade e testes manuais |
| **Dados** (`data/`) | arquivos binário/JSON | Grafo de 10 M transações, mensagens, chaves, gabarito |
| TypeSafe AI (Jev) | HTTPS externo | Classificação tipada |
| DeepSeek | HTTPS externo | Classificação em JSON mode |

Estilo: monólito Rust com processo satélite Python; comunicação por WebSocket com eventos JSON; estado da corrida em memória (`Arc<App>`), invalidado por `run_id`.

## 2. Fluxo principal (uma mensagem)

1. Browser envia `start {mode}`. Servidor incrementa `run_id`, envia `reset` e `run {concurrency, pace_ms}` a browser e worker, e todas as 1.000 `message` de uma vez.
2. Lado Rust: task por mensagem sob `Semaphore(concurrency)` → Jev → `decision` → sleep `pace_ms` → se golpe, `trace_lock` + `spawn_blocking(graph.trace)` → `trace` + `truth`.
3. Lado Python: task por mensagem sob `asyncio.Semaphore` → DeepSeek → `decision` → sleep → se golpe, `trace_lock` + `to_thread(trace)` → `trace`; o servidor injeta `side` e `truth`.
4. Browser atualiza contador, veredito, grafo, lista e medianas; quando os dois `done` chegam, mostra o cartão final; `report` traz a matriz de confusão.

## 3. Integrações externas

| Serviço | Protocolo | Autenticação | Contrato | Falhas |
|---|---|---|---|---|
| TypeSafe AI `POST https://api.typesafe.ai/v1/systemone` | HTTPS JSON | Bearer `TYPESAFE_API_KEY` | request `{model, state, questions}`; response `{model, answers{golpe.noul, tipo.choice/confidence, urgencia.score, pede_pix.noul}, usage.input_tokens}` | 429/529 → 3 retries; outros → `error` |
| DeepSeek `POST https://api.deepseek.com/chat/completions` | HTTPS JSON | Bearer `DEEPSEEK_API_KEY` | OpenAI-compatible; `response_format json_object`; content JSON `{golpe, tipo, urgencia, pede_pix}`; `usage.prompt_tokens/completion_tokens`; `model` | 429/5xx → 3 tentativas; JSON inválido → `error` |

Protocolos internos: HTTP `GET /`; WebSocket `/ws` (browser) e `/ws/worker` (worker), eventos documentados em `data-dictionary.md` §3.

## 4. Dados

Sem SGBD. `data/` é gerado uma vez e carregado inteiro em memória por servidor e worker no start. Volumes em disco (2026-09-21): `transacoes.bin` 152,1 MiB (9.968.511 × 16 B), `mensagens.jsonl` 189 KB, `chaves.json` 27 KB, `meta.json` 36 KB, `trace_ref.jsonl` 11 KB. ERD conceitual em `erd-complete.md`.

Memória em runtime 🟡: Rust mantém CSR (4 vetores de 10 M u32 ≈ 160 MB + `start`/`in_deg` de 1 M) e, por rastreio, vetores densos de 1 M posições; Python mantém 1 M listas de tuplas (várias vezes maior). A tela exibe `memory_mb` de cada lado.

## 5. Decisões arquiteturais

Ver `adrs/001` a `008`. Resumo: demo em tela dividida (001); regras de justiça (002); dataset sintético com semente (003); rastreio determinístico em 4 passos (004); axum único + worker filho (005); tela de arquivo único para leigos (006); Jev HTTP direto e DeepSeek JSON mode (007); veredito em três faixas (008).

## 6. Dívidas técnicas e riscos

| # | Item | Evidência | Impacto | Conf. |
|---|---|---|---|---|
| D1 | **Sem testes automatizados**; igualdade Rust/Python conferida à mão com `fc` | `surface.json.test_file_count = 0`, README | qualquer mudança em `graph.rs`/`trace.py` pode divergir silenciosamente | 🟢 |
| D2 | **Documentação desatualizada**: SPEC/PDF/README com escala 100 k/1,3 M; SPEC §4 `include_str!`; SPEC §5 tela antiga; screenshot com título antigo | `code-analysis.md` L1, L2, L5, L6 | confunde quem lê antes de codar | 🟢 |
| D3 | **Algoritmo duplicado por design** (Rust e Python): manutenção espelhada obrigatória | ADR-004 | custo de mudança dobrado | 🟢 |
| D4 | **Assimetria de medição** de retry entre lados | RN-07 | métricas p50/p95 comparáveis só sem 429/5xx | 🟢 |
| D5 | **Sem autenticação, bind 0.0.0.0**, `/ws/worker` aberto | `permissions.md` | qualquer host na rede pode disparar corridas e gastar créditos de API | 🟢 |
| D6 | **Dependências Python sem pin**; `websockets` 15 tem API nova | `dependencies.md` | ambiente novo pode quebrar o worker | 🟡 |
| D7 | **Preços de API hardcoded** | `jev.rs:10`, `deepseek.py:24-25` | custo exibido pode ficar defasado | 🟢 |
| D8 | `index.html` de 1.606 linhas em arquivo único com CSS, HTML, JS e mock | `frontend` | difícil de manter, mas decisão consciente (sem build) | 🟢 |
| D9 | `read_transacoes` carrega o arquivo inteiro com `fs::read` e depois converte (pico ≈ 2× o arquivo) | `data.rs:104-119` | pico de memória transitório de ~320 MB | 🟢 |
| D10 | Rastreio Rust aloca vetores densos de 1 M por chamada (`chegada`, `prof`, `in_sum`, `suspeita`, `repasse`, `grau`, `off`, `rotulo`, `eh_laranja`, `de_laranja`) | `graph.rs:90-233` | ~50 MB alocados e zerados por rastreio; rápido, mas é o custo fixo do `trace_ms` | 🟢 |
| D11 | `meta.json` lista os 2.000 hubs como array de inteiros (35 KB) sem uso no runtime | `server.rs:160-161` só usa `quadrilhas` | inofensivo | 🟢 |
| D12 | Broadcast de 8192 mensagens: em `burst` com browser lento pode ocorrer `Lagged` e perda de eventos na tela (não no relatório) | `server.rs:177,249` | tela pode pular eventos | 🟡 |
| D13 | Sem CI, sem Docker, sem versionamento Git | Scout | reprodutibilidade depende da máquina do apresentador | 🟢 |

## 7. Qualidades observadas

- Reprodutibilidade forte (semente fixa, `trace_ref.jsonl`).
- Invalidação por `run_id` simples e robusta nas três camadas.
- Worker resiliente: reconexão, validação de eventos, `done` mesmo com erros.
- Front-end acessível o suficiente para demo (dialogs, foco, reduced-motion) e com modo mock para desenvolvimento offline.
