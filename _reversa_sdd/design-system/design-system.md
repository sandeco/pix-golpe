# Design System: pix-golpe

> Documento consolidado gerado pelo Design System (Reversa) em 2026-09-21. Fontes: CSS e JS inline de `static/index.html`, screenshots `docs/tela-corrida.png` (1920×5657) e `docs/relatorio-acuracia.png` (1920×1080). Detalhes em `color-palette.md`, `typography.md`, `spacing.md`, `tokens.md`. 🟢 extraído, 🟡 inferido.

## 1. Princípios observados

1. **Feito para a câmera:** frame fixo de 1920 px, tipografia gigante (contador 108 px), contraste alto, tema escuro único. Tudo escala por `zoom`, nada "reflui".
2. **Dois lados, duas cores:** rosa `#ff2d95` (Rust + Jev) e azul `#6985f6` (Python + DeepSeek) atravessam título, borda, progresso, números, badges e canvas. O lado é a única variável de cor de marca.
3. **Semântica por veredito:** vermelho pulsante para GOLPE, verde para OK/conectado, âmbar para SUSPEITA/laranjas, cinza para aguardando/erro.
4. **Leigo primeiro:** rótulos em caixa alta com tracking ("MENSAGENS PROCESSADAS", "GOLPISTA → LARANJAS → SAQUE"), prosa nos resumos, tipos de golpe traduzidos.
5. **Movimento curto e honesto:** flash 600 ms, onda 300 ms, moedas 1 s; nada que mascare a diferença real de tempo; tudo desligável por `prefers-reduced-motion`.

## 2. Componentes

| Componente | Seletor | Variantes / estados | Conf. |
|---|---|---|---|
| Topbar | `.topbar` | sticky; contém título, conexão, ritmo, ações | 🟢 |
| Indicador de conexão | `.connection[data-state]` | `offline` (âmbar), `connected` (verde com glow) | 🟢 |
| Select de ritmo | `select#mode` | Narrado · 4 s, Normal; `disabled` | 🟢 |
| Botão primário | `.start[data-action]` | `start` (claro), `stop` (vermelho), `disabled` (opacidade 0,45), hover com glow | 🟢 |
| Botão secundário | `.report-button` | hover mais claro; `.report-close` | 🟢 |
| Lane | `.lane`, `.lane.python`, `[data-stopped]` | borda superior 4 px no acento; gradiente sutil | 🟢 |
| Contador | `.counter`, `.processed`, `.out-of`, `.counter-label`, `.stopped` | display 108 px; "Parado" quando parado | 🟢 |
| Barra de progresso | `.progress` / `.progress-fill` | `role=progressbar`; largura animada 140 ms | 🟢 |
| Velocidades | `dl.speed .speed-row` | 3 linhas (decisão, rastreio, memória) com "N×" | 🟢 |
| Bolha da mensagem | `button.bubble[data-empty]` | vazia ("Aguardando..."), preenchida, clicável só em golpe | 🟢 |
| Selo de veredito | `.verdict[data-verdict]` | `waiting`, `golpe` (pulse), `ok`, `revisar`, `error` | 🟢 |
| Painel do grafo | `.graph-panel`, `.graph-canvas`, `.graph-empty`, `.graph-tip` | vazio, rastreando, desenhado; tooltip | 🟢 |
| Fluxo do dinheiro | `.money`, `.money-flow`, `.money-group`, `.arrow .coin`, `.orange-grid .account`, `.cash-grid .cash`, `.money-summary` | vazio, preenchido, animando | 🟢 |
| Lista de golpes | `.scam-history`, `ol.scam-list`, `button.scam-row[data-selected]`, `.scam-badge`, `.scam-type`, `.scam-probability` | vazia, com itens, selecionado | 🟢 |
| Acumulador | `.accumulator` | texto "N processadas · N golpes · N ok" | 🟢 |
| Flash de alerta | `.alert-wash` | animação de opacidade | 🟢 |
| Cartão final | `section#final.final`, `.final-side`, `.final-time`, `.final-stats` | oculto/visível; `.compact` para números longos | 🟢 |
| Relatório | `section#accuracy-report`, `.report-heading`, `.report-note`, tabela 2×3, `.report-conclusion` | células verde/vermelho/neutra; N/D | 🟢 |
| Modal de detalhes | `#scam-modal.scam-backdrop`, `.scam-dialog[data-side]`, `.detail-*`, `.score-track[role=meter]` | 2 colunas / 1 coluna ≤ 1050 px | 🟢 |
| Rodapé | `.footer` | texto fixo de disclaimer | 🟢 |
| Utilitários | `.sr-only`, `[hidden]` | | 🟢 |

## 3. Layout de referência (screenshot da corrida)

```
┌ topbar: [PIX RACE / DETECTOR DE GOLPE]        ● Conectado  Ritmo [Normal ▾] [Parar] ┐
├──────────────────────────────┬──────────────────────────────────────────────────────┤
│ Rust + Jev (rosa)            │ Python + DeepSeek (azul)                             │
│ 143 / 1000   [mensagem atual]│ 38 / 1000   [mensagem atual]                          │
│ MENSAGENS PROCESSADAS  GOLPE │ MENSAGENS PROCESSADAS  ✓ OK                           │
│ ▓▓▓▓░░░░ progresso           │ ▓░░░░░░░ progresso                                    │
│ Caminho do dinheiro · #141   │ Caminho do dinheiro                                   │
│   (grafo radial)             │   "A investigação começa na chave Pix"                │
│ GOLPISTA → LARANJAS → SAQUE  │ Nenhum golpe rastreado ainda                          │
│ Golpes acumulados (lista)    │ Golpes acumulados (vazio)                             │
│ 143 processadas · 27 golpes… │ 38 processadas · 0 golpes · 38 ok                     │
└──────────────────────────────┴──────────────────────────────────────────────────────┘
  rodapé: Mensagens simuladas. Transações simuladas. Mesmo algoritmo…
```

## 4. Acessibilidade

- `role=dialog` + `aria-labelledby/describedby` nos overlays; `aria-modal=true` só no modal de detalhes. 🟢
- `role=status`/`aria-live` no veredito e no indicador de conexão; `role=progressbar` e `role=meter` com valores. 🟢
- Foco visível 3 px branco; foco preso no modal; `Escape` fecha. 🟢
- `prefers-reduced-motion` respeitado. 🟢
- Contraste alto por construção (tema escuro, texto claro). 🟡

## 5. Lacunas e recomendações

- 🟡 A paleta tem dezenas de variações de cinza/rosa/âmbar; consolidar nos tokens de `tokens.md`.
- 🟡 Cor "roxo" para saques (SPEC §5) não aparece como token explícito; confirmar no canvas.
- 🟡 Título divergente entre screenshot ("PIX RACE") e HTML ("DETECTOR DE GOLPE").
- 🟢 Não há variante clara nem responsividade real; se a tela for reutilizada fora da gravação, definir breakpoints.
- 🟢 Fonte depende do Windows (Segoe UI); em outros sistemas cai para Arial e os pesos 650/750/850 são arredondados.
