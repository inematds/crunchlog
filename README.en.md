# CrunchLog: complete user guide (Windows, macOS and Linux)

[![CrunchLog: local meetings](guia/assets/banner-en.jpg)](https://inematds.github.io/crunchlog/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## 📖 User guide

Complete guide (landing + step by step): **https://inematds.github.io/crunchlog/guia/en/**

**CrunchLog** records meetings and generates Markdown notes **without leaving your machine**. You press a key when the call starts and again when it ends. A few seconds later a note appears with every line attributed to a speaker ("Me" is you, "Speaker 2", "Speaker 3"... are the others). No bot joins the call, and you need no account and no API key.

- Author: **Christian Landsteiner**. Version tested here: **2.0.0a1** (build `1daf268`, 04/10/2026).
- Origin: post in the *AI Automations by Jack* community (Skool), [CrunchLog: live meeting co-pilot + fully local private mode for Claude Code, Codex and Agentic OS](https://www.skool.com/aiautomationsbyjack/crunchlog-live-meeting-co-pilot-fully-local-private-mode-for-claude-code-codex-and-agentic-os-windows-mac?p=e0359d6f). The zip is attached there, members only.
- The **Claude OS** integration is by **Jack Roberts** ([Agentic OS lesson](https://www.skool.com/aiautomationsbyjack/classroom/af686ad3?md=16da0f0bc87b4d399eadd0b1e69aabc5), members only). The CrunchLog licence requires keeping this credit.

> **This repository does not contain CrunchLog.** The licence is an evaluation licence and forbids redistributing the software (see [License](#license)). Here you will find only this guide, written by us, and our own Linux scripts in [`linux/`](linux/). To use it, download the zip from the Skool post.

---

## Table of contents

1. [What it does](#1-what-it-does)
2. [How it works inside](#2-how-it-works-inside)
3. [Requirements](#3-requirements)
4. [Install on Windows or macOS](#4-install-on-windows-or-macos)
5. [Install on Linux (tested)](#5-install-on-linux-tested)
6. [First note: the demo](#6-first-note-the-demo)
7. [Record a real meeting](#7-record-a-real-meeting)
8. [What the note looks like](#8-what-the-note-looks-like)
9. [Summary and questions with Claude or Codex](#9-summary-and-questions-with-claude-or-codex)
10. [Dashboard in the browser](#10-dashboard-in-the-browser)
11. [Cheatsheet before the meeting (`prep`)](#11-cheatsheet-before-the-meeting-prep)
12. [MCP: ask about your meetings inside Claude Code](#12-mcp-ask-about-your-meetings-inside-claude-code)
13. [Claude OS / Agentic OS](#13-claude-os--agentic-os)
14. [Live mode (alpha)](#14-live-mode-alpha)
15. [All commands](#15-all-commands)
16. [Configuration](#16-configuration)
17. [Privacy: what leaves the machine](#17-privacy-what-leaves-the-machine)
18. [Problems and fixes](#18-problems-and-fixes)
19. [Update and uninstall](#19-update-and-uninstall)
20. [License](#license)

---

## 1. What it does

| Feature | How it works | Status |
|---|---|---|
| **Two tracks, no driver** | Records what comes out of the speakers (the "far" track: Zoom, Meet, YouTube) separately from the microphone (the "mic" track). That way it knows which words are yours. No VoiceMeeter or BlackHole needed. | stable |
| **One key** | `crunchlog toggle` starts and stops. You can bind it to a shortcut, to a Stream Deck or to the dashboard. | stable |
| **Markdown note** | In the notes folder (works well with Obsidian), with every line attributed and timed `[mm:ss]`. | stable |
| **Local transcription** | Parakeet TDT 0.6B v2 (NVIDIA, int8, ONNX) on the CPU. Measured here: **27.6× real time** (a 1 h call in ~2 min). | stable |
| **Speaker separation** | pyannote segmentation 3.0 + TitaNet (sherpa-onnx) on the "far" track. | stable |
| **Summary and action items** | Through your **Claude Code** or **Codex** login (subscription, no paid API). | experimental |
| **Ask the meeting** (`ask`) | Answers cite `[mm:ss Speaker]`. | experimental |
| **Meeting cheatsheet** (`prep`) | Gathers pending items, decisions and open questions from a client's latest notes. No model. | experimental |
| **MCP server** | Claude Code / Codex / Claude Desktop read and search your meetings and start recordings. | experimental |
| **Dashboard** | Recorder, waveform, clickable transcript, speaker renaming, prompts, settings, doctor. | experimental |
| **Live co-pilot** | Live transcription by AssemblyAI (your account) and summary during the call. **Off by default.** | alpha |

Limits of this version: **English only**, the first setup downloads **~700 MB** of models, and macOS requires **14.2+ on Apple Silicon**. Everything beyond recording and generating the note is experimental.

## 2. How it works inside

```
 key / dashboard / MCP
          │
          ▼
  ┌──────────────── recording (Windows: WASAPI · macOS: CoreAudio · Linux: our pw-record) ────┐
  │  far.wav  ← what you hear          mic.wav ← what you say          meta.json (clock)      │
  └──────────────────────────────── = 1 "bundle" (one folder per meeting) ───────────────────┘
          │
          ▼  crunchlog process  (all local, CPU)
  VAD (silero) → ASR (Parakeet) per track → "gate" removes from the mic the sound that leaked from the speakers
          → speaker separation on the far track → turns (turns.json) → cleanup ("um", "uh", glossary)
          │
          ├──► Markdown note in the notes folder  (~/CrunchLog/notes/YYYY-MM-DD-HHMM-slug.md)
          └──► optional: summary / ask via `claude -p` or `codex` (your subscription)
```

The "two-track trick": since the microphone is recorded separately, everything that comes from it is **you** ("Me"). The AI separation only has to tell apart the people on the other end. If the speakers leak into the microphone, the *gate* compares the tracks and drops from the mic the words that were echo (in the demo, 262 of 396 words were dropped, which was exactly the simulated echo).

## 3. Requirements

| | Windows | macOS | Linux |
|---|---|---|---|
| System | 10 or 11 | 14.2+ Apple Silicon | **not officially supported**; works with this repo's scripts (tested on Ubuntu aarch64 with PipeWire) |
| Recording | WASAPI, native | `crunchlog-audio` helper (comes ready in the zip) | `pw-record` (PipeWire) through our `crunchlog-linux` |
| Demo with voice | System.Speech | `say` | Piper (installed by our script) |
| Always | [uv](https://docs.astral.sh/uv/) (it downloads Python 3.12 by itself), ~1 GB free for models | | |
| Optional | `ffmpeg` (import mp3/mp4), Claude Code or Codex logged in (summary/ask) | | |

Install uv:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 4. Install on Windows or macOS

1. Download `crunchlog-2.0.0a1.zip` from the Skool post and unzip it.
2. **Easiest way (the author recommends it):** open a terminal in the folder, run `claude` and paste:

   ```
   I have extracted CrunchLog into this folder. Read START-HERE.md and AGENTS.md and install it for me, then run the demo so I get my first note.
   ```

   Claude Code follows the `AGENTS.md` from the zip: it checks uv and Python, installs, asks four questions (notes folder, "far" device, microphone, summary provider), runs `doctor` and finishes with the `demo`.
3. **Manual way (four commands, inside the unzipped folder):**

   ```bash
   uv tool install --python 3.12 ".[mcp]"
   crunchlog setup        # Enter accepts the defaults; --yes asks nothing
   crunchlog doctor       # exit 0 and no [fail] line = ready to record
   crunchlog demo         # your first note in ~1 min
   ```

- `".[mcp]"` already includes the MCP server. For the tray icon: `".[mcp,tray]"`.
- If `crunchlog` is not found: `uv tool update-shell` and open another terminal (or use `uv tool run crunchlog ...`).
- **macOS:** the first recording asks for two permissions for `crunchlog-audio` (not for Terminal): **Microphone** and **Screen & System Audio Recording**. Without the second, the far track comes out silent. If Gatekeeper blocks the helper, run `xattr -cr .` **only in the unzipped folder**.

## 5. Install on Linux (tested)

CrunchLog 2.0.0a1 does not record on Linux (`crunchlog devices` → *no recorder backend for this platform*), but **everything else runs**: transcription, speaker separation, note, summary, ask, export, prep, dashboard and MCP. We tested on **Ubuntu, ARM64 (aarch64), PipeWire**, and the dependencies installed without any patch. To close the two gaps (recording and demo), this repo ships [`linux/`](linux/):

| File | What for |
|---|---|
| `linux/recorder_linux.py` | Two-track recorder with `pw-record`: default output monitor → `far.wav`, default input → `mic.wav`, `meta.json` in the official contract (`bundle_version: 2`). On `stop`, it calls the official pipeline. |
| `linux/demo_linux.py` | The same `crunchlog demo` (same script, same assembly, same pipeline), only swapping the system voice for **Piper**. Does not change CrunchLog's code. |
| `linux/crunchlog-linux` | Shortcut: `demo`, `start`, `stop`, `toggle`, `status`, `devices`. |
| `linux/instalar-extras-linux.sh` | Installs Piper + 3 English voices (~190 MB) and puts `crunchlog-linux` in `~/.local/bin`. |

Step by step (exactly what we ran):

```bash
# 1. CrunchLog (inside the unzipped zip folder)
uv tool install --python 3.12 ".[mcp]"
crunchlog --version          # crunchlog 2.0.0a1 (build 1daf268 of 2026-10-04)

# 2. Setup without questions (on Linux there is no device list to choose from)
crunchlog setup --yes --provider none      # downloads the ~700 MB of models

# 3. Extras from this repo
git clone https://github.com/inematds/crunchlog && bash crunchlog/linux/instalar-extras-linux.sh

# 4. Check
crunchlog doctor
```

Real `doctor` output on Linux: the two `[fail]` lines only concern native recording, which `crunchlog-linux` replaces.

```
[fail] platform: linux: CrunchLog records on Windows and macOS only
[ok  ] python: Python 3.12.3
[ok  ] sherpa-onnx: bundled onnxruntime not needed on this platform
[ok  ] config: /home/<you>/.config/crunchlog/config.toml
[fail] devices: UnsupportedPlatform: CrunchLog records on Windows and macOS; this is linux
[ok  ] models: /home/<you>/.cache/crunchlog/models
[ok  ] summary: provider none; on PATH: claude, codex
[ok  ] ffmpeg: /usr/bin/ffmpeg
[ok  ] asr speed: 27.6x realtime (a 1-hour call takes about 2 min)
[ok  ] disk: 211.9 GB free at /home/<you>/CrunchLog
Recording cannot start: fix platform, devices.
```

To pick other sound cards: `wpctl status` lists the devices and `wpctl inspect <id> | grep node.name` shows the name. Then just use `CRUNCHLOG_FAR_TARGET=<sink>` and `CRUNCHLOG_MIC_TARGET=<source>` before `crunchlog-linux start`.

## 6. First note: the demo

The demo acts out an invented meeting with three people ("Me" on the microphone; Dana and Lee on the other end), records both tracks with simulated speaker leakage, processes everything through the real pipeline and prints the path of the note. No microphone needed.

```bash
crunchlog demo            # Windows / macOS
crunchlog-linux demo      # Linux
```

Real output on Linux:

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
note: /home/<you>/CrunchLog/notes/2026-10-05-1642-demo.md
```

Options: `--no-process` (only records the bundle), `--voices A,B,C`, `--list-voices`, `--no-bleed` (no simulated leakage).

## 7. Record a real meeting

```bash
crunchlog toggle                 # start (Windows/macOS)
# ... meeting ...
crunchlog toggle                 # stop; the note appears in a few seconds

crunchlog-linux toggle           # the same on Linux
crunchlog start --slug acme --speakers 3   # folder name + total number of people (including you)
crunchlog status                 # idle / recording
```

**Binding it to a key:**
- **Windows:** PowerToys Keyboard Manager or AutoHotkey running `crunchlogw toggle` (`crunchlogw` doesn't open a console window). Stream Deck: "System: Open" action → `crunchlog.exe toggle`.
- **macOS:** Shortcuts app shortcut with "Run Shell Script" `crunchlog toggle`, or Raycast / Hammerspoon.
- **Linux:** custom GNOME/KDE shortcut pointing to `~/.local/bin/crunchlog-linux toggle`.
- **Tray with global hotkey** (Windows/macOS): install with `".[mcp,tray]"` and run `crunchlog tray --hotkey ...`.

Before your first call, `crunchlog check-audio --tone` records a few seconds and tells you whether both tracks are listening (Windows/macOS).

**Files you already have** (mp3, m4a, mp4, wav): `crunchlog process file.mp4`. Everything comes in as the "far" track, so there is no "Me" and speakers start at Speaker 2. A watched folder: `crunchlog watch ~/Gravador`. We tested with the author's walkthrough video (2:26): **note ready in 18 s**.

## 8. What the note looks like

File `~/CrunchLog/notes/2026-10-05-1642-demo.md` (the demo's invented meeting):

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

## Summary            ← only with the claude/codex provider
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

Next to it, in the recording folder (`~/CrunchLog/recordings/<name>/`), you will find `far.wav`, `mic.wav`, `meta.json`, `words.json`, `turns.json`, `summary.md`, `pipeline.log`.

After recording:

```bash
crunchlog speakers <recording> "Speaker 2=Dana" "Speaker 3=Lee"   # gives names and redoes the note
crunchlog note "client wants a proposal by Friday"                  # your notes go into the summary
crunchlog export ~/CrunchLog/recordings/<recording> --format srt    # srt|vtt|txt|json|csv|md
crunchlog open latest --obsidian
crunchlog rerender <recording>                                      # redoes the note without transcribing again
```

## 9. Summary and questions with Claude or Codex

The summary uses no paid API: CrunchLog calls **your logged-in CLI** (`claude -p ...` or `codex`) with tools, MCP and commands turned off, which means it comes out of your subscription.

```toml
# ~/.config/crunchlog/config.toml
[summary]
provider = "claude"        # none | claude | codex | auto
claude_model = "opus"      # opus | sonnet | haiku
claude_effort = "medium"
```

Measured here: demo summary by Claude in **10.3 s** (1,285 characters: Summary, Decisions, Action items, Open questions).

```bash
crunchlog ask latest "What was decided about the beta launch date and size?"
```

Real answer (with clickable citations in the dashboard):

> The beta starts on **November 12 with 200 testers**, and it opens to everyone else two weeks later [01:13 Me]. ... Me thought 500 was too many with a crash the team already knew about [00:49 Me].

Summary templates by meeting type: `crunchlog templates list | use standup | which` (standup, sales call, interview...). The prompts can be edited on the dashboard's **Prompts** page.

## 10. Dashboard in the browser

```bash
crunchlog dashboard            # http://127.0.0.1:47431/ (local only; --port changes it; --no-browser doesn't open it)
```

On each browser's first visit, use the link with `?t=...` that it prints (it is the local login) and then save the plain address in your bookmarks.

| Page | What it has |
|---|---|
| **Overview** | Record/Stop button, meters for both tracks, title, number of speakers, latest recordings, disk and models |
| **Recordings** | Recordings archive, filters (unprocessed, with problems), calendar |
| **Recording** | Waveform of both tracks, who speaks when, player (1×–2×), clickable transcript, speaker renaming, summary, export, "Process again" |
| **Notes** | All the notes in the folder |
| **Prompts** | Summary templates; which one is in use |
| **Settings** | Folders, devices, transcription, speaker labels, cleanup, summary (Opus medium through the subscription), ask, live, notifications |
| **Doctor** | The same checks as `crunchlog doctor` and the "Update now" button |

On Linux, the dashboard's **Record** button doesn't work (it uses the native recorder). Record with `crunchlog-linux`, and the dashboard shows and plays the recording normally.

![Dashboard: demo recording with the two tracks](guia/assets/dash-demo.jpg)

## 11. Cheatsheet before the meeting (`prep`)

```bash
crunchlog prep "acme"                     # gathers from the last 90 days of notes with "acme" in the title/participants
crunchlog prep "acme" --calendar "Thu 2pm, Ana and Bruno" --dry-run
```

Generates `<notes>/YYYY-MM-DD-acme-cheatsheet.md` with open action items, earlier decisions, open questions and 3 to 5 guide questions `(qN)`. It doesn't call any model. With `[prep] enabled = true`, when the next Acme note is ready, it **ticks off by itself** the questions that were answered. Per-client links live in `~/.config/crunchlog/links/acme.md`.

## 12. MCP: ask about your meetings inside Claude Code

```bash
claude mcp add crunchlog -- crunchlog mcp
```

Then just ask in Claude Code: *"what did we agree with Acme on Tuesday?"* or *"start recording the meeting"*. We tested the server over stdio, and it answers with **15 tools**:

`status`, `list_recordings`, `get_transcript`, `get_note`, `get_summary`, `search_notes`, `prep`, `cheatsheet`, `start_recording`, `stop_recording`, `toggle_recording`, `process`, `rename_speakers`, `export`, `doctor`.

In Codex and Claude Desktop, register the same `crunchlog mcp` command (stdio). The zip also ships a **Claude Code plugin** (`plugins/crunchlog`) with briefing and action-item skills: copy the folder to a fixed place and run `claude plugin marketplace add ./crunchlog` and `claude plugin install crunchlog@crunchlog`.

Note: whatever the MCP client reads from the notes goes to its model provider (Anthropic, OpenAI), as in any session.

## 13. Claude OS / Agentic OS

If you use **Jack Roberts' Claude OS** ([Agentic OS lesson](https://www.skool.com/aiautomationsbyjack/classroom/af686ad3?md=16da0f0bc87b4d399eadd0b1e69aabc5), members only):

```bash
crunchlog connect agentic-os --dry-run    # shows what it will do
crunchlog connect agentic-os              # registers the MCP in Claude Code + creates ~/Documents/Obsidian/CrunchLog/
crunchlog connect agentic-os --status | --undo
```

From then on, every new note is copied to that vault, shows up on Claude OS's **Memory** page and any Claude Code session can search it. (We did not run this command, because it changes Claude Code's MCP registry.)

## 14. Live mode (alpha)

Off by default. When on, it streams **both tracks to AssemblyAI** (with your key and on your account, which is paid) and sends the lines and questions to your Claude/Codex. During the call you see: the cheatsheet ticking off answered questions, block summaries that collapse, the latest question pinned and an "ask the meeting" box. **The final note still comes from the local pipeline.** Don't turn it on for confidential calls.

```toml
[live]
enabled = true
provider = "assemblyai"
api_key = "..."     # your key; never share it
```

## 15. All commands

| Command | What for |
|---|---|
| `toggle [--no-process]` | Starts/stops recording (the one for the key) |
| `start [--slug X] [--speakers N]` / `stop [--no-process]` / `status [--json]` | Manual control |
| `process <folder-or-file> [--speakers N]` | Processes a bundle again or imports audio/video |
| `devices` / `check-audio [--tone]` | Devices and 2-track test |
| `setup [--yes] [--notes P] [--far N] [--mic N] [--provider X]` | First setup + models |
| `doctor [--skip-benchmark] [--json]` | Full check (exit 0 = ok) |
| `init-config` / `config-path` | Default config / where it is |
| `demo [--no-process] [--voices A,B,C]` | Invented meeting → note |
| `dashboard [--port N] [--no-browser]` | Local web panel |
| `mcp` | MCP server (stdio) |
| `ask <recording\|latest> "question" [--follow-up]` | Ask the meeting |
| `note "text"` | Your notes for the current recording |
| `templates list\|use\|which` | Summary template by meeting type |
| `speakers <recording> "Speaker 2=Name"` / `rerender` / `open` | Note post-processing |
| `export <folder> --format srt\|vtt\|txt\|json\|csv\|md` | Export |
| `prep "client"` | Pre-meeting cheatsheet |
| `watch <folder>` / `watch-meetings` | Processes whatever lands in a folder / warns when a call starts |
| `tray [--hotkey K]` | Tray icon (`tray` extra) |
| `connect agentic-os` | Connects to Claude OS |
| `live tail` / `live summarise` | Live mode (alpha) |
| `update [zip] [--check]` | Updates from the zip in the Downloads folder |

Linux (from this repo): `crunchlog-linux demo | start | stop | toggle | status | devices`.

## 16. Configuration

File: `~/.config/crunchlog/config.toml` (or `$CRUNCHLOG_CONFIG`, or `--config`). The main fields:

```toml
[paths]
recordings = "~/CrunchLog/recordings"
notes = "~/CrunchLog/notes"          # can be a folder inside the Obsidian vault
models = "~/.cache/crunchlog/models"

[audio]
far_device = ""                      # empty = system default
mic_device = ""

[asr]
model = "nemo-parakeet-tdt-0.6b-v2"  # English
quantization = "int8"                # or "none" (fp32, 4x RAM)

[diarization]
far_track = true
max_speakers = 0                     # 0 = automatic

[speakers]
me_label = "Me"
them_label = "Speaker"

[gate]
enabled = true
margin_db = 3.0                      # increase if your mic picks up a lot of echo from the speakers

[cleanup]
fillers = ["um", "umm", "uhm", "uh", "uhh"]
glossary = "~/.config/crunchlog/glossary.txt"   # "Quillery => Quillory", one per line

[summary]
provider = "none"                    # none | claude | codex | auto
template = "~/.config/crunchlog/summary-prompt.md"

[dashboard]
port = 47431

[prep]
enabled = false
```

Tip: the glossary fixes names the ASR always gets wrong (in the demo, "Quillory" became "Quillery").

## 17. Privacy: what leaves the machine

- **Audio and recording folders: they never leave.** Recording and transcribing open no connection at all.
- **Meeting text leaves only** if you use summary or `ask` (it goes to Anthropic/OpenAI through your CLI), an MCP client, or Live mode (in which case the audio goes to AssemblyAI).
- **Downloads:** only the models, once (Hugging Face and sherpa-onnx releases on GitHub).
- **Fully private mode:** `provider = "none"` and `[live] enabled = false`.

## 18. Problems and fixes

| Symptom | Cause / fix |
|---|---|
| `crunchlog: command not found` | `uv tool update-shell` and open another terminal, or use `uv tool run crunchlog ...` |
| Far track silent (macOS) | The "Screen & System Audio Recording" permission is missing for `crunchlog-audio`. Grant it and record again |
| Processing fails, recording works (Windows) | `doctor` shows `sherpa-onnx ... bundled onnxruntime missing`. Run `uv tool install --python 3.12 --reinstall ".[mcp]"` in the zip folder |
| `Access is denied` when reinstalling (Windows) | Close the tray and the dashboard first |
| Speakers merged into one | `crunchlog process <folder> --speakers N` (N counts you) |
| Port 47431 busy | `crunchlog dashboard --port 47500` or `[dashboard] port` |
| **Linux:** `no recorder backend for this platform` | Expected. Use `crunchlog-linux start/stop/toggle` |
| **Linux:** `crunchlog demo` says it only speaks on Windows/macOS | Use `crunchlog-linux demo` (Piper) |
| **Linux:** far empty | Check with `crunchlog-linux devices`; if the sound goes out through another card, use `CRUNCHLOG_FAR_TARGET=<node.name>` |
| **Linux:** mic has no words in a remote session (RDP) | The RDP input has no microphone; use a real input with `CRUNCHLOG_MIC_TARGET` |
| Note from an imported file has no "Me" | Normal: a single file becomes only the far track |

The macOS problems are detailed in `docs/mac-helper.md` inside the zip, and the demo's in `docs/features/demo.md`.

## 19. Update and uninstall

- **Update:** download the new zip into the Downloads folder and click **Update CrunchLog** (tray), **Update now** (dashboard Doctor) or run `crunchlog update`. Config, recordings, notes and the dashboard login stay. In the first versions, without the `update` command, close everything and run `uv tool install --python 3.12 --reinstall ".[mcp]"` in the new folder.
- **Uninstall:** `uv tool uninstall crunchlog`, then delete `~/.cache/crunchlog` (models) and `~/.config/crunchlog` (config). Your recordings and notes stay where they are. The Linux extras go with `uv tool uninstall piper-tts` and `rm ~/.local/bin/crunchlog-linux`.

---

## License

**CrunchLog** is © 2026 Christian Landsteiner, under the **CrunchLog Evaluation Licence**. It allows you to download, install and use it on your own machines for personal use and evaluation, and to read and modify the code for that purpose. It **forbids** redistributing it (including in a public repository), selling it or offering it as a service, and removing the credit to Jack Roberts' Claude OS. For that reason this repository does **not** contain the zip, the code or the author's videos. Contact for other uses: the e-mail in the `LICENSE` inside the zip.

The content of this repository (this guide, the guide in `guia/` and the scripts in `linux/`) is by INEMA. The scripts in `linux/` only work with a CrunchLog that you downloaded and installed yourself.
