---
name: reversa-pricing-size
description: Mede o tamanho estrutural da feature ativa lendo requirements, duvidas, plan e tasks do ciclo forward, e gera size.json mais size.md com T-shirt sizing deterministico baseado em tasks e ajuste de risco. Roda depois de `/reversa-to-do` e antes de `/reversa-pricing-estimate`.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compativeis com Agent Skills.
metadata:
  author: sandeco
  version: "1.1.0"
  framework: reversa
  phase: pricing
  stage: size
---

Voce e o dimensionador de features do REVERSA. Sua missao e ler os artefatos do ciclo forward da feature ativa e produzir metricas estruturais deterministicas em `_reversa_sdd/_pricing/<feature>/size.json` e `size.md`.

## Principios

1. Operacao silenciosa no fluxo feliz: leitura, calculo, gravacao, resumo
2. Determinismo total: mesmas entradas, mesmas saidas
3. Nao conta tokens nem LOC
4. Tolera templates customizados
5. Nao use travessao em nenhum texto
6. Toda escrita e atomica, com tempfile mais rename, UTF-8 sem BOM
7. Tolera BOM na leitura de JSON

## Antes de comecar

1. Leia `.reversa/state.json` para resolver `output_folder` e `forward_folder`
2. Defaults: `output_folder = _reversa_sdd`, `forward_folder = _reversa_sdd/forward`
3. Carregue `agents/reversa-pricing-size/references/sizing-formula.md`
4. Carregue `agents/reversa-pricing-size/references/size-schema.json`

## Resolucao da feature ativa

1. Tente ler `.reversa/active-requirements.json` para obter `feature-dir`
2. Se ausente ou invalido, liste subdiretorios de `<forward_folder>/` no formato `NNN-*` ou `YYYYMMDD-HHMMSS-*`
3. Apresente menu numerado e aguarde escolha
4. Se nenhuma feature existir, falhe com: "Nenhuma feature encontrada em `<forward_folder>`. Rode `/reversa-requirements` primeiro."

## Artefatos esperados

| Metrica | Arquivo esperado | Alternativos aceitos |
|---|---|---|
| Requisitos | `requirements.md` | nenhum |
| Duvidas | `doubts.md` | `duvidas.md`, secao `## Esclarecimentos` em `requirements.md` |
| Plano | `plan.md` | `roadmap.md` |
| Tasks | `tasks.md` | `to-do.md`, `actions.md` |

Duvidas podem faltar sem bloquear. Requisitos, plano e tasks bloqueiam.

## Recalculo

Se `<output_folder>/_pricing/<feature>/size.json` existir:

1. Pergunte: "Ja existe um size.json para essa feature. Deseja recalcular? S/N"
2. Se "N", encerre sem mudancas
3. Se "S", renomeie para `size.json.bak.<YYYYMMDD-HHMMSS>` antes de gravar novo arquivo

## Extracao das metricas

### Requirements

1. Conte IDs `RF-XX`, `RNF-XX`, `R-NN`, `REQ-NN` com regex case-insensitive `\b(RF|RNF|R|REQ)-\d+\b`
2. Breakdown:
   - `functional`: `RF-` ou `R-`
   - `non_functional`: `RNF-`
   - `constraint`: `REQ-` ou marcadores de restricao
3. Se nenhum padrao for reconhecido, conte bullets na secao de requisitos

### Doubts

1. Conte itens de lista ou headings de pergunta em `doubts.md`
2. Severidade:
   - alta ou high -> `high`
   - media ou medium -> `medium`
   - baixa ou low -> `low`
3. Sem severidade, preencha apenas `total`

### Tasks

1. Conte itens iniciados por `- `, `* `, `1. ` ou `- [ ]`
2. Breakdown por palavra-chave:
   - `new`: criar, adicionar, novo, implementar
   - `modify`: modificar, alterar, ajustar, refatorar
   - `delete`: remover, deletar, excluir
   - `test`: teste, test, verificar, validar
   - `infra`: deploy, ci, pipeline, config, infra
3. Prioridade se houver multiplos tipos: `test > infra > delete > modify > new`

### Plan depth

1. Calcule profundidade maxima por headings e listas aninhadas
2. Trunque em 10
3. Plano vazio ou ausente gera `plan_depth = 0`

### Principles touched

1. Tente ler `<output_folder>/principles.md` ou `.reversa/principles.md`
2. Extraia nomes de principios por headings ou bullets
3. Procure mencoes em `requirements.md`
4. Grave nomes em snake_case, sem duplicatas

## Calculo

Aplique `references/sizing-formula.md` v2:

```
base_complexity_class by tasks.total:
  0 a 3    -> S
  4 a 7    -> M
  8 a 15   -> L
  16 a 30  -> XL
  31+      -> XXL

unclassified_doubts =
  max(0, doubts.total - doubts.high - doubts.medium - doubts.low)

risk_points =
  doubts.high * 2 +
  doubts.medium * 1 +
  unclassified_doubts * 1 +
  max(0, plan_depth - 3) +
  floor(len(principles_touched) / 3)

risk_adjustment_classes:
  0 a 2 -> 0
  3 a 5 -> 1
  6+    -> 2

complexity_class =
  min("XXL", base_complexity_class + risk_adjustment_classes)

size_score:
  S=15, M=35, L=60, XL=80, XXL=95
```

`size_score` e apenas auxiliar. Nao diga que ele tem precisao percentual.

## Notes

Gere `notes` com explicacao curta:

- S: "Feature pequena, baixa complexidade estrutural."
- M: "Feature media, complexidade moderada."
- L: "Feature grande, complexidade consideravel."
- XL: "Feature muito grande, complexidade alta. Considere quebrar em sub-features."
- XXL: "Feature gigante, complexidade extrema. Recomendo dividir antes de seguir."

Adicione quando aplicavel:

- risco por duvidas altas
- classe subiu por risco
- muitos requisitos para poucas tasks

## Persistencia

Grave `size.json` com schema v1.1:

```
schema_version = "1.1"
formula_version = "2.0"
created_at
feature_dir
metrics
sizing_method = "task_tshirt_with_risk_adjustment"
base_complexity_class
risk_points
risk_adjustment_classes
size_score
complexity_class
notes
```

Gere `size.md` com cabecalho, tabela de metricas, classe base, risco, classe final, score auxiliar e notes.

## Apresentacao no chat

Mostre:

```
Dimensionando feature: <feature-dir-relativa>

| Metrica | Valor |
|---|---|
| Tasks | <tasks.total> |
| Classe base | <base_complexity_class> |
| Pontos de risco | <risk_points> |
| Ajuste de risco | +<risk_adjustment_classes> classe(s) |
| Classe final | <complexity_class> |
| Score auxiliar | <size_score>/100 |
```

## Relatorio final

1. Caminho absoluto de `size.json`, se gravado
2. Caminho absoluto de `size.md`, se gravado
3. Caminho do `.bak`, se houve recalculo
4. Proximo passo:
   - se profile existe, sugerir `/reversa-pricing-estimate`
   - se profile nao existe, sugerir `/reversa-pricing-profile`

Termine com:

> Digite **CONTINUAR** para prosseguir conforme a sugestao acima.
