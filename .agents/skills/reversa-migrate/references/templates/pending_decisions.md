---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: pending_decisions
producedBy: orchestrator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Pending Decisions

> Arquivo transitório usado durante pausas humanas. Cada item descreve uma decisão aberta com contexto e opções.
> Após o usuário responder, o item é movido para `ambiguity_log.md` (ou para o artefato dono da decisão) e este arquivo pode ser apagado.

## Decisões abertas

### PD-001
- **Agente que solicitou**: paradigm_advisor | curator | strategist | designer | screen_translator | inspector
- **Tópico**: <título curto>
- **Contexto**:
  <texto explicando por que essa decisão é necessária aqui>
- **Opções**:
  1. <opção 1>
  2. <opção 2>
  3. <opção 3>
- **Default proposto** (usado em `--auto`): <opção número>
- **Impacto se decidido errado**: <texto>
- **Onde a decisão será gravada**: <ex: `paradigm_decision.md § Decisão do usuário`>

<repetir por decisão>

## Como responder

- No chat: respondendo direto ao agente com o número da opção e justificativa.
- Em arquivo: editando este `pending_decisions.md`, adicionando um campo `Resposta:` em cada item.
