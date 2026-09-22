# Benchmarks de mercado (market-benchmarks.md)

**Versao da tabela:** 2.0
**Data de referencia dos benchmarks:** 2026-05

Documenta as referencias estaticas que o agente `reversa-pricing-estimate` usa para o cenario Faixa de Mercado. A v2 remove faixas totais inventadas por combinacao e passa a usar benchmark horario por pais e senioridade, derivando o total pela faixa de horas do `effort-formula.md`.

## Disclaimer obrigatorio

Os numeros sao aproximacoes didaticas baseadas em fontes publicas e comerciais conhecidas em maio de 2026. Nao substituem pesquisa regional atualizada. Muitas fontes publicas trazem salario mensal ou anual, nao taxa freelance direta. Quando a linha deriva uma taxa freelance a partir de salario, o campo `source_kind` deve dizer isso explicitamente.

## Como calcular o cenario Mercado

Cada linha tem:

```
country | seniority | currency | min_hourly | max_hourly | source_kind | source_year | sources
```

O total por feature e derivado assim:

```
market_min = horas_min[complexity_class][seniority] * min_hourly
market_max = horas_max[complexity_class][seniority] * max_hourly
```

`pricing_model` muda apenas a apresentacao:

- `time_and_materials`: mostrar taxa hora e total estimado por horas
- `escopo_fechado`, `sprint`, `valor_fixo_por_entrega`: mostrar total por feature derivado por horas
- `retainer`: mostrar "faixa equivalente por feature dentro de retainer"

`client_profile` nao altera o numero na v2. Sem dataset por perfil, multiplicadores por cliente seriam invencao. O estimate.md pode adicionar alerta qualitativo para microempresa, pequena empresa ou enterprise.

## Tabela v2

| country | seniority | currency | min_hourly | max_hourly | source_kind | source_year | sources |
|---|---|---:|---:|---:|---|---:|---|
| BR | junior | BRL | 40 | 80 | salary_derived_freelance_estimate | 2025-2026 | Portal Salario CAGED, Glassdoor Brasil |
| BR | mid | BRL | 70 | 130 | salary_derived_freelance_estimate | 2025-2026 | Portal Salario CAGED, Glassdoor Brasil |
| BR | senior | BRL | 100 | 200 | salary_derived_freelance_estimate | 2025-2026 | Portal Salario CAGED, Glassdoor Brasil |
| BR | staff_lead | BRL | 160 | 300 | salary_derived_freelance_estimate | 2025-2026 | Portal Salario CAGED, Glassdoor Brasil |
| BR | principal | BRL | 220 | 420 | salary_derived_freelance_estimate | 2025-2026 | Portal Salario CAGED, Glassdoor Brasil |
| US | junior | USD | 20 | 40 | freelance_platform_and_public_wage | 2024-2025 | Upwork, O*NET/BLS |
| US | mid | USD | 40 | 70 | freelance_platform_and_public_wage | 2024-2025 | Upwork, O*NET/BLS |
| US | senior | USD | 70 | 150 | freelance_platform_and_public_wage | 2024-2025 | Upwork, O*NET/BLS |
| US | staff_lead | USD | 120 | 200 | freelance_platform_and_public_wage | 2024-2025 | Upwork, O*NET/BLS |
| US | principal | USD | 160 | 260 | freelance_platform_and_public_wage | 2024-2025 | Upwork, O*NET/BLS |
| PT | junior | EUR | 25 | 45 | salary_derived_contractor_estimate | 2024-2026 | Landing.Jobs, Hays Portugal |
| PT | mid | EUR | 40 | 70 | salary_derived_contractor_estimate | 2024-2026 | Landing.Jobs, Hays Portugal |
| PT | senior | EUR | 60 | 100 | salary_derived_contractor_estimate | 2024-2026 | Landing.Jobs, Hays Portugal |
| PT | staff_lead | EUR | 90 | 140 | salary_derived_contractor_estimate | 2024-2026 | Landing.Jobs, Hays Portugal |
| PT | principal | EUR | 120 | 180 | salary_derived_contractor_estimate | 2024-2026 | Landing.Jobs, Hays Portugal |
| MX | junior | MXN | 200 | 400 | salary_derived_freelance_estimate | 2025 | Glassdoor Mexico, Computrabajo Mexico |
| MX | mid | MXN | 350 | 650 | salary_derived_freelance_estimate | 2025 | Glassdoor Mexico, Computrabajo Mexico |
| MX | senior | MXN | 600 | 1000 | salary_derived_freelance_estimate | 2025 | Glassdoor Mexico, Computrabajo Mexico |
| MX | staff_lead | MXN | 900 | 1500 | salary_derived_freelance_estimate | 2025 | Glassdoor Mexico, Computrabajo Mexico |
| MX | principal | MXN | 1200 | 2000 | salary_derived_freelance_estimate | 2025 | Glassdoor Mexico, Computrabajo Mexico |

## Aliases de senioridade

```
pleno -> mid
especialista -> staff_lead
staff -> staff_lead
lead -> staff_lead
```

## Fontes

- Portal Salario, Programador de Sistemas de Informacao, CBO 317110, dados CAGED/eSocial/Empregador Web, atualizado em 2026: https://www.salario.com.br/profissao/programador-de-sistemas-de-informacao-cbo-317110/
- Glassdoor Brasil, Software Developer, faixa mensal, atualizado em 2025: https://www.glassdoor.com/Salaries/br%C3%A9sil-software-developer-salary-SRCH_IL.0%2C6_IN36_KO7%2C25.htm
- O*NET Online, Software Developers 15-1252.00, salarios locais com fonte BLS 2024: https://www.onetonline.org/link/localwages/15-1252.00
- Upwork, Software Developer hourly cost guide, faixas entry, intermediate e expert: https://www.upwork.com/hire/software-developers/cost/
- Landing.Jobs Global Tech Talent Trends 2024: https://campaign.landing.jobs/gttt-2024
- Hays Portugal Salary Guide 2026: https://www.hays.pt/en/salary-guide/overview
- Glassdoor Mexico, Software Developer, faixa mensal, atualizado em 2025: https://www.glassdoor.com/Salaries/mexico-software-developer-salary-SRCH_IL.0%2C6_IN169_KO7%2C25.htm
- Computrabajo Mexico, salarios de Developer e Desarrollador IT, atualizado em 2025: https://mx.computrabajo.com/salarios/desarrollador-it

## Regras de fallback

1. Se `country` nao estiver na tabela, Mercado fica `unavailable: true`
2. Se `seniority` vier em alias, normalize e calcule
3. Se `pricing_model` nao estiver entre os modelos conhecidos, use apresentacao de `escopo_fechado` e registre fallback
4. `client_profile` nao altera preco na v2
5. `complexity_class` sempre deve existir no size; se ausente, falhe com mensagem pedindo recalculo do Sizer

## Paises nao cobertos na v2

Para `country` fora de `[BR, US, PT, MX]`, o cenario Mercado fica indisponivel com explicacao:

"Faixa de mercado para `<country>` ainda nao esta documentada nesta versao do Reversa. Cobertos na v2: BR, US, PT, MX."

## Como estender

Para adicionar pais:

1. Prefira fonte publica de taxa freelance direta
2. Se usar salario, registre `source_kind = salary_derived_freelance_estimate`
3. Cite fonte e ano por linha
4. Nao adicione multiplicadores por `client_profile` sem dataset
5. Bump em `market` formula_version
