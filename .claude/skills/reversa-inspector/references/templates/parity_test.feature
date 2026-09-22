# Template de cenário Gherkin para parity_tests/.
# Cada arquivo deve cobrir um fluxo crítico identificado em process_flows do legado.
# Adaptar critérios ao paradigma alvo conforme `parity_specs.md`.

# language: pt
# spec-id: PT-001
# rastreabilidade:
#   process_flows: <ref ao fluxo no _reversa_sdd>
#   target_architecture: <ref a componente no target_architecture.md>
#   paradigma_alvo: <do paradigm_decision.md>

Funcionalidade: <Nome do fluxo>
  Como <ator>
  Quero <ação>
  Para <objetivo>

  # Critério geral de paridade aplicado a este cenário.
  # Quando o paradigma alvo é event-driven, expressar tolerância de consistência eventual aqui.
  @paridade @critico
  Cenário: <descrição>
    Dado <pré-condição observável>
    E <pré-condição secundária>
    Quando <ação executada via API / comando / evento de entrada>
    Então <efeito observável no sistema novo>
    E <efeito observável persiste após <janela de propagação>>

  # Cenário específico para validar idempotência (event-driven, retry seguro).
  @paridade @idempotencia
  Cenário: Reprocessamento não duplica efeito
    Dado <pré-condição>
    Quando <ação> é processada uma vez
    E <ação> é reentregue por retry
    Então o efeito observável é idêntico ao da primeira entrega

  # Cenário específico para validar ordem em paradigma event-driven.
  @paridade @ordem
  Cenário: Ordem de eventos é respeitada por chave
    Dado <chave de particionamento>
    Quando <evento A> é publicado antes de <evento B> com a mesma chave
    Então <efeito observável> reflete a ordem A → B
