# Dependências: pix-golpe

> Gerado pelo Scout (Reversa) em 2026-09-21. Versões resolvidas lidas de `Cargo.lock` e do ambiente Python. 🟢 CONFIRMADO salvo indicação.

## Toolchain

| Ferramenta | Versão | Fonte |
|---|---|---|
| rustc / cargo | 1.88.0 | `rustc --version` |
| Rust edition | 2021 | `Cargo.toml` |
| Python | 3.12.0 | `python --version` |

## Rust (`Cargo.toml` → `Cargo.lock`)

| Crate | Declarado | Resolvido | Uso |
|---|---|---|---|
| serde (derive) | 1 | 1.0.229 | structs de dados e protocolo |
| serde_json | 1 | 1.0.151 | JSON dos eventos, meta, chaves |
| tokio (full) | 1 | 1.53.1 | runtime async, spawn do worker |
| axum (ws) | 0.7 | 0.7.9 | HTTP + WebSocket (`tokio-tungstenite` 0.24.0, `hyper` 1.11.1 transitivos) |
| futures | 0.3 | 0.3.34 | split de streams WS |
| reqwest (json) | 0.12 | 0.12.28 | cliente HTTP do Jev |
| dotenvy | 0.15 | 0.15.7 | carga de `.env` |
| anyhow | 1 | 1.0.104 | erros |
| rand | 0.8 | 0.8.8 | gerador |
| rand_chacha | 0.3 | 0.3.1 | `ChaCha8Rng` seed 42 (reprodutibilidade) |
| rand_distr | 0.4 | 0.4.3 | lognormal dos valores |
| memory-stats | 1 | 1.2.0 | RSS no status 🟡 (uso a confirmar no Archaeologist) |

Perfil release: `opt-level = 3`.

## Python (`py-worker/requirements.txt`, sem pin)

| Pacote | Instalado | Uso |
|---|---|---|
| websockets | 15.0.1 | cliente WS (`websockets.asyncio.client.connect`) |
| httpx | 0.28.1 | cliente HTTP async do DeepSeek |
| truststore | instalado 🟡 | TLS com store do sistema (Windows) |

Regra do vídeo: **Python puro, sem numpy** no rastreio.

## Serviços externos

| Serviço | Autenticação | Env |
|---|---|---|
| TypeSafe AI `api.typesafe.ai/v1/systemone` | Bearer | `TYPESAFE_API_KEY` |
| DeepSeek `api.deepseek.com/chat/completions` | Bearer | `DEEPSEEK_API_KEY` |

## Front-end

Sem dependências: HTML/CSS/JS puro, sem build, sem CDN (`static/index.html`, embutido no binário via `include_str!`).

## Riscos

- `requirements.txt` sem versões fixas: `websockets` 15 mudou a API async (`websockets.asyncio.client`), versões antigas quebram o worker. 🟡
- Sem lockfile Python. 🟢
- Preços das APIs são constantes no código, sem verificação contra tabela atual. 🟢
