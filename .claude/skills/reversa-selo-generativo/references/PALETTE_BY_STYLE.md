# Paletas por Estilo Visual

Tabela das paletas usadas pelo selo, derivadas do estilo visual escolhido pelo usuário do `/reversa-documentation`.

Cada paleta tem 4 campos:

- `bg`: cor de fundo do canvas.
- `foreground`: lista de cores principais usadas pelo padrão (3 a 5 cores).
- `accent`: cor de destaque para elementos centrais (1 cor).
- `fg`: cor do texto do label fora do canvas.

---

## Paleta: `sober`

Estilo sóbrio, técnico, neutro. Foco em legibilidade e atemporalidade.

```json
{
  "bg": "#f5f3ee",
  "foreground": ["#3d4a5c", "#7c8a99", "#a06b4a", "#4f6b5d", "#bdb4a4"],
  "accent": "#1e2937",
  "fg": "#1e2937"
}
```

Tradução visual:
- Fundo: papel quebrado.
- Foreground: azul-petróleo, cinza-pedra, terracota, verde-musgo, areia.
- Accent: azul-meia-noite profundo.

**Variante dark**: para uso em mini-selo sobre header escuro, espelhar (bg ↔ fg).

---

## Paleta: `premium`

Estilo cinematográfico, luxuoso, dark. Foco em contraste e brilho.

```json
{
  "bg": "#0a0a14",
  "foreground": ["#d4af37", "#7a1c2a", "#b8b8b8", "#1e2b4f", "#3a3a4a"],
  "accent": "#f4d03f",
  "fg": "#eaeaea"
}
```

Tradução visual:
- Fundo: preto noite-azulada.
- Foreground: dourado, vermelho-vinho, prata, azul-meia-noite, cinza-fumaça.
- Accent: dourado claro (mais brilhante que o dourado base).

**Uso típico**: hero de apresentação executiva, selo de capa de documentação premium.

---

## Paleta: `dense`

Estilo denso, saturado, alta densidade visual. Foco em distinção entre múltiplas categorias.

```json
{
  "bg": "#f8f9fa",
  "foreground": ["#ff7a3e", "#00c6c6", "#e93f8f", "#a3d930", "#5b3fce"],
  "accent": "#1a1a2e",
  "fg": "#1a1a2e"
}
```

Tradução visual:
- Fundo: branco gelo.
- Foreground: laranja, ciano, magenta, lima, índigo.
- Accent: preto-azulado.

**Uso típico**: documentação de sistema com muitos componentes para distinguir; selo cobre múltiplos hues.

---

## Paleta: `exploratory`

Estilo exploratório, etéreo, luminoso. Foco em 3D e contemplação.

```json
{
  "bg": "#0d0d1a",
  "foreground": ["#ffb3ba", "#a0e7e5", "#c9b6e8", "#fff5b8", "#b8e0d2"],
  "accent": "#ffffff",
  "fg": "#eaeaea"
}
```

Tradução visual:
- Fundo: preto-violeta profundo.
- Foreground: rosa-aurora, ciano-glaciar, lilás-névoa, amarelo-suave, verde-aquoso.
- Accent: branco luz.

**Uso típico**: documentação com forte presença de cenas 3D; o selo dialoga com a estética da `arquitetura.html`.

---

## Paleta `other` (fallback)

Quando o usuário escolhe "Outro" no menu de estilo e fornece descrição livre, a skill mapeia a descrição para a paleta mais próxima, ou aplica heurística básica:

```javascript
function paletteFromFreeform(text) {
    const lower = text.toLowerCase();
    if (/(luxo|premium|cinematogr|dark)/.test(lower)) return palettes.premium;
    if (/(t[ée]cnico|s[óo]brio|clean|minimal)/.test(lower)) return palettes.sober;
    if (/(denso|saturado|colorido|vibra)/.test(lower)) return palettes.dense;
    if (/(explora|3D|luminoso|et[ée]reo)/.test(lower)) return palettes.exploratory;
    return palettes.sober; // fallback seguro
}
```

---

## Distribuição de cores dentro da paleta

Mesmo com 5 cores em `foreground`, o selo não usa todas igualmente. Regra de proporção visual:

| Posição na paleta | Proporção visual no selo |
|---|---|
| 1ª cor | 50% (dominante) |
| 2ª cor | 25% (secundária) |
| 3ª cor | 15% |
| 4ª cor | 7% |
| 5ª cor | 3% (vestígio) |

Padrões como `flow-field` e `wave-interference` herdam essa distribuição automaticamente (a cor 1 aparece em mais partículas).

Padrões como `crystal-lattice` usam cores em camadas distintas, mas as camadas mais visíveis (externas) usam as cores 1 e 2; camadas internas usam 3, 4, 5.

---

## Adaptação automática para mini-selo

Em mini-selos (<200px), a paleta é simplificada para 3 cores apenas:

```javascript
function simplifyForMini(palette) {
    return {
        ...palette,
        foreground: palette.foreground.slice(0, 3)
    };
}
```

Mantém legibilidade e impacto visual mesmo em tamanho reduzido.

---

## Verificação de contraste

Antes de renderizar, verificar que `accent` tem contraste suficiente com `bg` para padrões que destacam centro (ratio mínimo 4.5:1 conforme WCAG AA).

```javascript
function contrastRatio(hex1, hex2) {
    const lum = (hex) => {
        const { r, g, b } = hexToRgb(hex);
        const sRGB = [r, g, b].map((c) => {
            const v = c / 255;
            return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
    };
    const l1 = lum(hex1);
    const l2 = lum(hex2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    return (lighter + 0.05) / (darker + 0.05);
}
```

Se o contraste falhar, substituir `accent` por uma versão mais clara/escura derivada automaticamente.
