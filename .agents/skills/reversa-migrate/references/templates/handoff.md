---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: handoff
producedBy: orchestrator
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Handoff para o Agente de Codificação

> Este documento é a porta de entrada para o agente de codificação (Claude Code, Codex, Cursor, Antigravity, etc.) que vai escrever o sistema novo a partir das specs.

## ⚠️ Leitura obrigatória primeiro

1. **`paradigm_decision.md`**, leitura inegociável. O paradigma alvo molda como toda a codificação deve acontecer.
2. **`topology_decision.md`**, leitura inegociável. A topologia escolhida (preservar / modernizar / híbrido) define a árvore de pastas e a fronteira entre módulos.
3. **`screen_modernization_decision.md`**, leitura inegociável quando o legado tem UI. O modo escolhido (literal / modernizado / híbrido) define como o codificador vai materializar as telas.

## Ordem de leitura recomendada

1. `paradigm_decision.md` (obrigatório, primeiro)
2. `topology_decision.md` (obrigatório, segundo)
3. `screen_modernization_decision.md` (obrigatório quando há UI; pular se Screen Translator rodou em modo skipped)
4. `migration_brief.md`
5. `target_business_rules.md`
6. `migration_strategy.md`
7. `target_architecture.md`
8. `target_domain_model.md`
9. `target_data_model.md`
10. `data_migration_plan.md`
11. `target_screens.md` (quando há UI)
12. `parity_specs.md` + `parity_tests/`
13. `screen_deviation_log.md` (consultivo, quando há UI)
14. `risk_register.md` + `cutover_plan.md`
15. `discard_log.md` (consultivo)
16. `ambiguity_log.md` (consultivo)

## Lista de artefatos produzidos

| Artefato | Produzido por | Status |
|---|---|---|
| migration_brief.md | orchestrator | criado |
| paradigm_decision.md | paradigm_advisor | criado |
| target_business_rules.md | curator | criado |
| discard_log.md | curator | criado |
| migration_strategy.md | strategist | criado |
| risk_register.md | strategist | criado |
| cutover_plan.md | strategist | criado |
| topology_decision.md | designer (Fase 1) | criado |
| target_architecture.md | designer | criado |
| target_domain_model.md | designer | criado |
| target_data_model.md | designer | criado |
| data_migration_plan.md | designer | criado |
| screen_modernization_decision.md | screen_translator (Fase 1) | criado / skipped |
| target_screens.md | screen_translator | criado / skipped |
| screen_deviation_log.md | screen_translator | criado / vazio |
| _reversa_sdd/screens/inventory.json | screen_translator | criado / vazio |
| _reversa_sdd/screens/golden/manifest.yaml | screen_translator | criado / opcional |
| parity_specs.md | inspector | criado |
| parity_tests/*.feature | inspector | <N> arquivos |
| ambiguity_log.md | orchestrator | consolidado |

## Bloqueadores para começar a implementação
> Itens que precisam de decisão humana antes do agente de codificação começar.

- <AMB-XXX: descrição curta + onde decidir>
- <ou: nenhum bloqueador, prosseguir>

## Próximos passos para o agente de codificação

1. **Ler `paradigm_decision.md` e internalizar**: o paradigma alvo é <do paradigm_decision>. Toda escolha de código deve honrar esse paradigma.
2. **Ler `topology_decision.md` e internalizar**: a topologia escolhida é <preservar | modernizar | híbrido>. Use o esboço da árvore registrado nesse artefato como base para criar a estrutura de pastas do novo repositório.
3. **Ler `screen_modernization_decision.md` e internalizar** (quando há UI): o modo de tradução de telas é <literal | modernizado | híbrido>. Em literal, materialize byte-a-byte (ou pixel-equivalente) o que está em `target_screens.md`; em modernizado, honre a hierarquia de componentes, tokens e os 4 estados (idle, loading, error, success).
4. **Configurar o repositório novo** com a stack declarada em `migration_brief.md` e a topologia decidida.
5. **Implementar bottom-up** seguindo `target_architecture.md` e `target_domain_model.md`:
   - infraestrutura → dados → domínio → aplicação → bordas.
6. **Implementar as telas** consumindo `target_screens.md` como contrato literal. Em modo literal com golden files presentes em `_reversa_sdd/screens/golden/`, o resultado da implementação deve casar com o golden file dentro das `normalizationRules` declaradas no `manifest.yaml`.
7. **Escrever os testes** a partir de `parity_specs.md` e `parity_tests/*.feature` desde o início. Honrar a seção § Exceções, que reflete deviations aprovadas em `screen_deviation_log.md`.
8. **Para cada componente**, validar que respeita o paradigma escolhido (sinais explícitos em `target_architecture.md § Honra ao paradigma escolhido`) e a topologia escolhida (sinais explícitos em `target_architecture.md § Honra à topologia escolhida`).
9. **Para a migração de dados**, seguir `data_migration_plan.md`.
10. **Para o cutover**, seguir `cutover_plan.md` e os critérios go/no-go.

## Itens auto-decididos (apenas se executado em --auto)
> Listar aqui itens cujo default foi aplicado sem confirmação humana. Recomenda-se revisar antes do cutover.

- <ou: pipeline executado em modo interativo, nenhum item auto-decidido>

## Notas finais
<Observações do orquestrador para o agente de codificação.>
