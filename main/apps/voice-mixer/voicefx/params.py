"""Parameter schema and preset JSON format.

Preset files are nested by pipeline stage so a future Wyoming wrapper can read them without the UI:

    {
      "schema": "voicefx.preset/1",
      "name": "mid",
      "description": "...",
      "params": {"pitch": {"semitones": -2.5, ...}, "eq": {...}, ...}
    }

Missing keys fall back to defaults (older presets keep loading); unknown keys are reported and ignored.
Bleep clips are stored by file name, never by path; the bleep folder comes from the host config.
"""
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA = "voicefx.preset/1"
ON_CLIPS = ["on1.wav", "on2.wav"]
OFF_CLIPS = ["off1.wav", "off2.wav", "off3.wav", "off4.wav"]


@dataclass(frozen=True)
class P:
    key: str            # "stage.name"
    label: str
    default: object
    lo: float = None
    hi: float = None
    step: float = None
    info: str = ""
    kind: str = "float"  # float | int | bool | choice
    choices: tuple = field(default_factory=tuple)


GROUPS = {
    "pitch": "Pitch / Speed",
    "formant": "Formant",
    "eq": "Tone / EQ",
    "dynamics": "Dynamics",
    "radio": "Radio character",
    "bleeps": "Bleeps",
    "output": "Output",
}

PARAMS = [
    # --- pitch / speed (the slow WSOLA stage) ---
    P("pitch.semitones", "Pitch (semitones)", 0.0, -12, 6, 0.1, "Negative = deeper."),
    P("pitch.speed", "Speed", 1.0, 0.6, 1.5, 0.01, "<1 slower, >1 faster. Duration = original / speed."),
    P("pitch.method", "Pitch method", "resample", kind="choice",
      choices=(("resample (moves formants)", "resample"), ("pitch only (keeps formants)", "pitch_only")),
      info="Resample also lowers the formants (bigger, heavier speaker). Pitch only restores them with a cepstral formant shift."),
    # --- formant ---
    P("formant.shift_st", "Formant shift (semitones)", 0.0, -6, 6, 0.1,
      "Moves vocal-tract resonances without changing pitch. Negative = larger head/chest."),
    # --- tone / EQ ---
    P("eq.treble_db", "Treble restore max (dB)", 9.0, 0, 18, 0.5,
      "match_highs: pulls the spectrum above 'from' back toward the source after lowering pitch/formants. Only active when they move down."),
    P("eq.treble_from_hz", "Treble restore from (Hz)", 800.0, 200, 3000, 50, "Lower edge of the treble restore."),
    P("eq.presence_db", "Presence peak (dB)", 0.0, -6, 12, 0.5, "Peaking EQ for intelligibility."),
    P("eq.presence_hz", "Presence freq (Hz)", 2800.0, 1000, 6000, 50, ""),
    P("eq.presence_q", "Presence Q", 0.9, 0.3, 4, 0.05, "Higher = narrower."),
    P("eq.low_db", "Low boost (dB)", 0.0, 0, 12, 0.1, "Adds a low-passed copy (legacy --lowboost 0.45 = 3.2 dB)."),
    P("eq.low_hz", "Low boost corner (Hz)", 250.0, 60, 600, 5, ""),
    P("eq.hp_hz", "Low cut (Hz)", 0.0, 0, 1000, 10, "Gentle 12 dB/oct high-pass before the radio. 0 = off."),
    P("eq.lp_hz", "High cut (Hz)", 0.0, 0, 11000, 100, "Gentle 12 dB/oct low-pass. 0 = off."),
    P("eq.b1_db", "EQ band 1 gain (dB)", 0.0, -12, 12, 0.5, ""),
    P("eq.b1_hz", "EQ band 1 freq (Hz)", 250.0, 60, 1000, 10, ""),
    P("eq.b1_q", "EQ band 1 Q", 1.0, 0.3, 6, 0.05, ""),
    P("eq.b2_db", "EQ band 2 gain (dB)", 0.0, -12, 12, 0.5, ""),
    P("eq.b2_hz", "EQ band 2 freq (Hz)", 1000.0, 300, 4000, 10, ""),
    P("eq.b2_q", "EQ band 2 Q", 1.0, 0.3, 6, 0.05, ""),
    P("eq.b3_db", "EQ band 3 gain (dB)", 0.0, -12, 12, 0.5, ""),
    P("eq.b3_hz", "EQ band 3 freq (Hz)", 4000.0, 1500, 10000, 50, ""),
    P("eq.b3_q", "EQ band 3 Q", 1.0, 0.3, 6, 0.05, ""),
    # --- dynamics ---
    P("dynamics.gate_db", "Noise gate threshold (dB)", -90.0, -90, -20, 1, "Silences quiet gaps. -90 = off."),
    P("dynamics.comp_on", "Compressor", False, kind="bool", info="Evens out loud/quiet words before the drive stage."),
    P("dynamics.comp_threshold_db", "Comp threshold (dB)", -18.0, -60, 0, 0.5, ""),
    P("dynamics.comp_ratio", "Comp ratio", 3.0, 1, 20, 0.1, ""),
    P("dynamics.comp_attack_ms", "Comp attack (ms)", 5.0, 0.5, 100, 0.5, ""),
    P("dynamics.comp_release_ms", "Comp release (ms)", 120.0, 10, 1000, 5, ""),
    P("dynamics.comp_makeup_db", "Comp makeup (dB)", 0.0, 0, 24, 0.5, "Raises level into the drive stage (more grit)."),
    P("dynamics.limiter_db", "Limiter ceiling (dB)", 0.0, -12, 0, 0.5, "Look-ahead limiter. 0 = off."),
    # --- radio character ---
    P("radio.on", "Radio filter", True, kind="bool", info="Off = legacy --no-filter (clean speech, still normalised)."),
    P("radio.band_low", "Band-pass low (Hz)", 300.0, 50, 1000, 5, "Legacy --lowcut. Lower = fuller."),
    P("radio.band_high", "Band-pass high (Hz)", 3800.0, 1500, 10000, 50, "Radio/telephone top end."),
    P("radio.band_order", "Band-pass order", 4, 1, 8, 1, "Butterworth order (steepness).", kind="int"),
    P("radio.drive", "Drive / saturation", 1.6, 0.1, 6, 0.05, "tanh soft clip. Higher = grittier."),
    P("radio.bits", "Bit depth", 16, 2, 16, 1, "16 = off.", kind="int"),
    P("radio.rate_hz", "Sample-rate reduction (Hz)", 22050, 2000, 22050, 50, "22050 = off.", kind="int"),
    P("radio.noise", "Static level", 0.003, 0, 0.05, 0.0005, "Noise standard deviation (legacy fixed 0.003)."),
    P("radio.noise_colour", "Static colour", "white", kind="choice",
      choices=(("white", "white"), ("pink", "pink"), ("brown", "brown"))),
    P("radio.crackle", "Crackle", 0.0, 0, 1, 0.01, "Sparse clicks and pops."),
    P("radio.ring_mix", "Ring-mod mix", 0.0, 0, 1, 0.01, "Metallic ring modulation."),
    P("radio.ring_hz", "Ring-mod freq (Hz)", 300.0, 20, 2000, 5, ""),
    P("radio.trem_depth", "Tremolo depth", 0.0, 0, 1, 0.01, ""),
    P("radio.trem_hz", "Tremolo rate (Hz)", 6.0, 0.5, 20, 0.1, ""),
    P("radio.room_mix", "Room mix", 0.0, 0, 1, 0.01, "Short reverb. 0 = off."),
    P("radio.room_s", "Room decay (s)", 0.3, 0.05, 1.5, 0.05, ""),
    P("radio.squelch_ms", "Squelch tail (ms)", 0.0, 0, 600, 10, "Noise burst after speech. 0 = off."),
    P("radio.squelch_db", "Squelch level (dB)", -18.0, -40, 0, 0.5, ""),
    # --- bleeps ---
    P("bleeps.on", "Bleeps", True, kind="bool"),
    P("bleeps.on_clip", "Start bleep", "random", kind="choice",
      choices=tuple([("random", "random")] + [(c, c) for c in ON_CLIPS])),
    P("bleeps.off_clip", "End bleep", "random", kind="choice",
      choices=tuple([("random", "random")] + [(c, c) for c in OFF_CLIPS])),
    P("bleeps.seed", "Seed", 1, 0, 9999, 1, "Fixes the random bleep choice and the static noise.", kind="int"),
    P("bleeps.level_db", "Bleep level vs speech (dB)", -2.09, -24, 12, 0.1, "Legacy = -2.09 (0.70 vs 0.89 peak)."),
    P("bleeps.gap_pre_ms", "Gap before speech (ms)", 40.0, 0, 500, 5, ""),
    P("bleeps.gap_post_ms", "Gap after speech (ms)", 60.0, 0, 500, 5, ""),
    P("bleeps.gap_static", "Static in gaps", False, kind="bool",
      info="Fill the bleep gaps with the radio static instead of digital silence (avoids a dropout feel)."),
    P("bleeps.pitch_st", "Bleep pitch (semitones)", 0.0, -12, 12, 0.1, "Varispeed: also changes bleep length."),
    P("bleeps.speed", "Bleep speed", 1.0, 0.5, 2, 0.01, ""),
    P("bleeps.radio", "Radio-filter the bleeps", False, kind="bool"),
    # --- output ---
    P("output.mode", "Loudness mode", "peak", kind="choice",
      choices=(("peak", "peak"), ("RMS (LUFS-ish)", "rms"))),
    P("output.peak_db", "Peak target / ceiling (dB)", -1.01, -12, 0, 0.01, "Legacy = -1.01 dBFS (0.89)."),
    P("output.rms_db", "RMS target (dB)", -20.0, -40, -6, 0.5, "Used in RMS mode; peaks are then limited to the ceiling."),
    P("output.trim", "Trim silence", False, kind="bool", info="Trims leading/trailing silence of the speech before bleeps."),
    P("output.trim_db", "Trim threshold (dB)", -40.0, -60, -20, 1, ""),
    P("output.fade_in_ms", "Fade in (ms)", 0.0, 0, 500, 5, ""),
    P("output.fade_out_ms", "Fade out (ms)", 0.0, 0, 500, 5, ""),
]

BY_KEY = {p.key: p for p in PARAMS}
KEYS = [p.key for p in PARAMS]


def defaults():
    return {p.key: p.default for p in PARAMS}


def coerce(key, value):
    p = BY_KEY[key]
    if p.kind == "bool":
        return bool(value)
    if p.kind == "int":
        return int(round(float(value)))
    if p.kind == "choice":
        allowed = [c[1] for c in p.choices]
        if value not in allowed:
            raise ValueError(f"{key}: {value!r} not in {allowed}")
        return value
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"{key}: not finite")
    return v


def complete(flat):
    """Defaults + given flat params, coerced. Unknown keys raise."""
    out = defaults()
    for k, v in (flat or {}).items():
        if k not in BY_KEY:
            raise KeyError(f"unknown parameter {k!r}")
        out[k] = coerce(k, v)
    return out


def nest(flat):
    out = {}
    for k, v in flat.items():
        stage, name = k.split(".", 1)
        out.setdefault(stage, {})[name] = v
    return out


def flatten(nested):
    return {f"{s}.{n}": v for s, d in (nested or {}).items() for n, v in d.items()}


def diff_from_defaults(flat):
    d = defaults()
    return {k: v for k, v in flat.items() if d.get(k) != v}


# ---- the classic radio_fx.py presets, expressed in the new schema ----

LEGACY_PRESETS = {  # semitones, speed, lowcut Hz, low boost amount, drive, hf_db, presence dB
    "none":   dict(semitones=0.0, speed=1.0,  lowcut=300, lowboost=0.0, drive=1.6, hf_db=9.0, presence=0.0),
    "deep":   dict(semitones=-2.0, speed=0.97, lowcut=220, lowboost=0.35, drive=1.8, hf_db=11.0, presence=2.0),
    "mid":    dict(semitones=-2.5, speed=0.94, lowcut=200, lowboost=0.45, drive=2.0, hf_db=12.0, presence=3.0),
    "menace": dict(semitones=-3.5, speed=0.90, lowcut=190, lowboost=0.6, drive=2.2, hf_db=13.0, presence=3.5),
}
DESCRIPTIONS = {
    "none": "Bleeps and light radio filter only; no pitch change.",
    "deep": "Slightly deeper and slower.",
    "mid": "Current favourite: -2.5 st, 0.94 speed, fuller low end, more drive.",
    "menace": "Deepest and slowest of the classic presets.",
}


def from_legacy(lp, no_filter=False):
    """Map radio_fx.py preset keys/CLI flags onto flat schema params."""
    from .dsp import amount_to_low_shelf_db
    flat = {}
    m = {"semitones": "pitch.semitones", "speed": "pitch.speed", "lowcut": "radio.band_low",
         "drive": "radio.drive", "hf_db": "eq.treble_db", "presence": "eq.presence_db"}
    for k, v in lp.items():
        if v is None:
            continue
        if k == "lowboost":
            flat["eq.low_db"] = round(amount_to_low_shelf_db(v), 2)   # 0.01 dB: tidy in the UI, inaudible
        elif k in m:
            flat[m[k]] = float(v)
    if no_filter:
        flat["radio.on"] = False
    return flat


def to_legacy(flat):
    """Best-effort reverse mapping for 'copy as radio_fx.py flags'. Returns (legacy dict, unsupported keys)."""
    from .dsp import low_shelf_db_to_amount
    full = complete(flat)
    leg = dict(semitones=full["pitch.semitones"], speed=full["pitch.speed"], lowcut=full["radio.band_low"],
               lowboost=round(low_shelf_db_to_amount(full["eq.low_db"]), 2), drive=full["radio.drive"],
               hf_db=full["eq.treble_db"], presence=full["eq.presence_db"])
    covered = {"pitch.semitones", "pitch.speed", "radio.band_low", "eq.low_db", "radio.drive",
               "eq.treble_db", "eq.presence_db", "radio.on", "bleeps.seed"}
    unsupported = [k for k, v in diff_from_defaults(full).items() if k not in covered]
    return leg, unsupported


BUILTIN = {name: complete(from_legacy(lp)) for name, lp in LEGACY_PRESETS.items()}


# ---- preset files ----

def preset_doc(name, flat, description=""):
    return {"schema": SCHEMA, "name": name, "description": description, "params": nest(complete(flat))}


def save_preset(path, name, flat, description=""):
    Path(path).write_text(json.dumps(preset_doc(name, flat, description), indent=2) + "\n", encoding="utf-8")


def load_preset(path_or_doc):
    """Returns (flat params, doc, warnings)."""
    doc = path_or_doc
    if not isinstance(doc, dict):
        doc = json.loads(Path(path_or_doc).read_text(encoding="utf-8"))
    warnings = []
    if doc.get("schema") != SCHEMA:
        warnings.append(f"schema {doc.get('schema')!r} != {SCHEMA!r}; loading anyway")
    flat = {}
    for k, v in flatten(doc.get("params", {})).items():
        if k not in BY_KEY:
            warnings.append(f"ignored unknown parameter {k}")
            continue
        try:
            flat[k] = coerce(k, v)
        except (ValueError, TypeError) as e:
            warnings.append(f"ignored {k}: {e}")
    return complete(flat), doc, warnings
