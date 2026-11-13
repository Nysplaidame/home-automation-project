#!/usr/bin/env python3
"""radio_fx.py compatibility entry point backed by the voicefx library.

Same flags as the original voice/tools/radio_fx.py, plus --preset-file and --set (see voicefx/cli.py).
The original helpers (load, save, SR, pitch_speed, ...) are re-exported so `from radio_fx import ...`
keeps working for scripts such as gen_data.py.
"""
from voicefx.audio import SR, load, save  # noqa: F401
from voicefx.dsp import (low_boost, match_highs, normalise, pitch_speed, presence_boost,  # noqa: F401
                         radio_filter, time_stretch, wrap)
from voicefx.params import LEGACY_PRESETS as PRESETS, OFF_CLIPS as OFF, ON_CLIPS as ON  # noqa: F401
from voicefx.cli import main

if __name__ == "__main__":
    main()
