# Layer Stack 3D

Visualização de **camadas arquiteturais** empilhadas verticalmente, cada camada como um plano com seus módulos, conectadas por setas verticais que mostram o fluxo de dependências entre camadas.

## Mapeamento

| Conceito arquitetural | Visual |
|---|---|
| Camada (UI, Domain, Infra, etc) | Plano horizontal em altura distinta |
| Módulo dentro da camada | Caixa/disco posicionado no plano da camada |
| Dependência inter-camada | Linha vertical orientada conectando módulos |
| Direção do fluxo | Seta na ponta da linha |
| Violação de camada (camada de baixo importando de cima) | Linha vermelha pulsante |

## Quando usar

- Validar que a arquitetura segue Clean Architecture, Hexagonal, ou Onion.
- Detectar **violações de camada** (UI importando direto de Infra, por exemplo).
- Apresentar o sistema para stakeholders que pensam em camadas.
- Comparar com o diagrama arquitetural esperado lado a lado.

**Quando evitar**: sistemas sem separação clara de camadas (monolitos planos). Use Code City.

## Detecção de camadas

A skill aceita o mapeamento de camadas vindo do usuário (via JSON) ou tenta inferir de padrões de pasta.

**Mapeamento explícito**:

```json
{
  "layers": [
    { "name": "UI", "order": 0, "folders": ["src/components", "src/pages"] },
    { "name": "Application", "order": 1, "folders": ["src/services", "src/use-cases"] },
    { "name": "Domain", "order": 2, "folders": ["src/domain", "src/entities"] },
    { "name": "Infrastructure", "order": 3, "folders": ["src/db", "src/external"] }
  ]
}
```

**Inferência heurística** (quando não fornecido): regex sobre nomes de pasta.

```javascript
const LAYER_PATTERNS = [
    { name: "UI", regex: /(components|pages|views|screens|ui)/i, order: 0 },
    { name: "Application", regex: /(services|use-cases|application|handlers)/i, order: 1 },
    { name: "Domain", regex: /(domain|entities|models|business)/i, order: 2 },
    { name: "Infrastructure", regex: /(db|database|repositories|external|infra|adapters)/i, order: 3 }
];

function inferLayer(folder) {
    for (const p of LAYER_PATTERNS) {
        if (p.regex.test(folder)) return p;
    }
    return { name: "Outros", order: 999 };
}
```

## Algoritmo de layout

### 1. Empilhar camadas verticalmente

```javascript
const LAYER_GAP = 80;
const LAYER_SIZE = 400; // plano 400x400

const layerPlanes = layers.map((layer, i) => ({
    name: layer.name,
    y: i * LAYER_GAP,
    modules: modules.filter((m) => belongsToLayer(m, layer))
}));
```

### 2. Posicionar módulos dentro da camada

Empacotamento simples em grid 2D no plano da camada.

```javascript
layerPlanes.forEach((layer) => {
    const cols = Math.ceil(Math.sqrt(layer.modules.length));
    const cellSize = LAYER_SIZE / cols;
    layer.modules.forEach((m, idx) => {
        const col = idx % cols;
        const row = Math.floor(idx / cols);
        m.x = (col - cols / 2) * cellSize;
        m.y = layer.y;
        m.z = (row - cols / 2) * cellSize;
    });
});
```

### 3. Renderizar planos de camada

```javascript
layerPlanes.forEach((layer, i) => {
    const planeGeo = new THREE.PlaneGeometry(LAYER_SIZE, LAYER_SIZE);
    const planeMat = new THREE.MeshStandardMaterial({
        color: LAYER_COLORS[i % LAYER_COLORS.length],
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide
    });
    const plane = new THREE.Mesh(planeGeo, planeMat);
    plane.rotation.x = Math.PI / 2;
    plane.position.y = layer.y;
    scene.add(plane);

    // Label da camada lateral
    const label = addLabel(layer.name, new THREE.Vector3(LAYER_SIZE / 2 + 20, layer.y, 0));
    scene.add(label);
});

const LAYER_COLORS = [0x4a9eff, 0x6cc46c, 0xffc857, 0xb39ddb, 0xff9aa2];
```

### 4. Renderizar módulos como discos

```javascript
const moduleGeo = new THREE.CylinderGeometry(1, 1, 0.5, 16);
const moduleMat = new THREE.MeshStandardMaterial({ roughness: 0.5 });
const modulesMesh = new THREE.InstancedMesh(moduleGeo, moduleMat, modules.length);

modules.forEach((m, i) => {
    const dummy = new THREE.Object3D();
    const size = 1 + Math.sqrt(m.loc / 100);
    dummy.position.set(m.x, m.y, m.z);
    dummy.scale.set(size, 1, size);
    dummy.updateMatrix();
    modulesMesh.setMatrixAt(i, dummy.matrix);
});
modulesMesh.instanceMatrix.needsUpdate = true;
scene.add(modulesMesh);
```

### 5. Renderizar dependências como linhas verticais

```javascript
edges.forEach((e) => {
    const src = modules.find((m) => m.name === e.from);
    const dst = modules.find((m) => m.name === e.to);
    if (!src || !dst) return;

    const isViolation = isLayerViolation(src, dst);
    const color = isViolation ? 0xff5a4f : 0x6c8eb0;

    const points = [
        new THREE.Vector3(src.x, src.y, src.z),
        new THREE.Vector3(dst.x, dst.y, dst.z)
    ];
    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const mat = new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity: isViolation ? 1.0 : 0.4
    });
    const line = new THREE.Line(geo, mat);
    if (isViolation) line.userData.pulse = true; // anima opacidade
    scene.add(line);
});
```

### 6. Detecção de violação de camada

A regra padrão (Clean Architecture): camadas só dependem de camadas com `order` maior (mais para "dentro").

```javascript
function isLayerViolation(src, dst) {
    return src.layerOrder > dst.layerOrder;
}
```

Pode haver exceções configuráveis (ex: ports/adapters em hexagonal).

## Animação de violações

Linhas vermelhas pulsam (opacity oscilando) para chamar atenção.

```javascript
function pulseViolations(time) {
    scene.traverse((obj) => {
        if (obj.userData?.pulse) {
            obj.material.opacity = 0.5 + 0.5 * Math.sin(time * 0.003);
        }
    });
}
```

## Sidebar de controles

```html
<aside id="sidebar">
    <h3>Layer Stack</h3>

    <label>Espaçamento entre camadas
        <input type="range" min="40" max="200" value="80" data-param="layerGap">
    </label>

    <label>
        <input type="checkbox" data-param="showViolations" checked> Destacar violações
    </label>

    <label>
        <input type="checkbox" data-param="showLabels" checked> Labels de módulo
    </label>

    <label>Mostrar apenas
        <select data-param="layerFilter">
            <option value="all">Todas as camadas</option>
            <!-- POPULATED -->
        </select>
    </label>

    <div id="violations-count"></div>

    <button id="reset">Reset</button>
    <button id="export-png">Exportar PNG</button>
</aside>
```

O contador `#violations-count` mostra em tempo real "X violações detectadas".

## Interação

- **Hover em módulo**: tooltip com nome, camada, dependências.
- **Clique em violação**: foca câmera nos dois módulos envolvidos e mostra detalhes da relação no painel.
- **Filtro de camada**: oculta camadas não selecionadas.

## Performance

Camadas tipicamente têm dezenas a poucas centenas de módulos cada. Limite total de ~2.000 módulos. Acima disso, agrupar por pasta dentro de cada camada.
