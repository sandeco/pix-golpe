# Template — _reversa_sdd/confidence-report.md

Gerado pelo Revisor ao final da revisão.

---

## Estrutura do relatório

```markdown
# Relatório de Confiança — [Nome do Projeto]

> Gerado pelo Revisor em [data]

---

## Resumo Geral

| Nível | Quantidade | Percentual |
|-------|-----------|------------|
| 🟢 CONFIRMADO | [N] | [X%] |
| 🟡 INFERIDO   | [N] | [X%] |
| 🔴 LACUNA     | [N] | [X%] |
| **Total**     | [N] | 100% |

**Confiança geral:** [X%] (soma de 🟢 + metade dos 🟡)

---

## Por Spec

| Spec | 🟢 | 🟡 | 🔴 | Confiança |
|------|----|----|-----|-----------|
| `sdd/auth.md` | 8 | 3 | 1 | 79% |
| `sdd/orders.md` | 12 | 5 | 2 | 74% |
| `sdd/payments.md` | 6 | 8 | 4 | 56% |

---

## Lacunas Pendentes 🔴

Itens que permaneceram sem confirmação após a revisão:

### [Nome da Spec]
- **[Afirmação]** — [por que não foi possível confirmar]
  - Pergunta correspondente: `questions.md#pergunta-N`

---

## Recomendações

- [ ] [Módulo X] tem [N] lacunas críticas — priorizar validação com stakeholder
- [ ] [Módulo Y] — [observação específica]

---

## Histórico de Reclassificações

| De | Para | Afirmação | Evidência |
|----|------|-----------|-----------|
| 🔴 | 🟢 | [afirmação] | [arquivo:linha] |
| 🟡 | 🟢 | [afirmação] | [arquivo:linha] |
```

---

## Como calcular "Confiança geral"

```
confiança = (total_verde + total_amarelo * 0.5) / total * 100
```

Exemplo: 20 🟢 + 10 🟡 + 5 🔴 = 35 total
→ (20 + 5) / 35 = 71%
