# Permissões e papéis: pix-golpe

> Gerado pelo Detective (Reversa) em 2026-09-21. 🟢 CONFIRMADO.

## Resumo

Não existe autenticação, autorização, sessão ou papel de usuário no sistema. É uma demo local single-user para gravação de vídeo. Qualquer cliente que alcance a porta 8080 pode fazer tudo.

## Atores

| Ator | Como entra | O que pode fazer |
|---|---|---|
| Apresentador (browser) | `GET /` e `GET /ws` | start, pace, stop, reset, report; ver todos os eventos |
| Worker Python | `GET /ws/worker` | receber hello/run/message/pace/stop/reset; emitir status, decision, trace, error, done |
| Operador (terminal) | `cargo run`, `python` | gerar dados, subir servidor, rodar CLIs de conferência |
| TypeSafe AI, DeepSeek | chamadas de saída | recebem remetente + texto; nunca recebem `golpe_real` nem a chave |

## Matriz de acesso (implícita)

| Recurso | Browser | Worker | Observação |
|---|---|---|---|
| Iniciar/parar/reiniciar corrida | sim | não (ignora comandos) | qualquer browser conectado; múltiplos browsers compartilham a mesma corrida via broadcast |
| Trocar ritmo | sim | não | |
| Relatório de acurácia | sim | não | só browsers recebem `report` |
| Emitir decision/trace/done | não | sim | servidor força `side = "python"` em tudo que vem do worker |
| Registrar veredito | lado Rust interno, worker | | `registrar_verdict` |
| Ler `golpe_real` / `meta.json` | não (só via `report` e `truth` agregados) | não | verdade fica no servidor |
| Ler `static/index.html` | sim | | do disco, a cada request |
| Chaves de API | ninguém pela rede | | `.env` local, só no processo |

## Superfície de rede e riscos 🟢

| Item | Estado | Risco |
|---|---|---|
| Bind | `0.0.0.0:8080` (`server.rs:214`) | qualquer host da rede local pode abrir a tela e comandar a corrida (custo de API) |
| `/ws/worker` | sem segredo | um cliente qualquer pode se passar pelo worker Python; um worker novo substitui o slot |
| Origem do WS | não verificada | CSRF via WebSocket de outra origem seria possível |
| Segredos | `.env` na raiz, também citado em `C:\RUST-PROJECTS\.env` | não versionar; PDF e README usam marcadores |
| Dados sensíveis | nenhum: tudo sintético | |

Nenhum desses itens é requisito do produto (demo local); ficam registrados para um eventual uso fora da máquina do apresentador.
