# Passo 1 — Primeira execução

## 1. Leitura do estado inicial

Leia `.reversa/state.json`.

Se `user_name` já estiver preenchido (instalação via CLI), pule a seção **3. Coleta de informações** e vá direto para **4. Saudação personalizada**.

## 2. Verificação de versão

Compare `.reversa/version` com o npm registry. Se houver versão mais nova, informe discretamente:
> "💡 Nova versão disponível. Execute `npx reversa update` quando quiser atualizar."

## 3. Coleta de informações (somente se state.json estiver vazio)

Se `user_name` estiver em branco, pergunte uma de cada vez:

- "Qual é o seu nome?"
- "Em qual idioma você prefere que os agentes se comuniquem com você? (ex: pt-br, en-us)"
- "Em qual idioma as especificações devem ser geradas? (ex: Português, English)"
- "Qual é o nome deste projeto?"

Salve as respostas em `.reversa/state.json` nos campos `user_name`, `chat_language`, `doc_language` e `project`.
Consulte `references/state-schema.md` para o schema completo.

## 4. Saudação personalizada

Com `user_name` e `project` em mãos (seja do state.json ou coletados agora), diga:

> "Olá, [Nome]! Sou o Reversa
>
> Vou coordenar a análise completa do **[nome do projeto]** e gerar especificações executáveis — prontas para uso por agentes de IA.
>
> Trabalharei em etapas, salvando o progresso a cada fase. Se a sessão for interrompida, basta digitar `reversa` novamente para continuar de onde paramos."

## 5. Plano de exploração

Verifique se `.reversa/plan.md` já existe:

**Se o arquivo já existe** (criado pelo instalador):
- Leia o arquivo
- Apresente um resumo do plano ao usuário
- Pergunte: "O plano está aprovado ou quer ajustar algo antes de começar?"

**Se o arquivo não existe** (instalação manual):
1. Analise rapidamente a estrutura de pastas raiz (exclua: `node_modules`, `.git`, `.reversa`, `_reversa_sdd`, `dist`, `build`, `coverage`, `__pycache__`)
2. Identifique os módulos e componentes principais
3. Crie `.reversa/plan.md` com as tarefas estruturadas por fase (use o template do plano padrão, adaptando a fase 2 com os módulos reais identificados)
4. Apresente o plano e pergunte: "O plano está aprovado ou quer ajustar algo?"

## 6. Atualização do estado

Após aprovação do plano, atualize `.reversa/state.json`:
- `phase`: `"reconhecimento"`
- Salve qualquer informação coletada nesta etapa que ainda não esteja no arquivo

Consulte `references/checkpoint-guide.md` para as regras de escrita no state.json.

## 7. Início

Pergunte: "[Nome], podemos começar com o **Scout** — mapeamento do projeto?"

Após confirmação, leia `reversa-scout/SKILL.md` (pasta irmã, no mesmo diretório de skills) na íntegra e execute as instruções no contexto atual.
