"""voicefx: Combine/Metrocop radio voice post-processing (refactored from radio_fx.py).

Library use (e.g. a future Wyoming wrapper):

    from voicefx import Pipeline, load_preset
    params, _, _ = load_preset("presets/mid.json")
    out = Pipeline(bleep_dir).render(Pipeline.prepare_source(audio_22050_mono), params).audio
"""
from .audio import SR, load, save, to_wav_bytes
from .params import BUILTIN, PARAMS, complete, defaults, load_preset, save_preset
from .pipeline import Pipeline, Render, render_file

__all__ = ["SR", "load", "save", "to_wav_bytes", "BUILTIN", "PARAMS", "complete", "defaults",
           "load_preset", "save_preset", "Pipeline", "Render", "render_file"]
