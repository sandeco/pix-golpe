# Interface em tela dividida

> Unit `interface-tela-dividida`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Página única (`static/index.html`) pensada para gravação em 16:9: dois painéis lado a lado (Rust + Jev à esquerda, Python + DeepSeek à direita) mostram, em tempo real, a mensagem atual, o veredito, contadores, velocidades medianas, o caminho do dinheiro do último golpe e a lista de golpes acumulados. Inclui cartão final, modal de detalhes, controle de ritmo, botão Parar, reconexão automática e modo mock. O relatório de acurácia é tratado na unit `relatorio-de-acuracia`.

## Responsabilidades
- Conectar em `/ws`, enviar comandos (`start`, `pace`, `stop`, `report`, `reset`) e consumir os eventos.
- Manter a fase (`idle`, `running`, `done`, `stopped`) e a corrida atual (`runId`), descartando eventos de outras corridas.
- Renderizar, por lado: contador gigante `processadas / total`, barra de progresso, p50 de decisão e rastreio com contagem, memória, mensagem atual com remetente, selo de veredito, painel "Caminho do dinheiro" (canvas radial + fluxo GOLPISTA → LARANJAS → SAQUE + resumo), lista "Golpes acumulados", acumulador e flash vermelho.
- Mostrar o cartão final quando os dois lados terminam; abrir o modal de detalhes de um golpe.
- Escalar o frame de 1920 px para a largura da janela (`zoom`).
- Simular tudo localmente com `?mock=1`.

## Regras de Negócio
- RN-30 Eventos com `run_id` diferente do atual são descartados; `run` reinicia o estado; `reset` limpa e, se havia `pendingStart`, reenvia `start`. 🟢 `index.html:1224-1262`
- RN-33 Em `stopped` nenhum `message/decision/trace/error/done` altera a tela; animações pausam; rótulo "Parado" aparece. 🟢 `:1290,` `stopRun`
- RN-34 Cartão final só quando `lanes.rust.done` e `lanes.python.done` existem; `phase = done`. 🟢 `showFinal`
- Botão principal: `Iniciar` (sem corrida), `Parar` (running), `Reiniciar` (após corrida); desabilitado sem transporte ou com comando pendente. Reiniciar = `reset` + `start` com o ritmo do `select`. 🟢 `updateControls`, `start`
- Ritmo: `select#mode` com `step:4000` (Narrado · 4 s) e `serial` (Normal); mudar durante a corrida envia `pace`; mudar durante um start pendente aplica depois do `run`. 🟢 `changePace`, `receive(run)`
- Veredito exibido: `golpe` → "! GOLPE" + tipo em português (`TYPES`) + flash + bolha clicável; `ok` → "✓ OK"; `revisar` → "? SUSPEITA"; `error` → "× ERRO"; desconhecido → SUSPEITA. 🟢 `setVerdict`
- Velocidade: mediana das latências recebidas (`sorted[round((n−1)/2)]`) com contagem "N×"; separada para decisão (modelo) e rastreio (engine). 🟢 `laneMedian`, `recordSpeed`
- Contador: `processed` incrementa em `decision` e em `error`; barra = `processed/total`; acumulador "N processadas · N golpes · N ok" (golpes = tamanho de `scams`, ok = vereditos `ok`; `revisar` não conta em nenhum). 🟢 `countProcessed`, `updateAccumulator`
- Lista de golpes: item prepend (mais recente no topo) com remetente, texto completo, selo GOLPE, tipo e probabilidade em %; clique abre o modal; o golpe mais recente fica selecionado e é o que o painel do grafo mostra. 🟢 `addScam`, `renderDetail`
- Painel do grafo: título "Caminho do dinheiro · mensagem #id", chave Pix, "laranjas: a/r · saque: a/r" (de `truth`, senão contagens), "N contas · X ms"; enquanto o `trace` não chega: "Rastreando o dinheiro...". 🟢 `showTrace`, `renderDetail`
- Grafo radial: nós de `trace.nodes` (até 800), raiz = nó de prof 0 no centro, anéis por profundidade com ângulo `−π/2 + i·2π/n + prof·0,13`, raio `prof/maxProf`; arestas de `trace.edges` (até 1.500) só entre nós presentes; laranjas e saques destacados; 600 estrelas de fundo com semente 42; onda de 300 ms (desligada em `reduced-motion` ou `stopped`); tooltip no hover. 🟢 `prepareGraph`, `drawGraph`, `enableGraphHover`
- Fluxo do dinheiro: grade de laranjas (até 24 quadrados, 4 ou 6 colunas), grade de saques `$` (tamanho calculado), moedas animadas nas setas (1 s, escalonadas), resumo em prosa "O dinheiro saiu da chave, passou por N contas laranja e foi sacado em M contas. A de R laranjas encontradas." 🟢 `drawMoney`, `animateMoney`
- Memória: `status.memory_mb` em MB ou GB (≥ 1024); some quando o lado fica `offline`. 🟢 `receive(status)`
- Conexão: "Conectando..." / "Reconectando..." / "Conectado" / "Rust desconectado" / "Python desconectado" / "Simulação local"; reconexão com backoff `500·2ⁿ` ms até 10 s. 🟢 `updateConnection`, `connect`
- Cartão final: por lado, tempo total em segundos, "decisão p50", "rastreio p50", golpes detectados, custo (USD, 6 casas; Python "Custo estimado"); botões Fechar e Reiniciar. 🟢 `showFinal`
- Modal de detalhes: título "Lado · mensagem #id", remetente, hora (`messageTime(ts)`), texto, "GOLPE · p%", tipo, latências de decisão e rastreio, barras (golpe, pede Pix, urgência 0..2 com rótulo, confiança no tipo se houver), dados técnicos (modelo, tokens, custo desta decisão, custo por 1.000 mensagens), grafo e listas de contas laranja e de saque; foco preso, `Escape` fecha; `trace` tardio atualiza o modal aberto. 🟢 `openScam`, `updateScamTrace`
- Mock: 12 fixtures cíclicas, 24 mensagens, Rust rápido / Python lento, `pace`, `stop`, `report` e `done` simulados; tudo passa por `receive`. 🟢 `startMock`
- Frame de 1920 px com `zoom = min(1, largura/1920)`; página rolável; tema escuro fixo. 🟢 `fitStage`, CSS
- `h1` "DETECTOR DE GOLPE"; rodapé "Mensagens simuladas. Transações simuladas. Mesmo algoritmo nas duas linguagens, Python puro." 🟢 HTML
- Screenshot `docs/tela-corrida.png` mostra "PIX RACE": versão anterior. 🟡

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Conectar/reconectar em `/ws` e refletir o estado de conexão | Must | indicador muda; botão habilita só conectado |
| RF-02 | Iniciar / Parar / Reiniciar com ritmo escolhido | Must | comandos corretos conforme `corrida-em-tempo-real/contracts.md` |
| RF-03 | Trocar ritmo ao vivo | Must | `pace` enviado; `select` sincroniza com evento `pace` |
| RF-04 | Renderizar `decision` (mensagem, veredito, contadores, mediana, lista) | Must | cenários Gherkin |
| RF-05 | Renderizar `trace` (grafo radial, fluxo, resumo, truth) para o golpe mais recente | Must | painel atualizado; modal atualizado se aberto |
| RF-06 | Renderizar `error` (ERRO, contador) e `status` (conexão, memória) | Must | |
| RF-07 | Cartão final quando os dois `done` chegam | Must | overlay com 4 linhas por lado |
| RF-08 | Modal de detalhes por golpe | Should | abre por clique na lista ou na bolha |
| RF-09 | Modo `?mock=1` | Should | corrida simulada completa sem servidor |
| RF-10 | Acessibilidade: dialogs, `aria-live`, foco preso, `prefers-reduced-motion` | Should | Tab não sai do modal; animações desligam |
| RF-11 | Escala para qualquer largura via `zoom` | Should | sem barra horizontal em 1280 px |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | grafo em canvas com cache por evento (`WeakMap`); limites 800/1.500 | `graphCache`, `prepareGraph` | 🟢 |
| Disponibilidade | reconexão exponencial até 10 s; `pageshow` reconecta após bfcache | `connect`, `pageshow` | 🟢 |
| Portabilidade | sem build, sem CDN, sem dependências | `<script>` único | 🟢 |
| Acessibilidade | roles, aria, foco, reduced-motion | HTML/CSS | 🟢 |
| Localização | `Intl.NumberFormat('pt-BR')` para números, moeda USD com 6 casas | `:365-370` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado a tela conectada e sem corrida
Quando clico em Iniciar com "Narrado · 4 s"
Então envio {"type":"start","mode":"step:4000"}, o botão vira "Parar" e os contadores mostram "0 / 1000" após o evento run

Dado uma decision {side: "rust", verdict: "golpe", tipo: "troca_numero", golpe: 0.97}
Quando a tela recebe o evento
Então o painel Rust mostra a mensagem, "! GOLPE", "Golpe do número novo", o flash vermelho, a lista ganha o item no topo com "97%" e o acumulador conta 1 golpe

Dado o trace correspondente com truth {laranjas_acertadas: 14, laranjas_reais: 14, saque_acertadas: 2, saque_reais: 2}
Quando a tela recebe o evento
Então o painel mostra "laranjas: 14/14 · saque: 2/2", o grafo radial e o resumo "passou por 14 contas laranja e foi sacado em 2 contas. 14 de 14 laranjas encontradas."

Dado uma corrida em andamento
Quando clico em Parar
Então envio stop, a fase vira stopped após o evento, aparece "Parado" nos dois lados e eventos tardios não mudam nada

Dado done dos dois lados
Quando o segundo chega
Então o cartão final mostra tempo total, p50 de decisão e rastreio, golpes e custo por lado, e o botão Relatório habilita

Dado ?mock=1 sem servidor
Quando clico em Iniciar
Então a corrida simulada roda 24 mensagens e termina com cartão final
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Recepção de eventos e fase | Must | tudo depende |
| Painéis por lado (mensagem, veredito, contador, grafo) | Must | é o vídeo |
| Cartão final | Must | thumbnail |
| Modal de detalhes | Should | aprofundamento opcional na gravação |
| Mock | Should | desenvolvimento |
| Tooltip do grafo | Could | detalhe |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `static/index.html` (JS 348-1604) | `receive`, `send`, `connect`, `start`, `primaryAction`, `changePace`, `updateControls`, `updateConnection`, `clearRun`, `stopRun`, `setVerdict`, `showMessage`, `recordSpeed`, `countProcessed`, `addScam`, `renderDetail`, `openScam`, `closeScam`, `updateScamTrace`, `prepareGraph`, `drawGraph`, `showTrace`, `drawMoney`, `animateMoney`, `showFinal`, `fitStage`, `startMock`, `mockCommand` | 🟢 |
| `static/index.html` (HTML 209-347) | topbar, `#race`, `#final`, `#accuracy-report`, `template#lane-template`, `#scam-modal` | 🟢 |
| `static/index.html` (CSS 8-207) | tokens e estilos (ver agente Design System) | 🟢 |
