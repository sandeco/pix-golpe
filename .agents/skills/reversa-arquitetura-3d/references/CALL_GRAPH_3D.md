# Call Graph 3D

Árvore (ou DAG) de **chamadas de função** explorável em 3D. Cada nó é uma função, cada aresta é uma chamada. Permite navegar a profundidade de uma cadeia de invocações partindo de pontos de entrada (endpoints, handlers, main).

## Mapeamento

| Conceito | Visual |
|---|---|
| Função | Cápsula ou pílula 3D com label |
| Profundidade de chamada | Posição em Z (eixo de profundidade) |
| Função síncrona | Cápsula sólida |
| Função assíncrona | Cápsula translúcida com partículas |
| Função recursiva | Cápsula com brilho (emissive) |
| Caminho quente (frequência) | Linha mais grossa, cor saturada |
| Função externa (lib) | Cor cinza |
| Função do projeto | Cor por pasta/módulo |

## Quando usar

- Entender o fluxo de execução de um endpoint específico.
- Diagnosticar profundidade excessiva de chamadas (>15 níveis, sinal de overengineering).
- Detectar recursão indireta.
- Apresentar como o sistema responde a uma requisição típica.

**Quando evitar**: análise estática sem dados de execução é incompleta (não captura polimorfismo). Para visão estrutural use Dependency Graph 3D.

## Modelo de dados esperado

```json
{
  "entrypoints": ["POST /api/orders", "handleWebhookStripe"],
  "calls": [
    {
      "from": "POST /api/orders",
      "to": "OrderController.create",
      "type": "sync",
      "weight": 1000
    },
    {
      "from": "OrderController.create",
      "to": "OrderService.placeOrder",
      "type": "sync",
      "weight": 1000
    },
    {
      "from": "OrderService.placeOrder",
      "to": "PaymentClient.charge",
      "type": "async",
      "weight": 1000
    }
  ]
}
```

`weight` é frequência relativa (quantidade de invocações observadas em um período). `type` é `sync`, `async`, `recursive` ou `external`.

## Algoritmo de layout: árvore radial 3D

Cada entrypoint vira raiz da árvore. Profundidade aumenta no eixo Z (afastando-se da câmera), funções no mesmo nível distribuem-se em um plano XY.

```javascript
function layoutTree(entrypoint, calls) {
    const nodes = new Map();
    nodes.set(entrypoint, { id: entrypoint, depth: 0, x: 0, y: 0, z: 0, children: [] });

    function buildChildren(parentId, parentDepth) {
        const outgoing = calls.filter((c) => c.from === parentId);
        outgoing.forEach((c, i, arr) => {
            if (nodes.has(c.to)) {
                // detectou recursão
                nodes.get(c.to).recursive = true;
                return;
            }
            const angle = (i / arr.length) * Math.PI * 2;
            const radius = parentDepth * 15 + 30;
            const node = {
                id: c.to,
                depth: parentDepth + 1,
                x: nodes.get(parentId).x + Math.cos(angle) * radius,
                y: nodes.get(parentId).y + Math.sin(angle) * radius,
                z: -(parentDepth + 1) * 40,
                type: c.type,
                weight: c.weight,
                children: []
            };
            nodes.set(c.to, node);
            nodes.get(parentId).children.push(node);
            buildChildren(c.to, parentDepth + 1);
        });
    }

    buildChildren(entrypoint, 0);
    return Array.from(nodes.values());
}
```

Para múltiplos entrypoints, cada um ocupa uma região do plano XY (translação no centro), criando árvores paralelas.

## Renderização das cápsulas

```javascript
const capsuleGeo = new THREE.CapsuleGeometry(2, 6, 8, 12);
const capsuleMat = new THREE.MeshStandardMaterial({ roughness: 0.4 });
const capsules = new THREE.InstancedMesh(capsuleGeo, capsuleMat, nodes.length);

nodes.forEach((n, i) => {
    const dummy = new THREE.Object3D();
    dummy.position.set(n.x, n.y, n.z);
    dummy.rotation.z = Math.PI / 2; // horizontal
    const scale = 0.6 + Math.log(1 + (n.weight ?? 1)) * 0.2;
    dummy.scale.set(scale, scale, scale);
    dummy.updateMatrix();
    capsules.setMatrixAt(i, dummy.matrix);

    const color = new THREE.Color(colorForCall(n));
    capsules.setColorAt(i, color);
});
capsules.instanceMatrix.needsUpdate = true;
capsules.instanceColor.needsUpdate = true;
scene.add(capsules);
```

`colorForCall(n)` retorna cinza para externas, cor da pasta para internas, com emissive se `n.recursive`.

## Renderização das chamadas (arestas)

Linhas curvas tipo bezier conectando pai a filho. Mais grossas para `weight` alto.

```javascript
calls.forEach((c) => {
    const src = nodesById.get(c.from);
    const dst = nodesById.get(c.to);
    if (!src || !dst) return;

    const mid = new THREE.Vector3(
        (src.x + dst.x) / 2,
        (src.y + dst.y) / 2 + 10,
        (src.z + dst.z) / 2
    );
    const curve = new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(src.x, src.y, src.z),
        mid,
        new THREE.Vector3(dst.x, dst.y, dst.z)
    );
    const tube = new THREE.TubeGeometry(curve, 20, 0.2 + Math.log(1 + c.weight) * 0.1, 6, false);
    const isAsync = c.type === "async";
    const mat = new THREE.MeshStandardMaterial({
        color: isAsync ? 0xb39ddb : 0x4a9eff,
        transparent: true,
        opacity: 0.6
    });
    scene.add(new THREE.Mesh(tube, mat));
});
```

## Animação de fluxo (opcional)

Partículas viajando ao longo das arestas, indicando que a chamada está "viva". Útil para apresentações.

```javascript
function animateFlow(time) {
    edgeParticles.forEach((p) => {
        const t = (time * 0.001 + p.offset) % 1;
        const pos = p.curve.getPoint(t);
        p.mesh.position.copy(pos);
    });
}
```

## Sidebar de controles

```html
<aside id="sidebar">
    <h3>Call Graph 3D</h3>

    <label>Entrypoint
        <select data-param="entrypoint">
            <!-- POPULATED -->
        </select>
    </label>

    <label>Profundidade máxima
        <input type="range" min="1" max="20" value="10" data-param="maxDepth">
    </label>

    <label>
        <input type="checkbox" data-param="showAsync" checked> Destacar async
    </label>

    <label>
        <input type="checkbox" data-param="showExternal"> Mostrar libs externas
    </label>

    <label>
        <input type="checkbox" data-param="animateFlow"> Animar fluxo
    </label>

    <div id="depth-info"></div>
    <div id="recursive-warnings"></div>

    <button id="reset">Reset</button>
    <button id="export-png">Exportar PNG</button>
</aside>
```

## Interação

- **Hover em cápsula**: nome da função, módulo de origem, número de chamadores e chamados, tipo.
- **Clique em cápsula**: foca câmera, destaca cadeia desde o entrypoint até essa função.
- **Duplo clique**: expande/colapsa subárvore.
- **Toggle entrypoint**: muda a raiz da visualização, recalcula layout.

## Performance

- Limite prático: ~500 funções por entrypoint.
- Acima disso, colapsar subárvores automaticamente após profundidade 5 e exibir botão "+N funções".
- Animação de fluxo: limitar a 50 partículas simultâneas para não derrubar fps.
