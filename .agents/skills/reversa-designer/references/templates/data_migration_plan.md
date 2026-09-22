---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: data_migration_plan
producedBy: designer
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Data Migration Plan

> Plano de migração dos dados do legado para o sistema novo: mapeamento, transformações, ETL, cutover de dados e validação.

## Resumo
- Volume estimado: <linhas / GB por entidade principal>
- Janela de migração: <ver `cutover_plan.md`>
- Estratégia: backfill prévio + delta + corte | bulk único | replicação contínua

## Mapeamento legado → novo

| Origem | Destino | Tipo | Notas |
|---|---|---|---|
| `<schema legado>.tb_pedidos` | `pedidos` | renomeação | normalização de tipos |
| `<schema legado>.tb_pedido_item` | `pedido_itens` | renomeação | FK ajustada |
| `<schema legado>.usr_x` | `usuarios` (parcial) + `perfis` | divisão | extrai dados de perfil |

## Transformações

### Transformação T-01: <nome>
- **Aplica em**: <coluna ou tabela>
- **Regra**: <texto explícito>
- **Tratamento de inválidos**: <descartar | rejeitar | preencher com default>
- **Origem da regra**: <referência a `target_business_rules.md` ou `discard_log.md`>

<repetir por transformação>

## Estratégia de ETL

- **Ferramenta**: <ex: scripts SQL, dbt, Airbyte, custom>
- **Fluxo**:
  1. <extração>
  2. <transformação>
  3. <carga>
- **Idempotência**: <como o ETL é seguro para reexecução>
- **Throughput esperado**: <ex: 50k linhas/s>

## Backfill e delta

- **Backfill**: <data inicial, escopo, duração>
- **Captura de delta**:
  - **Mecanismo**: CDC | log mining | timestamps | replicação | trigger
  - **Latência aceitável**: <segundos>
- **Reconciliação periódica**: <frequência, escopo>

## Cutover de dados

> Ver também `cutover_plan.md`. Aqui apenas a parte específica de dados.

- **Janela**: <ISO-8601>
- **Sequência de corte**:
  1. <passo>
  2. <passo>
- **Verificação pós-corte**:
  - **Contagens**: <quais tabelas, tolerância>
  - **Checksums**: <colunas críticas>

## Validação de qualidade

| Métrica | Alvo | Fonte de medição |
|---|---|---|
| Contagem por entidade | igual ± 0% | comparação direta |
| Soma de valores monetários | igual ± 0,01% | reconciliação financeira |
| Integridade referencial | 0 órfãos | scripts de auditoria |

## Riscos específicos de dados
- <RISK-XXX: ver `risk_register.md`>

## Notas
<Observações adicionais.>
