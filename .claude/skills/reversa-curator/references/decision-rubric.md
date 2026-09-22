# Decision Rubric do Curator

Tabela de referência rápida para aplicar a política de decisão.

## Tabela de decisão

| Sinal observado na regra | Decisão default | Notas |
|---|---|---|
| 🟢 CONFIRMADA, compatível com paradigma alvo, sem pain point | MIGRAR | sem ressalva |
| 🟡 INFERIDA, compatível com paradigma alvo | MIGRAR | adicionar nota "validar no agente de codificação" |
| 🔴 LACUNA | DECISÃO HUMANA | recomendação opcional |
| ⚠️ AMBÍGUA | DECISÃO HUMANA | obrigatório listar interpretações |
| Regra citada como pain point | DECISÃO HUMANA | recomendação default: substituir por X no novo |
| Regra incompatível com brief (fora de escopo) | DESCARTAR | justificativa: "fora de escopo declarado em migration_brief.md" |
| Regra incompatível com brief (técnica) | DESCARTAR | justificativa: "restrição técnica do brief impede" |
| Regra é mecanismo do paradigma legado, paradigma mudou | DESCARTAR (vinculado a paradigma) | indicar substituto no paradigma alvo |
| Regra é mecanismo do paradigma legado, paradigma é o mesmo | MIGRAR | sem ressalva |

## Lista de mecanismos típicos do paradigma (descartáveis quando paradigma muda)

### Procedural → event-driven
- Lock pessimista (`SELECT ... FOR UPDATE`)
- Transação ACID inteira em torno do fluxo
- Resposta síncrona ao usuário com side effect inline
- Retry implementado como `for` no controller

### OO clássico → OO com DI
- Active Record que mistura persistência e domínio
- Herança usada para reuso de comportamento (preferir composição)
- Singleton manual (preferir scoped DI)

### OO clássico → funcional
- Encapsulamento mutável (preferir tipos imutáveis)
- Métodos void com side effect (preferir retorno + função pura)

### OO com DI → event-driven
- Comandos síncronos com retorno imediato (preferir evento + ack)
- Orquestração centralizada (preferir coreografia)
- 2PC / transação distribuída (preferir saga)

### Síncrono → assíncrono em geral
- Timeout configurado em controller (vai para retry policy do consumer)
- Tratamento de erro como exceção propagada (vira DLQ)

## O que NUNCA descartar por paradigma

- Regras de negócio puras (cálculos, condições, derivações).
- Regras regulatórias.
- Invariantes de domínio.
- Direitos / permissões.

Essas regras mudam de **lugar** no paradigma novo, mas não somem.
