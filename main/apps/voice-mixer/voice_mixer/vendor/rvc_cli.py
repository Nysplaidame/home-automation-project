#!/usr/bin/env python3
"""Run `python -m rvc_python cli ...` with a narrow fix for PyTorch >= 2.6.

Why: PyTorch 2.6 made torch.load refuse old pickled checkpoints unless each class inside is
allowlisted ("Unsupported global: fairseq.data.dictionary.Dictionary"). rvc-python's HuBERT
model hits this. Instead of switching the safety check off globally, this wrapper allowlists
only the classes the load asks for, and only from fairseq / omegaconf / a few stdlib modules.
Every class it allows is printed to stderr. Anything else still fails as before.

Usage is identical to rvc_python's CLI:
  python rvc_cli.py cli -i in.wav -o out.wav -mp model.pth -ip model.index -de cuda:0
"""
import importlib, re, runpy, sys

ALLOWED_PREFIXES = ("fairseq.", "omegaconf.", "argparse.", "collections.", "typing.", "pathlib.", "numpy.")
PAT = re.compile(r"GLOBAL\s+([\w\.]+)\s+was not an allowed global")


def install_patch():
    try:
        import torch
    except ImportError:
        print("[rvc_cli] torch not importable; running without patch", file=sys.stderr)
        return
    orig = torch.load

    def load(*a, **k):
        for _ in range(40):
            f = a[0] if a else k.get("f")
            pos = f.tell() if hasattr(f, "tell") else None
            try:
                return orig(*a, **k)
            except Exception as e:                      # pickle.UnpicklingError
                m = PAT.search(str(e))
                if not m or not m.group(1).startswith(ALLOWED_PREFIXES):
                    raise
                name = m.group(1)
                mod, _, attr = name.rpartition(".")
                obj = getattr(importlib.import_module(mod), attr)
                torch.serialization.add_safe_globals([obj])
                print(f"[rvc_cli] allowlisted {name}", file=sys.stderr)
                if pos is not None:
                    f.seek(pos)
        raise RuntimeError("too many unsupported globals; giving up")

    torch.load = load


if __name__ == "__main__":
    install_patch()
    sys.argv = ["rvc_python"] + sys.argv[1:]
    runpy.run_module("rvc_python", run_name="__main__")
