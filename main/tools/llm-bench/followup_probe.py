#!/usr/bin/env python3
"""Follow-up turns in ONE conversation through the real pipeline (text in, intent stage), as a satellite.

  python followup_probe.py --token-file F --device-id ID --ask "Who are you?" --ask "What time is it?" --ask "Tell me a joke."

Spoken questions within a few minutes of each other continue the same conversation, so each model turn also
reads the earlier turns. Compare the wall times here with `docker logs llama-cpp` (prompt eval tokens/time).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import time

import websockets

HA_WS = "wss://192.168.20.101:8123/api/websocket"
PIPELINE = "01kvgsqj25mjtvtxqz5vza719q"  # Overwatch


async def main_async(args):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    token = open(args.token_file).read().strip()
    conv = None
    async with websockets.connect(HA_WS, ssl=ctx, max_size=2**24) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            raise SystemExit("auth failed")
        for n, text in enumerate(args.ask, 1):
            msg = {"id": n, "type": "assist_pipeline/run", "start_stage": "intent", "end_stage": "intent",
                   "input": {"text": text}, "pipeline": args.pipeline}
            if conv:
                msg["conversation_id"] = conv
            if args.device_id:
                msg["device_id"] = args.device_id
            t0 = time.perf_counter()
            await ws.send(json.dumps(msg))
            speech, local = "", None
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=300))
                if m.get("id") != n:
                    continue
                if m.get("type") == "result" and not m.get("success"):
                    speech = f"ERROR {m.get('error')}"
                    break
                ev = m.get("event") or {}
                if ev.get("type") == "intent-end":
                    data = ev["data"]
                    io = data.get("intent_output") or {}
                    local = data.get("processed_locally")
                    conv = io.get("conversation_id") or conv
                    speech = (((io.get("response") or {}).get("speech") or {}).get("plain") or {}).get("speech", "")
                elif ev.get("type") in ("error", "run-end"):
                    break
            print(f"{time.perf_counter() - t0:5.1f}s local={local!s:5} {text[:44]!r:48} -> {speech[:90]!r}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--pipeline", default=PIPELINE)
    ap.add_argument("--device-id")
    ap.add_argument("--ask", action="append", required=True)
    asyncio.run(main_async(ap.parse_args()))
