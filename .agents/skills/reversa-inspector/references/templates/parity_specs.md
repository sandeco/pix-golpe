---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: parity_specs
producedBy: inspector
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Parity Specs

> Estratégia de validação de equivalência comportamental entre legado e sistema novo, adaptada ao paradigma escolhido em `paradigm_decision.md`.

## Estratégia geral
- **Modos de validação aplicáveis** (marcar os usados):
  - [ ] Shadow mode (espelhamento de tráfego com comparação assíncrona)
  - [ ] Characterization tests (suíte derivada do comportamento atual do legado)
  - [ ] Contract tests (interfaces externas)
  - [ ] Data parity (snapshots e checksums)
  - [ ] Outro: <especificar>

## Critérios de "paridade aceita"
- **Métrica primária**: <ex: índice de divergência funcional < 0,01% em N dias consecutivos>
- **Janela de observação**: <período de avaliação>
- **Critério de bloqueio**: <quando paridade insuficiente bloqueia o cutover>

## Cobertura adaptada ao paradigma

> Esta seção muda conforme o paradigma alvo confirmado em `paradigm_decision.md`.

### Sem mudança de paradigma
- Equivalência funcional padrão: mesma entrada → mesma saída → mesmo efeito colateral observável.

### Mudança síncrono → event-driven
- **Ordem de mensagens**: <critério de aceitação por canal / partição>
- **Idempotência**: <prova de que reprocessamento não duplica efeito>
- **Consistência eventual**: <janela máxima de propagação aceita>
- **Comportamento sob falha de fila**: <retry, DLQ, replay>

### Mudança procedural → OO
- **Invariantes em aggregates**: <conjunto a validar>
- **Validação em factories / construtores**: <casos críticos>

### Mudança OO → funcional
- **Imutabilidade**: <pontos críticos a observar>
- **Ausência de side effects esperados**: <onde o legado tinha efeito colateral implícito>
- **Equivalência sob composição**: <funções compostas equivalem ao fluxo legado>

## Tipos de teste a aplicar
- **Funcionais**: <descrição, ferramenta>
- **Contrato**: <descrição, ferramenta>
- **Carga / performance**: <descrição, alvos>
- **Resiliência** (se aplicável): <falha de fila, dependência externa indisponível>

## Reuso de characterization_specs do time de descoberta
- **Origem**: `_reversa_sdd/characterization_specs/` ou equivalente disponível.
- **Adaptações necessárias para o sistema novo**: <texto>

## Saídas
- `parity_tests/*.feature`: cenários em Gherkin para os fluxos críticos.

## Notas
<Observações adicionais.>
