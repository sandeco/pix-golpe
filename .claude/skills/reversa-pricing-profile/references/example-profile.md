# Perfil de Cobranca

**Criado em:** 2026-05-06 14:32 UTC
**Versao do schema:** 1.1

## Identificacao

| Campo | Valor |
|---|---|
| Pais | Brasil (BR) |
| Moeda local | Real Brasileiro (BRL) |
| Senioridade | senior |

## Custo direto

| Campo | Valor |
|---|---|
| Modo de taxa hora | Derivado |
| Renda mensal liquida desejada | 12.000,00 BRL |
| Horas faturaveis por mes | 120 |
| Taxa hora calculada | 100,00 BRL/h |

## Markup e impostos

| Campo | Valor |
|---|---|
| Markup de projeto | 35% |
| Regime tributario | Simples Nacional, servicos de TI |
| Fator aproximado | 15% |
| Tipo do fator | effective_reserve_estimate |
| Fonte do fator | Receita Federal, Simples Nacional, anexos e fator R |
| Inclui imposto destacado | Sim |
| Aviso de repasse | Sim |
| Confianca no regime | Alta, escolha explicita |

## Modelo comercial

| Campo | Valor |
|---|---|
| Modelos de cobranca | escopo_fechado, time_and_materials |
| Perfil de cliente | pequena_empresa |
| Cobranca em moeda estrangeira | Nao |

## Disclaimer

O fator de imposto registrado e uma reserva aproximada para orcamento, nao uma aliquota legal exata. Validacao tributaria real e responsabilidade do contador do usuario. Este arquivo contem dados financeiros sensiveis. Recomenda-se adicionar `_reversa_sdd/_pricing/profile.json` e `_reversa_sdd/_pricing/profile.md` ao `.gitignore` antes de commitar.
