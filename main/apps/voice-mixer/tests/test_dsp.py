import numpy as np
import pytest

from conftest import envelope_peak_hz, f0_of, pulse_voice, tone
from voicefx import dsp
from voicefx.audio import SR


@pytest.mark.parametrize("semitones,speed", [(-2.5, 0.94), (-3.5, 0.9), (-12, 1.0), (4, 1.2), (0, 0.7), (-2, 1.4)])
def test_pitch_speed_accuracy(semitones, speed):
    a = tone(220, 3.0)
    y = dsp.pitch_speed(a, semitones, speed)
    want_f = 220 * 2 ** (semitones / 12)
    assert abs(f0_of(y) / want_f - 1) < 0.01, "pitch within 1%"
    want_len = len(a) / speed
    assert abs(len(y) / want_len - 1) < 0.03, "duration within 3%"


@pytest.mark.parametrize("rate", [0.7, 0.94, 1.3])
def test_time_stretch_keeps_pitch(rate):
    a = tone(300, 2.0)
    y = dsp.time_stretch(a, rate)
    assert abs(f0_of(y) / 300 - 1) < 0.01
    assert abs(len(y) / (len(a) / rate) - 1) < 0.03


def test_formant_shift_moves_envelope_not_pitch():
    a = pulse_voice(120, 1000)
    y = dsp.formant_shift(a, 4.0)
    assert abs(f0_of(y, 80, 200) / f0_of(a, 80, 200) - 1) < 0.01
    want = 1000 * 2 ** (4 / 12)
    got = envelope_peak_hz(y)
    assert abs(got / want - 1) < 0.12, (got, want)
    assert len(y) == len(a)


def test_pitch_only_restores_formant():
    a = pulse_voice(150, 1200)
    lowered = dsp.pitch_speed(a, -4, 1.0)
    restored = dsp.formant_shift(lowered, 4.0)
    assert envelope_peak_hz(lowered) < 1050           # resampling moved the formant down
    assert abs(envelope_peak_hz(restored) / 1200 - 1) < 0.12
    assert abs(f0_of(restored, 80, 200) / (150 * 2 ** (-4 / 12)) - 1) < 0.01


def _gain_at(fn, f, *args, **kw):
    a = tone(f, 1.0, 0.1)
    y = fn(a, *args, **kw)
    s = slice(SR // 4, -SR // 4)
    return dsp.db(np.std(y[s]) / np.std(a[s]))


def test_presence_peak_gain():
    assert abs(_gain_at(dsp.presence_boost, 2800, 6.0, f0=2800, q=0.9) - 6.0) < 0.3
    assert abs(_gain_at(dsp.presence_boost, 300, 6.0, f0=2800, q=0.9)) < 0.5


def test_low_boost_db_mapping():
    amt = dsp.low_shelf_db_to_amount(6.0)
    assert abs(_gain_at(dsp.low_boost, 40, amt, fc=250) - 6.0) < 0.3
    assert abs(dsp.amount_to_low_shelf_db(0.45) - 3.23) < 0.01


def test_high_and_low_cut():
    assert _gain_at(dsp.highpass, 50, 400) < -15
    assert _gain_at(dsp.lowpass, 8000, 1000) < -25
    assert abs(_gain_at(dsp.highpass, 3000, 400)) < 0.3


def test_bandpass_rejects_outside_band():
    bp = lambda a: dsp.bandpass(a, 300, 3800, 4)
    assert _gain_at(bp, 100) < -30
    assert _gain_at(bp, 8000) < -30
    assert abs(_gain_at(bp, 1200)) < 0.5


def test_match_highs_restores_treble():
    rng = np.random.default_rng(0)
    ref = rng.normal(0, 0.1, SR).astype(np.float32)
    dull = dsp.lowpass(ref, 1500, order=4)
    out = dsp.match_highs(dull, ref, max_db=9)
    def hf(x):
        s = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / SR)
        return s[f > 2500].sum()
    assert hf(out) > hf(dull) * 4             # boosted ...
    assert hf(out) < hf(dull) * 10 ** (9 / 10) * 1.2   # ... but capped at max_db


def test_compressor_reduces_loud_part_by_ratio():
    a = np.concatenate([tone(440, 1, 0.02), tone(440, 1, 0.8)])   # -37 dB RMS (below) then -5 dB RMS
    y = dsp.compressor(a, threshold_db=-30, ratio=4, attack_ms=1, release_ms=50, knee_db=0)
    quiet_in, loud_in = dsp.rms_db(a[SR // 2: SR - 1000]), dsp.rms_db(a[-SR // 2:])
    quiet_out, loud_out = dsp.rms_db(y[SR // 2: SR - 1000]), dsp.rms_db(y[-SR // 2:])
    assert abs(quiet_out - quiet_in) < 0.5                       # below threshold: untouched
    expect = -30 + (loud_in - -30) / 4
    assert abs(loud_out - expect) < 1.5


def test_limiter_ceiling():
    a = tone(200, 1, 1.4)
    y = dsp.limiter(a, -3.0)
    assert np.max(np.abs(y)) <= dsp.undb(-3.0) + 1e-6


def test_noise_gate_silences_quiet_gap():
    rng = np.random.default_rng(1)
    a = np.concatenate([tone(300, 0.5, 0.5), rng.normal(0, 0.001, SR // 2).astype(np.float32), tone(300, 0.5, 0.5)])
    y = dsp.noise_gate(a, threshold_db=-40)
    gap = slice(int(SR * 0.7), int(SR * 0.9))
    assert dsp.rms_db(y[gap]) < dsp.rms_db(a[gap]) - 30
    assert abs(dsp.rms_db(y[:SR // 4]) - dsp.rms_db(a[:SR // 4])) < 0.5


def test_bit_and_rate_reduction():
    a = tone(300, 0.5, 0.9)
    assert len(np.unique(dsp.bit_reduce(a, 4))) <= 2 ** 4 + 1
    y = dsp.rate_reduce(a, 4000)
    assert len(y) == len(a)
    assert np.mean(np.diff(y) == 0) > 0.7       # sample-and-hold steps
    assert dsp.bit_reduce(a, 16) is a and dsp.rate_reduce(a, SR) is a


def test_noise_colours_have_requested_level():
    rng = np.random.default_rng(0)
    for c in ("white", "pink", "brown"):
        n = dsp.coloured_noise(rng, SR, 0.01, c)
        assert abs(np.std(n) / 0.01 - 1) < 0.05
    pink = dsp.coloured_noise(np.random.default_rng(1), SR * 2, 0.01, "pink")
    s = np.abs(np.fft.rfft(pink)) ** 2; f = np.fft.rfftfreq(len(pink), 1 / SR)
    assert s[(f > 100) & (f < 200)].mean() > 5 * s[(f > 5000) & (f < 6000)].mean()


def test_room_crackle_ring_squelch_shapes():
    a = tone(300, 0.5, 0.5)
    assert len(dsp.room(a, 0.3, 0.3)) == len(a)
    assert np.count_nonzero(dsp.crackle(np.random.default_rng(0), SR, 0.5)) > 0
    assert len(dsp.ring_tremolo(a, 0.5, 200, 0.5, 5)) == len(a)
    tail = dsp.squelch_tail(np.random.default_rng(0), 200, -12)
    assert len(tail) == int(SR * 0.2) and np.max(np.abs(tail)) <= 0.89 * dsp.undb(-12) + 1e-6


def test_trim_and_fade():
    a = np.concatenate([np.zeros(SR), tone(300, 0.5, 0.5), np.zeros(SR)]).astype(np.float32)
    y = dsp.trim_silence(a, -40, 0.08)
    assert abs(len(y) - (SR * 0.5 + 2 * 0.08 * SR)) < 50
    f = dsp.fade(tone(300, 0.5, 0.5), 50, 50)
    assert f[0] == 0 and abs(f[-1]) < 1e-6
