# Catálogo de Nós N8N e Mapeamento Python

Referência rápida usada pelo `reversa-n8n` para interpretar tipos de nó e sugerir bibliotecas Python equivalentes. Não é exaustivo: cobre os nós mais comuns. Quando o tipo do nó não estiver listado, deduza pelo nome (`type` segue o padrão `n8n-nodes-base.<servico>` ou `@n8n/n8n-nodes-langchain.<servico>`) e pelo `parameters`.

## Convenções

- **Tipo no JSON**: campo `type` do nó
- **Significado semântico**: o que o nó representa em termos de negócio
- **Python**: biblioteca recomendada e padrão de uso

---

## 1. Triggers (entrada do workflow)

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.webhook` | Endpoint HTTP que dispara o fluxo | FastAPI ou Flask. Rota POST/GET com `parameters.path` |
| `n8n-nodes-base.scheduleTrigger` | Disparo periódico (cron) | APScheduler (`BlockingScheduler`) ou systemd timer |
| `n8n-nodes-base.cron` | Cron clássico (versões antigas) | APScheduler ou crontab |
| `n8n-nodes-base.intervalTrigger` | Loop de tempo fixo | `while True: ... time.sleep(N)` ou APScheduler |
| `n8n-nodes-base.manualTrigger` | Execução manual | Script CLI (Typer, argparse) |
| `n8n-nodes-base.emailReadImap` | Leitura de caixa IMAP | `imapclient` + `email` |
| `n8n-nodes-base.executeWorkflowTrigger` | Sub-workflow chamado por outro | Função Python invocável |
| `n8n-nodes-base.errorTrigger` | Disparo em erro de outro workflow | Hook de exceção, decorator de erro |

Triggers de serviços (padrão `<servico>Trigger`): mapeiam para webhooks ou polling no SDK do serviço (ex: `slackTrigger` vira webhook do Slack ou polling via `slack-sdk`).

---

## 2. HTTP e APIs

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.httpRequest` | Chamada HTTP genérica | `httpx` (recomendado, suporta sync e async) ou `requests` |
| `n8n-nodes-base.respondToWebhook` | Resposta a webhook recebido | Return da rota FastAPI/Flask |
| `n8n-nodes-base.graphql` | Query GraphQL | `gql` ou `httpx` direto |
| `n8n-nodes-base.webhook` (output) | Confirmação de webhook | Response da rota |

---

## 3. Lógica e fluxo

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.if` | Condicional binária | `if/else` |
| `n8n-nodes-base.switch` | Multi-branch por valor | `match/case` (Python 3.10+) ou `if/elif` |
| `n8n-nodes-base.merge` | Junção de ramos paralelos | Combinação de listas, `dict.update`, `pandas.concat` |
| `n8n-nodes-base.splitInBatches` | Processamento em lotes | `itertools.batched` (3.12+) ou loop manual |
| `n8n-nodes-base.itemLists` | Operações de lista (split, agregação) | List comprehension, `itertools` |
| `n8n-nodes-base.wait` | Espera entre passos | `time.sleep(s)` ou `await asyncio.sleep(s)` |
| `n8n-nodes-base.noOp` | Passagem direta | `pass` ou função identidade |
| `n8n-nodes-base.stopAndError` | Interrompe com erro | `raise Exception(...)` |
| `n8n-nodes-base.executeWorkflow` | Chama outro workflow | Chamada de função/módulo Python |

---

## 4. Manipulação de dados

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.set` | Define valores em campos | Atribuição em dict |
| `n8n-nodes-base.editFields` | Edita estrutura do item | `dict.update`, list comp, dataclasses |
| `n8n-nodes-base.removeDuplicates` | Remove duplicatas | `set()`, `dict.fromkeys()`, `pandas.drop_duplicates` |
| `n8n-nodes-base.aggregate` | Agrupamento e agregação | `itertools.groupby` ou `pandas.groupby` |
| `n8n-nodes-base.dateTime` | Manipulação de datas | `datetime`, `dateutil`, `arrow`, `pendulum` |
| `n8n-nodes-base.crypto` | Hash, criptografia | `hashlib`, `hmac`, `cryptography` |
| `n8n-nodes-base.compression` | Zip, gzip | `zipfile`, `gzip`, `tarfile` |
| `n8n-nodes-base.xml` | Parse/build XML | `xml.etree.ElementTree`, `lxml` |
| `n8n-nodes-base.html` | Parse HTML | `beautifulsoup4`, `lxml` |
| `n8n-nodes-base.markdown` | Conversão Markdown | `markdown`, `mistune` |
| `n8n-nodes-base.spreadsheetFile` | Leitura/escrita XLSX/CSV | `openpyxl`, `pandas`, `csv` |

---

## 5. Execução de código

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.function` | Código JS arbitrário (legacy) | Função Python pura. Ler `parameters.functionCode` e descrever a lógica |
| `n8n-nodes-base.functionItem` | JS aplicado por item | List comprehension ou `map()` |
| `n8n-nodes-base.code` | Código JS ou Python (versão nova) | Função Python pura. Verificar `parameters.language` |

Ao traduzir Function/Code nodes para o `design.md`: descrever a lógica em pseudocódigo, não copiar o JS literal. O Python equivalente deve ser idiomático.

---

## 6. Bancos de dados

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.postgres` | Postgres | `psycopg[binary]` (v3) ou `asyncpg` |
| `n8n-nodes-base.mysql` | MySQL/MariaDB | `pymysql` ou `mysql-connector-python`, `aiomysql` |
| `n8n-nodes-base.mongoDb` | MongoDB | `pymongo` ou `motor` (async) |
| `n8n-nodes-base.redis` | Redis | `redis-py` (suporta sync e async) |
| `n8n-nodes-base.supabase` | Supabase | `supabase-py` |
| `n8n-nodes-base.microsoftSql` | SQL Server | `pyodbc` ou `pymssql` |
| `n8n-nodes-base.snowflake` | Snowflake | `snowflake-connector-python` |
| `n8n-nodes-base.questDb` | QuestDB | `psycopg` (compatível com PG wire) |

ORMs sugeridos quando o workflow tiver muitas operações relacionais: `SQLAlchemy 2.x` ou `SQLModel`.

---

## 7. Comunicação

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.emailSend` | Envio de email SMTP | `smtplib` + `email`, `yagmail`, `aiosmtplib` |
| `n8n-nodes-base.gmail` | Gmail (API) | `google-api-python-client` |
| `n8n-nodes-base.slack` | Slack (mensagens, canais) | `slack-sdk` |
| `n8n-nodes-base.discord` | Discord | `discord.py` ou webhook direto via `httpx` |
| `n8n-nodes-base.telegram` | Telegram Bot | `python-telegram-bot` ou `aiogram` |
| `n8n-nodes-base.whatsApp` | WhatsApp Business API | `httpx` direto (não há SDK oficial Python maduro) |
| `n8n-nodes-base.twilio` | SMS/voz Twilio | `twilio` SDK |
| `n8n-nodes-base.sendGrid` | SendGrid | `sendgrid` SDK |
| `n8n-nodes-base.mailchimp` | Mailchimp | `mailchimp-marketing` |

---

## 8. IA e LLM

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.openAi` ou `@n8n/n8n-nodes-langchain.openAi` | OpenAI (chat, embeddings, imagens) | `openai` SDK |
| `@n8n/n8n-nodes-langchain.lmChatAnthropic` | Anthropic Claude | `anthropic` SDK |
| `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` | Google Gemini | `google-generativeai` |
| `@n8n/n8n-nodes-langchain.embeddingsOpenAi` | Embeddings | `openai` SDK |
| `@n8n/n8n-nodes-langchain.vectorStorePinecone` | Pinecone | `pinecone-client` |
| `@n8n/n8n-nodes-langchain.vectorStoreSupabase` | Supabase pgvector | `supabase-py` + `pgvector` |
| `@n8n/n8n-nodes-langchain.vectorStoreQdrant` | Qdrant | `qdrant-client` |
| `@n8n/n8n-nodes-langchain.agent` | Agent LangChain | `langchain` ou `langgraph` |
| `@n8n/n8n-nodes-langchain.chainLlm` | Chain básica | Chamada direta ao SDK do LLM |
| `n8n-nodes-base.huggingFace` | Hugging Face | `transformers`, `huggingface_hub` |

Para projetos novos, considere se o LangChain/LangGraph é necessário ou se uma chamada direta ao SDK do LLM é mais simples.

---

## 9. Arquivos e armazenamento em nuvem

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.readBinaryFile` | Leitura de arquivo local | `open(path, 'rb')` |
| `n8n-nodes-base.writeBinaryFile` | Escrita de arquivo local | `open(path, 'wb')` |
| `n8n-nodes-base.s3` | AWS S3 | `boto3` |
| `n8n-nodes-base.googleDrive` | Google Drive | `google-api-python-client` + `google-auth` |
| `n8n-nodes-base.googleCloudStorage` | GCS | `google-cloud-storage` |
| `n8n-nodes-base.dropbox` | Dropbox | `dropbox` SDK |
| `n8n-nodes-base.ftp` | FTP/SFTP | `ftplib` ou `paramiko` |
| `n8n-nodes-base.ssh` | SSH | `paramiko` ou `fabric` |
| `n8n-nodes-base.box` | Box | `boxsdk` |

---

## 10. Produtividade e SaaS

| Tipo no JSON | Significado | Python |
|---|---|---|
| `n8n-nodes-base.googleSheets` | Google Sheets | `gspread` ou `google-api-python-client` |
| `n8n-nodes-base.googleCalendar` | Google Calendar | `google-api-python-client` |
| `n8n-nodes-base.googleDocs` | Google Docs | `google-api-python-client` |
| `n8n-nodes-base.airtable` | Airtable | `pyairtable` |
| `n8n-nodes-base.notion` | Notion | `notion-client` |
| `n8n-nodes-base.trello` | Trello | `py-trello` ou `httpx` direto |
| `n8n-nodes-base.asana` | Asana | `asana` SDK |
| `n8n-nodes-base.jira` | Jira | `jira` SDK ou `atlassian-python-api` |
| `n8n-nodes-base.gitHub` | GitHub | `PyGithub` ou `httpx` direto |
| `n8n-nodes-base.gitLab` | GitLab | `python-gitlab` |
| `n8n-nodes-base.hubspot` | HubSpot | `hubspot-api-client` |
| `n8n-nodes-base.salesforce` | Salesforce | `simple-salesforce` |
| `n8n-nodes-base.shopify` | Shopify | `ShopifyAPI` |
| `n8n-nodes-base.stripe` | Stripe | `stripe` SDK |

---

## 11. Credenciais e autenticação

Mapeamento de tipos de credencial do N8N para padrões Python:

| Tipo de credencial N8N | Significado | Padrão Python |
|---|---|---|
| `httpHeaderAuth` | Header customizado (geralmente API key) | Variável de ambiente, header em todas as chamadas |
| `httpBasicAuth` | Basic Auth | Tupla `(user, pass)` em `httpx`, vindas de env vars |
| `httpQueryAuth` | API key na querystring | Param fixo em todas as chamadas |
| `oAuth2Api` | OAuth2 (com refresh) | `authlib` ou `requests-oauthlib`, persistir refresh token |
| `oAuth1Api` | OAuth1 | `requests-oauthlib` |
| `<servico>Api` (ex: `slackApi`, `googleApi`) | Credencial específica do serviço | Seguir SDK oficial do serviço |

Recomendação geral: nunca hardcodar. Usar `pydantic-settings` ou `python-dotenv` para ler de `.env`. Para produção, usar secret manager (AWS Secrets Manager, HashiCorp Vault, etc.).

---

## 12. Padrões arquiteturais sugeridos

Baseado no trigger principal:

| Trigger | Arquitetura Python recomendada |
|---|---|
| Webhook | FastAPI (assíncrono, validação com Pydantic) |
| Schedule/Cron | Script standalone com APScheduler ou systemd timer |
| Manual | CLI com Typer ou argparse |
| Email IMAP | Worker daemon com loop de polling |
| Trigger de SaaS (polling) | Worker assíncrono com asyncio |
| Multi-trigger | FastAPI com endpoints + APScheduler embutido |

Considerações adicionais:

- Workflow com muitas chamadas HTTP em paralelo: usar `asyncio` + `httpx.AsyncClient`
- Workflow com batches longos: usar Celery, RQ ou Dramatiq
- Workflow com estado entre execuções: persistir em Postgres/Redis (não em memória)
- Workflow crítico: adicionar observabilidade desde o início (`structlog`, OpenTelemetry)

---

## 13. Tratamento de erros e retries

Comportamentos comuns no N8N e equivalente Python:

| Comportamento N8N | Python |
|---|---|
| `continueOnFail` no nó | `try/except` que loga e segue |
| `retryOnFail` com tentativas | `tenacity` (decorator `@retry`) |
| `errorTrigger` (workflow de erro) | Handler global de exceção, alerta via Slack/email |
| Timeout em HTTP request | `httpx.Timeout(...)` explícito |
| Wait between retries | Backoff exponencial via `tenacity` |

---

## 14. Observabilidade

Quando o workflow tem muitos passos ou é crítico, sugerir no `design.md`:

- Logs estruturados (`structlog` ou `loguru`)
- Tracing distribuído (`opentelemetry-api` + exporter)
- Métricas (`prometheus-client`)
- Health check endpoint (FastAPI)
- Sentry para captura de erros

---

## Notas finais

- Este catálogo cobre os nós mais comuns. Se aparecer um tipo desconhecido, registrar como 🟡 INFERIDO no spec e pedir esclarecimento ao usuário.
- Versões dos nós (`typeVersion`) podem mudar parâmetros internos. Verificar se a estrutura de `parameters` bate com a versão.
- Nós comunitários (que começam com `n8n-nodes-<comunidade>`) podem não ter equivalente Python direto. Tratar caso a caso.
