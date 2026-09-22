# User stories: corrida

> Gerado pelo Writer (Reversa) em 2026-09-21. Persona única: **apresentador** (grava o vídeo). 🟢 extraído do código.

## US-01 Iniciar a corrida narrada
Como apresentador, quero clicar em Iniciar com o ritmo "Narrado · 4 s" para que cada lado decida uma mensagem, mostre o veredito e espere 4 s, e eu consiga narrar.

Critérios: botão habilitado só com conexão; envia `start {mode: "step:4000"}`; após `run`, contadores em "0 / 1000"; cada lado mostra a mensagem e o veredito e aguarda 4 s antes da próxima. (`interface-tela-dividida` RF-02, `corrida-em-tempo-real` RN-32)

## US-02 Acelerar no meio da corrida
Como apresentador, quero trocar para "Normal" enquanto a corrida roda para que o Rust dispare na frente e o Python se arraste, sem reiniciar.

Critérios: mudar o `select` envia `pace {mode: "serial"}`; todos recebem `pace {ms: 0}`; as próximas decisões saem sem espera; o `select` reflete o modo mesmo se outro browser trocou. (RN-31)

## US-03 Ver o golpe ser detectado
Como apresentador, quero que, quando um lado detectar golpe, apareça um selo GOLPE grande com o tipo em português, um flash vermelho e a mensagem entre na lista de golpes acumulados com o texto completo.

Critérios: `decision.verdict == "golpe"` → "! GOLPE", tipo traduzido, flash 600 ms, item no topo da lista com remetente, texto, badge, tipo e probabilidade em %. (`setVerdict`, `addScam`)

## US-04 Ver o dinheiro ser rastreado
Como apresentador, quero que, logo após o golpe, o painel "Caminho do dinheiro" desenhe o grafo com a chave no centro, laranjas e saques destacados, e um resumo "passou por N contas laranja e foi sacado em M contas. A de R laranjas encontradas."

Critérios: `trace` do golpe mais recente → grafo radial, "laranjas: a/r · saque: a/r", "N contas · X ms", fluxo GOLPISTA → LARANJAS → SAQUE com moedas. (`showTrace`, `drawMoney`)

## US-05 Comparar velocidade ao vivo
Como apresentador, quero ver em cada lado a mediana de decisão e de rastreio com a contagem de amostras, e a memória usada, para mostrar a diferença enquanto a corrida roda.

Critérios: "JEV · DECISÃO p50 280,0 ms 143×", "RUST · RASTREIO p50 14,9 ms 27×", "RUST · MEMÓRIA 170 MB"; Python idem. (`recordSpeed`, `status.memory_mb`)

## US-06 Parar e congelar
Como apresentador, quero clicar em Parar para congelar a tela onde está e comentar o resultado parcial.

Critérios: `stop` → fase `stopped`, "Parado" nos dois lados, animações pausadas, nenhum evento tardio altera a tela; botão Relatório habilita. (RN-33)

## US-07 Terminar e ver o cartão final
Como apresentador, quero que, quando os dois lados terminarem, apareça um cartão grande com tempo total, p50 de decisão e rastreio, golpes e custo por lado, que sirva de thumbnail.

Critérios: só com os dois `done`; Python rotulado "Custo estimado"; botões Fechar e Reiniciar. (RN-34)

## US-08 Reiniciar
Como apresentador, quero clicar em Reiniciar para limpar tudo e começar outra corrida com o ritmo escolhido.

Critérios: envia `reset`, depois `start` com o ritmo do `select`; vereditos do relatório são zerados no servidor. (`start()`, `server.rs:268`)

## US-09 Testar a tela sem servidor
Como desenvolvedor, quero abrir `?mock=1` para ver a tela com eventos falsos (Rust rápido, Python lento) sem gastar API.

Critérios: 24 mensagens, 12 fixtures, `pace`, `stop`, `report` e cartão final funcionam localmente. (`startMock`)

## US-10 Subir tudo com um comando
Como operador, quero rodar `cargo run --release --bin server` e ter o worker Python iniciado junto, com os dois lados aquecidos e prontos.

Critérios: log de carga e memória; "jev aquecido"; "worker python iniciado"; `status ready` dos dois lados na tela; `PIX_NO_WORKER=1` sobe só o Rust. (`server.rs:143-217`)
