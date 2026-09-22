# Interface em tela dividida, Tarefas de Implementação

> Unit `interface-tela-dividida`. Reimplementação a partir de `static/index.html`.

## Pré-requisitos
- [ ] Protocolo em `corrida-em-tempo-real/contracts.md`
- [ ] Tokens visuais (cores, tipografia, espaçamentos) do agente Design System (`design-system.md`, quando gerado)
- [ ] Screenshots de referência em `docs/`

## Tarefas

- [ ] T-01, Estrutura HTML: topbar (título, conexão, ritmo, Iniciar, Relatório), `#race`, rodapé, `#final`, `#accuracy-report`, `template#lane-template`, `#scam-modal`
  - Origem no legado: `static/index.html:209-347`
  - Critério de pronto: todos os `id` e `data-field` listados em `code-analysis.md` §frontend existem
  - Confiança: 🟢

- [ ] T-02, Constantes, formatadores `Intl` pt-BR e clonagem das lanes
  - Origem no legado: `static/index.html:349-421`
  - Critério de pronto: dois painéis com rótulos "JEV · DECISÃO p50", "RUST · RASTREIO p50", "RUST · MEMÓRIA" (e equivalentes Python)
  - Confiança: 🟢

- [ ] T-03, Conexão WebSocket com reconexão, `send`, indicador de conexão
  - Origem no legado: `static/index.html:1326-1372`, `updateConnection`
  - Critério de pronto: derrubar o servidor mostra "Reconectando..." e reconecta ao voltar
  - Confiança: 🟢

- [ ] T-04, Controles: `start`, `primaryAction`, `changePace`, `updateControls`
  - Origem no legado: `static/index.html:1374-1400`, `:442-449`
  - Critério de pronto: sequência Iniciar → Parar → Reiniciar envia os comandos certos
  - Confiança: 🟢

- [ ] T-05, `receive` com fase, `runId`, descarte e roteamento de todos os tipos
  - Origem no legado: `static/index.html:1220-1322`
  - Critério de pronto: tabela de descarte de `contracts.md` reproduzida
  - Confiança: 🟢

- [ ] T-06, Painel por lado: `showMessage`, `setVerdict` (com flash), `recordSpeed`/`laneMedian`, `countProcessed`, `updateAccumulator`
  - Origem no legado: `static/index.html:529-552,990-1020`
  - Critério de pronto: cenários Gherkin de `requirements.md`
  - Confiança: 🟢

- [ ] T-07, Lista de golpes e seleção: `addScam`, `highlightScam`, `renderDetail`
  - Origem no legado: `static/index.html:559-618`
  - Critério de pronto: item no topo com remetente, texto, tipo, %; clique abre modal
  - Confiança: 🟢

- [ ] T-08, Grafo em canvas: `prepareGraph`, `drawGraph`, `resizeCanvas`, `enableGraphHover`, estrelas
  - Origem no legado: `static/index.html:794-940`
  - Critério de pronto: raiz no centro, anéis por profundidade, laranjas/saques destacados, tooltip com id/prof/suspeita
  - Confiança: 🟢

- [ ] T-09, Painel do dinheiro: `showTrace`, `drawMoney`, `animateMoney`, `clearGraph`
  - Origem no legado: `static/index.html:941-1068`
  - Critério de pronto: textos "laranjas: a/r · saque: a/r", "N contas · X ms" e resumo em prosa
  - Confiança: 🟢

- [ ] T-10, Modal de detalhes: `openScam`, `closeScam`, `updateScamTrace`, `scoreBar`, `traceLines`, foco preso, `Escape`
  - Origem no legado: `static/index.html:638-792`, `:1569-1583`
  - Critério de pronto: barras (golpe, pede Pix, urgência, confiança), dados técnicos, contas laranja/saque, `trace` tardio atualiza
  - Confiança: 🟢

- [ ] T-11, Cartão final `showFinal` e `stopRun`
  - Origem no legado: `static/index.html:1069-1105`, `:622-636`
  - Critério de pronto: só com os dois `done`; "Custo estimado (USD)" no Python
  - Confiança: 🟢

- [ ] T-12, `fitStage` com `zoom` e `resize`
  - Origem no legado: `static/index.html:433-439`, `:1584`
  - Critério de pronto: sem rolagem horizontal em 1280 px
  - Confiança: 🟢

- [ ] T-13, Modo mock completo
  - Origem no legado: `static/index.html:1403-1557`
  - Critério de pronto: `?mock=1` roda 24 mensagens, `pace`, `stop`, `report`, cartão final
  - Confiança: 🟢

- [ ] T-14, `pagehide`/`pageshow`, `prefers-reduced-motion`
  - Origem no legado: `static/index.html:1584-1596`, CSS `:206`
  - Critério de pronto: animações desligadas com a preferência ativa
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Corrida completa em `?mock=1` (smoke E2E sem rede)
- [ ] TT-02, `receive` com eventos fora de ordem e `run_id` antigo (unitário, injetando via função exposta ou módulo)
- [ ] TT-03, `laneMedian` com 1, 2, 3 e 1.000 valores
- [ ] TT-04, `prepareGraph` com `nodes` inválidos, duplicados e > 800
- [ ] TT-05, Modal: foco preso com Tab/Shift+Tab; `Escape` fecha
- [ ] TT-06, Cartão final não aparece com um só `done`

## Ordem Sugerida
1. T-01/T-02 → T-05 (receive) → T-03/T-04 → T-06/T-07 → T-08/T-09 → T-11 → T-10 → T-13 (mock) → T-12/T-14.
2. TT-01 assim que T-13 existir; usar o mock como harness dos demais testes.

## Lacunas Pendentes (🔴)
Nenhuma. Observação 🟡: confirmar se o título final da tela é "DETECTOR DE GOLPE" (HTML) ou "PIX RACE" (screenshot).
