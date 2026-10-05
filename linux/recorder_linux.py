"""Gravador de duas faixas para Linux (PipeWire) que entrega um bundle no formato do CrunchLog.

O CrunchLog 2.0.0a1 só grava no Windows (WASAPI) e no macOS (CoreAudio). No Linux, o
processamento (ASR, separação de falantes, nota, MCP, dashboard) funciona; falta o gravador.
Este script preenche essa lacuna com o `pw-record` do PipeWire:

    far.wav  <- monitor da saída de som (o que você OUVE: Zoom, Meet, YouTube...)
    mic.wav  <- entrada de som (o que você FALA)

Ambas em 16 kHz mono PCM16, com `meta.json` no contrato `bundle_version: 2`. No `stop`, chama o
pipeline oficial (`crunchlog process <bundle>`) e imprime `note: <caminho>`.

Uso (com o python do ambiente do CrunchLog):
    PY="$(uv tool dir)/crunchlog/bin/python"
    $PY linux/recorder_linux.py start [--slug cliente-x] [--speakers N]
    $PY linux/recorder_linux.py stop
    $PY linux/recorder_linux.py toggle      # para um atalho de teclado
    $PY linux/recorder_linux.py status
    $PY linux/recorder_linux.py devices     # saída/entrada padrão que serão gravadas

Variáveis: CRUNCHLOG_FAR_TARGET / CRUNCHLOG_MIC_TARGET para escolher outro node.name do PipeWire
(lista: `wpctl status`, nomes: `wpctl inspect <id> | grep node.name`).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from crunchlog import __version__, audio, bundle
from crunchlog.config import load_config

STATE = Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser() / "crunchlog-linux" / "current.json"
SILENT_DB = -60.0


def node_name(selector: str) -> str:
    out = subprocess.run(["wpctl", "inspect", selector], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if "node.name" in line:
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(f"error: não achei node.name para {selector}")


def targets() -> tuple[str, str]:
    far = os.environ.get("CRUNCHLOG_FAR_TARGET") or node_name("@DEFAULT_AUDIO_SINK@")
    mic = os.environ.get("CRUNCHLOG_MIC_TARGET") or node_name("@DEFAULT_AUDIO_SOURCE@")
    return far, mic


def pw_record(target: str, out: Path, *, monitor: bool) -> subprocess.Popen:
    argv = ["pw-record", "--target", target, "--rate", str(bundle.SAMPLE_RATE), "--channels", "1",
            "--format", "s16"]
    if monitor:
        argv += ["-P", "stream.capture.sink=true"]
    argv.append(str(out))
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, start_new_session=True)


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_state() -> dict | None:
    try:
        state = json.loads(STATE.read_text())
    except (OSError, ValueError):
        return None
    return state if any(alive(p) for p in state.get("pids", {}).values()) else None


def start(slug: str | None, speakers: int | None) -> int:
    if read_state():
        print("error: já está gravando (use stop)", file=sys.stderr)
        return 1
    config = load_config()
    started = datetime.now().astimezone()
    bundle_dir = bundle.new_bundle_dir(config.paths.recordings, started, slug)
    far, mic = targets()
    procs = {"far": pw_record(far, bundle_dir / "far.wav", monitor=True)}
    epochs = {"far": time.time()}
    procs["mic"] = pw_record(mic, bundle_dir / "mic.wav", monitor=False)
    epochs["mic"] = time.time()
    time.sleep(0.5)
    dead = [name for name, p in procs.items() if p.poll() is not None]
    if dead:
        for p in procs.values():
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
        err = "; ".join((procs[n].stderr.read() or b"").decode(errors="replace").strip() for n in dead)
        print(f"error: pw-record não iniciou ({', '.join(dead)}): {err}", file=sys.stderr)
        return 1
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"bundle": str(bundle_dir), "slug": slug, "speakers": speakers,
                                 "created_at": started.isoformat(timespec="seconds"),
                                 "devices": {"far": far, "mic": mic}, "epochs": epochs,
                                 "pids": {n: p.pid for n, p in procs.items()}}))
    print(f"recording: {bundle_dir}")
    print(f"  far <- monitor de {far}\n  mic <- {mic}")
    return 0


def stop(process: bool = True) -> int:
    state = read_state()
    if not state:
        print("error: nada gravando", file=sys.stderr)
        return 1
    for pid in state["pids"].values():
        if alive(pid):
            os.kill(pid, signal.SIGINT)
    deadline = time.time() + 10
    while time.time() < deadline and any(alive(p) for p in state["pids"].values()):
        time.sleep(0.1)
    bundle_dir = Path(state["bundle"])
    tracks, reasons = {}, []
    for name in ("far", "mic"):
        path = bundle_dir / f"{name}.wav"
        if not path.is_file():
            reasons.append(f"{name}_missing")
            continue
        audio.repair_wav_header(path)
        samples = audio.read_wav(path)
        silent = bool(len(samples) == 0 or audio.rms_db(samples) < SILENT_DB)
        if name == "far" and silent:
            reasons.append("far_silent")
        tracks[name] = bundle.Track(file=path.name, device=state["devices"][name],
                                    start_epoch=state["epochs"][name], samples=int(len(samples)),
                                    silent=silent)
    meta = bundle.BundleMeta(
        name=bundle_dir.name, slug=state.get("slug"), host=socket.gethostname(), platform=sys.platform,
        recorder={"package": "crunchlog-linux-pw-record", "version": __version__},
        created_at=state["created_at"], stopped_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        speakers=state.get("speakers"), tracks=tracks, damaged=bool(reasons), damage_reasons=tuple(reasons))
    bundle.write_meta(bundle_dir, meta)
    STATE.unlink(missing_ok=True)
    print(f"stopped: {bundle_dir}" + (f" (avisos: {', '.join(reasons)})" if reasons else ""))
    if not process:
        return 0
    from crunchlog import cli
    return cli.main(["process", str(bundle_dir)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start")
    p.add_argument("--slug")
    p.add_argument("--speakers", type=int)
    p = sub.add_parser("stop")
    p.add_argument("--no-process", action="store_true")
    p = sub.add_parser("toggle")
    p.add_argument("--slug")
    sub.add_parser("status")
    sub.add_parser("devices")
    args = parser.parse_args()
    if args.cmd == "start":
        return start(args.slug, args.speakers)
    if args.cmd == "stop":
        return stop(not args.no_process)
    if args.cmd == "toggle":
        return stop() if read_state() else start(args.slug, None)
    if args.cmd == "status":
        state = read_state()
        print(f"recording {state['bundle']}" if state else "idle")
        return 0
    far, mic = targets()
    print(f"far (monitor da saída): {far}\nmic (entrada): {mic}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
