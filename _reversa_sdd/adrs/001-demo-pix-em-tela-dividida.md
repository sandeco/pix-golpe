# ADR-001: Demo "IA detecta golpe do Pix" em tela dividida Rust+Jev vs Python+DeepSeek

**Status:** aceita (2026-09-21, madrugada). **Confiança:** 🟢 (brainstorm registrado em `BRAINSTORMING/BRAINSTORM_jev_rust_youtube.md`).

## Contexto

O usuário queria um vídeo para o canal mostrando o Jev (TypeSafe AI) com Rust: visual, texto em linguagem natural, decisão rápida e uma etapa pesada onde Rust fosse visivelmente mais rápido que Python. Três ideias foram avaliadas (comentários do canal, golpe do Pix, notícia e bolsa) e o Codex GPT-6 Astra propôs outras (cidade alagada, futebol, rede elétrica).

## Decisão

Escolhida a ideia B reformulada: "IA detecta golpe do Pix e rastreia a quadrilha". Tela dividida, esquerda Rust + Jev, direita Python + DeepSeek. Dados 100 % simulados com semente fixa.

## Alternativas consideradas

- Comentários do canal: gancho só para quem já acompanha; Jev não dá embeddings; 50 mil requisições não cabem em 12 s.
- Notícia e bolsa: distância grande entre promessa e evidência; atrai comentário tóxico.
- Cidade alagada: forte, mas toca em tragédia real recente; teria de ser ficção explícita.
- Rede elétrica com chat ao vivo: mais engajamento em live, deixado para o futuro.

## Consequências

- Thumbnail forte para público brasileiro; tudo declarado como simulação na tela.
- Grafo precisa existir antes da corrida (gerador) e a etapa pesada é rastreio em milhões de arestas, não "varrer 10 milhões" com índice.
- Divisão de trabalho: Claude fez o lado Rust e o SPEC; Codex fez front-end e worker Python.
