# Reconstruction Plan — {{PROJECT_NAME}}

**Fonte:** migração
**Paradigma alvo:** {{PARADIGM}}
**Topologia:** {{TOPOLOGY}}
**Stack:** {{STACK}}
**Estratégia:** {{STRATEGY}}
**Gerado em:** {{DATE}}
**Status:** {{TOTAL}} tarefas | {{DONE}} concluídas | {{PENDING}} pendentes

---

## Alertas de pré-voo

> Revise antes de iniciar. Itens REFERIDOS À CODIFICAÇÃO em `ambiguity_log.md` que afetam tarefas específicas estão marcados.

{{#each PREFLIGHT_ALERTS}}
- ⚠️ **{{this.item}}** — afeta Tarefa {{this.task_number}} ({{this.task_name}}). Origem: `_reversa_sdd/migration/ambiguity_log.md`
{{/each}}

{{#if NO_ALERTS}}
Nenhum item bloqueante. Pode iniciar.
{{/if}}

---

## Tarefas

### Tarefa 01 — Setup do Projeto Novo
**Status:** pending
**Lê:** `_reversa_sdd/migration/topology_decision.md`, `_reversa_sdd/migration/paradigm_decision.md`
**Constrói:** estrutura inicial de pastas/módulos, configuração base, dependências mínimas
**Pronto quando:** Esqueleto do repositório novo bate com a topologia aprovada e o paradigma escolhido

---

### Tarefa 02 — Schema do Banco Alvo
**Status:** pending
**Lê:** `_reversa_sdd/migration/target_data_model.md`
**Constrói:** migrations, schema, modelos ORM (conforme stack)
**Pronto quando:** Todas as tabelas/coleções do modelo de dados alvo existem com tipos, constraints e relações corretos

---

### Tarefa 03 — Plano de Migração de Dados
**Status:** pending
**Lê:** `_reversa_sdd/migration/data_migration_plan.md`, `_reversa_sdd/migration/target_data_model.md`
**Constrói:** scripts/jobs de ETL, validações de integridade, rollback
**Pronto quando:** Scripts de migração testados em volume representativo, validações batem com o plano
**Obs:** Pular se a estratégia em `migration_strategy.md` não envolver migração de dados (ex: sistema novo do zero sem dados legados)

---

### Tarefa 04 — Entidades de Domínio Alvo
**Status:** pending
**Lê:** `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** entidades, value objects, agregados, regras de negócio
**Pronto quando:** Domínio implementado conforme o modelo alvo, regras de negócio cobertas por testes

---

<!-- MODULE_TASKS_START -->
<!-- O Reconstructor insere aqui uma tarefa por módulo identificado em target_architecture.md, na ordem de dependência. -->
<!-- Exemplo: -->

### Tarefa 05 — [Nome do Módulo]
**Status:** pending
**Lê:** `_reversa_sdd/migration/target_architecture.md` (seção `[módulo]`), `_reversa_sdd/migration/target_domain_model.md`, `_reversa_sdd/migration/target_business_rules.md`
**Constrói:** [caminho do módulo conforme topologia aprovada]
**Pronto quando:** [critério de paridade extraído de parity_specs.md, se aplicável; senão, critério em target_architecture.md]
**Alerta:** [se houver item REFERIDO À CODIFICAÇÃO associado]

<!-- MODULE_TASKS_END -->

---

### Tarefa {{CUTOVER_N}} — Cutover
**Status:** pending
**Lê:** `_reversa_sdd/migration/cutover_plan.md`
**Constrói:** scripts/checklists de cutover, switch de tráfego, plano de rollback executável
**Pronto quando:** Sistema novo recebe tráfego conforme o plano e legado pode ser desligado/congelado conforme decidido

---

### Tarefa {{PARITY_N}} — Validação de Paridade
**Status:** pending
**Lê:** `_reversa_sdd/migration/parity_specs.md`, `_reversa_sdd/migration/parity_tests/[lista de arquivos .feature]`
**Constrói:** suíte de testes de paridade rodando contra legado e novo, relatório de divergências
**Pronto quando:** Todos os fluxos críticos definidos em parity_specs.md passam nos dois sistemas com resultados equivalentes
