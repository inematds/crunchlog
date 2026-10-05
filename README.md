# CrunchLog: guia completo de uso (Windows, macOS e Linux)

[![CrunchLog: reuniões locais](guia/assets/banner.jpg)](https://inematds.github.io/crunchlog/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/crunchlog/guia/**

**CrunchLog** grava reuniões e gera notas em Markdown **sem sair da sua máquina**. Você aperta uma tecla quando a call começa e de novo quando termina. Alguns segundos depois cai uma nota com cada fala marcada por pessoa ("Me" é você, "Speaker 2", "Speaker 3"... são os outros). Não entra bot na call, não precisa de conta nem de chave de API.

- Autor: **Christian Landsteiner**. Versão testada aqui: **2.0.0a1** (build `1daf268`, 04/10/2026).
- Origem: post na comunidade *AI Automations by Jack* (Skool), [CrunchLog: live meeting co-pilot + fully local private mode for Claude Code, Codex and Agentic OS](https://www.skool.com/aiautomationsbyjack/crunchlog-live-meeting-co-pilot-fully-local-private-mode-for-claude-code-codex-and-agentic-os-windows-mac?p=e0359d6f). O zip fica anexado lá, só para membros.
- A integração com o **Claude OS** é de **Jack Roberts** ([aula do Agentic OS](https://www.skool.com/aiautomationsbyjack/classroom/af686ad3?md=16da0f0bc87b4d399eadd0b1e69aabc5), só para membros). A licença do CrunchLog exige manter esse crédito.

> **Este repositório não contém o CrunchLog.** A licença é de avaliação e proíbe redistribuir o software (veja [Licença](#licença)). Aqui estão só este guia, escrito por nós, e os scripts próprios para Linux em [`linux/`](linux/). Para usar, baixe o zip no post do Skool.

---

## Sumário

1. [O que ele faz](#1-o-que-ele-faz)
2. [Como funciona por dentro](#2-como-funciona-por-dentro)
3. [Requisitos](#3-requisitos)
4. [Instalar no Windows ou macOS](#4-instalar-no-windows-ou-macos)
5. [Instalar no Linux (testado)](#5-instalar-no-linux-testado)
6. [Primeira nota: o demo](#6-primeira-nota-o-demo)
7. [Gravar uma reunião de verdade](#7-gravar-uma-reunião-de-verdade)
8. [Como fica a nota](#8-como-fica-a-nota)
9. [Resumo e perguntas com Claude ou Codex](#9-resumo-e-perguntas-com-claude-ou-codex)
10. [Dashboard no navegador](#10-dashboard-no-navegador)
11. [Cola antes da reunião (`prep`)](#11-cola-antes-da-reunião-prep)
12. [MCP: perguntar das reuniões dentro do Claude Code](#12-mcp-perguntar-das-reuniões-dentro-do-claude-code)
13. [Claude OS / Agentic OS](#13-claude-os--agentic-os)
14. [Modo Live (alpha)](#14-modo-live-alpha)
15. [Todos os comandos](#15-todos-os-comandos)
16. [Configuração](#16-configuração)
17. [Privacidade: o que sai da máquina](#17-privacidade-o-que-sai-da-máquina)
18. [Problemas e soluções](#18-problemas-e-soluções)
19. [Atualizar e desinstalar](#19-atualizar-e-desinstalar)
20. [Licença](#licença)

---

## 1. O que ele faz

| Recurso | Como é | Estado |
|---|---|---|
| **Duas faixas sem driver** | Grava o que sai da caixa de som (o "far": Zoom, Meet, YouTube) separado do microfone (o "mic"). Assim ele sabe quais palavras são suas. Não precisa de VoiceMeeter nem BlackHole. | estável |
| **Uma tecla** | `crunchlog toggle` liga e desliga. Dá pra ligar num atalho, no Stream Deck ou no dashboard. | estável |
| **Nota em Markdown** | Na pasta de notas (funciona bem com Obsidian), com cada fala marcada e tempo `[mm:ss]`. | estável |
| **Transcrição local** | Parakeet TDT 0.6B v2 (NVIDIA, int8, ONNX) na CPU. Medido aqui: **27,6× o tempo real** (1 h de call em ~2 min). | estável |
| **Separação de falantes** | pyannote segmentation 3.0 + TitaNet (sherpa-onnx) na faixa "far". | estável |
| **Resumo e itens de ação** | Pelo seu login do **Claude Code** ou do **Codex** (assinatura, sem API paga). | experimental |
| **Perguntar à reunião** (`ask`) | Respostas citam `[mm:ss Falante]`. | experimental |
| **Cola de reunião** (`prep`) | Junta pendências, decisões e perguntas abertas das últimas notas de um cliente. Sem modelo. | experimental |
| **Servidor MCP** | Claude Code / Codex / Claude Desktop leem e buscam suas reuniões e iniciam gravações. | experimental |
| **Dashboard** | Gravador, forma de onda, transcrição clicável, renomear falantes, prompts, configurações, doctor. | experimental |
| **Live co-pilot** | Transcrição ao vivo por AssemblyAI (sua conta) e resumo durante a call. **Desligado por padrão.** | alpha |

Limites desta versão: **só inglês**, a primeira configuração baixa **~700 MB** de modelos, e no macOS exige **14.2+ em Apple Silicon**. Tudo além de gravar e gerar a nota é experimental.

## 2. Como funciona por dentro

```
 tecla / dashboard / MCP
          │
          ▼
  ┌──────────────── gravação (Windows: WASAPI · macOS: CoreAudio · Linux: nosso pw-record) ───┐
  │  far.wav  ← o que você ouve        mic.wav ← o que você fala      meta.json (relógio)     │
  └──────────────────────────────── = 1 "bundle" (uma pasta por reunião) ─────────────────────┘
          │
          ▼  crunchlog process  (tudo local, CPU)
  VAD (silero) → ASR (Parakeet) por faixa → "gate" tira do mic o som que vazou da caixa
          → separação de falantes no far → falas (turns.json) → limpeza ("um", "uh", glossário)
          │
          ├──► nota Markdown na pasta de notas  (~/CrunchLog/notes/AAAA-MM-DD-HHMM-slug.md)
          └──► opcional: resumo / ask por `claude -p` ou `codex` (sua assinatura)
```

O "truque das duas faixas": como o microfone é gravado separado, tudo o que vem dele é **você** ("Me"). A separação por IA só precisa distinguir as pessoas do outro lado. Se a caixa de som vaza no microfone, o *gate* compara as faixas e descarta do mic as palavras que eram eco (no demo foram 262 de 396 palavras descartadas, que eram justamente o eco simulado).

## 3. Requisitos

| | Windows | macOS | Linux |
|---|---|---|---|
| Sistema | 10 ou 11 | 14.2+ Apple Silicon | **não suportado oficialmente**; funciona com os scripts deste repo (testado em Ubuntu aarch64 com PipeWire) |
| Gravar | WASAPI, nativo | helper `crunchlog-audio` (vem pronto no zip) | `pw-record` (PipeWire) pelo nosso `crunchlog-linux` |
| Demo com voz | System.Speech | `say` | Piper (instalado pelo nosso script) |
| Sempre | [uv](https://docs.astral.sh/uv/) (ele baixa o Python 3.12 sozinho), ~1 GB livre para modelos | | |
| Opcional | `ffmpeg` (importar mp3/mp4), Claude Code ou Codex logados (resumo/ask) | | |

Instalar o uv:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 4. Instalar no Windows ou macOS

1. Baixe `crunchlog-2.0.0a1.zip` no post do Skool e descompacte.
2. **Caminho mais fácil (o autor recomenda):** abra um terminal na pasta, rode `claude` e cole:

   ```
   I have extracted CrunchLog into this folder. Read START-HERE.md and AGENTS.md and install it for me, then run the demo so I get my first note.
   ```

   O Claude Code segue o `AGENTS.md` do zip: confere uv e Python, instala, faz quatro perguntas (pasta de notas, dispositivo "far", microfone, provedor de resumo), roda o `doctor` e termina com o `demo`.
3. **Caminho manual (quatro comandos, dentro da pasta descompactada):**

   ```bash
   uv tool install --python 3.12 ".[mcp]"
   crunchlog setup        # Enter aceita os padrões; --yes não pergunta nada
   crunchlog doctor       # exit 0 e nenhuma linha [fail] = pode gravar
   crunchlog demo         # sua primeira nota em ~1 min
   ```

- `".[mcp]"` já inclui o servidor MCP. Para o ícone na bandeja: `".[mcp,tray]"`.
- Se `crunchlog` não for encontrado: `uv tool update-shell` e abra outro terminal (ou use `uv tool run crunchlog ...`).
- **macOS:** a primeira gravação pede duas permissões para `crunchlog-audio` (não para o Terminal): **Microfone** e **Gravação de Tela e Áudio do Sistema**. Sem a segunda, a faixa far sai muda. Se o Gatekeeper bloquear o helper, rode `xattr -cr .` **só na pasta descompactada**.

## 5. Instalar no Linux (testado)

O CrunchLog 2.0.0a1 não grava no Linux (`crunchlog devices` → *no recorder backend for this platform*), mas **todo o resto roda**: transcrição, separação de falantes, nota, resumo, ask, export, prep, dashboard e MCP. Nós testamos em **Ubuntu, ARM64 (aarch64), PipeWire**, e as dependências instalaram sem nenhum patch. Para fechar as duas lacunas (gravar e demo), este repo traz [`linux/`](linux/):

| Arquivo | Para quê |
|---|---|
| `linux/recorder_linux.py` | Gravador de duas faixas com `pw-record`: monitor da saída padrão → `far.wav`, entrada padrão → `mic.wav`, `meta.json` no contrato oficial (`bundle_version: 2`). No `stop`, chama o pipeline oficial. |
| `linux/demo_linux.py` | O mesmo `crunchlog demo` (mesmo roteiro, mesma montagem, mesmo pipeline), só trocando a voz do sistema pelo **Piper**. Não altera o código do CrunchLog. |
| `linux/crunchlog-linux` | Atalho: `demo`, `start`, `stop`, `toggle`, `status`, `devices`. |
| `linux/instalar-extras-linux.sh` | Instala Piper + 3 vozes inglesas (~190 MB) e põe `crunchlog-linux` em `~/.local/bin`. |

Passo a passo (exatamente o que rodamos):

```bash
# 1. CrunchLog (dentro da pasta descompactada do zip)
uv tool install --python 3.12 ".[mcp]"
crunchlog --version          # crunchlog 2.0.0a1 (build 1daf268 of 2026-10-04)

# 2. Setup sem perguntas (no Linux não há lista de dispositivos para escolher)
crunchlog setup --yes --provider none      # baixa os ~700 MB de modelos

# 3. Extras deste repo
git clone https://github.com/inematds/crunchlog && bash crunchlog/linux/instalar-extras-linux.sh

# 4. Conferir
crunchlog doctor
```

Saída real do `doctor` no Linux: as duas linhas `[fail]` são só da gravação nativa, que o `crunchlog-linux` substitui.

```
[fail] platform: linux: CrunchLog records on Windows and macOS only
[ok  ] python: Python 3.12.3
[ok  ] sherpa-onnx: bundled onnxruntime not needed on this platform
[ok  ] config: /home/<você>/.config/crunchlog/config.toml
[fail] devices: UnsupportedPlatform: CrunchLog records on Windows and macOS; this is linux
[ok  ] models: /home/<você>/.cache/crunchlog/models
[ok  ] summary: provider none; on PATH: claude, codex
[ok  ] ffmpeg: /usr/bin/ffmpeg
[ok  ] asr speed: 27.6x realtime (a 1-hour call takes about 2 min)
[ok  ] disk: 211.9 GB free at /home/<você>/CrunchLog
Recording cannot start: fix platform, devices.
```

Escolher outras placas de som: `wpctl status` lista os dispositivos e `wpctl inspect <id> | grep node.name` mostra o nome. Depois é só usar `CRUNCHLOG_FAR_TARGET=<sink>` e `CRUNCHLOG_MIC_TARGET=<source>` antes do `crunchlog-linux start`.

## 6. Primeira nota: o demo

O demo encena uma reunião inventada com três pessoas ("Me" no microfone; Dana e Lee do outro lado), grava as duas faixas com vazamento de caixa simulado, processa tudo no pipeline real e imprime o caminho da nota. Não precisa de microfone.

```bash
crunchlog demo            # Windows / macOS
crunchlog-linux demo      # Linux
```

Saída real no Linux:

```
synthesising 33 lines
voices: Me: en_GB-alan-medium; Dana: en_US-amy-medium; Lee: en_US-ryan-medium
wrote 2026-10-05-1642-demo: 158.3 s per track
asr far: 261 words in 9.124 s
asr mic: 396 words in 11.478 s
gate: kept 134 mic words, dropped 262 (margin 3.0 dB)
diarize: 22 spans, 2 far speakers (asked for 2) in 6.218 s
turns: 33 turns, talk seconds per role {'Me': 53.8, 'Speaker 2': 55.5, 'Speaker 3': 29.0}
done in 57 s
note: /home/<você>/CrunchLog/notes/2026-10-05-1642-demo.md
```

Opções: `--no-process` (só grava o bundle), `--voices A,B,C`, `--list-voices`, `--no-bleed` (sem vazamento simulado).

## 7. Gravar uma reunião de verdade

```bash
crunchlog toggle                 # começa (Windows/macOS)
# ... reunião ...
crunchlog toggle                 # para; a nota sai em alguns segundos

crunchlog-linux toggle           # o mesmo no Linux
crunchlog start --slug acme --speakers 3   # nome na pasta + total de pessoas (incluindo você)
crunchlog status                 # idle / recording
```

**Ligar numa tecla:**
- **Windows:** PowerToys Keyboard Manager ou AutoHotkey rodando `crunchlogw toggle` (o `crunchlogw` não abre janela de console). Stream Deck: ação "System: Open" → `crunchlog.exe toggle`.
- **macOS:** atalho do app Atalhos com "Executar Script de Shell" `crunchlog toggle`, ou Raycast / Hammerspoon.
- **Linux:** atalho personalizado do GNOME/KDE apontando para `~/.local/bin/crunchlog-linux toggle`.
- **Bandeja com atalho global** (Windows/macOS): instale com `".[mcp,tray]"` e rode `crunchlog tray --hotkey ...`.

Antes da primeira call, `crunchlog check-audio --tone` grava alguns segundos e diz se as duas faixas estão ouvindo (Windows/macOS).

**Arquivos que você já tem** (mp3, m4a, mp4, wav): `crunchlog process arquivo.mp4`. Tudo entra como faixa "far", então não há "Me" e os falantes começam em Speaker 2. Uma pasta vigiada: `crunchlog watch ~/Gravador`. Testamos com o vídeo de walkthrough do autor (2:26): **nota pronta em 18 s**.

## 8. Como fica a nota

Arquivo `~/CrunchLog/notes/2026-10-05-1642-demo.md` (reunião inventada do demo):

```markdown
---
date: 2026-10-05
start: 16:42
duration: 02:38
speakers: 3
asr_model: nemo-parakeet-tdt-0.6b-v2:int8
diarization_model: sherpa-onnx:pyannote-segmentation-3.0+nemo_en_titanet_small
---

# Meeting 2026-10-05 16:42

## Summary            ← só com provedor claude/codex
## Decisions
- The beta starts on November 12 with 200 testers and opens to everyone else two weeks later.
## Action items
- [ ] Speaker 3: Fix the sync crash on older tablets ..., by next Wednesday.
- [ ] Speaker 2: Write a draft invite email for the first 200 testers ..., by Friday.
## Open questions
- Do we charge for the premium tier during the beta ...?

## Transcript
[00:00] Me: Okay, let's get started. Thanks for joining Dana and Lee. ...
[00:09] Speaker 2: Sounds good. I have the numbers from the last test round ...
[00:27] Speaker 3: Most of what is left is the same crash on older tablets. ...
```

Ao lado, na pasta da gravação (`~/CrunchLog/recordings/<nome>/`), ficam `far.wav`, `mic.wav`, `meta.json`, `words.json`, `turns.json`, `summary.md`, `pipeline.log`.

Depois de gravar:

```bash
crunchlog speakers <gravação> "Speaker 2=Dana" "Speaker 3=Lee"   # dá nomes e refaz a nota
crunchlog note "cliente quer proposta até sexta"                   # suas anotações entram no resumo
crunchlog export ~/CrunchLog/recordings/<gravação> --format srt    # srt|vtt|txt|json|csv|md
crunchlog open latest --obsidian
crunchlog rerender <gravação>                                      # refaz a nota sem transcrever de novo
```

## 9. Resumo e perguntas com Claude ou Codex

O resumo não usa API paga: o CrunchLog chama a **sua CLI logada** (`claude -p ...` ou `codex`) com ferramentas, MCP e comandos desligados, ou seja, sai da sua assinatura.

```toml
# ~/.config/crunchlog/config.toml
[summary]
provider = "claude"        # none | claude | codex | auto
claude_model = "opus"      # opus | sonnet | haiku
claude_effort = "medium"
```

Medido aqui: resumo do demo pelo Claude em **10,3 s** (1.285 caracteres: Summary, Decisions, Action items, Open questions).

```bash
crunchlog ask latest "What was decided about the beta launch date and size?"
```

Resposta real (com citações clicáveis no dashboard):

> The beta starts on **November 12 with 200 testers**, and it opens to everyone else two weeks later [01:13 Me]. ... Me thought 500 was too many with a crash the team already knew about [00:49 Me].

Modelos de resumo por tipo de reunião: `crunchlog templates list | use standup | which` (standup, sales call, interview...). Os prompts ficam editáveis na página **Prompts** do dashboard.

## 10. Dashboard no navegador

```bash
crunchlog dashboard            # http://127.0.0.1:47431/ (só local; --port muda; --no-browser não abre)
```

Na primeira visita de cada navegador, use o link com `?t=...` que ele imprime (é o login local) e depois salve o endereço simples nos favoritos.

| Página | O que tem |
|---|---|
| **Overview** | Botão Record/Stop, medidores das duas faixas, título, número de falantes, últimas gravações, disco e modelos |
| **Recordings** | Arquivo de gravações, filtros (não processadas, com problema), calendário |
| **Gravação** | Forma de onda das duas faixas, quem fala quando, player (1×–2×), transcrição clicável, renomear falantes, resumo, export, "Process again" |
| **Notes** | Todas as notas da pasta |
| **Prompts** | Modelos de resumo; qual está em uso |
| **Settings** | Pastas, dispositivos, transcrição, rótulos de falantes, limpeza, resumo (Opus médio pela assinatura), ask, live, notificações |
| **Doctor** | As mesmas checagens do `crunchlog doctor` e o botão "Update now" |

No Linux, o botão **Record** do dashboard não funciona (ele usa o gravador nativo). Grave com `crunchlog-linux`, e o dashboard mostra e toca a gravação normalmente.

![Dashboard: gravação do demo com as duas faixas](guia/assets/dash-demo.jpg)

## 11. Cola antes da reunião (`prep`)

```bash
crunchlog prep "acme"                     # junta das notas dos últimos 90 dias com "acme" no título/participantes
crunchlog prep "acme" --calendar "Qui 14h, Ana e Bruno" --dry-run
```

Gera `<notas>/AAAA-MM-DD-acme-cheatsheet.md` com itens de ação em aberto, decisões anteriores, perguntas abertas e 3 a 5 perguntas-roteiro `(qN)`. Não chama modelo nenhum. Com `[prep] enabled = true`, quando a próxima nota da Acme fica pronta, ele **marca sozinho** as perguntas que foram respondidas. Links por cliente ficam em `~/.config/crunchlog/links/acme.md`.

## 12. MCP: perguntar das reuniões dentro do Claude Code

```bash
claude mcp add crunchlog -- crunchlog mcp
```

Depois é só perguntar no Claude Code: *"o que combinamos com a Acme na terça?"* ou *"começa a gravar a reunião"*. Testamos o servidor por stdio, e ele responde com **15 ferramentas**:

`status`, `list_recordings`, `get_transcript`, `get_note`, `get_summary`, `search_notes`, `prep`, `cheatsheet`, `start_recording`, `stop_recording`, `toggle_recording`, `process`, `rename_speakers`, `export`, `doctor`.

No Codex e no Claude Desktop, registre o mesmo comando `crunchlog mcp` (stdio). O zip também traz um **plugin do Claude Code** (`plugins/crunchlog`) com skills de briefing e itens de ação: copie a pasta para um lugar fixo e rode `claude plugin marketplace add ./crunchlog` e `claude plugin install crunchlog@crunchlog`.

Atenção: o que o cliente MCP lê das notas vai para o provedor do modelo dele (Anthropic, OpenAI), como em qualquer sessão.

## 13. Claude OS / Agentic OS

Se você usa o **Claude OS de Jack Roberts** ([aula do Agentic OS](https://www.skool.com/aiautomationsbyjack/classroom/af686ad3?md=16da0f0bc87b4d399eadd0b1e69aabc5), só para membros):

```bash
crunchlog connect agentic-os --dry-run    # mostra o que vai fazer
crunchlog connect agentic-os              # registra o MCP no Claude Code + cria ~/Documents/Obsidian/CrunchLog/
crunchlog connect agentic-os --status | --undo
```

A partir daí, cada nota nova é copiada para esse cofre, aparece na página **Memory** do Claude OS e qualquer sessão do Claude Code consegue buscá-la. (Não rodamos este comando, porque ele altera o registro MCP do Claude Code.)

## 14. Modo Live (alpha)

Desligado por padrão. Quando ligado, transmite **as duas faixas para a AssemblyAI** (com a sua chave e na sua conta, que é paga) e manda as falas e perguntas para o seu Claude/Codex. Durante a call aparecem: a cola marcando as perguntas respondidas, resumos por bloco que se recolhem, a última pergunta fixada e um "pergunte à reunião". **A nota final continua vindo do pipeline local.** Não ative em calls confidenciais.

```toml
[live]
enabled = true
provider = "assemblyai"
api_key = "..."     # sua chave; nunca compartilhe
```

## 15. Todos os comandos

| Comando | Para quê |
|---|---|
| `toggle [--no-process]` | Liga/desliga a gravação (o da tecla) |
| `start [--slug X] [--speakers N]` / `stop [--no-process]` / `status [--json]` | Controle manual |
| `process <pasta-ou-arquivo> [--speakers N]` | Processa um bundle de novo ou importa áudio/vídeo |
| `devices` / `check-audio [--tone]` | Dispositivos e teste de 2 faixas |
| `setup [--yes] [--notes P] [--far N] [--mic N] [--provider X]` | Primeira configuração + modelos |
| `doctor [--skip-benchmark] [--json]` | Checagem completa (exit 0 = ok) |
| `init-config` / `config-path` | Config padrão / onde está |
| `demo [--no-process] [--voices A,B,C]` | Reunião inventada → nota |
| `dashboard [--port N] [--no-browser]` | Painel web local |
| `mcp` | Servidor MCP (stdio) |
| `ask <gravação\|latest> "pergunta" [--follow-up]` | Pergunta à reunião |
| `note "texto"` | Suas anotações da gravação atual |
| `templates list\|use\|which` | Modelo de resumo por tipo de reunião |
| `speakers <gravação> "Speaker 2=Nome"` / `rerender` / `open` | Pós-processamento da nota |
| `export <pasta> --format srt\|vtt\|txt\|json\|csv\|md` | Exportar |
| `prep "cliente"` | Cola pré-reunião |
| `watch <pasta>` / `watch-meetings` | Processa o que cair numa pasta / avisa quando uma call começa |
| `tray [--hotkey K]` | Ícone na bandeja (extra `tray`) |
| `connect agentic-os` | Liga no Claude OS |
| `live tail` / `live summarise` | Modo live (alpha) |
| `update [zip] [--check]` | Atualiza a partir do zip na pasta Downloads |

Linux (deste repo): `crunchlog-linux demo | start | stop | toggle | status | devices`.

## 16. Configuração

Arquivo: `~/.config/crunchlog/config.toml` (ou `$CRUNCHLOG_CONFIG`, ou `--config`). Os campos principais:

```toml
[paths]
recordings = "~/CrunchLog/recordings"
notes = "~/CrunchLog/notes"          # pode ser uma pasta dentro do cofre do Obsidian
models = "~/.cache/crunchlog/models"

[audio]
far_device = ""                      # vazio = padrão do sistema
mic_device = ""

[asr]
model = "nemo-parakeet-tdt-0.6b-v2"  # inglês
quantization = "int8"                # ou "none" (fp32, 4x RAM)

[diarization]
far_track = true
max_speakers = 0                     # 0 = automático

[speakers]
me_label = "Me"
them_label = "Speaker"

[gate]
enabled = true
margin_db = 3.0                      # aumente se o seu mic pega muito eco da caixa

[cleanup]
fillers = ["um", "umm", "uhm", "uh", "uhh"]
glossary = "~/.config/crunchlog/glossary.txt"   # "Quillery => Quillory", um por linha

[summary]
provider = "none"                    # none | claude | codex | auto
template = "~/.config/crunchlog/summary-prompt.md"

[dashboard]
port = 47431

[prep]
enabled = false
```

Dica: o glossário corrige nomes que o ASR erra sempre (no demo, "Quillory" virou "Quillery").

## 17. Privacidade: o que sai da máquina

- **Áudio e pastas de gravação: nunca saem.** Gravar e transcrever não abre conexão nenhuma.
- **Texto da reunião sai só** se você usar resumo ou `ask` (vai para a Anthropic/OpenAI pela sua CLI), um cliente MCP, ou o modo Live (aí o áudio vai para a AssemblyAI).
- **Downloads:** só os modelos, uma vez (Hugging Face e releases do sherpa-onnx no GitHub).
- **Modo totalmente privado:** `provider = "none"` e `[live] enabled = false`.

## 18. Problemas e soluções

| Sintoma | Causa / solução |
|---|---|
| `crunchlog: command not found` | `uv tool update-shell` e abra outro terminal, ou use `uv tool run crunchlog ...` |
| Faixa far muda (macOS) | Falta a permissão "Gravação de Tela e Áudio do Sistema" para `crunchlog-audio`. Conceda e grave de novo |
| Processar falha, gravar funciona (Windows) | `doctor` mostra `sherpa-onnx ... bundled onnxruntime missing`. Rode `uv tool install --python 3.12 --reinstall ".[mcp]"` na pasta do zip |
| `Access is denied` ao reinstalar (Windows) | Feche o tray e o dashboard antes |
| Falantes juntados num só | `crunchlog process <pasta> --speakers N` (N conta você) |
| Porta 47431 ocupada | `crunchlog dashboard --port 47500` ou `[dashboard] port` |
| **Linux:** `no recorder backend for this platform` | Esperado. Use `crunchlog-linux start/stop/toggle` |
| **Linux:** `crunchlog demo` diz que só fala no Windows/macOS | Use `crunchlog-linux demo` (Piper) |
| **Linux:** far vazio | Confira com `crunchlog-linux devices`; se o som sai por outra placa, use `CRUNCHLOG_FAR_TARGET=<node.name>` |
| **Linux:** mic sem palavras numa sessão remota (RDP) | A entrada do RDP não tem microfone; use uma entrada real com `CRUNCHLOG_MIC_TARGET` |
| Nota de arquivo importado sem "Me" | Normal: um arquivo único vira só faixa far |

Os problemas de macOS estão detalhados em `docs/mac-helper.md` dentro do zip, e os do demo em `docs/features/demo.md`.

## 19. Atualizar e desinstalar

- **Atualizar:** baixe o zip novo na pasta Downloads e clique em **Update CrunchLog** (bandeja), em **Update now** (Doctor do dashboard) ou rode `crunchlog update`. Config, gravações, notas e o login do dashboard ficam. Nas primeiras versões, sem o comando `update`, feche tudo e rode `uv tool install --python 3.12 --reinstall ".[mcp]"` na pasta nova.
- **Desinstalar:** `uv tool uninstall crunchlog`, depois apague `~/.cache/crunchlog` (modelos) e `~/.config/crunchlog` (config). Suas gravações e notas ficam onde estão. Os extras do Linux saem com `uv tool uninstall piper-tts` e `rm ~/.local/bin/crunchlog-linux`.

---

## Licença

O **CrunchLog** é © 2026 Christian Landsteiner, sob a **CrunchLog Evaluation Licence**. Ela permite baixar, instalar e usar nas suas máquinas para uso pessoal e avaliação, além de ler e modificar o código para isso. Ela **proíbe** redistribuir (inclusive em repositório público), vender ou oferecer como serviço, e remover o crédito ao Claude OS de Jack Roberts. Por isso este repositório **não** contém o zip, o código nem os vídeos do autor. Contato para outros usos: o e-mail que está no `LICENSE` dentro do zip.

O conteúdo deste repositório (este guia, o guia em `guia/` e os scripts em `linux/`) é do INEMA. Os scripts de `linux/` só funcionam com um CrunchLog que você mesmo baixou e instalou.
