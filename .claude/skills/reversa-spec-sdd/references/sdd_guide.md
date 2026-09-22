# Guia de Metodologia — Spec-Driven Development

## O que é SDD?

Spec-Driven Development é a prática de escrever uma especificação detalhada de comportamento **antes** de escrever qualquer código. A spec responde ao **quê** o sistema deve fazer — não ao **como** implementar.

Não confundir com:
- **TDD** (Test-Driven Development): escreve testes antes do código — complementar ao SDD
- **DDD** (Domain-Driven Design): padrão arquitetural — independente do SDD
- **BDD** (Behavior-Driven Development): foco em comportamentos com Gherkin — um subconjunto de SDD

---

## Princípios Fundamentais

### 1. Behavior, not Implementation

A spec descreve o comportamento observável, não a implementação interna.

❌ Ruim: "O sistema deve usar Redis para cache das sessões"
✅ Bom: "O sistema deve manter a sessão do usuário ativa por 30 dias em dispositivos onde ele marcou 'lembrar de mim'"

A implementação (Redis, JWT, banco de dados) é uma decisão técnica de quem implementa — não da spec.

### 2. Ambiguidade = Bug Futuro

Toda ambiguidade na spec se torna um bug, uma reunião de alinhamento ou uma discussão em PR no futuro. Torne ambiguidades explícitas com `⚠️ ABERTO:` — é melhor um item aberto visível do que uma suposição silenciosa.

### 3. Non-Goals são tão importantes quanto Goals

"O que não vamos fazer" previne scope creep, alinha expectativas e acelera decisões. Uma feature sem non-goals tende a crescer indefinidamente.

### 4. A Spec é um Contrato Vivo

A spec muda conforme o entendimento evolui — e isso é saudável. O que importa é que as mudanças sejam registradas (Decision Log) e que todos os stakeholders estejam alinhados com a versão atual.

### 5. LLM-Readiness

Uma boa spec moderna deve ser legível por LLMs que vão ajudar a implementar. Isso significa:
- Requisitos numerados (IDs rastreáveis)
- Comportamentos explícitos, não implícitos
- Edge cases documentados (LLMs não adivinham casos extremos)
- Contexto de negócio incluído (o "porquê" ajuda a tomar boas decisões de implementação)

---

## O Ciclo SDD

```
Ideia/Problema
      ↓
  Entrevista  ←──────────────────────┐
      ↓                              │
  Rascunho da Spec                   │
      ↓                              │
  Avaliação (Score)                  │
      ↓                              │
  Score < 80? ──── Sim ──── Identificar gaps
      ↓ Não
  Spec Aprovada
      ↓
  Implementação
      ↓
  Spec vs. Código (validação final)
```

---

## Quando Escrever a Spec

| Tamanho da feature | Recomendação |
|-------------------|--------------|
| Fix de bug | Não precisa de spec |
| Melhoria pequena (< 1 dia dev) | Spec mínima: goals + requisitos principais |
| Feature nova (1–5 dias) | Spec completa, mas concisa |
| Feature complexa (> 5 dias) | Spec completa + revisão por 2+ pessoas |
| Sistema novo | Spec de arquitetura + specs por feature |

---

## Prioridades de Requisitos (MoSCoW)

| Prioridade | Significado | Decisão se não couber no prazo |
|-----------|-------------|-------------------------------|
| **Must** | Obrigatório — sem isso não lança | Bloqueia o lançamento |
| **Should** | Importante — mas há workaround | Adia para próxima versão |
| **Could** | Nice-to-have | Descarta se necessário |
| **Won't** | Conscientemente fora do escopo | Documenta como Non-Goal |

---

## Antipadrões Comuns

### "Spec like a PRD de grande empresa"
Specs de 50 páginas que ninguém lê. Prefira specs concisas que cobrem o essencial com clareza.

### "Spec como lista de tarefas técnicas"
"Criar tabela users, adicionar endpoint POST /auth, integrar com OAuth..." — isso é um plano de implementação, não uma spec. A spec fala em comportamento.

### "Spec verbal / em Slack"
Decisões tomadas em conversa sem registro se perdem e geram conflitos. Toda spec deve existir como documento escrito.

### "Spec que nunca muda"
Specs congeladas que não refletem a realidade do que foi implementado. A spec deve ser atualizada quando a implementação divergir intencionalmente.

### "Open Questions silenciosas"
Assumir respostas para perguntas não respondidas. Sempre use `⚠️ ABERTO:` e resolva antes de implementar.

---

## Vocabulário do SDD

| Termo | Definição |
|-------|-----------|
| **Spec** | Documento que descreve o comportamento esperado de uma feature |
| **RF** | Requisito Funcional — o que o sistema deve fazer |
| **RNF** | Requisito Não-Funcional — como o sistema deve se comportar (performance, segurança...) |
| **Goal** | Objetivo que a feature deve atingir |
| **Non-Goal** | O que está explicitamente fora do escopo |
| **Edge Case** | Caso limite ou não-óbvio que o sistema deve tratar corretamente |
| **Happy Path** | O fluxo principal e mais comum de uso |
| **Critério de Aceite** | Condição verificável que define quando um requisito está implementado |
| **Open Question** | Dúvida não resolvida que pode impactar o design |
| **Decision Log** | Registro de decisões importantes e o porquê foram tomadas |
