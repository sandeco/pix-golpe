# Formula do cenario Esforco (effort-formula.md)

**Versao da formula:** 2.0

Documenta o calculo deterministico que o agente `reversa-pricing-estimate` aplica para o cenario Esforco. A formula v2 remove a conversao linear antiga de score para horas e usa faixas de horas por T-shirt size, com fator de senioridade inspirado nos multiplicadores de capacidade de pessoal do COCOMO II.

## Fonte e criterio

COCOMO II e um modelo parametrico de estimativa de esforco que usa tamanho, atributos de produto, plataforma, pessoal e projeto. Para a UX do Reversa, usar o modelo completo seria complexo demais. A v2 usa apenas a ideia defensavel de multiplicadores de capacidade de pessoal, mantendo faixas de horas simples por classe.

Referencia principal:

- Barry Boehm et al., *Software Cost Estimation with COCOMO II*, Prentice Hall, 2000
- Carnegie Mellon SEI, visao geral de software cost estimation e COCOMO II: https://insights.sei.cmu.edu/blog/software-cost-estimation-explained/

## Passo 1: faixa base de horas para senior

```
hours_by_complexity_class_senior:
  S:   4 a 12 horas
  M:   12 a 32 horas
  L:   32 a 80 horas
  XL:  80 a 160 horas
  XXL: 160 a 320 horas, com recomendacao obrigatoria de quebrar escopo
```

Estas faixas sao heuristica do Reversa, baseada em T-shirt sizing. Elas sao mais honestas que uma constante linear porque estimativa de software tem incerteza real.

## Passo 2: fator de senioridade

```
seniority_factor:
  junior:      1.34
  mid:         1.15
  senior:      1.00
  staff_lead:  0.88
  principal:   0.76
```

Aliases aceitos para compatibilidade:

```
pleno -> mid
especialista -> staff_lead
staff -> staff_lead
lead -> staff_lead
```

## Passo 3: horas estimadas

```
horas_min = round(hours_min[complexity_class] * seniority_factor)
horas_max = round(hours_max[complexity_class] * seniority_factor)
horas_estimadas = round((horas_min + horas_max) / 2)
```

O campo `horas_estimadas` e o ponto medio para compatibilidade e resumo. A faixa `horas_min` a `horas_max` deve ser exibida no estimate.md.

## Passo 4: custo direto

```
custo_direto_min = horas_min * profile.hourly_rate
custo_direto_max = horas_max * profile.hourly_rate
custo_direto = horas_estimadas * profile.hourly_rate
```

## Passo 5: imposto aproximado

```
imposto_aproximado_min = custo_direto_min * profile.tax_factor
imposto_aproximado_max = custo_direto_max * profile.tax_factor
imposto_aproximado = custo_direto * profile.tax_factor
```

Quando `profile.tax_regime == "outro"` ou `tax_factor = 0`, o imposto nao e computado e o estimate.md deve mostrar aviso explicito.

Se o profile indicar que o fator inclui VAT, IVA ou imposto destacado na fatura, o estimate.md deve avisar que esse valor pode ser repassado ao cliente e nao necessariamente reduz margem.

## Passo 6: markup de projeto

O campo historico `margin_percent` deve ser tratado como **markup de projeto sobre custo direto**, nao como margem liquida contabil.

```
markup_min = custo_direto_min * (profile.margin_percent / 100)
markup_max = custo_direto_max * (profile.margin_percent / 100)
markup_aplicado = custo_direto * (profile.margin_percent / 100)
```

## Passo 7: preco total

```
preco_minimo = round_currency(custo_direto_min + imposto_aproximado_min + markup_min)
preco_maximo = round_currency(custo_direto_max + imposto_aproximado_max + markup_max)
preco_total = round_currency(custo_direto + imposto_aproximado + markup_aplicado)
```

`preco_total` e o ponto medio da faixa e existe para compatibilidade. O estimate.md deve destacar `preco_minimo` a `preco_maximo`.

## Exemplo

```
profile:
  country = BR, currency = BRL, seniority = senior
  hourly_rate = 100.00, margin_percent = 35, tax_factor = 0.15

size:
  complexity_class = L

hours_by_complexity_class_senior[L] = 32 a 80
seniority_factor[senior] = 1.00
horas_min = 32
horas_max = 80
horas_estimadas = 56

custo_direto_min = 3200.00
custo_direto_max = 8000.00
imposto_min = 480.00
imposto_max = 1200.00
markup_min = 1120.00
markup_max = 2800.00

preco_minimo = 4800.00 BRL
preco_maximo = 12000.00 BRL
preco_total = 8400.00 BRL
```

## Conversao para moeda de cobranca

Quando `profile.billing_currency` e `profile.exchange_rate_to_local` estao preenchidos:

```
valor_billing = round_currency(valor_local / exchange_rate_to_local)
```

O estimate.md deve imprimir a taxa usada:

```
1 <billing_currency> = <exchange_rate_to_local> <currency>
```

## Limites

1. A formula nao mistura senioridades de equipe
2. XXL continua calculavel, mas deve gerar recomendacao forte de quebrar escopo
3. A faixa de horas e heuristica, nao promessa de entrega
4. `size_score` nao entra no calculo de horas
