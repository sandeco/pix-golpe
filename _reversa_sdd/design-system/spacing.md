# Espaçamento, grid e layout: pix-golpe

> Gerado pelo Design System (Reversa) em 2026-09-21 a partir de `static/index.html`. 🟢 extraído do CSS.

## Frame e escala

| Token | Valor | Conf. |
|---|---|---|
| largura do frame | 1920 px fixos (`#frame`, `#stage`), centralizado | 🟢 |
| escala | `zoom = min(1, clientWidth / 1920)` via JS (`fitStage`) | 🟢 |
| padding do palco | `0 32px 24px` | 🟢 |
| gutter lateral efetivo | 32 px | 🟢 |
| topbar | sticky, `min-height 92px`, `padding 16px 0`, z-index 10 | 🟢 |
| proporção alvo | 16:9 para gravação; página rolável abaixo (lista cresce) | 🟢 |

## Grid

| Região | Definição | Conf. |
|---|---|---|
| `#stage` | `display: grid; gap: 18px` (linhas: topbar, race, footer) | 🟢 |
| `.race` | `grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 24px; align-items: start` | 🟢 |
| `.lane` | `padding: 20px 24px`, borda 1px + borda superior 4px na cor do acento | 🟢 |
| `.final-columns` / `#report-columns` | duas colunas (cartão final e relatório) | 🟢 |
| `.detail-body` | 2 colunas; 1 coluna abaixo de 1050 px (`@media (max-width: 1050px)`) | 🟢 |
| `.orange-grid` | `--columns` 1 a 6 conforme quantidade de laranjas | 🟢 (JS) |
| `.cash-grid` | `--columns` = ceil(√n), `--size` 4 a 24 px | 🟢 (JS) |

## Escala de espaçamento (gap/padding observados)

| Valor | Ocorrências | Papel sugerido |
|---|---|---|
| 4 px | badges | `space-1` |
| 6 / 7 / 8 px | gaps pequenos, padding de badge | `space-2` |
| 10 / 12 px | gaps médios (12 é o 2º mais usado) | `space-3` |
| 14 / 16 px | gap padrão (16 é o mais usado) | `space-4` |
| 18 / 20 px | gaps de seção, padding de lane | `space-5` |
| 22 / 24 / 25 px | padding de cartões, gap entre lanes | `space-6` |
| 28 / 30 px | padding de dialogs (`28px 38px`, `30px 38px`), gap da topbar | `space-7` |
| 38 px | padding horizontal de dialogs | `space-8` |

Escala base recomendada ao reimplementar: 4 px (4, 8, 12, 16, 20, 24, 32, 40). 🟡

## Breakpoints

| Breakpoint | Comportamento | Conf. |
|---|---|---|
| < 1920 px | tudo escala por `zoom` (não é responsivo, é proporcional) | 🟢 |
| ≤ 1050 px | modal de detalhes em 1 coluna, padding 18 px, h2 menor | 🟢 |
| `prefers-reduced-motion: reduce` | sem transição na barra, sem pulse no GOLPE, sombra estática | 🟢 |

## Alturas de controle

| Controle | Altura | Conf. |
|---|---|---|
| botão primário `.start` | 57 px, `min-width 170px`, padding `0 28px` | 🟢 |
| botão secundário `.report-button` | 57 px, padding `0 20px` | 🟢 |
| select | padding `15px 38px 15px 16px` | 🟢 |
