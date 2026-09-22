# Architecture Tour

Câmera animada percorrendo a cena em ritmo cinematográfico, com **overlay narrativo** sincronizado. Funciona como um "trailer" do sistema: alguém aperta play e o vídeo se desenrola sozinho, parando em pontos-chave com legendas explicativas.

## Conceito

Tour não é um modo isolado, é uma **camada animada** que se sobrepõe a qualquer dos outros modos (Code City, Dependency Graph 3D, Layer Stack, Call Graph). A skill recebe uma sequência de waypoints e narrações, e a câmera viaja entre eles.

## Quando usar

- Apresentações para stakeholders não-técnicos.
- Onboarding de novos devs ("aperte play e veja como o sistema é").
- Demonstração executiva curta (1 a 3 minutos).
- Acompanhamento da `deck.html` do mini-site.

## Modelo de dados: a coreografia

```json
{
  "baseMode": "code-city",
  "duration": 90,
  "waypoints": [
    {
      "at": 0,
      "camera": { "position": [200, 250, 400], "target": [0, 0, 0] },
      "overlay": "Esse é o sistema de pagamentos visto de cima."
    },
    {
      "at": 12,
      "camera": { "position": [50, 30, 80], "target": [40, 0, 20] },
      "overlay": "O distrito mais alto, src/payments, concentra 40% do código."
    },
    {
      "at": 24,
      "camera": { "position": [80, 60, 60], "target": [60, 20, 30] },
      "highlight": ["src/payments/charge.ts", "src/payments/refund.ts"],
      "overlay": "Charge e refund são os arquivos centrais."
    },
    {
      "at": 40,
      "camera": { "position": [-100, 80, 200], "target": [-50, 0, 0] },
      "switchMode": "dependency-graph",
      "overlay": "Agora vamos olhar as dependências dele."
    }
  ]
}
```

- `at`: segundo da timeline em que o waypoint dispara.
- `camera`: posição e alvo da câmera ao chegar.
- `highlight`: lista de IDs de nó/módulo para destacar (outros desfocam).
- `overlay`: texto da legenda, em pt-br.
- `switchMode` (opcional): troca o modo base no meio do tour, com transição.

## Algoritmo de interpolação

Entre dois waypoints, a câmera interpola posição e alvo com easing.

```javascript
import { CatmullRomCurve3 } from "https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.module.js";

const positions = waypoints.map((w) => new THREE.Vector3(...w.camera.position));
const targets = waypoints.map((w) => new THREE.Vector3(...w.camera.target));
const positionCurve = new CatmullRomCurve3(positions);
const targetCurve = new CatmullRomCurve3(targets);

let startTime = null;
function playTour() {
    startTime = performance.now();
    controls.enabled = false; // desligar interação manual
    animateTour();
}

function animateTour() {
    const now = performance.now();
    const elapsed = (now - startTime) / 1000;

    if (elapsed >= tour.duration) {
        finishTour();
        return;
    }

    const t = elapsed / tour.duration; // 0..1
    const pos = positionCurve.getPoint(t);
    const tgt = targetCurve.getPoint(t);
    camera.position.copy(pos);
    camera.lookAt(tgt);

    updateOverlay(elapsed);
    updateHighlights(elapsed);

    renderer.render(scene, camera);
    requestAnimationFrame(animateTour);
}
```

## Overlay narrativo

Caixa de texto posicionada em rodapé ou lateral, com transições suaves entre falas.

```html
<div id="tour-overlay">
    <p id="tour-text"></p>
    <div id="tour-progress"><div id="tour-progress-fill"></div></div>
    <div id="tour-controls">
        <button id="tour-pause">Pausar</button>
        <button id="tour-restart">Reiniciar</button>
        <button id="tour-skip">Pular</button>
    </div>
</div>
```

```javascript
function updateOverlay(elapsed) {
    const current = waypoints.findLast((w) => w.at <= elapsed);
    if (!current) return;
    const textEl = document.getElementById("tour-text");
    if (textEl.dataset.at !== String(current.at)) {
        textEl.dataset.at = current.at;
        textEl.style.opacity = 0;
        setTimeout(() => {
            textEl.textContent = current.overlay;
            textEl.style.opacity = 1;
        }, 300);
    }
    const progress = (elapsed / tour.duration) * 100;
    document.getElementById("tour-progress-fill").style.width = progress + "%";
}
```

## Destaque de elementos

Durante highlights, os módulos selecionados ganham emissive e os demais reduzem opacidade.

```javascript
function updateHighlights(elapsed) {
    const current = waypoints.findLast((w) => w.at <= elapsed);
    const highlightIds = new Set(current?.highlight ?? []);

    modules.forEach((m, i) => {
        const isHighlighted = highlightIds.size === 0 || highlightIds.has(m.name);
        const targetOpacity = isHighlighted ? 1.0 : 0.15;
        // animar opacity via InstancedMesh é mais trabalhoso;
        // alternativa: trocar cor para uma versão dessaturada quando opacity baixa
        const baseColor = colorForModule(m);
        const finalColor = isHighlighted ? baseColor : dim(baseColor, 0.3);
        instanced.setColorAt(i, new THREE.Color(finalColor));
    });
    instanced.instanceColor.needsUpdate = true;
}

function dim(hex, factor) {
    const c = new THREE.Color(hex);
    c.r *= factor; c.g *= factor; c.b *= factor;
    return c.getHex();
}
```

## Mudança de modo no meio do tour

Quando um waypoint tem `switchMode`, fazer fade-out da cena atual, dispose, criar a nova cena, fade-in.

```javascript
function switchSceneMode(newMode) {
    fadeOverlay.style.opacity = 1;
    setTimeout(() => {
        clearScene();
        if (newMode === "dependency-graph") buildDependencyGraph();
        else if (newMode === "code-city") buildCodeCity();
        // etc
        fadeOverlay.style.opacity = 0;
    }, 600);
}
```

## Controles do tour

- **Pause**: para `requestAnimationFrame`, congela tempo.
- **Restart**: volta `startTime` para agora.
- **Skip**: pula para o próximo waypoint.
- **Manual takeover**: se usuário arrastar mouse na cena, interrompe tour e habilita OrbitControls.

```javascript
renderer.domElement.addEventListener("pointerdown", () => {
    if (tourPlaying) {
        pauseTour();
        controls.enabled = true;
        showResumeButton();
    }
});
```

## Trilha sonora opcional

Tour pode incluir música ambient sutil via `<audio>` embutido em base64 (curto, ~30s em loop) ou via Web Audio API gerando drones procedurais. Default: sem áudio.

## Geração da coreografia

A skill recebe waypoints prontos OU gera automaticamente a partir de heurísticas:

- Iniciar de cima olhando o centro.
- Mergulhar nos 3 maiores prédios (Code City).
- Voar pelo grafo de dependências destacando o nó mais central.
- Terminar mostrando a layer stack das camadas violadoras (se houver).

Cada heurística pode ser ativada ou desativada via parâmetro.

## Sidebar do tour

```html
<aside id="sidebar">
    <h3>Architecture Tour</h3>

    <label>Duração total
        <input type="range" min="30" max="300" value="90" data-param="duration"> s
    </label>

    <label>Modo base
        <select data-param="baseMode">
            <option value="code-city">Code City</option>
            <option value="dependency-graph">Dependency Graph</option>
            <option value="layer-stack">Layer Stack</option>
        </select>
    </label>

    <label>
        <input type="checkbox" data-param="autoPlay"> Tocar ao abrir
    </label>

    <label>
        <input type="checkbox" data-param="includeViolationsScene" checked> Incluir cena de violações
    </label>

    <button id="play-tour">Tocar Tour</button>
    <button id="pause-tour">Pausar</button>
    <button id="restart-tour">Reiniciar</button>
</aside>
```

## Performance

Tour herda performance do modo base. Adicionar tour custa pouco: apenas interpolação de câmera e animações de opacity. Cuidado com `switchMode` no meio: dispose + rebuild pode causar stutter de 200-500ms.
