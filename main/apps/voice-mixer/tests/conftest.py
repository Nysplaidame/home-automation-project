import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from voicefx.audio import SR, save  # noqa: E402


def tone(f0=220.0, secs=2.0, amp=0.5):
    t = np.arange(int(SR * secs)) / SR
    return (amp * np.sin(2 * np.pi * f0 * t)).astype(np.float32)


def f0_of(a, lo=50, hi=1000):
    """Fundamental by zero-padded FFT peak with parabolic interpolation (steady tones)."""
    a = a[len(a) // 8: -len(a) // 8] if len(a) > SR // 2 else a
    n = 1 << 20
    spec = np.abs(np.fft.rfft(a * np.hanning(len(a)), n))
    freqs = np.fft.rfftfreq(n, 1 / SR)
    m = (freqs >= lo) & (freqs <= hi)
    i = np.argmax(np.where(m, spec, 0))
    y0, y1, y2 = np.log(spec[i - 1: i + 2] + 1e-12)
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    return (i + d) * SR / n


def pulse_voice(f0=120.0, formant=1000.0, secs=1.5):
    """Glottal-ish pulse train through a single resonator: a known pitch and a known formant."""
    from scipy.signal import lfilter
    n = int(SR * secs)
    x = np.zeros(n); x[:: int(SR / f0)] = 1.0
    r = 0.97; w = 2 * np.pi * formant / SR
    y = lfilter([1.0], [1, -2 * r * np.cos(w), r * r], x)
    return (0.5 * y / np.max(np.abs(y))).astype(np.float32)


def envelope_peak_hz(a, lo=300, hi=4000):
    """Frequency of the strongest smoothed-spectrum region (formant estimate)."""
    n = 1 << 16
    spec = np.abs(np.fft.rfft(a * np.hanning(len(a)), n)) ** 2
    freqs = np.fft.rfftfreq(n, 1 / SR)
    k = int(300 / (SR / n))          # ~300 Hz smoothing hides the harmonics
    sm = np.convolve(spec, np.ones(k) / k, mode="same")
    m = (freqs >= lo) & (freqs <= hi)
    return freqs[m][np.argmax(sm[m])]


@pytest.fixture
def bleep_dir(tmp_path):
    """Synthetic stand-ins for on1/on2/off1-4 so tests never need the game files."""
    d = tmp_path / "bleeps"
    d.mkdir()
    for i, name in enumerate(["on1.wav", "on2.wav", "off1.wav", "off2.wav", "off3.wav", "off4.wav"]):
        save(str(d / name), tone(800 + 150 * i, 0.12 + 0.02 * i, 0.6))
    return str(d)


@pytest.fixture
def speechlike(tmp_path):
    """A 5 s source with varying pitch and amplitude (stands in for a speech clip)."""
    rng = np.random.default_rng(3)
    t = np.arange(int(SR * 5)) / SR
    f = 140 + 30 * np.sin(2 * np.pi * 0.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    a = sum(np.sin(k * ph) / k for k in range(1, 12))
    a *= 0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 1.3 * t))
    a += rng.normal(0, 0.01, len(a))
    a = (0.5 * a / np.max(np.abs(a))).astype(np.float32)
    path = tmp_path / "speech.wav"
    save(str(path), a)
    return str(path), a
