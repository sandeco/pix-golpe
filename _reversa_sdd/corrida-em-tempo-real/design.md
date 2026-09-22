# Corrida em tempo real, Design Técnico

> Unit `corrida-em-tempo-real`. Fonte: `src/bin/server.rs`, `py-worker/worker.py`. 🟢 salvo indicação.

## Interface

HTTP/WS (axum 0.7):

| Método | Caminho | Entrada | Saída | Status codes |
|--------|---------|---------|-------|--------------|
| GET | `/` | | HTML de `static/index.html` | 200 (também 200 com erro em HTML se o arquivo faltar) |
| GET | `/ws` | upgrade WebSocket | eventos JSON (texto) | 101 |
| GET | `/ws/worker` | upgrade WebSocket | eventos JSON (texto) | 101 |

Símbolos principais:

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `main` | async | `Result<()>` | boot, spawn worker, serve |
| `comando_browser` | `(app: &Arc<App>, texto: &str)` | `()` | JSON inválido → ignora |
| `pace_de` | `(mode: &str, padrao: u64)` | `u64` | ms de pausa |
| `run` | `(app, run_id, mode)` async | `()` | despacho + `done` |
| `processar` | `(app, run_id, m: Mensagem, stats, sem)` async | `()` | lado Rust por mensagem |
| `handle_browser` / `handle_worker` | `(WebSocket, Arc<App>)` async | `()` | loops `select!` |
| `App::enrich_truth` | `(&self, ev: &mut Value)` | `()` | só `type == "trace"` |
| `App::registrar_verdict` | `(&self, side, id, verdict)` | `()` | |
| `percentil` | `(v: &[f64], p: f64)` | `f64` | `s[round(p/100·(n−1))]`, vazio → 0 |
| `Worker.serve_forever` (py) | async | | loop de conexão |
| `Worker.handle_raw` / `handle_event` / `process_message` / `emit` / `hello` / `finish_message` / `maybe_done` | async | | |
| `parse_event` (py) | `(raw)` | `dict` | `ValueError` |
| `Run.totals` (py) | | `dict` | p50/p95, custo, `total_ms` |

Estado `App` (Rust): ver `code-analysis.md` §server. Estado `Worker`/`Run` (Python): ver `data-dictionary.md` §2.

## Fluxo Principal
1. **Boot** (`server.rs:143-217`): dotenv → `data_dir` → grafo (`load_ms`, `memory_mb` via `memory_stats`) → mensagens, chaves, `truth` → `JevClient` (obrigatório) → aquecimento → `App` → spawn worker → router → bind.
2. **Browser conecta** (`:236-259`): recebe `rust_status` e `python_status`; loop: broadcast → socket; socket → `comando_browser`.
3. **`start`** (`:264-271`): `pace_ms`, `run_id += 1`, `verdicts.clear()`, `reset` a todos, `spawn(run)`.
4. **`run`** (`:302-334`): `run` a todos; para cada mensagem (checando `run_id`), `message` a todos + `spawn(processar)`; `join_next` até esvaziar; se `run_id` ainda igual, `done` Rust a browsers.
5. **`processar`** (`:336-402`): permit → Jev → checagem `run_id` → erro ou decisão → `registrar_verdict("rust")`, stats → `decision` a browsers → sleep `pace_ms` → drop permit → se golpe: `chaves[m.chave]` → `trace_lock` → `spawn_blocking(trace)` → checagem `run_id` → `trace_ms` → `para_desenho` → `trace` + `enrich_truth` a browsers.
6. **Worker conecta** (`:404-461`): slot `worker` = canal; `hello`; `status connected`; loop: canal → socket; socket → JSON → `side = python` → guarda `status` / registra `decision` / `enrich_truth` → browsers. Desconexão: limpa slot se for o mesmo canal (`same_channel`) e emite `offline`.
7. **Worker Python** (`worker.py:298-317`): `connect(WS_URL, proxy=None, open_timeout=10)`; `for raw in ws: handle_raw`; queda → `run = None`, `ws = None`, sleep 2 s; ao encerrar cancela tasks.
8. **`hello`** (`worker.py:156-172`): se sem grafo ou modelo: `status loading`, `to_thread(load_data)` (`Graph.load`, `chaves.json`, `gc.collect()`, `memoria_mb`), aquecimento sob semáforo; exceção → `error` + `raise` (reconecta). Depois `status ready`.
9. **`run`** (`worker.py:211-216`): novo `Semaphore(concurrency)`, `pace_ms`, `Run`, `maybe_done` (total 0).
10. **`message`** → `process_message` (`worker.py:246-286`): `async with sem` → checagem identidade → `classificar` → veredito, custo, stats → `emit decision` → sleep `pace_ms` → fora do semáforo: se `sent` e golpe → `async with trace_lock` → checagens → `to_thread(trace_for_message)` → `emit trace`; exceções → `error`; `finally finish_message` → `processed += 1` → `maybe_done`.

## Fluxos Alternativos
- **`TYPESAFE_API_KEY` ausente:** servidor aborta no boot (`?` em `from_env`).
- **Aquecimento Jev falha:** aviso em stderr, `model = "jev-latest"`.
- **`python` não encontrado / worker.py ausente:** aviso; lado Python fica `offline`.
- **`index.html` ausente:** HTML com `<h1>static/index.html não encontrado</h1>`.
- **Browser lento (`Lagged`):** eventos perdidos na tela, loop continua (`:249`).
- **Erro do Jev na mensagem:** `erros += 1`, evento `error`, sem `decision`, sem veredito registrado.
- **`stop` durante rastreio:** o rastreio termina, resultado descartado (`:389`).
- **Worker: `message` malformado com `id` válido:** conta como processado com erro (`worker.py:184-194`).
- **Worker: `emit` com socket caído:** retorna `False`, invalida `run` (`:136-140`).
- **Worker: `reset` durante `to_thread`:** não cancela a thread; identidade do `Run` descarta o resultado (comentário `:203-206`).
- **Dois browsers:** ambos comandam e veem a mesma corrida.

## Dependências
- Units `decisao-por-ia` (clientes), `rastreio-no-grafo` (grafo), `geracao-de-dados` (arquivos), `relatorio-de-acuracia` (`relatorio`), `interface-tela-dividida` (consumidor).
- Crates: axum 0.7 (ws), tokio (full), futures, serde_json, memory-stats, dotenvy.
- Python: websockets 15 (`websockets.asyncio.client.connect`), asyncio, ctypes/psutil opcional.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Invalidação por `run_id` atômico em vez de cancelar tasks | `server.rs:38,314,341`, `worker.py:203-206` | 🟢 |
| Despacho de todas as mensagens de uma vez; ritmo por lado | `server.rs:313-319`, SPEC §4 | 🟢 |
| Sleep do ritmo dentro do permit (serializa o lado em modo passo a passo) | `server.rs:369-373` | 🟢 |
| Rastreio serializado com mutex async + thread bloqueante | `server.rs:43,379-388` | 🟢 |
| Broadcast para browsers, mpsc unbounded para o worker | `server.rs:34-35` | 🟢 |
| Worker como processo filho `kill_on_drop` | `server.rs:200` | 🟢 |
| `data_dir` canonizado sem `\\?\` e com `/` para o Python | `server.rs:192` | 🟢 |
| Página lida do disco por request | `server.rs:220-226` | 🟢 |
| Worker: `sys.dont_write_bytecode` para não sujar a pasta | `worker.py:8` | 🟢 |
| Worker: validação de esquema dos eventos de entrada | `worker.py:55-76` | 🟢 |
| Worker: `Run` por identidade de objeto | `worker.py:249,268` | 🟢 |
| Percentil nearest-rank idêntico nos dois lados | `server.rs:57-65`, `worker.py:79-83` | 🟢 |

## Estado Interno
Rust: `run_id`, `pace_ms` (atômicos), `verdicts` (por corrida), `rust_status`/`python_status`, slot `worker`, `Stats` por corrida (dentro de `run`). Python: `Worker.run` (identidade), `sem`, `pace_ms`, `graph`, `chaves`, `model`, `memory_mb`, `tasks`.

## Observabilidade
stdout do servidor: `dados: <dir>`, `grafo: ... memória ... MB`, `jev aquecido: <model> em <ms>`, `worker python iniciado (pid)`, `abra http://localhost:8080`, `worker python conectado/desconectado`. stderr: avisos. Worker: `python <type> run=<id> id=<id> <state|verdict>` por emissão; erros de tarefa e conexão em stderr.

## Riscos e Lacunas
- 🟢 Sem autenticação e bind `0.0.0.0` (ver `permissions.md`).
- 🟡 `Lagged` em rajada com browser lento.
- 🟢 `PIX_STEP_MS` inoperante com a tela atual (usa `step:4000`).
- 🟢 O `done` do Rust não é enviado ao worker (irrelevante) e o `done` do Python vem pelo repasse.
- 🟡 Se o Jev falhar em todas as mensagens, `done` sai com `erros = 1000` e `decision_p50 = 0`.
