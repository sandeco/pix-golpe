# Cenários de Erro e Tratamento

Catálogo de erros comuns na skill `arquitetura-3d` e como tratá-los para preservar a experiência do usuário.

---

## ERR-01: Three.js indisponível (CDN inacessível)

**Causa**: usuário está offline na primeira execução, ou CDN bloqueado por firewall corporativo.

**Detecção**: o script `<script type="module">` falha ao importar, ou `THREE` fica `undefined` após o carregamento.

**Tratamento**:

```javascript
try {
    const mod = await import("https://cdn.jsdelivr.net/npm/three@0.158.0/build/three.module.js");
    window.THREE = mod;
} catch (e) {
    document.getElementById("loader").innerHTML = `
        <div class="error-panel">
            <h2>Não foi possível carregar a biblioteca 3D</h2>
            <p>Esta visualização requer acesso à internet para baixar o Three.js uma vez.
               Conecte-se à internet e recarregue a página.</p>
            <p>Detalhe técnico: ${e.message}</p>
        </div>`;
    return;
}
```

Texto sempre em pt-br, sem travessão.

---

## ERR-02: WebGL não suportado

**Causa**: browser sem WebGL (raríssimo hoje, mas possível em VMs antigas ou ambientes corporativos restritos).

**Detecção**: `new THREE.WebGLRenderer()` lança exceção ou retorna `null`.

**Tratamento**:

```javascript
let renderer;
try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
} catch (e) {
    showFallback("WebGL não está disponível no seu browser. Use Chrome, Firefox ou Edge atualizados.");
    return;
}
```

Fallback exibe uma versão estática da cena (screenshot pré-renderizado se houver, ou ASCII art simbólico) com mensagem clara.

---

## ERR-03: JSON malformado

**Causa**: `modules.json` ou `deps.json` com sintaxe inválida, ou campos esperados ausentes.

**Detecção**: `JSON.parse` falha, ou validação de schema indica campos ausentes.

**Tratamento**:

```javascript
function loadData() {
    const raw = document.getElementById("data").textContent;
    let data;
    try {
        data = JSON.parse(raw);
    } catch (e) {
        showError("Dados de entrada inválidos: arquivo JSON malformado. " + e.message);
        return null;
    }

    if (!Array.isArray(data.modules)) {
        showError("Dados de entrada inválidos: 'modules' deve ser uma lista.");
        return null;
    }

    data.modules = data.modules.filter((m) => {
        if (!m.name) {
            console.warn("Módulo sem 'name' descartado:", m);
            return false;
        }
        return true;
    });

    return data;
}
```

Erros não-fatais (módulo individual ruim) descartam o item com aviso. Erros fatais (estrutura raiz inválida) mostram mensagem clara.

---

## ERR-04: Projeto vazio ou sem dados visualizáveis

**Causa**: `modules.json` tem 0 itens, ou `deps.json` tem 0 arestas, ou ambos.

**Detecção**: após `loadData()`, contagem dos itens.

**Tratamento**:

```javascript
if (data.modules.length === 0) {
    showEmptyState({
        title: "Nada para visualizar ainda",
        message: "O projeto não tem módulos detectados. Rode `/reversa` para extrair a estrutura primeiro.",
        actions: [
            { label: "Voltar à documentação", href: "index.html" }
        ]
    });
    return;
}
```

Empty state amigável, nunca cena vazia silenciosa.

---

## ERR-05: Projeto muito grande (>5.000 módulos sem agrupamento)

**Causa**: o usuário força modo Code City sem agrupamento em um projeto enorme.

**Detecção**: `data.modules.length > 5000` e nenhuma estratégia de agrupamento ativada.

**Tratamento**: aplicar agrupamento automaticamente e avisar.

```javascript
if (data.modules.length > 5000) {
    showToast("Projeto grande detectado (" + data.modules.length + " arquivos). Agrupando por pasta para manter performance.");
    data.modules = groupByFolder(data.modules);
    config.grouped = true;
}
```

O agrupamento e seu impacto aparecem no rodapé permanente da página: "Visualização agrupada por pasta. Cada bloco representa N arquivos."

---

## ERR-06: Performance degradada (fps < 30)

**Causa**: hardware fraco, projeto no limite superior, sombras pesadas.

**Detecção**: medir `requestAnimationFrame` delta.

```javascript
let frameTimes = [];
function measureFps(time) {
    frameTimes.push(time);
    if (frameTimes.length > 60) frameTimes.shift();
    if (frameTimes.length === 60) {
        const fps = 1000 / ((frameTimes[59] - frameTimes[0]) / 59);
        if (fps < 30 && !config.degraded) {
            degradeQuality();
        }
    }
}
```

**Tratamento progressivo** (`degradeQuality`):

1. Desativar sombras.
2. Reduzir pixelRatio para 1.
3. Reduzir contagem de partículas em tours.
4. Mostrar toast "Modo de performance ativado".

---

## ERR-07: InstancedMesh limit excedido

**Causa**: tentativa de criar InstancedMesh com mais instâncias do que o hardware suporta (limite de ~65k em hardwares antigos via Uint16, mas raro).

**Detecção**: console error do Three.js após `setMatrixAt` para índices altos.

**Tratamento**:

```javascript
const MAX_INSTANCES = 32768;
if (modules.length > MAX_INSTANCES) {
    showWarning("Limite de instâncias excedido. Mostrando apenas os " + MAX_INSTANCES + " maiores.");
    modules = modules.sort((a, b) => b.loc - a.loc).slice(0, MAX_INSTANCES);
}
```

---

## ERR-08: Ciclo de dependências infinito durante layout

**Causa**: grafo com ciclo fechado e layout iterativo sem critério de parada.

**Detecção**: medir iterações de simulação; se passar `MAX_SIM_FRAMES` sem convergir, abortar.

**Tratamento**: parar simulação no frame limite, mostrar aviso "Layout não convergiu, posições podem não refletir estabilidade ideal", desenhar mesmo assim.

---

## ERR-09: WebGL context lost

**Causa**: aba inativa por muito tempo, troca de driver gráfico, GPU sobrecarregada.

**Detecção**: evento `webglcontextlost` no canvas.

**Tratamento**:

```javascript
renderer.domElement.addEventListener("webglcontextlost", (e) => {
    e.preventDefault();
    showToast("Contexto 3D foi perdido. Tentando recuperar...");
});

renderer.domElement.addEventListener("webglcontextrestored", () => {
    rebuildScene();
    showToast("Contexto recuperado.");
});
```

Em vez de recarregar a página, reconstruir a cena no mesmo canvas. Importante chamar `rebuildScene()` que recria texturas e buffers.

---

## ERR-10: Sidebar localStorage corrompido

**Causa**: dados antigos de localStorage com formato incompatível após atualização da skill.

**Detecção**: `JSON.parse` falha ao restaurar estado, ou valor está fora do range esperado de um slider.

**Tratamento**: silencioso, descarta e usa default.

```javascript
function loadSliderState(slider) {
    try {
        const saved = localStorage.getItem(`arq3d.${slider.dataset.param}`);
        if (saved !== null) {
            const value = parseFloat(saved);
            if (value >= slider.min && value <= slider.max) {
                slider.value = value;
            }
        }
    } catch (e) {
        // ignora e mantém valor padrão
    }
}
```

---

## Função utilitária: showError + showWarning + showToast

```javascript
function showError(message) {
    const panel = document.createElement("div");
    panel.className = "reversa-error-panel";
    panel.innerHTML = `<h2>Erro</h2><p>${escapeHtml(message)}</p>`;
    document.body.appendChild(panel);
}

function showWarning(message) {
    const panel = document.createElement("div");
    panel.className = "reversa-warning-banner";
    panel.textContent = message;
    document.body.appendChild(panel);
    setTimeout(() => panel.remove(), 8000);
}

function showToast(message) {
    const t = document.createElement("div");
    t.className = "reversa-toast";
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4000);
}

function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
```

Estilos `reversa-error-panel`, `reversa-warning-banner`, `reversa-toast` ficam no CSS compartilhado do mini-site.

---

## Princípio geral

Nenhum erro deve resultar em **tela branca silenciosa**. Sempre mostrar mensagem clara em pt-br com instrução acionável ou indicação clara de limitação. Mensagens curtas, sem jargão de framework, sem travessão.
