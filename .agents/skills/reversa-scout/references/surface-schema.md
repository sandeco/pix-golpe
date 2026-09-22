# Schema — .reversa/context/surface.json

Arquivo gerado pelo Scout. Usado pelos demais agentes como fonte de contexto estruturado.

## Estrutura completa

```json
{
  "generated_at": "2026-04-26T10:00:00Z",
  "project_root": "/caminho/do/projeto",
  "languages": [
    { "name": "TypeScript", "extensions": [".ts", ".tsx"], "file_count": 142 },
    { "name": "JavaScript", "extensions": [".js", ".mjs"], "file_count": 23 }
  ],
  "primary_language": "TypeScript",
  "frameworks": [
    { "name": "Next.js", "version": "14.2.0", "source": "package.json" },
    { "name": "Prisma", "version": "5.10.0", "source": "package.json" }
  ],
  "package_manager": "npm",
  "entry_points": [
    { "path": "src/app/layout.tsx", "type": "app_entry" },
    { "path": "src/server.ts", "type": "server_entry" }
  ],
  "config_files": [
    "next.config.js", ".env.example", "tsconfig.json"
  ],
  "ci_cd": [
    ".github/workflows/deploy.yml"
  ],
  "docker": {
    "dockerfile": "Dockerfile",
    "compose": "docker-compose.yml"
  },
  "database_hints": [
    { "path": "prisma/schema.prisma", "type": "prisma_schema" },
    { "path": "prisma/migrations/", "type": "migrations_dir" }
  ],
  "test_framework": "Jest",
  "test_file_count": 47,
  "modules": [
    "auth", "orders", "payments", "users", "notifications"
  ],
  "total_files": 312,
  "organization_suggestion": {
    "granularity": "module",
    "rationale": "A estrutura de pastas top-level está organizada por domínio: auth/, orders/, payments/, users/, notifications/.",
    "signals": [
      { "type": "top_level_domain_folders", "evidence": ["src/auth/", "src/orders/", "src/payments/"] }
    ],
    "features": []
  }
}
```

## Campos obrigatórios

`generated_at`, `languages`, `primary_language`, `frameworks`, `entry_points`, `modules`, `organization_suggestion`

## Campos opcionais

Todos os demais, inclua apenas o que for encontrado.

## Campo `organization_suggestion`

Sugestão de como organizar as specs deste projeto. Lido pelo orquestrador Reversa para pré-marcar a opção default no menu de organização das specs.

### Subcampos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `granularity` | string | sim | Um de: `module`, `use-case`, `endpoint`, `hybrid`, `feature`, `custom`. O Scout nunca sugere `custom`, esse valor só vem da escolha do usuário. |
| `rationale` | string | sim | Frase curta explicando por que essa granularidade foi escolhida. Aparece no menu como "Razão:" do Scout. |
| `signals` | array | sim | Lista dos sinais detectados que levaram à sugestão. Cada item tem `type` e `evidence` (lista de caminhos). Pode ser vazia quando o fallback `feature` é usado. |
| `features` | array | sim quando `granularity = "feature"` | Lista de nomes de features descobertas pelo Scout. Cada nome vira uma pasta de primeiro nível. |

### Heurísticas para definir `granularity`

| Sinal detectado | `granularity` sugerida |
|-----------------|------------------------|
| Roteamento centralizado (`routes.*`, `urls.py`, `*Controller.cs`, `@RestController`) | `endpoint` |
| Pastas top-level com nomes de domínio (`auth/`, `orders/`, `payments/`) | `module` |
| Specs Gherkin / E2E orientadas a comportamento (`features/*.feature`, `*.spec.*` BDD) | `use-case` |
| Múltiplos sinais coexistindo com peso parecido | `hybrid` |
| Nenhum sinal claro de organização | `feature` (fallback, preencher `features` com o que foi possível extrair) |

### Imutabilidade

Após a primeira execução, o orquestrador persiste o `granularity` sugerido em `.reversa/config.toml` no campo `scout_suggestion`. Em re-execuções, o Scout pode regerar o `surface.json` (o legado pode ter mudado), mas o orquestrador NÃO atualiza o `scout_suggestion` em `config.toml` (RF-14 da spec de organização das specs).

## Nota

Use este schema como guia. Se um campo não se aplicar ao projeto, omita-o, exceto os obrigatórios listados acima.
