# Padrões Generativos do Selo

Catálogo dos 5 padrões consagrados que a skill `selo-generativo` produz. Cada padrão tem uma aparência distinta, algoritmo central e parâmetros derivados do seed.

Padrão geral de seed: o hash sha256 (64 chars hex) é cortado em fatias de 8 chars, cada fatia vira um `parseInt(slice, 16)` e alimenta um parâmetro distinto. Assim, padrões diferentes do mesmo seed compartilham personalidade visual.

---

## 1. flow-field

Campos de fluxo Perlin: milhares de partículas seguem vetores derivados de ruído, deixando rastros orgânicos curvos. Estilo "natural turbulento".

**Quando combina**: estilos `sober` (versão suave) e `exploratory` (versão luminosa).

**Algoritmo**:

```javascript
let particles = [];
const PARTICLE_COUNT = 500;
const NOISE_SCALE = 0.004;
const STEP = 1.5;

function setup() {
    const canvas = createCanvas(SIZE, SIZE);
    canvas.parent("seal-container");
    randomSeed(seedInt);
    noiseSeed(seedInt);
    background(palette.bg);
    noFill();
    strokeWeight(0.6);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
            x: random(width),
            y: random(height),
            color: random(palette.foreground),
            life: random(200, 600)
        });
    }
    noLoop();
    drawFlowField();
}

function drawFlowField() {
    particles.forEach((p) => {
        stroke(p.color + "55"); // semi-transparente
        let x = p.x, y = p.y;
        for (let step = 0; step < p.life; step++) {
            const angle = noise(x * NOISE_SCALE, y * NOISE_SCALE) * TWO_PI * 4;
            const nx = x + cos(angle) * STEP;
            const ny = y + sin(angle) * STEP;
            line(x, y, nx, ny);
            x = nx;
            y = ny;
            if (x < 0 || x > width || y < 0 || y > height) break;
        }
    });
}
```

**Parâmetros derivados do seed**:
- `PARTICLE_COUNT`: 300 a 1000 (slice 0 normalizado).
- `NOISE_SCALE`: 0.002 a 0.008 (slice 1).
- Centro de gravidade do campo (se houver atrator): coordenada XY (slices 2 e 3).

**Performance**: até 1500 partículas em canvas 800x800 sem trava.

---

## 2. particle-orbit

Partículas orbitando um centro com trilhas decrescentes, criando padrão de "constelação rotativa".

**Quando combina**: estilos `premium` (dark, dourado) e `exploratory` (pastéis luminosos).

**Algoritmo**:

```javascript
const ORBITS = 6;
const PARTICLES_PER_ORBIT = 24;

function setup() {
    const canvas = createCanvas(SIZE, SIZE);
    canvas.parent("seal-container");
    randomSeed(seedInt);
    noiseSeed(seedInt);
    background(palette.bg);
    drawOrbit();
    noLoop();
}

function drawOrbit() {
    const cx = width / 2;
    const cy = height / 2;
    for (let o = 0; o < ORBITS; o++) {
        const radius = (o + 1) * (width / (ORBITS * 2.5));
        const orbitColor = palette.foreground[o % palette.foreground.length];
        const phase = random(TWO_PI);
        const tilt = random(-PI / 6, PI / 6);

        for (let p = 0; p < PARTICLES_PER_ORBIT; p++) {
            const angle = (p / PARTICLES_PER_ORBIT) * TWO_PI + phase;
            const x = cx + cos(angle) * radius;
            const y = cy + sin(angle) * radius * cos(tilt);
            const size = map(noise(angle * 2, o), 0, 1, 1, 6);

            // Trilha
            stroke(orbitColor + "33");
            strokeWeight(0.4);
            noFill();
            arc(cx, cy, radius * 2, radius * 2 * cos(tilt), phase, angle);

            // Partícula
            noStroke();
            fill(orbitColor);
            ellipse(x, y, size);
        }
    }

    // Centro
    fill(palette.accent);
    noStroke();
    ellipse(cx, cy, 14);
}
```

**Parâmetros derivados do seed**:
- Número de órbitas: 3 a 8 (slice 0).
- Inclinação das órbitas (tilt): -π/4 a π/4 (slice 1).
- Densidade de partículas por órbita (slice 2).

**Performance**: trivial, dezenas de elementos.

---

## 3. crystal-lattice

Forma cristalina simétrica derivada de um polígono base, com subdivisões geométricas limpas. Estilo "logotipo arquitetural".

**Quando combina**: estilos `dense` (saturado) e `sober` (limpo).

**Algoritmo**:

```javascript
function setup() {
    const canvas = createCanvas(SIZE, SIZE);
    canvas.parent("seal-container");
    randomSeed(seedInt);
    background(palette.bg);
    drawCrystal();
    noLoop();
}

function drawCrystal() {
    const cx = width / 2;
    const cy = height / 2;
    const sides = floor(random(5, 9)); // 5 a 8 lados
    const radius = width * 0.35;
    const layers = floor(random(3, 6));

    push();
    translate(cx, cy);

    for (let layer = layers; layer > 0; layer--) {
        const r = radius * (layer / layers);
        const rotation = (layers - layer) * (PI / sides);
        const color = palette.foreground[layer % palette.foreground.length];
        fill(color);
        stroke(palette.bg);
        strokeWeight(2);

        beginShape();
        for (let i = 0; i < sides; i++) {
            const angle = (i / sides) * TWO_PI + rotation;
            const x = cos(angle) * r;
            const y = sin(angle) * r;
            vertex(x, y);
        }
        endShape(CLOSE);
    }

    // Núcleo central
    fill(palette.accent);
    noStroke();
    const coreRadius = radius * 0.15;
    beginShape();
    for (let i = 0; i < sides; i++) {
        const angle = (i / sides) * TWO_PI;
        vertex(cos(angle) * coreRadius, sin(angle) * coreRadius);
    }
    endShape(CLOSE);

    pop();
}
```

**Parâmetros derivados do seed**:
- Número de lados: 5 a 8 (slice 0).
- Número de camadas concêntricas: 3 a 6 (slice 1).
- Rotação de offset entre camadas (slice 2).

**Exportável como SVG**: este padrão é puramente geométrico, ideal para conversão a SVG real para mini-selos.

**Performance**: trivial.

---

## 4. wave-interference

Padrões de interferência tipo moiré: ondas circulares partindo de múltiplos centros que se cruzam, gerando texturas complexas a partir de regras simples.

**Quando combina**: estilos `premium` (preto + dourado, alta contraste) e `dense`.

**Algoritmo**:

```javascript
function setup() {
    const canvas = createCanvas(SIZE, SIZE);
    canvas.parent("seal-container");
    randomSeed(seedInt);
    pixelDensity(1);
    background(palette.bg);
    drawInterference();
    noLoop();
}

function drawInterference() {
    const centers = [];
    const numCenters = floor(random(2, 5));
    for (let i = 0; i < numCenters; i++) {
        centers.push({
            x: random(width * 0.2, width * 0.8),
            y: random(height * 0.2, height * 0.8),
            frequency: random(0.04, 0.10),
            phase: random(TWO_PI)
        });
    }

    loadPixels();
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            let value = 0;
            centers.forEach((c) => {
                const dx = x - c.x;
                const dy = y - c.y;
                const dist = sqrt(dx * dx + dy * dy);
                value += sin(dist * c.frequency + c.phase);
            });
            value = (value / centers.length + 1) / 2;

            const colorIdx = floor(value * palette.foreground.length);
            const hex = palette.foreground[constrain(colorIdx, 0, palette.foreground.length - 1)];
            const rgb = hexToRgb(hex);
            const i = (y * width + x) * 4;
            pixels[i] = rgb.r;
            pixels[i + 1] = rgb.g;
            pixels[i + 2] = rgb.b;
            pixels[i + 3] = 255;
        }
    }
    updatePixels();
}

function hexToRgb(hex) {
    const h = hex.replace("#", "");
    return {
        r: parseInt(h.slice(0, 2), 16),
        g: parseInt(h.slice(2, 4), 16),
        b: parseInt(h.slice(4, 6), 16)
    };
}
```

**Parâmetros derivados do seed**:
- Número de centros: 2 a 4 (slice 0).
- Frequência das ondas: 0.04 a 0.10 (slice 1).
- Posição de cada centro (slices 2-N).

**Performance**: O(width * height * centers). Em 800x800 com 3 centros, ~ 1.9M operações. Tudo bem para `noLoop()`.

---

## 5. noise-strata

Estratos horizontais de ruído, formando "paisagem abstrata" com camadas de Perlin noise.

**Quando combina**: estilos `sober` (terracota neutro) e `exploratory` (auroral).

**Algoritmo**:

```javascript
function setup() {
    const canvas = createCanvas(SIZE, SIZE);
    canvas.parent("seal-container");
    randomSeed(seedInt);
    noiseSeed(seedInt);
    background(palette.bg);
    drawStrata();
    noLoop();
}

function drawStrata() {
    const layers = floor(random(4, 8));
    const baseY = height * 0.3;
    const layerHeight = (height - baseY) / layers;

    for (let l = 0; l < layers; l++) {
        const y0 = baseY + l * layerHeight;
        const color = palette.foreground[l % palette.foreground.length];
        fill(color);
        noStroke();
        beginShape();
        vertex(0, height);
        for (let x = 0; x <= width; x += 4) {
            const n = noise(x * 0.005, l * 0.7);
            const y = y0 + n * layerHeight * 1.5;
            vertex(x, y);
        }
        vertex(width, height);
        endShape(CLOSE);
    }

    // Sol/lua decorativa
    fill(palette.accent);
    noStroke();
    const sunX = random(width * 0.2, width * 0.8);
    const sunY = baseY - random(20, 60);
    const sunR = random(30, 70);
    ellipse(sunX, sunY, sunR * 2);
}
```

**Parâmetros derivados do seed**:
- Número de camadas: 4 a 8 (slice 0).
- Altura base do horizonte: 25% a 40% do canvas (slice 1).
- Posição do sol/lua decorativo (slices 2 e 3).

**Performance**: trivial.

---

## Seleção de padrão pelo seed

```javascript
const PATTERNS = ["flow-field", "particle-orbit", "crystal-lattice", "wave-interference", "noise-strata"];

function pickPattern(seedHex, styleHint) {
    const patternIndex = parseInt(seedHex.slice(0, 2), 16) % PATTERNS.length;
    let chosen = PATTERNS[patternIndex];

    // Ajuste suave por estilo (escolhe entre padrões "compatíveis" se houver desconexão)
    if (styleHint && !isStyleCompatible(chosen, styleHint)) {
        chosen = pickCompatible(seedHex, styleHint);
    }
    return chosen;
}
```

A compatibilidade `padrão x estilo` aparece no início desta referência. Quando há incompatibilidade declarada, a função `pickCompatible` reavalia entre os padrões marcados como apropriados para o estilo.

---

## Override manual

A skill aceita parâmetro `forcePattern` para ignorar a derivação por seed e escolher o padrão manualmente, útil quando o usuário quer um selo específico em estilo diferente do default.
