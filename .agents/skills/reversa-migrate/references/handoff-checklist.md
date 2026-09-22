# Checklist do `handoff.md`

Antes de fechar o pipeline, o orquestrador valida que `handoff.md` cumpre todos os itens.

## Checklist obrigatório

- [ ] `paradigm_decision.md` aparece como **primeiro item** da seção "Leitura obrigatória" e da "Ordem de leitura recomendada".
- [ ] `topology_decision.md` aparece como **segundo item** da seção "Leitura obrigatória".
- [ ] `screen_modernization_decision.md` aparece como **terceiro item** quando há UI; em legado sem UI (Screen Translator skipped), a entrada é omitida com nota explícita "Screen Translator pulado, legado sem UI".
- [ ] Lista de artefatos produzidos é completa e reflete `_reversa_sdd/migration/` e `_reversa_sdd/screens/` reais.
- [ ] Deviations pendentes em `screen_deviation_log.md` aparecem como bloqueadores; deviations aprovadas estão refletidas em `parity_specs.md § Exceções`.
- [ ] Itens REFERIDOS À CODIFICAÇÃO de `ambiguity_log.md` aparecem em seção dedicada de `handoff.md`.
- [ ] Bloqueadores listados ou linha "nenhum bloqueador, prosseguir".
- [ ] Próximos passos para o agente de codificação são específicos e acionáveis (não genéricos).
- [ ] Em `--auto`: itens auto-decididos listados explicitamente.
- [ ] Estilo coerente com a engine instalada (formato adaptado, ex: front-matter compatível).

## Estrutura mínima

1. Banner de leitura obrigatória do `paradigm_decision.md`, `topology_decision.md` e (se houver UI) `screen_modernization_decision.md`.
2. Ordem de leitura recomendada.
3. Lista de artefatos.
4. Bloqueadores.
5. Próximos passos para o agente de codificação.
6. Itens auto-decididos (apenas se `--auto`).
7. Notas finais.

## Sinalização forte ao agente de codificação

A primeira frase de `handoff.md` deve transmitir clareza imediata. Padrão sugerido:

> "Sistema novo a ser construído em paradigma <X>, topologia <Y>, telas em modo <Z>. Antes de qualquer linha de código, leia `paradigm_decision.md`, `topology_decision.md` e `screen_modernization_decision.md`."

Em legado sem UI (Screen Translator skipped), substituir o trecho de telas por: "telas: nenhuma (sistema sem UI)".
