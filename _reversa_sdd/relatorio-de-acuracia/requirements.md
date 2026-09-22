# Relatório de acurácia

> Unit `relatorio-de-acuracia`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Ao terminar ou parar uma corrida, o apresentador pode abrir a matriz de confusão de cada lado (real × veredito) com acurácia, precisão e recall, mais uma conclusão em prosa comparando falsos alarmes e golpes perdidos. O servidor calcula sobre os vereditos registrados da corrida atual usando `golpe_real`; a tela renderiza.

## Responsabilidades
- Servidor: registrar o veredito de cada lado por mensagem (`verdicts[side][id]`), limpar no `start`, calcular a matriz e as métricas sob demanda (`report`).
- Tela: habilitar o botão só em `done`/`stopped`, pedir o relatório, renderizar matriz 2×3 por lado, métricas em %, legendas e conclusão; fechar com botão ou `Escape`.
- Cartão final (unit `interface-tela-dividida`) mostra golpes detectados e custo, não acurácia.

## Regras de Negócio
- RN-40 Matriz por lado só sobre mensagens com veredito registrado (`avaliadas`); linhas real ∈ {golpe, normal} (de `golpe_real`), colunas veredito ∈ {golpe, revisar, ok}; qualquer veredito desconhecido cai em `revisar`. 🟢 `server.rs:86-97`
- RN-41 `tp = (golpe,golpe)`, `fn = (golpe,ok) + (golpe,revisar)`, `fp = (normal,golpe)`, `tn = (normal,ok) + (normal,revisar)`. 🟢 `server.rs:99`
- RN-42 `acuracia = (tp+tn)/avaliadas`, `precisao = tp/(tp+fp)`, `recall = tp/(tp+fn)`; denominador zero → 0 (tela mostra "N/D"). 🟢 `server.rs:101-109`
- `golpes_reais` = total de mensagens com `golpe_real` no dataset (75), `total` = 1.000, independentemente do que foi avaliado. 🟢 `server.rs:112-113`
- Erros (`error`) não registram veredito, logo não entram em `avaliadas`. 🟢 `server.rs:344-350`
- `verdicts` é limpo no `start`; `stop` e `reset` não limpam (relatório de corrida interrompida continua disponível até o próximo `start`). 🟢 `server.rs:268`
- Tela: botão habilitado só com transporte, sem comando pendente e `phase ∈ {done, stopped}`; evento `report` fora dessas fases é ignorado. 🟢 `updateControls`, `receive(report)`
- Tela exige `sides.rust.matriz` e `sides.python.matriz` para renderizar. 🟢 `showReport`
- Título: "Relatório de acurácia · N mensagens avaliadas · G golpes reais" (N único se igual nos lados, senão "N (Jev) / M (DeepSeek)"); nota "Golpes reais no conjunto de 1000 mensagens." + "Relatório parcial: métricas apenas das mensagens avaliadas." se algum lado avaliou menos que o total + "Golpes perdidos incluem SUSPEITA e OK. N/D: sem casos para calcular." 🟢 `showReport`, screenshot
- Conclusão em prosa (`reportConclusion`): compara falsos alarmes ("Os dois tiveram N falsos alarmes cada." / "Nenhum dos lados deu falso alarme." / "X teve menos falsos alarmes (a contra b)."), depois por lado: "ainda não avaliou mensagens." / "Nenhum golpe real entre as mensagens avaliadas pelo X." / "X pegou todos os golpes avaliados." / "X deixou passar N golpe(s)."; e "Os lados avaliaram quantidades diferentes de mensagens." se aplicável. 🟢 `reportConclusion`
- Células: acerto (golpe,golpe) em verde; erros (normal,golpe) e (golpe,ok) em vermelho; demais neutras. 🟢 `showReport:838`, screenshot
- Mock: `mockReport` calcula a mesma matriz localmente com `mockTruth`. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Registrar veredito por lado e id durante a corrida | Must | `verdicts` preenchido pelos dois lados |
| RF-02 | Calcular matriz e métricas sob `report` | Must | JSON conforme `contracts.md` da corrida |
| RF-03 | Botão "Relatório de acurácia" habilitado só em `done`/`stopped` | Must | desabilitado durante `running` |
| RF-04 | Renderizar matriz 2×3 por lado com cores, métricas em % pt-BR e legendas | Must | screenshot `docs/relatorio-acuracia.png` |
| RF-05 | Conclusão em prosa | Should | frases da lista acima |
| RF-06 | Relatório parcial de corrida interrompida | Should | nota "Relatório parcial" |
| RF-07 | Fechar com botão e `Escape` | Could | |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Consistência | verdade de referência nunca sai do servidor em bruto; só agregados | `server.rs:86-113` | 🟢 |
| Performance | cálculo O(1000) por pedido, sob `Mutex` | `server.rs:87` | 🟢 |
| Localização | percentuais com 1 casa em pt-BR ("83,3%") | screenshot | 🟢 |

## Critérios de Aceitação

```gherkin
Dado uma corrida concluída em que o lado Rust deu 74 golpes certos, 1 golpe como revisar, 8 normais como revisar e 917 normais como ok
Quando o browser pede report
Então rust.matriz = {golpe:{golpe:74, revisar:1, ok:0}, normal:{golpe:0, revisar:8, ok:917}}, tp=74, fn=1, fp=0, tn=925, acuracia=0.999, precisao=1.0, recall=0.9867

Dado um lado sem nenhum veredito registrado
Quando calculo as métricas
Então avaliadas = 0 e acuracia, precisao e recall = 0 (tela mostra N/D)

Dado a corrida parada com 143 avaliadas no Rust e 38 no Python
Quando abro o relatório
Então o título mostra "143 (Jev) / 38 (DeepSeek) mensagens avaliadas" e a nota inclui "Relatório parcial"

Dado que os dois lados tiveram 2 falsos alarmes e deixaram passar 2 golpes cada
Quando leio a conclusão
Então o texto é "Os dois tiveram 2 falsos alarmes cada. Jev deixou passar 2 golpes. DeepSeek deixou passar 2 golpes."
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Registro e cálculo | Must | prova de honestidade do vídeo |
| Renderização da matriz | Must | |
| Conclusão em prosa | Should | ajuda o público leigo |
| Parcial | Should | corridas interrompidas são comuns na gravação |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/bin/server.rs:41-42,81-83,86-113,268,279-281,354,430-434` | `verdicts`, `registrar_verdict`, `relatorio`, comando `report` | 🟢 |
| `static/index.html` | `requestReport`, `hideReport`, `matrixCount`, `reportConclusion`, `showReport`, `mockReport`, `updateControls` | 🟢 |
| `docs/relatorio-acuracia.png` | referência visual | 🟢 |
