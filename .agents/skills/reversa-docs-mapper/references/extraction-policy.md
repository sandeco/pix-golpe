# Política de extração de dados (Mapper)

Define quando invocar scripts de extração vs reusar cache em `_reversa_docs/assets/data/`.

## Cache hit (reutilizar)

Use o JSON existente quando **todas** as condições forem verdadeiras:

1. O arquivo existe em `_reversa_docs/assets/data/<nome>.json`.
2. `mtime` do JSON é maior que o `mtime` máximo entre todos os arquivos fonte relevantes:
   - Para `modules.json`: maior `mtime` dentro do código fonte (excluindo `.reversa/`, `_reversa_sdd/`, `node_modules/`, `.git/`).
   - Para `deps.json`: maior `mtime` do código fonte E do `modules.json`.
3. O `schemaVersion` do JSON é compatível com a versão atual (1).

## Cache miss (regenerar)

Em qualquer outro caso, invoque o script Python correspondente:

```bash
python templates/documentation/scripts/extract_modules.py \
    --root . \
    --out _reversa_docs/assets/data/modules.json

python templates/documentation/scripts/extract_deps.py \
    --modules _reversa_docs/assets/data/modules.json \
    --out _reversa_docs/assets/data/deps.json
```

## Python indisponível

Faça extração inline na engine de IA:

1. Use Glob para listar arquivos por extensão (`*.py`, `*.js`, `*.ts`, `*.go`, `*.java`).
2. Use Read para contar linhas não-vazias de cada arquivo.
3. Monte estrutura idêntica ao schema `modules.json` (ver `specs/reversa-docs/design.md`).
4. Para `deps.json`, na falta de parser AST, comece com `nodes` populado e `edges: []`. Marque em `.config.json.pagesPlanned` que dependencies não foram extraídas.

## Forçar regeneração

Se o usuário passar `--force-extract` ao `/reversa-docs-mapper`, ignore o cache e regenere. Backup do JSON anterior em `.backup-<timestamp>/assets/data/`.

## Quando o Analyst invoca isolado

Se o `Analyst` rodar antes do Mapper ou em modo isolado e não encontrar `modules.json`/`deps.json`, ele deve invocar os **mesmos scripts** seguindo esta mesma política. O resultado é compartilhado: Mapper subsequente vai usar o cache.
