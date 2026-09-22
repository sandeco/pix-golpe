> Cópia local do catálogo consultivo. A fonte canônica fica em `templates/migration/catalogs/paradigm_catalog.md`.
> Esta cópia é instalada junto com o agente para que ele tenha acesso ao catálogo dentro do projeto do usuário, sem depender de localização do pacote npm.

# Paradigm Catalog (cópia local)

## Catálogo de paradigmas

### Procedural
- **Características**: funções top-level, fluxo linear em controllers, ausência de classes ou uso ornamental, dados como dicts/structs, side effects abertos.
- **Exemplos no legado**: scripts PHP clássicos, COBOL batch, sistemas Perl pré-OO, scripts shell.
- **Sinais em `_reversa_sdd/`**: domínio descrito como "funções", fluxos lineares em `process_flows`, ausência de aggregates explícitos.

### OO clássico
- **Características**: hierarquia de classes, herança forte, padrão Active Record, lógica acoplada aos modelos.
- **Exemplos no legado**: Rails monolítico, Django tradicional, Java EE pré-DI, .NET WebForms / clássico.
- **Sinais em `_reversa_sdd/`**: classes com responsabilidades amplas, herança em domain model, controllers anêmicos chamando métodos do modelo.

### OO com DI
- **Características**: containers de injeção, interfaces explícitas, padrão Repository / Service, separação clara entre camadas.
- **Exemplos no legado**: Spring moderno, .NET 6+, NestJS, Symfony moderno.
- **Sinais em `_reversa_sdd/`**: aggregates explícitos, interfaces de repositório, ausência de Active Record.

### Funcional
- **Características**: imutabilidade dominante, funções puras, composição, ausência de side effects implícitos, tipagem rica.
- **Exemplos no legado**: Haskell, Elm, F#, Scala funcional, Clojure.
- **Sinais em `_reversa_sdd/`**: tipos algébricos, ausência de classes, fluxo expresso como composição.

### Event-driven (assíncrono)
- **Características**: filas / tópicos, handlers desacoplados, ausência de fluxo linear, consistência eventual, idempotência explícita.
- **Exemplos no legado**: backends Node moderno orientado a fila, sistemas SQS / Kafka heavy, microsserviços assíncronos.
- **Sinais em `_reversa_sdd/`**: eventos no domain model, integrações via fila, processos de longa duração com retry.

### Actor model
- **Características**: atores isolados com mailbox, supervisão, isolamento de estado.
- **Exemplos no legado**: Erlang / Elixir / OTP, Akka.
- **Sinais em `_reversa_sdd/`**: processos supervisionados, mensagens entre atores.

### Dataflow
- **Características**: pipelines declarativos, transformações em fluxo, ausência de loops imperativos no domínio.
- **Exemplos no legado**: ETLs clássicos, Spark, Flink.
- **Sinais em `_reversa_sdd/`**: descrição em DAG, transformações em estágios.

## Mapeamento stack → paradigma natural

| Stack alvo | Paradigma natural | Alternativas viáveis | Notas |
|---|---|---|---|
| Node.js 20 (Fastify, Express, NestJS) | event-driven assíncrono | OO com DI (NestJS), funcional leve | runtime async-first; bloqueio CPU pesado vai para worker threads |
| Go (net/http, Echo, Fiber) | CSP / goroutines (event-driven leve) | procedural estruturado | concorrência via channels; OO simulada via interfaces |
| Rust (axum, Actix, tokio) | ownership / async funcional | event-driven | imutabilidade por default, segurança via tipos |
| Elixir / Phoenix | actor model (BEAM) | funcional | supervisão via OTP |
| Python moderno (FastAPI, Django 5) | OO com DI ou procedural rico | event-driven (Celery, asyncio) | escolha depende do framework |
| Kotlin (Spring Boot, Ktor) | OO com DI | event-driven (Reactor) | corrotinas habilitam async ergonômico |
| .NET 8 (ASP.NET Core, Minimal API) | OO com DI | event-driven (Channels, MediatR) | tradição OO + assincronismo first-class |
| Java moderno (Spring Boot 3, Quarkus) | OO com DI | event-driven (Project Reactor) | bibliotecas funcionais possíveis mas não dominantes |
| Ruby moderno (Rails 7, Hanami) | OO clássico (Rails) ou OO com DI (Hanami) | funcional leve (dry-rb) | Rails dita Active Record; Hanami é DI-heavy |
| TypeScript serverless (AWS Lambda, Cloudflare Workers) | event-driven | funcional | invocação por evento; cold start influencia design |

## Tabela de gaps típicos por par

| De → Para | Gap principal | Implicações concretas |
|---|---|---|
| procedural → event-driven | sincronia → assincronismo | resposta deixa de ser imediata; tratamento de erro vira retry/DLQ; idempotência obrigatória; ordem de eventos passa a importar |
| procedural → OO com DI | dados como dict → aggregates | invariantes ficam dentro de aggregates; lógica deixa de viver em controllers; dependências via interfaces |
| procedural → funcional | side effects abertos → puros + isolados | mutabilidade vira exceção; composição substitui sequência; tipos algébricos para estados |
| OO clássico → event-driven | fluxo síncrono → coreografia | ações deixam de ser atômicas; transações distribuídas viram sagas; consistência forte → eventual |
| OO clássico → OO com DI | herança → composição via interfaces | Active Record desaparece; persistência vira repositório; testes ganham mocks naturais |
| OO clássico → funcional | encapsulamento mutável → imutabilidade | métodos com efeito viram funções puras + atualização explícita; estado expresso como sequência de transformações |
| OO com DI → event-driven | comando síncrono → evento | retorno deixa de ser imediato; orquestração vira coreografia; ordem por chave |
| OO com DI → funcional | mocks → composição testável | DI deixa de ser por interface, vira por argumento de função |
| funcional → event-driven | composição síncrona → mensageria | latência aumenta; falha vira mensagem em DLQ; estado distribuído |
| event-driven → procedural síncrono | desnatural; só faz sentido para sistemas pequenos | colapsar handlers em chamadas diretas; perda de desacoplamento; consistência forte volta |
| dataflow → event-driven | DAG declarativa → coreografia mutável | controle fica menos previsível; ordem precisa ser garantida por chave |
| actor model → OO com DI | mensagens entre atores → chamadas síncronas | perda de isolamento de falha; supervisão precisa virar try/catch ou retry orquestrado |
