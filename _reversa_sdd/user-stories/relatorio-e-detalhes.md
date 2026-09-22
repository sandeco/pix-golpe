# User stories: relatório de acurácia e detalhes do golpe

> Gerado pelo Writer (Reversa) em 2026-09-21. Persona: **apresentador**. 🟢 extraído do código.

## US-11 Provar a acurácia dos dois lados
Como apresentador, quero abrir o Relatório de acurácia ao terminar ou parar para mostrar a matriz de confusão de cada lado e as métricas, sem esconder erros.

Critérios: botão só em `done`/`stopped`; matriz Real × Veredito (GOLPE, SUSPEITA, OK) por lado; acertos em verde, erros em vermelho; Acurácia, Precisão e Recall em % (N/D sem casos); legendas explicando cada métrica; nota "Golpes perdidos incluem SUSPEITA e OK". (`relatorio-de-acuracia`)

## US-12 Ler a conclusão em uma frase
Como apresentador, quero uma frase pronta no rodapé do relatório, como "Os dois tiveram 2 falsos alarmes cada. Jev deixou passar 2 golpes. DeepSeek deixou passar 2 golpes.", para narrar sem interpretar números.

Critérios: frases de `reportConclusion` conforme falsos alarmes, golpes perdidos e quantidades avaliadas.

## US-13 Relatório de corrida interrompida
Como apresentador, quero que o relatório funcione após Parar, avisando que é parcial e mostrando quantas mensagens cada lado avaliou.

Critérios: título "N (Jev) / M (DeepSeek) mensagens avaliadas" quando diferem; nota "Relatório parcial: métricas apenas das mensagens avaliadas."

## US-14 Abrir os detalhes de um golpe
Como apresentador, quero clicar num golpe da lista (ou na bolha da mensagem atual) e ver um modal com a mensagem completa, o tipo, as barras de probabilidade de golpe, pede Pix e urgência, o modelo, tokens, custo desta decisão e por 1.000 mensagens, e o grafo daquele rastreio com as contas laranja e de saque.

Critérios: `openScam` preenche título "Lado · mensagem #id", hora da mensagem, "GOLPE · p%", barras (com "Confiança no tipo" só no Rust), dados técnicos, grafo e listas de ids; `Escape` e Fechar fecham; foco preso; `trace` que chegar depois atualiza o modal aberto.

## US-15 Confiar que é simulação
Como espectador, quero ver na tela que mensagens e transações são simuladas e que o algoritmo é o mesmo nas duas linguagens, para não confundir a demo com um produto.

Critérios: rodapé fixo "Mensagens simuladas. Transações simuladas. Mesmo algoritmo nas duas linguagens, Python puro."; custo do Python marcado "estimado".
