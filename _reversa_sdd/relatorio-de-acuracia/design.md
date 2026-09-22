# Relatório de acurácia, Design Técnico

> Unit `relatorio-de-acuracia`. Fonte: `src/bin/server.rs`, `static/index.html`. 🟢 salvo indicação.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `App::registrar_verdict` | `(&self, side: &str, id: u32, verdict: &str)` | `()` | `verdicts[side][id] = verdict` |
| `App::relatorio` | `(&self)` | `Value` | evento `report` |
| `requestReport()` (js) | | | envia `{type: "report"}` |
| `showReport(event)` (js) | | | renderiza `#accuracy-report` |
| `matrixCount(data, real, verdict)` (js) | | number | leitura segura da matriz |
| `reportConclusion(sides)` (js) | | string | prosa |
| `hideReport()` (js) | | | |

Evento `report` (servidor → browser):
```json
{"type":"report","run_id":3,"total":1000,"golpes_reais":75,
 "sides":{"rust":{"avaliadas":1000,"matriz":{"golpe":{"golpe":74,"revisar":1,"ok":0},"normal":{"golpe":0,"revisar":8,"ok":917}},
                  "tp":74,"fp":0,"fn":1,"tn":925,"acuracia":0.999,"precisao":1.0,"recall":0.98667},
          "python":{...}}}
```

## Fluxo Principal
1. Durante a corrida, `processar` (Rust) chama `registrar_verdict("rust", id, verdict)` após decisão válida (`server.rs:354`); `handle_worker` chama `registrar_verdict("python", id, verdict)` para cada `decision` do worker (`:430-434`).
2. Tela em `done`/`stopped`: clique em "Relatório de acurácia" → `send({type:"report"})`.
3. Servidor: `relatorio()` (`:86-113`): para cada lado, percorre `mensagens`, pega o veredito registrado, monta `m[(real, pred)]`, calcula tp/fn/fp/tn e métricas com `div` segura; monta `sides`; adiciona `run_id`, `total`, `golpes_reais`. Envia só a browsers (`:279-281`).
4. Tela: `receive(report)` só em `done`/`stopped` sem pendência → `showReport(event)`: valida `matriz` dos dois lados, monta título e nota, para cada lado cria coluna com cabeçalho (nome, "N de T mensagens avaliadas"), tabela "Real / Veredito" × GOLPE, SUSPEITA, OK, células coloridas, métricas Acurácia/Precisão/Recall em % (ou N/D), 3 legendas; `reportConclusion` no rodapé; mostra o overlay.
5. Fechar: botão ou `Escape` → `hideReport()`.

## Fluxos Alternativos
- **Lado sem vereditos:** `avaliadas = 0`, matriz zerada, métricas 0 → tela N/D e frase "X ainda não avaliou mensagens."
- **Corrida interrompida:** relatório parcial com nota.
- **`report` recebido em `running`:** ignorado.
- **Mock:** `mockReport()` gera o mesmo formato a partir de `mockDecisions` e `mockTruth`.
- **Reiniciar:** `start` limpa `verdicts`; o relatório anterior some da tela (`clearRun` → `hideReport`).

## Dependências
- `App.mensagens` (com `golpe_real`) e `App.verdicts`.
- Unit `corrida-em-tempo-real` (registro dos vereditos, comando `report`).
- Unit `interface-tela-dividida` (overlay, `updateControls`, fases).

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Cálculo no servidor, tela só renderiza (verdade não vai ao browser) | `server.rs:86-113` | 🟢 |
| `revisar` tratado como não detectado nas métricas binárias | `server.rs:99`, nota da tela | 🟢 |
| Matriz 2×3 explícita além das métricas | `server.rs:104-107` | 🟢 |
| Divisão segura (0 em vez de NaN) | `server.rs:101` | 🟢 |
| Conclusão em prosa gerada por regras fixas | `reportConclusion` | 🟢 |
| Relatório disponível após `stop` (parcial) | `updateControls`, `showReport` | 🟢 |

## Estado Interno
Servidor: `verdicts: Mutex<HashMap<String, HashMap<u32, String>>>`. Tela: `#report-columns` reconstruído a cada `report`; nenhum estado além do DOM.

## Observabilidade
Nenhuma; o relatório é a própria saída.

## Riscos e Lacunas
- 🟢 `acuracia` divide por `avaliadas` (inclui `revisar` como tn/fn), coerente com a nota da tela.
- 🟡 Não há exportação (CSV/JSON) do relatório; os números do README foram transcritos à mão.
- 🟢 `total` e `golpes_reais` são do dataset inteiro mesmo em relatório parcial; a tela explica.
