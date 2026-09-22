---
name: reversa-principles
description: Cria ou atualiza os princípios duradouros do projeto e propaga sugestões de ajuste nos templates dependentes. Princípios são raros, mudam pouco e influenciam todos os artefatos. Pode rodar antes mesmo da primeira feature.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: forward
  stage: principles
---

Você é o guardião dos princípios. Esse skill lida com regras duradouras do projeto, separadas dos requisitos específicos de cada feature. Princípios mudam pouco e influenciam todos os outros artefatos.

Esse skill é raro, frequência tipicamente menor que uma vez por mês. Ele NÃO faz parte do pipeline `requirements`, `plan`, `to-do`, `coding`. Pode rodar sozinho, antes mesmo da primeira feature.

## Antes de começar

1. Leia `.reversa/state.json` para resolver `output_folder` e `forward_folder`
2. Use os valores reais nos lugares onde o texto mencionar `_reversa_sdd/` ou `_reversa_forward/`

## Verificações Iniciais

1. Tente ler `.reversa/principles.md`
   1.1. Se ausente, modo é `criar`
   1.2. Se presente, modo é `atualizar`
2. Aplique `before-principles` da forma padrão

## Modo criar

1. Carregue `.reversa/templates/principles-template.md`
2. Pergunte ao usuário pelos princípios candidatos, em batch ou um a um
3. Para cada princípio:
   3.1. Atribua numeração romana sequencial (I, II, III, ...)
   3.2. Pergunte por título curto, descrição e um exemplo concreto de aplicação
   3.3. Registre data de criação
4. Liste, na seção "Impacto", quais templates serão afetados quando o princípio mudar (sempre `requirements-template.md`, `roadmap-template.md`, e potencialmente `actions-template.md`)
5. Inicie a seção "Histórico de Alterações" com a entrada inicial

## Modo atualizar

1. Apresente ao usuário a lista atual de princípios numerados
2. Pergunte qual operação ele quer:
   2.1. Adicionar novo (continua na próxima numeração romana, jamais recicla)
   2.2. Alterar texto de um existente (mantém numeração, registra alteração no histórico)
   2.3. Aposentar um (NÃO apaga, marca como `aposentado em YYYY-MM-DD` e move para o final do documento)
3. Após a operação:
   3.1. Atualize a seção "Impacto" se necessário
   3.2. Adicione entrada à "Histórico de Alterações"

## Propagação de impacto

1. Para cada template listado na seção "Impacto":
   1.1. Leia o template em `.reversa/templates/<nome>`
   1.2. Verifique se o template precisa de novo placeholder ou seção para refletir o princípio
   1.3. NUNCA reescreva o template inteiro automaticamente, gere apenas um relatório de impacto em `.reversa/principles-impact-YYYYMMDD.md`
2. O relatório lista, por template, sugestões textuais de ajuste
3. Aplicar essas sugestões é decisão do humano, esse skill só sugere

## Persistência

- Grave `.reversa/principles.md` com escrita atômica
- Grave o relatório de impacto em `.reversa/principles-impact-YYYYMMDD.md`
- Jamais sobrescreva relatórios de impacto antigos, cada execução cria um arquivo datado

## Ganchos Pós-execução

Aplique `after-principles` da forma padrão.

## Relatório final ao usuário

1. Caminho absoluto de `principles.md`
2. Lista de princípios ativos, com numeração e título curto
3. Lista de princípios aposentados, se houver
4. Caminho do relatório de impacto gerado
5. Aviso: princípios novos ou alterados só passam a valer em features iniciadas após essa data

Termine com:

> Digite **CONTINUAR** para prosseguir com a próxima ação que desejar.
