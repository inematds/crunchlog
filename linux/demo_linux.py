"""crunchlog demo no Linux: a mesma reunião inventada do `crunchlog demo`, falada pelo Piper.

O `crunchlog demo` oficial só fala com a voz do sistema no Windows (System.Speech) e no macOS
(`say`). Aqui trocamos só o motor de voz: o roteiro, a montagem das duas faixas (far.wav e
mic.wav), o processamento e a nota são os do próprio CrunchLog. O código do CrunchLog não é
alterado; o `run` do módulo de demo recebe um `tts_factory` diferente antes de a CLI montar
os comandos.

Uso (com o python do ambiente do CrunchLog):
    "$(uv tool dir)/crunchlog/bin/python" linux/demo_linux.py [opções do crunchlog demo]

Variáveis:
    PIPER_BIN          executável do Piper (padrão: `piper` no PATH)
    PIPER_VOICES_DIR   pasta com os .onnx das vozes (padrão: ~/.cache/crunchlog/piper-voices)
"""

from __future__ import annotations

import functools
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

import numpy as np

from crunchlog import cli
from crunchlog.features import demo

VOICES_DIR = Path(os.environ.get("PIPER_VOICES_DIR", "~/.cache/crunchlog/piper-voices")).expanduser()
PIPER = os.environ.get("PIPER_BIN") or shutil.which("piper") or "piper"

#: Gênero de cada voz Piper que baixamos (o demo pede Me=male, Dana=female, Lee=male).
KNOWN_GENDERS = {"en_US-ryan-medium": "male", "en_GB-alan-medium": "male", "en_US-amy-medium": "female"}

#: Velocidade (length_scale do Piper) quando a mesma voz é reaproveitada para outra pessoa.
LENGTH_SCALES = (1.0, 0.9, 1.12, 0.82, 1.25)


class PiperTts:
    name = "piper"

    def __init__(self, *, voices: Sequence[str] = (), log=demo._null_log, **_ignored) -> None:
        self.wanted = tuple(voices)
        self.log = log
        self.voices_used: dict[str, demo.VoiceChoice] = {}

    def list_voices(self) -> list[demo.Voice]:
        found = []
        for model in sorted(VOICES_DIR.glob("*.onnx")):
            name = model.stem
            language = name.split("-", 1)[0].replace("_", "-")
            found.append(demo.Voice(name=name, language=language, gender=KNOWN_GENDERS.get(name, "")))
        if not found:
            raise demo.TtsError(f"nenhuma voz Piper em {VOICES_DIR}; baixe com "
                                f"`python -m piper.download_voices en_US-ryan-medium en_US-amy-medium "
                                f"en_GB-alan-medium --data-dir {VOICES_DIR}`")
        return found

    def __call__(self, requests: Sequence[demo.SpeechRequest]) -> list[np.ndarray]:
        speakers = list(dict.fromkeys(r.speaker for r in requests))
        self.voices_used = demo._choose(self.list_voices(), speakers, self.wanted, self.log)
        clips: list[np.ndarray] = []
        with tempfile.TemporaryDirectory(prefix="crunchlog-demo-piper-") as tmp:
            for i, request in enumerate(requests):
                choice = self.voices_used[request.speaker]
                out = Path(tmp) / f"line-{i:03d}.wav"
                scale = LENGTH_SCALES[choice.rate_step % len(LENGTH_SCALES)]
                argv = [PIPER, "-m", str(VOICES_DIR / f"{choice.voice}.onnx"), "--length-scale", str(scale),
                        "-f", str(out)]
                done = subprocess.run(argv, input=request.text, text=True, capture_output=True, timeout=120)
                if done.returncode != 0:
                    raise demo.TtsError(f"piper falhou (exit {done.returncode}): {done.stderr.strip()[-300:]}")
                clips.append(demo.read_tts_wav(out))
        return clips


def main() -> int:
    demo.run = functools.partial(demo.run, tts_factory=PiperTts)
    return cli.main(["demo", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
