# Passo 3, Organização das specs

Este passo acontece imediatamente após o usuário escolher o `doc_level` (Essencial / Completo / Detalhado) e antes da invocação do Archaeologist. É o momento em que o Reversa decide e persiste em qual estrutura as specs serão geradas.

## 1. Decidir se o menu deve ser exibido

Leia, nesta ordem, e mescle chave a chave (precedência total para `config.user.toml`):

1. `.reversa/config.toml`, seção `[specs]` (config gerenciado pelo Reversa)
2. `.reversa/config.user.toml`, seção `[specs]` (override manual do usuário)

A mescla é avaliada por chave: cada chave presente em `config.user.toml` substitui a correspondente em `config.toml`. Chaves ausentes continuam vindas de `config.toml`.

A seção é considerada **decidida** quando, após a mescla, `granularity` está preenchida com um dos valores válidos: `module`, `use-case`, `endpoint`, `hybrid`, `feature`, `custom`.

- **Se decidida:** pule este passo inteiro. Vá direto para a invocação do Archaeologist.
- **Se não decidida** (seção ausente, ou `granularity` vazia): apresente o menu (passo 2 abaixo).

### Caso especial, RF-18

Se `granularity` está vazia em `config.toml` (ou a seção foi removida) **e** existe seção `[specs]` em `config.user.toml` com qualquer chave preenchida, avise o usuário antes de exibir o menu. Use exatamente este formato:

> "Detectei que `.reversa/config.toml` não tem decisão de organização das specs, mas `.reversa/config.user.toml` contém um override em `[specs]`. O override continuará ativo após a sua escolha e pode sobrescrever campos que você decidir agora.
>
> Override atual em `config.user.toml`:
> [listar chaves e valores]
>
> Quer prosseguir com o menu mesmo assim? (s/N)"

Aguarde resposta afirmativa explícita antes de seguir para o menu. Resposta vazia ou negativa aborta sem persistir nada.

## 2. Apresentar o menu

Leia `.reversa/context/surface.json` → `organization_suggestion`. Use o campo `granularity` para pré-marcar a opção sugerida e o campo `rationale` para mostrar a razão.

Se o `surface.json` não tiver `organization_suggestion` preenchida (Scout não rodou ou falhou), exiba o menu sem default e peça que o usuário escolha manualmente, conforme EC-01 da spec de organização.

Use exatamente este formato (idioma seguindo `chat_language` do `state.json`, exemplo abaixo em pt-br):

```
Como você quer organizar as specs deste projeto?

O Scout analisou o legado e sugere: [tradução da granularity sugerida].
Razão: [organization_suggestion.rationale]

  [1] [marcador] Por módulo de código
  [2] [marcador] Por caso de uso
  [3] [marcador] Por endpoint/contrato
  [4] [marcador] Híbrida (módulo na raiz, casos de uso aninhados)
  [5] [marcador] Por features (Scout lista as features descobertas)
  [6] [marcador] Customizada

Escolha (Enter aceita o sugerido):
```

Onde `[marcador]` é `*` (asterisco) na opção pré-marcada e espaço nas demais. Adicione `(sugerido)` ao lado da opção pré-marcada.

Mapeamento das 6 opções para o valor de `granularity`:

| Opção | `granularity` |
|-------|---------------|
| 1 | `module` |
| 2 | `use-case` |
| 3 | `endpoint` |
| 4 | `hybrid` |
| 5 | `feature` |
| 6 | `custom` |

### Aceitar a entrada

- Enter sem digitar: aceita a opção pré-marcada.
- Número de 1 a 6: aceita a opção correspondente.
- Qualquer outra entrada: peça novamente sem persistir nada.
- Ctrl+C / ESC / cancelamento: aborte a execução e não persista nada (EC-02).

### Opção 6, customizada

Se o usuário escolher 6, abra o seguinte prompt:

> "Quais são os nomes das pastas de primeiro nível? Liste separados por vírgula ou um por linha (mínimo 1)."

Aceite a entrada, sanitize cada nome (remova caracteres proibidos pelo sistema de arquivos do OS, descarte nomes vazios). Se a lista resultar vazia, repita o prompt (EC-07). Os nomes vão para `custom_folders`.

## 3. Detectar conflito com estrutura já em disco (RF-11)

Antes de persistir a decisão, verifique se existe estrutura de specs já materializada em `<output_folder>/` (definido em `state.json`).

Se a pasta de saída tem subpastas que correspondem a uma granularidade diferente da escolhida agora (por exemplo, escolhida `endpoint` mas o disco tem pastas que parecem `module`), exiba aviso comparando as duas estruturas e peça confirmação:

> "Detectei que já existem specs geradas com a estrutura **[antiga]** em `<output_folder>/`. Você escolheu agora **[nova]**, que difere da anterior.
>
> Vou criar a nova estrutura em paralelo, sem tocar na anterior. Specs existentes ficam preservadas.
>
> Confirma? (s/N)"

Aguarde resposta afirmativa explícita. Negação aborta sem persistir.

A detecção é heurística e best-effort: comparar nomes de subpastas top-level com os módulos identificados pelo Scout (`module`), com URIs/rotas (`endpoint`), com features (`feature`), etc. Quando a heurística não conseguir decidir com clareza, **não** exiba o aviso (evita falso positivo).

## 4. Persistir a decisão (RNF-03, atomic write)

Atualize `.reversa/config.toml`, seção `[specs]`, com:

```toml
[specs]
layout = "feature-folder"
granularity = "<escolha do usuário>"
custom_folders = [<lista>]   # apenas quando granularity == "custom", caso contrário []
scout_suggestion = "<organization_suggestion.granularity do surface.json>"
decided_at = "<timestamp ISO 8601 UTC, exemplo 2026-05-03T14:32:00Z>"
```

Regras:

- **Atomic write:** escreva em um arquivo temporário no mesmo diretório (`config.toml.tmp`) e faça rename atômico para `config.toml`. Falha durante a escrita não pode deixar `config.toml` corrompido.
- **scout_suggestion é imutável** (RF-14): se a seção `[specs]` já existia mas estava com `granularity` vazia e `scout_suggestion` preenchida, preserve `scout_suggestion`. Em primeira execução, copie o valor atual de `organization_suggestion.granularity` do `surface.json`.
- **Non-destructive:** preserve qualquer chave/seção que você não esteja explicitamente atualizando. Não toque em `[project]`, `[user]`, `[output]`, `[agents]`, `[engines]`, `[analysis]` ou outras seções.
- **Não mexa em `.reversa/config.user.toml`.** Esse arquivo pertence ao usuário.
- **Falha de IO** (disco cheio, sem permissão, EC-06): exiba erro claro, não crie pastas de spec, não considere a escolha como confirmada. O usuário pode tentar de novo na próxima execução.

## 5. Continuação do fluxo

Após a persistência bem-sucedida, prossiga com a invocação do Archaeologist conforme o `plan.md`. A decisão fica disponível para todos os agentes que escrevem specs.

## 6. Reapresentação manual (RF-17)

Não existe flag de CLI dedicada para reconfigurar. O usuário reapresenta o menu removendo manualmente a seção `[specs]` de `.reversa/config.toml` (ou esvaziando `granularity`). Na próxima execução, este passo detecta o estado "não decidido" e roda novamente.

## Idioma das pastas (RF-10)

Os nomes que o Reversa usa para as pastas de feature seguem `doc_language` do `state.json`. Não pergunte idioma neste passo. Em uma instalação `pt-br`, as pastas saem em pt-br; em `en`, em inglês.

## Lista de checagens antes de avançar

- [ ] Ler `[specs]` de `config.toml` e mesclar com `config.user.toml` chave a chave
- [ ] Se já decidida, pular o passo
- [ ] Se há override em `config.user.toml` mas `config.toml` está vazio, exibir aviso RF-18
- [ ] Ler `organization_suggestion` de `surface.json`
- [ ] Exibir menu com sugestão pré-marcada
- [ ] Aceitar Enter, número 1 a 6, ou cancelamento
- [ ] Se opção 6, coletar `custom_folders`
- [ ] Detectar conflito com estrutura em disco e pedir confirmação
- [ ] Atomic write em `config.toml`
- [ ] Preservar `scout_suggestion` em re-execuções com seção parcial
- [ ] Prosseguir para o Archaeologist
