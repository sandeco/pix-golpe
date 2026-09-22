# Relatório de Confiança — pix-golpe

> Gerado pelo Revisor (Reversa) em 2026-09-21, ao final da extração autônoma (`/reversa-autonomous`, nível completo, specs por features).
> Contagem sobre todos os marcadores 🟢/🟡/🔴 dos artefatos em `_reversa_sdd/` (exceto `questions.md` e `gaps.md`).

---

## Resumo Geral

| Nível | Quantidade | Percentual |
|-------|-----------|------------|
| 🟢 CONFIRMADO | 599 | 85,8% |
| 🟡 INFERIDO   | 75 | 10,7% |
| 🔴 LACUNA     | 24 | 3,4% |
| **Total**     | 698 | 100% |

**Confiança geral:** 91% (soma de 🟢 + metade dos 🟡). Atualizado em 2026-09-22 após as respostas do usuário: Perguntas 1 e 3 resolvidas (vale o código), Pergunta 2 sem resposta.

Os marcadores 🔴 restantes correspondem a **1 lacuna real**: a intenção por trás da medição assimétrica de latência com retry (Pergunta 2). Os demais 🔴 são as legendas de escala nos cabeçalhos das specs.

---

## Por Spec

### Units (specs por feature)

| Spec | 🟢 | 🟡 | 🔴 | Confiança |
|------|----|----|-----|-----------|
| `geracao-de-dados/requirements.md` | 16 | 4 | 2 | 82% |
| `geracao-de-dados/design.md` | 10 | 3 | 1 | 82% |
| `geracao-de-dados/tasks.md` | 9 | 1 | 1 | 86% |
| `decisao-por-ia/requirements.md` | 19 | 2 | 2 | 87% |
| `decisao-por-ia/design.md` | 8 | 2 | 1 | 82% |
| `decisao-por-ia/contracts.md` | 1 | 0 | 0 | 100% |
| `decisao-por-ia/tasks.md` | 11 | 1 | 1 | 88% |
| `rastreio-no-grafo/requirements.md` | 17 | 3 | 1 | 88% |
| `rastreio-no-grafo/design.md` | 13 | 2 | 0 | 93% |
| `rastreio-no-grafo/tasks.md` | 8 | 0 | 1 | 89% |
| `corrida-em-tempo-real/requirements.md` | 26 | 1 | 1 | 95% |
| `corrida-em-tempo-real/design.md` | 16 | 2 | 0 | 94% |
| `corrida-em-tempo-real/contracts.md` | 1 | 0 | 0 | 100% |
| `corrida-em-tempo-real/tasks.md` | 15 | 0 | 1 | 94% |
| `interface-tela-dividida/requirements.md` | 28 | 2 | 1 | 94% |
| `interface-tela-dividida/design.md` | 17 | 2 | 0 | 95% |
| `interface-tela-dividida/tasks.md` | 14 | 1 | 1 | 91% |
| `relatorio-de-acuracia/requirements.md` | 19 | 1 | 1 | 93% |
| `relatorio-de-acuracia/design.md` | 9 | 1 | 0 | 95% |
| `relatorio-de-acuracia/tasks.md` | 8 | 0 | 1 | 89% |
| `verificacao-cli/requirements.md` | 16 | 3 | 1 | 88% |
| `verificacao-cli/design.md` | 8 | 1 | 0 | 94% |
| `verificacao-cli/tasks.md` | 3 | 1 | 1 | 70% |
| `volumetria-das-bases/requirements.md` | 19 | 7 | 2 | 80% |
| `volumetria-das-bases/design.md` | 7 | 3 | 1 | 77% |
| `volumetria-das-bases/tasks.md` | 3 | 2 | 2 | 57% |

### Artefatos transversais

| Spec | 🟢 | 🟡 | 🔴 | Confiança |
|------|----|----|-----|-----------|
| `inventory.md` | 14 | 2 | 1 | 88% |
| `dependencies.md` | 3 | 3 | 0 | 75% |
| `code-analysis.md` | 23 | 6 | 2 | 84% |
| `data-dictionary.md` | 3 | 0 | 0 | 100% |
| `domain.md` | 62 | 4 | 2 | 94% |
| `state-machines.md` | 8 | 0 | 0 | 100% |
| `permissions.md` | 2 | 0 | 0 | 100% |
| `adrs/001` a `008` | 8 | 0 | 0 | 100% |
| `architecture.md` | 12 | 3 | 0 | 90% |
| `c4-context.md`, `c4-containers.md`, `c4-components.md`, `erd-complete.md` | 4 | 0 | 0 | 100% |
| `traceability/spec-impact-matrix.md` | 1 | 0 | 0 | 100% |
| `traceability/code-spec-matrix.md` | 24 | 1 | 0 | 98% |
| `openapi/pix-golpe.yaml` | (sem marcadores; derivado de `server.rs`) | | | 🟢 |
| `user-stories/*.md` | 2 | 0 | 0 | 100% |
| `design-system/*.md` | 100 | 17 | 0 | 93% |
| `flowcharts/*.md` | (diagramas, sem marcadores; derivados do código) | | | 🟢 |

---

## Lacunas Pendentes 🔴

### Latência com retry (`decisao-por-ia`, `domain` RN-07, ADR-002)
- **Rust inclui o backoff de retentativa na latência de decisão; Python exclui** — comportamento confirmado no código; o usuário não sabe se foi intencional. Recomendação: excluir o backoff nos dois lados, coerente com o SPEC ("ida e volta HTTP medida pelo próprio lado"). Só afeta corridas com 429/5xx.
  - Pergunta correspondente: `questions.md#pergunta-2` (sem resposta)

### Resolvidas em 2026-09-22
- Escala do dataset: vale o código (1 M contas, 9.968.511 transações, 2.000 hubs). SPEC, README e PDF a corrigir.
- Contas de saque com movimento de fundo: vale o código. SPEC §1 e PDF p.4 a corrigir.

---

## Recomendações

- [ ] Responder as 3 perguntas de `questions.md`; as três afetam documentação, e a Pergunta 1 pode exigir regenerar `data/` e `trace_ref.jsonl`.
- [ ] `rastreio-no-grafo` é a unit mais crítica e está 100 % confirmada no algoritmo; priorizar a automação do `fc` (TT-01) antes de qualquer mudança em `graph.rs`/`trace.py`.
- [ ] `volumetria-das-bases` tem a confiança mais baixa nas tasks (57 %) porque três tarefas dependem das perguntas; não é falta de evidência no código.
- [ ] Atualizar `SPEC.md` §4 e §5 (D-01, D-02, D-04 em `gaps.md`) e regravar `docs/tela-corrida.png` com o título atual.
- [ ] Medir a memória do lado Rust (tarefa T-03 de `volumetria-das-bases`) para fechar a inferência I-01.
- [ ] Se o projeto for versionado, adicionar `data/` e `.env` ao `.gitignore`.

---

## Histórico de Reclassificações

| De | Para | Afirmação | Evidência |
|----|------|-----------|-----------|
| 🟡 | 🟢 | `chaves.json` tem 965 pares (40 de quadrilha + 925 legítimas) | contagem direta do arquivo (`inventory.md` §6, `data-dictionary.md` §1) |
| 🟡 | 🟢 | Memória do lado Python após carga ≈ 1,67 GB; carga 4,2 s; rastreio p50 158 ms | medição com `py-worker/trace.py` via `worker.memoria_mb` (`volumetria-das-bases/requirements.md`) |
| 🟡 | 🟢 (divergência) | Contas de saque movimentam dinheiro no período (RN-55) | varredura de `transacoes.bin`: 807 transações com origem em conta de saque (`domain.md` RN-55) |
| 🟡 | 🟡 (corrigido) | Pico de memória do Rust na carga: de ≈ 470 MB para ≈ 320 MB | análise de `data.rs:104-119` + `server.rs:150-152` (`volumetria-das-bases/requirements.md`) |
| 🟢 | 🟢 (verificado) | `trace --todas` reproduz `data/trace_ref.jsonl` byte a byte | execução de `target/release/trace.exe --todas` + `cmp` |
| 🔴 | 🟢 | Escala oficial do dataset = a do código (1 M / 9.968.511 / 2.000) | resposta do usuário à Pergunta 1 (2026-09-22) |
| 🔴 | 🟢 | Contas de saque podem ter transações de fundo; SPEC §1 desatualizado | resposta do usuário à Pergunta 3 (2026-09-22) |

## Revisão Cruzada

- Engine externa consultada: nenhuma. O plugin Codex está disponível, mas no nível `completo` a revisão cruzada é opcional e exige confirmação do usuário; em modo autônomo foi omitida. Pode ser executada depois com `/reversa` → Revisor, ou diretamente com o Codex sobre `_reversa_sdd/`.
- Apontamentos recebidos: 0 | Aceitos: 0 | Rejeitados: 0 | Pendentes: 0

## Verificação de regressão semântica

Não aplicável: primeira extração, sem `_reversa_forward/` nem `_reversa_sdd/addenda/`.
