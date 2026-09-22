# [Nome da Unit], Tarefas de Implementação

> Template do arquivo `tasks.md`. Foca em uma sequência de tarefas executáveis para reimplementar a unit a partir do legado, com rastreabilidade ao código original.

## Pré-requisitos
- [ ] Dependências da unit listadas em `design.md` estão disponíveis
- [ ] Schema/migrations do banco compatíveis (se aplicável)
- [ ] Variáveis de ambiente / configs necessárias documentadas

## Tarefas

> Cada tarefa referencia o arquivo do legado de onde o comportamento foi extraído.

- [ ] T-01, [Descrição da tarefa]
  - Origem no legado: `caminho/arquivo.ext:linha`
  - Critério de pronto: [como validar]
  - Confiança: 🟢 / 🟡 / 🔴

- [ ] T-02, [Descrição da tarefa]
  - Origem no legado: `caminho/arquivo.ext:linha`
  - Critério de pronto: [como validar]
  - Confiança: 🟢 / 🟡 / 🔴

## Tarefas de Teste

- [ ] TT-01, Teste do happy path do fluxo principal (ver `requirements.md`, Critérios de Aceitação)
- [ ] TT-02, Teste do caso de erro principal
- [ ] TT-03, [Outros cenários relevantes]

## Tarefas de Migração de Dados (se aplicável)

- [ ] TM-01, [Migração de dados X, com referência ao schema legado]

## Ordem Sugerida
1. [Quais tarefas devem ser feitas primeiro e por quê]
2. [Bloqueios entre tarefas]

## Lacunas Pendentes (🔴)
[Liste aqui as decisões que dependem de validação humana antes da implementação]
