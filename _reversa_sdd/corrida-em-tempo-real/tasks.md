# Corrida em tempo real, Tarefas de Implementação

> Unit `corrida-em-tempo-real`. Reimplementação a partir de `src/bin/server.rs` e `py-worker/worker.py`.

## Pré-requisitos
- [ ] Units `decisao-por-ia`, `rastreio-no-grafo` e `geracao-de-dados` disponíveis
- [ ] `.env` com as duas chaves; Python 3.12 com `websockets`, `httpx`, `truststore`
- [ ] Contrato em `contracts.md` desta unit

## Tarefas

- [ ] T-01, Boot do servidor: dados, grafo, `load_ms`, `memory_mb`, `truth`, Jev, aquecimento, `App`
  - Origem no legado: `src/bin/server.rs:143-194`
  - Critério de pronto: logs de boot; `rust_status` = `ready` com os 5 campos
  - Confiança: 🟢

- [ ] T-02, Spawn do worker Python com `kill_on_drop`, respeitando `PIX_NO_WORKER`
  - Origem no legado: `src/bin/server.rs:196-207`
  - Critério de pronto: processo filho morre com o servidor; variável desliga o spawn
  - Confiança: 🟢

- [ ] T-03, Router: `GET /` (arquivo do disco), `/ws`, `/ws/worker`; bind `0.0.0.0:8080`
  - Origem no legado: `src/bin/server.rs:209-234`
  - Critério de pronto: curl retorna o HTML; upgrades funcionam
  - Confiança: 🟢

- [ ] T-04, `handle_browser`: status iniciais, broadcast → socket, socket → comandos
  - Origem no legado: `src/bin/server.rs:236-259`
  - Critério de pronto: dois browsers recebem os mesmos eventos
  - Confiança: 🟢

- [ ] T-05, `comando_browser` e `pace_de`
  - Origem no legado: `src/bin/server.rs:261-300`
  - Critério de pronto: tabela de comandos de `contracts.md` reproduzida
  - Confiança: 🟢

- [ ] T-06, `run`: concorrência, evento `run`, despacho de todas as mensagens, join, `done`
  - Origem no legado: `src/bin/server.rs:302-334`
  - Critério de pronto: `done` com p50/p95 nearest-rank e `total_ms`
  - Confiança: 🟢

- [ ] T-07, `processar`: semáforo, decisão, `run_id`, erro, veredito, stats, ritmo, rastreio, `truth`
  - Origem no legado: `src/bin/server.rs:336-402`
  - Critério de pronto: cenários Gherkin de `requirements.md`
  - Confiança: 🟢

- [ ] T-08, `handle_worker`: slot, `hello`, injeção de `side`, guarda de `status`, registro de `decision`, `enrich_truth`, limpeza do slot
  - Origem no legado: `src/bin/server.rs:404-461`
  - Critério de pronto: worker novo substitui o antigo sem marcar `offline` indevido
  - Confiança: 🟢

- [ ] T-09, `enrich_truth` e `registrar_verdict`
  - Origem no legado: `src/bin/server.rs:81-83,117-139`
  - Critério de pronto: `truth` correto para chave de quadrilha e zeros para chave legítima
  - Confiança: 🟢

- [ ] T-10, Worker: `serve_forever` com reconexão e cancelamento final
  - Origem no legado: `py-worker/worker.py:298-317`
  - Critério de pronto: servidor reiniciado → worker reconecta em ≤ 2 s
  - Confiança: 🟢

- [ ] T-11, Worker: `parse_event` e `handle_raw` (erro de parse com `id` conta na corrida)
  - Origem no legado: `py-worker/worker.py:55-76,173-196`
  - Critério de pronto: casos da tabela de validação
  - Confiança: 🟢

- [ ] T-12, Worker: `hello` (carga em thread, memória, aquecimento, `loading`/`ready`)
  - Origem no legado: `py-worker/worker.py:146-172`
  - Critério de pronto: `ready` com `nodes = 1_000_000`; reconexão não recarrega
  - Confiança: 🟢

- [ ] T-13, Worker: `handle_event` (`run`, `reset`, `stop`, `pace`, `message`) e `Run`
  - Origem no legado: `py-worker/worker.py:85-109,198-226`
  - Critério de pronto: `run` recria semáforo; ids repetidos ignorados
  - Confiança: 🟢

- [ ] T-14, Worker: `process_message`, `trace_for_message`, `emit`, `finish_message`, `maybe_done`
  - Origem no legado: `py-worker/worker.py:129-144,233-296`
  - Critério de pronto: `done` sai mesmo com erros; `emit` injeta `side` e `run_id`; `allow_nan=False`
  - Confiança: 🟢

- [ ] T-15, `memoria_mb` (psutil → Win32 `GetProcessMemoryInfo` → `resource`)
  - Origem no legado: `py-worker/worker.py:24-47`
  - Critério de pronto: valor numérico no Windows sem psutil
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Corrida completa em `?mock`-less com modelos mockados (HTTP fake) e worker real: 1.000 `decision` por lado e 2 `done`
- [ ] TT-02, `stop` no meio: nenhum evento tardio da corrida antiga chega ao browser
- [ ] TT-03, `pace` ao vivo muda o intervalo entre decisões
- [ ] TT-04, Worker: `message` malformado, `run_id` antigo, `id` duplicado, `hello` sem `data_dir`
- [ ] TT-05, Worker reconexão após queda do servidor
- [ ] TT-06, `enrich_truth` com chave de quadrilha e com chave legítima
- [ ] TT-07, `percentil` nearest-rank em listas de 1, 2 e 1.000 elementos, igual nos dois lados

## Ordem Sugerida
1. T-03/T-04/T-05 (transporte e comandos) → T-06/T-07 (lado Rust) → T-09 → T-08 (worker no servidor) → T-10..T-15 (worker Python) → T-01/T-02 (boot completo).
2. TT-01 só após tudo; TT-04 junto com T-11.

## Lacunas Pendentes (🔴)
Nenhuma específica desta unit; Q-002 (latência com retry) pertence a `decisao-por-ia`.
