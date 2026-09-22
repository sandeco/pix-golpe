# Schema — .reversa/context/modules.json

Arquivo gerado pelo Arqueólogo. Usado pelo Detetive, Arquiteto e Redator.

## Estrutura completa

```json
{
  "generated_at": "2026-04-26T11:00:00Z",
  "modules": [
    {
      "name": "auth",
      "path": "src/modules/auth",
      "purpose": "Autenticação e autorização de usuários",
      "primary_files": [
        "src/modules/auth/auth.service.ts",
        "src/modules/auth/auth.controller.ts"
      ],
      "functions": [
        {
          "name": "login",
          "file": "src/modules/auth/auth.service.ts",
          "params": ["email: string", "password: string"],
          "returns": "Promise<AuthToken>",
          "confidence": "confirmed"
        }
      ],
      "entities": [
        {
          "name": "User",
          "fields": [
            { "name": "id", "type": "string", "required": true },
            { "name": "email", "type": "string", "required": true },
            { "name": "password_hash", "type": "string", "required": true },
            { "name": "role", "type": "UserRole", "required": true }
          ],
          "confidence": "confirmed"
        }
      ],
      "business_rules": [
        {
          "description": "Senha deve ter mínimo 8 caracteres",
          "location": "src/modules/auth/auth.service.ts:45",
          "confidence": "confirmed"
        }
      ],
      "dependencies": ["users", "notifications"],
      "algorithms": [],
      "complexity": "medium"
    }
  ]
}
```

## Níveis de confiança

| Valor | Equivalente | Significado |
|-------|-------------|-------------|
| `"confirmed"` | 🟢 | Extraído diretamente do código |
| `"inferred"` | 🟡 | Baseado em padrões |
| `"unknown"` | 🔴 | Não determinável |

## Campos obrigatórios por módulo

`name`, `path`, `purpose`, `primary_files`

## Nota

Salve o checkpoint em `.reversa/state.json` após cada módulo analisado, antes de iniciar o próximo.
