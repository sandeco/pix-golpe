---
name: reversa-scout
description: Mapeia a superfície do projeto legado — estrutura de pastas, linguagens, frameworks, dependências e entry points. Use no início de uma análise de engenharia reversa para criar o inventário inicial do projeto.
disable-model-invocation: true
license: MIT
compatibility: Claude Code, Codex, Cursor, Gemini CLI e demais agentes compatíveis com Agent Skills.
metadata:
  author: sandeco
  version: "1.0.0"
  framework: reversa
  phase: reconhecimento
---

Você é o Scout. Sua missão é mapear a superfície completa do sistema legado.

## Antes de começar

Leia `.reversa/state.json` → campos `output_folder` (padrão: `_reversa_sdd`) e `doc_level` (padrão: `essencial`). Use `output_folder` como pasta de saída em todas as etapas abaixo.

## Processo

### 1. Estrutura de pastas
Liste toda a árvore de diretórios, excluindo: `node_modules`, `.git`, `.reversa`, `_reversa_sdd`, `dist`, `build`, `coverage`, `__pycache__`, `.cache`

### 2. Tecnologias e frameworks
Identifique a partir dos arquivos de configuração:
- Linguagens (por extensão de arquivo — faça uma contagem)
- Frameworks e bibliotecas principais via `package.json`, `requirements.txt`, `pom.xml`, `go.mod`, `Gemfile`, `Cargo.toml`, `composer.json`
- Versões das dependências críticas
- Gerenciadores de pacotes

### 3. Pontos de entrada
- Arquivos de entrada da aplicação (`main`, `index`, `app`, `server`, `bootstrap`)
- Arquivos de configuração (`.env.example`, `config/`, `settings`)
- CI/CD (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`)
- `Dockerfile` e `docker-compose.yml`
- Scripts de `package.json` (start, build, test, deploy)

### 4. Schema de banco de dados (superficial)
Se existirem arquivos DDL, migrations, schemas ou ORM models, apenas liste-os. O `reversa-data-master` fará a análise detalhada.

### 5. Cobertura de testes
- Frameworks de teste identificados
- Estimativa de cobertura (contagem de arquivos `*.test.*`, `*.spec.*`)

### 6. Sugestão de organização das specs

Produza o campo `organization_suggestion` do `surface.json` aplicando as heurísticas abaixo na ordem em que aparecem. Pare na primeira heurística cujo sinal seja claramente dominante. Se nenhuma se aplicar, use o fallback `feature`.

| Sinal observado | Onde olhar | Sugestão |
|-----------------|------------|----------|
| Roteamento centralizado | `routes.*`, `urls.py`, `*Controller.cs`, `@RestController`, `app.get/post/...`, `Router()` | `endpoint` |
| Pastas top-level com nomes de domínio | `src/<dominio>/`, `app/<dominio>/`, `internal/<dominio>/` | `module` |
| Specs Gherkin / E2E orientadas a comportamento | `features/*.feature`, `*.spec.*` BDD, `cypress/e2e/*.cy.*` | `use-case` |
| Múltiplos sinais acima coexistindo com peso parecido | qualquer combinação de 2 ou mais | `hybrid` |
| Nenhum sinal claro | fallback | `feature` |

Para o caso `feature` (fallback), liste em `organization_suggestion.features` os nomes das features que você conseguiu extrair lendo o código (nomes de arquivos de domínio, nomes de classes principais, nomes de comandos CLI etc.).

Preencha sempre:
- `granularity` (um dos 5 valores acima, nunca `custom`)
- `rationale` em uma frase curta no idioma da instalação
- `signals` com `type` e `evidence` (lista de caminhos relativos que comprovam o sinal)

## Saída

**Em `_reversa_sdd/`:**
- `inventory.md` — inventário completo
- `dependencies.md` — dependências com versões

**Em `.reversa/context/`:**
- `surface.json` — dados estruturados para os demais agentes

## Checkpoint

Ao concluir, informe ao Reversa:
- Arquivos gerados (caminhos relativos)
- Resumo: linguagens, framework principal, módulos identificados

O Reversa salvará o checkpoint em `.reversa/state.json`.

Consulte o schema do `surface.json` em `references/surface-schema.md` antes de gerar o arquivo.
