#!/usr/bin/env bash
# Extras do CrunchLog para Linux: Piper (voz local do demo) + 3 vozes inglesas + atalho crunchlog-linux.
# Pré-requisitos: CrunchLog já instalado (uv tool install --python 3.12 ".[mcp]") e PipeWire (pw-record).
set -euo pipefail
here="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
voices="${PIPER_VOICES_DIR:-$HOME/.cache/crunchlog/piper-voices}"

command -v crunchlog >/dev/null || { echo "error: instale o CrunchLog primeiro" >&2; exit 1; }
command -v pw-record >/dev/null || echo "aviso: pw-record não encontrado (pacote pipewire-bin); gravar não vai funcionar" >&2

command -v piper >/dev/null || uv tool install piper-tts
mkdir -p "$voices"
"$(uv tool dir)/piper-tts/bin/python" -m piper.download_voices \
  en_GB-alan-medium en_US-amy-medium en_US-ryan-medium --data-dir "$voices"

mkdir -p "$HOME/.local/bin"
ln -sf "$here/crunchlog-linux" "$HOME/.local/bin/crunchlog-linux"
chmod +x "$here/crunchlog-linux"
echo "ok: crunchlog-linux em ~/.local/bin; teste com: crunchlog-linux demo"
