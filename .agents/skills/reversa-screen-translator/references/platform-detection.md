# Platform Detection

Heurísticas que o `reversa-screen-translator` usa para classificar a plataforma origem do legado a partir do conteúdo de `_reversa_sdd/inventory.md` e do código fonte. Use junto com `references/adapter-pairs.md` para escolher o adapter.

A escala de confiança aplicada por classificação:

- 🟢 **CONFIRMADO**: pelo menos uma assinatura forte (header, namespace, marcador único) está presente.
- 🟡 **INFERIDO**: extensão e padrão geral batem, mas não há assinatura única.
- 🔴 **LACUNA**: artefato de código fonte ausente; classifica só pelo `inventory.md`.
- ⚠️ **AMBÍGUO**: duas plataformas plausíveis empatadas (ex: ASP clássico vs ASP.NET WebForms em projetos antigos).

## Tabela de assinaturas

| Slug origem | Extensão típica | Assinatura forte | Assinatura fraca |
|---|---|---|---|
| `cobol-ansi-tui` | `.cob`, `.cbl`, `.cpy` | `PROCEDURE DIVISION.` + `DISPLAY`/`ACCEPT` + sequências `\x1B[`, box-drawing Unicode (`╔ ╗ ┌ ┐`) | só `PROCEDURE DIVISION` (sem ANSI = COBOL batch) |
| `cobol-screen-section` | `.cob`, `.cbl` | `SCREEN SECTION` + atributos `LINE`, `COLUMN`, `FOREGROUND-COLOR` | `SCREEN SECTION` sem detalhes |
| `ncurses-c` | `.c`, `.h` | `#include <ncurses.h>` ou `<curses.h>` + `WINDOW *`, `wprintw`, `mvwaddstr` | `printf` + `\033[` (TUI artesanal) |
| `delphi-vcl` | `.pas`, `.dfm`, `.dpr` | `unit `, `interface`, `TForm`, `TPanel`, `TButton` em `.dfm` | `.pas` puro sem `.dfm` (provável CLI) |
| `delphi-firemonkey` | `.pas`, `.fmx` | `TForm` em arquivo `.fmx` (FireMonkey) | só `.pas` |
| `vb6` | `.frm`, `.bas`, `.cls`, `.vbp` | `VERSION 5.00` no header, `Begin VB.Form`, `Begin VB.CommandButton` | `.bas` puro (módulo sem UI) |
| `vbnet-winforms` | `.vb` + `Designer.vb` | `Inherits System.Windows.Forms.Form` | só `Module ... Sub Main` (CLI) |
| `csharp-winforms` | `.cs`, `.designer.cs` | `using System.Windows.Forms;` + `partial class ... : Form` | só `using System;` |
| `csharp-wpf` | `.xaml`, `.cs` | `xmlns="http://schemas.microsoft.com/winfx/..."` + `<Window>`, `<Grid>` | só `.cs` sem `.xaml` |
| `win32-mfc` | `.cpp`, `.h`, `.rc` | `BEGIN_MESSAGE_MAP`, `CDialog`, `WinMain`, `IDD_*` em `.rc` | `WinMain` solto |
| `win32-raw` | `.cpp`, `.h` | `WinMain` + `RegisterClass`, `CreateWindow`, `WM_*` mensagens | só `WinMain` |
| `asp-classic` | `.asp`, `.inc` | `<%@ Language=VBScript %>` ou `<%@ Language=JScript %>` + `Response.Write` | `.asp` sem `<%@` |
| `aspnet-webforms` | `.aspx`, `.aspx.cs`, `.aspx.vb` | `<%@ Page Language="C#"`, `runat="server"`, `<asp:` controls | só `.aspx` simples |
| `jsp` | `.jsp`, `.jspf` | `<%@ page language="java" %>`, `<jsp:`, `<%! %>` | `.jsp` com só HTML |
| `php-server-rendered` | `.php` | `<?php ... ?>` + HTML inline + `mysql_*` ou `mysqli_*` | só `.php` em pasta `api/` (provavelmente API REST, não UI) |
| `html-legacy-jquery` | `.html`, `.htm`, `.js` | `jQuery`/`$.ajax` + form submits server-side, sem framework SPA | HTML estático (sem JS dinâmico) |
| `android-xml-java` | `res/layout/*.xml`, `*.java` | `<LinearLayout>`/`<RelativeLayout>`/`<ConstraintLayout>` + `Activity extends`, `setContentView(R.layout...)` | só Java sem `res/layout/` |
| `android-xml-kotlin` | `res/layout/*.xml`, `*.kt` | mesmo acima + `Activity()` Kotlin + `setContentView(R.layout...)` | só Kotlin sem `res/layout/` |
| `android-compose` | `*.kt` | `@Composable`, `setContent { ... }` | sem `setContent` |
| `ios-xib-objc` | `.xib`, `.m`, `.h`, `.storyboard` | `UIViewController` + `*.xib` ou `*.storyboard` referenciados | só `*.m` sem XIB |
| `ios-xib-swift` | `.xib`, `.swift`, `.storyboard` | `UIViewController` Swift + XIB/Storyboard | só `*.swift` sem XIB |
| `ios-swiftui` | `*.swift` | `View` + `var body: some View`, `App` lifecycle | sem `var body` |
| `flutter` | `*.dart`, `pubspec.yaml` | `import 'package:flutter/material.dart'` + `StatelessWidget`/`StatefulWidget` | sem `material.dart` |
| `react-class` | `*.jsx`, `*.tsx` | `class ... extends React.Component` + `render()` | só `*.tsx` (provavelmente moderno) |
| `react-hooks` | `*.jsx`, `*.tsx` | `function ... ({...}) { return <...>; }` + `useState`, `useEffect` | (não é legado, é alvo) |

## Indicadores adicionais

- **Estrutura de diretórios**:
  - `forms/`, `Forms/` → Delphi, VB6, .NET WinForms.
  - `views/`, `templates/` → MVC server-side (ASP, JSP, PHP).
  - `app/src/main/res/layout/` → Android.
  - `Storyboard.storyboard` ou `*.xib` na raiz → iOS legado.
  - `Pages/` em projeto Razor → ASP.NET.
- **Build files**:
  - `*.dpr` (Delphi), `*.vbp` (VB6), `*.csproj` (.NET), `pom.xml`/`build.gradle` (Java/Android), `Podfile` (iOS), `pubspec.yaml` (Flutter).
- **Strings de versão em comentários ou headers**: VB6 marca `VERSION 5.00`; Delphi 7 marca `{$OBJECT}`; .NET com `<TargetFramework>net48</TargetFramework>` indica WinForms legado.

## Quando duas plataformas empatam

- **ASP clássico vs ASP.NET WebForms**: arquivos `.asp` sem `.aspx` → clássico. `.aspx` + `.asp` no mesmo projeto → projeto migrando, marcar ⚠️ AMBÍGUO e perguntar.
- **VB6 vs VB.NET**: `.frm` + `.vbp` → VB6. `.vb` + `.designer.vb` + `.vbproj` → VB.NET WinForms.
- **Delphi VCL vs FireMonkey**: `.dfm` → VCL. `.fmx` → FireMonkey. Ambos no projeto → marcar ⚠️ AMBÍGUO.
- **Android Java vs Kotlin**: `.java` + `.kt` no mesmo projeto → projeto em migração; classificar por arquivo individual.
- **iOS Storyboard vs XIB**: ambos suportados; tratar como uma classe (`ios-xib-*`). Diferença vai no detalhe de captura.

## Quando nada bate

Registre `EC-01` (plataforma origem desconhecida) e ofereça ao usuário um template "raw" onde ele descreve a tela em prosa estruturada, com seções obrigatórias:

- Identidade.
- Layout em ASCII art ou screenshot.
- Lista de campos / componentes.
- Mensagens / labels literais.
- Eventos e transições.
- Validações.

O agente então gera `target_screens.md` com `spec.kind: raw-prose` e marca em `screen_deviation_log.md` que a tela não passou pelo adapter.
