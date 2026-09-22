# Template do estimate.md

Este e o template Markdown que o agente `reversa-pricing-estimate` usa para gerar `_reversa_sdd/_pricing/<feature>/estimate.md`. Substitua todos os `<placeholders>` pelos valores reais. Mantenha a estrutura fixa.

```markdown
# Estimativa de Preco

**Feature:** `<feature_dir_relativa>`
**Gerado em:** <created_at_local_legivel>
**Versao dos calculos:** Esforco v<effort_formula_version>, Valor v<value_formula_version>, Mercado v<market_table_version>

**Pre-requisitos consumidos:**
- Profile: `<output_folder>/_pricing/profile.json`
- Size: `<output_folder>/_pricing/<feature>/size.json` (classe `<complexity_class>`, score auxiliar `<size_score>`)

## Visao geral

| Cenario | Faixa | Comentario |
|---|---|---|
| **Esforco** | <esforco_str> | <horas_min> a <horas_max>h, custo + imposto + markup |
| **Valor** | <valor_str> | 10% a 30% do valor anual declarado |
| **Faixa de Mercado** | <mercado_str> | taxa hora fonteada por pais e senioridade |

## Cenario Esforco

**O que e:** preco calculado a partir de horas provaveis, taxa hora, reserva tributaria aproximada e markup de projeto. E o piso defensavel para nao subsidiar o cliente.

**Quando usar:** sempre como sanity check. Cobrar abaixo do Esforco significa assumir prejuizo ou reduzir demais o lucro do projeto.

| Item | Valor |
|---|---|
| Classe de complexidade | <complexity_class> |
| Senioridade | <seniority> |
| Fator de senioridade | <seniority_factor> |
| Horas estimadas | <horas_min> a <horas_max> h |
| Ponto medio | <horas_estimadas> h |
| Taxa hora | <hourly_rate> <currency>/h |
| Custo direto | <custo_direto_min> a <custo_direto_max> <currency> |
| Reserva tributaria aproximada | <imposto_aproximado_min> a <imposto_aproximado_max> <currency> |
| Markup de projeto (<margin_percent>%) | <markup_aplicado_min> a <markup_aplicado_max> <currency> |
| **Faixa Esforco** | **<preco_minimo> a <preco_maximo> <currency>** |
| Ponto medio | <preco_total> <currency> |

<aviso_vat_se_aplicavel>
<bloco_billing_currency_se_aplicavel>

## Cenario Valor

**O que e:** preco baseado em parte do valor economico anual que a feature gera ou protege para o cliente. O Reversa usa captura de 10% a 30% do valor anual declarado.

**Quando usar:** quando o cliente consegue declarar retorno, economia ou custo de nao fazer.

<se valor.available>

| Item | Valor |
|---|---|
| Retorno mensal declarado | <monthly_return_declared> <currency> |
| Usuarios impactados | <users_impacted> |
| Custo de nao fazer | <cost_of_not_doing> <currency> |
| Valor anual usado | <annual_value> <currency> |
| Captura aplicada | 10% a 30% |
| Preco recomendado | <preco_recomendado> <currency> |
| **Faixa Valor** | **<preco_minimo> a <preco_maximo> <currency>** |
| Payback aproximado | <payback_str> |

<bloco_billing_currency_se_aplicavel>

<se NOT valor.available>

> **Cenario Valor nao disponivel:** <razao_unavailable>

</se>

## Cenario Faixa de Mercado

**O que e:** faixa derivada de benchmark horario por pais e senioridade, multiplicado pela mesma faixa de horas do cenario Esforco.

**Quando usar:** como referencia externa. A v2 nao multiplica por perfil de cliente porque nao ha dataset publico confiavel para isso.

<se mercado.available>

| Item | Valor |
|---|---|
| Pais / Senioridade | <country_nome> / <seniority> |
| Modelo / Perfil cliente | <pricing_model> / <client_profile> |
| Complexidade | <complexity_class> |
| Taxa hora de mercado | <market_hourly_min> a <market_hourly_max> <currency>/h |
| Tipo de fonte | <source_kind> |
| Ano de referencia | <source_year> |
| Fontes | <sources> |
| **Faixa Mercado** | **<preco_minimo_mercado> a <preco_maximo_mercado> <currency>** |

<se fallback aplicado>

> Fallback aplicado: <razao>

</se>

<bloco_billing_currency_se_aplicavel>

<se NOT mercado.available>

> **Cenario Mercado nao disponivel:** <razao_unavailable>

</se>

## Como escolher entre os tres

<orientacao_pt_br_baseada_nos_cenarios>

Heuristica geral:

1. Cliente sem retorno claro: use Esforco como piso e Mercado como referencia externa
2. Cliente com retorno alto e claro: prefira Valor, com Esforco apenas como piso minimo
3. Esforco acima do Mercado: revise profile, size ou adequacao do cliente
4. Mercado acima do Esforco: ha espaco para subir markup ou melhorar proposta

## Disclaimer

Os numeros nesta estimativa sao aproximacoes para orientacao de orcamento, nao garantia de fechamento de venda. O fator de imposto e uma reserva aproximada, nao uma aliquota legal exata. Validacao tributaria real e responsabilidade do contador do usuario. A faixa de mercado e estatica e baseada nas fontes documentadas em `market-benchmarks.md`. O retorno declarado pelo cliente no cenario Valor e input bruto, nao validado. Recomenda-se adicionar `_reversa_sdd/_pricing/<feature>/estimate.{md,json}` ao `.gitignore` antes de commitar.
```

## Billing currency

Quando `profile.billing_currency` esta preenchido, cada cenario ganha linha extra:

```markdown
| Em <billing_currency> | <valor_billing> <billing_currency> (cambio: 1 <billing_currency> = <exchange_rate_to_local> <currency>) |
```

## Comentarios curtos

| Cenario | Comentario curto |
|---|---|
| Esforco | `<horas_min> a <horas_max>h, custo + imposto + markup` |
| Valor | `10% a 30% do valor anual declarado` ou `Nao disponivel` |
| Mercado | `taxa hora fonteada por pais e senioridade` ou `Nao disponivel` |
