---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: target_domain_model
producedBy: designer
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Target Domain Model

> Modelo de domínio do sistema novo. Rastreabilidade explícita para o legado (em `_reversa_sdd/domain.md` ou equivalente).

## Aggregates

### AGG-Pedido
- **Aggregate root**: Pedido
- **Invariantes**:
  - <invariante 1>
  - <invariante 2>
- **Comandos aceitos**: <lista>
- **Eventos publicados** (se paradigma event-driven): <lista>
- **Origem no legado**: <ref para `domain.md` ou equivalente>

<repetir por aggregate>

## Entidades

| Entidade | Aggregate dono | Atributos principais | Origem no legado |
|---|---|---|---|
| <nome> | <agg> | <lista resumida> | <ref> |

## Value objects

| Value object | Atributos | Validações | Origem |
|---|---|---|---|
| <nome> | <lista> | <regras> | <ref> |

## Eventos de domínio
> Seção obrigatória se o paradigma é event-driven ou híbrido.

| Evento | Publicado por | Consumido por | Schema (resumido) |
|---|---|---|---|
| <PedidoCriado> | AGG-Pedido | Pagamento, Estoque | <campos> |

## Regras de domínio
> Mapeamento de regras vindas de `target_business_rules.md` (apenas as MIGRAR) para os aggregates / serviços onde elas vivem agora.

| Regra (ID) | Local no domínio novo | Origem (target_business_rules.md) |
|---|---|---|
| BR-MIGRAR-001 | AGG-Pedido.invariante <nome> | BR-MIGRAR-001 |

## Rastreabilidade para o legado

| Elemento novo | Origem no legado | Tipo de mapeamento |
|---|---|---|
| AGG-Pedido | `domain.md § Pedido` + `sdd/orders.md` | fundido |
| <novo> | <ref> | 1-para-1 / fundido / dividido / novo |

## Notas
<Observações de modelagem adicionais.>
