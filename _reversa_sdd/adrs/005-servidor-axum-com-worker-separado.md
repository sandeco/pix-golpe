# ADR-005: Servidor axum único com lado Rust embutido e worker Python como processo filho

**Status:** aceita. **Confiança:** 🟢 (SPEC §4, `server.rs`, `worker.py`).

## Contexto

Precisa-se de uma fonte única de verdade para a corrida (ordem das mensagens, run_id, ritmo), um canal em tempo real para o browser e dois lados de linguagens diferentes.

## Decisão

- Um binário Rust (`server`) serve a página, mantém o estado da corrida e executa o lado Rust no próprio processo.
- O lado Python é um processo separado, iniciado pelo servidor (`python py-worker/worker.py`, `kill_on_drop`), que se conecta em `/ws/worker` e recebe os mesmos eventos de controle. `PIX_NO_WORKER=1` desliga.
- Protocolo de eventos JSON com `type`, `side`, `run_id`; o servidor injeta `side="python"` e `truth`.
- Broadcast para browsers (`tokio::broadcast` 8192); canal dedicado para o worker.
- Invalidação por `run_id` crescente em vez de cancelamento de tarefas.

## Alternativas consideradas

- Dois servidores: complicaria sincronizar o início e o placar.
- Worker Python iniciado manualmente: previsto (`PIX_NO_WORKER`), mas o padrão é automático para simplificar a gravação.
- Cancelar tasks em `reset`: rejeitado no worker ("não cancelar to_thread: a thread continuaria enquanto o lock seria liberado"; invalidar identidade descarta resultados).

## Consequências

- Página lida do disco a cada request (edição ao vivo da tela), apesar de o SPEC dizer `include_str!`.
- Bind em `0.0.0.0` sem autenticação (ver `permissions.md`).
- Reconexão automática do worker e do browser; um worker novo substitui o antigo no slot.
