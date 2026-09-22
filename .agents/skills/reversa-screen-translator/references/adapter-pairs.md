# Adapter Pairs

Mapa de pares origem→alvo suportados em v1, com modo recomendado por padrão e o formato canônico de spec a usar em `target_screens.md`. Pares não listados retornam `EC-01` e oferecem template raw.

## Tabela mestre

| Origem | Alvo | Modo recomendado | Adapter | Formato de spec |
|---|---|---|---|---|
| `cobol-ansi-tui` | `go-cli` | literal | `cobol_ansi__go_cli` | `ansi-byte-stream` |
| `cobol-ansi-tui` | `rust-cli` | literal | `cobol_ansi__rust_cli` | `ansi-byte-stream` |
| `cobol-ansi-tui` | `web-spa` | modernizado | `cobol_ansi__web_spa` | `component-tree` |
| `cobol-screen-section` | `go-cli` | literal | `cobol_screen__go_cli` | `ansi-byte-stream` |
| `ncurses-c` | `go-cli` | literal | `ncurses__go_cli` | `ansi-byte-stream` |
| `ncurses-c` | `rust-cli` | literal | `ncurses__rust_cli` | `ansi-byte-stream` |
| `delphi-vcl` | `web-spa` | modernizado | `delphi_vcl__web_spa` | `component-tree` |
| `delphi-vcl` | `tauri` | modernizado (com opção literal-ish) | `delphi_vcl__tauri` | `component-tree` |
| `delphi-vcl` | `electron` | modernizado | `delphi_vcl__electron` | `component-tree` |
| `delphi-firemonkey` | `flutter` | modernizado | `delphi_firemonkey__flutter` | `composable` |
| `vb6` | `web-spa` | modernizado | `vb6__web_spa` | `component-tree` |
| `vb6` | `tauri` | modernizado | `vb6__tauri` | `component-tree` |
| `vbnet-winforms` | `web-spa` | modernizado | `vbnet_winforms__web_spa` | `component-tree` |
| `csharp-winforms` | `web-spa` | modernizado | `csharp_winforms__web_spa` | `component-tree` |
| `csharp-wpf` | `web-spa` | modernizado | `csharp_wpf__web_spa` | `component-tree` |
| `win32-mfc` | `web-spa` | modernizado | `win32_mfc__web_spa` | `component-tree` |
| `win32-raw` | `web-spa` | modernizado | `win32_raw__web_spa` | `component-tree` |
| `asp-classic` | `web-spa` (React/Vue/Svelte) | modernizado | `asp_classic__spa` | `route-component` |
| `aspnet-webforms` | `web-spa` | modernizado | `aspnet_webforms__spa` | `route-component` |
| `jsp` | `web-spa` | modernizado | `jsp__spa` | `route-component` |
| `php-server-rendered` | `web-spa` | modernizado | `php__spa` | `route-component` |
| `html-legacy-jquery` | `web-spa` | modernizado | `html_legacy__spa` | `route-component` |
| `android-xml-java` | `flutter` | modernizado | `android_xml__flutter` | `composable` |
| `android-xml-java` | `compose` | modernizado (idioma próximo) | `android_xml__compose` | `composable` |
| `android-xml-kotlin` | `compose` | modernizado (idioma próximo) | `android_xml_kt__compose` | `composable` |
| `ios-xib-objc` | `flutter` | modernizado | `ios_xib_objc__flutter` | `composable` |
| `ios-xib-objc` | `swiftui` | modernizado (idioma próximo) | `ios_xib_objc__swiftui` | `composable` |
| `ios-xib-swift` | `swiftui` | modernizado (idioma próximo) | `ios_xib_swift__swiftui` | `composable` |

## Modos disponíveis por par

Para cada par, em geral três modos são apresentados ao usuário, mas alguns combinações têm modo literal **inviável**. A tabela abaixo restringe.

| Par | literal viável? | Por quê |
|---|---|---|
| `cobol-ansi-tui` → `go-cli` | sim | terminais textuais respeitam ANSI byte-a-byte |
| `cobol-ansi-tui` → `web-spa` | não | terminal não tem equivalente literal em DOM; recusa modo literal |
| `delphi-vcl` → `web-spa` | parcial | só com screenshot do legado e aceite explícito; pixel-perfect raro |
| `win32-mfc` → `web-spa` | não | recusa modo literal; recomenda modernizado |
| `android-xml-*` → `flutter` | parcial | só com screenshots por densidade; pixel-perfect dependente de fonte |
| `android-xml-*` → `compose` | parcial | mesmo idioma, mais próximo, mas widgets divergem |
| `ios-xib-*` → `swiftui` | parcial | mesma plataforma, mas constraints e auto-layout divergem |

Quando `literal` não é viável, o agente apresenta apenas modernizado e híbrido como opções, e explica ao usuário por quê literal foi descartado.

## Formato de spec por kind

### `ansi-byte-stream` (terminais textuais)

Cada linha como bloco `bytes` contendo a sequência literal, incluindo escapes ANSI. Usar `\x1b[...m` para cores. Interpolações declaradas com `interpolations.<nome>` por linha. Inputs do usuário via `spec.input_prompts`.

Implementação alvo típica: uma função por tela em `pkg/menu/screens.<ext>` que escreve em `io.Writer`.

### `component-tree` (desktop/web/mobile gráfico, modo modernizado)

Hierarquia de componentes nominais (`PageLayout`, `Form`, `FormField`, `Button`, ...). Tokens referenciados em `tokens: [...]`. Eventos em `submit_event`, `action`. Estados em `spec.states: [idle, loading, error, success]`. Mensagens por estado em `spec.state_messages`.

Implementação alvo: framework livre (React, Vue, Svelte, SwiftUI, Compose, Tauri webview, etc.) salvo se `target_architecture.md` já fixou um framework específico.

### `route-component` (web modernizado a partir de server-rendered)

Inclui `spec.route` (URL canônica do alvo) e `spec.layout` (layout pai). Body é um `component-tree`. `spec.api_changes` lista mudanças de contrato HTTP entre legado e alvo (URL, método, content-type), referenciando deviations.

### `composable` (mobile cross-platform)

Bloco `spec.composable` com pseudo-código declarativo no idioma do alvo (Flutter Dart, Compose Kotlin, SwiftUI Swift). Inclui `spec.viewmodel` quando o alvo separa view e estado.

### `raw-prose` (fallback EC-01)

Quando o adapter não cobre o par. Conteúdo é prosa estruturada com seções obrigatórias (identidade, layout, campos, mensagens, eventos, validações). Cada tela em `raw-prose` deve ter deviation registrada apontando que o codificador precisará interpretar a prosa.

## Entradas e estados especiais

Toda spec, em qualquer kind, pode incluir:

- `spec.normalize`: regras aceitas em comparação com golden file (line endings, trailing spaces, trim ANSI, etc.).
- `spec.interpolations`: pontos onde dados dinâmicos do domínio entram (ex: `{{titular}}`, `{{saldo}}`). Com tipos e restrições (max_width, regex, lookup).
- `spec.transitions`: lista de eventos que levam a outra tela.
- `spec.legacy_origin`: caminho `arquivo:linha` ou `arquivo:paragrafo` no legado.
- `spec.deviations`: ids `DEV-XXX` que afetam a tela.

## Pares não cobertos em v1

- Plataformas com renderização customizada (Canvas HTML5, OpenGL, jogos): retornam `EC-01`.
- 3D, AR/VR: fora do escopo (NG-07).
- Voz / conversacional: fora do escopo.
- Plugins descontinuados embedded (Crystal Reports, Flash, ActiveX): tratamento em v2 (OQ-03).

Pares novos podem ser adicionados como linhas nesta tabela, junto com um adapter descritivo (não código, é heurística textual usada pelo agente para gerar a spec).
