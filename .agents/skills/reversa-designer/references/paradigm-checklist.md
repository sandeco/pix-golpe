# Checklist de honra ao paradigma alvo

Lista de verificação rápida que o Designer aplica antes de fechar `target_architecture.md` e `target_domain_model.md`.

## Event-driven

- [ ] Eventos têm nome no passado (`PedidoCriado`, não `CriarPedido`).
- [ ] Cada evento tem schema explícito com versionamento.
- [ ] Comandos e eventos são distintos.
- [ ] Idempotência é garantida por construção (event ID, chave de deduplicação).
- [ ] Ordem de mensagens é tratada por chave de particionamento.
- [ ] Saga / orquestrador para transações distribuídas, com compensação.
- [ ] Outbox table para garantia at-least-once entre BD e fila.
- [ ] DLQ definida para falhas terminais.

## OO com DI

- [ ] Interfaces explícitas para dependências externas.
- [ ] Container de injeção configurado por bounded context.
- [ ] Aggregates não dependem de infra (sem persistência dentro do aggregate).
- [ ] Repositórios concretos vivem na camada de infra.
- [ ] Active Record explicitamente proibido.

## Funcional

- [ ] Tipos imutáveis no domínio.
- [ ] Funções puras no núcleo; side effects em borda.
- [ ] Estado é sequência de transformações, não mutação.
- [ ] Composição usada para construir fluxos.
- [ ] Tipos algébricos (sum types) para estados disjuntos.

## Actor model

- [ ] Cada ator tem mailbox e estado isolado.
- [ ] Supervisão hierárquica definida.
- [ ] Mensagens entre atores são imutáveis.
- [ ] Persistência via event sourcing ou snapshot.

## Procedural / dataflow

- [ ] Fluxo expresso como pipeline de transformações.
- [ ] Sem mutação compartilhada.
- [ ] Estágios independentes e testáveis isolados.

## Geral (qualquer paradigma)

- [ ] Cada elemento aponta para origem no legado ou para `discard_log.md`.
- [ ] Bounded contexts justificados por coesão, não por estrutura legada.
- [ ] Diagrama Mermaid renderiza sem erro.
- [ ] Decisões arquiteturais documentadas no formato ADR resumido.
