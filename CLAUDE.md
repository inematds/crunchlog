# CLAUDE.md — crunchlog

Guia + scripts Linux para o CrunchLog (notetaker local de reuniões, © Christian Landsteiner, licença de AVALIAÇÃO).

- **Nunca commitar/publicar o software do autor**: zip, `src/`, vídeos, transcrições ficam em `_fonte/` (gitignored). A licença proíbe redistribuir e repo público. O repo público só tem README, `guia/` e `linux/` (código nosso). Manter o crédito ao Claude OS de Jack Roberts sempre que citar o link do Agentic OS.
- Fonte: post Skool `aiautomationsbyjack` p=e0359d6f (zip 2.0.0a1, screenshot, vídeo 2:26 = mesmo do Tella). Rebaixar com `_fonte/fetch.py` (runbook skool.md, pegadinha do perfil do Firefox).
- Instalado neste host: `uv tool install --python 3.12 ".[mcp]"` na `_fonte/crunchlog-2.0.0a1`; config `~/.config/crunchlog/config.toml` (provider none); notas em `~/CrunchLog/`.
- Linux: gravar = `linux/recorder_linux.py` (pw-record); demo = `linux/demo_linux.py` (Piper, injeta `tts_factory` no `demo.run`). Testar com o python do tool: `"$(uv tool dir)/crunchlog/bin/python"`.
- Dashboard porta 47431: conferir `ss -ltn` antes; matar só o PID que subiu.
- Autor dos commits: `inematds <inematds@gmail.com>`.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule under ## Lessons, so it never happens again.

## Lessons

- `crunchlog export` exige o CAMINHO da pasta da gravação (não aceita só o nome, ao contrário do `ask`). (05/10/2026)
