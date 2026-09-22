# ERD: pix-golpe

> Gerado pelo Architect (Reversa) em 2026-09-21. 🟢 Não há SGBD: o modelo é conceitual sobre os arquivos de `data/` e as estruturas em memória. "PK/FK" indicam identidade lógica.

```mermaid
erDiagram
    CONTA {
        u32 id PK "0..999999"
        bool eh_hub "id < 2000"
        u32 grau_in_total "in_deg, calculado"
    }
    TRANSACAO {
        u32 origem FK
        u32 destino FK
        u32 valor_centavos
        u32 ts "0..864000, ordenado"
    }
    CHAVE_PIX {
        string chave PK "telefone | email | hex"
        u32 conta FK
    }
    MENSAGEM {
        u32 id PK "0..999"
        u32 ts
        string remetente
        string texto
        string chave FK
        bool golpe_real "verdade de referencia"
    }
    QUADRILHA {
        string chave PK_FK
        u32 no FK "conta da chave"
        u32 inicio_ts
    }
    LARANJA {
        string quadrilha FK
        u32 conta FK "12..18 por quadrilha"
    }
    SAQUE {
        string quadrilha FK
        u32 conta FK "2 por quadrilha"
    }
    META {
        u32 n_contas
        u32 n_transacoes
        u32_list hubs "0..1999"
    }
    DECISAO {
        string side "rust | python"
        u32 run_id
        u32 id FK "mensagem"
        f64 golpe
        string tipo
        f64 urgencia
        f64 pede_pix
        string verdict "golpe | revisar | ok"
        f64 latency_ms
        u64 tokens_in
        u64 tokens_out
        f64 cost_usd
        string model
    }
    RASTREIO {
        string side
        u32 run_id
        u32 id FK "mensagem"
        string chave FK
        f64 latency_ms
        usize visitados
        usize arestas_sub
        u32_list laranjas
        u32_list saque
        f64 soma_suspeita
    }
    TRUTH {
        u32 laranjas_reais
        u32 laranjas_acertadas
        u32 saque_reais
        u32 saque_acertadas
    }

    CONTA ||--o{ TRANSACAO : "origem"
    CONTA ||--o{ TRANSACAO : "destino"
    CONTA ||--o{ CHAVE_PIX : "possui"
    CHAVE_PIX ||--o{ MENSAGEM : "citada em"
    CHAVE_PIX ||--o| QUADRILHA : "identifica"
    CONTA ||--o| QUADRILHA : "no da chave"
    QUADRILHA ||--|{ LARANJA : "12..18"
    QUADRILHA ||--|{ SAQUE : "2"
    CONTA ||--o| LARANJA : "e"
    CONTA ||--o| SAQUE : "e"
    META ||--|{ QUADRILHA : "lista"
    MENSAGEM ||--o{ DECISAO : "uma por lado por corrida"
    DECISAO ||--o| RASTREIO : "se verdict = golpe"
    RASTREIO ||--|| TRUTH : "servidor compara com QUADRILHA"
```

## Cardinalidades e invariantes

| Relação | Cardinalidade | Invariante |
|---|---|---|
| Conta → Transação | 1:N (origem) e 1:N (destino) | ids < n_contas; `origem != destino` só nas normais |
| Conta → Chave Pix | 1:N | uma conta pode ter várias chaves (legítimas apontam para hubs repetidos) |
| Chave Pix → Mensagem | 1:N | toda `mensagem.chave` existe em `chaves.json`; chaves de quadrilha aparecem em 1 ou 2 mensagens de golpe |
| Chave Pix → Quadrilha | 1:0..1 | 40 chaves são de quadrilha |
| Quadrilha → Laranja / Saque | 1:12..18 / 1:2 | contas reservadas, disjuntas entre quadrilhas |
| Mensagem → Decisão | 1:0..2 por corrida | uma por lado; erro não gera decisão |
| Decisão → Rastreio | 1:0..1 | só `golpe` |
| Rastreio → Truth | 1:1 | adicionado pelo servidor; chave sem quadrilha → zeros |

## Onde cada entidade vive

| Entidade | Persistência | Em memória |
|---|---|---|
| Conta | implícita (ids) | `Graph.start/in_deg` (Rust), `saida/grau_in_total` (Python) |
| Transação | `transacoes.bin` | CSR `dst/val/ts` (Rust), listas por conta (Python) |
| Chave Pix | `chaves.json` | `HashMap<String,u32>` / `dict` |
| Mensagem | `mensagens.jsonl` | `Vec<Mensagem>` no servidor; cache `messages` no browser (sem `golpe_real`) |
| Quadrilha, Laranja, Saque, Meta | `meta.json` | `truth: HashMap<no, Quadrilha>` no servidor |
| Decisão, Rastreio, Truth | não persistidos (eventos) | `verdicts` no servidor; `lanes[].scams/traces` no browser; `Run` no worker |
| Referência de rastreio | `trace_ref.jsonl` | só para `fc` |
