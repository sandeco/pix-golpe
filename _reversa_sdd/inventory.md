# Inventário do projeto: pix-golpe (pacote Rust `pix-race`)

> Gerado pelo Scout (Reversa) em 2026-09-21. Nível: completo. Escala: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## 1. Propósito 🟢

Demo em tela dividida para vídeo do canal: "IA detecta golpe do Pix e rastreia a quadrilha". Esquerda **Rust + Jev** (TypeSafe AI), direita **Python + DeepSeek**. As mesmas mensagens em português entram nos dois lados; cada lado decide se é golpe e, se for, rastreia o caminho do dinheiro num grafo de transações sintéticas. Objetivo: comparar latência, custo e acertos. Nada é real: sem consulta a banco, sem bloqueio de Pix.

Fontes: `README.md`, `SPEC.md`, `output/pdf/pix-golpe-explicacao.pdf` (guia do projeto, 8 páginas, 21/09/2026), `BRAINSTORMING/BRAINSTORM_jev_rust_youtube.md` (origem da ideia, decisão em 2026-09-21).

## 2. Estrutura de pastas 🟢

```
pix-golpe/
  Cargo.toml, Cargo.lock        pacote Rust "pix-race" 0.1.0, edition 2021
  .env                          TYPESAFE_API_KEY, DEEPSEEK_API_KEY (não versionar)
  README.md                     visão geral, como rodar, números medidos
  SPEC.md                       especificação compartilhada Claude/Codex (262 linhas)
  AGENTS.md, CLAUDE.md          instruções do Reversa (instalador)
  BRAINSTORMING/                brainstorm que originou o projeto
  docs/                         2 screenshots (tela-corrida.png 1920x5657, relatorio-acuracia.png 1920x1080)
  output/pdf/                   pix-golpe-explicacao.pdf (guia do projeto)
  src/lib.rs                    expõe módulos data, graph, jev
  src/data.rs                   formatos e leitura de data/* (134 linhas)
  src/graph.rs                  grafo + algoritmo de rastreio (365 linhas)
  src/jev.rs                    cliente HTTP do Jev (148 linhas)
  src/bin/gerar_dados.rs        gerador do dataset sintético (274 linhas)
  src/bin/trace.rs              CLI: rastreia uma chave ou --todas (42 linhas)
  src/bin/server.rs             axum: HTTP + WebSocket + lado Rust (461 linhas)
  static/index.html             front-end em arquivo único, embutido no binário (1606 linhas)
  py-worker/worker.py           lado Python: WS + DeepSeek + rastreio (331 linhas)
  py-worker/trace.py            porte puro-Python de graph.rs (275 linhas)
  py-worker/deepseek.py         cliente DeepSeek (186 linhas)
  py-worker/requirements.txt    websockets, httpx, truststore
  data/                         dataset gerado (ver seção 6)
  target/                       build do cargo (release presente)
  tmp/pdfs/                     vazio
```

Total de arquivos-fonte: 7 `.rs`, 3 `.py`, 1 `.html`. Sem `.git` (projeto não versionado). Sem Dockerfile, sem CI/CD, sem testes automatizados.

## 3. Linguagens 🟢

| Linguagem | Arquivos | Linhas | Papel |
|---|---|---|---|
| Rust 2021 (rustc 1.88.0) | 7 | 1.427 | núcleo: gerador, grafo, cliente Jev, servidor |
| Python 3.12.0 | 3 | 792 | lado espelho: worker, cliente DeepSeek, rastreio puro |
| HTML/CSS/JS | 1 | 1.606 | interface, sem build, sem CDN |

Linguagem principal: **Rust**.

## 4. Pontos de entrada 🟢

| Binário / script | Arquivo | O que faz |
|---|---|---|
| `cargo run --release --bin gerar-dados` | `src/bin/gerar_dados.rs:122` | gera `data/*` com `ChaCha8Rng` seed 42 |
| `cargo run --release --bin server` | `src/bin/server.rs:143` | sobe axum na porta 8080, embute `static/index.html`, spawna `python py-worker/worker.py` (salvo `PIX_NO_WORKER=1`) |
| `cargo run --release --bin trace -- <chave>` ou `--todas` | `src/bin/trace.rs:8` | rastreio pela CLI, JSON |
| `python py-worker/worker.py` | `py-worker/worker.py:319` | conecta em `ws://127.0.0.1:8080/ws/worker`, reconecta a cada 2 s |
| `python py-worker/trace.py <chave>` ou `--todas` | `py-worker/trace.py:234` | rastreio pela CLI, JSON idêntico ao Rust |
| `python py-worker/deepseek.py` | `py-worker/deepseek.py:162` | teste manual do cliente DeepSeek |

Rotas HTTP (`src/bin/server.rs:209-212`): `GET /` (index), `GET /ws` (browser), `GET /ws/worker` (worker Python).

Variáveis de ambiente: `TYPESAFE_API_KEY` (`src/jev.rs:101`), `DEEPSEEK_API_KEY` (`py-worker/deepseek.py:43`), `PIX_STEP_MS` (padrão 2500, `server.rs:176`), `PIX_NO_WORKER` (`server.rs:199`). Carregadas via `dotenvy` (procura `.env` para cima).

## 5. Integrações externas 🟢

| Serviço | Endpoint | Modelo | Custo no código |
|---|---|---|---|
| TypeSafe AI (Jev) | `POST https://api.typesafe.ai/v1/systemone` | `jev-latest` | US$ 0,042 / 1M tokens de entrada, saída grátis |
| DeepSeek | `POST https://api.deepseek.com/chat/completions` | `deepseek-chat` (resolve para `deepseek-flash`) | US$ 0,28 / 1M entrada + US$ 0,42 / 1M saída (estimado, 3 tentativas) |

## 6. Bases de dados (arquivos em `data/`) 🟢

Não há SGBD. A "base" é um conjunto de arquivos gerados uma vez pelo `gerar-dados` e carregados inteiros em memória por cada lado no start. Tamanhos medidos em disco em 2026-09-21 15:08:

| Arquivo | Formato | Tamanho | Registros | Conteúdo |
|---|---|---|---|---|
| `transacoes.bin` | binário little-endian, cabeçalho `PIX1` + u32 n_contas + u32 n_transacoes, registros de 16 bytes (u32 origem, destino, valor_centavos, ts) ordenados por ts | **159.496.188 bytes (152,1 MiB)** | **9.968.511 transações** entre **1.000.000 contas** | histórico de 10 dias (ts em segundos, 0..864.000) |
| `mensagens.jsonl` | JSON por linha | 188.934 bytes | 1.000 mensagens (75 golpes, 925 legítimas) | id, ts, remetente, texto, chave, golpe_real |
| `chaves.json` | JSON objeto | 26.999 bytes | 965 pares (40 de quadrilha + 925 legítimas) 🟢 medido | chave Pix → id da conta |
| `meta.json` | JSON | 35.665 bytes | 2.000 hubs, 40 quadrilhas | verdade de referência (n_contas, n_transacoes, hubs, quadrilhas com laranjas 12 a 18 e 2 contas de saque) |
| `trace_ref.jsonl` | JSON por linha | 10.557 bytes | 40 rastreios | saída de referência do `trace --todas` (Rust) |

Conferência do binário: 12 bytes de cabeçalho + 9.968.511 × 16 = 159.496.188 bytes, bate com o tamanho em disco. 🟢

Constantes do gerador (`src/bin/gerar_dados.rs:11-17`): `N_CONTAS = 1_000_000`, `N_HUBS = 2_000`, `DIAS = 10`, `N_TX_NORMAIS = 9_500_000`, `N_QUADRILHAS = 40`, `N_MSG_GOLPE = 75`, `N_MSG_LEGIT = 925`.

**⚠️ Divergência documental (resolvida):** `SPEC.md` seção 1 e o PDF (página 3) descrevem **100.000 contas, ~1,27 milhão de transações e 200 hubs**. O código e os dados em disco têm **1.000.000 contas, 9.968.511 transações e 2.000 hubs**. O usuário confirmou em 2026-09-22 que vale o código 🟢; SPEC, README ("1,3 milhão") e PDF estão desatualizados. Spec dedicada em `volumetria-das-bases/`.

Memória em runtime: cada lado carrega o grafo inteiro (listas de adjacência de saída + grau_in). Medido em 2026-09-21 (ver `volumetria-das-bases/`): Python 1.668 MB residentes após a carga (4,2 s) 🟢; Rust estimado ≈ 170 MB de CSR estável, carga 328 ms 🟡/🟢. O evento `status` reporta `nodes`, `edges`, `load_ms`, `memory_mb`.

## 7. Testes 🟢

Nenhum `#[test]`, nenhum pytest. A única verificação é manual e determinística: `cargo run --bin trace -- --todas` versus `python py-worker/trace.py --todas`, comparados com `fc`, igualdade bit a bit nas 40 quadrilhas (README). `data/trace_ref.jsonl` guarda a referência.

## 8. CI/CD, Docker, build 🟢

Ausentes. Build local com `cargo` (perfil release `opt-level = 3`). `target/release/` já contém `gerar-dados.exe` e `server`.

## 9. Interface 🟢

Arquivo único `static/index.html`, tema escuro fixo (`color-scheme: dark`), frame de 1920px pensado para gravação 16:9, fonte "Segoe UI". Cores por lado: Jev rosa `#ff2d95`, DeepSeek azul `#6985f6`. Controles: Iniciar/Reiniciar, ritmo (Narrado 4 s / Normal), Parar, Relatório de acurácia. `?mock=1` gera eventos falsos sem servidor. Screenshots em `docs/`.

## 10. Módulos identificados

| Módulo | Arquivos | Responsabilidade |
|---|---|---|
| `data` | `src/data.rs` | formatos, leitura/escrita de `data/*` |
| `gerar-dados` | `src/bin/gerar_dados.rs` | gerador sintético com semente fixa |
| `graph` | `src/graph.rs`, `py-worker/trace.py` | grafo em memória e rastreio (BFS temporal, suspeição, propagação de rótulos, classificação) |
| `jev` | `src/jev.rs` | cliente TypeSafe AI, perguntas tipadas, veredito, custo |
| `deepseek` | `py-worker/deepseek.py` | cliente DeepSeek JSON mode, retries, custo |
| `server` | `src/bin/server.rs` | axum, protocolo WebSocket, corrida, lado Rust, relatório de acurácia, truth |
| `worker` | `py-worker/worker.py` | lado Python: WS, concorrência 8, rastreio serializado |
| `frontend` | `static/index.html` | tela dividida, celular, grafo radial, placar, relatório |
| `trace-cli` | `src/bin/trace.rs`, `py-worker/trace.py` (main) | verificação de igualdade dos algoritmos |
