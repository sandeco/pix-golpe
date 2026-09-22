# Tipografia: pix-golpe

> Gerado pelo Design System (Reversa) em 2026-09-21 a partir de `static/index.html`. 🟢 extraído do CSS.

## Família

| Token | Valor | Conf. |
|---|---|---|
| `font-family` | `"Segoe UI", Arial, sans-serif` (`:root`) | 🟢 |
| `font-synthesis` | `none` | 🟢 |
| pesos variáveis usados | 450, 500, 600, 650, 700, 750, 800, 850, 900 (Segoe UI Variable no Windows 11; em outros sistemas os pesos intermediários arredondam) 🟡 | 🟢 |

## Escala de tamanhos (px) e uso

| Token (proposto) | px | Uso | Conf. |
|---|---|---|---|
| `display-xl` | 108 | contador gigante "143" (`.processed`) | 🟢 |
| `display-l` | 100 | tempo total no cartão final | 🟢 |
| `display-m` | 50 | métricas do relatório (83,3%) | 🟢 |
| `h1` | 42 | "DETECTOR DE GOLPE", peso 900, letter-spacing −1,8px | 🟢 |
| `display-s` | 34 | números do cartão | 🟢 |
| `h2-lane` | 29 / 30 | "Rust + Jev", peso 750, ls −0,8px | 🟢 |
| `h2-dialog` | 26 a 28 | títulos de relatório e modal | 🟢 |
| `body-xl` | 22 a 24 | mensagem atual, botão Iniciar (22, peso 750) | 🟢 |
| `body-l` | 19 a 21 | select, botão secundário (19, peso 650) | 🟢 |
| `body` | 16 a 18 | texto de golpes na lista, legendas | 🟢 |
| `body-s` | 15 (9 usos, o mais comum) | rótulos e notas | 🟢 |
| `caption` | 13 a 14 | rótulos de velocidade, metadados | 🟢 |
| `micro` | 12 | selo GOLPE, contagem "N×" | 🟢 |

## Line-height

| Valor | Uso |
|---|---|
| 1 | contador gigante |
| 1,15 / 1,2 | títulos |
| 1,3 / 1,4 / 1,45 / 1,5 | corpo e listas |
| fixos 14, 17, 20, 26, 30, 34 px | elementos de altura controlada |

## Letter-spacing

| Valor | Uso |
|---|---|
| −7px, −5px | display gigante (contador, tempo) |
| −1,8px, −1px, −0,8px, −0,7px, −0,5px | títulos e números grandes |
| 0 | corpo |
| +1px, +1,5px, +2px | rótulos em caixa alta ("MENSAGENS PROCESSADAS", "GOLPISTA") |

## Hierarquia observada (screenshots)

1. Contador + "/ 1000" (display-xl + body-l).
2. Título do lado (h2-lane) na cor do acento.
3. Mensagem atual (body-xl) e selo de veredito (body-l, caixa alta).
4. Rótulos em caixa alta com tracking positivo (caption).
5. Lista de golpes: remetente (micro, cor do acento), texto (body), badge + tipo + % (micro/caption).

## Números

`Intl.NumberFormat('pt-BR')`: inteiros sem agrupamento no contador, com agrupamento em "contas"; 1 casa em ms; moeda USD com 6 casas (custo por decisão) e 2 a 3 casas (por 1.000). 🟢
