# Code City

Padrão consagrado de visualização de software em 3D: cada arquivo do projeto é um **prédio**, agrupados em **distritos** que correspondem a pastas. Permite captar tamanho, complexidade e distribuição do código em um único olhar.

## Mapeamento de atributos

| Atributo do código | Atributo visual do prédio |
|---|---|
| Linhas de código (LOC) | Altura |
| Complexidade ciclomática | Área da base (largura x profundidade) |
| Pasta do arquivo | Distrito (posição no plano) |
| Tipo de arquivo (código, teste, config) | Cor base |
| Hot path (frequência de mudança ou dependentes) | Cor de destaque (vermelho/amarelo) |

## Quando usar

- Visão geral inicial de um projeto desconhecido.
- Identificar arquivos muito grandes (prédios altos) ou complexos (prédios largos).
- Detectar agrupamento por pasta (distritos coesos vs espalhados).
- Apresentação executiva: visualmente impactante e intuitivo.

**Quando evitar**: projetos pequenos (< 30 arquivos), onde a metáfora urbana é overkill. Use Dependency Graph 3D ou módulos D3 2D.

## Algoritmo de layout

### 1. Agrupar por pasta

```javascript
const districts = {};
modules.forEach((m) => {
    if (!districts[m.folder]) districts[m.folder] = [];
    districts[m.folder].push(m);
});
```

### 2. Calcular tamanho de cada distrito

A área do distrito é proporcional ao número de arquivos. Use empacotamento simples (linha por linha) ou squarified treemap.

```javascript
function packDistrict(modules, padding = 1) {
    const count = modules.length;
    const cols = Math.ceil(Math.sqrt(count));
    const rows = Math.ceil(count / cols);
    return { cols, rows };
}
```

### 3. Posicionar distritos no plano

Os distritos formam a cidade. Para até ~20 pastas, empacotar em grid simples. Para mais, usar treemap.

```javascript
const districtSize = (count) => Math.sqrt(count) * cellSize * 2;
let offsetX = 0;
let offsetZ = 0;
const districtPositions = {};
Object.entries(districts).forEach(([folder, mods], i) => {
    const size = districtSize(mods.length);
    districtPositions[folder] = { x: offsetX, z: offsetZ, size };
    offsetX += size + districtGap;
    if ((i + 1) % gridCols === 0) {
        offsetX = 0;
        offsetZ += size + districtGap;
    }
});
```

### 4. Posicionar prédios dentro do distrito

```javascript
modules.forEach((m) => {
    const district = districtPositions[m.folder];
    const local = packDistrict(districts[m.folder]);
    const indexInDistrict = districts[m.folder].indexOf(m);
    const col = indexInDistrict % local.cols;
    const row = Math.floor(indexInDistrict / local.cols);
    m.x = district.x + col * cellSize;
    m.z = district.z + row * cellSize;
});
```

### 5. Dimensionar cada prédio

```javascript
const LOC_TO_HEIGHT = 0.4;      // 1000 LOC = 400 unidades de altura
const COMPLEXITY_TO_WIDTH = 0.8;
const MIN_W = 2;
const MIN_H = 1;

modules.forEach((m) => {
    m.height = Math.max(MIN_H, m.loc * LOC_TO_HEIGHT);
    const baseW = Math.max(MIN_W, Math.sqrt(m.complexity) * COMPLEXITY_TO_WIDTH);
    m.w = baseW;
    m.d = baseW;
});
```

### 6. Renderizar com InstancedMesh

Ver `THREE_PATTERNS.md` para o padrão de InstancedMesh. Cada prédio é uma instância da mesma BoxGeometry, com matriz e cor distintas.

```javascript
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
boxGeo.translate(0, 0.5, 0); // base no chão
const mat = new THREE.MeshStandardMaterial({ roughness: 0.6 });
const buildings = new THREE.InstancedMesh(boxGeo, mat, modules.length);
buildings.castShadow = true;
buildings.receiveShadow = true;

const dummy = new THREE.Object3D();
const color = new THREE.Color();

modules.forEach((m, i) => {
    dummy.position.set(m.x, 0, m.z);
    dummy.scale.set(m.w, m.height, m.d);
    dummy.updateMatrix();
    buildings.setMatrixAt(i, dummy.matrix);
    color.set(colorForModule(m));
    buildings.setColorAt(i, color);
});
buildings.instanceMatrix.needsUpdate = true;
buildings.instanceColor.needsUpdate = true;
scene.add(buildings);
```

### 7. Chão e distritos

Adicionar um plano grande como chão e quadrados coloridos demarcando cada distrito.

```javascript
const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(2000, 2000),
    new THREE.MeshStandardMaterial({ color: 0x14141a, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

Object.entries(districtPositions).forEach(([folder, d]) => {
    const districtPlane = new THREE.Mesh(
        new THREE.PlaneGeometry(d.size, d.size),
        new THREE.MeshStandardMaterial({ color: districtColor(folder), transparent: true, opacity: 0.15 })
    );
    districtPlane.rotation.x = -Math.PI / 2;
    districtPlane.position.set(d.x + d.size / 2, 0.01, d.z + d.size / 2);
    scene.add(districtPlane);
});
```

## Cores por tipo de arquivo

```javascript
const TYPE_COLORS = {
    code:    0x4a9eff,  // azul
    test:    0x6cc46c,  // verde
    config:  0xffc857,  // amarelo
    doc:     0xb39ddb,  // lilás
    style:   0xff9aa2,  // rosa
    asset:   0x999999   // cinza
};

function colorForModule(m) {
    if (m.isHotPath) return 0xff5a4f;
    return TYPE_COLORS[m.type] || 0xcccccc;
}
```

## Sidebar de controles (Code City)

```html
<aside id="sidebar">
    <h3>Code City</h3>

    <label>Altura (LOC)
        <input type="range" min="0.1" max="2.0" step="0.1" value="0.4" data-param="locScale">
    </label>

    <label>Base (complexidade)
        <input type="range" min="0.2" max="2.0" step="0.1" value="0.8" data-param="complexityScale">
    </label>

    <label>Threshold de hot path
        <input type="range" min="0" max="100" step="5" value="50" data-param="hotPathThreshold">
    </label>

    <label>
        <input type="checkbox" data-param="showLabels" checked> Labels visíveis
    </label>

    <label>
        <input type="checkbox" data-param="showDistricts" checked> Mostrar distritos
    </label>

    <label>Filtrar pasta
        <select data-param="folderFilter">
            <option value="all">Todas</option>
            <!-- POPULATED_FROM_DATA -->
        </select>
    </label>

    <button id="reset">Reset</button>
    <button id="export-png">Exportar PNG</button>
</aside>
```

Quando um slider muda, recalcular `m.height`, `m.w`, `m.d` e atualizar a `InstancedMesh` com novas matrizes.

## Interação

- **Hover em prédio**: tooltip mostra nome do arquivo, LOC, complexidade, pasta.
- **Clique em prédio**: foca câmera no prédio (anima `controls.target` para a posição do prédio).
- **Drag em distrito**: rotaciona câmera com OrbitControls.
- **Scroll**: zoom in/out.

## Performance

- Até **5.000 prédios** é seguro com InstancedMesh.
- Acima disso, agrupar arquivos por pasta (um prédio = uma pasta com altura agregada de LOC, área pelo número de arquivos).
- Desativar sombras se o framerate cair abaixo de 30fps (detectar via `requestAnimationFrame` timer).

## Variantes opcionais

- **Code City temporal**: animar crescimento ao longo do histórico do projeto (cada commit faz prédios crescerem).
- **Code City colorida por autor**: cores indicam quem é o maintainer principal de cada arquivo.
- **Code City com chuva**: hot paths recebem efeito de partículas vermelhas caindo, indicando "instabilidade".

Estas variantes ficam para versões futuras da skill.
