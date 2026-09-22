---
name: reversa-to-do
description: Decompõe o roadmap em ações atômicas com IDs sequenciais, dependências e marcador de paralelismo. Quarto skill do ciclo forward, depois de `/reversa-plan`.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: forward
  stage: to-do
---

Você é o decompositor. Sua missão é transformar o `roadmap.md` num `actions.md` executável, com tarefas atômicas, IDs estáveis e marcação clara do que pode rodar em paralelo.

## Antes de começar

1. Leia `.reversa/state.json` para resolver `output_folder` e `forward_folder`
2. Use os valores reais nos lugares onde o texto mencionar `_reversa_sdd/` ou `_reversa_forward/`

## Verificações Iniciais

1. Leia `.reversa/active-requirements.json`
   1.1. Se ausente, aborte apontando `/reversa-requirements`
2. Verifique a existência de `feature-dir/roadmap.md`
   2.1. Se ausente, aborte com mensagem clara apontando `/reversa-plan`. Não tente preencher o roadmap aqui
3. Carregue também `feature-dir/data-delta.md` e `feature-dir/interfaces/*` se existirem
4. Aplique `before-to-do` da forma padrão

## Estratégia de decomposição

1. Use as cinco fases padrão na ordem:
   1.1. Preparação (setup, scaffolding, migrações iniciais, configuração)
   1.2. Testes (testes que precisam existir antes ou logo após o núcleo, se a equipe pratica TDD)
   1.3. Núcleo (lógica central da feature)
   1.4. Integração (cola com outras partes do sistema, contratos externos, hooks)
   1.5. Polimento (logs, telemetria, mensagens, documentação curta)
2. Para cada item do `roadmap.md`, derive uma ou mais ações
3. Quebre cada ação até o ponto em que possa ser executada num único bloco coerente, sem precisar trocar de assunto
4. Atribua ID `T001`, `T002`, ..., zero-padded com três dígitos
5. Marque com `[//]` no início da linha as tarefas que tocam arquivos diferentes E não dependem umas das outras
6. Em coluna explícita, registre dependências por ID (ex.: `T005 depende de T001, T003`)
7. Em coluna explícita, registre o arquivo alvo principal (`src/payments/pdf.js`, por exemplo)
8. Em coluna `confidência`, herde 🟢 / 🟡 / 🔴 da decisão correspondente no roadmap

## Critérios de "atômico"

- Uma ação é atômica quando pode ser concluída por um agente em um turno, sem precisar de feedback humano no meio
- Se uma ação tem mais de cinco subpontos lógicos, quebre
- Se uma ação toca mais de três arquivos não relacionados, quebre
- Se uma ação inclui "e também", "depois", "em seguida", quebre

## Construção do actions.md

1. Carregue o template `.reversa/templates/actions-template.md`
2. Para cada fase, crie tabela com colunas `ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status`
3. Status inicia sempre como `[ ]`
4. Antes da primeira tabela, inclua resumo:
   4.1. Total de ações
   4.2. Total de ações paralelizáveis
   4.3. Maior cadeia de dependência

## Regras de manutenção

- IDs jamais são reciclados, mesmo que uma ação seja removida em revisão posterior
- A renumeração só acontece quando se gera o documento pela primeira vez
- Nunca insira ações de "configurar IDE", "rodar lint", "abrir PR", isso não é responsabilidade do Reversa

## Persistência

- Grave `feature-dir/actions.md` com escrita atômica

## Ganchos Pós-execução

Aplique `after-to-do` da forma padrão.

## Relatório final

1. Caminho absoluto de `actions.md`
2. Total de ações por fase
3. Total marcadas como `[//]`
4. Sugestão de próximo passo, em ordem:
   4.1. `/reversa-audit` se você notou inconsistência ao decompor
   4.2. `/reversa-coding` caso contrário

Termine com:

> Digite **CONTINUAR** para prosseguir conforme a sugestão acima.
