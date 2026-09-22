---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: topology_decision
producedBy: designer
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Topology Decision

> Decisão consciente sobre como organizar o sistema novo: preservar a topologia do legado, adotar uma topologia moderna ou aplicar um híbrido.
> Este artefato é leitura obrigatória do próprio Designer (para decompor bounded contexts) e do agente de codificação (para criar a árvore de pastas).

## Topologia do legado detectada
- **Padrão organizacional**: <package-by-layer | package-by-feature | feature-sliced | módulos por domínio | DDD com bounded contexts | monorepo | monolito sem fronteiras claras | híbrido: ...>
- **Confiança**: 🟢 CONFIRMADO | 🟡 INFERIDO | 🔴 LACUNA | ⚠️ AMBÍGUO
- **Evidências**:
  - <evidência 1, com referência a artefato do `_reversa_sdd/` (architecture.md, inventory.md, dependencies.md)>
  - <evidência 2>
- **Mapa da árvore legada** (resumido):
  ```
  <árvore curta com pastas/módulos principais>
  ```

## Diagnóstico estrutural
- **Acoplamento**: <alto | médio | baixo, com evidência>
- **Coesão por módulo**: <alta | média | baixa, com evidência>
- **Módulos órfãos / mortos**: <lista, ou "nenhum">
- **Camadas redundantes**: <lista, ou "nenhuma">
- **Violações de fronteira**: <lista, ou "nenhuma">
- **Mistura de paradigmas/estilos**: <descrição, ou "homogêneo">
- **Avaliação geral**: <saudável | problemática | parcialmente problemática>

## Topologia moderna proposta
- **Padrão**: <hexagonal | vertical slices | feature-sliced | DDD com bounded contexts | package-by-feature | modularização por capability | monorepo com pnpm/turborepo | ...>
- **Justificativa**: <por que esse padrão se encaixa no stack alvo, no domínio, no tamanho do time e na estratégia de migração escolhida>
- **Ganhos concretos esperados**:
  - <ganho 1: ex. testabilidade isolada por feature>
  - <ganho 2: ex. deploy independente por bounded context>
  - <ganho 3: ex. onboarding mais rápido>
- **Custo / risco**:
  - <custo 1: ex. curva de aprendizado da equipe>
  - <custo 2: ex. esforço de reorganização>
- **Esboço da árvore proposta**:
  ```
  <árvore curta com pastas/módulos no padrão moderno>
  ```

## Opções apresentadas ao usuário
1. **Preservar topologia legada** (conservador)
   - Consequências: mantém mapa mental do time atual; perpetua eventuais débitos estruturais; reduz risco de migração.
2. **Adotar topologia moderna proposta** (transformacional)
   - Consequências: rompe com débito estrutural; exige aprendizado; maximiza ganhos do stack alvo.
3. **Híbrido** (equilibrado)
   - Consequências: <descrever quais bordas preservam o legado e quais adotam o moderno, com justificativa por borda>

## Decisão do usuário
- **Escolha**: <1 | 2 | 3>
- **Justificativa do usuário**: <texto livre>
- **Decidido em**: <ISO-8601>

## Mapeamento legado → novo
| Módulo / pasta legada | Bounded context novo | Tipo | Observações |
|---|---|---|---|
| <legado A> | <novo X> | preservado | <obs> |
| <legado B + C> | <novo Y> | fundido | <justificativa> |
| <legado D> | <novo Y1, Y2> | dividido | <justificativa> |
| (vazio) | <novo Z> | novo | <justificativa> |
| <legado E> | (descartado) | removido | ver `discard_log.md` |

## Implicações pendentes para próximos passos do Designer
| Etapa do Designer | Implicação | Como honrar |
|---|---|---|
| Bounded contexts | <implicação> | <ação esperada> |
| target_architecture | <implicação> | <ação esperada> |
| target_domain_model | <implicação> | <ação esperada> |
| target_data_model | <implicação> | <ação esperada> |

## Notas
<Qualquer ponto adicional que o agente de codificação precisa saber para criar a árvore de pastas e respeitar a topologia escolhida.>
