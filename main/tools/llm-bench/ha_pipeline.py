#!/usr/bin/env python3
"""Inspect or update an HA Assist pipeline over the websocket API.

  python ha_pipeline.py --token-file F list
  python ha_pipeline.py --token-file F set-prefer-local <pipeline_id> <true|false>

`set-prefer-local` fetches the pipeline, flips only `prefer_local_intents`, and writes the full
object back (the update API requires every field). The token is read from the file, never printed.
"""
import argparse
import asyncio
import json
import ssl

import websockets

HA_WS = "wss://192.168.20.101:8123/api/websocket"


async def session(token, fn):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    async with websockets.connect(HA_WS, ssl=ctx, max_size=2**24) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            raise SystemExit("auth failed")
        n = 0

        async def call(payload):
            nonlocal n
            n += 1
            await ws.send(json.dumps({"id": n, **payload}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == n:
                    return msg

        return await fn(call)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("cmd", choices=["list", "set-prefer-local"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    token = open(a.token_file, encoding="utf-8").read().strip()

    async def run(call):
        r = await call({"type": "assist_pipeline/pipeline/list"})
        pipes = r["result"]["pipelines"]
        if a.cmd == "list":
            print("preferred:", r["result"].get("preferred_pipeline"))
            for p in pipes:
                print(json.dumps({k: p.get(k) for k in (
                    "id", "name", "conversation_engine", "prefer_local_intents",
                    "stt_engine", "tts_engine", "tts_voice", "wake_word_entity", "wake_word_id")}))
            return
        pid, val = a.args[0], a.args[1].lower() == "true"
        p = next(x for x in pipes if x["id"] == pid)
        before = p.get("prefer_local_intents")
        payload = {k: v for k, v in p.items() if k != "id"}
        payload["prefer_local_intents"] = val
        res = await call({"type": "assist_pipeline/pipeline/update", "pipeline_id": pid, **payload})
        print("update success:", res.get("success"), "| prefer_local_intents:", before, "->", val)
        if not res.get("success"):
            print(res)

    asyncio.run(session(token, run))


if __name__ == "__main__":
    main()
