# Passo 2 — Retomada de sessão

## 0. Verificação de migração em andamento

Antes de tudo, leia `.reversa/state.json` apenas para resolver `output_folder` (padrão `_reversa_sdd`).

Verifique se `<output_folder>/migration/.state.json` existe. Se não existir, pule esta seção e siga para a seção 1.

Se existir, leia o arquivo e classifique o estado da migração:

| Condição | Estado |
|----------|--------|
| `pendingAgents.length > 0` ou `currentAgent.agent` diferente de `null` | em andamento |
| `currentAgent.status == "awaiting_user_approval"` | pausa intra-agente pendente |
| `pendingAgents.length == 0`, `currentAgent.agent == null` e `<output_folder>/migration/handoff.md` existe | concluída |

Se o estado for **concluída**, pule esta seção (a migração já terminou, nada a perguntar) e siga para a seção 1.

Se o estado for **em andamento** ou **pausa intra-agente pendente**, apresente a pergunta ao usuário antes de qualquer outra coisa:

> "[Nome], encontrei uma **migração em andamento** em `<output_folder>/migration/`.
>
> - Concluído: <N> de 6 agentes (<lista de completedAgents>)
> - Pendente: <lista de pendingAgents>
> - Estado atual: <currentAgent.agent ou \"aguardando aprovação humana\">
>
> Como prefere continuar:
>
> 1. **Retomar a migração**: volta ao Time de Migração de onde parou
> 2. **Retomar o fluxo do Reversa**: segue descoberta/forward, ignora migração por agora
> 3. **Cancelar**: encerra esta sessão sem mudar nada
> 4. **Outro**: descreva o que prefere fazer
>
> Use o mecanismo de menu interativo da engine (no Claude Code, `AskUserQuestion`); em engines sem suporte a menu, peça que o usuário digite o número 1–4 ou texto livre."

Aguarde a resposta. NÃO escolha por conta própria.

- Se **1**: encerre o `/reversa` aqui com a instrução final:
  > "Para retomar a migração, digite `/reversa-migrate`. Ele detecta o estado salvo e oferece as opções de retomada."
  
  NÃO ative `reversa-migrate` automaticamente, deixe o usuário digitar (padrão de handoff explícito do Reversa).
- Se **2**: prossiga com a seção 1 deste passo normalmente.
- Se **3**: encerre sem fazer nada.
- Se **4** (texto livre): interprete a intenção do usuário e ofereça a melhor rota possível, sem inventar fluxos novos. Se a intenção for ambígua, refaça a pergunta uma vez antes de decidir.

## 1. Leitura do estado

Leia `.reversa/state.json` e `.reversa/plan.md`.

## 2. Verificação de versão

Compare `.reversa/version` com o npm registry. Se houver versão mais nova, informe discretamente:
> "💡 Nova versão disponível. Execute `npx reversa update` quando quiser atualizar."

## 3. Saudação

Diga: "[Nome], bem-vindo de volta ao Reversa! 🎼"

## 4. Resumo de progresso

Mostre:
- ✅ Fases concluídas (campo `completed` do state.json)
- 🔄 Fase atual (campo `phase`) com a última tarefa registrada em `checkpoints`
- ⏳ Próximas fases (campo `pending`)

Exemplo:
> "Progresso atual:
> ✅ Reconhecimento concluído
> 🔄 Escavação em andamento — módulos `auth` e `orders` analisados, `payments` e `users` pendentes
> ⏳ Interpretação, Geração, Revisão"

## 5. Modo de resposta a lacunas

Se `answer_mode` for `"file"`:
> "Lembre-se: suas respostas às perguntas devem ser preenchidas em `_reversa_sdd/questions.md`. Me avise quando terminar."

Se `answer_mode` for `"chat"` (padrão):
> Continue normalmente — farei as perguntas aqui no chat.

## 6. Confirmação

Pergunte apenas: "Continuamos de onde paramos? (CONTINUAR para seguir)"

Após confirmação, retome a próxima tarefa pendente no plano (`.reversa/plan.md`).

**🚫 Não ofereça `/clear` + `/reversa` neste momento.** O usuário acabou de retomar a sessão; pedir para limpar e reabrir agora é redundante. O prompt de pausa entre etapas (descrito em `SKILL.md`, seção "Checkpoint preventivo entre etapas") só vale **depois** que um agente concluir trabalho dentro desta sessão, nunca na própria saudação de retomada.

Consulte `references/checkpoint-guide.md` para as regras de escrita no state.json.
