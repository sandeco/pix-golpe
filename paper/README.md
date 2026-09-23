# Pacote de dados para artigo científico

Material de reprodutibilidade do experimento **Pix Race**: detecção de golpe do Pix por IA e rastreio do
dinheiro num grafo de transações, comparando **Rust + Jev (TypeSafe AI)** e **Python + DeepSeek** sob o
mesmo dataset, as mesmas perguntas e a mesma concorrência.

Conteúdo desta pasta:

| Arquivo | O que é |
|---|---|
| `SHA256SUMS` | Hash SHA-256 dos cinco arquivos de `data/`, para conferir que o dataset é o mesmo |
| `capture_run.py` | Cliente WebSocket que dispara uma corrida e grava todos os eventos brutos em JSONL |
| `analyze.py` | Gera tabelas CSV, tabela LaTeX, matriz de confusão, concordância entre lados e figuras |
| `results/run-2026-09-22-burst.jsonl` | Dado bruto da corrida de 22/09/2026 (3156 eventos, modo burst) |
| `results/run-2026-09-22-burst/` | Saída do `analyze.py` para essa corrida |

## 1. Dataset (sintético, semente fixa)

Gerado por `cargo run --release --bin gerar-dados` ([src/bin/gerar_dados.rs](../src/bin/gerar_dados.rs)),
gerador de números aleatórios ChaCha8 com semente 42. Nenhum dado bancário real. Os quatro arquivos pequenos
estão versionados em `data/`; o binário de transações (160 MB) é gerado localmente em cerca de 10 s e sai
idêntico byte a byte, o que foi conferido em 22/09/2026 regenerando e comparando com `SHA256SUMS`.

| Arquivo | Tamanho | Conteúdo |
|---|---|---|
| `mensagens.jsonl` | 188 934 B | 1000 mensagens em português: 75 golpes, 925 legítimas, embaralhadas, 120 remetentes distintos. Campos `id`, `ts`, `remetente`, `texto`, `chave`, `golpe_real` |
| `chaves.json` | 26 999 B | Mapa chave Pix → id da conta (nó do grafo) |
| `transacoes.bin` | 159 496 188 B | 9 968 511 transações entre 1 000 000 de contas, 10 dias. Little-endian: cabeçalho `PIX1`, `u32 n_contas`, `u32 n_transacoes`, depois registros de 16 B (`u32 origem`, `u32 destino`, `u32 valor_centavos`, `u32 ts`) ordenados por `ts` |
| `meta.json` | 35 665 B | Verdade de referência: 2000 hubs e 40 quadrilhas (chave, nó, laranjas, contas de saque, `inicio_ts`) |
| `trace_ref.jsonl` | 10 557 B | Rastreio de referência das 40 quadrilhas, saída do binário `trace` em Rust |

Parâmetros do gerador: `N_CONTAS = 1 000 000`, `N_HUBS = 2000` (pesos 1/(i+1)^0.8), `DIAS = 10`,
`N_TX_NORMAIS = 9 500 000` (valores log-normais, mediana R$ 80, horário comercial com peso 3),
lotes diários dos hubs (10 a 1510 transações por dia), `N_QUADRILHAS = 40` com 12 a 18 laranjas e 2 contas
de saque cada (606 laranjas e 80 contas de saque no total), 20 a 40 vítimas por quadrilha pagando entre
R$ 300 e R$ 3000. Mensagens: 75 golpes e 925 legítimas a partir de templates.

Verdade de referência por mensagem: `golpe_real`. Os modelos nunca recebem esse campo.
Verdade por rastreio: conjunto de laranjas e contas de saque da quadrilha ligada à chave Pix da mensagem.

## 2. Protocolo experimental

**Dois braços, mesma entrada.** Cada mensagem é enviada aos dois lados ao mesmo tempo:

| | Rust + Jev | Python + DeepSeek |
|---|---|---|
| Linguagem | Rust 1.88 (axum, tokio, reqwest) | Python 3.12, puro (sem numpy), `httpx`, `websockets` |
| Modelo | `jev-latest`, servido como `jev-1.13.0` | `deepseek-chat`, respondido como `deepseek-flash`, `temperature = 0`, `response_format = json_object` |
| Endpoint | `https://api.typesafe.ai/v1/systemone` | `https://api.deepseek.com/chat/completions` |
| Perguntas | 4 campos tipados numa passada: `golpe` (nível), `tipo` (escolha entre 8 classes), `urgencia` (score 0 a 2), `pede_pix` (nível) | As mesmas 4 em JSON, com o mesmo texto de instrução |
| Custo | US$ 0,042 por milhão de tokens de entrada | US$ 0,28 por milhão de entrada, US$ 0,42 por milhão de saída (estimado a partir de `usage`) |

**Veredito em três faixas** (idêntico nos dois lados): `golpe >= 0,6` → GOLPE; `golpe <= 0,4` → OK;
entre os dois → SUSPEITA. Na classe binária usada para acurácia, precisão e recall, só GOLPE conta como
positivo; SUSPEITA conta como negativo (golpe perdido quando a mensagem era golpe).

**Rastreio** (só quando o veredito é GOLPE): busca temporal em largura a partir da conta da chave Pix,
janela `JANELA = 86 400 s` (24 h), profundidade máxima `PROF_MAX = 5`, valor mínimo `VALOR_MIN = 2000`
centavos, `MAX_NOS = 40 000` nós visitados, propagação de rótulos com `ITER_LP = 10` iterações,
classificação em laranjas e contas de saque. Mesmo algoritmo em [src/graph.rs](../src/graph.rs) e
[py-worker/trace.py](../py-worker/trace.py); a igualdade é verificada bit a bit nas 40 quadrilhas
(`trace_ref.jsonl`). O grafo fica em memória como listas de adjacência de saída em formato CSR,
ordenadas por tempo dentro de cada conta.

**Concorrência e ritmo.** Modo `burst`: até 8 mensagens em voo por lado (`CONCORRENCIA = 8`),
sem pausa entre mensagens. O rastreio é serializado dentro de cada lado. O tempo de decisão mede a chamada
HTTP ao modelo (do envio até a resposta parseada); o tempo de rastreio mede só o algoritmo, com o grafo já
carregado (carga medida à parte: 395 ms, 128,9 MB).

**Coleta.** `capture_run.py` conecta em `ws://localhost:8080/ws`, envia `reset` e `start` com o modo,
grava cada evento recebido com o instante de recepção (`_recv_s`) e, quando os dois lados emitem `done`,
pede o `report` do servidor e encerra.

## 3. Ambiente da corrida de 22/09/2026

| Item | Valor |
|---|---|
| CPU | Intel Core i9-13980HX (13ª geração) |
| RAM | 32 GB |
| SO | Windows 11 Home Single Language 10.0.26200 |
| Rust | rustc 1.88.0 |
| Python | 3.12.0, `websockets` 15.0.1, `httpx` 0.28.1 |
| Rede | APIs externas via internet doméstica; a latência inclui a rede |

## 4. Resultados da corrida de 22/09/2026 (modo burst)

Resumo de `results/run-2026-09-22-burst/summary.csv`:

| | Rust + Jev | Python + DeepSeek |
|---|---|---|
| Mensagens avaliadas | 1000 | 999 (1 falha de TLS no cliente, mensagem 7) |
| Tempo total | 46,0 s | 141,6 s |
| Decisão p50 [IC 95% bootstrap] | 358,9 ms [355,0, 363,0] | 1099,6 ms [1088,7, 1116,6] |
| Decisão p95 | 460,1 ms | 1410,4 ms |
| Rastreio p50 | 28,1 ms | 294,2 ms |
| Rastreio p95 | 66,6 ms | 1130,3 ms |
| TP / FP / FN / TN | 73 / 0 / 2 / 925 | 75 / 0 / 0 / 924 |
| Acurácia / Precisão / Recall / F1 | 0,998 / 1,0 / 0,973 / 0,987 | 1,0 / 1,0 / 1,0 / 1,0 |
| SUSPEITA em golpe real / em normal | 2 / 9 | 0 / 0 |
| Recall de laranjas no rastreio | 0,986 | 0,985 |
| Tokens entrada / saída | 611 513 / 148 729 | 320 421 / 39 782 |
| Custo | US$ 0,0257 (só entrada é cobrada) | US$ 0,1064 (estimado) |

Concordância entre os lados (`agreement.csv`): 988 de 999 vereditos iguais, kappa de Cohen 0,925;
os 73 rastreios feitos pelos dois lados deram laranjas e contas de saque idênticas.

Os IC 95% das medianas vêm de bootstrap com 10 000 reamostragens (semente 42). Os números da
corrida anterior (21/09/2026), citados no README principal, foram lidos da tela e não têm dado bruto.

Limitações a declarar no artigo: dataset sintético (os modelos acertam quase tudo, a diferença está em
latência e custo); uma única corrida por modo; latência inclui rede e fila da API; custo do lado Python
é estimado a partir dos tokens reportados e da tabela de preços pública; Python puro sem numpy por regra
do experimento.

## 5. Como reproduzir

```
cargo run --release --bin gerar-dados            # gera data/ (10 s); confira com: cd data && sha256sum -c ../paper/SHA256SUMS
cargo run --release --bin server                 # precisa do .env com as duas chaves
python paper/capture_run.py burst                # grava paper/results/run-<data>-burst.jsonl
python paper/analyze.py paper/results/run-<data>-burst.jsonl
```

Para o modo serial (uma mensagem por vez por lado): `python paper/capture_run.py serial`.
