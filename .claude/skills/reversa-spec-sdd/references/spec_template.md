# Spec Template — RFC Pragmático

> Instruções de uso: substitua todo texto entre `[colchetes]` pelo conteúdo real.
> Remova as instruções em itálico ao finalizar.
> Marque itens em aberto com `⚠️ ABERTO:` para não esquecer de resolver.

---

# Spec: [Nome da Feature]

**Versão:** 1.0
**Status:** Rascunho | Em Revisão | Aprovada | Implementada
**Autor:** [Nome]
**Data:** [YYYY-MM-DD]
**Reviewers:** [Nomes ou "N/A"]

---

## 1. Resumo

> *1–3 frases. O que é essa feature e por que ela existe? Leia isso e já entenda o objetivo.*

[Descrição concisa da feature e seu propósito.]

---

## 2. Contexto e Motivação

> *Por que estamos construindo isso agora? Qual problema ou oportunidade motivou a decisão?*

**Problema:**
[Descreva o problema que existe hoje. Seja específico — inclua exemplos reais se possível.]

**Evidências:**
[Dados, feedbacks, métricas ou observações que justificam a prioridade.]

**Por que agora:**
[O que mudou que torna isso urgente ou oportuno.]

---

## 3. Goals (Objetivos)

> *O que essa feature precisa entregar para ser considerada um sucesso?*
> *Cada goal deve ser verificável — se você não consegue medir, reformule.*

- [ ] G-01: [Objetivo 1]
- [ ] G-02: [Objetivo 2]
- [ ] G-03: [Objetivo 3]

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| [Ex: Taxa de conversão] | [X%] | [Y%] | [data] |

---

## 4. Non-Goals (Fora do Escopo)

> *Explícito é melhor que implícito. Diga o que NÃO vai ser feito nessa versão.*
> *Isso previne scope creep e alinha expectativas.*

- NG-01: [O que não será feito]
- NG-02: [O que não será feito]
- NG-03: [Versões futuras podem incluir X, mas não agora]

---

## 5. Usuários e Personas

> *Quem vai usar isso? Qual o contexto deles?*

**Usuário primário:** [Descrição — ex: "Usuário logado com plano Pro, familiarizado com a plataforma"]
**Usuário secundário:** [Se houver — ex: "Admin que configura as permissões"]

**Jornada atual (sem a feature):**
[Descreva em 2–4 passos o que o usuário faz hoje para resolver o mesmo problema, ou por que não consegue.]

**Jornada futura (com a feature):**
[Descreva em 2–4 passos o que o usuário fará com a feature pronta.]

---

## 6. Requisitos Funcionais

> *O coração da spec. Cada requisito deve ser: atômico, testável e sem ambiguidade.*
> *Formato: RF-XX — [O sistema / usuário] deve [verbo concreto] [complemento].*

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | [O sistema deve...] | Must | [Como testar que isso está funcionando] |
| RF-02 | [O usuário deve poder...] | Must | [Condição verificável] |
| RF-03 | [O sistema deve...] | Should | [Condição verificável] |
| RF-04 | [O sistema deve...] | Could | [Condição verificável] |

> Prioridades: **Must** (obrigatório no MVP) / **Should** (importante, mas negociável) / **Could** (nice-to-have)

### 6.2 Fluxo Principal (Happy Path)

> *Descreva o fluxo mais comum, passo a passo.*

1. O usuário [ação 1]
2. O sistema [resposta 1]
3. O usuário [ação 2]
4. O sistema [resposta 2]
5. Resultado: [estado final]

### 6.3 Fluxos Alternativos

> *Variações do fluxo principal que também devem funcionar.*

**Fluxo Alternativo A — [Nome]:**
1. [Passo divergente do fluxo principal]
2. [Comportamento específico]

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Performance | [ex: P95 < 300ms] | [contexto] |
| RNF-02 | Disponibilidade | [ex: 99,9% uptime] | [contexto] |
| RNF-03 | Segurança | [ex: autenticação obrigatória] | [contexto] |
| RNF-04 | Acessibilidade | [ex: WCAG 2.1 AA] | [contexto] |

---

## 8. Design e Interface

> *Descreva o comportamento da UI/UX, não o visual. Wireframes podem ser referenciados.*

**Componentes afetados:** [Lista de telas, componentes ou endpoints tocados]

**Comportamento esperado:**
[Descreva o que o usuário vê e como os elementos respondem às ações.]

**Estados da UI:**
- Estado vazio: [o que mostrar quando não há dados]
- Estado de carregamento: [o que mostrar enquanto processa]
- Estado de erro: [o que mostrar em caso de falha]
- Estado de sucesso: [o que mostrar após completar]

---

## 9. Modelo de Dados

> *Apenas se a feature cria ou modifica dados persistidos.*

**Entidades novas ou modificadas:**

```
[NomeEntidade] {
  campo_1: tipo        // descrição
  campo_2: tipo        // descrição
}
```

**Migrações necessárias:** [Sim / Não — se sim, descreva o impacto]

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| [API externa / Serviço / Biblioteca] | [Obrigatória / Opcional] | [Comportamento de fallback] |

---

## 11. Edge Cases e Tratamento de Erros

> *Esta seção é onde specs costumam falhar. Pense nos casos difíceis.*

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: [Nome do edge case] | [O que causa esse cenário] | [O que o sistema deve fazer] |
| EC-02: [Input inválido] | [Condição] | [Mensagem de erro / fallback] |
| EC-03: [Timeout / falha externa] | [Condição] | [Retry / degradação / erro claro] |
| EC-04: [Limite de rate/quota atingido] | [Condição] | [Comportamento] |

---

## 12. Segurança e Privacidade

- **Autenticação:** [Quem pode acessar essa feature?]
- **Autorização:** [Quais permissões são necessárias?]
- **Dados sensíveis:** [A feature processa PII, dados financeiros ou confidenciais? Como são protegidos?]
- **Auditoria:** [É necessário log de auditoria? O quê deve ser logado?]

---

## 13. Plano de Rollout

- **Estratégia:** [Big bang / Feature flag / Rollout gradual / Canário]
- **Como reverter (rollback):** [Passos para desfazer se algo der errado]
- **Monitoramento pós-deploy:** [O que observar nas primeiras 24–48h]

---

## 14. Open Questions

> *Dúvidas ainda não resolvidas que podem impactar o design. Cada item deve ter um dono e prazo.*

| # | Pergunta | Impacto | Dono | Prazo |
|---|---------|---------|------|-------|
| OQ-01 | [Pergunta em aberto] | [Alto/Médio/Baixo] | [Nome] | [data] |

---

## 15. Decisões Tomadas (Decision Log)

> *Registre decisões importantes e o racional — útil para futuras revisões.*

| Decisão | Alternativas consideradas | Racional |
|---------|--------------------------|---------|
| [O que foi decidido] | [O que foi descartado] | [Por que essa opção] |

---

## Apêndice

### Referências
- [Links para docs, tickets, designs, pesquisas relacionadas]

### Histórico de Revisões
| Versão | Data | Autor | Mudanças |
|--------|------|-------|---------|
| 1.0 | [data] | [autor] | Criação inicial |
