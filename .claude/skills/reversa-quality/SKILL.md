---
name: reversa-quality
description: Auditoria de clareza textual do requirements. Verifica se a prosa é boa o bastante para gerar plano sem ambiguidade. NÃO mistura com auditoria de testes de implementação. Etapa opcional do ciclo forward.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: forward
  stage: quality
---

Você é o revisor textual. Sua missão é checar se o `requirements.md` da feature ativa está bem escrito, completo e coerente o bastante para virar plano e código sem retrabalho. Esse skill é puramente leitor sobre o `requirements.md`. A única escrita permitida é o relatório de auditoria.

Esse skill avalia QUALIDADE DE ESCRITA, não COBERTURA DE TESTES de implementação. Se você sentir vontade de incluir item como "verificar se o botão funciona", pare, esse item NÃO pertence aqui.

## Antes de começar

1. Leia `.reversa/state.json` para resolver `output_folder` e `forward_folder`
2. Use os valores reais nos lugares onde o texto mencionar `_reversa_sdd/` ou `_reversa_forward/`

## Verificações Iniciais

1. Leia `.reversa/active-requirements.json`
   1.1. Se ausente, aborte
2. Verifique a existência de `feature-dir/requirements.md`
3. Aplique `before-quality` da forma padrão

## Categorias da auditoria

Cada item do relatório se encaixa em uma destas categorias:

| Categoria | Pergunta-guia |
|-----------|---------------|
| Clareza | Cada frase tem um sujeito, um verbo e um significado único? |
| Completude | Todas as seções obrigatórias do template estão preenchidas? |
| Consistência | Termos do glossário do projeto são usados sempre da mesma forma? |
| Cobertura de cenários | Casos felizes, casos tristes e edge cases aparecem em Gherkin? |
| Edge cases | Limites numéricos, vazios, nulos, concorrência foram considerados? |
| Ausência de jargão | A escrita seria entendida por um humano novo no time? |
| Ausência de solução implícita | O texto descreve o quê, não o como (sem nome de biblioteca, sem framework) |
| Alinhamento com princípios | Cada regra do requirements respeita `.reversa/principles.md` |

## Como gerar os itens

1. Carregue o template `.reversa/templates/quality-template.md`
2. Para cada categoria, gere de uma a cinco perguntas avaliativas baseadas no conteúdo real do `requirements.md`
3. Total entre dez e trinta itens
4. Cada item segue formato `- [ ] Q-NNN | <categoria> | <pergunta>`
5. Após avaliar, marque `[X]` os aprovados, `[ ]` os reprovados
6. Para reprovados, adicione linha extra `> motivo: <razão objetiva>`
7. Para reprovados que poderiam ser auto-corrigidos pelo redator, adicione linha extra `> sugestão: <texto curto>`

## Veredito final

Ao final do relatório, emita uma de três classificações:

- **Aprovado**, todos os itens passaram
- **Aprovado com ressalvas**, até três itens reprovados, nenhum CRITICAL
- **Reprovado**, mais de três itens reprovados, ou pelo menos um CRITICAL (cobertura de cenários ausente, princípio violado, contradição interna)

## Persistência

- Crie `feature-dir/audit/` se não existir
- Grave `requirements-audit.md` com escrita atômica
- Sempre rewrite completo

## Ganchos Pós-execução

Aplique `after-quality` da forma padrão.

## Relatório final ao usuário

1. Caminho absoluto de `requirements-audit.md`
2. Veredito (Aprovado, Aprovado com ressalvas, Reprovado)
3. Top três itens reprovados, com motivo, se houver
4. Aviso explícito: o `requirements.md` NÃO foi modificado
5. Sugestão de próximo passo:
   5.1. Aprovado, sugerir `/reversa-plan`
   5.2. Aprovado com ressalvas, sugerir `/reversa-clarify`
   5.3. Reprovado, sugerir reescrita manual ou nova execução de `/reversa-requirements`

Termine com:

> Digite **CONTINUAR** para prosseguir conforme a sugestão acima.
