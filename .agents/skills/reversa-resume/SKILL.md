---
name: reversa-resume
description: Retoma uma feature pausada (listada em paused-features de active-requirements.json) e a torna ativa. NÃO cria features novas, apenas troca a ativa pela escolhida e (quando faz sentido) move a ativa atual para paused-features.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: forward
  stage: resume
---

Você é o retomador. Sua missão é trocar a feature ativa por uma das que estão em `paused-features`, sem perder o trabalho de nenhuma das duas.

## Antes de começar

1. Leia `.reversa/state.json` para resolver `output_folder` e `forward_folder`
2. Use os valores reais nos lugares onde o texto mencionar `_reversa_sdd/` ou `_reversa_forward/`

## Verificações Iniciais

1. Leia `.reversa/active-requirements.json`
   1.1. Se ausente, aborte com mensagem:

       > 🛑 `/reversa-resume` exige uma feature ativa para fazer a troca. `active-requirements.json` não existe.
       >
       > Use `/reversa-requirements` para criar a primeira feature do projeto.

2. Verifique o campo `paused-features`
   2.1. Se ausente ou array vazio, aborte com mensagem:

       > 🛑 Não há features pausadas para retomar. O array `paused-features` está vazio.
       >
       > Features ficam pausadas quando você roda `/reversa-requirements` numa feature ativa em andamento e escolhe a opção 2 (criar paralela).

3. Aplique ganchos `before-resume` da forma padrão (lê `.reversa/hooks.yml`, filtra `enabled: false`, mesma lógica de outros skills do ciclo forward)

## Listagem das pausadas

Para cada entrada em `paused-features`:

1. Verifique se o `feature-dir` ainda existe em disco
   1.1. Se NÃO existir, marque como `ausente` (a pasta foi apagada manualmente, a entry virou lixo)
2. Se existir, detecte o **estágio físico atual** com a mesma lógica do `/reversa-requirements`:

   | Condição observada em `feature-dir` | Estágio físico |
   |--------------------------------------|----------------|
   | `requirements.md` ausente | `vazio` |
   | `requirements.md` presente, `roadmap.md` ausente | `requirements` |
   | `roadmap.md` presente, `actions.md` ausente | `plan` |
   | `actions.md` presente com pelo menos uma linha `\| ... \| \[ \] \|` | `coding-em-progresso` |
   | `actions.md` presente, todas as ações como `\| ... \| \[X\] \|` | `done` |

3. Para `coding-em-progresso`, conte ações `[X]` versus `[ ]`

Apresente lista numerada ao usuário:

```
Features pausadas:

1. <NNN-short-name>  ·  estágio: <físico>  ·  pausada em <YYYY-MM-DD>  [· N de M ações]
2. <NNN-short-name>  ·  estágio: <físico>  ·  pausada em <YYYY-MM-DD>
3. <NNN-short-name>  ·  estágio: ausente   ·  pausada em <YYYY-MM-DD>  (pasta apagada, entry orfã)
```

Para entries `ausente`, marque visualmente que estão órfãs.

## Escolha do usuário

Pergunte:

> Qual feature você quer retomar? Digite o número da lista, ou `0` para cancelar.

Aguarde a resposta. NÃO escolha por conta própria.

## Tratamento de entry órfã

Se o usuário escolheu uma entry com estágio `ausente`:

1. NÃO faça swap
2. Pergunte: "A pasta dessa feature foi apagada. Quer remover essa entry de `paused-features`? (sim / não)"
3. Se sim, remova só essa entry do array, escreva `active-requirements.json` atualizado (atomicamente), encerre o skill.
4. Se não, encerre sem mudar nada.

## Detecção do estado da feature atualmente ativa

Para a feature em `active-requirements.json#feature-dir`, detecte o estágio físico usando a mesma tabela acima. Esse valor decide se ela vai ser pausada ou descartada na troca.

## Swap

1. Construa a nova entrada de pausa para a feature **atualmente ativa**, copiando todos os campos do `active-requirements.json` exceto `paused-features`, e adicionando:
   - `paused-at`: ISO 8601 da hora atual
   - `paused-from-stage`: estágio físico detectado da ativa atual
2. Decida o destino da feature ativa atual:
   - 2.1. Se estágio físico for `requirements`, `plan` ou `coding-em-progresso`: **pause**, ou seja, faça push da entrada construída no array `paused-features`
   - 2.2. Se estágio físico for `done`: **descarte do active**, NÃO faça push (a feature está concluída, não vale ocupar espaço em paused-features). A pasta dela continua intocada em `_reversa_forward/`
   - 2.3. Se estágio físico for `vazio`: **descarte do active**, NÃO faça push (corrupção, pasta sem `requirements.md`)
3. Remova a feature escolhida do array `paused-features`
4. Construa o novo `active-requirements.json`:

```json
{
  "schema-version": 1,
  "feature-dir": "<feature-dir da escolhida>",
  "feature-id": "<feature-id da escolhida>",
  "short-name": "<short-name da escolhida>",
  "started-at": "<started-at original da escolhida>",
  "current-stage": "<current-stage original da escolhida, ou estágio físico detectado>",
  "stages-completed": [<copiado da escolhida, ou [] se ausente>],
  "paused-features": [<array atualizado>]
}
```

   4.1. Se a escolhida não tinha `started-at`/`current-stage`/`stages-completed` (entry de versão antiga, antes do schema rico), use o estágio físico detectado para `current-stage` e a hora atual como `started-at` (registre essa fallback em mensagem ao usuário)

5. Escreva o JSON atomicamente (tempfile mais rename)

## Ganchos Pós-execução

Aplique `after-resume` da forma padrão.

## Relatório final ao usuário

1. Feature retomada: identificador `<NNN-short-name>`
2. Estágio físico detectado dessa feature: valor entre `requirements` / `plan` / `coding-em-progresso`
3. Para `coding-em-progresso`, mostrar `N de M ações concluídas`
4. Destino da feature anteriormente ativa:
   4.1. "pausada" (se foi push pra paused-features)
   4.2. "descartada do ativo (estado: done)" ou "descartada do ativo (estado: vazio)"
5. Sugestão de próximo skill conforme o estágio da feature retomada:
   5.1. `requirements` → sugerir `/reversa-clarify` (se houver `[DÚVIDA]`) ou `/reversa-plan`
   5.2. `plan` → sugerir `/reversa-to-do`
   5.3. `coding-em-progresso` → sugerir `/reversa-coding` (com argumento opcional pra restringir escopo)

Termine sempre com:

> Digite **CONTINUAR** para prosseguir conforme a sugestão acima.

NÃO execute o próximo skill automaticamente, deixe a decisão com o usuário.
