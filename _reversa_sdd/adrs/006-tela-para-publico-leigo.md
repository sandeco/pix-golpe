# ADR-006: Tela em arquivo único, escura, 1920 px, refeita para público leigo

**Status:** aceita (refeita em 2026-09-21, dia). **Confiança:** 🟢 (brainstorm "Decisão", SPEC §5, `index.html`, screenshots).

## Contexto

A primeira versão (mockup de celular com bolhas, seletor `step`/`burst`) era voltada a devs. Feedback: público leigo precisa entender em segundos quem está ganhando e por quê.

## Decisão

- Arquivo único `static/index.html`, sem build, sem CDN; frame fixo de 1920 px escalado por `zoom`; tema escuro; fonte Segoe UI.
- Elementos gigantes: contador de mensagens processadas, mensagem atual, selo GOLPE com flash, gráfico radial do caminho do dinheiro, fluxo GOLPISTA → LARANJAS → SAQUE com moedas, lista de golpes acumulando com texto completo, página rolável.
- Cores por lado: Jev rosa `#ff2d95`, DeepSeek azul `#6985f6`.
- Só dois ritmos na tela: Narrado (4 s) e Normal; troca ao vivo; botão Parar; botão Relatório de acurácia com matriz de confusão e conclusão em prosa.
- `revisar` exibido como SUSPEITA; custo do Python rotulado "estimado".
- Modo `?mock=1` para desenvolver sem servidor; acessibilidade básica (dialog, foco, reduced-motion).

## Alternativas consideradas

- Manter mockup de celular e seletor burst: rejeitado após feedback.
- Framework front-end: rejeitado, sem build.

## Consequências

- O SPEC §5 descreve a versão antiga (celular, `step`/`burst` na UI, cartão final como thumbnail); o cartão final existe, o resto mudou.
- O screenshot `docs/tela-corrida.png` mostra o título "PIX RACE"; o HTML atual diz "DETECTOR DE GOLPE".
- Tokens visuais ficam para o agente Design System extrair.
