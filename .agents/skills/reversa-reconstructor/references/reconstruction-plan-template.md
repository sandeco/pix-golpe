# Reconstruction Plan — {{PROJECT_NAME}}

**Stack:** {{STACK}}
**Gerado em:** {{DATE}}
**Status:** {{TOTAL}} tarefas | {{DONE}} concluídas | {{PENDING}} pendentes

---

## Alertas de pré-voo

> Revise estes pontos antes de iniciar. Gaps marcados com ⚠️ bloqueiam a tarefa associada.

{{#each PREFLIGHT_ALERTS}}
- ⚠️ **{{this.gap}}** — bloqueia Tarefa {{this.task_number}} ({{this.task_name}})
{{/each}}

{{#if NO_ALERTS}}
Nenhum gap crítico identificado. Pode iniciar com segurança.
{{/if}}

---

## Tarefas

### Tarefa 01 — Schema do Banco de Dados
**Status:** pending
**Lê:** `_reversa_sdd/erd-complete.md`, `_reversa_sdd/data-dictionary.md`
**Constrói:** migrations, schema, modelos ORM (conforme stack detectada)
**Pronto quando:** Todas as tabelas do ERD existem com tipos, constraints e foreign keys corretos

---

### Tarefa 02 — Entidades de Domínio
**Status:** pending
**Lê:** `_reversa_sdd/domain.md`, `_reversa_sdd/data-dictionary.md`
**Constrói:** entidades, value objects, validações de domínio
**Pronto quando:** Todas as entidades implementadas com as regras de negócio descritas

---

### Tarefa 03 — Máquinas de Estado
**Status:** pending
**Lê:** `_reversa_sdd/state-machines.md`
**Constrói:** implementação dos fluxos de estado de cada entidade
**Pronto quando:** Todos os estados e transições documentados estão implementados
**Obs:** Pular esta tarefa se `_reversa_sdd/state-machines.md` não existir

---

<!-- COMPONENT_TASKS_START -->
<!-- O Reconstructor insere aqui uma tarefa por unit, na ordem bottom-up determinada pelo dependencies.md -->
<!-- Exemplo de tarefa de unit: -->

### Tarefa 04 — [Nome da Unit]
**Status:** pending
**Lê:** `_reversa_sdd/[unit]/requirements.md`, `_reversa_sdd/[unit]/design.md`, `_reversa_sdd/[unit]/tasks.md`, `_reversa_sdd/dependencies.md`
**Constrói:** [caminho do módulo conforme stack]
**Pronto quando:** [critério de aceitação extraído de requirements.md, campo "Dado/Quando/Então"]
**Alerta:** [se houver gap associado, descreva aqui]

<!-- COMPONENT_TASKS_END -->

---

### Tarefa {{API_N}} — Camada de API
**Status:** pending
**Lê:** `_reversa_sdd/openapi/[lista de arquivos]`
**Constrói:** endpoints, controllers, middlewares, autenticação
**Pronto quando:** Todos os endpoints respondem conforme os contratos OpenAPI

---

### Tarefa {{STORIES_N}} — Fluxos de Usuário
**Status:** pending
**Lê:** `_reversa_sdd/user-stories/[lista de arquivos]`
**Constrói:** integração end-to-end, fluxos completos de usuário
**Pronto quando:** Todos os critérios de aceitação das user stories estão satisfeitos
