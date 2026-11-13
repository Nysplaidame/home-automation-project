#!/usr/bin/env python3
"""Time to first audio for a pipeline turn (text in, intent + TTS), as a satellite would hear it.

  python tts_stream_probe.py --token-file F [--device-id ID] --ask "Tell me three facts about the moon."

Runs `assist_pipeline/run` from the intent stage to the TTS stage, fetches the TTS stream URL the run
announces at `run-start`, and reports when each pipeline event and the first audio bytes arrive. With
sentence-by-sentence speech the first audio should arrive well before `intent-end` on a long model reply.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import time
import urllib.request

import websockets

HA = "https://192.168.20.101:8123"
HA_WS = "wss://192.168.20.101:8123/api/websocket"
PIPELINE = "01kvgsqj25mjtvtxqz5vza719q"  # Overwatch


def _ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_audio(url, t0, out):
    """Blocking: read the TTS stream; record first-audio time (past the WAV header), end time and size."""
    try:
        with urllib.request.urlopen(HA + url, timeout=300, context=_ctx()) as r:
            total = 0
            while True:
                block = r.read(4096)
                if not block:
                    break
                total += len(block)
                if "first_audio_s" not in out and total > 1024:
                    out["first_audio_s"] = round(time.perf_counter() - t0, 1)
            out["audio_end_s"] = round(time.perf_counter() - t0, 1)
            out["audio_bytes"] = total
    except Exception as err:  # noqa: BLE001 - a probe reports, it does not crash
        out["audio_error"] = repr(err)


async def ask(ws, n, text, pipeline, device_id):
    msg = {"id": n, "type": "assist_pipeline/run", "start_stage": "intent", "end_stage": "tts",
           "input": {"text": text}, "pipeline": pipeline}
    if device_id:
        msg["device_id"] = device_id
    t0 = time.perf_counter()
    await ws.send(json.dumps(msg))
    row = {"user": text, "events": {}, "deltas": 0}
    fetch = None
    while True:
        m = json.loads(await asyncio.wait_for(ws.recv(), timeout=300))
        if m.get("id") != n:
            continue
        if m.get("type") == "result" and not m.get("success"):
            row["error"] = m.get("error")
            break
        ev = m.get("event") or {}
        kind, data = ev.get("type"), ev.get("data") or {}
        now = round(time.perf_counter() - t0, 1)
        if kind == "intent-progress":
            if (data.get("chat_log_delta") or {}).get("content"):
                row["deltas"] += 1
                row["events"].setdefault("first_delta", now)
            if data.get("tts_start_streaming"):
                row["events"].setdefault("tts_start_streaming", now)
            continue
        if kind:
            row["events"].setdefault(kind, now)
        if kind == "run-start":
            tts_output = data.get("tts_output") or {}
            row["stream_response"] = tts_output.get("stream_response")
            if tts_output.get("url"):
                fetch = asyncio.get_running_loop().run_in_executor(None, fetch_audio, tts_output["url"], t0, row)
        elif kind == "intent-end":
            io = data.get("intent_output") or {}
            row["reply"] = (((io.get("response") or {}).get("speech") or {}).get("plain") or {}).get("speech", "")
        elif kind == "error":
            row["error"] = data
            break
        elif kind == "run-end":
            break
    if fetch is not None:
        await fetch
    return row


async def main_async(args):
    token = open(args.token_file).read().strip()
    rows = []
    async with websockets.connect(HA_WS, ssl=_ctx(), max_size=2**24) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            raise SystemExit("auth failed")
        for n, text in enumerate(args.ask, 1):
            row = await ask(ws, n, text, args.pipeline, args.device_id)
            rows.append(row)
            print(json.dumps(row))
    if args.out:
        json.dump(rows, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--pipeline", default=PIPELINE)
    ap.add_argument("--device-id")
    ap.add_argument("--ask", action="append", required=True)
    ap.add_argument("--out")
    asyncio.run(main_async(ap.parse_args()))
