# Catálogo de Gráficos Highcharts

Referência completa dos 40+ tipos de gráfico com orientação de uso e exemplos de opções.

---

## 1. Line & Spline

**Quando usar:** Tendências ao longo do tempo, séries temporais, evolução de métricas.

**Variantes:** `line`, `spline` (curvas suaves), `step` (degraus)

```javascript
{
    chart: { type: 'line' },
    title: { text: 'Título do Gráfico' },
    xAxis: { categories: ['Jan','Fev','Mar','Abr','Mai','Jun'] },
    yAxis: { title: { text: 'Valores' } },
    plotOptions: {
        line: {
            dataLabels: { enabled: true },
            enableMouseTracking: true
        }
    },
    series: [{
        name: 'Série A',
        data: [7, 6.9, 9.5, 14.5, 18.2, 21.5]
    }]
}
```

---

## 2. Area & Areaspline

**Quando usar:** Tendências com volume/magnitude, composição ao longo do tempo (stacked).

**Variantes:** `area`, `areaspline`, `arearange`, `areasplinerange`

```javascript
{
    chart: { type: 'areaspline' },
    plotOptions: {
        areaspline: {
            fillOpacity: 0.3,
            marker: { enabled: false }
        }
    },
    series: [{ name: 'Série', data: [...] }]
}
```

**Stacked area** para composição:
```javascript
plotOptions: {
    area: {
        stacking: 'normal', // ou 'percent' para 100%
        lineWidth: 1,
        marker: { enabled: false }
    }
}
```

---

## 3. Column & Bar

**Quando usar:** Comparação entre categorias discretas. Column = vertical, Bar = horizontal.

**Variantes:** `column`, `bar`, `columnrange`, `columnpyramid`

```javascript
{
    chart: { type: 'column' },
    xAxis: { categories: ['A', 'B', 'C', 'D'] },
    plotOptions: {
        column: {
            borderRadius: 5,
            dataLabels: { enabled: true }
        }
    },
    series: [
        { name: 'Série 1', data: [49, 71, 106, 129] },
        { name: 'Série 2', data: [83, 78, 98, 93] }
    ]
}
```

**Stacked / Grouped / Percent:**
```javascript
plotOptions: {
    column: {
        stacking: 'normal', // 'percent' para 100%
        groupPadding: 0.1,
        pointPadding: 0.05
    }
}
```

---

## 4. Pie & Donut

**Quando usar:** Composição de um todo, proporções, participação de mercado. Máximo 7-8 fatias.

```javascript
{
    chart: { type: 'pie' },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                format: '<b>{point.name}</b>: {point.percentage:.1f}%'
            },
            showInLegend: true
        }
    },
    series: [{
        name: 'Participação',
        colorByPoint: true,
        data: [
            { name: 'Item A', y: 45 },
            { name: 'Item B', y: 26.8 },
            { name: 'Item C', y: 12.8, sliced: true, selected: true },
            { name: 'Outros', y: 15.4 }
        ]
    }]
}
```

**Donut** (pie com innerSize):
```javascript
plotOptions: { pie: { innerSize: '60%' } }
```

**Semi-circle donut:**
```javascript
plotOptions: {
    pie: {
        innerSize: '50%',
        startAngle: -90,
        endAngle: 90,
        center: ['50%', '75%']
    }
}
```

---

## 5. Scatter & Bubble

**Quando usar:** Correlação entre duas variáveis (scatter), três variáveis (bubble).

**Requer:** `highcharts-more.js` para bubble.

```javascript
// Scatter
{ chart: { type: 'scatter' },
  xAxis: { title: { text: 'Variável X' } },
  yAxis: { title: { text: 'Variável Y' } },
  series: [{ data: [[1,2],[3,4],[5,1],[7,8]] }]
}

// Bubble
{ chart: { type: 'bubble' },
  series: [{ data: [[9,81,63],[98,5,89],[51,50,73]] }] // [x, y, z]
}
```

---

## 6. Heatmap

**Quando usar:** Matriz de valores, padrões em duas dimensões, calendários de atividade.

**Requer:** `modules/heatmap.js`

```javascript
{
    chart: { type: 'heatmap' },
    colorAxis: {
        min: 0,
        minColor: '#FFFFFF',
        maxColor: '#c4463a'
    },
    series: [{
        borderWidth: 1,
        data: [[0,0,10],[0,1,19],[1,0,92],[1,1,58]], // [x, y, value]
        dataLabels: { enabled: true, color: '#000' }
    }]
}
```

---

## 7. Treemap & Sunburst

**Quando usar:** Hierarquias, proporção dentro de categorias, orçamentos.

**Requer:** `modules/treemap.js`, `modules/sunburst.js`

```javascript
// Treemap
{
    chart: { type: 'treemap' },
    series: [{
        layoutAlgorithm: 'squarified',
        data: [
            { name: 'A', value: 6, colorValue: 1 },
            { name: 'B', value: 3, colorValue: 2 },
            { name: 'C', value: 4, colorValue: 3 }
        ]
    }]
}

// Sunburst (hierárquico com parent/id)
{
    chart: { type: 'sunburst' },
    series: [{
        data: [
            { id: '0', name: 'Root' },
            { id: '1', parent: '0', name: 'Filho A', value: 5 },
            { id: '2', parent: '0', name: 'Filho B', value: 3 }
        ]
    }]
}
```

---

## 8. Gauge & Solid Gauge

**Quando usar:** KPIs, progresso, indicadores de status, velocímetros.

**Requer:** `highcharts-more.js`, `modules/solid-gauge.js`

```javascript
// Solid Gauge (estilo moderno)
{
    chart: { type: 'solidgauge' },
    pane: {
        startAngle: -90, endAngle: 90,
        background: {
            backgroundColor: '#EEE',
            innerRadius: '60%', outerRadius: '100%',
            shape: 'arc'
        }
    },
    yAxis: { min: 0, max: 100, stops: [
        [0.1, '#55BF3B'], [0.5, '#DDDF0D'], [0.9, '#DF5353']
    ]},
    series: [{ name: 'Progresso', data: [73], innerRadius: '60%' }]
}
```

---

## 9. Sankey & Dependency Wheel

**Quando usar:** Fluxos, transferências, relações entre entidades.

**Requer:** `modules/sankey.js`, `modules/dependency-wheel.js`

```javascript
// Sankey
{
    chart: { type: 'sankey' },
    series: [{
        keys: ['from', 'to', 'weight'],
        data: [
            ['Brasil', 'EUA', 5], ['Brasil', 'Europa', 3],
            ['EUA', 'Ásia', 2], ['Europa', 'Ásia', 1]
        ]
    }]
}
```

---

## 10. Funnel & Pyramid

**Quando usar:** Funis de conversão, processos sequenciais com perda.

**Requer:** `modules/funnel.js`

```javascript
{
    chart: { type: 'funnel' },
    plotOptions: { funnel: { neckWidth: '30%', neckHeight: '25%' } },
    series: [{
        data: [
            ['Visitantes', 15654], ['Downloads', 4064],
            ['Signup', 1987], ['Compra', 976], ['Renovação', 846]
        ]
    }]
}
```

---

## 11. Wordcloud

**Quando usar:** Frequência de palavras, tags, termos populares.

**Requer:** `modules/wordcloud.js`

```javascript
{
    chart: { type: 'wordcloud' },
    series: [{
        data: [
            { name: 'JavaScript', weight: 15 },
            { name: 'Python', weight: 12 },
            { name: 'React', weight: 8 }
        ]
    }]
}
```

---

## 12. Network Graph

**Quando usar:** Relações entre entidades, grafos, redes sociais.

**Requer:** `modules/networkgraph.js`

```javascript
{
    chart: { type: 'networkgraph' },
    plotOptions: {
        networkgraph: {
            layoutAlgorithm: { enableSimulation: true },
            keys: ['from', 'to']
        }
    },
    series: [{
        data: [['A','B'],['B','C'],['C','D'],['D','A'],['B','D']]
    }]
}
```

---

## 13. Box Plot & Histogram

**Quando usar:** Distribuição estatística, quartis, outliers.

**Requer:** `highcharts-more.js`, `modules/histogram-bellcurve.js`

```javascript
// Box Plot
{
    chart: { type: 'boxplot' },
    series: [{
        data: [
            [760, 801, 848, 895, 965], // [low, q1, median, q3, high]
            [733, 853, 939, 980, 1080]
        ]
    }]
}
```

---

## 14. Stock Charts (Highstock)

**Quando usar:** Dados financeiros, séries temporais com range selector, navigator.

**Requer:** `stock/highstock.js` (substitui highcharts.js)

```javascript
Highcharts.stockChart('container', {
    rangeSelector: { selected: 1 },
    series: [{
        name: 'AAPL',
        data: [[Date.UTC(2024,0,1), 150], [Date.UTC(2024,0,2), 152], ...],
        tooltip: { valueDecimals: 2 }
    }]
});
```

---

## 15. Maps (Highmaps)

**Quando usar:** Dados geográficos, mapas coropléticos.

**Requer:** `maps/highmaps.js` (substitui highcharts.js) + mapa GeoJSON

---

## 16. Gantt Chart

**Quando usar:** Planejamento, cronogramas, gestão de projetos.

**Requer:** `gantt/highcharts-gantt.js` (substitui highcharts.js)

---

## 17. Outros Tipos

- **Lollipop**: `modules/lollipop.js` — barras com dot no final
- **Dumbbell**: `modules/dumbbell.js` — antes/depois, range entre dois pontos
- **Timeline**: `modules/timeline.js` — eventos ao longo do tempo
- **Venn**: `modules/venn.js` — diagramas de Venn
- **Waterfall**: tipo `waterfall` — decomposição de valores
- **Polar / Spider**: usando `chart: { polar: true }` — comparação multidimensional
- **3D Charts**: usando `highcharts-3d.js` — versões 3D de column, pie, scatter

---

## Combinando Gráficos (Dual Axis / Mixed)

```javascript
{
    yAxis: [
        { title: { text: 'Receita (R$)' } },
        { title: { text: 'Unidades' }, opposite: true }
    ],
    series: [
        { type: 'column', name: 'Unidades', data: [...], yAxis: 1 },
        { type: 'spline', name: 'Receita', data: [...], yAxis: 0 }
    ]
}
```

## Drilldown

**Requer:** `modules/drilldown.js`

```javascript
{
    series: [{
        name: 'Categorias',
        data: [
            { name: 'Frutas', y: 55, drilldown: 'frutas' },
            { name: 'Vegetais', y: 25, drilldown: 'vegetais' }
        ]
    }],
    drilldown: {
        series: [
            { id: 'frutas', data: [['Maçã',30],['Banana',15],['Laranja',10]] },
            { id: 'vegetais', data: [['Cenoura',10],['Tomate',8],['Alface',7]] }
        ]
    }
}
```
