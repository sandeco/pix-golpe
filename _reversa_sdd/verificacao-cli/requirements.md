# Verificação por CLI

> Unit `verificacao-cli`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Ferramentas de linha de comando para conferir a igualdade do rastreio entre Rust e Python (`trace` e `trace.py`) e para testar o cliente DeepSeek com uma mensagem (`deepseek.py`). Substituem a suíte de testes automatizados, que não existe.

## Responsabilidades
- `cargo run --release --bin trace -- <chave>` ou `--todas`: carregar o grafo, rastrear e imprimir o resumo JSON por chave em stdout, diagnósticos em stderr.
- `python py-worker/trace.py <chave>` ou `--todas`: mesmo comportamento com o porte Python.
- Comparação manual: `fc data\trace_ref.jsonl data\trace_py.jsonl`.
- `python py-worker/deepseek.py [texto] [--remetente]`: classificar uma mensagem e imprimir a decisão.

## Regras de Negócio
- `t0` por chave = `ts` da **primeira** mensagem (ordem do arquivo) com aquela chave; se não houver, `inicio_ts − 300` da quadrilha; senão 0. 🟢 `trace.rs:27-32`, `trace.py:251-263`
- `--todas` = as 40 chaves de `meta.json.quadrilhas`, na ordem do arquivo. 🟢
- Chave inexistente em `chaves.json` → erro ("chave desconhecida"). 🟢
- Rust: argumento ausente equivale a `--todas`. Python: exige exatamente um de `chave` ou `--todas` (`parser.error`). 🟢 `trace.rs:9`, `trace.py:242-243`
- stdout recebe só o JSON compacto do resumo (uma linha por chave); stderr recebe carga e diagnóstico. Python força UTF-8 em stdout/stderr. 🟢 `trace.py:236-237`
- Rust imprime também acertos de laranjas (`acertou la/lr`) usando `meta.json`; Python não. 🟢 `trace.rs:37-39`
- Python destrói o resultado anterior (`del result`) antes da próxima medição. 🟢 `trace.py:271`
- `deepseek.py` sem texto usa a primeira mensagem com `golpe_real` do dataset (verdade só para escolher o exemplo); imprime `verdict` e `cost_usd` no JSON. 🟢 `deepseek.py:162-178`
- Igualdade esperada: `visitados`, `arestas_sub`, `laranjas`, `saque`, `soma_suspeita` idênticos nas 40 chaves; `data/trace_ref.jsonl` é a referência gerada pelo Rust. 🟢 README, SPEC §3

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | `trace --todas` imprime 40 linhas JSON iguais a `data/trace_ref.jsonl` | Must | `fc` sem diferenças |
| RF-02 | `trace.py --todas` imprime as mesmas 40 linhas | Must | `fc` sem diferenças |
| RF-03 | `trace <chave>` / `trace.py <chave>` para uma chave | Should | 1 linha |
| RF-04 | Diagnóstico em stderr com carga (ms) e por chave (nós, arestas, ms) | Should | stderr não contamina stdout |
| RF-05 | Erro claro para chave desconhecida | Should | mensagem "chave desconhecida: X" |
| RF-06 | `deepseek.py` classifica uma mensagem e imprime decisão com veredito e custo | Could | JSON em stdout |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Reprodutibilidade | saída determinística | unit `rastreio-no-grafo` | 🟢 |
| Portabilidade | UTF-8 forçado no Windows | `trace.py:236-237` | 🟢 |
| Performance | carga do grafo medida e reportada (Rust ~s, Python dezenas de s) 🟡 | stderr | 🟡 |

## Critérios de Aceitação

```gherkin
Dado data/ gerado
Quando executo cargo run --release --bin trace -- --todas > a.jsonl e python py-worker/trace.py --todas > b.jsonl
Então a.jsonl e b.jsonl são idênticos e têm 40 linhas

Dado a chave 51942117050
Quando executo trace.py 51942117050
Então stdout tem uma linha JSON com "visitados":10782 e "soma_suspeita":2627.0042

Dado a chave inexistente "abc"
Quando executo trace abc
Então o processo falha com "chave desconhecida: abc"

Dado trace.py sem argumentos
Quando executo
Então argparse responde "informe uma chave ou --todas"
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `--todas` nos dois lados | Must | única verificação da igualdade |
| Chave única | Should | depuração |
| `deepseek.py` CLI | Could | teste manual |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/bin/trace.rs` | `main` | 🟢 |
| `py-worker/trace.py:234-275` | `main` | 🟢 |
| `py-worker/deepseek.py:162-186` | `main` | 🟢 |
| `data/trace_ref.jsonl` | referência | 🟢 |
