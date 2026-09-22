# Domínio: pix-golpe

> Gerado pelo Detective (Reversa) em 2026-09-21. Escala: 🟢 CONFIRMADO (código), 🟡 INFERIDO (docs, brainstorm, padrões), 🔴 LACUNA.
> Sem histórico Git: o projeto não é repositório. A "arqueologia" usou `BRAINSTORMING/BRAINSTORM_jev_rust_youtube.md`, `SPEC.md`, `README.md`, o PDF do projeto e comentários no código.

## 1. Propósito e público

O software é uma **demonstração para vídeo** do canal do usuário (público brasileiro leigo e desenvolvedores). Ele encena uma corrida entre dois pipelines idênticos, Rust + Jev e Python + DeepSeek, para mostrar diferença de velocidade e custo com acurácia equivalente. Não é produto antifraude: não consulta bancos, não bloqueia Pix, não recupera dinheiro. 🟢 (README, PDF p.1, rodapé da tela)

Objetivos declarados no brainstorm 🟡: visual, processa texto em linguagem natural, Jev para decisão rápida, etapa pesada onde Rust seja visivelmente mais rápido que Python, comparação justa e declarada na tela.

## 2. Glossário

| Termo | Definição | Fonte |
|---|---|---|
| **Lado** | Um dos dois pipelines: `rust` (Jev + graph.rs no servidor) ou `python` (DeepSeek + trace.py no worker) | 🟢 |
| **Corrida (run)** | Uma execução completa das 1.000 mensagens nos dois lados, identificada por `run_id` crescente | 🟢 |
| **Ritmo (pace)** | Pausa por mensagem em cada lado. `Narrado · 4 s` = `step:4000`; `Normal` = `serial` (0 ms) | 🟢 |
| **Rajada (burst)** | Modo com 8 decisões em voo por lado; existe no protocolo, não no seletor da tela; usado no benchmark do README | 🟢 |
| **Mensagem** | Texto em português, com remetente e chave Pix, sintético, gerado por template | 🟢 |
| **Golpe real** | Rótulo `golpe_real` do gerador, verdade de referência; nunca vai ao modelo | 🟢 |
| **Decisão** | Resposta do modelo às 4 perguntas: `golpe`, `tipo`, `urgencia`, `pede_pix` | 🟢 |
| **Veredito** | `golpe` / `revisar` (tela: SUSPEITA) / `ok`, derivado só do escore `golpe` | 🟢 |
| **Chave Pix** | Identificador citado na mensagem, resolvido para uma conta pelo mapa `chaves.json` | 🟢 |
| **Conta** | Nó do grafo, id `u32` em 0..999.999 | 🟢 |
| **Hub** | Conta comerciante (ids 0..1999) com muitas entradas e lotes de saída; "explode" o rastreio | 🟢 |
| **Quadrilha** | Esquema sintético: 1 conta da chave, 12 a 18 laranjas, 2 contas de saque, 20 a 40 vítimas | 🟢 |
| **Laranja** | Conta intermediária: mesma comunidade da chave e suspeição ≥ 0,6 | 🟢 |
| **Conta de saque** | Destino final: recebe ≥ 3 transferências de laranjas e repassa < 30 % | 🟢 |
| **Rastreio (trace)** | Passos A a D sobre o grafo a partir da conta da chave e do `ts` da mensagem | 🟢 |
| **Suspeição** | Nota 0..1 por conta: 0,4 repasse + 0,5 rapidez + 0,1 pequeno | 🟢 |
| **Comunidade** | Conjunto de contas com o mesmo rótulo da chave após propagação de rótulos | 🟢 |
| **Truth** | Comparação do rastreio com `meta.json`: laranjas e saques acertados | 🟢 |
| **Verdade de referência** | `meta.json` + `golpe_real`: só para placar e relatório | 🟢 |
| **Relatório de acurácia** | Matriz real × veredito por lado, com acurácia, precisão e recall | 🟢 |
| **Cartão final** | Overlay quando os dois lados terminam; serve de thumbnail | 🟢 |
| **Aquecimento** | Chamada inicial ao modelo para tirar o handshake TLS da medição | 🟢 |
| **Mock** | `?mock=1`: eventos falsos locais para desenvolver a tela | 🟢 |

## 3. Regras de negócio

### 3.1 Decisão

| ID | Regra | Fonte | Conf. |
|---|---|---|---|
| RN-01 | As mesmas mensagens, na mesma ordem, entram nos dois lados ao mesmo tempo. O servidor despacha todas de uma vez; o ritmo é aplicado por lado. | `server.rs:313-319` | 🟢 |
| RN-02 | Os dois lados respondem as mesmas 4 perguntas: golpe (0..1), tipo (8 categorias), urgência (0..2), pede_pix (0..1). Estado em português, instruções em inglês. | `jev.rs:43-58`, `deepseek.py:29-34` | 🟢 |
| RN-03 | Veredito: `golpe >= 0,6` → golpe; `<= 0,4` → ok; entre → revisar. Só o escore `golpe` decide; tipo, urgência e pede_pix são descritivos. | `jev.rs:33-41`, `deepseek.py:71-72` | 🟢 |
| RN-04 | Só veredito `golpe` dispara rastreio. `revisar` sinaliza suspeita sem rastrear. | `server.rs:374`, `worker.py:265` | 🟢 |
| RN-05 | O modelo recebe apenas remetente e texto. `golpe_real` e a chave não vão ao modelo; a chave já vem no dataset. | `server.rs:317`, `jev.rs:113` | 🟢 |
| RN-06 | Concorrência das decisões é a informada no evento `run`: 1 nos modos passo a passo e serial, 8 na rajada, igual nos dois lados. | `server.rs:306`, `worker.py:213` | 🟢 |
| RN-07 | Latência de decisão é a ida e volta HTTP medida pelo próprio lado. Rust inclui backoff de retry; Python exclui. | `server.rs:338`, `deepseek.py:147` | 🟢 assimetria |
| RN-08 | Custo: Jev `tokens_in × 0,042/M` (saída grátis); DeepSeek `in × 0,28/M + out × 0,42/M`, marcado "estimado" na tela. | `jev.rs:10`, `deepseek.py:24-25`, `index.html` | 🟢 |
| RN-09 | Retentativas: Jev 3× em 429/529 (200·2ⁿ ms); DeepSeek 3 tentativas em 429/5xx (2ⁿ s). Outros erros viram evento `error` e contam em `erros`; a corrida não trava. | `jev.rs:139`, `deepseek.py:149` | 🟢 |
| RN-10 | Resposta do DeepSeek fora do contrato (JSON inválido, campo fora da faixa, tipo desconhecido) é erro do lado Python, não veredito. | `deepseek.py:79-112` | 🟢 |
| RN-11 | Os dois lados fazem uma chamada de aquecimento na inicialização, fora da medição. | `server.rs:165`, `worker.py:165` | 🟢 |

### 3.2 Rastreio

| ID | Regra | Fonte | Conf. |
|---|---|---|---|
| RN-20 | O rastreio parte da conta da chave e do `ts` da mensagem (`t0`), não de uma extração livre da chave pela IA. | `server.rs:377-378` | 🟢 |
| RN-21 | Só transferências ≥ R$ 20 contam; janela de 24 h contada a partir da chegada em cada conta; profundidade máxima 5; máximo 40.000 contas visitadas. | `graph.rs:8-12` | 🟢 |
| RN-22 | Suspeição = 0,4·repasse + 0,5·rapidez + 0,1·pequeno. Rapidez zera se o primeiro repasse demora ≥ 1 h. Pequeno = menos de 50 entradas no histórico inteiro (descarta hubs). | `graph.rs:150-156` | 🟢 |
| RN-23 | Laranja: mesma comunidade da chave (10 iterações de propagação de rótulos ponderada por suspeição, empate → menor id) e suspeição ≥ 0,6. | `graph.rs:198-228` | 🟢 |
| RN-24 | Conta de saque: não é laranja, recebeu ≥ 3 transferências (contadas, não remetentes únicos) de laranjas no subgrafo e repassou < 30 %. | `graph.rs:239-243` | 🟢 |
| RN-25 | O algoritmo é determinístico e idêntico em Rust e Python puro (sem numpy), incluindo ordem de soma em ponto flutuante e arredondamento `f64::round`. Verificado nas 40 quadrilhas. | `trace.py:25-31,222`, README | 🟢 |
| RN-26 | Rastreio serializado por lado (um por vez) para comparar algoritmo, não número de núcleos. Tempo medido = passos A a D; carga do grafo e seleção para desenho ficam fora. | `server.rs:379`, `worker.py:236,267` | 🟢 |
| RN-27 | Para a tela vão no máximo 800 nós (chave, laranjas, saque, depois por profundidade) e 1.500 arestas (prioridade às que tocam nós especiais). | `graph.rs:309-364` | 🟢 |
| RN-28 | O servidor acrescenta `truth` a todo `trace` de qualquer lado comparando com `meta.json`; chave desconhecida → zeros. | `server.rs:117-139` | 🟢 |

### 3.3 Corrida e ritmo

| ID | Regra | Fonte | Conf. |
|---|---|---|---|
| RN-30 | `start`, `stop` e `reset` incrementam `run_id`; qualquer resultado de corrida anterior é descartado em todas as camadas. | `server.rs:264-289`, `worker.py:219`, `index.html:1250` | 🟢 |
| RN-31 | O ritmo pode ser trocado no meio da corrida e vale a partir da próxima mensagem de cada lado. | `server.rs:273-278`, `worker.py:209` | 🟢 |
| RN-32 | No ritmo narrado o lado dorme `pace_ms` depois de emitir a decisão, ainda segurando a vaga de concorrência. | `server.rs:369-373`, `worker.py:263` | 🟢 |
| RN-33 | `Parar` congela a tela onde está; nada mais muda até um `reset`. O relatório fica disponível. | `index.html:1263,1275` | 🟢 |
| RN-34 | `done` de um lado sai quando todas as mensagens daquele lado foram processadas (inclusive erros). O cartão final só aparece com os dois `done`. | `worker.py:293-296`, `index.html:1070` | 🟢 |
| RN-35 | Reiniciar com corrida existente = `reset` seguido de `start` com o ritmo escolhido. | `index.html` `start()` | 🟢 |

### 3.4 Relatório de acurácia

| ID | Regra | Fonte | Conf. |
|---|---|---|---|
| RN-40 | Matriz por lado: linhas = real (golpe/normal), colunas = veredito (golpe/revisar/ok), só sobre mensagens com veredito registrado. | `server.rs:86-113` | 🟢 |
| RN-41 | Para métricas binárias, `revisar` conta como não detectado: falso negativo em golpe real, verdadeiro negativo em normal. | `server.rs:99` | 🟢 |
| RN-42 | Acurácia = (tp+tn)/avaliadas; precisão = tp/(tp+fp); recall = tp/(tp+fn); divisão por zero → 0 (tela mostra N/D). | `server.rs:101-109` | 🟢 |
| RN-43 | Corridas interrompidas geram relatório parcial, só das mensagens avaliadas por cada lado; a tela avisa. | `index.html` `showReport` | 🟢 |

### 3.5 Dados sintéticos

| ID | Regra | Fonte | Conf. |
|---|---|---|---|
| RN-50 | Tudo é simulado e reprodutível: `ChaCha8Rng` seed 42; o dataset é idêntico a cada geração. | `gerar_dados.rs:125` | 🟢 |
| RN-51 | Volume oficial: 1.000.000 contas, 2.000 hubs, 10 dias, 9.968.511 transações, 40 quadrilhas, 1.000 mensagens (75 golpes). Confirmado pelo usuário em 2026-09-22; SPEC/README/PDF desatualizados. | `gerar_dados.rs:11-17`, `meta.json` | 🟢 |
| RN-52 | Padrão de quadrilha: vítimas pagam R$ 300 a 3.000 em 2 h; chave repassa a 12..18 laranjas ~2 h depois em 5 min; laranjas repassam a 1 de 2 saques em 10 a 45 min. | `gerar_dados.rs:188-220` | 🟢 |
| RN-53 | Mensagem de golpe chega 2 a 10 min antes do início dos pagamentos; aponta para a chave da quadrilha. | `gerar_dados.rs:236` | 🟢 |
| RN-54 | Mensagens legítimas têm remetente coerente com o texto (mesma loja/banco), correção feita para evitar falsos positivos. | `gerar_dados.rs:245-250`, brainstorm | 🟢 |
| RN-55 | Contas de saque "não movimentam nada nas 24 h seguintes" (SPEC); o gerador só garante que o esquema da quadrilha não as movimenta. Medido no dataset: 807 transações de fundo **saem** de contas de saque e 1.032 chegam a elas (das quais 606 são do esquema). A promessa do SPEC não vale. | SPEC §1 vs `gerar_dados.rs:141`; varredura de `transacoes.bin` | 🟢 divergência |

### 3.6 Justiça da comparação (regras do vídeo) 🟡→🟢

| ID | Regra | Fonte |
|---|---|---|
| RN-60 | Mesmo dataset, mesmas perguntas, mesma concorrência, rastreio serializado, Python puro sem numpy, Rust em release. | README, SPEC, brainstorm |
| RN-61 | Anunciar "Rust vs Python puro", não vs ecossistema numpy. | brainstorm (Codex) |
| RN-62 | Mostrar latência completa (p50/p95), separar decisão de rastreio, mostrar custo e modelo real retornado. | brainstorm, `done`, `status.model` |
| RN-63 | Honestidade: os dois modelos acertam quase tudo; a vantagem do Jev é velocidade e custo; a matriz de confusão dos dois fica visível. | README |

## 4. Lacunas 🔴

| ID | Lacuna | Onde registrar |
|---|---|---|
| ~~L1~~ | Escala oficial do dataset: resolvida, vale o código (1 M / ~10 M) | respondida 2026-09-22 |
| L2 | SPEC diz `include_str!`; servidor lê `index.html` do disco | divergência documental |
| ~~L3~~ | Contas de saque (RN-55): resolvida, vale o código; SPEC a corrigir | respondida 2026-09-22 |
| L4 | Assimetria da medição de retry (RN-07): usuário não sabe; decisão pendente | `questions.md` Pergunta 2 🔴 |
