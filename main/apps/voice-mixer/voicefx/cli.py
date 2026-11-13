"""Command line, flag-compatible with the original radio_fx.py plus --preset-file and --set.

  python -m voicefx speech.wav out.wav --bleeps <dir> [--seed 1] [--preset mid]
  python -m voicefx in_dir out_dir --bleeps <dir> --preset-file presets/mid.json
  python -m voicefx in.wav out.wav --bleeps <dir> --preset mid --set radio.crackle=0.2 --set output.mode=rms

Precedence: --preset (built-in) < --preset-file < legacy flags (--semitones ...) < --set.
"""
import argparse
import os
import random

from . import params as P
from .audio import load, save
from .pipeline import Pipeline


def parse_set(items):
    flat = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--set expects key=value, got {item!r}")
        k, v = item.split("=", 1)
        k = k.strip()
        if k not in P.BY_KEY:
            raise SystemExit(f"--set: unknown parameter {k!r}. Known: {', '.join(P.KEYS)}")
        if P.BY_KEY[k].kind == "bool":
            v = v.strip().lower() in ("1", "true", "yes", "on")
        flat[k] = P.coerce(k, v)
    return flat


def build_params(a):
    flat = dict(P.BUILTIN[a.preset])
    if a.preset_file:
        loaded, _, warnings = P.load_preset(a.preset_file)
        for w in warnings:
            print(f"[voicefx] {a.preset_file}: {w}")
        flat.update(loaded)
    legacy = {k: getattr(a, k) for k in ("semitones", "speed", "lowcut", "lowboost", "drive", "hf_db", "presence")}
    flat.update(P.from_legacy(legacy, no_filter=a.no_filter))
    flat.update(parse_set(a.set))
    # Like radio_fx.py: no --seed means a fresh random bleep choice and noise each run.
    flat["bleeps.seed"] = a.seed if a.seed is not None else random.randrange(10000)
    return P.complete(flat)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--bleeps", required=True, help="folder holding on1/on2/off1-4 wavs")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--no-filter", action="store_true")
    p.add_argument("--preset", choices=list(P.BUILTIN), default="none")
    p.add_argument("--preset-file", help="preset JSON saved by the Voice Mixer (voicefx.preset/1)")
    p.add_argument("--semitones", type=float, help="override preset pitch (negative = deeper)")
    p.add_argument("--speed", type=float, help="override preset speed (<1 slower)")
    p.add_argument("--hf-db", dest="hf_db", type=float); p.add_argument("--presence", type=float); p.add_argument("--lowcut", type=float); p.add_argument("--lowboost", type=float); p.add_argument("--drive", type=float)
    p.add_argument("--set", action="append", metavar="KEY=VALUE", help="any mixer parameter, e.g. radio.crackle=0.2")
    p.add_argument("--sr44", action="store_true", help="write 44.1 kHz instead of 22.05 kHz")
    a = p.parse_args(argv)
    flat = build_params(a)
    pl = Pipeline(a.bleeps)
    out_sr = 44100 if a.sr44 else None

    def one(src, dst):
        r = pl.render(Pipeline.prepare_source(load(src)), flat)
        save(dst, r.audio, out_sr=out_sr)

    if os.path.isdir(a.src):
        os.makedirs(a.dst, exist_ok=True)
        for f in sorted(os.listdir(a.src)):
            if f.lower().endswith(".wav"):
                one(os.path.join(a.src, f), os.path.join(a.dst, f))
    else:
        one(a.src, a.dst)


if __name__ == "__main__":
    main()
