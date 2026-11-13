#!/usr/bin/env python3
"""End-to-end acceptance run through Home Assistant's conversation API (stdlib only).

Sends read-only scripted conversations to the Overwatch agent
(`conversation.llama_cpp_conversation`) and records wall time and reply text per turn.
Nothing here switches a device, adds to a list, or saves a recipe.

Usage:
  python accept.py --token-file K:\\...\\.ha-token --label 14b --out accept-14b.json
The token is read from the file and never printed. TLS verification is off because HA uses a
private CA on a LAN IP; the target is fixed by --ha.
"""
from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.request

AGENT = "conversation.llama_cpp_conversation"

# Each scenario is one conversation (shared conversation_id), run in order.
SCENARIOS = {
    "recipe_flow": [
        "Find three chicken curry recipes and give me just their names.",
        "Pick the second one and read me the ingredient list.",
        "Now read me the steps.",
        "Repeat the ingredients.",
        "Repeat step two.",
        "What was the name of the first recipe you found?",
    ],
    "house_queries": [
        "What time is it?",
        "Is the flux capacitor switched on?",  # nonexistent: must say it cannot find it
        "What is on my shopping list?",
        "What recipes do I have saved?",
    ],
    "web": [
        "Search the web for how tall Mount Everest is.",
    ],
}


def converse(ha: str, token: str, text: str, conv_id: str | None):
    body = {"text": text, "language": "en", "agent_id": AGENT}
    if conv_id:
        body["conversation_id"] = conv_id
    req = urllib.request.Request(
        ha.rstrip("/") + "/api/conversation/process",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=240, context=ctx) as r:
        data = json.load(r)
    wall = time.perf_counter() - t0
    resp = data.get("response", {})
    speech = ((resp.get("speech") or {}).get("plain") or {}).get("speech", "")
    return wall, speech, data.get("conversation_id"), resp.get("response_type")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ha", default="https://192.168.20.101:8123")
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--label", default="run")
    ap.add_argument("--out")
    args = ap.parse_args()
    token = open(args.token_file, encoding="utf-8").read().strip()

    results = {}
    for name, turns in SCENARIOS.items():
        conv_id = None
        rows = []
        for text in turns:
            try:
                wall, speech, conv_id, rtype = converse(args.ha, token, text, conv_id)
            except Exception as exc:  # record and continue
                wall, speech, rtype = 0.0, f"ERROR: {type(exc).__name__}: {exc}", "error"
            rows.append({"user": text, "wall_s": round(wall, 1), "type": rtype, "reply": speech})
            print(f"[{name}] {wall:5.1f}s  U: {text}\n{'':16}A: {speech[:300]}")
        results[name] = rows

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"label": args.label, "results": results}, f, indent=2)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
