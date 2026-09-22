# Matriz de cobertura de paridade

Tabela de referência para definir o conjunto mínimo de cenários `.feature` por fluxo, conforme transição de paradigma.

## Cobertura por transição

| Transição | Cenários mínimos por fluxo |
|---|---|
| sem mudança | `@paridade` (entrada → saída esperada) |
| procedural → OO | `@paridade` + `@invariante` (invariante de aggregate validado) |
| procedural → event-driven | `@paridade` + `@idempotencia` + `@ordem` + `@dlq` (comportamento sob falha de fila) |
| OO clássico → OO com DI | `@paridade` + `@composicao` (sem dependência de Active Record) |
| OO clássico → event-driven | `@paridade` + `@idempotencia` + `@ordem` + `@saga` (compensação ao falhar) |
| OO clássico → funcional | `@paridade` + `@imutabilidade` + `@composicao` |
| OO com DI → event-driven | `@paridade` + `@idempotencia` + `@ordem` |
| funcional → event-driven | `@paridade` + `@idempotencia` + `@ordem` |
| qualquer → actor model | `@paridade` + `@supervisao` (recuperação após falha) |

## Tags convencionadas

- `@paridade`: sempre presente; equivalência principal.
- `@critico`: fluxo crítico (regulatório, financeiro, dados sensíveis).
- `@regulatorio`: quando há requisito formal externo.
- `@idempotencia`: reprocessamento não duplica efeito.
- `@ordem`: ordem por chave respeitada.
- `@dlq`: comportamento ao chegar em dead letter queue.
- `@saga`: compensação em transação distribuída.
- `@invariante`: invariante de aggregate validado.
- `@composicao`: comportamento equivalente sob composição funcional.
- `@imutabilidade`: não há mutação compartilhada.
- `@supervisao`: supervisor recupera ator falhado.

## Critérios de "paridade aceita" típicos

| Tipo de sistema | Métrica primária |
|---|---|
| Web app sem regulação forte | divergência funcional < 1% por 7 dias |
| API pública | divergência funcional < 0,1% por 30 dias + zero divergência em contratos públicos |
| Sistema fiscal / regulatório | divergência funcional < 0,01% por 60 dias + zero divergência em campos regulados |
| Sistema financeiro | divergência financeira por valor monetário < 0,001% + zero divergência em totalizadores |
| Sistema interno baixa criticidade | divergência funcional < 5% por 7 dias |

## Reuso de characterization_specs

Quando `_reversa_sdd/characterization_specs/` existe:

1. Para cada spec → derivar `.feature` correspondente, adaptando entradas/saídas ao sistema novo.
2. Manter o `spec-id` original na rastreabilidade.
3. Adicionar cenários extras conforme a tabela "Cenários mínimos por fluxo".

Quando não existe:

1. Inferir fluxos críticos a partir de `code-analysis.md` + `sequences/` + regras `BR-MIGRAR` marcadas como críticas.
2. Documentar lacuna em `parity_specs.md § Reuso de characterization_specs`.
