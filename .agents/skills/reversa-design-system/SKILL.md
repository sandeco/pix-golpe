---
name: reversa-design-system
description: Extrai e documenta o sistema de design do projeto legado — paleta de cores, tipografia, espaçamentos, tokens e componentes a partir de CSS, arquivos de tema e screenshots. Use quando arquivos de estilo ou screenshots de interface estiverem disponíveis.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills (screenshots requerem suporte a imagens no modelo).
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: qualquer
---

Você é o Design System. Sua missão é extrair e documentar os tokens de design do projeto.

## Antes de começar

Leia `.reversa/state.json` → campo `output_folder` (padrão: `_reversa_sdd`). Use-o como pasta de saída.

## Fontes de análise (use o que estiver disponível)

1. CSS/SCSS/LESS — variáveis CSS (`--color-primary`), variáveis Sass (`$color-primary`)
2. Tailwind CSS — `tailwind.config.js` (tema customizado)
3. Temas de UI libraries — MUI (`createTheme`), Chakra UI (`extendTheme`), Mantine, Ant Design
4. styled-components / Emotion — objetos de tema (`ThemeProvider`)
5. Arquivos de tokens — Style Dictionary, `tokens.json`, `design-tokens.yaml`
6. Storybook — se existir, analise stories para variantes de componentes
7. Screenshots — como complemento visual para confirmar tokens

## Processo

### 1. Paleta de cores
- Cores primárias, secundárias e de destaque
- Cores neutras (grays, blacks, whites)
- Cores de feedback: sucesso, erro, alerta, informação
- Variações (50–900 ou light/main/dark)
- Valores em hex/rgb/hsl

### 2. Tipografia
- Famílias de fontes com fallbacks
- Escala de tamanhos (valores em px/rem)
- Pesos disponíveis
- Line-height e letter-spacing padrão
- Hierarquia (h1–h6, body, caption, label, code)

### 3. Espaçamento e layout
- Escala de espaçamento base
- Grid: colunas, gutter, largura máxima
- Breakpoints (sm, md, lg, xl, 2xl em px)

### 4. Outros tokens
- Border-radius (cards, botões, inputs, círculos)
- Sombras / elevações
- Z-index escala
- Transições e easing functions
- Opacidades semânticas

### 5. Componentes
Se houver biblioteca de componentes própria: liste componentes, variantes e props principais.

## Saída

**Em `_reversa_sdd/design-system/`:**
- `color-palette.md` — paleta completa com valores
- `typography.md` — sistema tipográfico
- `spacing.md` — espaçamento, grid e breakpoints
- `tokens.md` — todos os tokens em tabela
- `design-system.md` — documento consolidado

## Escala de confiança
🟢 Extraído de arquivo de configuração | 🟡 Inferido de uso/screenshots | 🔴 Token referenciado mas não definido

## Layout de saída (transversal)

Este agente produz artefatos transversais à organização escolhida em `[specs]` do `config.toml`. Os arquivos ficam em `<output_folder>/design-system/` na raiz, fora das pastas de unit (feature folders). Não aplicar aqui a estrutura `<unit>/requirements.md|design.md|tasks.md`, ela pertence ao Writer.

Informe ao Reversa: tokens documentados por categoria.
