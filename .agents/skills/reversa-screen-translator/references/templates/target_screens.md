---
schemaVersion: 1
generatedAt: <ISO-8601>
reversa:
  version: "x.y.z"
kind: target_screens
producedBy: screen-translator
mode: literal | modernized | hybrid
sourcePlatform: <slug>
targetPlatform: <slug>
adapter: <adapters/origem__alvo>
screenCount: <int>
hash: "sha256:<hash do corpo abaixo do front-matter>"
---

# Target Screens

> Especificação executável de cada tela do sistema novo, derivada do legado segundo o modo aprovado em `screen_modernization_decision.md`. Conteúdo textual preservado literalmente, salvo aprovação explícita de revisão linguística.
> Leitura primária para o codificador. Cada seção é um contrato.

## Resumo

- **Modo aplicado**: <literal | modernizado | híbrido>
- **Telas geradas**: <N>
- **Adapter**: <slug>
- **Tokens consumidos**: ver `_reversa_sdd/design-system/tokens.md` e `tokens-derived.md` quando aplicável
- **Golden files**: <N> em `_reversa_sdd/screens/golden/` (manifest em `golden/manifest.yaml`)
- **Deviations registradas**: <N> em `screen_deviation_log.md`

> Caso o legado não possua UI (sistema batch / API / daemon), substituir esta seção por:
> "Nenhuma tela detectada. Agente pulado em modo `skipped`. Próximo agente: Inspector."

---

## Tela: <nome-canonical>

**Origem**: `<arquivo-legado>:<linha-ou-paragrafo>`
**Modo aplicado**: literal | modernizado
**Componentes do design-system**: [<token1>, <token2>, ...]
**Pontos de interpolação**: `{{var1}}`, `{{var2}}`
**Transições de saída**: [<próxima tela ou evento>]
**Tela crítica?**: sim | não (consulta `reversa-detective` quando disponível)

### Especificação

> O bloco abaixo varia conforme o par origem→alvo e o modo. Veja `references/adapter-pairs.md` para o formato canônico de cada par. Exemplos abaixo.

#### Exemplo: COBOL TUI → Go CLI/TUI (literal)

```yaml
spec.kind: ansi-byte-stream
spec.normalize:
  - trim_trailing_spaces: false
  - line_endings: "\n"
spec.lines:
  - bytes: "\x1b[96m╔══════════════════════════════════════════════════╗\x1b[0m\n"
  - bytes: "\x1b[96m║                \x1b[93m▓▓▓  BANCO ATM  ▓▓▓\x1b[96m               ║\x1b[0m\n"
  - bytes: "\x1b[96m║                  \x1b[97m{{header_subtitle}}\x1b[96m                ║\x1b[0m\n"
    interpolations:
      header_subtitle:
        type: string
        max_width: 16
        source: literal "Caixa Eletronico" | literal "Acesso ao Sistema"
  - bytes: "\x1b[96m╚══════════════════════════════════════════════════╝\x1b[0m\n"
spec.input_prompts:
  - kind: accept-line
    prompt_bytes: "   \x1b[96m>>\x1b[97m Selecione uma opcao: \x1b[0m"
    captures: opcao
    valid: ["0", "1", "2", "3", "4", "5"]
```

#### Exemplo: Win32/Delphi VCL → Web SPA (modernizado)

```yaml
spec.kind: component-tree
spec.states: [idle, loading, error, success]
spec.root:
  component: PageLayout
  variant: form
  children:
    - component: Header
      tokens: [color.brand-primary, typography.h1]
      content:
        text: "Cadastro de Cliente"
    - component: Form
      submit_event: cliente.create
      children:
        - component: FormField
          name: nome
          label: "Nome completo"
          legacy_origin: "TForm1.edtNome"
          validation:
            required: true
            max_length: 80
        - component: FormField
          name: cpf
          label: "CPF"
          legacy_origin: "TForm1.mskCPF"
          mask: "999.999.999-99"
          validation:
            required: true
            cpf: true
    - component: ButtonRow
      children:
        - component: Button
          variant: primary
          label: "Salvar"
          legacy_origin: "TForm1.btnSalvar"
          action: form.submit
        - component: Button
          variant: ghost
          label: "Cancelar"
          legacy_origin: "TForm1.btnCancelar"
          action: navigate.back
spec.state_messages:
  loading: "Salvando..."
  error: "{{error_message}}"
  success: "Cliente cadastrado com sucesso."
```

#### Exemplo: HTML legado server-rendered → SPA componentizada (modernizado)

```yaml
spec.kind: route-component
spec.route: /clientes/novo
spec.layout: AppLayout
spec.states: [idle, loading, error, success]
spec.component:
  component: ClientesNovoPage
  legacy_origin: "/admin/cliente_novo.asp"
  state:
    cliente:
      type: Cliente
      initial: empty
  children:
    - component: PageTitle
      content: "Novo Cliente"
    - component: ClienteForm
      props:
        onSubmit: clienteService.create
        initial: $state.cliente
spec.api_changes:
  - legacy: POST /admin/cliente_novo.asp (form-urlencoded)
    target: POST /api/clientes (application/json)
    deviation: DEV-014
```

#### Exemplo: Android XML → Flutter (modernizado)

```yaml
spec.kind: composable
spec.name: ClienteListScreen
spec.legacy_origin: "app/src/main/res/layout/activity_cliente_list.xml + ClienteListActivity.java"
spec.states: [idle, loading, error, success]
spec.composable: |
  Scaffold(
    appBar: AppBar(title: Text("Clientes")),
    body: Consumer<ClienteListVM>(
      builder: (ctx, vm, _) => vm.loading
        ? CircularProgressIndicator()
        : ListView.builder(
            itemCount: vm.clientes.length,
            itemBuilder: (_, i) => ClienteListTile(cliente: vm.clientes[i]),
          ),
    ),
    floatingActionButton: FloatingActionButton(
      onPressed: () => Navigator.pushNamed(ctx, '/clientes/novo'),
      child: Icon(Icons.add),
    ),
  )
spec.viewmodel:
  name: ClienteListVM
  legacy_origin: "ClienteListActivity.onResume"
  methods:
    - load(): chama clienteService.listar
```

### Pontos de divergência aceitos

- DEV-XXX: <descrição curta> (ver `screen_deviation_log.md#DEV-XXX`)

### Estados (apenas modo modernizado)

| Estado | Descrição | Conteúdo / mensagem |
|---|---|---|
| Idle | Estado padrão antes de qualquer ação | <conteúdo> |
| Loading | Operação assíncrona em curso | <spinner / skeleton> |
| Error | Falha na operação ou dado inválido | `{{error_message}}` |
| Success | Operação concluída com sucesso | <mensagem confirmação> |

> Em modo literal, esta seção pode ser omitida ou substituída por "preserva os estados do legado" se o legado não tiver disposição explícita de estados.

---

## Tela: <segunda-tela>

(repetir o bloco acima para cada tela)

---

## Apêndice: rastreabilidade ao inventário

| Tela do `target_screens.md` | Origem em `_reversa_sdd/ui/inventory.md` | Origem em `_reversa_sdd/screens/inventory.json` |
|---|---|---|
| <tela 1> | <linha do inventário> | <id do inventário interno> |
| <tela 2> | <linha do inventário> | <id do inventário interno> |
