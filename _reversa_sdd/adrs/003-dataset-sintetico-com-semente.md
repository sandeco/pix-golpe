# ADR-003: Dataset sintético reprodutível com hubs e quadrilhas plantadas

**Status:** aceita. **Confiança:** 🟢 (SPEC §1, `gerar_dados.rs`).

## Contexto

Não existe dado bancário real disponível nem desejável. A demo precisa de um grafo grande o suficiente para o rastreio ser pesado e de uma verdade de referência para medir acertos.

## Decisão

- Gerador Rust com `ChaCha8Rng` seed 42: arquivo idêntico a cada execução.
- Fundo: transações normais lognormais concentradas em horário comercial.
- Hubs (comerciantes) com peso `1/(i+1)^0.8` recebendo metade dos pagamentos e pagando lotes diários: eles fazem o BFS explodir e obrigam o algoritmo a descartá-los (`pequeno` = grau de entrada < 50).
- 40 quadrilhas plantadas: vítimas → chave → 12..18 laranjas → 2 saques, em janelas de minutos a horas.
- `meta.json` guarda o gabarito; `golpe_real` marca as mensagens.
- Formato binário compacto de 16 bytes por transação, ordenado por tempo, para carga rápida e listas de adjacência já ordenadas.

## Alternativas consideradas

- Dataset público de fraude: não tem chave Pix ligada a mensagem nem grafo temporal completo.
- CSV/JSON para transações: 10× maior e lento para carregar em Python.

## Consequências

- Escala foi aumentada 10× depois do SPEC/PDF (100 k → 1 M contas; 1,3 M → 10 M transações; 200 → 2.000 hubs). Os documentos não foram atualizados (Q-001).
- `transacoes.bin` tem 152 MiB e não deve ser versionado; `data/` é regenerável em segundos.
- Os dois lados carregam o grafo inteiro em memória; a tela mostra a memória residente de cada lado.
