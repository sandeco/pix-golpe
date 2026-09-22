# Padrões Highcharts.js

Referência de padrões de código testados para gerar gráficos Highcharts profissionais.

---

## Template HTML Completo

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Título do Gráfico]</title>
    
    <!-- Highcharts Core (obrigatório) -->
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <!-- Módulos extras conforme necessidade (ver tabela no SKILL.md) -->
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        #container {
            max-width: 900px;
            margin: 0 auto;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
            padding: 10px;
        }
        /* Para múltiplos gráficos (dashboard) */
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .chart-card {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.08);
            padding: 10px;
        }
    </style>
</head>
<body>
    <div id="container"></div>
    <script>
        Highcharts.chart('container', {
            // Opções do gráfico aqui
        });
    </script>
</body>
</html>
```

## Opções Globais Recomendadas

Aplicar antes de criar qualquer gráfico:

```javascript
Highcharts.setOptions({
    lang: {
        months: ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
        shortMonths: ['Jan','Fev','Mar','Abr','Mai','Jun',
                      'Jul','Ago','Set','Out','Nov','Dez'],
        weekdays: ['Domingo','Segunda','Terça','Quarta','Quinta','Sexta','Sábado'],
        decimalPoint: ',',
        thousandsSep: '.',
        loading: 'Carregando...',
        noData: 'Sem dados para exibir',
        downloadPNG: 'Baixar como PNG',
        downloadJPEG: 'Baixar como JPEG',
        downloadPDF: 'Baixar como PDF',
        downloadSVG: 'Baixar como SVG',
        downloadCSV: 'Baixar como CSV',
        downloadXLS: 'Baixar como XLS',
        viewData: 'Ver tabela de dados',
        printChart: 'Imprimir gráfico',
        viewFullscreen: 'Tela cheia',
        exitFullscreen: 'Sair da tela cheia',
        contextButtonTitle: 'Menu do gráfico'
    }
});
```

## Paletas de Cores Profissionais

```javascript
// Paleta padrão Highcharts (boa para maioria dos casos)
// É a padrão, não precisa definir

// Paleta Corporate Blue
colors: ['#2f7ed8','#0d233a','#8bbc21','#910000','#1aadce',
         '#492970','#f28f43','#77a1e5','#c42525','#a6c96a']

// Paleta Vibrante Moderna
colors: ['#6366f1','#8b5cf6','#ec4899','#f43f5e','#f97316',
         '#eab308','#22c55e','#06b6d4','#3b82f6','#a855f7']

// Paleta Dark Mode
colors: ['#7cb5ec','#90ed7d','#f7a35c','#8085e9','#f15c80',
         '#e4d354','#2b908f','#f45b5b','#91e8e1','#b2e87e']

// Paleta Earth Tones
colors: ['#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf',
         '#d62728','#1f77b4','#ff7f0e','#2ca02c','#9467bd']
```

## Tema Dark Mode Completo

```javascript
const darkTheme = {
    chart: {
        backgroundColor: '#1a1a2e',
        style: { fontFamily: "'Segoe UI', Roboto, sans-serif" }
    },
    title: { style: { color: '#e0e0e0' } },
    subtitle: { style: { color: '#a0a0a0' } },
    xAxis: {
        gridLineColor: '#2a2a4a',
        labels: { style: { color: '#b0b0b0' } },
        lineColor: '#3a3a5a',
        tickColor: '#3a3a5a',
        title: { style: { color: '#c0c0c0' } }
    },
    yAxis: {
        gridLineColor: '#2a2a4a',
        labels: { style: { color: '#b0b0b0' } },
        title: { style: { color: '#c0c0c0' } }
    },
    legend: {
        itemStyle: { color: '#c0c0c0' },
        itemHoverStyle: { color: '#fff' }
    },
    tooltip: {
        backgroundColor: 'rgba(20,20,40,0.95)',
        borderColor: '#4a4a6a',
        style: { color: '#e0e0e0' }
    },
    plotOptions: {
        series: {
            dataLabels: { color: '#c0c0c0' }
        }
    },
    credits: { style: { color: '#555' } }
};

// Aplicar tema globalmente
Highcharts.setOptions(darkTheme);
```

## Tooltip Formatado (Padrões Úteis)

```javascript
// Tooltip com moeda brasileira
tooltip: {
    pointFormat: '{series.name}: <b>R$ {point.y:,.2f}</b><br/>',
    shared: true,
    useHTML: true
}

// Tooltip com percentual
tooltip: {
    pointFormat: '{series.name}: <b>{point.y:.1f}%</b><br/>'
}

// Tooltip customizado com HTML
tooltip: {
    useHTML: true,
    formatter: function() {
        return `<div style="padding:8px">
            <b style="font-size:14px">${this.key}</b><br/>
            <span style="color:${this.color}">●</span>
            ${this.series.name}: <b>${Highcharts.numberFormat(this.y, 0, ',', '.')}</b>
        </div>`;
    }
}

// Tooltip compartilhado (múltiplas séries)
tooltip: {
    shared: true,
    crosshairs: true,
    borderRadius: 8,
    shadow: true
}
```

## Formatação de Eixos

```javascript
// Eixo Y com moeda
yAxis: {
    title: { text: 'Receita' },
    labels: {
        formatter: function() {
            return 'R$ ' + Highcharts.numberFormat(this.value, 0, ',', '.');
        }
    }
}

// Eixo X temporal
xAxis: {
    type: 'datetime',
    dateTimeLabelFormats: {
        month: '%b %Y',
        year: '%Y'
    }
}

// Eixo com categorias rotacionadas
xAxis: {
    categories: [...],
    labels: { rotation: -45, style: { fontSize: '11px' } }
}
```

## Animações

```javascript
// Animação de entrada
plotOptions: {
    series: {
        animation: {
            duration: 1500,
            easing: 'easeOutBounce'
        }
    }
}

// Animação staggered (cada série com delay)
plotOptions: {
    series: {
        animation: { duration: 1000 },
        // cada ponto aparece com delay
        dataSorting: { enabled: true }
    }
}
```

## Responsividade

```javascript
responsive: {
    rules: [{
        condition: { maxWidth: 500 },
        chartOptions: {
            legend: { layout: 'horizontal', align: 'center', verticalAlign: 'bottom' },
            yAxis: { title: { text: null } },
            subtitle: { text: null }
        }
    }]
}
```

## Dashboard com Múltiplos Gráficos

```html
<div class="chart-grid">
    <div class="chart-card" id="chart1"></div>
    <div class="chart-card" id="chart2"></div>
    <div class="chart-card" id="chart3"></div>
    <div class="chart-card" id="chart4"></div>
</div>
<script>
    // KPI cards + gráficos em grid
    Highcharts.chart('chart1', { /* opções */ });
    Highcharts.chart('chart2', { /* opções */ });
    Highcharts.chart('chart3', { /* opções */ });
    Highcharts.chart('chart4', { /* opções */ });
</script>
```

## Dados Grandes (Boost Module)

```javascript
// Para séries com >10.000 pontos
// Incluir: <script src="https://code.highcharts.com/modules/boost.js"></script>
{
    boost: { useGPUTranslations: true },
    series: [{
        boostThreshold: 5000, // ativar boost acima de 5k pontos
        data: massiveDataArray
    }]
}
```

## Eventos Úteis

```javascript
chart: {
    events: {
        load: function() {
            // Executar após gráfico renderizar
            console.log('Gráfico carregado');
        },
        redraw: function() {
            // Após resize ou update
        }
    }
},
plotOptions: {
    series: {
        events: {
            click: function(e) {
                alert(e.point.category + ': ' + e.point.y);
            }
        },
        point: {
            events: {
                mouseOver: function() {
                    // Highlight on hover
                }
            }
        }
    }
}
```

## Anotações

```javascript
// Requer: modules/annotations.js
annotations: [{
    labels: [{
        point: { x: 3, y: 150, xAxis: 0, yAxis: 0 },
        text: 'Ponto importante!',
        backgroundColor: 'rgba(255,255,255,0.9)',
        borderColor: '#666',
        shape: 'callout'
    }],
    labelOptions: {
        borderRadius: 5,
        padding: 10
    }
}]
```
