# Lacunas e divergências: pix-golpe

> Gerado pelo Revisor (Reversa) em 2026-09-21. Itens que permaneceram sem confirmação humana ou que divergem entre código e documentação. Severidade: **crítico** (bloqueia reimplementação fiel ou invalida a comparação), **moderado** (afeta docs/medições), **cosmético**.

## Lacunas 🔴 (dependem do usuário, ver `questions.md`)

| # | Lacuna | Severidade | Pergunta | Specs |
|---|---|---|---|---|
| ~~G-01~~ | Escala oficial do dataset: **resolvida** em 2026-09-22, vale o código (1 M / ~10 M / 2.000). Virou divergência documental D-05/D-07 | resolvida | Pergunta 1 ✅ | volumetria-das-bases, geracao-de-dados, domain RN-51 |
| G-02 | Latência de decisão inclui backoff no Rust e exclui no Python. Usuário não tem posição; permanece aberta. Recomendação: igualar excluindo o backoff nos dois lados | moderado (crítico só se houver 429/5xx na gravação) | Pergunta 2 ⏳ | decisao-por-ia, domain RN-07, ADR-002 |
| ~~G-03~~ | Contas de saque com movimento de fundo: **resolvida** em 2026-09-22, vale o código; SPEC §1 e PDF p.4 a corrigir (D-08) | resolvida | Pergunta 3 ✅ | geracao-de-dados RN-55, volumetria T-05 |

## Divergências documentais 🟢 (confirmadas no código, sem pergunta)

| # | Divergência | Severidade | Onde corrigir |
|---|---|---|---|
| D-01 | SPEC §4 diz que `index.html` é embutido com `include_str!`; o servidor lê do disco a cada request (`server.rs:220-226`) | cosmético | SPEC.md |
| D-02 | SPEC §5 descreve a tela antiga (mockup de celular, seletor `step`/`burst`); a tela atual tem contador gigante, lista de golpes, Narrado/Normal, Parar, relatório | moderado | SPEC.md §5, ADR-006 já registra |
| D-03 | `docs/tela-corrida.png` mostra o título "PIX RACE"; o HTML atual tem "DETECTOR DE GOLPE" | cosmético | regravar screenshot ou confirmar título |
| D-04 | `memory_mb` no `status` e linha "MEMÓRIA" na tela não constam do SPEC §4 | cosmético | SPEC.md |
| D-05 | README diz "1,3 milhão de transações"; o dataset tem ~10 milhões | moderado | README.md (depende da Pergunta 1) |
| D-06 | Modo `burst` existe no protocolo e no benchmark do README, mas não no seletor da tela | cosmético | documentar como o benchmark foi disparado |
| D-07 | SPEC §1 e PDF p.3-4 citam 100 k contas / 1,27 M transações / 200 hubs; oficial é 1 M / 9.968.511 / 2.000 | moderado | SPEC.md §1, PDF, README |
| D-08 | SPEC §1 e PDF p.4 dizem que contas de saque não movimentam nada em 24 h; o gerador permite fundo (807 saídas) | moderado | SPEC.md §1, PDF |

## Inferências 🟡 que permanecem

| # | Item | Motivo | Specs |
|---|---|---|---|
| I-01 | Memória residente do lado Rust (~170 MB CSR; pico ~320 MB na carga) | não medida nesta extração (o servidor exige chave de API para subir) | volumetria-das-bases, architecture D9/D10 |
| I-02 | Tempo de geração de 2 s (README) | não reexecutado (evita sobrescrever `data/`) | geracao-de-dados |
| I-03 | Cores do canvas (chave, laranjas, saque) | lidas do screenshot, não do código do `drawGraph` linha a linha | design-system |
| I-04 | `Lagged` no broadcast em rajada com browser lento | cenário não reproduzido | corrida-em-tempo-real, architecture D12 |
| I-05 | `requirements.txt` sem pin pode quebrar com `websockets` < 13 | não testado | dependencies |
| I-06 | Reprodutibilidade do gerador depende das versões de `rand*` | não há teste de hash | geracao-de-dados |

## Dívidas técnicas relevantes para quem for reimplementar

Ver `architecture.md` §6 (D1 a D13). As três mais importantes: ausência de testes automatizados (a igualdade Rust/Python é verificada à mão), documentação desatualizada (D-01 a D-06 acima) e ausência de autenticação com bind `0.0.0.0` (irrelevante para a demo local, relevante fora dela).

## Agentes independentes não executados

| Agente | Motivo |
|---|---|
| Visor | screenshots já foram usados pelo Design System e pela unit `interface-tela-dividida`; a documentação de telas por unit não foi gerada separadamente |
| Data Master | não há SGBD; o conteúdo equivalente está em `data-dictionary.md`, `erd-complete.md` e `volumetria-das-bases/` |
| Tracer | exige o sistema em execução com chaves de API (custo e chamadas externas); não executado em modo autônomo |
| Revisão cruzada via Codex | opcional no nível `completo` e exige confirmação do usuário; não executada em modo autônomo |
