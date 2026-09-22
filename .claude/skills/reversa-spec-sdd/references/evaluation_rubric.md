# Rubrica de Avaliação de Specs

Usada pelo `scripts/spec_scorer.py` e como guia de revisão manual.

Score total: **0–100 pontos**

---

## Dimensão 1: Completude (30 pontos)

Avalia se todas as seções essenciais estão presentes e preenchidas.

| Critério | Pontos | Como verificar |
|----------|--------|----------------|
| Seções 1–6 todas presentes e preenchidas (não apenas headers) | 10 | Cada seção tem ≥ 2 frases ou 1 item de lista |
| Requisitos funcionais com IDs (RF-XX) | 8 | Pelo menos 3 requisitos numerados |
| Critérios de aceite definidos para cada RF Must | 7 | Coluna "Critério de Aceite" preenchida |
| Non-Goals explícitos (seção 4) | 5 | Pelo menos 2 non-goals listados |

**Penalidades:**
- Seção obrigatória completamente ausente: -5 por seção
- Seção com placeholder não preenchido (`[colchetes]`): -2 por ocorrência

---

## Dimensão 2: Testabilidade (25 pontos)

Avalia se um QA consegue escrever testes a partir da spec sem fazer perguntas.

| Critério | Pontos | Como verificar |
|----------|--------|----------------|
| Requisitos usam verbos concretos e mensuráveis | 10 | Ausência de "deve ser bom", "deve ser rápido", "deve ser intuitivo" |
| Fluxo principal (happy path) descrito passo a passo | 8 | Seção 6.2 com ≥ 3 passos |
| Métricas de sucesso com valores numéricos | 7 | Seção 3 tem pelo menos 1 métrica com target numérico |

**Penalidades:**
- Requisito não-testável ("o sistema deve ser fácil de usar"): -3 por ocorrência
- Happy path ausente: -8

---

## Dimensão 3: Clareza (20 pontos)

Avalia se a linguagem é precisa e não ambígua.

| Critério | Pontos | Como verificar |
|----------|--------|----------------|
| Ausência de termos vagos sem definição | 8 | "rapidamente", "logo", "muitos", "alguns" sem valor — -2 cada |
| Open Questions sinalizadas com ⚠️ ou na seção 14 | 6 | Ambiguidades são explícitas, não silenciosas |
| Sujeito claro em cada requisito ("o sistema", "o usuário") | 6 | Não há requisitos sem sujeito identificado |

**Penalidades:**
- Contradição entre requisitos: -5 por contradição
- Termo técnico sem definição para audiência não-técnica: -2 por ocorrência

---

## Dimensão 4: Escopo (15 pontos)

Avalia se os limites da feature estão claros.

| Critério | Pontos | Como verificar |
|----------|--------|----------------|
| Seção de Non-Goals (4) clara e útil | 7 | Pelo menos 2 non-goals que previnem scope creep real |
| Dependências e integrações mapeadas (seção 10) | 5 | Toda dependência externa está listada |
| Plano de rollout / rollback presente (seção 13) | 3 | Estratégia e como reverter definidos |

**Penalidades:**
- Non-goals vagos ("funcionalidades futuras"): -2 por ocorrência
- Dependência crítica não mapeada: -3

---

## Dimensão 5: Edge Cases (10 pontos)

Avalia se os casos difíceis foram antecipados.

| Critério | Pontos | Como verificar |
|----------|--------|----------------|
| Pelo menos 3 edge cases listados (seção 11) | 5 | Tabela com ≥ 3 linhas preenchidas |
| Tratamento de erro com mensagem/comportamento definido | 3 | Cada erro tem comportamento esperado |
| Casos de falha de dependências externas cobertos | 2 | Pelo menos 1 EC para timeout/indisponibilidade |

**Penalidades:**
- Zero edge cases: -10 (esta seção zera)
- Edge case sem comportamento definido: -1 por ocorrência

---

## Classificação por Score

| Score | Classificação | Significado |
|-------|--------------|-------------|
| 90–100 | ⭐ Excelente | Pronta para implementação imediata |
| 80–89 | ✅ Boa | Pronta com ajustes menores |
| 65–79 | ⚠️ Adequada | Implementável mas com riscos |
| 50–64 | 🔶 Incompleta | Precisa de revisão antes de implementar |
| < 50 | ❌ Insuficiente | Voltar para entrevista / rascunho |

---

## Checklist Rápido de Revisão

Antes de marcar uma spec como "Aprovada", confirme:

- [ ] Qualquer dev pode implementar sem perguntar nada?
- [ ] Qualquer QA pode escrever testes sem perguntar nada?
- [ ] Os non-goals estão tão claros quanto os goals?
- [ ] Todo caso de erro tem um comportamento definido?
- [ ] Todos os requisitos têm IDs rastreáveis?
- [ ] Não há contradições entre requisitos?
- [ ] Open questions estão documentadas (não silenciosas)?
- [ ] Métricas de sucesso são numéricas e verificáveis?
