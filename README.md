# Pix Race: IA detecta golpe do Pix e rastreia a quadrilha

Demo em tela dividida para vídeo. Esquerda: **Rust + Jev** (TypeSafe AI). Direita: **Python + DeepSeek**.
As mesmas mensagens entram nos dois lados ao mesmo tempo. Cada lado decide se é golpe e, se for, rastreia
o caminho do dinheiro num grafo com 10 milhões de transações e 1 milhão de contas.

Tudo é simulado. Mensagens geradas por templates, transações geradas com semente fixa. Nenhum dado bancário real.

## Pré-requisitos

- Rust (cargo)
- Python 3.12 com `websockets`, `httpx` e `truststore` (`pip install -r py-worker/requirements.txt`)
- Uma chave da [TypeSafe AI](https://typesafe.ai) (Jev) e uma chave da [DeepSeek](https://platform.deepseek.com)

## Configurar as chaves

Na raiz do projeto existe o arquivo `.envexemple`. Renomeie para `.env` e preencha as duas chaves:

```
TYPESAFE_API_KEY=sua_chave_typesafe
DEEPSEEK_API_KEY=sua_chave_deepseek
```

O servidor Rust carrega o `.env` com `dotenvy` e o worker Python lê o mesmo arquivo. O `.env` está no
`.gitignore`, nunca suba ele para o GitHub.

## Rodar

Na pasta do projeto:

```
cargo run --release --bin gerar-dados     # uma vez: cria a pasta data/
cargo run --release --bin server          # sobe o servidor e o worker Python juntos
```

Abra http://localhost:8080 e clique em **Iniciar**.

- **Narrado · 4 s**: cada lado decide uma mensagem, mostra o veredito e espera 4 s. Para narrar.
- **Normal**: sem espera, uma mensagem por vez em cada lado. Rust dispara na frente; Python se arrasta.
- O ritmo pode ser trocado no meio da corrida. **Parar** congela a tela onde está.
- **Relatório de acurácia**: habilita ao terminar ou parar. Matriz de confusão por lado, acurácia, precisão,
  recall, custo por lado e gasto total da corrida.
- Clicar num golpe da lista abre o detalhe: mensagem, modelo, tokens, custo da decisão e o rastreio daquele golpe no grafo.
- `PIX_NO_WORKER=1` sobe só o lado Rust. `http://localhost:8080/?mock=1` mostra a tela com eventos falsos, sem chaves.

## Como funciona

1. Mensagem em português entra nos dois lados.
2. Decisão: Jev responde 4 perguntas tipadas numa passada (golpe? tipo? urgência? pede Pix?). DeepSeek responde as mesmas 4 em JSON. Latência medida em cada lado.
3. Se `golpe >= 0.6`, rastreio: busca temporal de 24 h a partir da chave Pix, suspeição por conta, propagação de rótulos, classificação em laranjas e contas de saque. Mesmo algoritmo em Rust ([src/graph.rs](src/graph.rs)) e Python puro ([py-worker/trace.py](py-worker/trace.py)), verificado bit a bit nas 40 quadrilhas.
4. O grafo acende na tela e o placar mostra ms, custo e acertos contra a verdade de referência.

O grafo fica em memória como listas de adjacência de saída em formato CSR, ordenadas por tempo dentro de cada conta.
Carga dos 10 milhões de transações: cerca de 400 ms, 129 MB.

Regras de justiça: mesmo dataset, mesmas perguntas, mesma concorrência, rastreio serializado nos dois lados, Python sem numpy.

## Dados para artigo científico

A pasta [paper/](paper/) tem o dataset card, o protocolo experimental, o ambiente, o dado bruto de uma corrida
completa (`paper/results/*.jsonl`) e os scripts que geram as tabelas, a matriz de confusão, os intervalos de
confiança e as figuras. Checksums do dataset em `paper/SHA256SUMS`.

## Gerar os dados (pasta `data/`)

O repositório traz os arquivos pequenos de `data/` (mensagens, chaves, verdade de referência e rastreio de
referência). O binário de transações tem 160 MB e não está no GitHub: você gera na sua máquina, e o resultado
é idêntico byte a byte, porque o gerador usa semente fixa (ChaCha8, semente 42).

```
cargo run --release --bin gerar-dados     # cerca de 10 s, escreve os cinco arquivos em data/
sha256sum -c paper/SHA256SUMS             # rode dentro de data/; os cinco devem dar OK
```

- `mensagens.jsonl`: 1000 mensagens (75 golpes, 925 legítimas), com `id`, `ts`, `remetente`, `texto`, `chave` e `golpe_real`.
- `chaves.json`: mapa de chave Pix para id de conta.
- `transacoes.bin`: 9 968 511 transações entre 1 000 000 de contas. Binário little-endian, cabeçalho `PIX1`,
  `u32 n_contas`, `u32 n_transacoes`, depois registros de 16 bytes (`u32 origem`, `u32 destino`, `u32 valor_centavos`, `u32 ts`),
  ordenados por `ts`.
- `meta.json`: verdade de referência das 40 quadrilhas (chave, nó, laranjas, contas de saque, início).
- `trace_ref.jsonl`: rastreio de referência das 40 quadrilhas, usado para conferir o porte Python.

O gerador sobrescreve os arquivos existentes em `data/`. Como a saída é determinística, isso não muda nada.

## Conferir a igualdade dos algoritmos

```
cargo run --release --bin trace -- --todas > data/trace_ref.jsonl
python py-worker/trace.py --todas > data/trace_py.jsonl
fc data\trace_ref.jsonl data\trace_py.jsonl
```

## Números medidos (2026-09-21, 1000 mensagens, 75 golpes, rajada com 8 em paralelo por lado)

| | Rust + Jev | Python + DeepSeek |
|---|---|---|
| Tempo total | 36 s | 139 s |
| Decisão p50 / p95 | 280 ms / 356 ms | 1085 ms / 1376 ms |
| Rastreio p50 / p95 | 14 ms / 32 ms | 239 ms / 734 ms |
| Golpes detectados | 74 de 75 (1 ficou como "suspeita") | 75 de 75 |
| Falsos alarmes | 0 (8 normais como "suspeita") | 0 |
| Acurácia | 99,9% | 100% |
| Custo | US$ 0,026 | US$ 0,106 (estimado) |

p50 é a mediana: metade das decisões levou até esse tempo. p95: 95% das decisões ficaram abaixo dele.

No modo Normal (uma mensagem por vez), a diferença de velocidade é maior ainda: em 40 s o Rust passa de 140 mensagens enquanto o Python fica perto de 40.

Honestidade para o vídeo: os dois modelos acertam praticamente tudo neste dataset simulado. A vantagem do Jev é velocidade e custo, e o botão "Relatório de acurácia" mostra a matriz de confusão dos dois. O rastreio dá o mesmo resultado nas duas linguagens; a diferença é só tempo de execução.
