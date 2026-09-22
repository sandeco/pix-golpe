# Decisão por IA, Tarefas de Implementação

> Unit `decisao-por-ia`. Reimplementação a partir de `src/jev.rs` e `py-worker/deepseek.py`.

## Pré-requisitos
- [ ] `TYPESAFE_API_KEY` e `DEEPSEEK_API_KEY` em `.env` na raiz (ou ambiente)
- [ ] Contratos em `contracts.md` desta unit
- [ ] Regra de veredito compartilhada com `relatorio-de-acuracia`

## Tarefas

- [ ] T-01, Cliente Jev: construção a partir do ambiente, timeout 30 s
  - Origem no legado: `src/jev.rs:93-107`
  - Critério de pronto: ausência da chave produz erro com a mensagem do legado
  - Confiança: 🟢

- [ ] T-02, Montar `questions()` com as 4 perguntas e 8 critérios exatos
  - Origem no legado: `src/jev.rs:43-58`
  - Critério de pronto: JSON idêntico ao de `contracts.md` §1
  - Confiança: 🟢

- [ ] T-03, `classificar` Jev com retry 429/529 (3×, 200·2ⁿ ms) e mapeamento para `Decisao`
  - Origem no legado: `src/jev.rs:110-147`
  - Critério de pronto: mock 429,429,200 → sucesso; mock 500 → erro com corpo
  - Confiança: 🟢

- [ ] T-04, `verdict` e `cost_usd` do lado Rust
  - Origem no legado: `src/jev.rs:24-41`
  - Critério de pronto: 0,6 → golpe; 0,4 → ok; 0,5 → revisar; custo = tokens_in × 0,042e-6
  - Confiança: 🟢

- [ ] T-05, `load_api_key` Python com busca de `.env` em cwd e pais
  - Origem no legado: `py-worker/deepseek.py:41-68`
  - Critério de pronto: aceita `export X=`, aspas simples/duplas e comentário `#`
  - Confiança: 🟢

- [ ] T-06, `DeepSeekClient` com httpx, TLS truststore opcional, pool 8, timeout 120/20 s
  - Origem no legado: `py-worker/deepseek.py:14-21,115-133`
  - Critério de pronto: cliente fecha em `aclose`; funciona sem `truststore`
  - Confiança: 🟢

- [ ] T-07, `classificar` DeepSeek: body exato, 3 tentativas 429/5xx com 2ⁿ s, latência por tentativa
  - Origem no legado: `py-worker/deepseek.py:135-159`
  - Critério de pronto: mock 503,200 → sucesso com latência da 2ª tentativa
  - Confiança: 🟢

- [ ] T-08, `parse_response` com validação estrita
  - Origem no legado: `py-worker/deepseek.py:79-112`
  - Critério de pronto: cada regra da tabela de validação em `contracts.md` §2 tem um caso negativo que levanta `ValueError`
  - Confiança: 🟢

- [ ] T-09, `verdict` e `cost_usd` do lado Python
  - Origem no legado: `py-worker/deepseek.py:71-76`
  - Critério de pronto: mesmos limiares do Rust; custo 0,28/0,42 por milhão
  - Confiança: 🟢

- [ ] T-10, Aquecimento no boot dos dois lados
  - Origem no legado: `src/bin/server.rs:163-174`, `py-worker/worker.py:163-166`
  - Critério de pronto: uma chamada antes de `ready`; falha no Rust só avisa
  - Confiança: 🟢

- [ ] T-11, CLI `deepseek.py [texto] [--remetente]`
  - Origem no legado: `py-worker/deepseek.py:162-186`
  - Critério de pronto: imprime JSON com `verdict` e `cost_usd`; sem texto usa o primeiro golpe do dataset
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Happy path Jev e DeepSeek com respostas gravadas (fixtures)
- [ ] TT-02, Veredito nos limites 0,4 e 0,6 (inclusivos) nos dois lados
- [ ] TT-03, Retry e esgotamento de tentativas nos dois lados
- [ ] TT-04, Tabela de validação do DeepSeek (10 casos negativos)
- [ ] TT-05, Custo por token com números do README (US$ 0,026 e 0,106 para 1.000 mensagens) 🟡

## Ordem Sugerida
1. T-04/T-09 (regra compartilhada) → T-02 → T-01/T-03 → T-05/T-06/T-07/T-08 → T-10 → T-11.
2. TT-02 antes de qualquer integração com `corrida-em-tempo-real`.

## Lacunas Pendentes (🔴)
- Q-002: decidir se a latência inclui ou exclui o backoff, e igualar os lados.
