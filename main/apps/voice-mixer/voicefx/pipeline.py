"""Staged render with per-stage caching.

source -> pitch/speed -> formant -> EQ -> dynamics -> radio -> bleeps -> output

Each stage's output is cached under a key made from the previous stage's key plus only the
parameters that stage reads, so moving a late-stage slider never recomputes WSOLA.
"""
import hashlib
import json
import os
import random
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np

from . import dsp
from .audio import SR, load
from .params import OFF_CLIPS, ON_CLIPS, complete

INPUT_PEAK = 0.89     # sources are peak-normalised first (as radio_fx.py did) so drive behaves consistently
SPEECH_PEAK = 0.89


def audio_key(a):
    return hashlib.sha1(np.ascontiguousarray(a, np.float32).tobytes()).hexdigest()[:16]


def _k(prev, name, params):
    blob = json.dumps([prev, name, params], sort_keys=True, default=str)
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


class LRU:
    def __init__(self, size=24):
        self.size, self.d, self.lock = size, OrderedDict(), threading.Lock()

    def get(self, k):
        with self.lock:
            if k in self.d:
                self.d.move_to_end(k)
                return self.d[k]
        return None

    def put(self, k, v):
        with self.lock:
            self.d[k] = v
            self.d.move_to_end(k)
            while len(self.d) > self.size:
                self.d.popitem(last=False)


_bleep_cache = {}


def load_bleep(bleep_dir, name):
    path = os.path.join(bleep_dir, name)
    st = os.stat(path)
    key = (path, st.st_mtime_ns)
    if key not in _bleep_cache:
        _bleep_cache[key] = load(path)
    return _bleep_cache[key]


def _sub(p, *prefixes):
    return {k: v for k, v in p.items() if k.split(".", 1)[0] in prefixes}


def formant_move(p):
    """Net downward/upward movement of formants, used to decide whether treble restore applies."""
    return (p["pitch.semitones"] if p["pitch.method"] == "resample" else 0.0) + p["formant.shift_st"]


# ---- stage functions: (audio, params, ctx) -> audio ----

def st_pitch(a, p, ctx):
    return dsp.pitch_speed(a, p["pitch.semitones"], p["pitch.speed"])


def st_formant(a, p, ctx):
    shift = p["formant.shift_st"]
    if p["pitch.method"] == "pitch_only":
        shift -= p["pitch.semitones"]          # undo the formant move that resampling caused
    return dsp.formant_shift(a, shift)


def st_eq(a, p, ctx):
    if p["eq.treble_db"] > 0 and formant_move(p) < 0:
        a = dsp.match_highs(a, ctx["source"], f_lo=p["eq.treble_from_hz"], max_db=p["eq.treble_db"])
    a = dsp.presence_boost(a, p["eq.presence_db"], f0=p["eq.presence_hz"], q=p["eq.presence_q"])
    a = dsp.low_boost(a, dsp.low_shelf_db_to_amount(p["eq.low_db"]), fc=p["eq.low_hz"])
    for b in ("b1", "b2", "b3"):
        a = dsp.peaking(a, p[f"eq.{b}_db"], p[f"eq.{b}_hz"], p[f"eq.{b}_q"])
    a = dsp.highpass(a, p["eq.hp_hz"])
    a = dsp.lowpass(a, p["eq.lp_hz"])
    return a


def st_dynamics(a, p, ctx):
    a = dsp.noise_gate(a, p["dynamics.gate_db"])
    if p["dynamics.comp_on"]:
        a = dsp.compressor(a, p["dynamics.comp_threshold_db"], p["dynamics.comp_ratio"],
                           p["dynamics.comp_attack_ms"], p["dynamics.comp_release_ms"], p["dynamics.comp_makeup_db"])
    if p["dynamics.limiter_db"] < 0:
        a = dsp.limiter(a, p["dynamics.limiter_db"])
    return a


def radio_chain(a, p, seed, with_noise=True):
    """The radio character, in the original order: band-pass -> soft clip -> noise, then extras."""
    a = dsp.bandpass(a, p["radio.band_low"], p["radio.band_high"], p["radio.band_order"])
    d = p["radio.drive"]
    a = np.tanh(a * d) / np.tanh(d)
    if with_noise and p["radio.noise"]:
        nrng = np.random.default_rng(seed)            # first draw = the radio_fx.py noise stream
        a = a + dsp.coloured_noise(nrng, len(a), p["radio.noise"], p["radio.noise_colour"])
    a = a.astype(np.float32)
    a = dsp.bit_reduce(a, p["radio.bits"])
    a = dsp.rate_reduce(a, p["radio.rate_hz"])
    a = dsp.ring_tremolo(a, p["radio.ring_mix"], p["radio.ring_hz"], p["radio.trem_depth"], p["radio.trem_hz"])
    if with_noise and p["radio.crackle"] > 0:
        a = a + dsp.crackle(np.random.default_rng(seed + 1), len(a), p["radio.crackle"])
    a = dsp.room(a, p["radio.room_mix"], p["radio.room_s"], seed)
    return a.astype(np.float32)


def st_radio(a, p, ctx):
    seed = p["bleeps.seed"]
    if p["radio.on"]:
        a = radio_chain(a, p, seed)
    a = dsp.normalise(a, SPEECH_PEAK).astype(np.float32)
    ctx["speech_len"] = len(a)
    if p["radio.on"] and p["radio.squelch_ms"] > 0:
        tail = dsp.squelch_tail(np.random.default_rng(seed + 2), p["radio.squelch_ms"], p["radio.squelch_db"],
                                p["radio.band_low"], p["radio.band_high"])
        a = np.concatenate([a, tail])
    return a


def pick_bleeps(p):
    r = random.Random(p["bleeps.seed"])
    on, off = r.choice(ON_CLIPS), r.choice(OFF_CLIPS)  # always draw both so 'random' stays stable
    if p["bleeps.on_clip"] != "random":
        on = p["bleeps.on_clip"]
    if p["bleeps.off_clip"] != "random":
        off = p["bleeps.off_clip"]
    return on, off


def _prep_bleep(b, p, peak):
    b = dsp.resample_pitch(b, p["bleeps.pitch_st"])
    if abs(p["bleeps.speed"] - 1) > 1e-3:
        b = dsp.time_stretch(b, p["bleeps.speed"])
    if p["bleeps.radio"] and p["radio.on"]:
        b = radio_chain(b, p, p["bleeps.seed"], with_noise=False)
    return dsp.normalise(b, peak).astype(np.float32)


def st_bleeps(a, p, ctx):
    speech_len = ctx.get("speech_len", len(a))
    lead_trim = 0
    if p["output.trim"]:
        # trim the speech part only; keep any squelch tail attached
        sp, tail = a[:speech_len], a[speech_len:]
        idx = np.where(np.abs(sp) > float(dsp.undb(p["output.trim_db"])))[0]
        if len(idx):
            pad = int(0.08 * SR)
            s, e = max(0, idx[0] - pad), min(len(sp), idx[-1] + pad)
            lead_trim = s
            sp = sp[s:e]
            speech_len = len(sp)
            a = np.concatenate([sp, tail])
    ctx["speech_len"] = speech_len
    ctx["lead_trim"] = lead_trim
    if not p["bleeps.on"] or not ctx.get("bleep_dir"):
        ctx["lead"] = 0
        return a
    on_name, off_name = pick_bleeps(p)
    peak = SPEECH_PEAK * float(dsp.undb(p["bleeps.level_db"]))
    on = _prep_bleep(load_bleep(ctx["bleep_dir"], on_name), p, peak)
    off = _prep_bleep(load_bleep(ctx["bleep_dir"], off_name), p, peak)
    pre, post = p["bleeps.gap_pre_ms"] / 1000, p["bleeps.gap_post_ms"] / 1000
    ctx["lead"] = len(on) + int(SR * pre)
    ctx["bleeps_used"] = (on_name, off_name)
    return dsp.wrap(a, on, off, pre, post)


def st_output(a, p, ctx):
    if p["output.mode"] == "rms":
        a = a * float(dsp.undb(p["output.rms_db"] - dsp.rms_db(a)))
        a = dsp.limiter(a.astype(np.float32), min(p["output.peak_db"], -0.1))
    else:
        a = dsp.normalise(a, float(dsp.undb(p["output.peak_db"])))
    return dsp.fade(np.asarray(a, np.float32), p["output.fade_in_ms"], p["output.fade_out_ms"])


STAGES = [  # name, function, param groups it reads
    ("pitch", st_pitch, ("pitch",)),
    ("formant", st_formant, ("pitch", "formant")),
    ("eq", st_eq, ("pitch", "formant", "eq")),
    ("dynamics", st_dynamics, ("dynamics",)),
    ("radio", st_radio, ("radio", "bleeps.seed")),
    ("bleeps", st_bleeps, ("bleeps", "radio", "output.trim", "output.trim_db")),
    ("output", st_output, ("output",)),
]
CTX_KEYS = ("speech_len", "lead", "lead_trim", "bleeps_used")


def _stage_params(p, groups):
    out = {}
    for g in groups:
        if "." in g:
            out[g] = p[g]
        else:
            out.update(_sub(p, g))
    return out


@dataclass
class Render:
    audio: np.ndarray
    source: np.ndarray
    info: dict = field(default_factory=dict)


class Pipeline:
    def __init__(self, bleep_dir=None, cache_size=24):
        self.bleep_dir = bleep_dir
        self.cache = {name: LRU(cache_size) for name, _, _ in STAGES}
        self.calls = {name: 0 for name, _, _ in STAGES}   # stage executions (for tests/diagnostics)

    @staticmethod
    def prepare_source(a):
        return dsp.normalise(np.asarray(a, np.float32), INPUT_PEAK).astype(np.float32)

    def render(self, source, params, source_key=None):
        """`source` must already be prepared (prepare_source). Returns Render."""
        p = complete(params)
        key = source_key or audio_key(source)
        ctx = {"source": source, "bleep_dir": self.bleep_dir}
        a, timings, hits = source, {}, []
        for name, fn, groups in STAGES:
            sp = _stage_params(p, groups)
            if name == "bleeps":
                sp["_bleep_dir"] = self.bleep_dir
            key = _k(key, name, sp)
            cached = self.cache[name].get(key)
            if cached is not None:
                a, saved = cached
                ctx.update(saved)
                hits.append(name)
                continue
            t = time.perf_counter()
            a = fn(a, p, ctx)
            self.calls[name] += 1
            timings[name] = round((time.perf_counter() - t) * 1000, 1)
            self.cache[name].put(key, (a, {k: ctx[k] for k in CTX_KEYS if k in ctx}))
        info = {k: ctx.get(k) for k in CTX_KEYS}
        info.update(timings_ms=timings, cache_hits=hits, key=key)
        return Render(audio=a, source=source, info=info)


def render_file(src_path, params, bleep_dir, pipeline=None):
    pl = pipeline or Pipeline(bleep_dir)
    return pl.render(Pipeline.prepare_source(load(src_path)), params)
