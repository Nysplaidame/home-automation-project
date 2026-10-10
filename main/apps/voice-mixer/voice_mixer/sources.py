"""Source clips: files, Piper TTS, Piper -> RVC, dataset and game clips.

Piper and RVC always run as subprocesses of the configured python, so this process never imports
PyTorch. RVC goes through rvc_cli.py (torch.load allowlist patch for PyTorch >= 2.6).
Synthesised clips are cached on disk by a hash of text + settings.
"""
import csv
import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from voicefx.audio import load

AUDIO_EXT = (".wav", ".flac", ".mp3", ".ogg")


@dataclass
class Availability:
    piper: bool
    piper_msg: str
    rvc: bool
    rvc_msg: str


def _has_module(python, module):
    try:
        r = subprocess.run([python, "-c", f"import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('{module}') else 1)"],
                           capture_output=True, timeout=60)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def check(cfg):
    """Cheap checks (find_spec only; nothing heavy is imported)."""
    py = cfg["python"]
    voice = cfg.p("piper_voice")
    if not Path(py).exists():
        return Availability(False, f"python not found: {py}", False, f"python not found: {py}")
    if not voice or not voice.exists():
        piper, pmsg = False, f"Piper voice not found: {voice}"
    elif not Path(str(voice) + ".json").exists():
        piper, pmsg = False, f"Piper voice config missing: {voice}.json"
    elif not _has_module(py, "piper"):
        piper, pmsg = False, "piper-tts is not installed for the configured python"
    else:
        piper, pmsg = True, f"Piper ready ({voice.name})"
    missing = [k for k in ("rvc_cli", "rvc_model") if not (cfg.p(k) and cfg.p(k).exists())]
    if not piper:
        rvc, rmsg = False, "RVC needs Piper first"
    elif missing:
        rvc, rmsg = False, "RVC disabled, missing: " + ", ".join(f"{k}={cfg.get(k)}" for k in missing)
    elif not _has_module(py, "rvc_python"):
        rvc, rmsg = False, "rvc-python is not installed for the configured python"
    else:
        rvc, rmsg = True, f"RVC ready ({cfg.p('rvc_model').name}, {cfg['rvc_device']})"
    return Availability(piper, pmsg, rvc, rmsg)


def _key(*parts):
    return hashlib.sha1(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


def _run(cmd, timeout):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


def piper_tts(cfg, text, length_scale=1.0):
    """Returns path to a cached 22.05 kHz wav of `text` spoken by the configured Piper voice."""
    text = " ".join(text.split())
    if not text:
        raise ValueError("type some text first")
    voice = str(cfg.p("piper_voice"))
    out = cfg.p("cache_dir") / "piper" / f"{_key(text, voice, round(float(length_scale), 3))}.wav"
    if out.exists() and out.stat().st_size > 1000:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.wav")
    cmd = [cfg["python"], "-m", "piper", "-m", voice, "-f", str(tmp), "--length-scale", str(length_scale), "--", text]
    rc, msg = _run(cmd, 300)
    if rc != 0 or not tmp.exists() or tmp.stat().st_size < 1000:
        raise RuntimeError(f"Piper failed (rc={rc}): {msg[-600:]}")
    os.replace(tmp, out)
    return out


def rvc_convert(cfg, text, length_scale=1.0, pitch=0, protect=0.33, index_rate=0.75, use_index=True):
    """Piper -> RVC; returns path to a cached wav."""
    raw = piper_tts(cfg, text, length_scale)
    model, index = cfg.p("rvc_model"), cfg.p("rvc_index") if use_index else None
    settings = dict(pitch=int(pitch), protect=round(float(protect), 3), index_rate=round(float(index_rate), 3),
                    index=str(index) if index and index.exists() else "", model=str(model),
                    method=cfg["rvc_method"], device=cfg["rvc_device"])
    out = cfg.p("cache_dir") / "rvc" / f"{_key(raw.name, settings)}.wav"
    if out.exists() and out.stat().st_size > 1000:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as td:      # same drive, so os.replace works
        tmp = Path(td) / "rvc.wav"
        cmd = [cfg["python"], str(cfg.p("rvc_cli")), "cli", "-i", str(raw), "-o", str(tmp), "-mp", settings["model"],
               "-de", settings["device"], "-me", settings["method"], "-pi", str(settings["pitch"]),
               "-pr", str(settings["protect"]), "-ir", str(settings["index_rate"])]
        if settings["index"]:
            cmd += ["-ip", settings["index"]]
        rc, msg = _run(cmd, int(cfg.get("rvc_timeout_s", 900)))
        if rc != 0 or not tmp.exists():
            raise RuntimeError(f"RVC failed (rc={rc}): {msg[-1200:]}")
        os.replace(tmp, out)
    return out


def dataset_items(cfg):
    """[(label, path)] from <dataset_dir>/metadata.csv (id|text) and <dataset_dir>/wav/<id>.wav."""
    d = cfg.p("dataset_dir")
    if not d or not (d / "metadata.csv").exists():
        return []
    items = []
    with open(d / "metadata.csv", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="|", quoting=csv.QUOTE_NONE):
            if len(row) >= 2:
                wav = d / "wav" / f"{row[0]}.wav"
                if wav.exists():
                    items.append((f"{row[0]}  {row[1]}", str(wav)))
    return items


def game_items(cfg):
    d = cfg.p("game_clips_dir")
    if not d or not d.exists():
        return []
    return [(p.relative_to(d).as_posix(), str(p)) for p in sorted(d.rglob("*")) if p.suffix.lower() in AUDIO_EXT]


def load_any(path):
    return load(str(path))
