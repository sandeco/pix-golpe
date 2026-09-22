# Máquinas de estado: pix-golpe

> Gerado pelo Detective (Reversa) em 2026-09-21. 🟢 CONFIRMADO salvo indicação.

## 1. Corrida no servidor (`run_id` / `pace_ms`) 🟢

O servidor não guarda um enum de estado; a corrida "atual" é o `run_id` mais recente. Toda transição incrementa `run_id`, o que invalida tarefas em voo.

```mermaid
stateDiagram-v2
    [*] --> Ociosa : boot, run_id = 0
    Ociosa --> Correndo : start -> run_id+1, reset a todos, spawn run
    Correndo --> Correndo : pace -> pace_ms, broadcast pace
    Correndo --> Parada : stop -> run_id+1, stop a todos
    Correndo --> Ociosa : reset -> run_id+1, reset a todos
    Correndo --> Concluida : todas as tasks terminaram com run_id igual -> done rust
    Parada --> Correndo : start
    Parada --> Ociosa : reset
    Concluida --> Correndo : start
    Concluida --> Ociosa : reset
```

Gatilhos: comandos do browser (`server.rs:261-292`). `report` não muda estado; usa `verdicts` da corrida atual.

## 2. Mensagem em um lado 🟢

```mermaid
stateDiagram-v2
    [*] --> Despachada : evento message
    Despachada --> Decidindo : permit adquirido, chamada ao modelo
    Decidindo --> Erro : falha HTTP / JSON invalido -> evento error
    Decidindo --> Decidida : decision emitida (golpe | revisar | ok)
    Decidida --> Aguardando_ritmo : pace_ms > 0
    Aguardando_ritmo --> Encerrada : verdict != golpe
    Decidida --> Encerrada : verdict != golpe e pace 0
    Decidida --> Rastreando : verdict == golpe, trace_lock
    Aguardando_ritmo --> Rastreando : verdict == golpe
    Rastreando --> Rastreada : evento trace (+ truth pelo servidor)
    Rastreando --> Erro : chave desconhecida / grafo ausente (Python)
    Rastreada --> Encerrada
    Erro --> Encerrada
    Encerrada --> [*]
    Despachada --> Descartada : run_id mudou
    Decidindo --> Descartada : run_id mudou
    Rastreando --> Descartada : run_id mudou
```

Rust: `server.rs:336-402`. Python: `worker.py:246-286` (o `finally` sempre chama `finish_message`, então Erro também conta para `done`).

## 3. Veredito de uma mensagem (tela) 🟢

```mermaid
stateDiagram-v2
    [*] --> waiting : Aguardando...
    waiting --> golpe : decision golpe >= 0.6 (GOLPE, flash vermelho, entra na lista)
    waiting --> revisar : 0.4 < golpe < 0.6 (SUSPEITA)
    waiting --> ok : golpe <= 0.4 (OK)
    waiting --> error : evento error (ERRO)
```

Terminal por mensagem; a bolha da lane mostra sempre a última decisão (`setVerdict`, `index.html:1000-1020`).

## 4. Fase da tela (`phase`) 🟢

```mermaid
stateDiagram-v2
    [*] --> idle
    idle --> running : run
    running --> done : done dos dois lados
    running --> stopped : stop
    running --> idle : reset
    done --> idle : reset (Reiniciar encadeia start)
    stopped --> idle : reset
```

Regras: em `stopped` nenhum evento altera a tela; `report` só em `done` ou `stopped`; botão principal mostra Iniciar / Parar / Reiniciar conforme `phase` e `runId` (`updateControls`).

## 5. Conexão do lado Python (`status.state`) 🟢

```mermaid
stateDiagram-v2
    [*] --> offline : servidor sobe
    offline --> connected : worker conecta em /ws/worker (hello enviado)
    connected --> loading : worker inicia carga do grafo
    loading --> ready : grafo + aquecimento ok (nodes, edges, load_ms, memory_mb, model)
    loading --> connected : erro de inicializacao -> error, reconecta preservando grafo
    ready --> offline : socket cai (se ainda era o slot ativo)
    connected --> offline : socket cai
    offline --> connected : reconexao a cada 2 s
```

Lado Rust: nasce `ready` no boot (`server.rs:179`). Um worker novo pode assumir o slot; o antigo, ao cair, não marca `offline` (`server.rs:444-459`).

## 6. Worker Python: `Run` 🟢

```mermaid
stateDiagram-v2
    [*] --> Sem_run : boot, reset, stop, queda do socket
    Sem_run --> Ativo : evento run (novo objeto Run, semaforo, pace)
    Ativo --> Ativo : message (id inedito) -> task
    Ativo --> Concluido : processed == total -> done
    Ativo --> Sem_run : reset / stop / queda
    Concluido --> Sem_run : reset / stop
```

Identidade por objeto: tarefas antigas comparam `self.run is run` e descartam resultados (`worker.py:249-277`).

## 7. Conexão WebSocket do browser 🟢

```mermaid
stateDiagram-v2
    [*] --> Conectando
    Conectando --> Conectado : open (transportReady, reconnectAttempt = 0)
    Conectado --> Reconectando : close/error
    Reconectando --> Conectando : timeout 500 * 2^n ms, max 10 s
    Conectado --> Encerrado : pagehide
    Encerrado --> Conectando : pageshow persisted
```

Em modo mock a conexão é sempre "Simulação local".
