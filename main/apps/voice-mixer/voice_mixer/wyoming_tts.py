"""Metrocop Wyoming TTS: Piper voice -> voicefx preset -> Home Assistant.

A minimal Wyoming server (no external wyoming package) that answers `describe` and `synthesize`.
Each request is synthesised with a local Piper voice, run through a Voice Mixer preset (radio,
bleeps, loudness; no RVC), and streamed back as 16-bit mono PCM.

    python -m voice_mixer.wyoming_tts --voice /voices/en_GB-metrocop2-medium.onnx \
        --preset /data/presets/metrocop.json --bleep-dir /clips/bleeps --port 10201

Environment fallbacks: METROCOP_VOICE, METROCOP_PRESET, METROCOP_BLEEPS, METROCOP_PORT.
"""
import argparse
import asyncio
import io
import json
import logging
import os
import random
import threading
import time
import wave

import numpy as np

from voicefx import Pipeline, load_preset
from voicefx.audio import SR

log = logging.getLogger("metrocop-tts")
NAME = "metrocop"
ATTR = {"name": "home-automation-project", "url": ""}
CHUNK_SAMPLES = 2048


# ---------------------------------------------------------------- wire format
def encode_event(etype, data=None, payload=b""):
    hdr = {"type": etype, "version": "1.0.0"}
    body = json.dumps(data).encode() if data else b""
    if body:
        hdr["data_length"] = len(body)
    if payload:
        hdr["payload_length"] = len(payload)
    return json.dumps(hdr).encode() + b"\n" + body + payload


async def read_event(reader):
    line = await reader.readline()
    if not line:
        return None
    hdr = json.loads(line)
    data = hdr.get("data") or {}
    if hdr.get("data_length"):
        data = {**data, **json.loads(await reader.readexactly(hdr["data_length"]))}
    if hdr.get("payload_length"):
        await reader.readexactly(hdr["payload_length"])
    return hdr["type"], data


# ---------------------------------------------------------------- synthesis
class Engine:
    def __init__(self, voice_path, preset_path, bleep_dir, length_scale=None):
        from piper import PiperVoice  # imported lazily so tests of the wire format stay light

        self.voice = PiperVoice.load(voice_path)
        self.params, _, _ = load_preset(preset_path)
        self.pipeline = Pipeline(bleep_dir)
        self.length_scale = length_scale
        self.lock = threading.Lock()
        sr = self.voice.config.sample_rate
        if sr != SR:
            log.warning("voice sample rate %s != pipeline %s; audio will be resampled", sr, SR)

    def synthesize(self, text):
        from piper import SynthesisConfig

        t0 = time.perf_counter()
        with self.lock:
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                cfg = SynthesisConfig(length_scale=self.length_scale) if self.length_scale else None
                self.voice.synthesize_wav(text, w, syn_config=cfg)
            buf.seek(0)
            with wave.open(buf) as w:
                sr = w.getframerate()
                a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            if sr != SR:
                from voicefx.audio import resample
                a = resample(a, sr, SR)
            # fresh seed per announcement so the end blip (and static) vary like the game
            params = {**self.params, "bleeps.seed": random.randint(0, 9999)}
            out = self.pipeline.render(Pipeline.prepare_source(a), params).audio
        pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes()
        log.info("synth %.2fs audio in %.2fs: %r", len(out) / SR, time.perf_counter() - t0, text[:60])
        return pcm


def info_event():
    voice = {"name": NAME, "description": "Metrocop radio voice (Piper + voicefx)", "attribution": ATTR,
             "installed": True, "version": "1.0", "languages": ["en_GB", "en"]}
    return {"tts": [{"name": "metrocop", "description": "Metrocop TTS", "attribution": ATTR,
                     "installed": True, "version": "1.0", "voices": [voice]}],
            "asr": [], "handle": [], "intent": [], "wake": [], "mic": [], "snd": []}


# ---------------------------------------------------------------- server
async def handle(engine, reader, writer):
    peer = writer.get_extra_info("peername")
    try:
        while True:
            ev = await read_event(reader)
            if ev is None:
                break
            etype, data = ev
            if etype == "describe":
                writer.write(encode_event("info", info_event()))
            elif etype == "synthesize":
                text = (data.get("text") or "").strip()
                pcm = await asyncio.to_thread(engine.synthesize, text) if text else b""
                fmt = {"rate": SR, "width": 2, "channels": 1}
                writer.write(encode_event("audio-start", fmt))
                step = CHUNK_SAMPLES * 2
                for i in range(0, len(pcm), step):
                    writer.write(encode_event("audio-chunk", fmt, pcm[i:i + step]))
                writer.write(encode_event("audio-stop"))
            else:
                log.debug("ignoring %s from %s", etype, peer)
            await writer.drain()
    except (ConnectionError, asyncio.IncompleteReadError):
        pass
    except Exception:
        log.exception("error serving %s", peer)
    finally:
        writer.close()


async def serve(engine, host, port):
    server = await asyncio.start_server(lambda r, w: handle(engine, r, w), host, port)
    log.info("Metrocop TTS ready on %s:%s", host, port)
    async with server:
        await server.serve_forever()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--voice", default=os.environ.get("METROCOP_VOICE", "/voices/en_GB-metrocop2-medium.onnx"))
    ap.add_argument("--preset", default=os.environ.get("METROCOP_PRESET", "/data/presets/metrocop.json"))
    ap.add_argument("--bleep-dir", default=os.environ.get("METROCOP_BLEEPS", "/clips/bleeps"))
    ap.add_argument("--host", default=os.environ.get("METROCOP_HOST", "0.0.0.0"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("METROCOP_PORT", "10201")))
    ap.add_argument("--length-scale", type=float, default=None)
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    engine = Engine(a.voice, a.preset, a.bleep_dir, a.length_scale)
    engine.synthesize("Ready.")  # warm up model and caches
    asyncio.run(serve(engine, a.host, a.port))


if __name__ == "__main__":
    main()
