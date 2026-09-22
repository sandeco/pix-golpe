# Exemplos de Specs: Boa vs. Ruim

Estes exemplos usam a feature "Notificações por E-mail" para ilustrar a diferença.

---

## ❌ Spec Ruim — Score: 32/100

```markdown
# Spec: Notificações

## O que vamos fazer
Implementar notificações por e-mail para os usuários quando acontecer algo importante.

## Requisitos
- O sistema deve enviar e-mails
- Os e-mails devem ser bonitos
- O usuário deve poder desativar notificações
- Deve ser rápido

## Notas técnicas
Usar SendGrid ou SES. Talvez usar fila SQS.
```

### Por que é ruim:

| Problema | Impacto |
|---------|---------|
| "quando acontecer algo importante" — o que é importante? | Dev vai implementar o que achar certo, não o que o negócio quer |
| "e-mails devem ser bonitos" — não testável | Nenhum critério de aceite possível |
| "deve ser rápido" — sem número | Bug: e-mail demora 5min, dev acha que está ok |
| Non-goals ausentes | Scope creep: "e o SMS? e o push notification?" |
| Edge cases ausentes | O que acontece se o e-mail bounce? Se o usuário desativou? |
| Mistura spec com decisão técnica (SendGrid/SES/SQS) | Acopla o "o quê" ao "como" desnecessariamente |
| Nenhum ID de requisito | Impossível rastrear qual requisito um PR implementou |

---

## ✅ Spec Boa — Score: 87/100

```markdown
# Spec: Notificações por E-mail — Atividades da Conta

**Versão:** 1.0 | **Status:** Aprovada | **Data:** 2025-01-15

## 1. Resumo
Enviar notificações por e-mail transacional para usuários quando eventos relevantes
da conta ocorrerem, com controle granular de preferências de notificação.

## 2. Contexto e Motivação
**Problema:** Usuários perdem ações importantes (ex: novo comentário, pagamento processado)
porque só descobrem ao acessar o app. Resultado: engajamento tardio e abandono de tarefas.
**Evidência:** 68% dos usuários inativos citaram "não sabia que tinha algo esperando"
na pesquisa de churn de Dez/2024.
**Por que agora:** Plataforma de e-mail contratada (SendGrid), integração viável em 1 sprint.

## 3. Goals
- [ ] G-01: Usuários recebem e-mail em < 2 min após evento gatilho
- [ ] G-02: Taxa de abertura ≥ 25% (benchmark: 21% no setor)
- [ ] G-03: 100% dos usuários conseguem desativar notificações em ≤ 3 cliques

## 4. Non-Goals
- NG-01: Notificações push (mobile) — versão futura
- NG-02: Notificações por SMS — fora do roadmap 2025
- NG-03: E-mails de marketing / newsletter — escopo do time de Growth
- NG-04: Suporte a múltiplos endereços de e-mail por usuário

## 5. Usuários
**Primário:** Usuário com conta ativa, qualquer plano.
**Jornada atual:** Usuário precisa entrar no app para ver se há novidades.
**Jornada futura:** Usuário recebe e-mail com resumo do evento e link direto para a ação.

## 6. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | O sistema deve enviar e-mail quando um comentário for adicionado a um item do usuário | Must | E-mail recebido em < 2 min em 95% dos casos (teste com 100 envios) |
| RF-02 | O sistema deve enviar e-mail quando um pagamento for processado (sucesso ou falha) | Must | E-mail recebido em < 2 min; inclui valor, data e status |
| RF-03 | O usuário deve poder desativar cada tipo de notificação individualmente em Configurações > Notificações | Must | Toggle persiste após logout/login; e-mail do tipo desativado não é enviado |
| RF-04 | O sistema deve incluir link de "cancelar todas as notificações" no rodapé de todo e-mail | Must | Link funciona sem login; redireciona para página de confirmação |
| RF-05 | O sistema deve agrupar notificações do mesmo tipo em digest diário quando houver > 5 eventos em 1h | Should | Usuário recebe 1 e-mail com lista dos 5+ eventos, não 5+ e-mails separados |

### Fluxo Principal (RF-01)
1. Usuário B comenta no item X do Usuário A
2. Sistema detecta evento `comment.created`
3. Sistema verifica se Usuário A tem RF-01 ativado (padrão: ativo)
4. Sistema envia e-mail para Usuário A com: nome do comentador, trecho do comentário (máx. 200 chars), link direto para o item
5. Resultado: Usuário A recebe e-mail em < 2 min

## 7. Requisitos Não-Funcionais
| ID | Requisito | Target |
|----|-----------|--------|
| RNF-01 | Latência de envio | P95 < 2min após evento |
| RNF-02 | Taxa de entrega | ≥ 98% (excluindo bounces permanentes) |
| RNF-03 | Segurança | Links de unsubscribe com token único e assinado |

## 11. Edge Cases

| ID | Cenário | Trigger | Comportamento |
|----|---------|---------|---------------|
| EC-01 | E-mail inválido/bounce permanente | SendGrid retorna hard bounce | Desativar envios para esse e-mail; notificar usuário in-app |
| EC-02 | Usuário desativou notificações | `user.notifications.comments = false` | Não envia; não registra erro |
| EC-03 | SendGrid indisponível | Timeout ou erro 5xx | Retry com backoff: 1min, 5min, 30min. Após 3 falhas: logar e alertar time |
| EC-04 | Usuário deletou conta antes do envio | User ID não encontrado na fila | Descartar silenciosamente; logar para auditoria |
| EC-05 | Mesmo evento dispara 2x | Bug de duplicidade | Deduplicar por event_id com TTL de 1h |

## 14. Open Questions
| # | Pergunta | Impacto | Prazo |
|---|---------|---------|-------|
| OQ-01 | ⚠️ ABERTO: Digest diário (RF-05) — qual o horário do envio? Timezone do usuário ou UTC? | Médio | 20/01 |
```

### Por que é boa:

| Ponto forte | Benefício |
|------------|-----------|
| Cada requisito tem ID, prioridade e critério de aceite | QA escreve testes direto da tabela |
| Non-goals explícitos (4 itens) | Time sabe exatamente o que recusar |
| Edge cases cobrem falhas externas | Dev implementa retry sem precisar perguntar |
| Métricas numéricas (< 2min, ≥ 25%) | Sucesso é verificável |
| Open Question sinalizada com `⚠️ ABERTO:` | Ambiguidade visível, não silenciosa |
| Fluxo principal passo a passo | LLM implementa sem suposições |

---

## 🔶 Spec Média — Score: 63/100

```markdown
# Spec: Login com Google

## Objetivo
Permitir que usuários façam login usando a conta Google deles.

## Requisitos
- RF-01: Adicionar botão "Entrar com Google" na tela de login
- RF-02: Usuário deve ser redirecionado para OAuth do Google
- RF-03: Após autenticação, criar sessão do usuário
- RF-04: Se o e-mail já existe no sistema, fazer login na conta existente
- RF-05: Se o e-mail não existe, criar nova conta automaticamente

## Fora do escopo
- Login com Facebook/Apple por enquanto

## Edge Cases
- E se o usuário cancelar o fluxo OAuth?
- E se o Google estiver fora do ar?
```

### O que está bom:
- Requisitos numerados ✅
- Non-goals presentes ✅
- Edge cases identificados (mas sem resposta) ⚠️

### O que está faltando (-37 pontos):
- Edge cases sem comportamento definido — "e se?" sem resposta (-10)
- Nenhum critério de aceite nos requisitos (-7)
- Seção de segurança ausente (dados OAuth, tokens) (-8)
- Sem métricas de sucesso (-7)
- RF-03 "criar sessão" — por quanto tempo? Com quais dados? (-5)
