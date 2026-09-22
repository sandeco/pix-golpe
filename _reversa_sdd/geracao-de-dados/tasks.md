# Geração de dados, Tarefas de Implementação

> Unit `geracao-de-dados`. Reimplementação fiel a partir de `src/bin/gerar_dados.rs` e `src/data.rs`.

## Pré-requisitos
- [ ] Formatos de `data/` definidos conforme `data-dictionary.md` §1 (unit `volumetria-das-bases` descreve os volumes)
- [ ] RNG determinístico equivalente a `ChaCha8Rng` seed 42 e distribuições `LogNormal` idênticas (se a reprodução byte a byte for requisito; senão, aceitar dataset diferente e regenerar `trace_ref.jsonl`)

## Tarefas

- [ ] T-01, Implementar escrita dos 4 formatos (`PIX1`, JSONL, JSON ordenado, JSON pretty)
  - Origem no legado: `src/data.rs:72-100,122-134`
  - Critério de pronto: `read_transacoes` do legado lê o arquivo gerado sem erro
  - Confiança: 🟢

- [ ] T-02, Gerar transações normais com hubs ponderados e horário comercial
  - Origem no legado: `src/bin/gerar_dados.rs:129-161`
  - Critério de pronto: 9.500.000 registros; ~50 % com destino < 2000; valores em [500, 500000]
  - Confiança: 🟢

- [ ] T-03, Gerar lotes diários dos hubs
  - Origem no legado: `src/bin/gerar_dados.rs:164-173`
  - Critério de pronto: hub 0 tem 1.510 saídas/dia entre 9h e 11h30; valores em [2000, 2000000]
  - Confiança: 🟢

- [ ] T-04, Plantar 40 quadrilhas com contas reservadas e cronologia RN-52
  - Origem no legado: `src/bin/gerar_dados.rs:176-220`
  - Critério de pronto: `meta.json` com 40 quadrilhas; rastreio de referência encontra laranjas e saques
  - Confiança: 🟢

- [ ] T-05, Ordenar transações por ts e gravar
  - Origem no legado: `src/bin/gerar_dados.rs:222,261`
  - Critério de pronto: `trace.py Graph.load` não acusa "fora da ordem"
  - Confiança: 🟢

- [ ] T-06, Gerar 75 mensagens de golpe com 30 templates e remetentes desconhecidos
  - Origem no legado: `src/bin/gerar_dados.rs:19-50,226-238`
  - Critério de pronto: cada golpe tem chave de quadrilha e `ts < inicio_ts`
  - Confiança: 🟢

- [ ] T-07, Gerar 925 mensagens legítimas com 20 templates e remetentes coerentes
  - Origem no legado: `src/bin/gerar_dados.rs:53-74,240-252`
  - Critério de pronto: loja/banco no texto e no remetente coincidem; chaves inéditas mapeadas
  - Confiança: 🟢

- [ ] T-08, Embaralhar, enumerar ids e gravar `mensagens.jsonl`, `chaves.json`, `meta.json`
  - Origem no legado: `src/bin/gerar_dados.rs:253-264`
  - Critério de pronto: 1.000 linhas, ids 0..999, 75 `golpe_real`
  - Confiança: 🟢

- [ ] T-09, Imprimir resumo final
  - Origem no legado: `src/bin/gerar_dados.rs:265-272`
  - Critério de pronto: linha em stdout com os 4 números
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Duas execuções produzem arquivos idênticos (hash)
- [ ] TT-02, Invariantes do binário: tamanho `12 + 16·n`, ts monotônico, ids < n_contas
- [ ] TT-03, Toda `mensagem.chave` existe em `chaves.json`; toda chave de quadrilha existe
- [ ] TT-04, `trace --todas` encontra ≥ 1 laranja em cada quadrilha (sanidade do padrão plantado) 🟡

## Tarefas de Migração de Dados
Não se aplica; o dataset é regenerável.

## Ordem Sugerida
1. T-01 (formatos) → T-02/T-03/T-04 (conteúdo) → T-05 (ordenação e escrita) → T-06/T-07/T-08 (mensagens) → T-09.
2. TT-02 e TT-03 logo após T-08; TT-04 depende da unit `rastreio-no-grafo`.

## Lacunas Pendentes (🔴)
Nenhuma; escala oficial confirmada em 2026-09-22 (1 M contas, 9,5 M transações de fundo, 2.000 hubs).
