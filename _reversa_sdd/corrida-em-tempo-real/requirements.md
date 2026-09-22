# Corrida em tempo real

> Unit `corrida-em-tempo-real`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Orquestra a corrida: o servidor Rust (axum, porta 8080) serve a tela, recebe comandos do browser, despacha as mesmas mensagens aos dois lados, executa o lado Rust no próprio processo, sobe e conversa com o worker Python por WebSocket, aplica ritmo e concorrência iguais, enriquece rastreios com a verdade de referência e emite estatísticas finais. O worker Python é o espelho do lado Rust em processo separado.

## Responsabilidades
- Servir `GET /` (tela) e aceitar WebSocket em `/ws` (browsers) e `/ws/worker` (worker).
- Carregar grafo, mensagens, chaves e verdade no boot; aquecer o modelo; publicar `status` por lado.
- Subir o worker Python automaticamente (`python py-worker/worker.py`), salvo `PIX_NO_WORKER`.
- Comandos: `start`, `pace`, `stop`, `report`, `reset`; invalidação por `run_id`.
- Lado Rust: decisão sob semáforo, ritmo, rastreio serializado, eventos `decision`/`trace`/`error`/`done`.
- Worker Python: mesma sequência com DeepSeek e `trace.py`; reconexão; validação de eventos; `done`.
- Injetar `side="python"` e `truth` nos eventos do worker; registrar vereditos para o relatório.

## Regras de Negócio
- RN-01 Todas as mensagens são despachadas de uma vez, na ordem de `mensagens.jsonl`, a browsers e worker, sem `golpe_real`. 🟢 `server.rs:313-319`
- RN-06 `concurrency = 8` se `mode == "burst"`, senão 1; informado no evento `run` e obedecido pelo worker (`Semaphore`). 🟢 `server.rs:306`, `worker.py:213`
- RN-30 `start`, `stop`, `reset` incrementam `run_id`; tarefas cujo `run_id` divergiu descartam o resultado em todas as camadas. 🟢 `server.rs:264-289,314,341,389`, `worker.py:219,249-277`
- RN-31 `pace` troca o ritmo ao vivo; `pace_de`: `step` → `PIX_STEP_MS` (2500), `step:<ms>` → ms, outro → 0. 🟢 `server.rs:295-300`
- RN-32 Após emitir `decision`, o lado dorme `pace_ms` ainda segurando a vaga do semáforo. 🟢 `server.rs:369-373`, `worker.py:263-264`
- RN-04/RN-26 Só `golpe` rastreia; rastreio sob `trace_lock`, em `spawn_blocking` / `to_thread`; `t0 = ts` da mensagem. 🟢
- RN-28 `enrich_truth` adiciona `truth` a todo `trace` (qualquer lado), comparando `laranjas`/`saque` com `meta.json` pela chave; chave sem quadrilha → zeros. 🟢 `server.rs:117-139`
- RN-34 `done` de um lado quando todas as mensagens terminaram (Rust: join das tasks; Python: `processed == total`, contando erros). Rust envia `done` só a browsers. 🟢 `server.rs:320-333`, `worker.py:293-296`
- `status` inicial: Rust `ready` com `nodes`, `edges`, `load_ms`, `memory_mb`, `model`; Python `offline` até conectar; browsers novos recebem os dois status ao conectar. 🟢 `server.rs:179-180,239-244`
- Worker: `hello {data_dir}` ao conectar; `status loading` → `ready` (com memória) após carregar grafo e aquecer; erro de inicialização emite `error` e reconecta preservando o grafo. 🟢 `worker.py:156-172`
- Worker valida eventos (`parse_event`): `hello.data_dir` str não vazia; `run.run_id/total` int ≥ 0; `message` com `run_id, id, ts` int e `remetente, texto, chave` str. Evento inválido → `error`; `message` inválido com id válido conta como erro da corrida. 🟢 `worker.py:55-76,173-196`
- Worker ignora `message` de `run_id` antigo, de corrida concluída ou id repetido. 🟢 `worker.py:218-222`
- Um worker novo substitui o slot; o antigo, ao cair, não marca `offline` se não for mais o slot. 🟢 `server.rs:404-461`
- `PIX_STEP_MS` (padrão 2500) só vale para `mode == "step"` sem sufixo; a tela usa `step:4000`. 🟢
- Página lida do disco a cada `GET /` (permite editar a tela sem recompilar). 🟢 `server.rs:220-226`
- Bind `0.0.0.0:8080`, sem autenticação. 🟢 `server.rs:214`

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Boot: carregar dados, montar grafo, aquecer Jev, publicar `status` Rust | Must | log "grafo: N contas, M transações, carga X ms" e `status ready` |
| RF-02 | Servir `GET /` com `static/index.html` | Must | 200 com HTML; 200 com mensagem de erro se o arquivo faltar |
| RF-03 | Aceitar `/ws` e enviar os 2 `status` atuais ao conectar | Must | primeiro frame após upgrade |
| RF-04 | Comandos `start`, `pace`, `stop`, `report`, `reset` conforme tabela em `contracts.md` | Must | eventos correspondentes |
| RF-05 | Despachar `run` + todas as `message` a browsers e worker | Must | 1.000 eventos `message` por corrida |
| RF-06 | Lado Rust por mensagem: decisão, ritmo, rastreio, eventos | Must | `decision` para cada mensagem; `trace` para cada `golpe` |
| RF-07 | `done` Rust com p50/p95 (nearest-rank), golpes, erros, custo, `total_ms` | Must | evento após a última task |
| RF-08 | Subir o worker Python como processo filho com `kill_on_drop` | Should | log "worker python iniciado (pid ...)"; `PIX_NO_WORKER=1` desliga |
| RF-09 | Aceitar `/ws/worker`, enviar `hello`, repassar eventos com `side` e `truth` | Must | browser recebe `status python connected` |
| RF-10 | Worker: conectar, reconectar a cada 2 s, carregar grafo, aquecer, `ready` | Must | `status ready` com `nodes/edges/load_ms/memory_mb/model` |
| RF-11 | Worker: processar mensagens com semáforo, ritmo, rastreio serial, `done` | Must | `done` após `total` mensagens |
| RF-12 | Worker: validar eventos e nunca travar por entrada malformada | Should | JSON inválido → `error`, worker segue vivo |
| RF-13 | Invalidação por `run_id` em servidor, worker e browser | Must | após `stop`, nenhum `decision`/`trace` da corrida antiga chega à tela |
| RF-14 | Medir memória residente de cada lado no `status` | Could | `memory_mb` numérico |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | rastreio fora do runtime async (`spawn_blocking`, `to_thread`) | `server.rs:381`, `worker.py:274` | 🟢 |
| Performance | broadcast com buffer 8192; `Lagged` ignorado | `server.rs:177,249` | 🟢 |
| Disponibilidade | worker reconecta indefinidamente; browser reconecta com backoff | `worker.py:298-311` | 🟢 |
| Disponibilidade | `open_timeout=10`, `proxy=None` no worker | `worker.py:301` | 🟢 |
| Escalabilidade | múltiplos browsers compartilham a corrida (broadcast) | `server.rs:34` | 🟢 |
| Segurança | nenhuma; bind `0.0.0.0` | `server.rs:214` | 🟢 |
| Consistência | `send_lock` no worker serializa envios; `allow_nan=False` | `worker.py:130,136` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado servidor e worker prontos
Quando o browser envia {"type":"start","mode":"step:4000"}
Então todos recebem reset, depois run com concurrency 1 e pace_ms 4000, depois 1000 message
E cada lado emite uma decision por mensagem, esperando 4 s entre decisões

Dado uma corrida em andamento em ritmo narrado
Quando o browser envia {"type":"pace","mode":"serial"}
Então todos recebem pace com ms 0 e as próximas decisões saem sem espera

Dado uma corrida em andamento
Quando o browser envia {"type":"stop"}
Então todos recebem stop com o run_id da corrida e nenhum decision/trace/done dessa corrida chega ao browser depois

Dado um trace do worker para a chave 51942117050
Quando o servidor repassa ao browser
Então o evento contém side "python" e truth {laranjas_reais: 14, laranjas_acertadas: N, saque_reais: 2, saque_acertadas: M}

Dado o worker desconectado
Quando ele volta e recebe hello
Então emite status loading e ready sem recarregar o grafo se já estava carregado

Dado o worker recebe um message sem o campo texto, com id 17 e run_id atual
Quando processa
Então emite error com id 17, conta um erro e a corrida ainda chega a done
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Protocolo e invalidação por run_id | Must | tudo depende |
| Lado Rust e worker com ritmo/concorrência iguais | Must | justiça da comparação |
| truth e registro de vereditos | Must | placar e relatório |
| Spawn automático do worker | Should | `PIX_NO_WORKER` cobre o manual |
| Memória no status | Could | informativo |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/bin/server.rs` | `main`, `index`, `ws_browser`, `ws_worker`, `handle_browser`, `comando_browser`, `pace_de`, `run`, `processar`, `handle_worker`, `App::{to_*, registrar_verdict, enrich_truth}`, `percentil` | 🟢 |
| `py-worker/worker.py` | `Worker`, `Run`, `parse_event`, `percentil`, `memoria_mb`, `main` | 🟢 |
| `src/bin/server.rs:86-113` | `relatorio` | ver unit `relatorio-de-acuracia` |
