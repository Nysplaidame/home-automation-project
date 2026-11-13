#!/usr/bin/env python3
"""Write-action acceptance test for the Overwatch agent (stdlib only).

Uses throwaway targets only and reverts them:
  * a shopping-list item named "acceptance test cheese" (added, then removed by voice command;
    any leftover in HA's built-in list is removed by this script)
  * the Voice PE LED ring light (turned on, then off; left off at the end)
Never touches VentSys, camera, or other devices. Records what each backend actually did.

Usage: python write_test.py --token-file K:\\...\\.ha-token --label 30b --out write-30b.json
"""
from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.request

AGENT = "conversation.llama_cpp_conversation"
LED = "light.home_assistant_voice_0ae52a_led_ring"
TODO = "todo.shopping_list"
HA = "https://192.168.20.101:8123"

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def api(token, path, data=None):
    req = urllib.request.Request(
        HA + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=240, context=_ctx) as r:
        return json.load(r)


def say(token, text, conv_id=None):
    body = {"text": text, "language": "en", "agent_id": AGENT}
    if conv_id:
        body["conversation_id"] = conv_id
    t0 = time.perf_counter()
    d = api(token, "/api/conversation/process", body)
    wall = time.perf_counter() - t0
    speech = ((d["response"].get("speech") or {}).get("plain") or {}).get("speech", "")
    return round(wall, 1), speech, d.get("conversation_id")


def todo_items(token):
    r = api(token, "/api/services/todo/get_items?return_response", {"entity_id": TODO})
    return [i["summary"] for i in r["service_response"][TODO]["items"]]


def led_state(token):
    return api(token, f"/api/states/{LED}")["state"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--label", default="run")
    ap.add_argument("--out")
    args = ap.parse_args()
    token = open(args.token_file, encoding="utf-8").read().strip()

    log = []

    def step(name, text, conv=None, check=None):
        wall, speech, conv = say(token, text, conv)
        extra = check() if check else None
        row = {"step": name, "user": text, "wall_s": wall, "reply": speech, "check": extra}
        log.append(row)
        print(f"[{name}] {wall:5.1f}s U: {text}\n{'':14}A: {speech[:240]}\n{'':14}check: {extra}")
        return conv

    todo_before = todo_items(token)
    led_before = led_state(token)
    print("before: todo items", len(todo_before), "| led", led_before)

    # Shopping list round trip
    c = step("add", "Add acceptance test cheese to my shopping list.", None,
             lambda: {"ha_todo_has_item": any("acceptance test" in s.lower() for s in todo_items(token))})
    c = step("list", "What is on my shopping list?", c)
    c = step("remove", "Remove acceptance test cheese from my shopping list.", c,
             lambda: {"ha_todo_has_item": any("acceptance test" in s.lower() for s in todo_items(token))})

    # Device round trip (Voice PE LED ring)
    c2 = step("led_on", "Turn on the Voice assistant LED ring.", None, lambda: {"led": led_state(token)})
    c2 = step("led_off", "Turn off the Voice assistant LED ring.", c2, lambda: {"led": led_state(token)})

    # Cleanup: guarantee the original state
    cleanup = []
    for s in todo_items(token):
        if "acceptance test" in s.lower():
            api(token, "/api/services/todo/remove_item", {"entity_id": TODO, "item": s})
            cleanup.append(f"removed leftover HA todo item: {s}")
    if led_before == "off" and led_state(token) != "off":
        api(token, "/api/services/light/turn_off", {"entity_id": LED})
        cleanup.append("turned LED ring off")
    after = {"todo_items": len(todo_items(token)), "led": led_state(token)}
    print("cleanup:", cleanup or "none needed", "| after:", after, "| before todo:", len(todo_before))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"label": args.label, "steps": log, "cleanup": cleanup, "after": after,
                       "before": {"todo_items": len(todo_before), "led": led_before}}, f, indent=2)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
