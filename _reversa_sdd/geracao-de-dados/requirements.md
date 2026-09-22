# Geração de dados

> Unit `geracao-de-dados`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Gera, uma única vez e de forma reprodutível, o dataset sintético da demo: 1 milhão de contas, ~10 milhões de transações em 10 dias, 40 quadrilhas plantadas com gabarito e 1.000 mensagens em português (75 golpes). Sem dados reais.

## Responsabilidades
- Produzir `data/transacoes.bin`, `data/chaves.json`, `data/meta.json` e `data/mensagens.jsonl` no diretório `data/` da raiz do crate.
- Garantir determinismo: mesma saída a cada execução (`ChaCha8Rng` seed 42).
- Plantar padrões de golpe detectáveis pelo algoritmo de rastreio e mensagens legítimas que não gerem falsos positivos triviais.
- Registrar a verdade de referência (quadrilhas, `golpe_real`).

## Regras de Negócio
- RN-50 Determinismo por semente fixa 42. 🟢 `src/bin/gerar_dados.rs:125`
- RN-51 Volumes: `N_CONTAS=1_000_000`, `N_HUBS=2_000`, `DIAS=10`, `N_TX_NORMAIS=9_500_000`, `N_QUADRILHAS=40`, 75 golpes + 925 legítimas. 🟢 `:11-17`
- Hubs são as contas 0..1999; peso `1/(i+1)^0.8`; 50 % das transações normais têm um hub como destino; cada hub paga lotes diários de `10 + 1500·peso/peso0` transações entre 9h e 11h. 🟢 `:129-173`
- Valores normais `LogNormal(ln 8000, 1.1)` centavos, clamp R$ 5 a R$ 5.000; lotes `LogNormal(ln 30000, 0.8)`, clamp R$ 20 a R$ 20.000. 🟢 `:142-143,158,170`
- Horário: horas 8..22 com peso 3× em relação às demais. 🟢 `:111-120`
- RN-52 Quadrilha: contas reservadas (nunca repetidas entre quadrilhas), 12..18 laranjas, 2 saques; `inicio_ts` em dia 1..8, hora 9..19; 20..40 vítimas pagam R$ 300..3.000 em até 2 h; `t_repasse = inicio + 7200 + 60..900 s`; chave paga cada laranja `total/n − até 2 %` em até 5 min; cada laranja paga um dos 2 saques `valor − taxa(<1 %)` em `t_repasse + 600..2700 s`. 🟢 `:188-220`
- RN-53 Mensagem de golpe `i` usa a quadrilha `i % 40` e o template `i % 30`; `ts = inicio_ts − 120..600 s`; remetente telefone, `SMS 2xxxx` ou telefone "(número desconhecido)". 🟢 `:226-238`
- RN-54 Mensagem legítima: chave nova; conta destino é hub se o template cita `{loja}`, senão conta normal; loja e banco iguais no texto e no remetente; remetente sorteado da lista do template. 🟢 `:240-252`
- Chaves Pix têm três formatos: telefone `DD9NNNNNNNN`, `nome####@gmail.com`, `xxxxxxxx-xxxx` hex; únicas. 🟢 `:98-109`
- Mensagens são embaralhadas; `id` é a posição final. 🟢 `:253-258`
- Transações são ordenadas globalmente por `ts` antes da escrita. 🟢 `:222`
- RN-55 Contas de saque podem aparecer em transações de fundo (807 saídas medidas no dataset); a frase do SPEC "não movimentam nada nas 24 h seguintes" está desatualizada. Vale o código (usuário, 2026-09-22). 🟢
- Escala oficial = a do código (1 M contas, ~10 M transações); docs com 100 k estão desatualizados (usuário, 2026-09-22). 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Gerar os 4 arquivos em `<crate>/data/`, criando a pasta se necessário | Must | arquivos existem após `cargo run --release --bin gerar-dados` |
| RF-02 | Saída byte a byte idêntica entre execuções | Must | `fc` entre duas gerações não acusa diferença |
| RF-03 | `transacoes.bin` no formato PIX1, ordenado por ts | Must | `read_transacoes` valida cabeçalho e tamanho; `trace.py` valida ordem |
| RF-04 | 40 quadrilhas com estrutura RN-52 registradas em `meta.json` | Must | `meta.json.quadrilhas.len == 40`, cada uma com 12..18 laranjas e 2 saques |
| RF-05 | 1.000 mensagens, 75 com `golpe_real=true`, todas com chave presente em `chaves.json` | Must | contagem e verificação de chaves |
| RF-06 | Mensagens de golpe apontam para chaves de quadrilha, com `ts` antes de `inicio_ts` | Must | para cada golpe, `ts < inicio_ts` da quadrilha |
| RF-07 | Imprimir resumo ao final (contas, transações, quadrilhas, mensagens) | Could | stdout |
| RF-08 | Rastreio de referência acerta laranjas e saques nas 40 quadrilhas | Should | `trace --todas` reporta acertos (README: 14/14, 2/2 nos screenshots) 🟡 |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | geração em ~2 s (README) para 10 M transações; `Vec::with_capacity(N_TX_NORMAIS + 1_000_000)` | README, `:126` | 🟡 |
| Reprodutibilidade | RNG determinístico | `:125` | 🟢 |
| Armazenamento | 152 MiB em disco; `data/` não versionado | SPEC layout | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que a pasta data/ não existe
Quando executo cargo run --release --bin gerar-dados
Então data/ contém transacoes.bin, chaves.json, meta.json e mensagens.jsonl
E meta.json declara n_contas = 1000000 e n_transacoes = 9968511

Dado dois diretórios gerados em execuções distintas
Quando comparo os quatro arquivos byte a byte
Então não há diferença

Dado uma mensagem com golpe_real = true
Quando procuro sua chave em meta.json.quadrilhas
Então existe uma quadrilha com essa chave e mensagem.ts < quadrilha.inicio_ts

Dado o arquivo transacoes.bin
Quando leio os registros em sequência
Então ts nunca decresce e todo id de conta é menor que n_contas
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Formato PIX1 e ordenação | Must | contrato com graph, trace.py, server, worker |
| Determinismo | Must | igualdade Rust/Python e `trace_ref.jsonl` dependem disso |
| Quadrilhas com gabarito | Must | placar e relatório |
| Coerência remetente/texto nas legítimas | Should | reduz falsos positivos, mas não quebra o sistema |
| Resumo em stdout | Could | conveniência |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/bin/gerar_dados.rs` | `main`, `preencher`, `telefone`, `nova_chave`, `ts_comercial`, constantes | 🟢 |
| `src/data.rs` | `write_transacoes`, `write_chaves`, `write_meta`, `write_mensagens` | 🟢 |
