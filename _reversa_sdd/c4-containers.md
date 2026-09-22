# C4 Nível 2: Containers

> Gerado pelo Architect (Reversa) em 2026-09-21. 🟢

```mermaid
C4Container
    title pix-golpe: containers
    Person(apresentador, "Apresentador")
    System_Boundary(pix, "pix-golpe") {
        Container(browser, "Tela (static/index.html)", "HTML/CSS/JS puro", "Tela dividida, grafo em canvas, relatório, modal, modo mock")
        Container(server, "Servidor (src/bin/server.rs)", "Rust, axum 0.7, tokio", "GET /, /ws, /ws/worker; orquestra a corrida; lado Rust: Jev + graph.rs; relatório; truth; spawn do worker")
        Container(worker, "Worker Python (py-worker/worker.py)", "Python 3.12, websockets, httpx", "Lado Python: DeepSeek + trace.py; rastreio serial em thread")
        Container(gerador, "Gerador (src/bin/gerar_dados.rs)", "Rust, rand_chacha", "Gera data/ com semente 42 (roda uma vez)")
        Container(cli, "CLIs de conferência", "trace.rs / trace.py / deepseek.py", "Rastreio por chave ou --todas; teste do DeepSeek")
        ContainerDb(data, "data/", "Arquivos", "transacoes.bin 152 MiB, mensagens.jsonl, chaves.json, meta.json, trace_ref.jsonl")
        ContainerDb(env, ".env", "Arquivo", "TYPESAFE_API_KEY, DEEPSEEK_API_KEY")
    }
    System_Ext(jev, "TypeSafe AI (Jev)")
    System_Ext(deepseek, "DeepSeek")
    Rel(apresentador, browser, "Usa", "http://localhost:8080")
    Rel(browser, server, "GET / e WebSocket /ws", "eventos JSON")
    Rel(server, worker, "spawn python worker.py; WebSocket /ws/worker", "hello, run, message, pace, stop, reset")
    Rel(worker, server, "status, decision, trace, error, done", "WebSocket")
    Rel(server, jev, "POST /v1/systemone", "HTTPS")
    Rel(worker, deepseek, "POST /chat/completions", "HTTPS")
    Rel(gerador, data, "escreve")
    Rel(server, data, "lê tudo no boot")
    Rel(worker, data, "lê transacoes.bin e chaves.json (data_dir do hello)")
    Rel(cli, data, "lê")
    Rel(server, env, "dotenvy")
    Rel(worker, env, "leitura manual")
```

## Comunicação

| De → Para | Canal | Conteúdo |
|---|---|---|
| Browser → Servidor | WS `/ws` | `start`, `pace`, `stop`, `report`, `reset` |
| Servidor → Browser | WS `/ws` (broadcast 8192) | `status`×2 no connect; `run`, `message`, `pace`, `stop`, `reset`, `decision`, `trace`(+truth), `error`, `done`, `report` |
| Servidor → Worker | WS `/ws/worker` (canal dedicado) | `hello {data_dir}`, `run`, `message`, `pace`, `stop`, `reset` |
| Worker → Servidor | WS `/ws/worker` | `status`, `decision`, `trace`, `error`, `done` (servidor injeta `side`) |
| Servidor → Jev | HTTPS | 4 perguntas tipadas |
| Worker → DeepSeek | HTTPS | chat JSON mode |

## Processos e portas

- `server`: porta 8080, bind `0.0.0.0`; roda o lado Rust no próprio runtime tokio (rastreio em `spawn_blocking`).
- `worker.py`: processo filho com `kill_on_drop`; conecta em `127.0.0.1:8080`.
- Nenhum outro serviço: sem banco, sem cache, sem fila.
