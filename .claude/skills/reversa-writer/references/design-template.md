# [Nome da Unit], Design Técnico

> Template do arquivo `design.md`. Foca no COMO a unit é construída, com base no código legado lido.

## Interface
[Entradas, saídas, parâmetros, tipos de dados]

Para endpoints HTTP:

| Método | Caminho | Entrada | Saída | Status codes |
|--------|---------|---------|-------|--------------|
| GET | `/recurso/:id` | `id: string` | `Recurso` | 200, 404 |
| POST | `/recurso` | `RecursoCreate` | `Recurso` | 201, 400, 409 |

Para classes/funções:

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `NomeDaClasse.metodo` | `(arg1: T, arg2: U)` | `V` | [Detalhe relevante] |

## Fluxo Principal
1. [Passo 1, com referência ao arquivo legado quando aplicável]
2. [Passo 2]
3. [Passo N]

## Fluxos Alternativos
- **[Condição especial]:** [comportamento]
- **[Caso de erro]:** [comportamento]

## Dependências
- [Componente X], [motivo, como usa]
- [Serviço Y], [motivo, como usa]

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| [ex: persistência via Prisma com soft-delete] | `prisma/schema.prisma:42` | 🟢 |
| [ex: cache em memória com TTL de 5min] | `cache/store.ts:18` | 🟡 |

## Estado Interno
[Se a unit mantém estado, descrever quais campos, onde são armazenados, como evoluem]

## Observabilidade
[Logs, métricas, traces emitidos pela unit, com referência ao código]

## Riscos e Lacunas
- 🔴 [Comportamento que não foi possível inferir do código, requer validação humana]
- 🟡 [Suposição que pode estar errada]
