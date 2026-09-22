# Spec Impact Matrix: pix-golpe

> Gerado pelo Architect (Reversa) em 2026-09-21. 🟢. Linhas = componente alterado; colunas = componentes que precisam ser revistos. `●` impacto direto (contrato ou algoritmo compartilhado), `○` impacto indireto (exibição, métricas, docs).

| Alterado ↓ / Impacta → | data | gerar-dados | graph | trace.py | jev | deepseek | server | worker | frontend | trace-cli | data/ (regenerar) | SPEC/README/PDF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **data** (formato dos arquivos) | | ● | ● | ● | | | ● | ● | | ● | ● | ● |
| **gerar-dados** (constantes, padrões) | | | ○ | ○ | | | ○ | ○ | ○ | ● | ● | ● |
| **graph** (algoritmo/constantes) | | | | ● | | | ○ | | ○ | ● | ○ trace_ref | ● |
| **trace.py** | | | ● | | | | | ● | | ● | | ● |
| **jev** (perguntas, veredito, custo) | | | | | | ● espelho | ● | | ○ | | | ● |
| **deepseek** (prompt, validação, custo) | | | | | ● espelho | | ○ | ● | ○ | | | ● |
| **server** (protocolo WS, eventos) | | | | | | | | ● | ● | | | ● |
| **worker** (eventos emitidos) | | | | | | | ● | | ● | | | ● |
| **frontend** (comandos enviados) | | | | | | | ● | | | | | ○ |
| **trace-cli** (formato do resumo) | | | | | | | | | | | ● trace_ref | ○ |
| **.env / chaves de API** | | | | | ● | ● | ● | ● | | | | |

## Contratos compartilhados (pontos de acoplamento)

| Contrato | Lados | Arquivo de referência |
|---|---|---|
| Formato `transacoes.bin` | data.rs ↔ trace.py `Graph.load` | `data-dictionary.md` §1 |
| Constantes do rastreio (JANELA, PROF_MAX, VALOR_MIN, MAX_NOS, ITER_LP, limites de desenho) | graph.rs ↔ trace.py | `graph.rs:8-14`, `trace.py:15-21` |
| Passos A a D e ordem de soma flutuante | graph.rs ↔ trace.py | ADR-004 |
| 4 perguntas e 8 tipos | jev.rs `questions()` ↔ deepseek.py `SYSTEM_PROMPT`/`TIPOS` ↔ index.html `TYPES` | SPEC §2 |
| Regra de veredito (0,6 / 0,4) | jev.rs ↔ deepseek.py ↔ relatório | ADR-008 |
| Eventos WS (`run`, `message`, `decision`, `trace`, `status`, `done`, `report`, ...) | server ↔ worker ↔ frontend | `data-dictionary.md` §3 |
| Modos (`step`, `step:<ms>`, `serial`, `burst`) e concorrência (1 / 8) | frontend → server → worker | RN-06 |
| Preços por token | jev.rs, deepseek.py, cartão final | ADR-007 |
| Resumo JSON do rastreio (`TraceResumo`) | trace.rs ↔ trace.py ↔ `trace_ref.jsonl` | RN-25 |

## Regras de verificação após mudança

1. Mudou `graph.rs` ou `trace.py`: rodar `cargo run --release --bin trace -- --todas > data/trace_ref.jsonl` e `python py-worker/trace.py --todas > data/trace_py.jsonl`, comparar com `fc`.
2. Mudou `gerar_dados.rs` ou `data.rs`: regenerar `data/`, refazer o passo 1, atualizar SPEC §1, PDF e README (volumes).
3. Mudou o protocolo em `server.rs`: atualizar `worker.py` (`parse_event`) e `index.html` (`receive`) e o `?mock=1`.
4. Mudou perguntas/tipos: atualizar os três lugares (jev, deepseek, `TYPES` na tela) e o SPEC §2.
