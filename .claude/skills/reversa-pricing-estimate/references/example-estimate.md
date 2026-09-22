# Estimativa de Preco

**Feature:** `_reversa_sdd/forward/042-pagamento-pix`
**Gerado em:** 2026-05-06 16:42 UTC
**Versao dos calculos:** Esforco v2.0, Valor v2.0, Mercado v2.0

**Pre-requisitos consumidos:**
- Profile: `_reversa_sdd/_pricing/profile.json`
- Size: `_reversa_sdd/_pricing/042-pagamento-pix/size.json` (classe `L`, score auxiliar `60`)

## Visao geral

| Cenario | Faixa | Comentario |
|---|---|---|
| **Esforco** | 4.800,00 a 12.000,00 BRL | 32 a 80h, custo + imposto + markup |
| **Valor** | 2.400,00 a 7.200,00 BRL | 10% a 30% do valor anual declarado |
| **Faixa de Mercado** | 3.200,00 a 16.000,00 BRL | taxa hora fonteada por pais e senioridade |

## Cenario Esforco

**O que e:** preco calculado a partir de horas provaveis, taxa hora, reserva tributaria aproximada e markup de projeto. E o piso defensavel para nao subsidiar o cliente.

**Quando usar:** sempre como sanity check. Cobrar abaixo do Esforco significa assumir prejuizo ou reduzir demais o lucro do projeto.

| Item | Valor |
|---|---|
| Classe de complexidade | L |
| Senioridade | senior |
| Fator de senioridade | 1,00 |
| Horas estimadas | 32 a 80 h |
| Ponto medio | 56 h |
| Taxa hora | 100,00 BRL/h |
| Custo direto | 3.200,00 a 8.000,00 BRL |
| Reserva tributaria aproximada | 480,00 a 1.200,00 BRL |
| Markup de projeto (35%) | 1.120,00 a 2.800,00 BRL |
| **Faixa Esforco** | **4.800,00 a 12.000,00 BRL** |
| Ponto medio | 8.400,00 BRL |

Aviso: parte do fator tributario pode ser imposto destacado e repassado ao cliente. Valide com contador.

## Cenario Valor

**O que e:** preco baseado em parte do valor economico anual que a feature gera ou protege para o cliente. O Reversa usa captura de 10% a 30% do valor anual declarado.

**Quando usar:** quando o cliente consegue declarar retorno, economia ou custo de nao fazer.

| Item | Valor |
|---|---|
| Retorno mensal declarado | 2.000,00 BRL |
| Usuarios impactados | 500 |
| Custo de nao fazer | 5.000,00 BRL |
| Valor anual usado | 24.000,00 BRL |
| Captura aplicada | 10% a 30% |
| Preco recomendado | 4.800,00 BRL |
| **Faixa Valor** | **2.400,00 a 7.200,00 BRL** |
| Payback aproximado | 1,2 a 3,6 meses |

## Cenario Faixa de Mercado

**O que e:** faixa derivada de benchmark horario por pais e senioridade, multiplicado pela mesma faixa de horas do cenario Esforco.

**Quando usar:** como referencia externa. A v2 nao multiplica por perfil de cliente porque nao ha dataset publico confiavel para isso.

| Item | Valor |
|---|---|
| Pais / Senioridade | Brasil / senior |
| Modelo / Perfil cliente | escopo_fechado / pequena_empresa |
| Complexidade | L |
| Taxa hora de mercado | 100,00 a 200,00 BRL/h |
| Tipo de fonte | salary_derived_freelance_estimate |
| Ano de referencia | 2025-2026 |
| Fontes | Portal Salario CAGED, Glassdoor Brasil |
| **Faixa Mercado** | **3.200,00 a 16.000,00 BRL** |

## Como escolher entre os tres

O Valor declarado gera uma faixa menor que o Esforco medio. Use Esforco como piso defensavel e Mercado como referencia externa. Para este cliente, cobre abaixo de 4.800 BRL apenas se houver motivo estrategico claro.

Heuristica geral:

1. Cliente sem retorno claro: use Esforco como piso e Mercado como referencia externa
2. Cliente com retorno alto e claro: prefira Valor, com Esforco apenas como piso minimo
3. Esforco acima do Mercado: revise profile, size ou adequacao do cliente
4. Mercado acima do Esforco: ha espaco para subir markup ou melhorar proposta

## Disclaimer

Os numeros nesta estimativa sao aproximacoes para orientacao de orcamento, nao garantia de fechamento de venda. O fator de imposto e uma reserva aproximada, nao uma aliquota legal exata. Validacao tributaria real e responsabilidade do contador do usuario. A faixa de mercado e estatica e baseada nas fontes documentadas em `market-benchmarks.md`. O retorno declarado pelo cliente no cenario Valor e input bruto, nao validado. Recomenda-se adicionar `_reversa_sdd/_pricing/<feature>/estimate.{md,json}` ao `.gitignore` antes de commitar.
