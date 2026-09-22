# Geração de dados, Design Técnico

> Unit `geracao-de-dados`. Fonte: `src/bin/gerar_dados.rs`, `src/data.rs`. 🟢 salvo indicação.

## Interface

Binário `gerar-dados` (Cargo `[[bin]]`), sem argumentos, sem variáveis de ambiente.

| Símbolo | Assinatura | Retorno | Observação |
|---------|-----------|---------|------------|
| `main` | `()` | `Result<()>` | escreve em `<CARGO_MANIFEST_DIR>/data` |
| `preencher` | `(rng, tpl: &str, chave: &str, valor_centavos: u32)` | `String` | substitui `{parente} {nome} {banco} {loja} {pedido} {valor} {chave}`; `valor` formatado `R$ x,yy` |
| `telefone` | `(rng)` | `String` | `+55 DD 9NNNN-NNNN`, DDD de lista de 10 |
| `nova_chave` | `(rng, usadas)` | `String` | 3 formatos, garante unicidade |
| `ts_comercial` | `(rng, dia)` | `u32` | `dia·86400 + hora·3600 + 0..3600`, horas 8..22 com peso 3 |
| `data::write_*` | ver `data-dictionary.md` | | |

Saídas: `data/transacoes.bin`, `data/chaves.json` (ordenado), `data/meta.json` (pretty), `data/mensagens.jsonl`.

## Fluxo Principal
1. `rng = ChaCha8Rng::seed_from_u64(42)`; `txs` com capacidade 10,5 M (`:125-126`).
2. Pesos dos hubs e closures `escolher_hub` (roleta), `normal` (uniforme em `[2000, 1_000_000)`), distribuições `ln_pequeno`, `ln_lote` (`:129-143`).
3. 9,5 M transações normais (`:146-161`).
4. Lotes diários por hub × dia (`:164-173`).
5. 40 quadrilhas: reserva de contas, vítimas, repasses, chave (`:176-220`).
6. `txs.sort_by_key(ts)` (`:222`).
7. 75 mensagens de golpe, 925 legítimas, shuffle, enumeração (`:225-258`).
8. `Meta { n_contas, n_transacoes: txs.len(), hubs: 0..2000, quadrilhas }` e escrita dos 4 arquivos (`:260-264`).
9. `println!` do resumo (`:265-272`).

## Fluxos Alternativos
- **Pasta `data/` inexistente:** `create_dir_all` cria (`:124`).
- **Falha de I/O:** `anyhow` propaga, binário termina com erro; arquivos parciais podem ficar no disco. 🟢
- **Conta reservada sorteada como vítima:** loop até achar conta não reservada (`:198-203`).
- **Chave repetida:** `nova_chave` re-sorteia até inédita (`:99-108`).

## Dependências
- `rand` 0.8 (`gen_range`, `choose`, `shuffle`), `rand_chacha` 0.3 (`ChaCha8Rng`), `rand_distr` 0.4 (`LogNormal`). Trocar versão pode mudar a sequência e quebrar a reprodutibilidade. 🟡
- `pix_race::data` para os formatos.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Hubs com cauda pesada (`1/(i+1)^0.8`) para "explodir" o rastreio | `:129` | 🟢 |
| Metade das transações normais vai a hubs | `:148-150` | 🟢 |
| Contas de quadrilha reservadas e disjuntas | `:176-193` | 🟢 |
| Laranjas repassam quase tudo (taxa < 1 %) rapidamente (10 a 45 min) | `:214-215` | 🟢 |
| Vítimas pagam valores altos (R$ 300 a 3.000) acima de `VALOR_MIN` | `:204` | 🟢 |
| Mensagens legítimas com loja/banco coerentes (evita falso positivo) | `:245-250`, brainstorm | 🟢 |
| Binário compacto LE de 16 B/registro | `data.rs:122-134` | 🟢 |

## Estado Interno
Sem estado persistente entre execuções. Estruturas transitórias: `txs: Vec<Tx>` (~160 MB), `reservadas: HashSet<u32>`, `chaves_usadas: HashSet<String>`, `chaves: HashMap<String,u32>`, `quadrilhas: Vec<Quadrilha>`, `msgs`.

## Observabilidade
Uma linha em stdout ao final: `gerado em <dir>: <contas> contas, <tx> transações, <quadrilhas> quadrilhas, <mensagens> mensagens`.

## Riscos e Lacunas
- 🟢 Escala oficial confirmada: a do código. SPEC §1, README e PDF a corrigir.
- 🟢 RN-55: contas de saque participam de transações de fundo (comportamento válido); o SPEC promete silêncio de 24 h e está desatualizado.
- 🟡 Determinismo depende das versões exatas de `rand*`; não há teste que fixe um hash do dataset.
- 🟢 Escrita não atômica: falha no meio deixa arquivos parciais.
