---
name: reversa-agents-help
description: Explica com analogias o que cada agente do Reversa faz e quando usá-lo. Ative com /reversa-agents-help.
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  role: help
---

Apresente exatamente o texto abaixo, sem alterações, sem resumir.

---

# Agentes do Reversa — guia com analogias

O Reversa é um time de especialistas. Cada agente faz uma coisa só — e faz bem.

---

## Menu principal

| O que você quer fazer? | Comando | Time |
|---|---|---|
| Descobrir e documentar um sistema legado | `/reversa` | Reversa Agents Core |
| Clarear a ideia antes de qualquer código | `/reversa-brainstorm` | Ideation Agents |
| Criar um projeto novo a partir de uma ideia | `/reversa-new` | Code New Project Agents |
| Implementar ou evoluir código a partir das specs | `/reversa-forward` | Code Forward Agents |
| Planejar a migração de um legado | `/reversa-migrate` | Migration Agents |
| Gerar um mini-site visual da documentação | `/reversa-docs` | Documentation Agents |
| Entender qual agente usar | `/reversa-agents-help` | Guia de agentes |

Os times de Pricing e Translators têm comandos especializados. Use `/reversa-pricing-profile`, `/reversa-pricing-size`, `/reversa-pricing-estimate` ou `/reversa-n8n` conforme a necessidade.

---

## 💡 Reversa Brainstorm, a mesa antes da obra
**Comando:** `/reversa-brainstorm`

Antes de o pedreiro levantar parede, alguém senta na mesa e pergunta o que se quer com a casa: para quem é, o que dói morar como está hoje, quais os caminhos possíveis, o que pode dar errado. Ninguém desenha planta nessa mesa. Só se decide o que vale construir.

> Use o Reversa Brainstorm quando a ideia ainda está bruta, em projeto novo ou em legado. Ele conduz `Framer → Explorer → Challenger → Arbiter → Pre-Spec` e entrega o resultado ao `/reversa-new` (greenfield) ou ao `/reversa-requirements` (legado).

**Os cinco da mesa:**

| Agente | Analogia | Comando |
|---|---|---|
| **Framer** | O médico que não aceita "quero remédio X" e pergunta onde dói | `/reversa-framer` |
| **Explorer** | O guia que mostra todas as trilhas, inclusive a de não subir a montanha | `/reversa-explorer` |
| **Challenger** | O advogado do diabo que já viu esse projeto fracassar antes | `/reversa-challenger` |
| **Arbiter** | O juiz que dá o veredito e assume o que se perde com ele, mas quem decide é você | `/reversa-arbiter` |
| **Pre-Spec** | O escrivão que entrega o mínimo para a obra começar, e nada além | `/reversa-pre-spec` |

---

## 🆕 Reversa New — o fundador de produto
**Comando:** `/reversa-new`

O fundador começa com uma ideia ainda bruta, investiga o problema, entende para quem o produto existe, consolida um PRD e transforma tudo em especificações prontas para implementação.

> Use o Reversa New para projetos greenfield. Ele conduz `Ideator → Researcher → Drafter → Spec SDD` e entrega o resultado ao `/reversa-forward`.

---

## 🎼 Reversa — orquestrador central
**Comando:** `/reversa`

Um regente de orquestra não toca nenhum instrumento. Ele conhece a partitura inteira e diz quem entra quando, em que ordem, em que ritmo. Sem ele, cada músico tocaria sua parte sem se conectar com os outros.

> Use o Reversa para iniciar ou retomar a análise completa. Ele cuida da sequência por você.

---

## 🗺️ Scout — o corretor de imóveis
**Comando:** `/reversa-scout`

O corretor faz o primeiro tour no imóvel. Não abre gavetas, não lê documentos, não mexe em nada. Só mapeia: quantos cômodos, qual o bairro, que instalações existem, qual o estado geral.

> Use o Scout no começo. Ele gera o inventário do projeto — linguagens, frameworks, módulos, dependências — sem entrar no código.

---

## 🧬 Soul Extractor: o biógrafo expresso
**Comando:** `/reversa-extract-soul`

O biógrafo expresso visita o personagem, lê as anotações do corretor (Scout), folheia rapidamente alguns álbuns de família e o histórico de cartas (git log), e produz uma biografia de uma página: quem é, o que faz, e as decisões fundadoras que moldaram a vida toda. Não é a história completa, é a alma destilada.

> Use o Soul Extractor logo após o Scout, quando quiser uma síntese executiva do sistema (propósito, entidades centrais e decisões fundadoras) numa única Spec, sem esperar todo o pipeline. Não substitui Archaeologist nem Detective.

---

## ⛏️ Archaeologist — o escavador
**Comando:** `/reversa-archaeologist`

O arqueólogo escava o terreno com paciência, camada por camada. Cataloga cada artefato encontrado: tamanho, material, localização, forma. Ele não interpreta a civilização, só descreve com precisão o que está lá.

> Use o Archaeologist para analisar o código módulo a módulo. Ele extrai funções, algoritmos, estruturas de dados e fluxos de controle. **Roda um módulo por sessão** para economizar tokens.

---

## 🔍 Detective — o Sherlock Holmes
**Comando:** `/reversa-detective`

Sherlock Holmes chega depois do arqueólogo. Olha para os artefatos catalogados e pergunta: *"Mas por que isso está aqui? Quem colocou? O que isso revela sobre quem viveu aqui?"* Ele não escava. Ele interpreta.

> Use o Detective após o Archaeologist. Ele extrai regras de negócio implícitas, lê o histórico git como um diário e reconstrói decisões que ninguém documentou.

---

## 📐 Architect — o cartógrafo
**Comando:** `/reversa-architect`

O cartógrafo visita um território e produz mapas formais: planta baixa, mapa de elevação, planta estrutural. Alguém que nunca pisou lá consegue entender tudo olhando para os mapas.

> Use o Architect após o Detective. Ele sintetiza tudo em diagramas C4, ERD completo e mapa de integrações.

---

## 📝 Writer — o tabelião
**Comando:** `/reversa-writer`

O tabelião transforma o que foi descoberto em contratos formais, precisos e rastreáveis. Cada cláusula tem grau de certeza declarado. O documento vale como contrato: um agente de IA pode reimplementar o sistema a partir dele.

> Use o Writer após o Architect. Ele gera as specs SDD, OpenAPI e user stories com rastreabilidade de código.

---

## ⚖️ Reviewer — o revisor de specs
**Comando:** `/reversa-reviewer`

O Reviewer pega os contratos do Writer e tenta furar: *"Isso é contradição. Esse ponto não tem prova. Essa regra some se o usuário fizer X."* Ele não quer destruir, quer garantir que o que ficou de pé seja sólido.

> Use o Reviewer após o Writer. Ele revisa criticamente as specs, reclassifica confiança e levanta perguntas para validação humana.

---

## 🖼️ Visor — o ilustrador forense
**Comando:** `/reversa-visor`

O ilustrador forense trabalha só com imagens. Recebe screenshots do sistema e reconstrói fielmente a interface: telas, formulários, fluxos de navegação. Não precisa que o sistema esteja rodando — só das fotos.

> Use o Visor quando tiver screenshots disponíveis. Ele documenta a UI sem precisar de acesso ao sistema.

---

## 🗄️ Data Master — o geólogo
**Comando:** `/reversa-data-master`

O geólogo mapeia o subsolo — a camada que ninguém vê mas que sustenta tudo. Tabelas, relacionamentos, constraints, triggers, procedures. A fundação invisível sobre a qual a aplicação está construída.

> Use o Data Master quando houver DDL, migrations ou modelos ORM disponíveis. Ele documenta o banco completamente.

---

## 🎨 Design System — o estilista
**Comando:** `/reversa-design-system`

O estilista cataloga o guarda-roupa: paleta de cores, tipografia, espaçamentos, tokens de design. As "regras de moda" que governam a aparência do sistema — o que pode e o que não pode ser combinado.

> Use o Design System quando houver arquivos CSS, temas ou screenshots de interface. Ele extrai os tokens visuais do projeto.

---

## Sequência recomendada

```
Projeto legado: /reversa → descoberta e especificações
Projeto novo:   /reversa-new → PRD e specs → /reversa-forward
Migração:       /reversa → /reversa-migrate → /reversa-forward

Pipeline legado manual:
Scout → Archaeologist (N sessões) → Detective → Architect → Writer → Reviewer

Opcionais em qualquer fase:
Soul Extractor · Visor · Data Master · Design System · Reversa Docs
```
