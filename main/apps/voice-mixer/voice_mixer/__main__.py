"""python -m voice_mixer [--config path] [--host 127.0.0.1] [--port 7860]"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # make voicefx importable


def main():
    ap = argparse.ArgumentParser(description="Voice Mixer: tune the Metrocop radio voice post-processing.")
    ap.add_argument("--config", help="config.json path (default: $VOICE_MIXER_CONFIG or <app>/config.json)")
    ap.add_argument("--host"); ap.add_argument("--port", type=int)
    a = ap.parse_args()
    from voice_mixer.config import load_config
    cfg = load_config(a.config)
    if a.host:
        cfg["host"] = a.host
    if a.port:
        cfg["port"] = a.port
    from voice_mixer.ui import build
    demo, launch = build(cfg)
    print(f"[voice-mixer] config {cfg.path}; serving http://{cfg['host']}:{cfg['port']}/")
    demo.queue(default_concurrency_limit=2).launch(**launch)


if __name__ == "__main__":
    main()
