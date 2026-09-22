# Defaults de `--auto`

Quando o usuário invoca `/reversa-migrate --auto`, o orquestrador pula pausas humanas e aplica estes defaults. Antes de iniciar, o aviso ao usuário lista cada um deles. Cada item auto-aplicado é registrado em `ambiguity_log.md` com tag `auto-decidido` para revisão posterior.

## Paradigm Advisor
- Escolha **opção 1: adotar paradigma natural da stack alvo**.
- `derived_appetite` = `transformational`.

## Curator
- Itens DECISÃO HUMANA são marcados como pendentes em `ambiguity_log.md` e não bloqueiam o pipeline.
- Itens 🟡 INFERIDOS → MIGRAR (com nota "validar no agente de codificação").
- Itens 🔴 LACUNA e ⚠️ AMBÍGUOS → DESCARTAR com nota explícita "auto-descartado, requer revisão".

## Strategist
- Adota a estratégia marcada como **recomendada**.
- Riscos `crítico` que dependeriam de owner humano ficam com `owner = "a definir"` em `risk_register.md`.

## Designer
- **Topologia (Fase 1)**: aceita a topologia moderna proposta (opção 2). Justificativa registrada em `topology_decision.md` é a do próprio Designer; no `ambiguity_log.md` fica a tag `auto-decidido` para revisão posterior. Rationale: `--auto` é para usuários que querem o caminho recomendado; refusing-to-decide pararia o pipeline e violaria o contrato de `--auto`.
- **Arquitetura (Fase 2)**: aprova a primeira proposta sem iteração.
- Bounded contexts, eventos e ADRs são aceitos como propostos.

## Screen Translator
- **Modo (Fase 1)**: adota o modo recomendado pelo agente para o par origem→alvo detectado (literal para pares textuais; modernizado para mudanças de plataforma; híbrido só com lista explícita, portanto nunca em `--auto`).
- **Geração (Fase 2)**: aceita o `target_screens.md` gerado e propaga deviations como `pendente`. `--auto` não aprova deviations sozinho; elas ficam em `ambiguity_log.md` como `auto-decidido` para revisão posterior, sem bloquear o handoff (exceção a `--auto`: se uma deviation for `tipo=correcao` em modo literal, o agente recusa e pede aprovação humana mesmo em `--auto`, pois mudar texto sem aval rompe expectativa).
- **Captura de golden files**: não automatiza em `--auto` (driver de oráculo é OQ-02). Apenas emite `manifest.yaml` com comandos sugeridos.
- **Legado sem UI**: marca status `skipped` automaticamente, sem perguntar.
- **Pré-requisitos Discovery ausentes** (`_reversa_sdd/design-system/` ou `_reversa_sdd/ui/inventory.md`): cria `tokens-derived.md` mínimo e constrói inventário só a partir do código fonte; alerta no `ambiguity_log.md`.

## Inspector
- Usa critérios de paridade derivados diretamente do paradigma escolhido (ver `parity-coverage-matrix.md` no agente).
- Não negocia critério "paridade aceita" com o usuário.

## Modificações manuais detectadas
- Adota **opção (a)**: preservar a versão modificada manualmente e abortar regeneração desse artefato. Nunca destrói trabalho humano.

## Aviso obrigatório

Sempre antes de iniciar `--auto`, apresentar:

> "⚠️ Modo `--auto` ativado. Os defaults abaixo serão aplicados sem pausa para confirmação:
> - Paradigm Advisor: adotar paradigma natural da stack (transformacional).
> - Curator: itens ⚠️/🔴 serão DESCARTADOS com nota; 🟡 serão MIGRADOS com nota.
> - Strategist: estratégia recomendada será adotada.
> - Designer (topologia): topologia moderna proposta será adotada (opção 2).
> - Designer (arquitetura): primeira proposta de arquitetura será aceita.
> - Screen Translator (modo): adota o modo recomendado para o par origem→alvo. Modo híbrido nunca em `--auto`. Em legado sem UI, status `skipped`.
> - Screen Translator (geração): deviations ficam pendentes em `ambiguity_log.md` (não aprovadas). Captura de golden files não automatizada (apenas manifesto).
> - Inspector: critérios de paridade derivados do paradigma sem ajuste interativo.
>
> O `handoff.md` final destacará todos os itens auto-decididos para revisão posterior.
> Confirma? (s/N)"
