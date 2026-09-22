---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: discard_log
producedBy: curator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Discard Log

> Registro completo do que foi descartado da migração e por quê. Cada item tem rastreabilidade para a origem no legado.

## Itens descartados

### BR-DESCARTAR-001
- **Origem**: `_reversa_sdd/<unit>/{requirements,design}.md` § <seção>
- **Descrição**: <regra ou comportamento descartado>
- **Justificativa**: <texto>
- **Vinculado a paradigma**: sim | não
  - Se sim: <qual paradigma e como o paradigma alvo absorve o caso>
- **Reposição no sistema novo**: <none | substituído por X>
- **Risco de descartar**: baixo | médio | alto, com nota explicativa

<repetir por item>

## Itens descartados por mudança de paradigma (subseção dedicada)

> Lista apenas dos itens cujo `Vinculado a paradigma = sim`. Auditoria explícita para o agente de codificação.

| ID | Origem | Paradigma legado | Substituto no paradigma alvo |
|---|---|---|---|
| BR-DESCARTAR-XXX | <ref> | <ex: lock pessimista síncrono> | <ex: idempotência via event ID> |

## Notas
<Observações finais do Curator sobre o conjunto descartado.>
