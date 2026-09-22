# Verificação por CLI, Design Técnico

> Unit `verificacao-cli`. Fonte: `src/bin/trace.rs`, `py-worker/trace.py` (main), `py-worker/deepseek.py` (main). 🟢

## Interface

| Comando | Argumentos | stdout | stderr | Código de saída |
|---|---|---|---|---|
| `cargo run --release --bin trace -- [chave \| --todas]` | opcional; ausente = `--todas` | 1 linha JSON por chave (`TraceResumo`) | `grafo: N contas, M transações, carga X ms`; por chave `  <chave>: N nós, M arestas, laranjas L (acertou a/r), saque S, X.X ms` | 0; erro `anyhow` → 1 |
| `python py-worker/trace.py (chave \| --todas)` | exatamente um | 1 linha JSON compacta por chave | `grafo: ... carga X.XXX ms`; por chave `  <chave>: N nos, M arestas, X.XXX ms` | 0; `parser.error` → 2 |
| `python py-worker/deepseek.py [texto] [--remetente R]` | opcionais | JSON da decisão + `verdict` + `cost_usd` | erro | 0; `ValueError`/`HTTPError` → 1 |

Resumo JSON (ordem de campos): `chave, no, t0, visitados, arestas_sub, laranjas, saque, soma_suspeita`. Python usa `separators=(",", ":")` e `ensure_ascii=False`; Rust usa `serde_json::to_string` (compacto). 🟢

## Fluxo Principal (`trace`)
1. Resolve `data_dir()`; lê `transacoes.bin`; `Graph::from_txs`; descarta `txs`; imprime carga.
2. Lê `chaves.json`, `meta.json`, `mensagens.jsonl`.
3. Alvos: 40 chaves de `meta.quadrilhas` ou a chave dada.
4. Para cada: `no = chaves[chave]` (erro se ausente); `t0` por regra; `graph.trace(no, t0)` cronometrado; `println!(resumo)`; `eprintln!` com acertos de laranjas comparando com a quadrilha.

## Fluxo Principal (`trace.py`)
1. Reconfigura stdout/stderr para UTF-8; `argparse` com `chave` opcional e `--todas`; valida exclusividade.
2. `Graph.load(DEFAULT_DATA_DIR)` (pasta `data/` irmã de `py-worker/`), imprime carga.
3. Lê `chaves.json`, `meta.json`; `primeiros[chave] = ts` da primeira mensagem por chave.
4. Alvos e loop como no Rust; `del result` após imprimir.

## Fluxo Principal (`deepseek.py`)
1. `argparse` (`texto`, `--remetente` default "teste").
2. Sem texto: abre `data/mensagens.jsonl`, pega a primeira com `golpe_real`, usa `remetente` e `texto`.
3. `DeepSeekClient().classificar` → adiciona `verdict` e `cost_usd` → `print(json.dumps(..., ensure_ascii=False))`.

## Fluxos Alternativos
- Rust: `data_dir()` cai para `<crate>/data` se `./data/meta.json` não existe.
- Python: `DEFAULT_DATA_DIR` fixo relativo ao arquivo (não usa cwd).
- Chave sem mensagem e sem quadrilha: `t0 = 0` (rastreio a partir do início da simulação).

## Dependências
- Units `rastreio-no-grafo`, `geracao-de-dados`, `decisao-por-ia`.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Comparação por arquivos e `fc`, sem framework de teste | README | 🟢 |
| stdout limpo (só JSON) para redirecionamento | `trace.rs:36`, `trace.py:267` | 🟢 |
| `t0` da primeira mensagem, coerente com o servidor (que usa o `ts` da própria mensagem; para chaves com 2 mensagens de golpe, a segunda mensagem no servidor tem `t0` diferente do CLI) | `trace.rs:27-32` | 🟢 |
| Referência gerada pelo Rust (`trace_ref.jsonl`) | README | 🟢 |

## Estado Interno
Nenhum.

## Observabilidade
stderr conforme tabela.

## Riscos e Lacunas
- 🟢 A conferência não cobre `para_desenho` (nodes/edges) nem `trace_ms`.
- 🟡 Quadrilhas com 2 mensagens de golpe: o CLI só rastreia com o `t0` da primeira; o servidor rastreia as duas com `t0` distintos e pode obter resultados diferentes entre si (esperado, não é bug).
- 🟢 Sem teste automatizado; a verificação depende de alguém rodar os dois comandos.
