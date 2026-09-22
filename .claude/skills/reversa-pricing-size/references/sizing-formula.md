# Formula de dimensionamento (sizing-formula.md)

**Versao da formula:** 2.0
**Versao do schema do size.json:** 1.1

Documenta o calculo deterministico que o agente `reversa-pricing-size` aplica para transformar os artefatos do ciclo forward em uma classe de complexidade (`S/M/L/XL/XXL`). A formula v2 abandona a soma linear de pesos arbitrarios e passa a usar T-shirt sizing baseado em tasks, com ajuste separado de risco.

## Fonte e criterio

O Reversa v1 precisa de uma medida compreensivel para usuario leigo, multi-engine e derivada dos arquivos ja produzidos em `_reversa_sdd/forward/<feature>/`.

Function Points (IFPUG, ISO/IEC 20926) e COSMIC (ISO/IEC 19761) sao padroes formais de medicao funcional, mas exigem classificacao especializada. Para a UX do Reversa, a melhor base e estimativa agil aproximada, inspirada em Story Points e T-shirt sizing. Mike Cohn, em *Agile Estimating and Planning* (Addison-Wesley, 2005), descreve estimativas relativas e tamanhos aproximados como praticas de planejamento agil.

Esta formula nao afirma que as faixas sao padrao universal. Ela documenta uma heuristica simples do Reversa, com base em T-shirt sizing, e mantem os fatores de risco separados para evitar falsa precisao.

## Entradas

As entradas continuam vindo de `metrics`:

- `tasks.total`
- `doubts.high`, `doubts.medium`, `doubts.low`, `doubts.total`
- `plan_depth`
- `principles_touched`
- `requirements.total`, usado apenas como alerta de consistencia, nao como driver primario

## Passo 1: classe base por quantidade de tasks

`tasks.total` e a melhor proxy de tamanho porque o ciclo forward ja quebrou a feature em unidades de trabalho.

```
if tasks.total <= 0:       base_complexity_class = "S"
elif tasks.total <= 3:     base_complexity_class = "S"
elif tasks.total <= 7:     base_complexity_class = "M"
elif tasks.total <= 15:    base_complexity_class = "L"
elif tasks.total <= 30:    base_complexity_class = "XL"
else:                      base_complexity_class = "XXL"
```

## Passo 2: pontos de risco

Risco nao e tamanho. Ele ajusta a classe para cima quando a feature tem incerteza, profundidade ou impacto transversal.

```
unclassified_doubts =
  max(0, doubts.total - doubts.high - doubts.medium - doubts.low)

risk_points =
  doubts.high * 2 +
  doubts.medium * 1 +
  unclassified_doubts * 1 +
  max(0, plan_depth - 3) +
  floor(len(principles_touched) / 3)
```

`doubts.low` nao sobe risco na v2. Duvida baixa e ruido esperado de refinamento.

## Passo 3: ajuste de risco

```
if risk_points <= 2:       risk_adjustment_classes = 0
elif risk_points <= 5:     risk_adjustment_classes = 1
else:                      risk_adjustment_classes = 2
```

## Passo 4: classe final

Classes sao ordenadas assim:

```
S=0, M=1, L=2, XL=3, XXL=4
```

```
complexity_class =
  class_from_index(min(4, index(base_complexity_class) + risk_adjustment_classes))
```

## Passo 5: size_score auxiliar

`size_score` fica apenas para compatibilidade e leitura rapida. Ele nao deve mais dirigir horas diretamente.

```
size_score_by_class:
  S:   15
  M:   35
  L:   60
  XL:  80
  XXL: 95
```

## Campos recomendados no size.json

O agente deve gravar estes campos alem dos campos antigos:

```
sizing_method = "task_tshirt_with_risk_adjustment"
base_complexity_class = <classe antes do risco>
risk_points = <inteiro>
risk_adjustment_classes = <0, 1 ou 2>
size_score = <midpoint auxiliar da classe final>
```

## Exemplos de calculo

### Exemplo 1: feature pequena (S)

```
tasks.total = 3
doubts.high = 0
doubts.medium = 0
doubts.low = 0
doubts.total = 0
plan_depth = 2
principles_touched = []

base_complexity_class = S
risk_points = 0
risk_adjustment_classes = 0
complexity_class = S
size_score = 15
```

### Exemplo 2: feature media que sobe para L por risco

```
tasks.total = 7
doubts.total = 3 (high=1, medium=2, low=0)
plan_depth = 3
principles_touched = ["non_destructive", "multi_engine", "handoff_pattern"]

base_complexity_class = M
risk_points = 1*2 + 2*1 + 0 + 0 + floor(3/3) = 5
risk_adjustment_classes = 1
complexity_class = L
size_score = 60
```

### Exemplo 3: feature grande (XL)

```
tasks.total = 12
doubts.total = 1 (high=0, medium=1, low=0)
plan_depth = 4
principles_touched = 2

base_complexity_class = L
risk_points = 0 + 1 + 0 + 1 + 0 = 2
risk_adjustment_classes = 0
complexity_class = L
size_score = 60
```

### Exemplo 4: feature gigante (XXL)

```
tasks.total = 31
doubts.total = 6 (high=2, medium=3, low=1)
plan_depth = 6
principles_touched = 8

base_complexity_class = XXL
risk_points = 2*2 + 3*1 + 0 + 3 + floor(8/3) = 12
risk_adjustment_classes = 2
complexity_class = XXL
size_score = 95
```

## Alertas de consistencia

Requisitos nao entram no calculo primario, mas podem gerar nota:

```
if requirements.total >= 12 and tasks.total <= 3:
  notes += "Muitos requisitos para poucas tasks. Verifique se tasks.md esta granular o bastante."
```

## Limites e premissas

1. A formula mede tamanho estrutural antes do coding, portanto nao usa LOC
2. Tokens nao sao contados
3. `size_score` e auxiliar, nao deve ser convertido diretamente em horas
4. XXL deve gerar recomendacao de quebrar escopo antes de precificar ou codar
5. Se mudar limite de classe, bump em `formula_version`
