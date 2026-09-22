# ADR-004: Rastreio determinístico em quatro passos, idêntico em Rust e Python

**Status:** aceita. **Confiança:** 🟢 (SPEC §3, `graph.rs`, `trace.py`).

## Contexto

A etapa pesada precisa ser um algoritmo real sobre o grafo, com saída comparável entre linguagens, e visualizável (laranjas e saques).

## Decisão

Passos fixos: (A) BFS temporal com janela de 24 h por chegada, valor mínimo R$ 20, profundidade 5, teto de 40 mil nós; (B) suspeição por conta com pesos 0,4 / 0,5 / 0,1; (C) propagação de rótulos assíncrona, 10 iterações, ponderada por suspeição, empate pelo menor id; (D) laranjas por comunidade + suspeição ≥ 0,6 e saques por ≥ 3 entradas de laranjas e repasse < 30 %.

Determinismo garantido por: ordem crescente de id em toda soma flutuante, inteiros em centavos antes de dividir, `rust_round` replicando `f64::round`, proibição de `sum()` no Python 3.12 (soma compensada).

## Alternativas consideradas

- Detecção de comunidade genérica (Louvain): não determinística entre implementações e difícil de portar sem bibliotecas.
- Só BFS e listar destinos: explode nos hubs e não separa laranjas de comerciantes.

## Consequências

- Porte Python obrigatoriamente literal; qualquer mudança em `graph.rs` exige mudança espelho em `trace.py` e nova conferência com `fc`.
- Rust usa vetores densos de 1 M posições por rastreio (rápido, mais memória); Python usa dicts.
- Sem testes automatizados: a conferência é manual (`trace_ref.jsonl`).
