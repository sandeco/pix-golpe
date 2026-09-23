# Decisão por IA, Design Técnico

> Unit `decisao-por-ia`. Fonte: `src/jev.rs`, `py-worker/deepseek.py`. 🟢 salvo indicação.

## Interface

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `JevClient::from_env` | `()` | `Result<JevClient>` | exige `TYPESAFE_API_KEY`; timeout 30 s |
| `JevClient::classificar` | `(remetente: &str, texto: &str)` async | `Result<Decisao>` | 3 retries 429/529 |
| `jev::verdict` | `(golpe: f64)` | `&'static str` | `golpe` / `ok` / `revisar` |
| `jev::questions` | `()` | `Value` | 4 perguntas tipadas |
| `Decisao::verdict` / `cost_usd` | `(&self)` | `&str` / `f64` | |
| `DeepSeekClient.__init__` | `(api_key=None, *, transport=None)` | | httpx async, TLS truststore |
| `DeepSeekClient.classificar` | `(remetente, texto)` async | `dict` | 3 tentativas 429/5xx |
| `parse_response` | `(payload: dict, latency_ms: float)` | `dict` | validação estrita |
| `verdict(golpe)` / `cost_usd(tin, tout)` | | `str` / `float` | |
| `load_api_key(start=None)` | | `str` | env, depois `.env` em cwd e pais |

Estrutura `Decisao` (Rust) e dict (Python):

| Campo | Rust | Python | Origem |
|---|---|---|---|
| golpe | f64 | float | `answers.golpe.noul` / JSON `golpe` |
| tipo | String | str | `answers.tipo.choice` / JSON `tipo` |
| tipo_confianca | f64 | (ausente) | `answers.tipo.confidence` |
| urgencia | f64 (0..2) | float | `answers.urgencia.score` / JSON |
| pede_pix | f64 | float | `answers.pede_pix.noul` / JSON |
| tokens_in / tokens_out | u64 | int | `usage.input_tokens/output_tokens` (out default 0) / `usage.prompt_tokens/completion_tokens` |
| model | String | str | `model` da resposta |
| latency_ms | medido fora (`server.rs:338-340`) | dentro (`deepseek.py:145-148`) | |

## Fluxo Principal (Jev)
1. Body `{"model":"jev-latest","state":{"remetente","mensagem"},"questions":questions()}` (`jev.rs:111-115`).
2. `POST` com `bearer_auth`; loop de tentativas (`:117-146`).
3. 200 → desserializa `Resp{model, answers, usage}` → `Decisao`.
4. 429/529 e `tentativa < 3` → sleep `200·2^tentativa` ms → repete.
5. Outro status → `bail!("Jev respondeu {status}: {corpo}")`.

## Fluxo Principal (DeepSeek)
1. Body `{"model":"deepseek-flash","temperature":0,"response_format":{"type":"json_object"},"messages":[system SYSTEM_PROMPT, user "Remetente: r\nMensagem: t"]}` (`deepseek.py:136-143`).
2. Para `attempt` em 0..3: `POST`, mede `latency_ms`; 429/5xx com tentativas restantes → sleep `2^attempt` s → continua; senão `raise_for_status()` (`:144-153`).
3. `response.json()` → `parse_response(payload, latency_ms)` (`:154-158`).
4. `parse_response`: extrai `choices[0].message.content`, `usage`, `model`; `json.loads(content)`; exige dict com `golpe, tipo, urgencia, pede_pix`; numéricos finitos não-bool em [0,1], [0,2], [0,1]; `tipo ∈ TIPOS`; `model` str não vazia; tokens `int ≥ 0` (`:79-112`).
5. Esgotadas as tentativas → `RuntimeError("DeepSeek: tentativas esgotadas")`.

## Fluxos Alternativos
- **Chave ausente:** Rust `context("TYPESAFE_API_KEY não definida (ver .env na raiz)")`; Python `ValueError` após varrer `.env` (aceita `export`, aspas, `#` comentário).
- **`truststore` ausente:** `verify=True` padrão (`deepseek.py:16-21`).
- **`usage.output_tokens` ausente no Jev:** `#[serde(default)]` = 0.
- **CLI `deepseek.py` sem texto:** usa a primeira mensagem com `golpe_real` do dataset (só para escolher o exemplo).

## Dependências
- `reqwest` 0.12 (json), `serde_json`, `tokio::time::sleep`.
- `httpx` 0.28, `truststore`, `asyncio`.
- Unit `corrida-em-tempo-real` chama `classificar` sob semáforo e registra o veredito.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Estado em português, instruções/critérios em inglês (Jev é inglês primário) | `jev.rs:45-56`, brainstorm | 🟢 |
| `temperature 0` e JSON mode para comparabilidade | `deepseek.py:137-138` | 🟢 |
| Validação estrita em vez de "melhor esforço" | `deepseek.py:79-112` | 🟢 |
| Backoff diferente entre lados (ms vs s) | `jev.rs:140`, `deepseek.py:151` | 🟢 |
| Preços como constantes | `jev.rs:10`, `deepseek.py:24-25` | 🟢 |
| Pool de 8 conexões = concorrência de rajada | `deepseek.py:120` | 🟢 |

## Estado Interno
Clientes HTTP reutilizáveis (`reqwest::Client` clonável; `httpx.AsyncClient` com keepalive 60 s). Sem cache de respostas.

## Observabilidade
Nenhum log próprio; erros sobem como evento `error` (`server.rs:348`, `worker.py:283`). O CLI Python imprime o JSON da decisão.

## Riscos e Lacunas
- 🔴 Q-002: assimetria da latência com retry.
- 🟡 Preços podem estar defasados; nenhum aviso além de "estimado" para o DeepSeek.
- 🟡 Jev: status 5xx diferentes de 529 não são retentados.
- 🟢 Nenhum limite de taxa local; o Jev tem limite de 1200 req/min (brainstorm), suficiente para 8 em voo.
