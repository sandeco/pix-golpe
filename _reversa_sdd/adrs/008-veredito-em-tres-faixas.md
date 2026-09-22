# ADR-008: Veredito em três faixas e tratamento de "revisar" no relatório

**Status:** aceita. **Confiança:** 🟢 (SPEC §2, `jev.rs:33-41`, `server.rs:99`, tela).

## Contexto

Um limiar único forçaria alarmes em mensagens ambíguas. Para o vídeo, é melhor mostrar "suspeita" do que errar alto.

## Decisão

- `golpe >= 0,6` → golpe (rastreia); `<= 0,4` → ok; entre → revisar (tela: SUSPEITA), sem rastreio.
- No relatório binário, `revisar` conta como não detectado: falso negativo se era golpe, verdadeiro negativo se era normal.
- Só o escore `golpe` decide; tipo, urgência e pede_pix são descritivos na tela e no modal de detalhes.

## Alternativas consideradas

- Limiar único em 0,5: rejeitado, mais falsos alarmes.
- Rastrear também em `revisar`: rejeitado, aumentaria custo de rastreio e ruído visual.

## Consequências

- No README, o Jev deixou 1 golpe e 8 normais como "suspeita" em 1.000 mensagens; o relatório mostra isso com honestidade.
- Um golpe em `revisar` reduz o recall do lado, mesmo sem alarme falso.
