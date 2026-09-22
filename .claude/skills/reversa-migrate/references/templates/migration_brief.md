---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: migration_brief
producedBy: orchestrator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Migration Brief

> Documento de critério de migração coletado em entrevista no início do `/reversa-migrate`.
> Consumido pelos seis agentes do Time de Migração. Não pergunta paradigma (responsabilidade do Paradigm Advisor) nem apetite (derivado em `paradigm_decision.md`).

## Objetivo da migração
<Por que esta migração existe? O que muda no negócio se ela acontecer ou não.>

## Métricas de sucesso
- <métrica 1, com alvo numérico ou qualitativo claro>
- <métrica 2>
- <métrica 3>

## Restrições
- **Prazo**: <data ou janela>
- **Orçamento**: <faixa, time, contratação envolvida>
- **Técnicas**: <APIs externas que não podem mudar, contratos, regras regulatórias>
- **Operacionais**: <janelas de manutenção, SLAs durante a migração>

## Fatores de risco conhecidos
- <risco 1: descrição curta>
- <risco 2>

## Stakeholders
| Nome / papel | Responsabilidade na migração |
|---|---|
| <nome> | <responsabilidade> |

## Stack alvo
- **Linguagem**: <ex: Node.js 20>
- **Framework**: <ex: Fastify>
- **Banco**: <ex: PostgreSQL 16>
- **Mensageria** (se houver): <ex: SQS, Kafka, none>
- **Infra**: <ex: AWS Lambda, Kubernetes, on-premise>
- **Outros componentes relevantes**: <cache, observabilidade, gateway>

## Escopo declarado
- **Incluído**: <módulos do legado que entram>
- **Excluído**: <módulos que ficam de fora ou serão descontinuados>

## Notas livres
<Qualquer contexto que o usuário queira deixar registrado para os agentes lerem.>
