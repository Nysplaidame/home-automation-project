"""Audio I/O. Internally everything is float32 mono at SR (22050 Hz, matching Piper medium voices)."""
import io
import wave
from math import gcd

import numpy as np
from scipy.signal import resample_poly

SR = 22050


def resample(a, sr_in, sr_out=SR):
    if sr_in == sr_out:
        return a.astype(np.float32)
    g = gcd(int(sr_in), int(sr_out))
    return resample_poly(a, sr_out // g, sr_in // g).astype(np.float32)


def _to_mono(a):
    return a.mean(axis=1) if a.ndim > 1 else a


def load(path, sr=SR):
    """Load wav/flac/ogg/mp3 as float32 mono at `sr`.

    PCM WAV goes through the stdlib `wave` module exactly like the original radio_fx.py so
    results stay bit-compatible; anything else uses soundfile, then librosa as a last resort."""
    try:
        with wave.open(str(path)) as w:
            n, sw, ch, rate = w.getnframes(), w.getsampwidth(), w.getnchannels(), w.getframerate()
            raw = w.readframes(n)
        if sw == 1:
            a = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128
        elif sw == 2:
            a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        else:
            raise wave.Error(f"sample width {sw}")
        if ch > 1:
            a = a.reshape(-1, ch).mean(axis=1)
        return resample(a, rate, sr)
    except (wave.Error, EOFError):
        pass
    try:
        import soundfile as sf
        a, rate = sf.read(str(path), dtype="float32", always_2d=False)
    except Exception:
        import librosa  # handles mp3 via audioread/ffmpeg when libsndfile cannot
        a, rate = librosa.load(str(path), sr=None, mono=True)
    return resample(_to_mono(np.asarray(a, np.float32)), rate, sr)


def to_wav_bytes(a, sr=SR, out_sr=None):
    """16-bit PCM mono WAV bytes; optionally resampled to out_sr (e.g. 44100) on export."""
    if out_sr and out_sr != sr:
        a = resample(a, sr, out_sr)
        sr = out_sr
    a = np.clip(np.asarray(a, np.float32), -1, 1)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((a * 32767).astype(np.int16).tobytes())
    return buf.getvalue()


def save(path, a, sr=SR, out_sr=None):
    with open(path, "wb") as f:
        f.write(to_wav_bytes(a, sr, out_sr))
