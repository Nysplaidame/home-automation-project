#!/usr/bin/env python3
"""Fixed-prompt benchmark for the Overwatch llama.cpp server (stdlib only).

Usage:
  python bench.py [--url http://192.168.20.104:8081] [--runs 3] [--label baseline] [--out results.json]

Sends a fixed prompt set to /v1/chat/completions and records llama.cpp `timings`
(prompt tok/s, generation tok/s) plus wall time. Run against production (8081) for the
baseline, or a temporary candidate container on another port. Read-only: it only
generates text, it never touches Home Assistant.

The tool-call prompt uses a *representative* HA tool schema, not the live one. Replace
TOOLS from a real `conversation/process` debug run before comparing models for
tool-calling quality (see HANDOFF-2026-11-11-llm-igpu-speed.md, step 0).
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
import urllib.request

SEARCH_SYSTEM = (
    "You turn web search snippets into a spoken answer for a voice assistant. "
    "Answer the user's question in ONE short sentence using only facts in the "
    "snippets, with concrete values (numbers, units, ranges) when present. "
    "No lists, URLs, markdown or source numbers. If the snippets do not answer "
    "it, say so briefly. /no_think"
)
SEARCH_USER = (
    "Question: how long do you boil an egg for a soft yolk\n\nSnippets:\n"
    "[1] Perfect soft boiled eggs: Lower eggs into boiling water and cook for 6 minutes for a "
    "runny yolk, 7 minutes for a jammy centre, then cool in ice water.\n"
    "[2] How to boil eggs: Hard boiled eggs take 10 to 12 minutes; soft boiled take 4 to 6 "
    "minutes depending on egg size and fridge temperature.\n"
    "[3] Egg timing guide: 6.5 minutes gives a set white and soft yolk for large eggs."
)

HA_SYSTEM = (
    "You are Overwatch, a cold, authoritative home assistant. Control the home with the "
    "provided tools. Never invent entities. Current time: 19:42. Areas: kitchen, living room, "
    "garage. Devices: light.kitchen_ceiling (on), light.living_room_lamp (off), "
    "switch.garage_fan (off). /no_think"
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "HassTurnOn",
            "description": "Turn on a device or entity",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "area": {"type": "string"},
                    "domain": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "HassTurnOff",
            "description": "Turn off a device or entity",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "area": {"type": "string"},
                    "domain": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
]

# name -> (messages, extra payload, max_tokens, expected tool name or None)
PROMPTS = {
    "chat_short": (
        [
            {"role": "system", "content": HA_SYSTEM},
            {"role": "user", "content": "Who are you?"},
        ],
        {},
        60,
        None,
    ),
    "tool_call_light": (
        [
            {"role": "system", "content": HA_SYSTEM},
            {"role": "user", "content": "Turn on the living room lamp."},
        ],
        {"tools": TOOLS},
        80,
        "HassTurnOn",
    ),
    "tool_call_search": (
        [
            {"role": "system", "content": HA_SYSTEM},
            {"role": "user", "content": "Search the web for how tall Mount Everest is."},
        ],
        {"tools": TOOLS},
        80,
        "web_search",
    ),
    "web_summary": (
        [
            {"role": "system", "content": SEARCH_SYSTEM},
            {"role": "user", "content": SEARCH_USER},
        ],
        {},
        60,
        None,
    ),
}


def call(url: str, messages, extra, max_tokens):
    payload = {
        "model": "home-assistant-llm",
        "messages": messages,
        "stream": False,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
        **extra,
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as r:
        body = json.load(r)
    wall = time.perf_counter() - t0
    msg = body["choices"][0]["message"]
    calls = [c["function"]["name"] for c in msg.get("tool_calls") or []]
    t = body.get("timings") or {}
    return {
        "wall_s": round(wall, 2),
        "prompt_n": t.get("prompt_n"),
        "prompt_tps": round(t["prompt_per_second"], 1) if t.get("prompt_per_second") else None,
        "gen_n": t.get("predicted_n"),
        "gen_tps": round(t["predicted_per_second"], 2) if t.get("predicted_per_second") else None,
        "tool_calls": calls,
        "text": (msg.get("content") or "").strip(),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://192.168.20.104:8081")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--label", default="baseline")
    ap.add_argument("--out")
    args = ap.parse_args()

    results = {}
    for name, (messages, extra, max_tokens, expect) in PROMPTS.items():
        runs = [call(args.url, messages, extra, max_tokens) for _ in range(args.runs)]
        ok = None if expect is None else all(expect in r["tool_calls"] for r in runs)
        results[name] = {
            "runs": runs,
            "wall_median_s": statistics.median(r["wall_s"] for r in runs),
            "gen_tps_median": statistics.median(r["gen_tps"] for r in runs if r["gen_tps"]),
            "prompt_tps_median": statistics.median(r["prompt_tps"] for r in runs if r["prompt_tps"]),
            "tool_call_ok": ok,
        }
        r = results[name]
        print(
            f"{name:18} wall {r['wall_median_s']:6.2f}s  gen {r['gen_tps_median']:5.2f} tok/s  "
            f"prompt {r['prompt_tps_median']:6.1f} tok/s  tool_ok={ok}"
        )
        print(f"{'':18} e.g. {runs[0]['tool_calls'] or runs[0]['text'][:90]!r}")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"label": args.label, "url": args.url, "results": results}, f, indent=2)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
