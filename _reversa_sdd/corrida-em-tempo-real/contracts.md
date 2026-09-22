# Corrida em tempo real, Contrato do protocolo WebSocket

> Unit `corrida-em-tempo-real`. Extraído de `src/bin/server.rs`, `py-worker/worker.py`, `static/index.html`. 🟢. Frames de texto, um objeto JSON por frame, sempre com `type`.

## Endpoints

| Endpoint | Cliente | Direção |
|---|---|---|
| `ws://<host>:8080/ws` | browser | bidirecional; servidor faz broadcast a todos os browsers |
| `ws://127.0.0.1:8080/ws/worker` | worker Python | bidirecional; canal dedicado |

Ao conectar em `/ws`, o servidor envia imediatamente os dois `status` atuais (rust, python). Ao conectar em `/ws/worker`, o servidor envia `hello` e publica `status {side: python, state: connected}` aos browsers.

## Browser → servidor

| type | Campos | Efeito |
|---|---|---|
| `start` | `mode: "step" \| "step:<ms>" \| "serial" \| "burst"` (default `step`) | nova corrida: `reset` a todos, `run`, mensagens |
| `pace` | `mode` (default `serial`) | troca o ritmo; `pace` a todos |
| `stop` | | `stop` a todos; corrida invalidada |
| `report` | | `report` só ao browser (todos os browsers) |
| `reset` | | `reset` a todos; corrida invalidada |

Outros `type` ou JSON inválido: ignorados.

`pace_de(mode)`: `step` → `PIX_STEP_MS` (2500); `step:<ms>` → `<ms>` (parse falho → padrão); qualquer outro → 0.

## Servidor → browser e worker (controle)

| type | Campos | Notas |
|---|---|---|
| `reset` | | limpa a tela / `run = None` |
| `run` | `run_id: u32, mode: string, total: usize, concurrency: 1 \| 8, pace_ms: u64` | `concurrency = 8` só em `burst` |
| `message` | `run_id, id: u32, ts: u32, remetente, texto, chave` | sem `golpe_real` |
| `pace` | `run_id, mode, ms: u64` | |
| `stop` | `run_id` | o `run_id` da corrida interrompida |
| `hello` | `data_dir: string` | só worker; caminho absoluto com `/` |

## Lado → servidor → browser (resultados)

O worker emite sem `side`; o servidor injeta `side: "python"`. O lado Rust emite direto com `side: "rust"`.

| type | Campos | Notas |
|---|---|---|
| `status` | `side, state: connected \| loading \| ready \| offline, nodes?, edges?, load_ms?, memory_mb?, model?` | último `status` de cada lado é guardado e reenviado a browsers novos |
| `decision` | `side, run_id, id, latency_ms, golpe, tipo, urgencia, pede_pix, verdict, tokens_in, tokens_out, cost_usd, model, tipo_confianca?` | `tipo_confianca` só Rust |
| `trace` | `side, run_id, id, chave, latency_ms, visitados, arestas_sub, laranjas: u32[], saque: u32[], nodes: [[id, prof, suspeita(3 casas)]], edges: [[src, dst]], truth: {laranjas_reais, laranjas_acertadas, saque_reais, saque_acertadas}` | `truth` adicionado pelo servidor |
| `error` | `side, run_id?, id?, message` | `id` ausente em erros de inicialização/parse |
| `done` | `side, run_id, totals: {messages, golpes, erros, decision_p50_ms, decision_p95_ms, trace_p50_ms, trace_p95_ms, cost_usd, total_ms}` | Rust: só browsers; Python: repassado |
| `report` | `run_id, total, golpes_reais, sides: {rust: Lado, python: Lado}` | `Lado = {avaliadas, matriz: {golpe: {golpe, revisar, ok}, normal: {golpe, revisar, ok}}, tp, fp, fn, tn, acuracia, precisao, recall}` |

## Regras de validação no worker (`parse_event`)

| type | Campos obrigatórios e tipos |
|---|---|
| `hello` | `data_dir: str` não vazio |
| `run` | `run_id: int ≥ 0`, `total: int ≥ 0` |
| `reset` | nenhum |
| `message` | `run_id: int ≥ 0`, `id: int ≥ 0`, `ts: int ≥ 0`, `remetente: str`, `texto: str`, `chave: str` |
| outros | sem validação (`stop`, `pace` usam `.get`) |

`bool` não é aceito como `int` (`type(value) is not kind`).

## Regras de descarte

- Servidor: `processar` descarta após a chamada ao modelo e após o rastreio se `run_id` mudou.
- Worker: descarta `message` de `run_id ≠ run.run_id`, de corrida `done`, ou `id` já visto; `emit` descarta se `self.run is not run`.
- Browser: descarta qualquer evento com `run_id` presente e ≠ `runId`; em `stopped` descarta `message/decision/trace/error/done`.

## Exemplo de sequência (ritmo narrado)

```
B→S start {mode: "step:4000"}
S→* reset
S→* run {run_id: 3, mode: "step:4000", total: 1000, concurrency: 1, pace_ms: 4000}
S→* message {run_id: 3, id: 0, ...} ... message {id: 999}
R→B decision {side: rust, id: 0, ...}          (t ≈ 0,3 s)
P→S→B decision {side: python, id: 0, ...}      (t ≈ 1,1 s)
R→B trace {side: rust, id: 0, truth: {...}}    (se golpe)
R→B decision {id: 1}                           (t ≈ 4,3 s)
...
R→B done {side: rust, totals}
P→S→B done {side: python, totals}
B→S report
S→B report {...}
```
