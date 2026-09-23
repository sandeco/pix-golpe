# ADR-007: Jev por HTTP direto com perguntas tipadas; DeepSeek em JSON mode com validação estrita

**Status:** aceita. **Confiança:** 🟢 (brainstorm "Fatos do Jev", SPEC §2, `jev.rs`, `deepseek.py`).

## Contexto

O Jev não gera texto: recebe `state` e perguntas tipadas (`noul`, `choice`, `score`) e devolve probabilidade e confiança em uma passada, com latência de dezenas de ms e sem SDK Rust. O DeepSeek é um chat model e precisa de JSON mode para ser comparável.

## Decisão

- Rust chama `POST /v1/systemone` com `reqwest` + `serde`, modelo `jev-latest`, 4 perguntas fixas, `state` em português e instruções em inglês (validado ao vivo em 2026-09-20).
- Python chama `chat/completions` com `deepseek-flash`, `temperature 0`, `response_format json_object`, prompt de sistema exato do SPEC, e valida o JSON campo a campo (faixas, tipo na lista, tokens inteiros). Falha vira evento `error`, não veredito.
- Retentativas curtas nos dois lados (429/529 e 429/5xx), 3 tentativas.
- TLS do Python via `truststore` (store do sistema) por causa de proxy/antivírus com CA própria no Windows.

## Alternativas consideradas

- SDK oficial: inexistente para Rust.
- Deixar o DeepSeek responder texto livre e extrair: rejeitado, quebra a comparabilidade.

## Consequências

- Preços fixos no código (US$ 0,042/M para Jev; 0,28 e 0,42/M para DeepSeek), sem consulta a tabela; DeepSeek marcado "estimado".
- `model` real retornado é exibido (DeepSeek resolvia para `deepseek-flash`).
- Chaves em `.env` na raiz, carregadas por `dotenvy` e por leitura manual no Python.
