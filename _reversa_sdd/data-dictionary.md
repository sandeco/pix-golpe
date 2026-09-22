# Dicionário de dados: pix-golpe

> Gerado pelo Archaeologist (Reversa) em 2026-09-21. 🟢 CONFIRMADO salvo indicação. Sem SGBD: os dados vivem em arquivos de `data/` e em memória.

## 1. Arquivos persistidos

### `data/transacoes.bin` (binário, 159.496.188 bytes)

| Campo | Tipo | Offset | Obrigatório | Descrição |
|---|---|---|---|---|
| magic | `[u8;4]` = `PIX1` | 0 | sim | assinatura |
| n_contas | `u32 LE` | 4 | sim | 1.000.000 |
| n_transacoes | `u32 LE` | 8 | sim | 9.968.511 |
| registro[i].origem | `u32 LE` | 12+16i | sim | id da conta pagadora, 0..n_contas−1 |
| registro[i].destino | `u32 LE` | +4 | sim | id da conta recebedora |
| registro[i].valor | `u32 LE` | +8 | sim | centavos, 500..2.000.000 |
| registro[i].ts | `u32 LE` | +12 | sim | segundos desde t=0, 0..864.000, **ordenado crescente** |

Invariantes: `len == 12 + 16·n_transacoes`; ids < n_contas; ts não decrescente (validado só no Python).

### `data/mensagens.jsonl` (1.000 linhas)

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| id | u32 | sim | 0..999, posição após o shuffle, ordem de exibição |
| ts | u32 | sim | segundos; golpes: `inicio_ts − 120..600` |
| remetente | string | sim | telefone `+55 DD 9xxxx-xxxx`, `SMS 2xxxx`, nome ou "(número desconhecido)" |
| texto | string | sim | português, template preenchido |
| chave | string | sim | chave Pix citada; sempre existe em `chaves.json` |
| golpe_real | bool | sim | verdade de referência; **nunca enviado aos modelos** |

### `data/chaves.json` (objeto, 965 entradas 🟢 medido)

| Chave | Valor | Descrição |
|---|---|---|
| chave Pix (string) | u32 | id da conta. Formatos: `DD9NNNNNNNN` (telefone), `nome####@gmail.com`, `xxxxxxxx-xxxx` (hex) |

Ordenado alfabeticamente na escrita. 40 chaves de quadrilha + 925 chaves legítimas = 965 🟢 (medido; mensagens de golpe repetem as 40 chaves).

### `data/meta.json`

| Campo | Tipo | Descrição |
|---|---|---|
| n_contas | u32 | 1.000.000 |
| n_transacoes | u32 | 9.968.511 |
| hubs | u32[] | ids 0..1999 (comerciantes) |
| quadrilhas[] | objeto | 40 itens |
| quadrilhas[].chave | string | chave Pix do golpe |
| quadrilhas[].no | u32 | conta da chave |
| quadrilhas[].laranjas | u32[] | 12 a 18 ids |
| quadrilhas[].saque | u32[] | 2 ids |
| quadrilhas[].inicio_ts | u32 | início dos pagamentos das vítimas |

### `data/trace_ref.jsonl` (40 linhas, saída de `trace --todas`)

| Campo | Tipo | Descrição |
|---|---|---|
| chave | string | |
| no | u32 | |
| t0 | u32 | ts da primeira mensagem com a chave |
| visitados | usize | nós alcançados |
| arestas_sub | usize | arestas do subgrafo |
| laranjas | u32[] | ordenado por id |
| saque | u32[] | ordenado por id |
| soma_suspeita | f64 | 4 casas |

### `.env`

| Variável | Uso |
|---|---|
| TYPESAFE_API_KEY | Jev (Rust) |
| DEEPSEEK_API_KEY | DeepSeek (Python) |

Variáveis de ambiente opcionais: `PIX_STEP_MS` (u64, padrão 2500), `PIX_NO_WORKER` (presença desliga o worker).

## 2. Estruturas em memória

### Rust

| Struct | Arquivo | Campos |
|---|---|---|
| `Tx` | data.rs | origem, destino, valor, ts: u32 |
| `Mensagem`, `Quadrilha`, `Meta` | data.rs | ver seção 1 |
| `Graph` | graph.rs | n: u32, n_edges: usize, start: Vec<u32> (n+1), dst/val/ts: Vec<u32> (m), in_deg: Vec<u32> (n) |
| `Trace` | graph.rs | no, t0, visitados, arestas_sub, laranjas, saque, soma_suspeita, nos: Vec<(id, prof: u8, suspeita: f64)>, sub: Vec<(src, dst, valor, ts)> |
| `TraceResumo` | graph.rs | projeção serializável de `Trace` + chave |
| `Decisao` | jev.rs | golpe, tipo, tipo_confianca, urgencia, pede_pix: f64; tokens_in, tokens_out: u64; model: String |
| `App` | server.rs | estado global compartilhado (ver code-analysis) |
| `Stats` | server.rs | decision_ms, trace_ms: Vec<f64>; golpes, erros: u64; cost_usd: f64 |

### Python

| Classe | Arquivo | Campos |
|---|---|---|
| `Graph` | trace.py | n, n_edges, saida: list[list[(dst, valor, ts)]], grau_in_total: list[int] (alias in_deg) |
| `Trace` (dataclass slots) | trace.py | mesmos campos do Rust |
| `Run` (dataclass) | worker.py | run_id, total, started, seen: set[int], processed, golpes, erros, decision_ms, trace_ms, cost, done |
| `Worker` | worker.py | client, url, ws, graph, chaves, load_ms, memory_mb, model, run, sem, pace_ms, trace_lock, send_lock, tasks |
| resultado de `parse_response` | deepseek.py | golpe, urgencia, pede_pix: float; tipo: str; tokens_in, tokens_out: int; model: str; latency_ms: float |

### Front-end (JS)

| Objeto | Campos |
|---|---|
| `lanes[side]` | root, ui (data-fields), accent, rgb, processed, ok, done, decisionMs[], traceMs[], graph, scams: Map, traces: Map, latestId, selectedId, currentId |
| `messages` | Map id → {texto, remetente, chave, ts} |
| estado global | runId, total, runMode, concurrency, paceMs, phase, pending, pendingStart, transportReady, sideStatus |

## 3. Protocolo WebSocket (eventos JSON)

Todo evento tem `type`. Eventos de lado têm `side: "rust" | "python"`. Eventos de corrida têm `run_id`.

### Browser → servidor
| type | campos |
|---|---|
| start | mode: `"step"` \| `"step:<ms>"` \| `"serial"` \| `"burst"` |
| pace | mode |
| stop | |
| report | |
| reset | |

### Servidor → browser e worker
| type | campos |
|---|---|
| run | run_id, mode, total, concurrency (1 ou 8), pace_ms |
| message | run_id, id, ts, remetente, texto, chave |
| pace | run_id, mode, ms |
| stop | run_id |
| reset | |
| hello (só worker) | data_dir |

### Lado → servidor → browser
| type | campos |
|---|---|
| status | side, state: connected \| loading \| ready \| offline; nodes, edges, load_ms, memory_mb, model |
| decision | side, run_id, id, latency_ms, golpe, tipo, urgencia, pede_pix, verdict, tokens_in, tokens_out, cost_usd, model; Rust também tipo_confianca |
| trace | side, run_id, id, chave, latency_ms, visitados, arestas_sub, laranjas[], saque[], nodes[[id, prof, suspeita]], edges[[src, dst]], truth{laranjas_reais, laranjas_acertadas, saque_reais, saque_acertadas} (adicionado pelo servidor) |
| error | side, run_id, id?, message |
| done | side, run_id, totals{messages, golpes, erros, decision_p50_ms, decision_p95_ms, trace_p50_ms, trace_p95_ms, cost_usd, total_ms} |
| report (só browser) | run_id, total, golpes_reais, sides{rust, python}{avaliadas, matriz{golpe{golpe,revisar,ok}, normal{golpe,revisar,ok}}, tp, fp, fn, tn, acuracia, precisao, recall} |

## 4. Enumerações de domínio

| Enum | Valores |
|---|---|
| verdict | `golpe` (≥ 0,6), `revisar` (0,4 < x < 0,6; UI "SUSPEITA"), `ok` (≤ 0,4); UI ainda `waiting`, `error` |
| tipo | troca_numero, boleto_falso, falsa_central, premio, pix_errado, cobranca_legitima, pessoal, outro |
| urgencia | 0 (sem pressão), 1 (alguma), 2 (extrema) |
| mode | step, step:<ms>, serial, burst |
| status.state | connected, loading, ready, offline |
| phase (UI) | idle, running, done, stopped |
| papel de conta (rastreio) | chave, laranja, saque, demais |
| papel de conta (gerador) | hub (0..1999), normal, vítima, chave, laranja, saque |
