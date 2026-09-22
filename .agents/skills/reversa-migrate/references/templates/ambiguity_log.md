---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: ambiguity_log
producedBy: orchestrator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Ambiguity Log

> Consolidação de todos os itens ⚠️ AMBÍGUOS ou pendentes detectados pelos agentes ao longo do pipeline.
> Status final esperado quando o pipeline conclui: nenhum item PENDENTE.

## Resumo
- Total de itens: <N>
- PENDENTES: <n>
- RESOLVIDOS COM DECISÃO HUMANA: <n>
- REFERIDOS À CODIFICAÇÃO: <n>

## Itens

### AMB-001
- **Descrição**: <texto>
- **Detectado por**: paradigm_advisor | curator | strategist | designer | screen_translator | inspector
- **Origem**: <referência ao artefato e seção>
- **Status**: PENDENTE | RESOLVIDO COM DECISÃO HUMANA | REFERIDO À CODIFICAÇÃO
- **Decisão tomada** (se houver):
  - **Escolha**: <texto>
  - **Decisor**: <nome>
  - **Quando**: <ISO-8601>
  - **Justificativa**: <texto>

<repetir por item>

## Itens referidos à codificação
> Lista somente itens com status `REFERIDO À CODIFICAÇÃO`. Aparecem destacados em `handoff.md`.

- AMB-XXX: <descrição curta>

## Notas
<Observações finais do orquestrador.>
