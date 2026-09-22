---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: cutover_plan
producedBy: strategist
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Cutover Plan

> Plano de corte do legado para o sistema novo, alinhado à estratégia escolhida em `migration_strategy.md`.

## Estratégia base
- **Estratégia confirmada**: <referência ao migration_strategy.md>

## Pré-requisitos
- [ ] <pré-requisito 1: ex. paridade comportamental ≥ X% por N dias>
- [ ] <pré-requisito 2>
- [ ] <pré-requisito 3>

## Janela de cutover
- **Data alvo**: <ISO-8601 ou janela>
- **Duração estimada**: <horas>
- **Ambiente afetado**: <produção / staging / outro>
- **Comunicação prévia**: <stakeholders avisados, prazo>

## Passos do cutover

| # | Passo | Owner | Duração | Reversível? |
|---|---|---|---|---|
| 1 | <ex: congelar escritas no legado> | | | |
| 2 | <ex: ETL final dos dados> | | | |
| 3 | <ex: roteamento DNS> | | | |
| 4 | <ex: smoke tests no novo> | | | |

## Plano de rollback
- **Critérios de acionamento**: <quando rollback é decidido>
- **Passos**:
  1. <passo>
  2. <passo>
- **Tempo máximo aceitável até rollback**: <minutos / horas>
- **Owner do rollback**: <nome / papel>

## Critérios de go / no-go
- **Go**:
  - <critério 1>
  - <critério 2>
- **No-go**:
  - <critério 1>
  - <critério 2>

## Pós-cutover
- [ ] Monitoramento estendido por <período>
- [ ] Validação de paridade conforme `parity_specs.md`
- [ ] Decommission do legado em <data>

## Notas
<Observações adicionais.>
