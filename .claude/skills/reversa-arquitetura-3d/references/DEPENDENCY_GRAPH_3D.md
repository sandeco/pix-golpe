# Dependency Graph 3D

Grafo orientado de dependências entre módulos visualizado em 3D, com simulação de forças (atração entre nós conectados, repulsão entre não conectados) que distribui o grafo no espaço de forma orgânica.

## Mapeamento

| Atributo do código | Atributo visual do nó |
|---|---|
| Módulo | Esfera ou ícone |
| Tamanho (LOC ou número de dependentes) | Raio da esfera |
| Tipo do módulo | Cor |
| Pasta | Cor secundária ou cluster próximo |
| Aresta = `imports/requires` | Linha curva orientada (com seta) |
| Peso da aresta (frequência de uso) | Espessura da linha |

## Quando usar

- Detectar **acoplamento alto** (nós muito conectados ficam no centro do cluster).
- Identificar **módulos centrais** (alto fan-in) e **módulos isolados**.
- Visualizar **ciclos de dependência** (loops visíveis na simulação).
- Comparar coesão entre pastas (módulos da mesma pasta deveriam estar próximos).

**Quando evitar**: projetos com mais de ~300 módulos, onde o grafo vira hairball ilegível. Use Code City ou agrupe por pasta.

## Algoritmo de layout: força em 3D

Simulação tipo D3-force adaptada para 3 dimensões. Roda em loop até estabilizar, depois congela.

```javascript
const nodes = deps.nodes.map((n) => ({
    id: n.id,
    x: (Math.random() - 0.5) * 200,
    y: (Math.random() - 0.5) * 200,
    z: (Math.random() - 0.5) * 200,
    vx: 0, vy: 0, vz: 0,
    fx: 0, fy: 0, fz: 0,
    mass: 1 + (n.loc ?? 0) / 100
}));

const edges = deps.edges.map((e) => ({
    source: nodes.find((n) => n.id === e.from),
    target: nodes.find((n) => n.id === e.to),
    weight: e.weight ?? 1
}));

const REPULSION = 800;
const ATTRACTION = 0.04;
const CENTER_GRAVITY = 0.002;
const DAMPING = 0.85;

function simulationStep() {
    nodes.forEach((n) => { n.fx = 0; n.fy = 0; n.fz = 0; });

    // Repulsão entre todos os pares
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i], b = nodes[j];
            const dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z;
            const distSq = dx * dx + dy * dy + dz * dz + 0.1;
            const dist = Math.sqrt(distSq);
            const force = REPULSION / distSq;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            const fz = (dz / dist) * force;
            a.fx -= fx; a.fy -= fy; a.fz -= fz;
            b.fx += fx; b.fy += fy; b.fz += fz;
        }
    }

    // Atração ao longo das arestas
    edges.forEach((e) => {
        const dx = e.target.x - e.source.x;
        const dy = e.target.y - e.source.y;
        const dz = e.target.z - e.source.z;
        const f = ATTRACTION * e.weight;
        e.source.fx += dx * f; e.source.fy += dy * f; e.source.fz += dz * f;
        e.target.fx -= dx * f; e.target.fy -= dy * f; e.target.fz -= dz * f;
    });

    // Gravidade para o centro
    nodes.forEach((n) => {
        n.fx -= n.x * CENTER_GRAVITY;
        n.fy -= n.y * CENTER_GRAVITY;
        n.fz -= n.z * CENTER_GRAVITY;
    });

    // Integrar
    nodes.forEach((n) => {
        n.vx = (n.vx + n.fx / n.mass) * DAMPING;
        n.vy = (n.vy + n.fy / n.mass) * DAMPING;
        n.vz = (n.vz + n.fz / n.mass) * DAMPING;
        n.x += n.vx;
        n.y += n.vy;
        n.z += n.vz;
    });
}
```

Para grafos grandes (>200 nós), substituir repulsão O(n²) por **octree (Barnes-Hut)** para reduzir a O(n log n).

## Renderização dos nós

Usar `InstancedMesh` de esferas para até 1.000 nós; acima disso, billboard com sprites.

```javascript
const sphereGeo = new THREE.SphereGeometry(1, 16, 16);
const sphereMat = new THREE.MeshStandardMaterial({ roughness: 0.4 });
const nodeMesh = new THREE.InstancedMesh(sphereGeo, sphereMat, nodes.length);
nodeMesh.castShadow = true;

const dummy = new THREE.Object3D();
const color = new THREE.Color();

function updateNodes() {
    nodes.forEach((n, i) => {
        dummy.position.set(n.x, n.y, n.z);
        const radius = 1 + Math.sqrt(n.mass) * 0.5;
        dummy.scale.set(radius, radius, radius);
        dummy.updateMatrix();
        nodeMesh.setMatrixAt(i, dummy.matrix);
        color.set(colorForNode(n));
        nodeMesh.setColorAt(i, color);
    });
    nodeMesh.instanceMatrix.needsUpdate = true;
    nodeMesh.instanceColor.needsUpdate = true;
}
```

## Renderização das arestas

Linhas curvas em 3D usando `BufferGeometry` com `LineSegments` ou `TubeGeometry` para arestas com volume.

```javascript
const edgePositions = new Float32Array(edges.length * 6);
const edgeGeo = new THREE.BufferGeometry();
edgeGeo.setAttribute("position", new THREE.BufferAttribute(edgePositions, 3));
const edgeMat = new THREE.LineBasicMaterial({ color: 0x4a9eff, transparent: true, opacity: 0.4 });
const edgeLines = new THREE.LineSegments(edgeGeo, edgeMat);
scene.add(edgeLines);

function updateEdges() {
    edges.forEach((e, i) => {
        edgePositions[i * 6 + 0] = e.source.x;
        edgePositions[i * 6 + 1] = e.source.y;
        edgePositions[i * 6 + 2] = e.source.z;
        edgePositions[i * 6 + 3] = e.target.x;
        edgePositions[i * 6 + 4] = e.target.y;
        edgePositions[i * 6 + 5] = e.target.z;
    });
    edgeGeo.attributes.position.needsUpdate = true;
}
```

Para arestas orientadas com seta visível, usar `ArrowHelper` ou pequenos cones próximos ao target.

## Loop de simulação + renderização

```javascript
let frame = 0;
const MAX_SIM_FRAMES = 400; // estabiliza após ~7s em 60fps
function tick() {
    if (frame < MAX_SIM_FRAMES) {
        simulationStep();
        updateNodes();
        updateEdges();
        frame++;
    }
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
}
```

Depois de estabilizar, manter renderização mas pausar simulação para economizar CPU.

## Detecção de ciclos

Rodar Tarjan ou Kosaraju antes de renderizar; nós que pertencem a ciclos recebem cor especial (laranja) e suas arestas viram vermelhas.

```javascript
const cycles = findStronglyConnectedComponents(nodes, edges).filter((c) => c.length > 1);
cycles.flat().forEach((n) => n.inCycle = true);
edges.forEach((e) => {
    e.inCycle = e.source.inCycle && e.target.inCycle;
});
```

## Sidebar de controles

```html
<aside id="sidebar">
    <h3>Dependency Graph 3D</h3>

    <label>Repulsão
        <input type="range" min="100" max="2000" value="800" data-param="repulsion">
    </label>

    <label>Atração
        <input type="range" min="0.01" max="0.2" step="0.01" value="0.04" data-param="attraction">
    </label>

    <label>Filtrar por pasta
        <select data-param="folderFilter">
            <option value="all">Todas</option>
        </select>
    </label>

    <label>
        <input type="checkbox" data-param="highlightCycles" checked> Destacar ciclos
    </label>

    <label>
        <input type="checkbox" data-param="showLabels"> Labels visíveis
    </label>

    <button id="reset">Reset</button>
    <button id="freeze">Congelar simulação</button>
    <button id="export-png">Exportar PNG</button>
</aside>
```

Mudanças nos sliders reativam a simulação por mais 100 frames antes de congelar novamente.

## Interação

- **Hover em nó**: tooltip com nome, número de dependentes (fan-in), dependências (fan-out).
- **Clique em nó**: destaca o nó e suas arestas conectadas, desfoca os demais (opacity reduzida).
- **Duplo clique em nó**: foca câmera no nó.
- **Scroll**: zoom.

## Performance

| Nós | Estratégia |
|---|---|
| < 50 | Esferas individuais com `add()` |
| 50 a 500 | InstancedMesh + repulsão O(n²) |
| 500 a 2.000 | InstancedMesh + Barnes-Hut octree |
| > 2.000 | Agrupar por pasta antes (cada cluster = um meta-nó) |

Arestas: até **10.000** com LineSegments. Acima disso, simplificar (mostrar só as top N por peso) ou usar gradient de cor em vez de duplicar geometria.
