# Verificação por CLI, Tarefas de Implementação

> Unit `verificacao-cli`. Reimplementação a partir de `src/bin/trace.rs`, `py-worker/trace.py` e `py-worker/deepseek.py`.

## Pré-requisitos
- [ ] Units `rastreio-no-grafo` e `geracao-de-dados`
- [ ] `data/trace_ref.jsonl` existente (ou regenerado pelo Rust após T-01)

## Tarefas

- [ ] T-01, `trace` (Rust): argumentos, carga, alvos, regra de `t0`, saída JSON e diagnóstico com acertos
  - Origem no legado: `src/bin/trace.rs:8-42`
  - Critério de pronto: `--todas` reproduz `trace_ref.jsonl`
  - Confiança: 🟢

- [ ] T-02, `trace.py` (Python): argparse exclusivo, UTF-8, `primeiros`, saída compacta, `del result`
  - Origem no legado: `py-worker/trace.py:234-275`
  - Critério de pronto: `fc` sem diferenças contra o Rust
  - Confiança: 🟢

- [ ] T-03, `deepseek.py` CLI
  - Origem no legado: `py-worker/deepseek.py:162-186`
  - Critério de pronto: imprime JSON com `verdict` e `cost_usd`; sem texto usa o primeiro golpe
  - Confiança: 🟢

- [ ] T-04, Script de conferência (novo, opcional): roda os dois `--todas` e compara, com código de saída
  - Origem no legado: README "Conferir a igualdade dos algoritmos"
  - Critério de pronto: um comando falha se houver divergência
  - Confiança: 🟡 (não existe no legado)

## Tarefas de Teste

- [ ] TT-01, Igualdade nas 40 chaves (o próprio `fc`)
- [ ] TT-02, Chave desconhecida e argumentos inválidos nos dois CLIs
- [ ] TT-03, `t0` para chave com mensagem, sem mensagem mas com quadrilha, e sem ambos

## Ordem Sugerida
1. T-01 → gerar `trace_ref.jsonl` → T-02 → TT-01 → T-03 → T-04.

## Lacunas Pendentes (🔴)
Nenhuma.
