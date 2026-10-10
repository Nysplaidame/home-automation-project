"""config.json: the only place host-specific paths live.

Location: $VOICE_MIXER_CONFIG, else <app>/config.json. Created with defaults on first run.
Relative paths are resolved against the config file's folder. VOICE_MIXER_HOST / VOICE_MIXER_PORT
override host/port (the container uses them to listen on its own network namespace).
"""
import json
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
_VOICE = "K:/Documents/Obsidian/voice"   # desktop defaults; edit config.json rather than this

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 7860,
    "python": sys.executable,
    "piper_voice": f"{_VOICE}/tools/en_GB-alba-medium.onnx",
    "piper_length_scale": 1.0,
    "rvc_cli": f"{_VOICE}/tools/rvc_cli.py",
    "rvc_model": f"{_VOICE}/models/combine_soldierv2.pth",
    "rvc_index": f"{_VOICE}/models/added_IVF292_Flat_nprobe_1_combine_s2_v2.index",
    "rvc_device": "cuda:0",
    "rvc_method": "rmvpe",
    "rvc_timeout_s": 900,
    "bleep_dir": f"{_VOICE}/Combine/metropolice/vo",
    "game_clips_dir": f"{_VOICE}/Combine/metropolice/vo",
    "dataset_dir": f"{_VOICE}/tools/dataset",
    "presets_dir": "presets",
    "cache_dir": "cache",
    "output_dir": "outputs",
    "batch_roots": [],
}
PATH_KEYS = ("piper_voice", "rvc_cli", "rvc_model", "rvc_index", "bleep_dir", "game_clips_dir",
             "dataset_dir", "presets_dir", "cache_dir", "output_dir")


class Config(dict):
    path: Path

    def p(self, key):
        """Resolved Path for a path-valued key ('' -> None)."""
        v = self.get(key)
        if not v:
            return None
        q = Path(os.path.expandvars(os.path.expanduser(v)))
        return q if q.is_absolute() else (self.path.parent / q).resolve()


def load_config(path=None):
    path = Path(path or os.environ.get("VOICE_MIXER_CONFIG") or APP_DIR / "config.json")
    data = dict(DEFAULTS)
    created = False
    if path.exists():
        data.update(json.loads(path.read_text(encoding="utf-8")))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(DEFAULTS, indent=2) + "\n", encoding="utf-8")
        created = True
    if os.environ.get("VOICE_MIXER_HOST"):
        data["host"] = os.environ["VOICE_MIXER_HOST"]
    if os.environ.get("VOICE_MIXER_PORT"):
        data["port"] = int(os.environ["VOICE_MIXER_PORT"])
    cfg = Config(data)
    cfg.path = path
    cfg.created = created
    for k in ("cache_dir", "output_dir", "presets_dir"):
        cfg.p(k).mkdir(parents=True, exist_ok=True)
    return cfg
