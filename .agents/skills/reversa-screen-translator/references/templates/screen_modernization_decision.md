---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: screen_modernization_decision
producedBy: screen-translator
decidedBy: <human-id ou null quando mode=skipped>
decidedAt: <ISO-8601 ou null quando mode=skipped>
mode: literal | modernized | hybrid | skipped
sourcePlatform: <slug ou null quando mode=skipped>
targetPlatform: <slug ou null quando mode=skipped>
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

> Quando `mode: skipped`, esta decisão **não passou por humano**: foi emitida automaticamente pelo Screen Translator porque o legado não tem UI. Apenas as seções "Contexto" e "Decisão" são preenchidas, com a razão da omissão; as demais ficam como N/A. O Inspector lê `mode: skipped` no front-matter e pula a paridade visual sem perguntar.


# Decisão de Modernização de Telas

> Decisão consciente sobre como traduzir as telas do sistema legado: paridade observável byte-a-byte, redesign idiomático para a plataforma alvo, ou combinação tela-a-tela.
> Este artefato é leitura obrigatória do próprio Screen Translator (para gerar `target_screens.md`), do Inspector (para construir parity tests adequados ao modo) e do agente de codificação.

## Contexto

- **Plataforma origem detectada**: <slug> (ex: `cobol-ansi-tui`, `delphi-vcl`, `asp-classic`, `android-xml`)
- **Confiança**: 🟢 CONFIRMADO | 🟡 INFERIDO | 🔴 LACUNA | ⚠️ AMBÍGUO
- **Plataforma alvo**: <slug> (ex: `go-cli`, `web-spa`, `flutter`, `tauri`)
- **Telas inventariadas**: <N>
- **Origem do inventário**: `_reversa_sdd/screens/inventory.json` + `_reversa_sdd/ui/inventory.md`
- **Adapter aplicado**: `<adapters/origem__alvo>` (ver `references/adapter-pairs.md`)

## Modos avaliados

### Modo: literal
- **Definição**: paridade observável byte-a-byte ou pixel-equivalente entre legado e novo.
- **Trade-offs**:
  - Custo de implementação: <alto | médio | baixo>
  - Fidelidade visual: <alta | média | baixa>
  - Viabilidade de parity tests construtivos: <sim | parcial | não>
  - Aceitação esperada do usuário final: <alta | média | baixa>
  - Débito técnico futuro: <alto | médio | baixo>
- **Recomendado**: <sim | não>
- **Justificativa**: <texto curto>

### Modo: modernizado
- **Definição**: redesign idiomático para a plataforma alvo, preservando informação e fluxo, mas re-expressando hierarquia e interação.
- **Trade-offs**:
  - Custo de implementação: <alto | médio | baixo>
  - Fidelidade visual: <alta | média | baixa>
  - Viabilidade de parity tests construtivos: <sim | parcial | não>
  - Aceitação esperada do usuário final: <alta | média | baixa>
  - Débito técnico futuro: <alto | médio | baixo>
- **Recomendado**: <sim | não>
- **Justificativa**: <texto curto>

### Modo: híbrido
- **Definição**: parte das telas em literal, parte em modernizado, com listas explícitas.
- **Trade-offs**:
  - Custo de implementação: <alto | médio | baixo>
  - Fidelidade visual mista: <descrição>
  - Viabilidade de parity tests: <descrição por subset>
  - Custo de manutenção da separação: <alto | médio | baixo>
- **Recomendado**: <sim | não>
- **Justificativa**: <texto curto>

## Decisão

- **Modo escolhido**: <literal | modernizado | híbrido>
- **Justificativa do humano**: <texto>
- **Alternativas descartadas**: <lista breve com razão>
- **Decidido em**: <ISO-8601>
- **Decidido por**: <nome ou identificador>

### Em modo híbrido, listas explícitas (obrigatórias)

**Telas em modo literal**:
- <tela 1>
- <tela 2>

**Telas em modo modernizado**:
- <tela 3>
- <tela 4>

> Listas vazias bloqueiam a Fase 2. O agente recusa prosseguir.

## Implicações pendentes para a Fase 2

| Etapa | Implicação | Como honrar |
|---|---|---|
| Geração de `target_screens.md` | <implicação> | <ação esperada> |
| Captura de golden files | <implicação> | <ação esperada> |
| Tokens do design-system | <implicação> | <ação esperada> |
| Conteúdo textual | Preservar literal salvo aprovação explícita de revisão linguística | <ação esperada> |

## Implicações para o Inspector

- **Estratégia de paridade**:
  - Modo literal → paridade observável byte-a-byte / pixel-equivalente, validada por golden files quando o oráculo executa.
  - Modo modernizado → contrato semântico (eventos, transições, conteúdo textual, estados), sem comparação visual byte-a-byte.
  - Modo híbrido → estratégia mista, declarada por tela em `parity_specs.md`.
- **Deviations conhecidas a propagar**: ver `screen_deviation_log.md`.

## Notas

<Pontos adicionais que o codificador, o Inspector e o agente precisam saber para honrar a decisão. Inclui, por exemplo, aprovação explícita de revisão linguística, tolerância a renderização aproximada, ou marcação de telas que não admitem modernização por exigência regulatória.>
