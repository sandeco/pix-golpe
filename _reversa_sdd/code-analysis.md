# Análise de código: pix-golpe

> Gerado pelo Archaeologist (Reversa) em 2026-09-21. Nível: completo. Escala: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.
> Fontes: todos os arquivos de `src/`, `py-worker/` e `static/index.html`, mais `SPEC.md`, `README.md` e o PDF do projeto.

## Visão geral

O sistema é uma corrida em tela dividida. Um servidor Rust (axum) carrega o grafo de transações em memória, distribui as mesmas 1.000 mensagens para dois "lados" e repassa os eventos ao navegador por WebSocket. O lado Rust roda dentro do próprio servidor (cliente Jev + `graph.rs`). O lado Python é um processo separado (`worker.py`) que o servidor sobe automaticamente, conecta em `/ws/worker`, chama o DeepSeek e roda o porte puro-Python do mesmo algoritmo de rastreio. O navegador só desenha.

```
gerar-dados ──► data/{transacoes.bin, mensagens.jsonl, chaves.json, meta.json}
                      │                       │
                      ▼                       ▼
            server.rs (lado Rust)     worker.py (lado Python)
            Jev API + graph.rs        DeepSeek API + trace.py
                      │        ▲               │
                      │        └── /ws/worker ─┘
                      ▼
               /ws ──► static/index.html (browser)
```

Regras transversais 🟢:

| Regra | Onde |
|---|---|
| Veredito: `golpe >= 0.6` → `golpe`; `<= 0.4` → `ok`; entre → `revisar` | `src/jev.rs:33-41`, `py-worker/deepseek.py:71-72` |
| Só `golpe` dispara rastreio | `server.rs:374`, `worker.py:265` |
| Rastreio serializado por lado (um por vez) | `server.rs:379` (`trace_lock`), `worker.py:267` (`trace_lock`) |
| Concorrência das decisões: 8 em `burst`, 1 nos demais modos | `server.rs:26,306`, `worker.py:213` |
| `golpe_real` nunca vai aos modelos; só ao relatório | `server.rs:317` (evento `message` sem o campo), `server.rs:92-96` |
| Aquecimento do modelo na inicialização, fora da medição | `server.rs:165`, `worker.py:165` |
| Latência de decisão = ida e volta HTTP medida pelo lado | `server.rs:338-340`, `deepseek.py:145-148` |
| Latência de rastreio = passos A a D, sem carga e sem desenho | `server.rs:381-385`, `worker.py:233-237` |

---

## Módulo `data` (`src/data.rs`, 134 linhas) 🟢

**Propósito:** formatos e I/O dos arquivos em `data/`.

### Estruturas

| Struct | Campos | Serialização |
|---|---|---|
| `Mensagem` | `id: u32, ts: u32, remetente: String, texto: String, chave: String, golpe_real: bool` | serde, JSONL |
| `Quadrilha` | `chave: String, no: u32, laranjas: Vec<u32>, saque: Vec<u32>, inicio_ts: u32` | serde, dentro de `Meta` |
| `Meta` | `n_contas: u32, n_transacoes: u32, hubs: Vec<u32>, quadrilhas: Vec<Quadrilha>` | serde, `meta.json` pretty |
| `Tx` | `origem: u32, destino: u32, valor: u32, ts: u32` (Copy) | binário manual, 16 bytes LE |

### Funções

| Função | Assinatura | Comportamento |
|---|---|---|
| `data_dir()` | `-> PathBuf` | tenta `./data` e depois `<CARGO_MANIFEST_DIR>/data`; escolhe a primeira com `meta.json`; fallback para a segunda |
| `read_mensagens(dir)` | `-> Result<Vec<Mensagem>>` | JSONL, ignora linhas em branco |
| `write_mensagens(dir, msgs)` | | um JSON por linha |
| `read_chaves(dir)` | `-> Result<HashMap<String,u32>>` | `chaves.json` |
| `write_chaves(dir, chaves)` | | grava ordenado por chave (BTreeMap), pretty |
| `read_meta` / `write_meta` | | `meta.json` pretty |
| `read_transacoes(dir)` | `-> Result<(u32, Vec<Tx>)>` | valida magic `PIX1` e `len == 12 + n*16`; lê tudo em memória (`fs::read`) |
| `write_transacoes(dir, n_contas, txs)` | | cabeçalho + registros, `BufWriter` |

### Formato `transacoes.bin` 🟢

```
offset 0   b"PIX1"
offset 4   u32 LE n_contas
offset 8   u32 LE n_transacoes
offset 12  n_transacoes × { u32 origem, u32 destino, u32 valor_centavos, u32 ts }
```
Ordenado por `ts` crescente (garantido pelo gerador, `gerar_dados.rs:222`). O leitor Rust **não** valida a ordem; o leitor Python (`trace.py:114`) valida ordem e faixa de contas.

---

## Módulo `gerar-dados` (`src/bin/gerar_dados.rs`, 274 linhas) 🟢

**Propósito:** gerar o dataset sintético, determinístico (`ChaCha8Rng::seed_from_u64(42)`), em `<CARGO_MANIFEST_DIR>/data`.

### Constantes

| Constante | Valor | Observação |
|---|---|---|
| `N_CONTAS` | 1.000.000 | ids 0..999.999 |
| `N_HUBS` | 2.000 | ids 0..1999 são comerciantes |
| `DIAS` | 10 | ts em 0..864.000 s |
| `N_TX_NORMAIS` | 9.500.000 | transações de fundo |
| `N_QUADRILHAS` | 40 | |
| `N_MSG_GOLPE` / `N_MSG_LEGIT` | 75 / 925 | total 1.000 |
| `GOLPES` | 30 templates | placeholders `{parente} {nome} {banco} {loja} {pedido} {valor} {chave}` |
| `LEGITIMAS` | 20 templates × remetentes coerentes | remetente escolhido de lista por template |

### Algoritmo de geração (ordem exata)

1. **Pesos dos hubs:** `peso[i] = 1/(i+1)^0.8`; escolha por roleta. Hub 0 é o maior.
2. **Transações normais** (9,5 M): origem uniforme em `[N_HUBS, N_CONTAS)`; destino 50 % hub (roleta) / 50 % conta normal ≠ origem; valor `LogNormal(ln 8000, 1.1)` em centavos, clamp `[500, 500_000]` (R$ 5 a R$ 5.000); `ts = ts_comercial(dia)` com horas 8..22 com peso 3× (linhas 146-161).
3. **Lotes diários dos hubs:** por hub e por dia, `diario = 10 + peso[h]/peso[0] × 1500` transações (hub 0: 1.510/dia), a partir de 9h + até 2h, dispersas em 30 min; valor `LogNormal(ln 30000, 0.8)` clamp `[2_000, 2_000_000]` (linhas 164-173). 🟡 Total estimado ≈ 465 mil transações (9.968.511 − 9.500.000 − quadrilhas).
4. **Quadrilhas** (40): contas reservadas (nunca reutilizadas): 1 nó da chave, 12 a 18 laranjas, 2 contas de saque. `inicio_ts` em dia 1..8, hora 9..19. 20 a 40 vítimas (contas não reservadas) pagam `30_000..300_000` centavos em até 2 h. `t_repasse = inicio + 7200 + 60..900 s`: a chave paga a cada laranja `total/n_lar − até 2 %` em até 5 min; cada laranja paga a uma das 2 contas de saque `valor − taxa(<1 %)` em `t_repasse + 300 + 300..2400 s`. Chave Pix nova gerada (`nova_chave`: telefone, e-mail ou uuid curto) e mapeada ao nó (linhas 188-220).
5. **Ordenação** global por `ts` (linha 222).
6. **Mensagens de golpe** (75): `quadrilha[i % 40]` (quadrilhas 0..34 recebem 2 mensagens, 35..39 recebem 1 🟢), template `GOLPES[i % 30]`, valor `8_000..250_000`, remetente telefone / `SMS 2xxxx` / telefone "(número desconhecido)"; `ts = inicio_ts − 120..600 s`.
7. **Mensagens legítimas** (925): template cíclico, chave nova apontando para hub (se template cita `{loja}`) ou conta normal; loja/banco iguais no texto e no remetente (correção registrada no brainstorm para evitar falsos positivos); `ts` comercial em dia 1..8.
8. **Shuffle** das 1.000 mensagens, `id` = posição final.
9. Escrita: `transacoes.bin`, `chaves.json`, `meta.json`, `mensagens.jsonl`.

Regra de negócio embutida 🟢: `normal()` sorteia qualquer conta ≥ N_HUBS, então contas reservadas (chave, laranjas, saque) **podem** receber ou originar transações de fundo; o gerador só garante o esquema da quadrilha. Medido: 807 transações de fundo saem de contas de saque. O SPEC ("não movimentam nada nas 24 h seguintes") está desatualizado; vale o código (usuário, 2026-09-22).

---

## Módulo `graph` (`src/graph.rs`, 365 linhas; porte `py-worker/trace.py`) 🟢

**Propósito:** grafo de saída em CSR e o algoritmo de rastreio determinístico.

### Parâmetros

| Constante | Valor | Papel |
|---|---|---|
| `JANELA` | 86.400 s | janela de 24 h a partir da chegada em cada nó |
| `PROF_MAX` | 5 | profundidade máxima do BFS |
| `VALOR_MIN` | 2.000 centavos | ignora transferências < R$ 20 |
| `MAX_NOS` | 40.000 | teto de nós visitados |
| `ITER_LP` | 10 | iterações da propagação de rótulos |
| `MAX_NODES_DESENHO` / `MAX_EDGES_DESENHO` | 800 / 1.500 | seleção para o canvas |

### Estrutura `Graph` (CSR)

`start[n+1]`, `dst[m]`, `val[m]`, `ts[m]`, `in_deg[n]`. Construído em `from_txs` por counting sort por origem, preservando a ordem por `ts` do arquivo (linhas 31-55). O Python usa `saida[v] = [(dst, valor, ts)]` e `grau_in_total` (`trace.py:108-119`).

### `Graph::trace(no_chave, t0) -> Trace`

- **Passo A, BFS temporal** (linhas 94-133): `chegada[v]` = ts de chegada; para cada aresta de saída de `v` com `chegada[v] <= ts <= chegada[v]+JANELA` e `valor >= VALOR_MIN`: a aresta entra em `sub` sempre; o destino só entra na fila se não visitado e `visitados < MAX_NOS`. Nós com `prof == PROF_MAX` não expandem. `ids` = visitados ordenados por id.
- **Passo B, suspeição** (linhas 135-158): `in_sum[v]` soma dos valores de `sub` com destino `v`; `out_sum`, `primeiro_out` via `saida_na_janela(v, chegada[v])` (mesmo critério do passo A, independente de profundidade). `repasse = min(1, out/in)`; `rapidez = 0` se sem saída, senão `max(0, 1 − (primeiro_out − chegada)/3600)`; `pequeno = 1` se `in_deg < 50`. `suspeita = 0.4·repasse + 0.5·rapidez + 0.1·pequeno`. Chave: `suspeita = repasse = 1`.
- **Passo C, propagação de rótulos** (linhas 160-221): grafo não direcionado dos pares `(min,max)` de `sub` sem autoarestas e com destino visitado; vizinhos ordenados por id; 10 iterações assíncronas em ordem crescente de id; rótulo = maior soma de suspeita dos vizinhos, empate → menor rótulo. Nós sem vizinhos mantêm rótulo.
- **Passo D, classificação** (linhas 223-243): `laranjas` = mesma comunidade da chave e `suspeita >= 0.6`; `saque` = não laranja, ≥ 3 arestas de `sub` vindas de laranjas (conta transações, não pares) e `repasse < 0.3`.
- `soma_suspeita` = soma em ordem crescente de id, arredondada a 4 casas (`f64::round`, empate longe do zero; Python replica com `rust_round`, `trace.py:25-31`, e evita `sum()` por causa da soma compensada do 3.12, `trace.py:222`).

### `Trace::para_desenho()` (linhas 309-364)

`nodes`: chave, laranjas, saque, depois os demais por `(prof, id)` até 800. `edges`: pares únicos `(src,dst)` de `sub` com os dois extremos presentes; primeiro as que tocam nós especiais (sem limite), depois as demais até 1.500; `truncate(1500)` no final (então as prioritárias também são cortadas se passarem de 1.500 🟢). Python idêntico (`trace.py:54-82`).

### Diferenças Rust × Python que **não** afetam a saída 🟢
- Rust usa vetores densos de tamanho `n` (1 M) por rastreio; Python usa dicts esparsos.
- Rust `sort_unstable` em ids; Python `sorted(chegada)`. Ids são únicos, resultado igual.
- Python valida `no_chave` fora do intervalo (`trace.py:122`); Rust confia no chamador.

---

## Módulo `jev` (`src/jev.rs`, 148 linhas) 🟢

**Propósito:** cliente da API TypeSafe AI System One.

- `URL = https://api.typesafe.ai/v1/systemone`, `MODEL = "jev-latest"`, `USD_POR_TOKEN_ENTRADA = 0.042e-6`. Saída não é cobrada.
- `JevClient::from_env()`: exige `TYPESAFE_API_KEY` não vazia; `reqwest::Client` com timeout 30 s.
- `classificar(remetente, texto) -> Decisao`: body `{model, state:{remetente, mensagem}, questions}`; até **3 retentativas** em HTTP 429/529 com backoff `200·2^n ms` (200, 400, 800). Qualquer outro status → erro com corpo.
- `questions()`: 4 perguntas tipadas: `golpe` (noul), `tipo` (choice, 8 critérios), `urgencia` (score 0..2, 3 níveis), `pede_pix` (noul). Instruções em inglês; estado em português.
- `Decisao { golpe, tipo, tipo_confianca, urgencia, pede_pix, tokens_in, tokens_out, model }`; `verdict()` e `cost_usd() = tokens_in × 0.042e-6`.
- Resposta esperada: `answers.golpe.noul`, `answers.tipo.{choice,confidence}`, `answers.urgencia.score`, `answers.pede_pix.noul`, `usage.input_tokens` (`output_tokens` opcional), `model`.

---

## Módulo `deepseek` (`py-worker/deepseek.py`, 186 linhas) 🟢

**Propósito:** cliente async do DeepSeek em JSON mode, com validação estrita.

- `API_URL = https://api.deepseek.com/chat/completions`, `MODEL = "deepseek-flash"`, `temperature 0`, `response_format json_object`. Custos estimados: entrada US$ 0,28/M, saída US$ 0,42/M.
- `load_api_key()`: env `DEEPSEEK_API_KEY` tem precedência; senão procura `.env` no cwd e nos pais, aceita `export`, aspas e comentário `#`.
- `DeepSeekClient`: `httpx.AsyncClient`, timeout 120 s (connect 20 s), pool de 8 conexões keepalive, TLS via `truststore` (store do sistema) quando disponível.
- `classificar()`: até `MAX_ATTEMPTS = 3` tentativas em 429/5xx com backoff `2^n s` (1, 2). `latency_ms` mede apenas a tentativa HTTP bem-sucedida (backoff excluído). Outros erros HTTP → `raise_for_status`.
- `parse_response()`: exige `choices[0].message.content` JSON com `golpe` (0..1), `urgencia` (0..2), `pede_pix` (0..1) numéricos finitos e não-bool, `tipo` ∈ 8 critérios, `model` string, tokens inteiros ≥ 0. Falha → `ValueError` (vira evento `error`).
- `SYSTEM_PROMPT` idêntico ao SPEC; user: `Remetente: <r>\nMensagem: <t>`.
- CLI: `python deepseek.py [texto] [--remetente]`; sem texto usa a primeira mensagem `golpe_real` do dataset.

**Assimetria de medição 🟢:** no lado Rust, `decision_ms` mede `classificar()` inteiro, **incluindo** os sleeps de retry (`server.rs:338-340`); no Python o backoff fica fora. Só importa quando há 429/5xx.

---

## Módulo `server` (`src/bin/server.rs`, 461 linhas) 🟢

**Propósito:** servidor HTTP/WS, orquestrador da corrida, lado Rust, relatório e verdade de referência.

### Estado `App`
`graph`, `mensagens`, `chaves`, `truth: HashMap<no, Quadrilha>`, `jev`, `browsers: broadcast(8192)`, `worker: Mutex<Option<mpsc::UnboundedSender>>`, `rust_status`, `python_status`, `run_id: AtomicU32`, `pace_ms: AtomicU64`, `verdicts: Mutex<HashMap<side, HashMap<id, verdict>>>`, `trace_lock: tokio::Mutex<()>`, `data_dir`, `step_ms`.

### Inicialização (`main`)
1. `dotenvy::dotenv()`; `data_dir()`.
2. Lê `transacoes.bin`, monta `Graph`, descarta o vetor bruto, mede `load_ms` e `memory_mb` (`memory_stats`, RSS).
3. Lê mensagens, chaves, meta → `truth`.
4. `JevClient::from_env()` (falha aborta); aquecimento com "Oi, tudo bem? Aquecimento." (falha só avisa; `model` cai para `jev-latest`).
5. `PIX_STEP_MS` (padrão 2500) só afeta o modo `step` sem sufixo.
6. Sobe `python py-worker/worker.py` com `kill_on_drop`, salvo `PIX_NO_WORKER` definido ou arquivo ausente.
7. Rotas: `GET /` → **lê `static/index.html` do disco a cada request** (não é `include_str!` como diz o SPEC §4 🟢 divergência), `GET /ws`, `GET /ws/worker`. Bind `0.0.0.0:8080`.

### Comandos do browser (`comando_browser`)
| type | Efeito |
|---|---|
| `start {mode}` | `pace_ms = pace_de(mode)`; `run_id += 1`; limpa `verdicts`; envia `reset` a todos; `spawn(run)` |
| `pace {mode}` | atualiza `pace_ms`; broadcast `pace {run_id, mode, ms}` a todos |
| `report` | envia `relatorio()` só aos browsers |
| `stop` | `run_id += 1` (invalida a corrida) e envia `stop {run_id antigo}` a todos |
| `reset` | `run_id += 1`; envia `reset` a todos |

`pace_de`: `"step"` → `step_ms`; `"step:<ms>"` → ms; qualquer outro (`serial`, `burst`) → 0.

### Corrida (`run`)
`concurrency = 8` se `mode == "burst"`, senão 1. Emite `run {run_id, mode, total, concurrency, pace_ms}` a todos, depois **todas** as mensagens de uma vez (evento `message` sem `golpe_real`), uma task `processar` por mensagem limitada por `Semaphore`. Ao terminar (e se `run_id` ainda for o mesmo) emite `done` do lado Rust com p50/p95 (`percentil`: nearest-rank `round(p·(n−1))`), custo e `total_ms`.

### `processar` (lado Rust, por mensagem)
1. Adquire permit; chama Jev; mede `decision_ms`.
2. Se `run_id` mudou, descarta. Erro → `stats.erros++`, evento `error`.
3. Registra veredito, custo, `golpes`; emite `decision`.
4. **Ritmo narrado:** dorme `pace_ms` ainda segurando o permit (serializa o lado no modo passo a passo).
5. Se `golpe`: resolve `chaves[m.chave]`, `t0 = m.ts`; sob `trace_lock`, roda `graph.trace` em `spawn_blocking`, mede `trace_ms`; emite `trace` com `nodes` (suspeita com 3 casas), `edges` e `truth` via `enrich_truth`.

### Worker (`handle_worker`)
Ao conectar: registra canal, envia `hello {data_dir}` (caminho canonizado sem `\\?\`, barras `/`), status `connected`. Cada evento do worker recebe `side = "python"`; `status` é guardado; `decision` registra veredito; `trace` ganha `truth`; tudo é repassado aos browsers. Ao desconectar, só limpa o slot se ainda for o mesmo canal e emite `offline`.

### Relatório (`relatorio`)
Por lado, sobre as mensagens com veredito registrado: matriz `real ∈ {golpe, normal}` × `veredito ∈ {golpe, revisar, ok}`; `tp = (golpe,golpe)`, `fn = (golpe,ok)+(golpe,revisar)`, `fp = (normal,golpe)`, `tn = (normal,ok)+(normal,revisar)`; `acuracia = (tp+tn)/avaliadas`, `precisao = tp/(tp+fp)`, `recall = tp/(tp+fn)`, divisão por zero → 0.

---

## Módulo `worker` (`py-worker/worker.py`, 331 linhas) 🟢

**Propósito:** lado Python: WS, DeepSeek com concorrência, rastreio serializado, estatísticas.

- Conecta em `ws://127.0.0.1:8080/ws/worker` (`open_timeout 10`, `proxy=None`), reconecta a cada 2 s para sempre; ao cair, `run = None`.
- `parse_event`: valida tipo e campos obrigatórios de `hello`, `run`, `reset`, `message` (tipos exatos, inteiros ≥ 0). Um `message` malformado com `id` válido conta como erro da corrida e ainda "conclui" a unidade (para o `done` sair).
- `hello`: carrega `Graph.load(data_dir)` em thread, `chaves.json`, `gc.collect()`, mede `load_ms` e memória (`psutil` → `GetProcessMemoryInfo` no Windows → `resource`); aquecimento do DeepSeek; emite `status loading` → `ready {nodes, edges, load_ms, memory_mb, model}`. Falha na inicialização emite `error` e re-levanta (reconecta preservando grafo já carregado).
- `run`: novo `Semaphore(concurrency)`, `pace_ms`, novo `Run`; `reset`/`stop`: `run = None` (tasks em voo descartam resultados por identidade do objeto `Run`); `pace`: atualiza `pace_ms`.
- `message`: ignora `run_id` antigo, corrida concluída ou id duplicado; cria task `process_message`.
- `process_message`: sob semáforo → `classificar` → veredito, custo, stats → `emit decision` → sleep `pace_ms` (ainda sob semáforo, igual ao Rust). Se `golpe`: sob `trace_lock`, `to_thread(trace_for_message)`; `emit trace` com `nodes` (`rust_round(s,3)`), `edges`. Exceções viram `error` e contam em `erros`. `finally: finish_message` → `processed++` → `done` quando `processed == total`.
- `emit`: injeta `side="python"` e `run_id`; descarta se a corrida mudou; `allow_nan=False`.

---

## Módulo `frontend` (`static/index.html`, 1.606 linhas: CSS 8-207, HTML 209-347, JS 348-1604) 🟢

**Propósito:** tela dividida para gravação, 1920 px de largura escalada por `zoom`.

### Estrutura HTML
- `header.topbar`: `h1` "DETECTOR DE GOLPE" (o screenshot `docs/tela-corrida.png` mostra "PIX RACE", versão anterior 🟡), status de conexão, `select#mode` (`step:4000` "Narrado · 4 s", `serial` "Normal"), `button#start` (Iniciar / Parar / Reiniciar), `button#report`.
- `#race`: duas `section.lane` clonadas de `template#lane-template` (`rust`, `python`). Cada lane: contador gigante `processadas / total`, barra de progresso, `dl.speed` (DECISÃO p50, RASTREIO p50, MEMÓRIA), bolha da mensagem atual (clicável quando golpe), veredito (`waiting | golpe | ok | revisar | error` → "Aguardando... / GOLPE / OK / SUSPEITA / ERRO"), painel "Caminho do dinheiro" (canvas radial + fluxo GOLPISTA → LARANJAS → SAQUE com moedas animadas + resumo), lista "Golpes acumulados", acumulador "N processadas · N golpes · N ok", `alert-wash` (flash vermelho).
- `section#final` (cartão final, quando os dois `done` chegam): tempo total em segundos, decisão p50, rastreio p50, golpes, custo (Python rotulado "estimado"), botões Fechar / Reiniciar.
- `section#accuracy-report`: matriz 2×3 por lado, acurácia/precisão/recall, conclusão em prosa (`reportConclusion`).
- `#scam-modal`: detalhes de um golpe (mensagem, veredito, barras de golpe/urgência/pede_pix, dados técnicos, grafo, contas laranja/saque).
- `footer`: "Mensagens simuladas. Transações simuladas. Mesmo algoritmo nas duas linguagens, Python puro."

### Máquina de estados do JS
`phase ∈ {idle, running, done, stopped}`; `pending` (aguardando ack), `pendingStart` (reinício após `reset`), `transportReady`, `runId`.

`receive(event)` (linhas 1220-1320):
- `run` → `clearRun()`, adota `run_id`, `total`, `mode`, `concurrency`, `pace_ms`; se o usuário mudou o ritmo enquanto esperava, envia `pace`.
- Eventos com `run_id` diferente do atual são descartados.
- `reset` → limpa; se havia `pendingStart`, envia `start` de novo.
- `status` → conexão por lado e memória ("GB" acima de 1024 MB).
- `pace` → sincroniza o `select`. `stop` → `stopRun()` (fase `stopped`, congela). `report` → `showReport` só em `done|stopped`.
- Em `stopped`, nada mais muda a tela.
- `message` → só cacheia texto/remetente/chave/ts.
- `decision` → mediana de latência, mostra mensagem, veredito, adiciona à lista se golpe, conta `ok`, atualiza contador. `trace` → mediana, guarda, desenha se é o golpe mais recente, atualiza modal. `error` → conta e mostra ERRO. `done` → `lane.done`; `showFinal()` só quando **os dois** lados terminaram.

Comandos enviados: `start {mode}`, `reset` (quando já houve corrida; reinício encadeado), `stop`, `pace {mode}`, `report`. Reconexão do WS com backoff `500·2^n ms` até 10 s.

### Grafo no canvas
`prepareGraph`: layout radial por `prof` (anéis), nós distribuídos uniformemente; 600 "estrelas" de fundo com `seeded(42)`; cores: chave/laranjas/saque destacados; animação de onda 300 ms (`requestAnimationFrame`); hover mostra tooltip com id, prof, suspeita. `graphCache` (WeakMap) por evento.

### Modo mock (`?mock=1`)
12 fixtures com verdade independente (`mockTruth`), 24 mensagens, Rust rápido / Python lento, `done`, `report` e `stop` simulados. Tudo passa por `receive()`.

### Acessibilidade
`role=dialog`, `aria-live`, foco preso no modal (Tab/Shift+Tab), `Escape` fecha, `prefers-reduced-motion` desliga animações. Tema escuro fixo.

---

## Módulo `trace-cli` (`src/bin/trace.rs` 42 linhas; `py-worker/trace.py::main`) 🟢

- Rust: arg único (`--todas` padrão). Carrega grafo (mede carga em stderr), chaves, meta, mensagens. Para cada chave: `t0` = `ts` da **primeira** mensagem com aquela chave, senão `inicio_ts − 300`, senão 0. Imprime `TraceResumo` JSON em stdout e diagnóstico (acertos de laranjas) em stderr.
- Python: `chave` ou `--todas` (exclusivos). Mesma regra de `t0` (`primeiros.setdefault`). Stdout reconfigurado para UTF-8; `del result` fora da medição.
- Verificação de igualdade: `fc data\trace_ref.jsonl data\trace_py.jsonl`. Sem teste automatizado.

---

## Lacunas e divergências encontradas

| # | Item | Status |
|---|---|---|
| L1 | Escala do dataset: docs dizem 100 k contas / 1,3 M tx / 200 hubs; código tem 1 M / 9,97 M / 2.000 | 🟢 resolvido: vale o código (usuário, 2026-09-22); docs desatualizados |
| L2 | SPEC §4: `index.html` "embutido com include_str!"; código lê do disco a cada request | 🟢 divergência documental |
| L3 | SPEC §1: "contas de saque não movimentam nada nas 24 h seguintes"; o gerador não impede transações de fundo com elas (807 medidas) | 🟢 resolvido: vale o código; SPEC desatualizado |
| L4 | `decision_ms` do Rust inclui backoff de retry; Python exclui | 🟢 assimetria confirmada; intenção 🔴 sem resposta (Pergunta 2) |
| L5 | `h1` atual "DETECTOR DE GOLPE" vs screenshot "PIX RACE" | 🟡 screenshot desatualizado |
| L6 | SPEC §4 descreve modos `step`/`burst` na UI; o `select` só expõe `step:4000` e `serial`; `burst` só via protocolo | 🟢 |
| L7 | `memory_mb` no `status` e "MEMÓRIA" na tela não constam do SPEC | 🟢 adição posterior |
| L8 | Sem testes automatizados; igualdade Rust/Python verificada só manualmente | 🟢 |
