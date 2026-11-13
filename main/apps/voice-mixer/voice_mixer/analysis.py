"""Metrics and fast numpy-drawn waveform/spectrogram images (no matplotlib)."""
import numpy as np
from scipy.signal import stft

from voicefx import dsp
from voicefx.audio import SR

# magma-like stops
_STOPS = np.array([[0, 0, 4], [40, 11, 84], [101, 21, 110], [159, 42, 99], [212, 72, 66],
                   [245, 125, 21], [250, 193, 39], [252, 255, 164]], np.float32)
_LUT = np.stack([np.interp(np.linspace(0, 1, 256), np.linspace(0, 1, len(_STOPS)), _STOPS[:, c]) for c in range(3)], 1).astype(np.uint8)


def hf_ratio(a, split=1500.0):
    """Share of spectral energy above `split` Hz (the 'muffling' meter)."""
    if len(a) == 0:
        return 0.0
    s = np.abs(np.fft.rfft(a)) ** 2
    f = np.fft.rfftfreq(len(a), 1 / SR)
    tot = s.sum() or 1.0
    return float(s[f >= split].sum() / tot)


def metrics(a):
    return {
        "duration_s": len(a) / SR,
        "peak_db": float(dsp.db(np.max(np.abs(a)) if len(a) else 0)),
        "rms_db": dsp.rms_db(a),
        "hf_pct": 100 * hf_ratio(a),
    }


def metrics_md(src, out, info):
    ms, mo = metrics(src), metrics(out)
    t = info.get("timings_ms") or {}
    hits = info.get("cache_hits") or []
    computed = ", ".join(f"{k} {v:.0f} ms" for k, v in t.items()) or "all cached"
    bleeps = info.get("bleeps_used")
    rows = [
        "| | Source | Result |", "|---|---:|---:|",
        f"| Duration | {ms['duration_s']:.2f} s | {mo['duration_s']:.2f} s |",
        f"| Energy > 1.5 kHz | {ms['hf_pct']:.1f} % | {mo['hf_pct']:.1f} % |",
        f"| Peak / RMS | {ms['peak_db']:.1f} / {ms['rms_db']:.1f} dB | {mo['peak_db']:.1f} / {mo['rms_db']:.1f} dB |",
    ]
    tail = f"Computed: {computed}" + (f" · cached: {', '.join(hits)}" if hits else "")
    if bleeps:
        tail += f" · bleeps: {bleeps[0]} / {bleeps[1]}"
    return "\n".join(rows) + f"\n\n<small>{tail}</small>"


def _spectrogram(a, width, height, fmax=SR / 2):
    if len(a) < 512:
        a = np.pad(a, (0, 512 - len(a)))
    hop = max(64, len(a) // width)
    f, _, Z = stft(a, fs=SR, nperseg=512, noverlap=max(0, 512 - hop), boundary=None)
    S = 20 * np.log10(np.abs(Z) + 1e-7)
    S = S[f <= fmax]
    S = np.clip((S - (S.max() - 80)) / 80, 0, 1)
    # resample to width x height (nearest)
    yi = np.linspace(S.shape[0] - 1, 0, height).astype(int)
    xi = np.linspace(0, S.shape[1] - 1, width).astype(int)
    return _LUT[(S[yi][:, xi] * 255).astype(np.uint8)]


def _waveform(a, width, height, colour, bg=(22, 24, 30)):
    img = np.empty((height, width, 3), np.uint8); img[:] = bg
    if len(a) == 0:
        return img
    n = int(np.ceil(len(a) / width))
    p = np.zeros(n * width, np.float32); p[: len(a)] = a
    p = p.reshape(width, n)
    mx, mn = np.clip(p.max(1), -1, 1), np.clip(p.min(1), -1, 1)
    mid = height / 2
    top = (mid - mx * mid * 0.95).astype(int); bot = (mid - mn * mid * 0.95).astype(int)
    rows = np.arange(height)[:, None]
    mask = (rows >= top[None, :]) & (rows <= bot[None, :])
    img[mask] = colour
    img[int(mid), :] = (60, 64, 72)
    return img


def panel(a, total_s, width=900, wave_h=90, spec_h=150, colour=(120, 190, 255)):
    """Waveform over spectrogram, drawn on a shared time axis of total_s seconds (so source and
    result line up visually); the unused right part stays dark."""
    w = max(40, int(width * min(1.0, (len(a) / SR) / max(total_s, 1e-6))))
    img = np.zeros((wave_h + spec_h + 2, width, 3), np.uint8); img[:] = (22, 24, 30)
    img[:wave_h, :w] = _waveform(a, w, wave_h, colour)
    img[wave_h + 2:, :w] = _spectrogram(a, w, spec_h)
    # 1.5 kHz marker line on the spectrogram
    y = wave_h + 2 + int(spec_h * (1 - 1500 / (SR / 2)))
    img[y, :w:4] = (255, 255, 255)
    return img
