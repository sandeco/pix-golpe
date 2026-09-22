# Code/Spec Matrix: pix-golpe

> Gerado pelo Writer (Reversa) em 2026-09-21. Para cada arquivo do legado, qual unit (pasta em `_reversa_sdd/`) cobre o quê. 🟢 coberto integralmente, 🟡 coberto parcialmente, n/a sem unit.

| Arquivo do legado | Unit correspondente | Cobertura | Observação |
|---|---|---|---|
| `src/lib.rs` | (todas as units Rust) | 🟢 | só declara módulos |
| `src/data.rs` | `geracao-de-dados/`, `volumetria-das-bases/` | 🟢 | formatos; leitura também em `rastreio-no-grafo/` |
| `src/bin/gerar_dados.rs` | `geracao-de-dados/` | 🟢 | |
| `src/graph.rs` | `rastreio-no-grafo/` | 🟢 | |
| `src/jev.rs` | `decisao-por-ia/` (+ `contracts.md`) | 🟢 | |
| `src/bin/server.rs` | `corrida-em-tempo-real/` (+ `contracts.md`) | 🟢 | `relatorio()` em `relatorio-de-acuracia/`; `memory_mb` em `volumetria-das-bases/` |
| `src/bin/trace.rs` | `verificacao-cli/` | 🟢 | |
| `py-worker/worker.py` | `corrida-em-tempo-real/` | 🟢 | `memoria_mb` em `volumetria-das-bases/` |
| `py-worker/deepseek.py` | `decisao-por-ia/` (+ `contracts.md`) | 🟢 | CLI em `verificacao-cli/` |
| `py-worker/trace.py` | `rastreio-no-grafo/` | 🟢 | `main` em `verificacao-cli/` |
| `py-worker/requirements.txt` | `dependencies.md` | 🟢 | transversal |
| `static/index.html` (JS) | `interface-tela-dividida/` | 🟢 | relatório em `relatorio-de-acuracia/` |
| `static/index.html` (CSS) | `design-system/` | 🟢 | transversal |
| `static/index.html` (HTML) | `interface-tela-dividida/`, `design-system/` | 🟢 | |
| `Cargo.toml`, `Cargo.lock` | `dependencies.md` | 🟢 | transversal |
| `.env` | `decisao-por-ia/`, `permissions.md` | 🟢 | só nomes das variáveis |
| `data/transacoes.bin`, `chaves.json`, `meta.json`, `mensagens.jsonl` | `volumetria-das-bases/`, `data-dictionary.md`, `erd-complete.md` | 🟢 | |
| `data/trace_ref.jsonl` | `verificacao-cli/`, `volumetria-das-bases/` | 🟢 | |
| `SPEC.md` | `domain.md`, `adrs/` | 🟢 | fonte de regras; divergências listadas em `code-analysis.md` |
| `README.md` | `inventory.md`, `adrs/002` | 🟢 | números medidos |
| `output/pdf/pix-golpe-explicacao.pdf` | `inventory.md`, `volumetria-das-bases/` | 🟢 | propósito; volumes desatualizados |
| `BRAINSTORMING/BRAINSTORM_jev_rust_youtube.md` | `adrs/001`, `adrs/002`, `adrs/006` | 🟢 | origem das decisões |
| `docs/tela-corrida.png`, `docs/relatorio-acuracia.png` | `design-system/`, `interface-tela-dividida/`, `relatorio-de-acuracia/` | 🟢 | screenshot da corrida desatualizado (título) |
| `AGENTS.md`, `CLAUDE.md` | n/a | n/a | instalador do Reversa, não é código do projeto |
| `target/` | n/a | n/a | build |
| `tmp/pdfs/` | n/a | n/a | vazio |

## Cobertura

| Métrica | Valor |
|---|---|
| Arquivos-fonte do legado (rs, py, html) | 11 |
| Cobertos por alguma unit | 11 (100 %) |
| Arquivos de dados/config/docs mapeados | 14 de 16 (AGENTS.md e CLAUDE.md são do Reversa) |
| Units | 8 |
| Arquivos canônicos + opcionais nas units | 26 (24 canônicos + 2 `contracts.md`) |
| Globais | `openapi/pix-golpe.yaml`, `user-stories/corrida.md`, `user-stories/relatorio-e-detalhes.md`, este arquivo |

## Units → regras de domínio

| Unit | Regras (`domain.md`) | ADRs |
|---|---|---|
| geracao-de-dados | RN-50 a RN-55 | 003 |
| decisao-por-ia | RN-02, RN-03, RN-05, RN-07 a RN-11 | 007, 008 |
| rastreio-no-grafo | RN-20 a RN-27 | 004 |
| corrida-em-tempo-real | RN-01, RN-04, RN-06, RN-28, RN-30 a RN-34 | 005 |
| interface-tela-dividida | RN-30, RN-33, RN-34, RN-35 | 006 |
| relatorio-de-acuracia | RN-40 a RN-43 | 008 |
| verificacao-cli | RN-25 | 004 |
| volumetria-das-bases | RN-51, RN-55 | 003 |
