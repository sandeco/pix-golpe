# Tokens: pix-golpe

> Gerado pelo Design System (Reversa) em 2026-09-21. Tabela consolidada. Os nomes de token são propostos (o CSS só define `--accent`, `--accent-light`, `--accent-dark`, `--columns`, `--size`); os valores são 🟢 extraídos do CSS/JS salvo indicação.

## Cor

| Token | Valor | Origem |
|---|---|---|
| color.bg | #080b12 | `:root` |
| color.surface.1 | #0b0f18f5 | `.topbar` |
| color.surface.2 | #0b1320 | cartões |
| color.surface.3 | #111722 | cartões |
| color.surface.4 | #171e2b | select |
| color.surface.5 | #1b2536 | botão secundário |
| color.surface.6 | #29374e | hover |
| color.border.1 | #354052 | select |
| color.border.2 | #53627c | botão secundário |
| color.text.primary | #f3f5fa | `:root` |
| color.text.strong | #eef4f8 / #fff | títulos |
| color.text.secondary | #a7b1c1 | rótulos |
| color.text.muted | #77869c | metadados |
| color.text.on-primary | #111923 | botão primário |
| color.accent.rust | #ff2d95 | `--accent` |
| color.accent.rust.light | #ff8cc6 | `--accent-light` |
| color.accent.rust.dark | #55223f | `--accent-dark` |
| color.accent.python | #6985f6 | `--accent` |
| color.accent.python.light | #a7b8ff | `--accent-light` |
| color.accent.python.dark | #26355f | `--accent-dark` |
| color.danger.bg | #d62d42 | veredito GOLPE |
| color.danger.border | #ff6975 | |
| color.danger.strong | #c72c42 | botão Parar |
| color.danger.text | #ff526b | células de erro |
| color.success | #59e0a4 | conexão OK, célula tp |
| color.success.bg | #143929 | |
| color.warning | #ffad61 | laranjas, SUSPEITA |
| color.warning.soft | #ffd2a1 | |
| color.pending | #f3bb62 | conexão pendente |
| color.overlay.hairline | #ffffff12 | bordas sutis (9 usos) |
| color.overlay.glow | #ffffff18 | hover do botão primário |

## Tipografia

| Token | Valor |
|---|---|
| font.family | "Segoe UI", Arial, sans-serif |
| font.size.display-xl | 108px |
| font.size.display-l | 100px |
| font.size.display-m | 50px |
| font.size.h1 | 42px |
| font.size.display-s | 34px |
| font.size.h2 | 29px |
| font.size.h3 | 26px |
| font.size.body-xl | 22px |
| font.size.body-l | 19px |
| font.size.body | 16px |
| font.size.body-s | 15px |
| font.size.caption | 13px |
| font.size.micro | 12px |
| font.weight.regular | 450 |
| font.weight.medium | 500 |
| font.weight.semibold | 650 |
| font.weight.bold | 750 |
| font.weight.black | 900 |
| line-height.tight | 1 |
| line-height.heading | 1.15 |
| line-height.body | 1.4 |
| letter-spacing.display | -7px |
| letter-spacing.heading | -1.8px |
| letter-spacing.label | 1px |

## Espaço e layout

| Token | Valor |
|---|---|
| layout.frame | 1920px |
| layout.gutter | 32px |
| layout.topbar.height | 92px |
| space.1 … space.8 | 4, 8, 12, 16, 20, 24, 30, 38 px |
| grid.race.gap | 24px |
| grid.stage.gap | 18px |
| control.height | 57px |
| breakpoint.detail-stack | 1050px |

## Raio

| Token | Valor | Uso |
|---|---|---|
| radius.xs | 5px | badges |
| radius.s | 9px / 10px | chips, células |
| radius.m | 12px | botões, select, cartões |
| radius.l | 14px | painéis |
| radius.xl | 22px | dialogs |
| radius.full | 50% | pontos, moedas, avatar |

## Sombra

| Token | Valor | Uso |
|---|---|---|
| shadow.dialog | 0 24px 120px #000c | modal |
| shadow.overlay | 0 20px 100px #000a | cartão final |
| shadow.glow.primary | 0 0 24px #ffffff18 | botão primário hover |
| shadow.glow.success | 0 0 12px #59e0a433 | conexão |
| shadow.glow.warning | 0 0 14px #ffe09c80 | laranjas |
| shadow.ring.danger | 0 0 0 5px #ff435426, 0 0 30px #ff435438 | pulse GOLPE |
| shadow.ring.danger.static | 0 0 0 4px #ff435438 | reduced-motion |
| shadow.inset.warning | inset 0 0 0 1px #ffd2a1 | |

## Movimento

| Token | Valor | Uso |
|---|---|---|
| motion.progress | width 140ms linear | barra |
| motion.pulse | 720ms ease-in-out infinite | selo GOLPE |
| motion.flash | 600ms ease-out, opacidade 0,6 → 0 (reduzido: 0,22 → 0) | `alert-wash` |
| motion.wave | 300ms | onda do grafo |
| motion.coins | 1000ms linear, delay 250ms por seta + 125ms por moeda | fluxo do dinheiro |
| motion.reduced | tudo desligado sob `prefers-reduced-motion` | |

## Z-index

| Token | Valor |
|---|---|
| z.topbar | 10 |
| z.overlay (final, report, modal) | acima do palco 🟡 (valor não lido) |

## Ícones e formas
- Sem biblioteca de ícones. Símbolos de veredito em texto: `!`, `✓`, `?`, `×`, `–`. Avatar do golpista em SVG inline (círculo + busto). Moedas `$` em `<i class="coin">`. 🟢
