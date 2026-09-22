# Formula do cenario Valor (value-formula.md)

**Versao da formula:** 2.0

Documenta o calculo deterministico que o agente `reversa-pricing-estimate` aplica para o cenario Valor. A formula v2 substitui o multiplo fixo de 6 a 12 meses por captura percentual do valor economico anual declarado.

## Fonte e criterio

Value-based pricing usa o valor percebido ou economico para o cliente como base de preco, nao apenas custo interno ou preco de concorrentes.

Referencias:

- Hinterhuber, A. (2008), *Customer value-based pricing strategies: why companies resist*, Journal of Business Strategy, 29(4), DOI 10.1108/02756660810887079
- Nagle, Hogan e Zale, *The Strategy and Tactics of Pricing*, 5a ed., Routledge, 2016, especialmente Economic Value to the Customer

A faixa de 10% a 30% e uma heuristica comercial do Reversa para B2B/freelance/agencia. Ela deve ser descrita como captura de parte do valor anual, nao como lei academica universal.

## Passo 1: validacao de input

```
if monthly_return_declared == 0 AND cost_of_not_doing == 0:
  available = false
  explanation_pt_br = "Cenario Valor nao pode ser calculado: cliente nao declarou retorno mensuravel."
```

`users_impacted` e contexto comercial. Ele aparece no estimate.md, mas nao entra no calculo numerico v2.

## Passo 2: valor economico anual

```
annual_value =
  max(monthly_return_declared * 12, cost_of_not_doing)
```

O cliente pode declarar:

- retorno mensal recorrente
- custo anual de nao fazer
- ambos

Quando ambos existem, a formula usa o maior valor economico defensavel.

## Passo 3: captura de valor

```
value_capture_min = 0.10
value_capture_recommended = 0.20
value_capture_max = 0.30

preco_minimo = round_currency(annual_value * value_capture_min)
preco_recomendado = round_currency(annual_value * value_capture_recommended)
preco_maximo = round_currency(annual_value * value_capture_max)
```

## Passo 4: payback explicativo

Se `monthly_return_declared > 0`, calcule payback como explicacao secundaria:

```
payback_months_min = preco_minimo / monthly_return_declared
payback_months_max = preco_maximo / monthly_return_declared
```

Se `monthly_return_declared == 0`, grave `payback_months_min = null` e `payback_months_max = null`.

Payback nao define preco. Ele apenas ajuda o usuario a explicar a proposta.

## Exemplos

### Exemplo 1: retorno mensal claro

```
monthly_return_declared = 2000 BRL
cost_of_not_doing = 5000 BRL

annual_value = max(2000 * 12, 5000) = 24000
preco_minimo = 24000 * 0.10 = 2400
preco_recomendado = 24000 * 0.20 = 4800
preco_maximo = 24000 * 0.30 = 7200
payback_months_min = 1.2
payback_months_max = 3.6
```

### Exemplo 2: prevencao de perda anual

```
monthly_return_declared = 0
cost_of_not_doing = 60000 BRL

annual_value = max(0, 60000) = 60000
preco_minimo = 6000
preco_recomendado = 12000
preco_maximo = 18000
payback_months_min = null
payback_months_max = null
```

### Exemplo 3: sem dado mensuravel

```
monthly_return_declared = 0
cost_of_not_doing = 0

available = false
```

## Conversao para moeda de cobranca

Identica ao Esforco. Quando `profile.billing_currency` esta preenchido:

```
preco_minimo_billing = round_currency(preco_minimo / exchange_rate_to_local)
preco_recomendado_billing = round_currency(preco_recomendado / exchange_rate_to_local)
preco_maximo_billing = round_currency(preco_maximo / exchange_rate_to_local)
```

## Limites e premissas

1. O retorno declarado pelo cliente nao e validado pelo agente
2. A faixa de captura 10% a 30% e heuristica documentada
3. `users_impacted` nao entra no calculo numerico v2
4. Valores extremos nao sao truncados
5. A explicacao pode mencionar meses de payback, mas nao deve dizer que o preco e "6 a 12 meses"
