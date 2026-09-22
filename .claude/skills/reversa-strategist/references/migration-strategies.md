> Cópia local do catálogo consultivo. Fonte canônica em `templates/migration/catalogs/migration_strategies.md`.

# Migration Strategies (cópia local)

## Estratégias

### Strangler Fig
- **Quando aplica**: sistema em produção, não pode parar; necessidade de incrementalidade; possibilidade de roteamento (proxy / API gateway).
- **Custo**: médio. **Risco**: baixo. **Tempo**: longo.
- **Apetite favorecido**: conservative, balanced.

### Big Bang
- **Quando aplica**: sistema pequeno; janela tolerada; apetite transformacional; poucas integrações vivas.
- **Custo**: baixo. **Risco**: alto. **Tempo**: curto.
- **Apetite favorecido**: transformational (em sistemas pequenos).

### Parallel Run
- **Quando aplica**: lógica crítica (financeiro / fiscal / regulatório); precisa de prova de equivalência por longo período.
- **Custo**: alto. **Risco**: médio. **Tempo**: médio.
- **Apetite favorecido**: balanced.

### Branch by Abstraction
- **Quando aplica**: migração interna (linguagem ou framework muda, domínio fica); apetite conservador.
- **Custo**: baixo. **Risco**: baixo. **Tempo**: médio.
- **Apetite favorecido**: conservative.

## Regras de recomendação

- apetite `conservative` → Branch by Abstraction + Strangler Fig.
- apetite `balanced` → Strangler Fig + Parallel Run.
- apetite `transformational` → Big Bang em sistemas pequenos; Strangler Fig com bordas profundas em maiores.
- mudança grande de paradigma + apetite transformacional → recomendar Parallel Run para validar paridade.
- sistema com integrações regulatórias → nunca recomendar Big Bang.

## Pseudo-procedimento

1. Filtrar estratégias aplicáveis com base em brief.
2. Pontuar restantes por aderência ao apetite e gap de paradigma.
3. Selecionar 2 a 3 candidatas.
4. Marcar uma como recomendada com justificativa.
5. Para cada outra, listar contras como motivo de não-recomendação.
