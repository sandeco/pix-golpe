---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: paradigm_decision
producedBy: paradigm_advisor
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Paradigm Decision

> Decisão consciente sobre como tratar a mudança (ou ausência) de paradigma entre o legado e a stack alvo.
> Este artefato é leitura obrigatória primeiro para qualquer agente posterior e para o agente de codificação.

## Paradigma do legado detectado
- **Paradigma principal**: <procedural | OO clássico | OO com DI | funcional | event-driven | actor model | dataflow | híbrido: ...>
- **Confiança**: 🟢 CONFIRMADO | 🟡 INFERIDO | 🔴 LACUNA | ⚠️ AMBÍGUO
- **Evidências**:
  - <evidência 1, com referência a artefato do `_reversa_sdd/`>
  - <evidência 2>
- **Variações observadas** (se híbrido):
  - <componente A: paradigma X, evidência>
  - <componente B: paradigma Y, evidência>

## Stack alvo declarada
- Linguagem: <do migration_brief.md>
- Framework: <do migration_brief.md>
- Infra: <do migration_brief.md>

## Paradigma natural inferido
- **Paradigma**: <inferido via paradigm_catalog>
- **Justificativa**: <por que essa stack tem esse paradigma natural>
- **Alternativas viáveis**: <ex: OO com DI também é viável em Node, com custo X>

## Gap identificado
- **Severidade**: alto | médio | baixo | nenhum
- **Implicações concretas** (não em abstrato; com exemplo do próprio sistema legado):
  - <implicação 1, citando regra/fluxo do legado afetado>
  - <implicação 2>
  - <implicação 3>
  - <implicação 4>

## Opções apresentadas ao usuário
1. **Adotar paradigma natural da stack** (transformacional)
   - Consequências: <lista>
2. **Forçar paradigma similar ao legado** (conservador)
   - Consequências: <lista>
3. **Híbrido** (equilibrado)
   - Consequências: <lista>

## Decisão do usuário
- **Escolha**: <1 | 2 | 3>
- **Justificativa do usuário**: <texto livre>
- **Decidido em**: <ISO-8601>

## Apetite derivado
- `derived_appetite`: conservative | balanced | transformational

## Implicações pendentes para próximos agentes
| Agente | Implicação | Como honrar |
|---|---|---|
| Curator | <implicação> | <ação esperada> |
| Strategist | <implicação> | <ação esperada> |
| Designer | <implicação> | <ação esperada> |
| Inspector | <implicação> | <ação esperada> |

## Notas
<Qualquer ponto adicional que o agente de codificação precisa saber sobre o paradigma alvo.>
