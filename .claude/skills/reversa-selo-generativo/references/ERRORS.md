# Cenários de Erro e Tratamento

Cenários comuns na skill `selo-generativo` e como tratá-los.

---

## ERR-01: p5.js indisponível (CDN inacessível)

**Causa**: usuário offline na primeira execução, ou CDN bloqueado.

**Detecção**: variável `p5` global não definida após o `<script>` do CDN.

**Tratamento**:

```javascript
window.addEventListener("load", () => {
    if (typeof p5 === "undefined") {
        document.getElementById("seal-container").innerHTML = `
            <div class="seal-fallback" style="width: ${SIZE}px; height: ${SIZE}px;
                 background: ${palette.bg}; display: flex; align-items: center;
                 justify-content: center; border-radius: 50%; color: ${palette.fg};">
                <span>Selo indisponível</span>
            </div>`;
        return;
    }
    // setup normal aqui
});
```

Fallback: SVG mínimo (círculo + cor de fundo da paleta) inline, sem dependência de p5.

---

## ERR-02: Canvas não suportado pelo browser

**Causa**: browser muito antigo sem suporte a `<canvas>` (caso raríssimo hoje).

**Detecção**: `canvas.getContext("2d")` retorna `null`.

**Tratamento**: cair para SVG inline com `crystal-lattice` (que é o padrão mais compatível com SVG real).

---

## ERR-03: Seed inválido ou ausente

**Causa**: agente chamou a skill sem seed, ou passou string vazia.

**Detecção**: validação na entrada.

**Tratamento**: fallback seguro.

```javascript
function resolveSeed(rawSeed) {
    if (!rawSeed || typeof rawSeed !== "string" || rawSeed.length === 0) {
        const timestamp = Date.now().toString();
        console.warn("Seed ausente, usando timestamp como fallback. Selo não será reprodutível.");
        return timestamp;
    }
    return rawSeed;
}
```

Quando timestamp é usado, exibir aviso no rodapé da página (apenas se for hero grande): "Selo não-reprodutível (sem seed)".

---

## ERR-04: Tamanho extremo

**Causa**: requisição de canvas muito grande (>4096) ou muito pequeno (<16).

**Detecção**: validação do parâmetro `size`.

**Tratamento**:

```javascript
function clampSize(requested) {
    const MIN = 16;
    const MAX = 4096;
    if (requested < MIN) {
        console.warn(`Tamanho ${requested} abaixo do mínimo (${MIN}). Ajustando.`);
        return MIN;
    }
    if (requested > MAX) {
        console.warn(`Tamanho ${requested} acima do máximo (${MAX}). Ajustando.`);
        return MAX;
    }
    return requested;
}
```

Acima de 1024, padrões de pixel-loop como `wave-interference` ficam pesados. A skill deve avisar e oferecer `noLoop()` obrigatório com cache do canvas.

---

## ERR-05: Paleta com cores inválidas

**Causa**: paleta recebida com hex malformado ou campo ausente.

**Detecção**: regex de validação em cada cor.

**Tratamento**:

```javascript
function validatePalette(palette) {
    const HEX_RX = /^#[0-9a-fA-F]{6}$/;
    const required = ["bg", "foreground", "accent", "fg"];
    for (const field of required) {
        if (!(field in palette)) {
            throw new Error(`Paleta inválida: campo '${field}' ausente.`);
        }
    }
    if (!Array.isArray(palette.foreground) || palette.foreground.length === 0) {
        throw new Error("Paleta inválida: 'foreground' deve ser lista não-vazia.");
    }
    [palette.bg, palette.accent, palette.fg].forEach((c) => {
        if (!HEX_RX.test(c)) throw new Error(`Cor inválida: ${c}`);
    });
    palette.foreground.forEach((c) => {
        if (!HEX_RX.test(c)) throw new Error(`Cor inválida em foreground: ${c}`);
    });
}
```

Se a paleta é inválida, cair para `palettes.sober` (paleta de fallback mais conservadora) e logar a falha.

---

## ERR-06: Contraste insuficiente

**Causa**: paleta com `accent` e `bg` muito próximos, gerando elemento central invisível.

**Detecção**: `contrastRatio(accent, bg) < 4.5` (ver PALETTE_BY_STYLE.md).

**Tratamento**: derivar `accent` ajustado automaticamente.

```javascript
function ensureContrast(palette) {
    if (contrastRatio(palette.accent, palette.bg) < 4.5) {
        const bgIsLight = luminance(palette.bg) > 0.5;
        palette.accent = bgIsLight ? darken(palette.accent, 0.4) : lighten(palette.accent, 0.4);
    }
    return palette;
}
```

---

## ERR-07: Padrão escolhido incompatível com estilo

**Causa**: derivação por seed resultou em padrão visualmente incompatível com o estilo escolhido (ex: `crystal-lattice` em estilo `exploratory`).

**Detecção**: tabela de compatibilidade declarada em `GENERATIVE_PATTERNS.md`.

**Tratamento**: re-rolar dentro dos padrões compatíveis.

```javascript
const STYLE_COMPATIBLE = {
    sober: ["flow-field", "crystal-lattice", "noise-strata"],
    premium: ["particle-orbit", "wave-interference"],
    dense: ["crystal-lattice", "wave-interference"],
    exploratory: ["flow-field", "particle-orbit", "noise-strata"]
};

function pickCompatible(seedHex, styleHint) {
    const allowed = STYLE_COMPATIBLE[styleHint];
    if (!allowed) return PATTERNS[0];
    const idx = parseInt(seedHex.slice(2, 4), 16) % allowed.length;
    return allowed[idx];
}
```

---

## ERR-08: Performance muito ruim em mini-selo

**Causa**: padrão pesado em canvas pequeno consumindo CPU desproporcional.

**Detecção**: medir tempo entre `setup` e `draw` final.

**Tratamento**: se canvas é mini (<200px) e padrão escolhido é `wave-interference` (pixel loop), trocar automaticamente para `crystal-lattice` (geometria simples) com mensagem no console.

---

## ERR-09: Múltiplas instâncias do mesmo selo na mesma página

**Causa**: o mini-selo aparece em todas as páginas do mini-site. Recarregar p5.js e gerar canvas em cada uma é desperdício.

**Tratamento**: gerar o selo uma vez como SVG (para `crystal-lattice`) ou PNG dataURI (para outros padrões) e embutir inline em todas as páginas. A skill aceita parâmetro `mode: "svg" | "dataURI" | "html"` para retornar formato apropriado.

```javascript
function exportAs(mode) {
    if (mode === "svg") return canvasToSvg();
    if (mode === "dataURI") return canvas.elt.toDataURL("image/png");
    return wrapInStandaloneHtml(canvas);
}
```

---

## ERR-10: localStorage de seed corrompido

Não aplicável diretamente, porque a skill não persiste estado entre execuções. O seed sempre vem do invocador (agente orquestrador), e a reprodutibilidade depende apenas dele.

Se o invocador perdeu o seed, o agente deve recalcular do soul.md (sha256). Esta skill não é responsável por isso.

---

## Princípio geral

O selo é um elemento **decorativo**. Falha de selo nunca deve quebrar a página inteira. Em todos os cenários acima, há fallback que sempre renderiza algo: um círculo colorido, um SVG mínimo, uma versão simplificada. Nada de tela branca.

Mensagens em pt-br, sem travessão.
