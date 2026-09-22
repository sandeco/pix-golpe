#!/usr/bin/env python3
"""
Gera dados de exemplo prontos para diferentes tipos de gráfico Highcharts.

Útil quando o usuário quer explorar um tipo de gráfico sem ter dados reais.

Uso:
    python sample_data.py --type line
    python sample_data.py --type pie --items 6
    python sample_data.py --type stock --days 365
    python sample_data.py --type sankey
    python sample_data.py --list  (lista todos os tipos)

Saída:
    JSON com opções Highcharts prontas para usar.
"""

import sys
import json
import random
import argparse
from datetime import datetime, timedelta


def sample_line(months: int = 12, series_count: int = 2) -> dict:
    """Dados de exemplo para line/spline/area chart."""
    months_list = ['Jan','Fev','Mar','Abr','Mai','Jun',
                   'Jul','Ago','Set','Out','Nov','Dez'][:months]
    series = []
    for i in range(series_count):
        base = random.randint(50, 200)
        data = [round(base + random.gauss(0, 20) + j * random.uniform(-2, 5), 1)
                for j in range(months)]
        series.append({"name": f"Série {chr(65+i)}", "data": data})
    return {"categories": months_list, "series": series, "suggested_type": "line"}


def sample_column(categories: int = 6, series_count: int = 2) -> dict:
    """Dados de exemplo para column/bar chart."""
    cats = [f"Categoria {chr(65+i)}" for i in range(categories)]
    series = []
    for i in range(series_count):
        data = [random.randint(20, 150) for _ in range(categories)]
        series.append({"name": f"Grupo {i+1}", "data": data})
    return {"categories": cats, "series": series, "suggested_type": "column"}


def sample_pie(items: int = 6) -> dict:
    """Dados de exemplo para pie/donut chart."""
    names = ['Tecnologia', 'Saúde', 'Finanças', 'Educação',
             'Varejo', 'Indústria', 'Energia', 'Transporte'][:items]
    values = [random.randint(5, 35) for _ in range(items)]
    total = sum(values)
    data = [{"name": n, "y": round(v / total * 100, 1)} for n, v in zip(names, values)]
    # Destacar o maior
    max_idx = max(range(len(data)), key=lambda i: data[i]["y"])
    data[max_idx]["sliced"] = True
    data[max_idx]["selected"] = True
    return {"series": [{"name": "Participação", "colorByPoint": True, "data": data}],
            "suggested_type": "pie"}


def sample_scatter(points: int = 50) -> dict:
    """Dados de exemplo para scatter chart."""
    data_a = [[round(random.gauss(5, 2), 1), round(random.gauss(5, 2), 1)]
              for _ in range(points)]
    data_b = [[round(random.gauss(8, 1.5), 1), round(random.gauss(3, 1.5), 1)]
              for _ in range(points)]
    return {"series": [
        {"name": "Grupo A", "data": data_a},
        {"name": "Grupo B", "data": data_b}
    ], "suggested_type": "scatter"}


def sample_heatmap(rows: int = 7, cols: int = 12) -> dict:
    """Dados de exemplo para heatmap."""
    row_cats = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'][:rows]
    col_cats = ['Jan','Fev','Mar','Abr','Mai','Jun',
                'Jul','Ago','Set','Out','Nov','Dez'][:cols]
    data = [[x, y, random.randint(0, 100)] for x in range(cols) for y in range(rows)]
    return {
        "xCategories": col_cats, "yCategories": row_cats,
        "series": [{"data": data}], "suggested_type": "heatmap"
    }


def sample_sankey() -> dict:
    """Dados de exemplo para Sankey diagram."""
    data = [
        ['Marketing', 'Leads', 1000],
        ['Vendas Diretas', 'Leads', 500],
        ['Indicação', 'Leads', 300],
        ['Leads', 'Qualificados', 900],
        ['Leads', 'Descartados', 900],
        ['Qualificados', 'Proposta', 600],
        ['Qualificados', 'Perdidos', 300],
        ['Proposta', 'Fechados', 400],
        ['Proposta', 'Perdidos', 200],
    ]
    return {
        "series": [{"keys": ["from", "to", "weight"], "data": data}],
        "suggested_type": "sankey"
    }


def sample_gauge(value: float = None) -> dict:
    """Dados de exemplo para gauge/solid gauge."""
    val = value or round(random.uniform(30, 95), 1)
    return {
        "series": [{"name": "Performance", "data": [val]}],
        "suggested_type": "solidgauge",
        "min": 0, "max": 100
    }


def sample_treemap() -> dict:
    """Dados de exemplo para treemap."""
    data = [
        {"name": "Brasil", "value": 211, "colorValue": 1},
        {"name": "México", "value": 128, "colorValue": 2},
        {"name": "Colômbia", "value": 50, "colorValue": 3},
        {"name": "Argentina", "value": 45, "colorValue": 4},
        {"name": "Peru", "value": 32, "colorValue": 5},
        {"name": "Venezuela", "value": 28, "colorValue": 6},
        {"name": "Chile", "value": 19, "colorValue": 7},
        {"name": "Equador", "value": 17, "colorValue": 8},
    ]
    return {"series": [{"data": data}], "suggested_type": "treemap"}


def sample_stock(days: int = 365) -> dict:
    """Dados de exemplo para stock chart (OHLC)."""
    start = datetime(2024, 1, 1)
    price = 150.0
    data = []
    for i in range(days):
        date = start + timedelta(days=i)
        if date.weekday() >= 5:
            continue
        o = round(price + random.gauss(0, 2), 2)
        h = round(o + abs(random.gauss(0, 3)), 2)
        l = round(o - abs(random.gauss(0, 3)), 2)
        c = round(random.uniform(l, h), 2)
        price = c
        ts = int(date.timestamp() * 1000)
        data.append([ts, o, h, l, c])
    return {"series": [{"type": "candlestick", "name": "ACME", "data": data}],
            "suggested_type": "stock"}


def sample_funnel() -> dict:
    """Dados de exemplo para funnel chart."""
    data = [
        ['Visitantes do Site', 15654],
        ['Downloads', 4064],
        ['Cadastros', 1987],
        ['Trial Ativo', 976],
        ['Compra', 846]
    ]
    return {"series": [{"data": data}], "suggested_type": "funnel"}


GENERATORS = {
    "line": sample_line, "spline": sample_line, "area": sample_line,
    "column": sample_column, "bar": sample_column,
    "pie": sample_pie, "donut": sample_pie,
    "scatter": sample_scatter, "bubble": sample_scatter,
    "heatmap": sample_heatmap,
    "sankey": sample_sankey,
    "gauge": sample_gauge, "solidgauge": sample_gauge,
    "treemap": sample_treemap,
    "stock": sample_stock, "candlestick": sample_stock,
    "funnel": sample_funnel, "pyramid": sample_funnel,
}


def main():
    parser = argparse.ArgumentParser(description="Gera dados de exemplo para Highcharts")
    parser.add_argument("--type", "-t", choices=list(GENERATORS.keys()),
                        help="Tipo de gráfico")
    parser.add_argument("--list", "-l", action="store_true", help="Lista tipos disponíveis")
    parser.add_argument("--output", "-o", help="Salvar em arquivo")
    args = parser.parse_args()

    if args.list:
        print("Tipos disponíveis:")
        for t in sorted(set(GENERATORS.keys())):
            print(f"  • {t}")
        return

    if not args.type:
        parser.print_help()
        sys.exit(1)

    generator = GENERATORS[args.type]
    result = generator()

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[INFO] Salvo em: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
