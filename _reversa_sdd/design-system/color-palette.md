# Paleta de cores: pix-golpe

> Gerado pelo Design System (Reversa) em 2026-09-21 a partir de `static/index.html` (CSS inline, linhas 8-207, e constantes JS) e dos screenshots em `docs/`. Tema escuro único (`color-scheme: dark`), sem variante clara. 🟢 extraído do CSS/JS, 🟡 inferido de uso/screenshot.

## Cores de marca (por lado)

| Token | Valor | Uso | Conf. |
|---|---|---|---|
| `--accent` (rust) | `#ff2d95` | título, borda superior, progresso, números, selo do lado Rust + Jev | 🟢 `.lane`, `ACCENTS.rust` |
| `--accent-light` (rust) | `#ff8cc6` | texto de destaque claro | 🟢 |
| `--accent-dark` (rust) | `#55223f` | fundos de badge/seleção | 🟢 |
| `--accent` (python) | `#6985f6` | idem para Python + DeepSeek | 🟢 `.lane.python`, `ACCENTS.python` |
| `--accent-light` (python) | `#a7b8ff` | | 🟢 |
| `--accent-dark` (python) | `#26355f` | | 🟢 |
| rgb dos acentos | `255,45,149` / `105,133,246` | canvas com alfa | 🟢 `ACCENT_RGB` |
| gradiente de fundo | `radial-gradient(#ff2d9514 …)` e equivalente azul | `#stage` | 🟢 |

## Superfícies (neutros escuros)

| Token (proposto) | Valor | Uso | Conf. |
|---|---|---|---|
| `surface-0` | `#080b12` | fundo da página (`:root background`) | 🟢 |
| `surface-1` | `#0b0f18f5` | topbar sticky (translúcido) | 🟢 |
| `surface-2` | `#0b1320` | cartões, painéis, células | 🟢 (5 usos) |
| `surface-3` | `#111722` | cartões secundários | 🟢 |
| `surface-4` | `#171e2b` | select | 🟢 |
| `surface-5` | `#1b2536` | botão secundário | 🟢 |
| `surface-6` | `#29374e` | botão secundário hover | 🟢 |
| borda | `#354052`, `#53627c` | select, botão secundário | 🟢 |
| realce translúcido | `#ffffff04` … `#ffffff22` (12 variantes) | fundos e bordas sutis | 🟢 |

## Texto

| Token (proposto) | Valor | Uso | Conf. |
|---|---|---|---|
| `text-primary` | `#f3f5fa` | corpo | 🟢 `:root color` |
| `text-strong` | `#fff` / `#eef4f8` | títulos, botão primário (fundo) | 🟢 |
| `text-secondary` | `#a7b1c1`, `#a7b4c7`, `#a6b1c2`, `#b7c4d7`, `#dbe5f3` | rótulos, legendas, notas | 🟢 (variações próximas, candidatas a unificar 🟡) |
| `text-muted` | `#9da9ba`, `#77869c` | metadados | 🟢 |
| texto sobre botão primário | `#111923` | `.start` | 🟢 |

## Feedback e semântica

| Token (proposto) | Valor | Uso | Conf. |
|---|---|---|---|
| `danger` (GOLPE) | `#d62d42` fundo, `#ff6975` borda, `#fff` texto | `.verdict[data-verdict="golpe"]` | 🟢 |
| `danger-glow` | `#ff435426`, `#ff435438` | `@keyframes pulse` | 🟢 |
| `danger-strong` | `#c72c42` / `#e1374f` | botão Parar e hover | 🟢 |
| `danger-text` | `#ff304a`, `#ff526b`, `#ff5266`, `#ff818c`, `#ff97a7`, `#ffe0e5` | células de erro no relatório, badges | 🟢 |
| `success` (OK) | `#59e0a4` (+ `#59e0a433` glow), `#79efb5`, `#143929` fundo | conexão conectada, célula tp | 🟢 |
| `warning` (SUSPEITA) | `#f3bb62` (conexão pendente), `#ffad61`, `#ffb771`, `#ffd2a1`, `#ffda79`, `#ffde83`, `#ffe09c80` | laranjas no grafo/fluxo, SUSPEITA | 🟢 |
| `purple` (saque) | não definido em hex fixo; SPEC §5 pede roxo 🟡 | nós de saque no canvas | 🟡 |
| foco | `outline: 3px solid #fff`, offset 5px | `:focus-visible` | 🟢 |

## Canvas (grafo)

| Elemento | Cor | Conf. |
|---|---|---|
| estrelas de fundo | branco com alfa 0,08 a 0,24 | 🟢 `stars` |
| nó chave | acento do lado | 🟡 (visto no screenshot: vermelho/rosa) |
| laranjas | laranja `#ffad61` família | 🟡 |
| saque | roxo/rosa escuro | 🟡 |
| demais nós | acento com alfa ∝ suspeita | 🟢 `drawGraph` |

## Observações
- A paleta é ad hoc: 60+ hex distintos, muitos a 1 uso. Recomenda-se consolidar em ~20 tokens (tabela acima) ao reimplementar. 🟡
- Contraste: texto `#f3f5fa` sobre `#080b12` ≈ 17:1; `#a7b1c1` sobre `#0b1320` ≈ 8:1. Acentos sobre fundo escuro ≥ 5:1. 🟡 (cálculo aproximado)
