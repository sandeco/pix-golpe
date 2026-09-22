# Perguntas para Validação — pix-golpe

> Gerado pelo Revisor (Reversa) em 2026-09-21, modo autônomo (`answer_mode = file`).
> Responda o campo **Resposta** de cada pergunta e me avise (digite `reversa`). As specs afetadas serão atualizadas e reclassificadas.

---

## Pergunta 1

**Contexto:** Gerador de dados, constantes em `src/bin/gerar_dados.rs:11-14` (`N_CONTAS = 1_000_000`, `N_HUBS = 2_000`, `N_TX_NORMAIS = 9_500_000`) e arquivos em `data/` (1.000.000 contas, 9.968.511 transações). `SPEC.md` §1, `README.md` e o PDF `output/pdf/pix-golpe-explicacao.pdf` (p.3-4) descrevem 100.000 contas, ~1,27 a 1,3 milhão de transações e 200 hubs.
**Spec afetada:** `_reversa_sdd/volumetria-das-bases/requirements.md`, `_reversa_sdd/geracao-de-dados/requirements.md`, `_reversa_sdd/domain.md` (RN-51), `_reversa_sdd/inventory.md`
✅ Respondida em 2026-09-22

**Pergunta:** Qual escala é a oficial do vídeo: a do código (1 M contas / ~10 M transações / 2.000 hubs) ou a dos documentos (100 k / ~1,3 M / 200)? Os documentos devem ser atualizados para a escala do código?
**Impacto:** Se a escala oficial for a do código, SPEC, README e PDF precisam de correção (tarefa T-04 de `volumetria-das-bases/tasks.md`). Se for a dos documentos, as constantes voltam a 100 k, `data/` e `trace_ref.jsonl` são regenerados, e as tabelas de volumetria e de memória (Python 1,67 GB) mudam de ordem de grandeza.

**Resposta:** 10 milhões de transações e 1 milhão de contas, como está na base de dados. SPEC, README e PDF estão desatualizados.

---

## Pergunta 2

**Contexto:** Medição da latência de decisão. Lado Rust: `src/bin/server.rs:338-340` cronometra `classificar()` inteiro, que inclui os sleeps de retentativa em 429/529 (`src/jev.rs:139-143`). Lado Python: `py-worker/deepseek.py:145-152` cronometra só a tentativa HTTP bem-sucedida e exclui o backoff (comentário "espera de backoff nao e latencia HTTP").
**Spec afetada:** `_reversa_sdd/decisao-por-ia/requirements.md` (RN-07), `_reversa_sdd/decisao-por-ia/design.md`, `_reversa_sdd/domain.md` (RN-07), `_reversa_sdd/adrs/002-comparacao-justa.md`
⏳ Sem resposta (usuário: "não tenho ideia"). Mantida como 🔴; recomendação em `confidence-report.md`.

**Pergunta:** Essa assimetria é intencional? Qual comportamento deve valer para os dois lados: incluir o backoff (latência "vista pelo usuário") ou excluir (latência "da API")?
**Impacto:** Define se `decision_p50_ms`/`p95` são comparáveis quando há 429/5xx. Se for para igualar, uma das duas implementações muda (tarefa a acrescentar em `decisao-por-ia/tasks.md`). Se for intencional, a regra de justiça (ADR-002) ganha uma nota explícita.

**Resposta:** Não tenho ideia.

---

## Pergunta 3

**Contexto:** `SPEC.md` §1 afirma que "as contas de saque não movimentam nada nas 24 h seguintes (saque em espécie)". O gerador (`src/bin/gerar_dados.rs:141,147-161`) sorteia contas de fundo em todo o intervalo `[2000, 1_000_000)`, sem excluir as contas reservadas das quadrilhas. Medido no dataset: 807 transações de fundo **saem** de contas de saque e 426 chegam a elas além das do esquema.
**Spec afetada:** `_reversa_sdd/geracao-de-dados/requirements.md` (RN-55), `_reversa_sdd/domain.md` (RN-55), `_reversa_sdd/volumetria-das-bases/tasks.md` (T-05)
✅ Respondida em 2026-09-22

**Pergunta:** O comportamento desejado é o do SPEC (contas de saque silenciosas, o que exigiria excluir contas reservadas do sorteio de fundo) ou o do código (contas de saque podem ter movimento de fundo, o que torna a classificação `repasse < 0,3` um pouco mais difícil e realista)?
**Impacto:** Se for o SPEC, o gerador muda e o dataset/`trace_ref.jsonl` são regenerados. Se for o código, o SPEC §1 e o PDF p.4 são corrigidos.

**Resposta:** O que vale é o que está na programação e nos dados. Specs e PDF devem estar desatualizados.
