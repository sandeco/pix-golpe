# Catalogo de regimes tributarios

Catalogo extensivel usado pelo agente `reversa-pricing-profile` para mapear o regime tributario declarado pelo usuario em um `tax_factor` aproximado. Os fatores sao reservas didaticas para orcamento, nao aliquotas legais exatas.

## Como ler este arquivo

Cada regime tem:

- `key`: chave canonica gravada em `profile.json`
- `country`: codigo ISO 3166-1 alpha-2 ou `INTL`
- `name_pt_br`: nome amigavel usado no chat
- `tax_factor`: fator aproximado aplicado sobre custo direto
- `tax_factor_kind`: `effective_reserve_estimate`, `statutory_proxy` ou `not_computed`
- `includes_vat`: se combina imposto sobre renda/contribuicao com VAT/IVA/ISS destacado
- `vat_pass_through_warning`: se o estimate deve avisar que parte do imposto pode ser repassada ao cliente
- `tax_factor_source`: fonte publica ou descricao da base
- `notes_pt_br`: observacao curta para o usuario

## Disclaimer obrigatorio

Os fatores aqui registrados sao aproximacoes didaticas com base em referencia publica conhecida em 2026-05. Nao substituem orientacao contabil. A precisao depende de dedutiveis, municipio, faixa de receita, CNAE, enquadramento, retencoes, tratados internacionais e regras vigentes no momento da emissao da nota.

O agente deve repetir o disclaimer durante a entrevista e no rodape do `profile.md`.

## Brasil (BR)

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| MEI | Microempreendedor Individual (MEI) | 0.06 | effective_reserve_estimate | true | true | Portal do Empreendedor e regras publicas do DAS-MEI | Reserva simplificada. MEI costuma ter DAS fixo e limite de receita. Atividade de software pode exigir validacao de enquadramento. |
| simples_servicos | Simples Nacional, servicos de TI | 0.15 | effective_reserve_estimate | true | true | Receita Federal, Simples Nacional, anexos e fator R | Reserva media. Aliquota real depende de anexo, RBT12, fator R, ISS e retencoes. |
| lucro_presumido | Lucro Presumido, servicos | 0.165 | effective_reserve_estimate | true | true | Receita Federal, IRPJ, CSLL, PIS, COFINS e ISS | Reserva combinada para servicos. Validar ISS municipal e retencoes. |
| autonomo_pf | Pessoa fisica autonoma, carne-leao | 0.275 | effective_reserve_estimate | false | false | Receita Federal, IRPF progressivo e INSS | Reserva para profissional senior. Aliquota efetiva varia por deducoes e contribuicao previdenciaria. |

## Estados Unidos (US)

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| self_employed_1099 | Self-Employed, 1099, sole proprietor | 0.30 | effective_reserve_estimate | false | false | IRS, self-employment tax e federal income tax | Reserva combinada. Nao inclui state tax nem deducoes especificas. |
| s_corp_llc | S-Corp ou LLC com S-Corp election | 0.22 | effective_reserve_estimate | false | false | IRS, payroll tax, reasonable salary e distributions | Reserva simplificada. Exige contador para salario razoavel e distribuicoes. |

## Portugal (PT)

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| pt_simplificado | Categoria B, regime simplificado | 0.21 | effective_reserve_estimate | true | true | Autoridade Tributaria, IRS Categoria B, IVA e Seguranca Social | Reserva combinada. IVA pode ser destacado e repassado ao cliente. |
| pt_organizada | Categoria B, contabilidade organizada | 0.18 | effective_reserve_estimate | true | true | Autoridade Tributaria, contabilidade organizada | Reserva simplificada. Custos reais podem reduzir base tributavel. |

## Mexico (MX)

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| mx_resico | Regimen Simplificado de Confianza (RESICO) | 0.10 | effective_reserve_estimate | true | true | SAT, RESICO PF e IVA | Reserva combinada. ISR pode ser baixo, mas IVA pode aplicar conforme caso. |
| mx_actividad_empresarial | Actividad Empresarial y Profesional (PF) | 0.20 | effective_reserve_estimate | true | true | SAT, ISR progressivo e IVA | Reserva simplificada para profissional independente. |

## Internacional (INTL)

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| intl_freelance_no_withhold | Freelance internacional, cliente sem retencao | 0.00 | not_computed | false | false | Depende do pais do prestador | Cliente paga bruto. Use o regime nacional do prestador para imposto real. |
| intl_freelance_with_withhold | Freelance internacional, cliente retem na fonte | 0.15 | effective_reserve_estimate | false | false | Tratados bilaterais e regras locais | Retencao real depende de tratado e pais do cliente. |

## Outro

| key | name_pt_br | tax_factor | tax_factor_kind | includes_vat | vat_pass_through_warning | tax_factor_source | notes_pt_br |
|---|---|---:|---|---|---|---|---|
| outro | Outro regime, nao listado | 0.00 | not_computed | false | false | Usuario informou regime nao catalogado | Imposto nao computado. Estimate deve avisar que o calculo fica a cargo do contador. |

## Regimes essenciais para futuras regioes

Nao habilite estes paises como cobertos no cenario Mercado sem catalogar regimes minimos:

| country | regimes essenciais |
|---|---|
| GB | sole_trader_self_assessment, limited_company |
| DE | freiberufler, gewerbe_einzelunternehmen, gmbh |
| ES | autonomo_estimacion_directa_simplificada, autonomo_estimacion_directa_normal, sociedad_limitada |
| AR | monotributo, responsable_inscripto |
| CO | regimen_simple, regimen_ordinario_persona_natural, sociedad |

Fontes oficiais verificadas:

- UK GOV.UK, sole trader e limited company: https://www.gov.uk/set-up-business/sole-trader.html
- Alemanha, portal administrativo federal, registro fiscal: https://verwaltung.bund.de/leistungsverzeichnis/EN/leistung/99102019120000/herausgeber/HH-S1000020010000009790/region/020000000000
- Espanha, Agencia Tributaria, regimes de determinacao de rendimento: https://sede.agenciatributaria.gob.es/Sede/irpf/empresarios-individuales-profesionales/regimenes-determinar-rendimiento-actividad.html
- Argentina ARCA, Monotributo: https://www.afip.gob.ar/monotributo/
- Colombia DIAN, Regimen Simple de Tributacion: https://micrositios.dian.gov.co/regimen-simple-tributacion/

## Sugestao de regime padrao por pais

Quando o usuario responde "nao sei", o agente sugere o padrao abaixo e marca `tax_regime_confidence = "low"`:

| country | regime padrao sugerido |
|---|---|
| BR | simples_servicos |
| US | self_employed_1099 |
| PT | pt_simplificado |
| MX | mx_resico |
| Outro pais | sem sugestao, pedir escolha explicita |

## Como estender

1. Adicione a secao do pais com a mesma tabela
2. Cite fonte publica
3. Marque se o fator inclui VAT, IVA ou imposto destacado
4. Nao chame `tax_factor` de aliquota legal
5. Atualize o schema se novos campos forem necessarios
