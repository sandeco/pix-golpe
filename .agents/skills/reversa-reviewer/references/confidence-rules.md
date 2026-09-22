# Regras de Classificação de Confiança

Use esta escala em **toda** afirmação nas specs. Sem exceções.

## Definições

| Símbolo | Nome | Significado |
|---------|------|-------------|
| 🟢 | CONFIRMADO | Extraído diretamente do código — pode ser citado com arquivo e linha |
| 🟡 | INFERIDO | Deduzido de padrões, nomes, convenções ou contexto — pode estar errado |
| 🔴 | LACUNA | Não foi possível determinar pelo código — requer validação humana |

## Quando usar cada nível

### 🟢 CONFIRMADO
- O comportamento está explícito no código (if/else, return, throw)
- O valor é uma constante ou enum definido no código
- A regra está em um comentário descritivo junto ao código relevante
- Existe um teste automatizado que cobre exatamente esse comportamento
- A DDL/migration define a constraint diretamente

### 🟡 INFERIDO
- O nome da função/variável sugere o comportamento, mas não há lógica explícita
- O comportamento é consistente com convenções do framework (ex: soft delete em Eloquent)
- Há indícios no código mas a lógica completa não está visível no escopo analisado
- A regra foi inferida de múltiplos exemplos semelhantes, não de uma definição única
- Comentário antigo ou TODO que pode não refletir o estado atual

### 🔴 LACUNA
- A funcionalidade é referenciada mas não implementada no código visível
- A lógica depende de configuração externa não acessível (variável de ambiente, banco, API)
- O comportamento esperado contradiz o que está no código (possível bug ou lógica oculta)
- Código gerado ou compilado sem acesso ao source original
- Regra de negócio que só existe na cabeça dos stakeholders

---

## Reclassificação durante revisão

### Upgrade: 🟡 → 🟢
Condições: encontrar evidência direta no código que confirma a afirmação.
Ação: anote a evidência (arquivo + linha) na spec.

### Upgrade: 🔴 → 🟡
Condições: encontrar indícios suficientes para uma inferência razoável.
Ação: reformule a afirmação como inferência, não certeza.

### Upgrade: 🔴 → 🟢
Condições: o usuário confirma com evidência concreta (ex: "sim, essa é a regra").
Ação: atualize a spec e registre a confirmação.

### Downgrade: 🟢 → 🟡
Condições: encontrar contradição entre a spec e o código real.
Ação: sinalize a contradição e reclassifique.

### Downgrade: 🟡 → 🔴
Condições: encontrar evidência de que a inferência estava errada.
Ação: reclassifique e crie pergunta para o usuário se necessário.

---

## Regra de ouro

**Quando houver dúvida, use o nível mais baixo.**
Uma 🔴 honesta é mais útil do que uma 🟡 enganosa.
