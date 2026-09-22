---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: target_business_rules
producedBy: curator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Target Business Rules

> Catálogo das regras de negócio do legado com decisão de migração: MIGRAR, DESCARTAR ou DECISÃO HUMANA.
> Cada item rastreia para a origem em `_reversa_sdd/` e respeita o `paradigm_decision.md`.

## Resumo
- Total de regras analisadas: <N>
- MIGRAR: <n>
- DESCARTAR: <n> (detalhe em `discard_log.md`)
- DECISÃO HUMANA: <n>

## Regras MIGRAR

### BR-MIGRAR-001
- **Origem**: `_reversa_sdd/<unit>/{requirements,design}.md` § <seção>
- **Confiança original**: 🟢 | 🟡 | 🔴 | ⚠️
- **Descrição**: <regra>
- **Justificativa de migração**: <por que migra>
- **Compatibilidade com paradigma alvo**: <nota; ex: precisará ser expressa como evento>

<repetir por regra>

## Regras DESCARTAR (resumo)

| ID | Origem | Motivo curto | Vínculo a paradigma? |
|---|---|---|---|
| BR-DESCARTAR-001 | <ref> | <motivo> | sim/não |

> Detalhe completo em `discard_log.md`.

## Regras DECISÃO HUMANA

### BR-HUMANA-001
- **Origem**: <ref>
- **Tipo de ambiguidade**: ⚠️ AMBÍGUA | 🔴 GAP | dependência de stakeholder
- **Descrição**: <regra>
- **Opções**: <opções claras>
- **Recomendação do Curator**: <opção sugerida e por quê>
- **Status**: PENDENTE | RESOLVIDA (escolha + decisor + data)

<repetir por item>

## Notas
<Observações gerais do Curator. Itens que serão consolidados em `ambiguity_log.md`.>
