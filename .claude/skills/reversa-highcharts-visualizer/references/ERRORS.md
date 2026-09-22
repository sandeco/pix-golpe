# Tratamento de Erros — Highcharts Visualizer

## Dados insuficientes ou vazios

**Sintoma:** Gráfico renderiza vazio ou com mensagem "No data to display".

**Ação:** Configurar `noData` module ou verificar os dados antes de criar o gráfico:
```javascript
// Incluir: modules/no-data-to-display.js
lang: { noData: 'Nenhum dado disponível para exibir' },
noData: { style: { fontWeight: 'bold', fontSize: '16px', color: '#666' } }
```

Avisar o usuário:
> "Os dados fornecidos parecem estar vazios ou não foram processados corretamente. Poderia verificar?"

## Formato de dados incompatível

**Sintoma:** Erro no console ou gráfico com valores NaN/undefined.

**Ação:** Validar dados com `scripts/parse_data.py` antes de embutir. O script converte automaticamente
strings numéricas ("1.234,56" → 1234.56) e datas em múltiplos formatos.

## Módulo CDN não carrega

**Sintoma:** Erro "Highcharts is not defined" ou tipo de gráfico não reconhecido.

**Ação:** Verificar ordem dos scripts. O core `highcharts.js` deve vir primeiro, depois os módulos.
Para Stock/Maps/Gantt, usar o respectivo script principal (highstock.js, highmaps.js, highcharts-gantt.js)
**no lugar de** highcharts.js, não junto.

Ordem correta:
```html
<script src="https://code.highcharts.com/highcharts.js"></script>
<script src="https://code.highcharts.com/highcharts-more.js"></script>
<script src="https://code.highcharts.com/modules/solid-gauge.js"></script>
<script src="https://code.highcharts.com/modules/exporting.js"></script>
<script src="https://code.highcharts.com/modules/accessibility.js"></script>
```

## Gráfico não responsivo

**Sintoma:** Gráfico não redimensiona com a janela, ou fica cortado.

**Ação:** Não definir `chart.width` fixo. Usar container com CSS responsivo.
Garantir que `chart.reflow` não está desabilitado.

```javascript
chart: { 
    // NÃO definir width/height fixos
    // Deixar o Highcharts adaptar ao container
    reflow: true
}
```

## Performance lenta com muitos dados

**Sintoma:** Gráfico travando ou demorando para renderizar com >10.000 pontos.

**Ação:**
1. Incluir `modules/boost.js`
2. Setar `boostThreshold: 5000` na série
3. Desabilitar animações: `plotOptions: { series: { animation: false } }`
4. Desabilitar markers: `marker: { enabled: false }`
5. Considerar agregar dados (downsampling) via `scripts/analyze_data.py`

## Tooltips com valores incorretos

**Sintoma:** Tooltip mostra "undefined" ou formato errado.

**Ação:** Verificar se os dados estão no formato correto para o tipo de gráfico.
Usar `tooltip.formatter` customizado para ter controle total sobre o formato.

## Cores ilegíveis

**Sintoma:** Séries ou labels com contraste insuficiente.

**Ação:** Usar `Highcharts.getOptions().colors` para verificar a paleta ativa.
Para dark mode, garantir que labels/grid/tick tem cores claras.
O módulo de accessibility alerta sobre problemas de contraste.

## CSV com encoding diferente (UTF-8 BOM, Latin1)

**Sintoma:** Caracteres especiais (acentos) aparecem como "�" ou "Ã©".

**Ação:** O `scripts/parse_data.py` tenta detectar encoding automaticamente.
Se falhar, forçar encoding:
```bash
python scripts/parse_data.py dados.csv --encoding latin1
```

## Arquivo Excel com múltiplas abas

**Sintoma:** Dados extraídos são de aba errada.

**Ação:**
```bash
python scripts/parse_data.py dados.xlsx --sheet "Planilha2"
```
