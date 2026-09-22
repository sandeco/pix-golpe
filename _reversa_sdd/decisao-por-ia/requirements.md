# Decisão por IA

> Unit `decisao-por-ia`. Gerado pelo Writer (Reversa) em 2026-09-21. 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA.

## Visão Geral
Cada lado classifica uma mensagem em português respondendo 4 perguntas equivalentes (golpe, tipo, urgência, pede Pix) e deriva um veredito em três faixas. Lado Rust usa o Jev (TypeSafe AI) com perguntas tipadas; lado Python usa o DeepSeek em JSON mode. Mede latência HTTP e custo por mensagem.

## Responsabilidades
- Montar a requisição com remetente e texto (nunca `golpe_real`, nunca a chave).
- Chamar a API do lado, com retentativas curtas em sobrecarga.
- Validar a resposta e produzir a decisão normalizada `{golpe, tipo, urgencia, pede_pix, tokens_in, tokens_out, model, latency_ms}`.
- Derivar o veredito e o custo.
- Executar uma chamada de aquecimento na inicialização.

## Regras de Negócio
- RN-02 Perguntas idênticas nos dois lados: `golpe` (0..1), `tipo` ∈ {troca_numero, boleto_falso, falsa_central, premio, pix_errado, cobranca_legitima, pessoal, outro}, `urgencia` (0, 1, 2), `pede_pix` (0..1). Estado em português, instruções em inglês. 🟢 `src/jev.rs:43-58`, `py-worker/deepseek.py:29-38`
- RN-03 Veredito: `golpe >= 0.6` → `golpe`; `<= 0.4` → `ok`; senão `revisar`. 🟢 `jev.rs:33-41`, `deepseek.py:71-72`
- RN-05 O modelo recebe só `remetente` e `mensagem`/`texto`. 🟢 `jev.rs:113`, `deepseek.py:141`
- RN-08 Custo Jev = `tokens_in × 0,042/1e6` USD; DeepSeek = `prompt × 0,28/1e6 + completion × 0,42/1e6` USD, "estimado". 🟢
- RN-09 Jev: até 3 retentativas em HTTP 429/529, backoff 200·2ⁿ ms; DeepSeek: até 3 tentativas em 429/5xx, backoff 2ⁿ s. Outros status → erro. 🟢 `jev.rs:139-143`, `deepseek.py:149-153`
- RN-10 Resposta DeepSeek inválida (JSON, faixas, tipo fora da lista, `model` vazio, tokens não inteiros) → `ValueError`, evento `error`. 🟢 `deepseek.py:79-112`
- RN-11 Aquecimento: `classificar("teste", "Oi, tudo bem? Aquecimento.")` no boot; falha do Jev só avisa e usa `jev-latest` como nome; falha do DeepSeek emite `error` e reconecta. 🟢 `server.rs:165-174`, `worker.py:163-169`
- RN-07 Latência: Rust mede `classificar()` inteiro (inclui backoff); Python mede só a tentativa bem-sucedida. 🟢 assimetria confirmada; 🔴 intenção sem resposta (Pergunta 2, usuário não sabe). Recomendação: excluir o backoff nos dois lados, pois o SPEC define latência como "ida e volta HTTP".
- O `model` retornado pela API é o exibido na tela (DeepSeek resolvia para `deepseek-flash`). 🟢 `jev.rs:136`, `deepseek.py:85`
- Jev também retorna `tipo_confianca`; DeepSeek não. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Classificar uma mensagem no Jev com as 4 perguntas tipadas | Must | resposta 200 mapeada para `Decisao` |
| RF-02 | Classificar uma mensagem no DeepSeek em JSON mode com o prompt exato | Must | resposta validada por `parse_response` |
| RF-03 | Derivar veredito em 3 faixas | Must | tabela 0,6 / 0,4 |
| RF-04 | Calcular custo por mensagem com as constantes de cada lado | Must | `cost_usd` no evento `decision` |
| RF-05 | Retentativas com backoff em sobrecarga | Should | 429 simulado → nova tentativa |
| RF-06 | Rejeitar resposta fora do contrato como erro, sem travar a corrida | Must | JSON inválido → `error`, corrida continua |
| RF-07 | Aquecimento no boot | Should | uma chamada antes de `ready` |
| RF-08 | Carregar chaves de API do ambiente ou `.env` (Python procura nos diretórios pais) | Must | ausência → erro claro |
| RF-09 | CLI `deepseek.py` para testar uma mensagem | Could | imprime JSON com verdict e custo |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Performance | timeout 30 s no Jev; 120 s (connect 20 s) no DeepSeek | `jev.rs:105`, `deepseek.py:119` | 🟢 |
| Disponibilidade | retry 3× com backoff exponencial | `jev.rs:139`, `deepseek.py:149` | 🟢 |
| Escalabilidade | pool httpx de 8 conexões keepalive (= concorrência máxima) | `deepseek.py:120` | 🟢 |
| Segurança | Bearer token de `.env`; TLS com store do sistema no Python | `jev.rs:121`, `deepseek.py:16-21` | 🟢 |
| Custo | US$ 0,026 (Jev) vs US$ 0,106 (DeepSeek) por 1.000 mensagens, medido | README | 🟡 |

## Critérios de Aceitação

```gherkin
Dado uma mensagem "Mãe, troquei de número..." com remetente desconhecido
Quando o lado Rust chama o Jev
Então recebe golpe >= 0,6, tipo troca_numero, e o veredito é "golpe"

Dado golpe = 0,5 em qualquer lado
Quando derivo o veredito
Então o resultado é "revisar" e nenhum rastreio é disparado

Dado que o DeepSeek responde um JSON sem o campo "tipo"
Quando o worker processa a resposta
Então emite evento error com id da mensagem e a corrida continua

Dado que o Jev responde 429 duas vezes e 200 na terceira
Quando o lado Rust classifica
Então a decisão é emitida e a latência inclui as esperas de 200 ms e 400 ms

Dado TYPESAFE_API_KEY ausente
Quando o servidor inicia
Então falha com "TYPESAFE_API_KEY não definida (ver .env na raiz)"
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| Perguntas e veredito idênticos | Must | base da comparação justa |
| Validação estrita do DeepSeek | Must | sem ela a comparação de acurácia é inválida |
| Custo por token | Must | aparece no placar e no cartão final |
| Retry | Should | sem retry a corrida ainda termina, com erros |
| CLI de teste | Could | uso manual |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `src/jev.rs` | `JevClient`, `Decisao`, `verdict`, `questions` | 🟢 |
| `py-worker/deepseek.py` | `DeepSeekClient`, `parse_response`, `verdict`, `cost_usd`, `load_api_key`, `main` | 🟢 |
| `src/bin/server.rs:163-174,336-367` | aquecimento e uso em `processar` | 🟢 |
| `py-worker/worker.py:163-166,250-262` | aquecimento e uso em `process_message` | 🟢 |
