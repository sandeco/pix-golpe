# C4 Nível 1: Contexto

> Gerado pelo Architect (Reversa) em 2026-09-21. 🟢

```mermaid
C4Context
    title pix-golpe: contexto
    Person(apresentador, "Apresentador", "Grava o vídeo; clica Iniciar, troca o ritmo, abre o relatório")
    Person(operador, "Operador", "Gera os dados e sobe o servidor pelo terminal")
    System(pix, "pix-golpe (Pix Race)", "Corrida em tela dividida: Rust+Jev vs Python+DeepSeek detectando golpes e rastreando quadrilhas em dados simulados")
    System_Ext(jev, "TypeSafe AI (Jev)", "API de perguntas tipadas, modelo jev-latest")
    System_Ext(deepseek, "DeepSeek", "API chat/completions em JSON mode, modelo deepseek-flash")
    Rel(apresentador, pix, "Usa", "browser, http://localhost:8080")
    Rel(operador, pix, "cargo run gerar-dados / server", "terminal")
    Rel(pix, jev, "Classifica mensagens", "HTTPS, Bearer")
    Rel(pix, deepseek, "Classifica mensagens", "HTTPS, Bearer")
```

## Notas

- Não há outros usuários nem sistemas: sem banco, sem fila, sem auth.
- Os dois serviços externos recebem apenas remetente e texto da mensagem; a verdade de referência nunca sai do servidor.
- Nada é real: mensagens, contas, chaves e transações são sintéticas (ADR-003).
