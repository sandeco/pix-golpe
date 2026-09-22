# ADR-002: Regras de justiça da comparação

**Status:** aceita. **Confiança:** 🟢 (brainstorm, SPEC §3-4, README "Regras de justiça", código).

## Contexto

Duas variáveis mudam juntas (modelo e linguagem). Sem cuidado, a demo vira "Rust vs ecossistema numpy" ou "8 núcleos vs 1".

## Decisão

1. Mesmo dataset, mesmas 4 perguntas, mesma regra de veredito nos dois lados.
2. Mesma concorrência de decisões, informada pelo servidor no evento `run` (1 ou 8).
3. Rastreio serializado (um por vez, uma thread) nos dois lados; tempo medido só nos passos A a D.
4. Python puro, sem numpy, no rastreio; Rust em `--release`.
5. Aquecimento do modelo fora da medição; latência HTTP medida por cada lado.
6. Igualdade do algoritmo verificada bit a bit nas 40 quadrilhas (`trace --todas` vs `trace.py --todas`).
7. Custo e modelo real retornado exibidos; custo do DeepSeek marcado como estimado.

## Alternativas consideradas

- Rastreio paralelo: rejeitado, mediria núcleos.
- Python com numpy: rejeitado pela regra do vídeo.
- Gravar decisões e reproduzir offline: sugerido pelo Codex, não implementado (as chamadas são ao vivo).

## Consequências

- Divergência residual: o Rust inclui o backoff de retry na latência de decisão, o Python não (`server.rs:338` vs `deepseek.py:147`). Só afeta corridas com 429/5xx. Registrada como Q-002.
- A vantagem medida vem de latência e custo; acurácia é praticamente igual e o relatório mostra isso.
