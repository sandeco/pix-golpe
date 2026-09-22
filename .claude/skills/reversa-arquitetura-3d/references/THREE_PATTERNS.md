# Padrões Three.js para Visualização de Arquitetura

Referência rápida de setup, materiais e técnicas comuns a todos os modos da skill. Three.js v0.158+, ESM via CDN.

---

## Setup base da cena

```javascript
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.module.js";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.158.0/examples/jsm/controls/OrbitControls.js";

const container = document.getElementById("scene-container");
const width = container.clientWidth;
const height = container.clientHeight;

// Cena
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a14);
scene.fog = new THREE.Fog(0x0a0a14, 100, 800);

// Câmera
const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 2000);
camera.position.set(150, 200, 300);
camera.lookAt(0, 0, 0);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(width, height);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

// Controles
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 20;
controls.maxDistance = 1500;
```

## Iluminação padrão

```javascript
// Luz ambiente leve para não ter sombras totalmente pretas
const ambient = new THREE.AmbientLight(0xffffff, 0.35);
scene.add(ambient);

// Hemisfério: céu vs chão, dá profundidade natural
const hemi = new THREE.HemisphereLight(0xddeeff, 0x202028, 0.5);
hemi.position.set(0, 200, 0);
scene.add(hemi);

// Direcional: simula sol, projeta sombras
const dir = new THREE.DirectionalLight(0xffffff, 0.85);
dir.position.set(80, 200, 100);
dir.castShadow = true;
dir.shadow.mapSize.set(2048, 2048);
dir.shadow.camera.left = -400;
dir.shadow.camera.right = 400;
dir.shadow.camera.top = 400;
dir.shadow.camera.bottom = -400;
scene.add(dir);
```

## Loop de renderização

```javascript
function tick() {
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
}
tick();
```

## Handler de resize

```javascript
window.addEventListener("resize", () => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
});
```

## InstancedMesh para grandes volumes

Quando há mais de 200 elementos do mesmo tipo (prédios do Code City, nós do dep graph), usar `InstancedMesh` em vez de loop com `add()`.

```javascript
const boxGeo = new THREE.BoxGeometry(1, 1, 1);
const mat = new THREE.MeshStandardMaterial({ color: 0xffffff });
const instanced = new THREE.InstancedMesh(boxGeo, mat, modules.length);

const dummy = new THREE.Object3D();
const colorObj = new THREE.Color();

modules.forEach((m, i) => {
    dummy.position.set(m.x, m.height / 2, m.z);
    dummy.scale.set(m.w, m.height, m.d);
    dummy.updateMatrix();
    instanced.setMatrixAt(i, dummy.matrix);
    colorObj.set(m.color);
    instanced.setColorAt(i, colorObj);
});
instanced.instanceMatrix.needsUpdate = true;
if (instanced.instanceColor) instanced.instanceColor.needsUpdate = true;
scene.add(instanced);
```

## Labels em CSS2D (legíveis sempre)

```javascript
import { CSS2DRenderer, CSS2DObject } from "https://cdn.jsdelivr.net/npm/three@0.158.0/examples/jsm/renderers/CSS2DRenderer.js";

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(width, height);
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.top = "0";
labelRenderer.domElement.style.pointerEvents = "none";
container.appendChild(labelRenderer.domElement);

function addLabel(text, position) {
    const div = document.createElement("div");
    div.className = "label-3d";
    div.textContent = text;
    const label = new CSS2DObject(div);
    label.position.copy(position);
    return label;
}
```

No `tick()`, chamar `labelRenderer.render(scene, camera)` junto com o renderer principal.

**Regra**: mostrar labels apenas quando o nó está próximo da câmera (distância < threshold) ou em hover, para evitar poluição.

## Raycaster para hover e clique

```javascript
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

renderer.domElement.addEventListener("pointermove", (e) => {
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObject(instanced);
    if (hits.length > 0) {
        const i = hits[0].instanceId;
        showTooltip(modules[i]);
    } else {
        hideTooltip();
    }
});
```

## Sidebar reativa

```javascript
const sliders = document.querySelectorAll("aside input[type=range]");
sliders.forEach((slider) => {
    slider.addEventListener("input", (e) => {
        const param = e.target.dataset.param;
        const value = parseFloat(e.target.value);
        applyParam(param, value); // função específica do modo
        localStorage.setItem(`arq3d.${param}`, value);
    });
    // restore
    const saved = localStorage.getItem(`arq3d.${slider.dataset.param}`);
    if (saved !== null) {
        slider.value = saved;
        slider.dispatchEvent(new Event("input"));
    }
});
```

## Exportar PNG

```javascript
document.getElementById("export-png").addEventListener("click", () => {
    renderer.render(scene, camera); // garantir frame atual
    renderer.domElement.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "arquitetura-3d.png";
        a.click();
        URL.revokeObjectURL(url);
    });
});
```

## Dispose ao trocar de modo

```javascript
function clearScene() {
    scene.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
            else obj.material.dispose();
        }
    });
    while (scene.children.length > 0) scene.remove(scene.children[0]);
}
```

## Performance: limites práticos

| Cenário | Limite seguro | Acima disso |
|---|---|---|
| BoxGeometry independentes | 200 | Migrar para InstancedMesh |
| InstancedMesh de cubos | 5.000 | Aplicar agrupamento por pasta |
| Linhas (LineSegments) | 10.000 segmentos | Usar Line2 (fat lines) ou agrupar |
| Sprites/labels CSS2D | 100 visíveis | Mostrar só sob hover ou proximidade |
| Polígonos texturizados | 50.000 tris | Reduzir LOD ou desativar sombras |
