---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: screen_deviation_log
producedBy: screen-translator
mode: append-only
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Screen Deviation Log

> Registro de toda divergência entre o legado e a spec gerada em `target_screens.md`. Append-only. Deviations pendentes bloqueiam o handoff ao Inspector.
> Deviations aprovadas são propagadas para `parity_specs.md § Exceções` quando o Inspector rodar.

## Convenções

- **ID**: `DEV-NNN` (sequencial, três dígitos).
- **Tipo**:
  - `tecnica`: limitação técnica do alvo (ex: terminal Windows sem UTF-8 sem `chcp 65201`).
  - `modernizacao`: divergência intencional decorrente do modo modernizado.
  - `plataforma`: divergência forçada por incompatibilidade de plataforma (ex: Win16 → web).
  - `correcao`: bug visual do legado que o alvo corrige (ex: typo em label).
- **Aprovação**: `pendente` | `aprovado` | `rejeitado`.
- Deviation `aprovado` → também listada em `parity_specs.md § Exceções`.
- Deviation `pendente` → bloqueia handoff ao Inspector.
- Deviation `rejeitado` → arquivada com nota explícita; agente regenera a tela em modo conformante.

## Resumo

- **Total**: <N>
- **Pendentes**: <N>
- **Aprovadas**: <N>
- **Rejeitadas**: <N>

## Entradas

### DEV-001

| Campo | Valor |
|---|---|
| Tela afetada | <nome-canonical> |
| Tipo | `tecnica` \| `modernizacao` \| `plataforma` \| `correcao` |
| Descrição | <o que diverge entre legado e novo> |
| Motivo | <por que a divergência é necessária ou aceitável> |
| Origem no legado | <arquivo:linha> |
| Implicação para parity tests | <ex: comparação byte-a-byte falsa, usar comparação semântica> |
| Aprovação | `pendente` \| `aprovado` \| `rejeitado` |
| Aprovado por | <nome ou identificador, quando aprovado> |
| Aprovado em | <ISO-8601, quando aprovado> |
| Propaga para `parity_specs.md § Exceções` | sim \| não |

### DEV-002

(repetir o bloco acima para cada deviation)

## Telas com mais de uma deviation

| Tela | IDs |
|---|---|
| <tela X> | DEV-001, DEV-007 |

## Notas

<Observações gerais sobre o conjunto de deviations: padrões, aprendizados que valem para futuras migrações no mesmo par origem→alvo, sugestões de adapter melhorado para v2.>
