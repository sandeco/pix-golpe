---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: target_data_model
producedBy: designer
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Target Data Model

> Modelo de dados do sistema novo. Schema, relacionamentos e restrições.

## Visão geral
<Texto curto: tipo de banco principal, divisão por bounded context, papéis (OLTP / OLAP / event store).>

## Entidades de dados

| Entidade | Tabela / coleção | Aggregate dono | PK | Bounded context |
|---|---|---|---|---|
| <nome> | <ref> | <AGG> | <campo> | <BC> |

## Schema (DDL ou equivalente)

```sql
-- Substituir pelo DDL real do sistema alvo.
CREATE TABLE pedidos (
    id UUID PRIMARY KEY,
    cliente_id UUID NOT NULL,
    status TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Relacionamentos

| Origem | Destino | Cardinalidade | Integridade | Notas |
|---|---|---|---|---|
| pedidos.cliente_id | clientes.id | N:1 | FK ON DELETE RESTRICT | |

## Restrições

- **Unicidade**: <lista>
- **Integridade referencial**: <ativada / desativada e por quê>
- **Particionamento / sharding** (se aplicável): <descrição>
- **Índices críticos**: <lista>

## Considerações específicas do paradigma alvo

> Seção dedicada quando o paradigma alvo é event-driven, funcional ou outro com implicação direta no modelo de dados.

- <ex: event-driven → tabela de outbox para garantia at-least-once>
- <ex: event sourcing → store de eventos como fonte da verdade, projeções derivadas>
- <ex: imutabilidade → eventos / snapshots imutáveis, sem updates>

## Origem no legado

| Tabela / coleção nova | Origem no legado | Transformação |
|---|---|---|
| pedidos | `<schema legado>.tb_pedidos` | renomeação + tipos normalizados |

## Notas
<Observações adicionais sobre o modelo de dados.>
