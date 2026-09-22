# Interface em tela dividida, Design Técnico

> Unit `interface-tela-dividida`. Fonte: `static/index.html`. 🟢 salvo indicação.

## Interface

Entrada: eventos WebSocket (ver `corrida-em-tempo-real/contracts.md`) ou eventos do mock. Saída: comandos WebSocket e DOM/canvas.

| Símbolo | Assinatura | Observação |
|---------|-----------|------------|
| `receive(event)` | dispatcher | único ponto de entrada de eventos |
| `send(event)` | envia JSON ou roteia para `mockCommand` | fecha o socket em erro |
| `connect()` | abre `ws(s)://host/ws` | backoff `min(10000, 500·2^n)` |
| `start()` / `primaryAction()` / `changePace()` | handlers de UI | |
| `updateControls()` / `updateConnection()` / `setConnection()` | estado dos controles | |
| `clearRun()` / `stopRun()` / `hideFinal()` / `hideReport()` | limpeza | |
| `showMessage(lane, id)` / `setVerdict(lane, verdict, type)` | bolha e selo | |
| `recordSpeed(lane, kind, ms)` / `laneMedian(values)` / `countProcessed(lane)` / `updateAccumulator(lane)` | métricas | |
| `addScam(lane, decision)` / `highlightScam` / `renderDetail(lane)` | lista e painel | |
| `openScam(lane, id, origin)` / `closeScam()` / `updateScamTrace(trace)` / `scoreBar` / `urgencyLabel` / `messageTime` / `traceLines` | modal | |
| `prepareGraph(trace)` / `graphFor(trace)` / `drawGraph(canvas, trace, accent, time)` / `resizeCanvas(view)` / `clearGraph` / `enableGraphHover(view)` / `nodeAt` | canvas | cache `WeakMap` |
| `showTrace(view, trace, animate)` / `drawMoney(view, trace)` / `animateMoney(view)` | painel do dinheiro | |
| `showFinal()` | cartão final | |
| `fitStage()` | `zoom` do frame | também redimensiona canvases |
| `startMock(mode)` / `mockCommand(event)` / `mockTrace` / `mockReport` / `later` / `cancelMock` | simulação | |

Constantes: `SIDES = ['rust','python']`, `NAMES`, `PARTS` (model/engine), `ACCENTS` (`#ff2d95`, `#6985f6`), `ACCENT_RGB`, `TYPES` (8 rótulos pt-br), `MOCK`, formatadores `Intl` (`integer`, `grouped`, `decimal`, `seconds`, `currency` 6 casas, `currencyShort`).

## Fluxo Principal
1. **Boot** (`:1597-1603`): clona o template para cada lado (`lanes[side]` com `ui` = mapa de `data-field`), monta a `detailView` (cópia do painel do grafo para o modal), `fitStage()`, e `connect()` ou, em mock, marca os dois lados `ready`.
2. **Conexão** (`connect`): `open` → `transportReady = true` → `updateConnection`; `message` → `JSON.parse` → `receive`; `close` → limpa `sideStatus`, pendências e agenda reconexão.
3. **Iniciar** (`start`): `pending = true`; se já houve corrida, `pendingStart = mode` e envia `reset` (o `reset` recebido dispara `start`); senão envia `start`.
4. **`run`** (`receive`): `clearRun()`, adota `runId/total/mode/concurrency/paceMs`, `phase = running`, ajusta o `select`, mostra `total` nos lados; aplica ritmo trocado durante a espera.
5. **`message`**: cacheia `{texto, remetente, chave, ts}` por id.
6. **`decision`**: ignora se o lado já deu `done`; `recordSpeed`, `showMessage`, `setVerdict`, `addScam` se golpe, `ok++` se ok, `countProcessed`.
7. **`trace`**: `recordSpeed`, guarda em `lane.traces`; se `lane.latestId === id`, `showTrace(lane, event, true)`; `updateScamTrace` para o modal.
8. **`error`**: `countProcessed`, `setVerdict(lane, 'error')`.
9. **`done`**: `lane.done = totals`; `showFinal()` (só age com os dois).
10. **`stop`**: `stopRun()`; **`pace`**: sincroniza; **`status`**: conexão e memória; **`report`**: unit `relatorio-de-acuracia`.

## Fluxos Alternativos
- **Socket fechado ao enviar:** `send` reseta pendências, `transportReady = false`, atualiza indicador.
- **JSON inválido recebido:** indicador "Evento inválido", evento ignorado.
- **`run` sem `run_id`:** ignorado.
- **Decisão após `done` do lado:** ignorada.
- **Trace de golpe que não é o mais recente:** guardado, não desenhado no painel (mas atualiza o modal se for o aberto).
- **Trace sem `nodes`:** painel mostra "Este rastreio não incluiu o desenho das contas."
- **Sem `location.host` (arquivo local sem `?mock`):** "Use o servidor ou ?mock=1".
- **`pagehide`/`pageshow`:** fecha tudo e reconecta ao voltar do bfcache.
- **Ritmo trocado enquanto `start` está pendente:** `pendingStart` atualizado; aplicado após o `run`.

## Dependências
- Servidor (`/ws`) e protocolo de eventos.
- APIs do browser: WebSocket, Canvas 2D, Web Animations (`element.animate`), `Intl.NumberFormat`, `matchMedia`, `requestAnimationFrame`, CSS `zoom`.
- Sem bibliotecas.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Template único clonado por lado; campos por `data-field` | `:398-421` | 🟢 |
| Frame fixo 1920 px + `zoom` em vez de layout fluido (gravação) | `fitStage`, CSS `#frame` | 🟢 |
| Mediana como estatística ao vivo (p50 oficial só no `done`) | `laneMedian` | 🟢 |
| Lista de golpes com prepend e texto completo (pedido do público leigo) | `addScam`, brainstorm | 🟢 |
| Painel do grafo sempre mostra o golpe mais recente | `lane.latestId` | 🟢 |
| Layout radial por profundidade com deslocamento angular por anel (0,13 rad) | `prepareGraph:465-475` | 🟢 |
| Cache de layout por evento em `WeakMap` | `graphCache` | 🟢 |
| Estrelas de fundo determinísticas (`seeded(42)`) | `:391-392` | 🟢 |
| Onda de 300 ms curta para não mascarar a diferença real de tempo | `showTrace`, SPEC §5 | 🟢 |
| `revisar` rotulado SUSPEITA; erro rotulado ERRO | `setVerdict` | 🟢 |
| Custo do Python rotulado "estimado" | `showFinal`, `openScam` | 🟢 |
| Modo mock passando por `receive` (mesmo caminho do real) | `startMock` | 🟢 |
| Overflow do body travado com modal aberto; foco preso | `openScam`, `keydown` | 🟢 |

## Estado Interno
Globais: `runId, total, runMode, concurrency, paceMs, phase, requestedStartMode, pending, pendingStart, transportReady, socket, reconnectTimer, reconnectAttempt, pageLeaving, sideStatus, messages (Map), activeDetail, previousOverflow`. Por lado (`lanes[side]`): `processed, ok, done, flash, coins, decisionMs[], traceMs[], graph, graphAnimation, waveProgress, scams (Map id→entry), traces (Map id→trace), latestId, selectedId, currentId`. Mock: `mockRun, mockGeneration, mockTimers, mockDecisions`.

## Observabilidade
Nenhum log; estado visível na tela (indicador de conexão, "Parado", contadores). Erros de parse viram texto no indicador.

## Riscos e Lacunas
- 🟡 `docs/tela-corrida.png` desatualizado (título "PIX RACE").
- 🟢 O `select` não expõe `burst`; benchmark do README exige cliente customizado ou edição do HTML.
- 🟢 `zoom` CSS é não padrão em navegadores antigos (funciona em Chromium/Firefox recentes).
- 🟡 `Lagged` no servidor pode fazer o contador não chegar a `total` sem `done` (mas `done` chega, e o cartão aparece).
- 🟢 Golpes de `revisar` não entram em "golpes" nem em "ok" no acumulador.
