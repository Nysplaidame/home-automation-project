#!/usr/bin/env python3
"""Wrap speech in Combine-style radio on/off bleeps plus a light radio filter.

Usage:
  python radio_fx.py speech.wav out.wav --bleeps "K:\\...\\Combine\\metropolice\\vo"
  python radio_fx.py in_dir out_dir --bleeps <dir> [--seed 1]
  add --preset deep|menace  (or --semitones -3 --speed 0.9 --lowcut 170 --lowboost 0.9 --drive 2.4)

Needs: numpy, scipy. Reads/writes PCM WAV (8/16-bit in, 16-bit out, 22050 Hz mono).
"""
import argparse, os, random, wave
import numpy as np
from scipy.signal import butter, sosfilt, resample_poly
from math import gcd

SR = 22050
ON = ["on1.wav", "on2.wav"]
OFF = ["off1.wav", "off2.wav", "off3.wav", "off4.wav"]


def load(path):
    with wave.open(path) as w:
        n, sw, ch, sr = w.getnframes(), w.getsampwidth(), w.getnchannels(), w.getframerate()
        raw = w.readframes(n)
    if sw == 1:
        a = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128
    elif sw == 2:
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    else:
        raise ValueError(f"{path}: unsupported sample width {sw}")
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        g = gcd(sr, SR)
        a = resample_poly(a, SR // g, sr // g).astype(np.float32)
    return a


def save(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


PRESETS = {  # semitones (negative = deeper), speed (<1 slower), lowcut Hz, low boost, drive
    "none":   dict(semitones=0.0, speed=1.0,  lowcut=300, lowboost=0.0, drive=1.6, hf_db=9.0, presence=0.0),
    "deep":   dict(semitones=-2.0, speed=0.97, lowcut=220, lowboost=0.35, drive=1.8, hf_db=11.0, presence=2.0),
    "menace": dict(semitones=-3.5, speed=0.90, lowcut=190, lowboost=0.6, drive=2.2, hf_db=13.0, presence=3.5),
}


def time_stretch(a, rate, frame_ms=32, search_ms=10):
    """WSOLA time stretch (time-domain, no phase vocoder 'echo'). rate>1 = faster/shorter.
    Pitch is unchanged. Works well for speech at rates roughly 0.7-1.4."""
    if abs(rate - 1.0) < 1e-3:
        return a
    N = int(SR * frame_ms / 1000) // 2 * 2
    Hs = N // 2                                   # synthesis hop (50% overlap)
    Ha = Hs * rate                                # analysis hop
    T = int(SR * search_ms / 1000)
    if len(a) < N + 2 * T + Hs:
        return a
    win = np.hanning(N + 1)[:N].astype(np.float32)   # periodic Hann: overlaps sum to 1 at 50%
    n_out = int((len(a) - N - T) / Ha)
    y = np.zeros(n_out * Hs + N, np.float32)
    pos = 0
    y[:N] += a[:N] * win
    for k in range(1, n_out):
        target = int(round(k * Ha))
        ref = a[pos + Hs: pos + Hs + N]               # what naturally followed the last frame
        lo, hi = max(0, target - T), min(len(a) - N, target + T)
        if hi <= lo or len(ref) < N:
            pos = min(target, len(a) - N)
        else:
            cand = np.lib.stride_tricks.sliding_window_view(a[lo:hi + N], N)[: hi - lo + 1]
            pos = lo + int(np.argmax(cand @ ref))
        y[k * Hs:k * Hs + N] += a[pos:pos + N] * win
    return y


def match_highs(a, ref, f_lo=800.0, max_db=9.0):
    """Restore treble lost by pitch lowering: long-term spectrum above f_lo is pulled back toward ref (capped boost)."""
    n = 1 << int(np.ceil(np.log2(max(len(a), len(ref)))))
    fa = np.abs(np.fft.rfft(a, n)); fr = np.abs(np.fft.rfft(ref, n))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    edges = np.geomspace(f_lo, SR / 2 - 100, 14)
    g = np.ones_like(freqs)
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (freqs >= lo) & (freqs < hi)
        ea, er = np.sqrt(np.mean(fa[m] ** 2)) + 1e-9, np.sqrt(np.mean(fr[m] ** 2)) + 1e-9
        g[m] = np.clip(er / ea, 1.0, 10 ** (max_db / 20))
    k = max(3, len(freqs) // 400)
    g = np.convolve(g, np.ones(k) / k, mode="same")        # smooth the gain curve
    out = np.fft.irfft(np.fft.rfft(a, n) * g, n)[: len(a)]
    return out.astype(np.float32)


def pitch_speed(a, semitones=0.0, speed=1.0):
    """Lower/raise pitch by resampling (this also moves the formants, so negative values sound
    like a bigger, heavier speaker), then ONE WSOLA pass so the final duration = original / speed."""
    r = 2 ** (semitones / 12.0) if semitones else 1.0
    if semitones:
        g = gcd(int(round(r * 1000)), 1000)
        a = resample_poly(a, 1000 // g, int(round(r * 1000)) // g).astype(np.float32)  # pitch*r, length/r
    return time_stretch(a, speed / r)


def presence_boost(a, gain_db, f0=2800.0, q=0.9):
    """RBJ peaking EQ around f0: adds intelligibility ('clarity') to a dull voice."""
    if not gain_db:
        return a
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A]); aa = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    from scipy.signal import lfilter
    return lfilter(b / aa[0], aa / aa[0], a).astype(np.float32)


def low_boost(a, gain, fc=250):
    if not gain:
        return a
    sos = butter(2, fc, btype="low", fs=SR, output="sos")
    return (a + gain * sosfilt(sos, a)).astype(np.float32)


def radio_filter(a, drive=1.6, noise=0.003, rng=None, lowcut=300):
    sos = butter(4, [lowcut, 3800], btype="band", fs=SR, output="sos")
    a = sosfilt(sos, a)
    a = np.tanh(a * drive) / np.tanh(drive)          # soft clip
    if rng is not None and noise:
        a = a + rng.normal(0, noise, a.shape).astype(np.float32)
    return a.astype(np.float32)


def normalise(a, peak=0.89):
    m = float(np.max(np.abs(a))) or 1.0
    return a * (peak / m)


def wrap(speech, on, off, gap_pre=0.04, gap_post=0.06):
    z = lambda s: np.zeros(int(SR * s), np.float32)
    return np.concatenate([on, z(gap_pre), speech, z(gap_post), off])


def process(speech_path, out_path, bleep_dir, rng, filt=True, p=None):
    p = p or PRESETS["none"]
    orig = normalise(load(speech_path))
    speech = pitch_speed(orig, p["semitones"], p["speed"])
    if p["semitones"] < 0:
        speech = match_highs(speech, orig, max_db=p["hf_db"])   # undo the dullness from lowering pitch
    speech = presence_boost(speech, p["presence"])
    speech = low_boost(speech, p["lowboost"])
    if filt:
        speech = normalise(radio_filter(speech, drive=p["drive"], rng=rng, lowcut=p["lowcut"]))
    else:
        speech = normalise(speech)
    on = normalise(load(os.path.join(bleep_dir, rng.choice(ON))), 0.7)
    off = normalise(load(os.path.join(bleep_dir, rng.choice(OFF))), 0.7)
    save(out_path, wrap(speech, on, off))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--bleeps", required=True, help="folder holding on1/on2/off1-4 wavs")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--no-filter", action="store_true")
    p.add_argument("--preset", choices=list(PRESETS), default="none")
    p.add_argument("--semitones", type=float, help="override preset pitch (negative = deeper)")
    p.add_argument("--speed", type=float, help="override preset speed (<1 slower)")
    p.add_argument("--hf-db", dest="hf_db", type=float); p.add_argument("--presence", type=float); p.add_argument("--lowcut", type=float); p.add_argument("--lowboost", type=float); p.add_argument("--drive", type=float)
    a = p.parse_args()
    rng = random.Random(a.seed); nrng = np.random.default_rng(a.seed)
    pr = dict(PRESETS[a.preset])
    for k in ("semitones", "speed", "lowcut", "lowboost", "drive", "hf_db", "presence"):
        if getattr(a, k) is not None:
            pr[k] = getattr(a, k)

    class R:  # one object offering .choice and .normal
        choice = staticmethod(rng.choice)
        normal = staticmethod(nrng.normal)

    if os.path.isdir(a.src):
        os.makedirs(a.dst, exist_ok=True)
        for f in sorted(os.listdir(a.src)):
            if f.lower().endswith(".wav"):
                process(os.path.join(a.src, f), os.path.join(a.dst, f), a.bleeps, R, not a.no_filter, pr)
    else:
        process(a.src, a.dst, a.bleeps, R, not a.no_filter, pr)


if __name__ == "__main__":
    main()
