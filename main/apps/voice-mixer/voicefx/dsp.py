"""DSP building blocks (numpy/scipy only).

The first group of functions is lifted unchanged from the original radio_fx.py so the classic
presets render identically (tests/test_legacy_equivalence.py checks this against a frozen copy).
The second group adds the extra stages used by the mixer: formant shift, EQ, dynamics and the
extended radio character effects.
"""
from math import gcd

import numpy as np
from scipy.ndimage import minimum_filter1d
from scipy.signal import butter, fftconvolve, lfilter, resample_poly, sosfilt, istft, stft

from .audio import SR

# --------------------------------------------------------------------------------------------
# Original radio_fx.py DSP (behaviour preserved)
# --------------------------------------------------------------------------------------------


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


def wrap(speech, on, off, gap_pre=0.04, gap_post=0.06, fill=None):
    """on + gap + speech + gap + off. fill(n) supplies gap samples (e.g. the radio static) instead of digital silence."""
    z = lambda s: (fill(int(SR * s)) if fill else np.zeros(int(SR * s))).astype(np.float32)
    return np.concatenate([on, z(gap_pre), speech, z(gap_post), off])


# --------------------------------------------------------------------------------------------
# Mixer extensions
# --------------------------------------------------------------------------------------------

def db(x):
    return 20 * np.log10(np.maximum(x, 1e-12))


def undb(x):
    return 10 ** (np.asarray(x, dtype=np.float64) / 20)


def low_shelf_db_to_amount(gain_db):
    """low_boost() adds `amount * lowpass(a)`; at DC that is a gain of 1+amount."""
    return float(undb(gain_db) - 1.0) if gain_db else 0.0


def amount_to_low_shelf_db(amount):
    return float(db(1.0 + amount)) if amount else 0.0


def formant_shift(a, semitones, n_fft=1024, hop=256, lifter_ms=1.5):
    """Move the spectral envelope (formants) by `semitones` while keeping the harmonics (pitch).

    Classic cepstral method: per STFT frame, a low-quefrency liftered cepstrum gives the smooth
    envelope; the envelope is warped along frequency and re-applied to the flattened excitation.
    Original phases are kept. Good enough for character voices; not studio grade."""
    if abs(semitones) < 1e-3 or len(a) < n_fft:
        return a
    alpha = 2 ** (semitones / 12.0)
    _, _, Z = stft(a, fs=SR, window="hann", nperseg=n_fft, noverlap=n_fft - hop, boundary="even")
    mag = np.abs(Z) + 1e-9
    logmag = np.log(mag)
    cep = np.fft.irfft(logmag, n=n_fft, axis=0)
    L = max(8, int(SR * lifter_ms / 1000))
    lift = np.zeros(n_fft)
    lift[0] = 1; lift[1:L] = 2; lift[L] = 1                       # fold to a causal cepstrum
    env_log = np.fft.rfft(cep * lift[:, None], axis=0).real
    k = np.arange(mag.shape[0], dtype=np.float64)
    src = np.clip(k / alpha, 0, mag.shape[0] - 1)                 # new env(k) = old env(k / alpha)
    i0 = np.floor(src).astype(int); i1 = np.minimum(i0 + 1, mag.shape[0] - 1); fr = (src - i0)[:, None]
    warped = env_log[i0] * (1 - fr) + env_log[i1] * fr
    Z2 = np.exp(logmag - env_log + warped) * np.exp(1j * np.angle(Z))
    _, y = istft(Z2, fs=SR, window="hann", nperseg=n_fft, noverlap=n_fft - hop, boundary=True)
    y = y[: len(a)]
    if len(y) < len(a):
        y = np.pad(y, (0, len(a) - len(y)))
    return y.astype(np.float32)


def peaking(a, gain_db, f0, q=1.0):
    """Generic RBJ peaking band (same maths as presence_boost)."""
    if not gain_db or f0 <= 0 or f0 >= SR / 2:
        return a
    return presence_boost(a, gain_db, f0=f0, q=q)


def highpass(a, hz, order=2):
    if not hz or hz <= 0:
        return a
    return sosfilt(butter(order, min(hz, SR / 2 - 50), btype="high", fs=SR, output="sos"), a).astype(np.float32)


def lowpass(a, hz, order=2):
    if not hz or hz <= 0 or hz >= SR / 2 - 50:
        return a
    return sosfilt(butter(order, hz, btype="low", fs=SR, output="sos"), a).astype(np.float32)


def bandpass(a, lo, hi, order=4):
    hi = min(hi, SR / 2 - 50)
    lo = max(1.0, min(lo, hi - 50))
    return sosfilt(butter(int(order), [lo, hi], btype="band", fs=SR, output="sos"), a)


# ---- dynamics: block-rate envelopes (1 ms blocks) keep the Python loops short ----

_BLOCK = 22  # ~1 ms at 22050 Hz


def _block_level_db(a, block=_BLOCK, mode="peak"):
    n = int(np.ceil(len(a) / block))
    p = np.zeros(n * block, np.float32); p[: len(a)] = np.abs(a)
    p = p.reshape(n, block)
    lvl = p.max(axis=1) if mode == "peak" else np.sqrt(np.mean(p ** 2, axis=1))
    return db(lvl)


def _smooth(target_db, attack_ms, release_ms, block=_BLOCK, attack_when_lower=True):
    """One-pole smoothing with separate attack/release; `attack_when_lower` = attack applies when
    the gain is falling (compressor/limiter); a gate opens on rising gain instead."""
    t = block / SR
    aa = np.exp(-t / max(attack_ms / 1000, 1e-5))
    ar = np.exp(-t / max(release_ms / 1000, 1e-5))
    out = np.empty_like(target_db)
    g = target_db[0] if len(target_db) else 0.0
    for i, x in enumerate(target_db):
        falling = x < g
        c = aa if falling == attack_when_lower else ar
        g = c * g + (1 - c) * x
        out[i] = g
    return out


def _apply_block_gain_db(a, gain_db, block=_BLOCK):
    centres = np.arange(len(gain_db)) * block + block / 2
    g = np.interp(np.arange(len(a)), centres, undb(gain_db))
    return (a * g).astype(np.float32)


def compressor(a, threshold_db=-18.0, ratio=3.0, attack_ms=5.0, release_ms=120.0, makeup_db=0.0, knee_db=6.0):
    lvl = _block_level_db(a, mode="rms")
    over = lvl - threshold_db
    # soft knee
    gr = np.where(over <= -knee_db / 2, 0.0,
                  np.where(over >= knee_db / 2, over * (1 - 1 / ratio),
                           (1 - 1 / ratio) * (over + knee_db / 2) ** 2 / (2 * max(knee_db, 1e-6))))
    g = _smooth(-gr, attack_ms, release_ms)
    return _apply_block_gain_db(a, g + makeup_db)


def noise_gate(a, threshold_db=-50.0, floor_db=-80.0, attack_ms=2.0, release_ms=80.0, hold_ms=40.0):
    if threshold_db <= -89:
        return a
    lvl = _block_level_db(a, mode="rms")
    open_ = lvl > threshold_db
    hold = int(hold_ms / 1000 * SR / _BLOCK)
    if hold > 0 and open_.any():
        # keep the gate open for `hold` blocks after the level drops
        idx = np.where(open_, np.arange(len(open_)), -10 ** 9)
        last = np.maximum.accumulate(idx)
        open_ = (np.arange(len(open_)) - last) <= hold
    target = np.where(open_, 0.0, floor_db)
    g = _smooth(target, attack_ms, release_ms, attack_when_lower=False)
    return _apply_block_gain_db(a, g)


def limiter(a, ceiling_db=-1.0, lookahead_ms=2.0):
    """Look-ahead brickwall limiter: never exceeds the ceiling, smooth gain around peaks."""
    if ceiling_db >= 0 and np.max(np.abs(a)) <= 1.0:
        return a
    c = float(undb(ceiling_db))
    need = np.minimum(1.0, c / np.maximum(np.abs(a), 1e-12))
    L = max(1, int(SR * lookahead_ms / 1000))
    g = minimum_filter1d(need, size=2 * L + 1, mode="nearest")
    g = np.convolve(g, np.ones(L + 1) / (L + 1), mode="same")      # still <= need at every peak
    return np.clip(a * g, -c, c).astype(np.float32)


# ---- radio character ----

def coloured_noise(rng, n, std, colour="white"):
    """White draws are taken first so a 'white' render matches the original radio_fx stream."""
    w = rng.normal(0, std, n).astype(np.float32)
    if colour == "white" or n == 0:
        return w
    if colour == "pink":   # Paul Kellet's economy pink filter
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        aa = [1, -2.494956002, 2.017265875, -0.522189400]
        x = lfilter(b, aa, w)
    else:                  # brown / red: leaky integrator
        x = lfilter([1.0], [1, -0.995], w)
    x = x - np.mean(x)
    s = np.std(x) or 1.0
    return (x * (std / s)).astype(np.float32)


def crackle(rng, n, amount):
    """Sparse clicks/pops; amount 0..1 scales both density and level."""
    if amount <= 0 or n == 0:
        return np.zeros(n, np.float32)
    density = 3 + 60 * amount                   # clicks per second
    k = rng.poisson(density * n / SR)
    out = np.zeros(n, np.float32)
    pos = rng.integers(0, n, k)
    amp = rng.uniform(0.05, 0.35, k) * amount * rng.choice([-1, 1], k)
    out[pos] = amp
    # each click rings briefly
    return lfilter([1.0], [1, -0.6], out).astype(np.float32)


def bit_reduce(a, bits):
    if bits >= 16:
        return a
    q = 2 ** (int(bits) - 1)
    return (np.round(a * q) / q).astype(np.float32)


def rate_reduce(a, rate_hz):
    if rate_hz >= SR - 1:
        return a
    idx = (np.floor(np.arange(len(a)) * rate_hz / SR) * SR / rate_hz).astype(int)
    return a[np.minimum(idx, len(a) - 1)]


def ring_tremolo(a, ring_mix=0.0, ring_hz=300.0, trem_depth=0.0, trem_hz=6.0):
    if ring_mix <= 0 and trem_depth <= 0:
        return a
    t = np.arange(len(a)) / SR
    y = a
    if ring_mix > 0:
        y = y * ((1 - ring_mix) + ring_mix * np.sin(2 * np.pi * ring_hz * t))
    if trem_depth > 0:
        y = y * (1 - trem_depth * (0.5 + 0.5 * np.sin(2 * np.pi * trem_hz * t)))
    return y.astype(np.float32)


def room(a, mix, decay_s, seed=0):
    """Short room: exponentially decaying noise impulse response, FFT convolution."""
    if mix <= 0:
        return a
    rng = np.random.default_rng(seed + 7)
    n = max(32, int(decay_s * SR))
    ir = rng.normal(0, 1, n) * np.exp(-6.9 * np.arange(n) / n)       # -60 dB at decay_s
    ir = lowpass(ir.astype(np.float32), 5000)
    ir /= np.sqrt(np.sum(ir ** 2)) or 1.0
    wet = fftconvolve(a, ir)[: len(a)]
    return ((1 - mix) * a + mix * wet).astype(np.float32)


def squelch_tail(rng, ms, level_db, lo=300, hi=3800):
    """Noise burst that decays quickly, like a receiver squelch closing."""
    n = int(SR * ms / 1000)
    if n <= 0:
        return np.zeros(0, np.float32)
    x = rng.normal(0, 1, n)
    x = bandpass(x, lo, hi, 2)
    env = np.exp(-4.0 * np.arange(n) / n)
    env[: min(n, 40)] *= np.linspace(0, 1, min(n, 40))
    x = x * env
    x = x / (np.max(np.abs(x)) or 1.0)
    return (x * float(undb(level_db)) * 0.89).astype(np.float32)


def trim_silence(a, threshold_db=-40.0, pad_s=0.08):
    idx = np.where(np.abs(a) > float(undb(threshold_db)))[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(pad_s * SR)); e = min(len(a), idx[-1] + int(pad_s * SR))
    return a[s:e]


def fade(a, in_ms=0.0, out_ms=0.0):
    a = a.copy()
    ni, no = min(len(a), int(SR * in_ms / 1000)), min(len(a), int(SR * out_ms / 1000))
    if ni:
        a[:ni] *= np.linspace(0, 1, ni, dtype=np.float32)
    if no:
        a[len(a) - no:] *= np.linspace(1, 0, no, dtype=np.float32)
    return a


def rms_db(a):
    return float(db(np.sqrt(np.mean(np.square(a, dtype=np.float64))) if len(a) else 0.0))


def resample_pitch(a, semitones):
    """Simple varispeed pitch (changes length too); used for the bleeps."""
    if not semitones:
        return a
    r = 2 ** (semitones / 12.0)
    g = gcd(int(round(r * 1000)), 1000)
    return resample_poly(a, 1000 // g, int(round(r * 1000)) // g).astype(np.float32)
