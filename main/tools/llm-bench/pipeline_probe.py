#!/usr/bin/env python3
"""Probe the REAL Assist pipeline (intent stage) and report who answered each utterance.

The REST `agent_id` calls used by accuracy.py skip the pipeline's `prefer_local_intents` step, so they
show only the LLM agent's own behaviour. A voice command goes pipeline -> Home Assistant's built-in
sentence matching first -> the LLM agent only if nothing local matched. This runs utterances through
`assist_pipeline/run` (text in, intent stage only) and records `processed_locally`, time and speech.
Read-only utterances only: it never asks for a device to be switched.

  python pipeline_probe.py --token-file F [--pipeline ID] [--out probe.json]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import sys
import time

import websockets

from ha_pipeline import HA_WS

PIPELINE = "01kvgsqj25mjtvtxqz5vza719q"  # Overwatch

SINGLE = [
    ("state_unknown_dev", "Is the garage door open?"),
    ("state_unknown_dev2", "Is the flux capacitor switched on?"),
    ("state_fan", "Is the inline fan on?"),
    ("state_fan_ambig", "Is the fan on?"),
    ("state_value", "What is the FDM enclosure temperature?"),
    ("state_value_area", "What is the temperature in the garage?"),
    ("state_value_casual", "How warm is it in the garage?"),
    ("state_humidity", "What's the humidity in the garage?"),
    ("state_motion", "Is there any motion on the gate camera?"),
    ("state_pronoun", "Is it on?"),
    ("time", "What time is it?"),
    ("date", "What is today's date?"),
    ("shopping_read", "What is on my shopping list?"),
    ("chat_fact", "What is the capital of France?"),
    ("chat_identity", "Who are you?"),
    ("chat_math", "What is two plus two times three?"),
    ("chat_echo", "Say exactly: the quick brown fox."),
    ("recipes_saved", "What recipes do I have saved?"),
    ("web_search", "Search the web for how tall Mount Everest is."),
    ("garden", "What garden tasks are due today?"),
    ("action_unknown_dev", "Turn on the flux capacitor."),
]
RECIPE_FLOW = [
    ("flow_list", "Find three chicken curry recipes and give me just their names."),
    ("flow_recall", "What was the first one?"),
    ("flow_pick", "Pick the second one and read me the ingredient list."),
    ("flow_step", "Repeat step two."),
]


async def main_async(token, pipeline, out, device_id=None, asks=None):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    rows = []
    async with websockets.connect(HA_WS, ssl=ctx, max_size=2**24) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            raise SystemExit("auth failed")
        n = 0

        async def turn(text, conv_id=None):
            nonlocal n
            n += 1
            msg = {"id": n, "type": "assist_pipeline/run", "start_stage": "intent", "end_stage": "intent",
                   "input": {"text": text}, "pipeline": pipeline}
            if conv_id:
                msg["conversation_id"] = conv_id
            if device_id:  # same prompt and tool list as a spoken question to that satellite
                msg["device_id"] = device_id
            t0 = time.perf_counter()
            await ws.send(json.dumps(msg))
            local, speech, conv, err = None, "", conv_id, None
            while True:
                m = json.loads(await asyncio.wait_for(ws.recv(), timeout=300))
                if m.get("id") != n:
                    continue
                if m.get("type") == "result" and not m.get("success"):
                    err = m.get("error")
                    break
                ev = m.get("event") or {}
                if ev.get("type") == "intent-end":
                    data = ev["data"]
                    local = data.get("processed_locally")
                    io = data.get("intent_output") or {}
                    conv = io.get("conversation_id") or conv
                    speech = (((io.get("response") or {}).get("speech") or {}).get("plain") or {}).get("speech", "")
                elif ev.get("type") == "error":
                    err = ev.get("data")
                    break
                elif ev.get("type") == "run-end":
                    break
            return round(time.perf_counter() - t0, 1), local, (speech if err is None else f"ERROR {err}"), conv

        if asks:  # custom questions only, each in a fresh conversation
            for i, text in enumerate(asks, 1):
                secs, local, speech, _ = await turn(text)
                rows.append({"id": f"ask{i}", "user": text, "wall_s": secs, "local": local, "reply": speech})
                print(f"{secs:5.1f}s {text[:52]!r:56} -> {speech[:150]!r}")
            if out:
                json.dump(rows, open(out, "w", encoding="utf-8"), indent=2)
            return
        for cid, text in SINGLE:
            secs, local, speech, _ = await turn(text)
            rows.append({"id": cid, "user": text, "wall_s": secs, "local": local, "reply": speech})
            print(f"{secs:5.1f}s {'LOCAL' if local else 'LLM  '}  {cid:20} {text[:46]!r:50} -> {speech[:80]!r}")
        conv = None
        for cid, text in RECIPE_FLOW:
            secs, local, speech, conv = await turn(text, conv)
            rows.append({"id": cid, "user": text, "wall_s": secs, "local": local, "reply": speech})
            print(f"{secs:5.1f}s {'LOCAL' if local else 'LLM  '}  {cid:20} {text[:46]!r:50} -> {speech[:80]!r}")
    if out:
        json.dump(rows, open(out, "w", encoding="utf-8"), indent=2)
        print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--pipeline", default=PIPELINE)
    ap.add_argument("--out")
    ap.add_argument("--device-id", help="send as this device (e.g. the Voice PE) so the prompt matches a spoken turn")
    ap.add_argument("--ask", action="append", help="ask only this question (repeatable) instead of the standard battery")
    a = ap.parse_args()
    token = open(a.token_file, encoding="utf-8").read().strip()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    asyncio.run(main_async(token, a.pipeline, a.out, a.device_id, a.ask))


if __name__ == "__main__":
    main()
