import json
import random
import subprocess
import sys
import time

import numpy as np
import pytest

from conftest import ROOT
from voicefx import params as P
from voicefx.audio import SR, load
from voicefx.pipeline import Pipeline

sys.path.insert(0, f"{ROOT}/tests/legacy")
import radio_fx_v1 as legacy  # noqa: E402  frozen copy of the original voice/tools/radio_fx.py


def legacy_render(path, bleep_dir, preset, seed, filt=True, tmp=None):
    rng = random.Random(seed); nrng = np.random.default_rng(seed)

    class R:
        choice = staticmethod(rng.choice)
        normal = staticmethod(nrng.normal)

    out = str(tmp / "legacy.wav")
    legacy.process(path, out, bleep_dir, R, filt, preset)
    return load(out)


@pytest.mark.parametrize("name", ["none", "deep", "menace"])
def test_matches_original_radio_fx(name, speechlike, bleep_dir, tmp_path):
    path, _ = speechlike
    ref = legacy_render(path, bleep_dir, legacy.PRESETS[name], seed=5, tmp=tmp_path)
    flat = dict(P.BUILTIN[name]); flat["bleeps.seed"] = 5
    out = Pipeline(bleep_dir).render(Pipeline.prepare_source(load(path)), flat).audio
    assert len(out) == len(ref)
    # 16-bit quantisation + bleep/peak levels rounded to 0.01 dB in the schema
    assert np.max(np.abs(out - ref)) < 3e-3


def test_no_filter_matches_original(speechlike, bleep_dir, tmp_path):
    path, _ = speechlike
    ref = legacy_render(path, bleep_dir, legacy.PRESETS["deep"], seed=2, filt=False, tmp=tmp_path)
    flat = dict(P.BUILTIN["deep"]); flat["bleeps.seed"] = 2; flat["radio.on"] = False
    out = Pipeline(bleep_dir).render(Pipeline.prepare_source(load(path)), flat).audio
    assert len(out) == len(ref) and np.max(np.abs(out - ref)) < 3e-3


def test_late_stage_change_skips_slow_stages_and_is_fast(speechlike, bleep_dir):
    _, a = speechlike                                   # 5 s clip
    pl = Pipeline(bleep_dir)
    src = Pipeline.prepare_source(a)
    flat = dict(P.BUILTIN["mid"])
    pl.render(src, flat)
    before = dict(pl.calls)
    worst = 0
    for k, v in [("radio.drive", 2.6), ("bleeps.level_db", -6), ("output.peak_db", -3), ("radio.crackle", 0.3),
                 ("dynamics.comp_on", True), ("eq.presence_db", 5.0), ("radio.room_mix", 0.2)]:
        flat[k] = v
        t = time.perf_counter()
        pl.render(src, flat)
        worst = max(worst, time.perf_counter() - t)
    assert pl.calls["pitch"] == before["pitch"] and pl.calls["formant"] == before["formant"]
    assert worst < 0.3, f"late-stage re-render took {worst * 1000:.0f} ms"


def test_identical_render_is_fully_cached(speechlike, bleep_dir):
    _, a = speechlike
    pl = Pipeline(bleep_dir)
    src = Pipeline.prepare_source(a)
    r1 = pl.render(src, P.BUILTIN["mid"])
    r2 = pl.render(src, P.BUILTIN["mid"])
    assert r2.info["cache_hits"] == [s for s, _, _ in __import__("voicefx.pipeline").pipeline.STAGES]
    assert np.array_equal(r1.audio, r2.audio)


def test_bleep_layout_and_lead(speechlike, bleep_dir):
    _, a = speechlike
    flat = P.complete({"bleeps.on_clip": "on2.wav", "bleeps.off_clip": "off3.wav",
                       "bleeps.gap_pre_ms": 100, "bleeps.gap_post_ms": 200})
    r = Pipeline(bleep_dir).render(Pipeline.prepare_source(a), flat)
    on, off = load(f"{bleep_dir}/on2.wav"), load(f"{bleep_dir}/off3.wav")
    assert r.info["bleeps_used"] == ("on2.wav", "off3.wav")
    assert r.info["lead"] == len(on) + int(SR * 0.1)
    assert len(r.audio) == len(on) + int(SR * 0.1) + r.info["speech_len"] + int(SR * 0.2) + len(off)


def test_rms_mode_and_peak_mode(speechlike, bleep_dir):
    from voicefx import dsp
    _, a = speechlike
    src = Pipeline.prepare_source(a)
    pk = Pipeline(bleep_dir).render(src, {"output.peak_db": -6}).audio
    assert abs(dsp.db(np.max(np.abs(pk))) - -6) < 0.01
    rm = Pipeline(bleep_dir).render(src, {"output.mode": "rms", "output.rms_db": -18, "output.peak_db": -1}).audio
    assert np.max(np.abs(rm)) <= dsp.undb(-1) + 1e-6
    assert abs(dsp.rms_db(rm) - -18) < 1.5


def test_pitch_only_keeps_duration_and_lowers_pitch(bleep_dir):
    from conftest import f0_of, tone
    src = Pipeline.prepare_source(tone(200, 2.0))
    flat = {"pitch.semitones": -3, "pitch.method": "pitch_only", "bleeps.on": False, "radio.on": False}
    out = Pipeline(bleep_dir).render(src, flat).audio
    assert abs(len(out) / len(src) - 1) < 0.03
    assert abs(f0_of(out) / (200 * 2 ** (-3 / 12)) - 1) < 0.01


def test_presets_roundtrip_and_shipped_files_match_builtin(tmp_path):
    for name, flat in P.BUILTIN.items():
        f = tmp_path / f"{name}.json"
        P.save_preset(f, name, flat)
        back, doc, warnings = P.load_preset(f)
        assert back == flat and not warnings and doc["schema"] == P.SCHEMA
        shipped, _, w = P.load_preset(f"{ROOT}/presets/{name}.json")
        assert shipped == flat and not w, name


def test_preset_tolerates_missing_and_unknown_keys():
    doc = {"schema": P.SCHEMA, "params": {"pitch": {"semitones": -1}, "future": {"thing": 1}}}
    flat, _, warnings = P.load_preset(doc)
    assert flat["pitch.semitones"] == -1 and flat["radio.drive"] == 1.6
    assert any("future.thing" in w for w in warnings)


def test_legacy_mapping_roundtrip():
    leg, unsupported = P.to_legacy(P.BUILTIN["mid"])
    assert leg == {**P.LEGACY_PRESETS["mid"], "lowboost": 0.45} and unsupported == []
    _, unsupported = P.to_legacy({**P.BUILTIN["mid"], "radio.crackle": 0.2})
    assert unsupported == ["radio.crackle"]


def _cli(*args):
    return subprocess.run([sys.executable, "-m", "voicefx", *args], cwd=ROOT, capture_output=True, text=True)


def test_cli_legacy_flags_and_preset_file(speechlike, bleep_dir, tmp_path):
    path, _ = speechlike
    out1, out2 = tmp_path / "a.wav", tmp_path / "b.wav"
    r = _cli(path, str(out1), "--bleeps", bleep_dir, "--seed", "4", "--preset", "mid")
    assert r.returncode == 0, r.stderr
    pf = tmp_path / "p.json"
    P.save_preset(pf, "mid-copy", P.BUILTIN["mid"])
    r = _cli(path, str(out2), "--bleeps", bleep_dir, "--seed", "4", "--preset-file", str(pf))
    assert r.returncode == 0, r.stderr
    assert np.array_equal(load(str(out1)), load(str(out2)))
    ref = legacy_render(path, bleep_dir, {**legacy.PRESETS["deep"], "semitones": -2.5}, seed=4, tmp=tmp_path)
    r = _cli(path, str(out1), "--bleeps", bleep_dir, "--seed", "4", "--preset", "deep", "--semitones", "-2.5")
    assert r.returncode == 0, r.stderr
    assert np.max(np.abs(load(str(out1)) - ref)) < 3e-3


def test_cli_set_and_directory_mode(speechlike, bleep_dir, tmp_path):
    path, _ = speechlike
    out = tmp_path / "outdir"
    r = _cli(str(tmp_path), str(out), "--bleeps", bleep_dir, "--seed", "1", "--set", "radio.crackle=0.3",
             "--set", "bleeps.on=false", "--sr44")
    assert r.returncode == 0, r.stderr
    import wave
    with wave.open(str(out / "speech.wav")) as w:
        assert w.getframerate() == 44100
    r = _cli(path, str(tmp_path / "x.wav"), "--bleeps", bleep_dir, "--set", "nope=1")
    assert r.returncode != 0 and "unknown parameter" in r.stderr + r.stdout
