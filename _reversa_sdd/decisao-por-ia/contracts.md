# Decisão por IA, Contratos externos

> Unit `decisao-por-ia`. Contratos consumidos, extraídos de `src/jev.rs` e `py-worker/deepseek.py`. 🟢

## 1. TypeSafe AI, System One (Jev)

`POST https://api.typesafe.ai/v1/systemone`
Headers: `Authorization: Bearer $TYPESAFE_API_KEY`, `Content-Type: application/json`. Timeout 30 s.

### Request
```json
{
  "model": "jev-latest",
  "state": { "remetente": "<remetente>", "mensagem": "<texto em português>" },
  "questions": {
    "golpe":    { "type": "noul",   "instructions": "This message is a scam or fraud attempt (impersonation, fake bill, fake bank alert, fake prize, pressure to pay)" },
    "tipo":     { "type": "choice", "instructions": "What kind of message is this", "criteria": {
      "troca_numero": "Someone claims to be a relative with a new phone number asking for money",
      "boleto_falso": "Fake bill or invoice to be paid",
      "falsa_central": "Fake bank or support center alert about the account",
      "premio": "Fake prize, lottery or giveaway",
      "pix_errado": "Claims a Pix was sent by mistake and asks for a refund",
      "cobranca_legitima": "Legitimate charge, bill or order confirmation",
      "pessoal": "Ordinary personal message between people who know each other",
      "outro": "Something else" } },
    "urgencia": { "type": "score",  "instructions": "How much time pressure or threat the message applies", "criteria": ["No time pressure", "Some urgency", "Extreme urgency, threats or deadlines"] },
    "pede_pix": { "type": "noul",   "instructions": "The message asks the reader to make a Pix transfer or payment" }
  }
}
```

### Response 200 (campos consumidos)
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "golpe":    { "noul": 0.97 },
    "tipo":     { "choice": "troca_numero", "confidence": 0.93 },
    "urgencia": { "score": 2.0 },
    "pede_pix": { "noul": 0.99 }
  },
  "usage": { "input_tokens": 159, "output_tokens": 0 }
}
```
`output_tokens` opcional (default 0). Campos extras ignorados.

### Erros
| Status | Tratamento |
|---|---|
| 429, 529 | até 3 retentativas, backoff 200, 400, 800 ms |
| outros ≠ 200 | erro `Jev respondeu {status}: {corpo}` |
| timeout / rede | erro `reqwest` |

Custo: `input_tokens × 0.042 / 1e6` USD.

## 2. DeepSeek, Chat Completions

`POST https://api.deepseek.com/chat/completions`
Headers: `Authorization: Bearer $DEEPSEEK_API_KEY`. Timeout 120 s (connect 20 s). Pool 8 conexões.

### Request
```json
{
  "model": "deepseek-chat",
  "temperature": 0,
  "response_format": { "type": "json_object" },
  "messages": [
    { "role": "system", "content": "<SYSTEM_PROMPT exato de deepseek.py:29-34>" },
    { "role": "user", "content": "Remetente: <remetente>\nMensagem: <texto>" }
  ]
}
```

SYSTEM_PROMPT (literal):
```
You classify a message in Brazilian Portuguese. Reply ONLY with a JSON object:
{"golpe": <probability 0..1 that this message is a scam or fraud attempt (impersonation, fake bill, fake bank alert, fake prize, pressure to pay)>,
 "tipo": <one of "troca_numero","boleto_falso","falsa_central","premio","pix_errado","cobranca_legitima","pessoal","outro">,
 "urgencia": <0 = no time pressure, 1 = some urgency, 2 = extreme urgency, threats or deadlines>,
 "pede_pix": <probability 0..1 that the message asks the reader to make a Pix transfer or payment>}
Meaning of tipo: troca_numero = relative with a new phone number asking for money; boleto_falso = fake bill or invoice; falsa_central = fake bank or support alert; premio = fake prize or giveaway; pix_errado = claims a Pix was sent by mistake and asks for refund; cobranca_legitima = legitimate charge or order confirmation; pessoal = ordinary personal message; outro = anything else.
```

### Response 200 (campos consumidos)
```json
{
  "model": "deepseek-flash",
  "choices": [ { "message": { "content": "{\"golpe\": 0.95, \"tipo\": \"troca_numero\", \"urgencia\": 2, \"pede_pix\": 0.98}" } } ],
  "usage": { "prompt_tokens": 210, "completion_tokens": 39 }
}
```

### Validação do `content` (falha → `ValueError`)
| Campo | Regra |
|---|---|
| golpe | número finito, não-bool, 0 ≤ x ≤ 1 |
| urgencia | número finito, não-bool, 0 ≤ x ≤ 2 |
| pede_pix | número finito, não-bool, 0 ≤ x ≤ 1 |
| tipo | string em {troca_numero, boleto_falso, falsa_central, premio, pix_errado, cobranca_legitima, pessoal, outro} |
| model | string não vazia |
| prompt_tokens, completion_tokens | `int` ≥ 0 |

### Erros
| Status | Tratamento |
|---|---|
| 429, 5xx | até 3 tentativas, backoff 1 s, 2 s |
| outros 4xx | `raise_for_status` → `HTTPStatusError` |
| JSON HTTP inválido / content inválido | `ValueError` |

Custo: `prompt_tokens × 0.28/1e6 + completion_tokens × 0.42/1e6` USD (estimado).

## 3. Contrato interno de saída (normalizado)

| Campo | Tipo | Ambos os lados |
|---|---|---|
| golpe, urgencia, pede_pix | número | sim |
| tipo | string dos 8 | sim |
| tipo_confianca | número | só Rust |
| tokens_in, tokens_out | inteiro | sim (Jev out = 0) |
| model | string | sim |
| latency_ms | número | sim (medição diferente, Q-002) |
| verdict | golpe / revisar / ok | derivado |
| cost_usd | número | derivado |
