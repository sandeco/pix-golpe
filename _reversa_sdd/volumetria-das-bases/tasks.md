# Volumetria das bases de dados, Tarefas

> Unit `volumetria-das-bases`. Tarefas para tornar os volumes verificáveis e alinhar a documentação.

## Pré-requisitos
- [x] Resposta a Q-001: escala do código confirmada (2026-09-22)
- [ ] `data/` gerado

## Tarefas

- [ ] T-01, Script de verificação de invariantes (tamanho do binário, ordem de `ts`, faixas, contagens de entidades, chaves, quadrilhas)
  - Origem no legado: regras de `requirements.md`; leitura em `src/data.rs:103-119`, `py-worker/trace.py:94-119`
  - Critério de pronto: retorna 0 com o `data/` atual e 1 ao alterar 1 byte do binário
  - Confiança: 🟢

- [ ] T-02, Registrar a composição das transações (fundo, lotes de hubs, quadrilhas) como saída do gerador ou do script
  - Origem no legado: contagens medidas (466.110 lotes; 807 saídas de contas de saque)
  - Critério de pronto: números reproduzidos
  - Confiança: 🟢

- [ ] T-03, Medir memória do lado Rust sem subir o servidor (ex.: `memory_stats` no `trace.rs` ou flag)
  - Origem no legado: `src/bin/server.rs:155`
  - Critério de pronto: valor impresso em stderr pelo CLI
  - Confiança: 🟡 (novo)

- [ ] T-04, Alinhar `SPEC.md` §1, `README.md` e o PDF à escala vigente (1 M contas, 9.968.511 transações, 2.000 hubs)
  - Origem no legado: divergência L1
  - Critério de pronto: os três documentos citam os mesmos números do `meta.json`
  - Confiança: 🟢 decisão tomada pelo usuário

- [ ] T-05, Corrigir SPEC §1 e PDF p.4 sobre contas de saque (RN-55): o comportamento válido é o do código, o fundo pode tocá-las
  - Origem no legado: `src/bin/gerar_dados.rs:141,147-161`; medição: 807 transações de fundo saem de contas de saque
  - Critério de pronto: SPEC e PDF descrevem o comportamento do código
  - Confiança: 🟢 decisão tomada pelo usuário

- [ ] T-06, Adicionar `data/` e `.env` a um `.gitignore` quando o projeto for versionado
  - Origem no legado: SPEC "data/ (gerado, não versionar)"
  - Critério de pronto: arquivo existe
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Executar T-01 após cada regeneração
- [ ] TT-02, `fc` de `trace_ref.jsonl` contra saída atual do Rust e do Python
- [ ] TT-03, Verificar `status.nodes/edges` dos dois lados contra `meta.json`

## Ordem Sugerida
1. T-01 → T-02 → TT-01/TT-02 → T-03 → T-04/T-05 → T-06.

## Lacunas Pendentes (🔴)
Nenhuma; Q-001 e Q-003 respondidas em 2026-09-22.
