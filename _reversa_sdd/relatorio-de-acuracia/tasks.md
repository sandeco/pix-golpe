# Relatório de acurácia, Tarefas de Implementação

> Unit `relatorio-de-acuracia`. Reimplementação a partir de `src/bin/server.rs` e `static/index.html`.

## Pré-requisitos
- [ ] Unit `corrida-em-tempo-real` emitindo `decision` e mantendo `verdicts`
- [ ] Unit `interface-tela-dividida` com fases e overlay `#accuracy-report`

## Tarefas

- [ ] T-01, `registrar_verdict` nos dois pontos (lado Rust e repasse do worker); limpar no `start`
  - Origem no legado: `src/bin/server.rs:81-83,268,354,430-434`
  - Critério de pronto: após uma corrida, `verdicts.rust.len == decisões válidas`
  - Confiança: 🟢

- [ ] T-02, `relatorio()`: matriz real × veredito, tp/fn/fp/tn, métricas com divisão segura, `total`, `golpes_reais`
  - Origem no legado: `src/bin/server.rs:86-113`
  - Critério de pronto: cenários Gherkin de `requirements.md`
  - Confiança: 🟢

- [ ] T-03, Comando `report` → `relatorio()` só a browsers
  - Origem no legado: `src/bin/server.rs:279-281`
  - Critério de pronto: worker não recebe `report`
  - Confiança: 🟢

- [ ] T-04, Tela: `requestReport`, habilitação do botão, `receive(report)` só em `done`/`stopped`
  - Origem no legado: `static/index.html` `updateControls`, `requestReport`, `receive`
  - Critério de pronto: botão desabilitado em `running`
  - Confiança: 🟢

- [ ] T-05, Tela: `showReport` (título, nota, colunas, matriz 2×3 com cores, métricas em %, legendas)
  - Origem no legado: `static/index.html:1152-1200` (aprox.), `docs/relatorio-acuracia.png`
  - Critério de pronto: layout equivalente ao screenshot; N/D quando denominador zero
  - Confiança: 🟢

- [ ] T-06, Tela: `reportConclusion` com todas as frases
  - Origem no legado: `static/index.html:1123-1150`
  - Critério de pronto: 7 frases possíveis cobertas por teste
  - Confiança: 🟢

- [ ] T-07, Tela: `hideReport` por botão e `Escape`; `clearRun` esconde
  - Origem no legado: `static/index.html` `hideReport`, `keydown`
  - Critério de pronto: overlay fecha
  - Confiança: 🟢

- [ ] T-08, Mock: `mockReport` com `mockTruth`
  - Origem no legado: `static/index.html:1069-1086`
  - Critério de pronto: `?mock=1` mostra relatório coerente (screenshot: 24 avaliadas, 14 golpes reais)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, `relatorio()` com vereditos sintéticos: caso do README (74/1/0 e 0/8/917) e caso vazio
- [ ] TT-02, `reportConclusion` para cada ramo (iguais, diferentes, sem avaliação, sem golpe real, pegou todos, perdeu N, quantidades diferentes)
- [ ] TT-03, Botão desabilitado em `running`, habilitado em `done` e `stopped`
- [ ] TT-04, Relatório parcial após `stop`

## Ordem Sugerida
1. T-01 → T-02 → T-03 (servidor) → T-04 → T-05 → T-06 → T-07 → T-08 (tela).

## Lacunas Pendentes (🔴)
Nenhuma.
