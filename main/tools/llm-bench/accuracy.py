#!/usr/bin/env python3
"""Accuracy harness for the Overwatch agent through Home Assistant (stdlib only, read-only prompts).

Each scenario is a fresh conversation; every turn has a pass check (regex must match, optional regex
must NOT match). Scenarios are repeated --reps times to expose run-to-run variance.

  python accuracy.py --token-file F --label 30b --reps 3 --out accuracy-30b.json

Expected facts assume the current Mealie data (Creamy Tarragon Chicken, Creamy Tarragon Chicken (1),
Ultimate Chicken Soup for "chicken curry"; Lentil soup saved). Update CHECKS if that data changes.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import ssl
import time
import urllib.request
from collections import defaultdict

AGENT = "conversation.llama_cpp_conversation"
HA = "https://192.168.20.101:8123"
NO_SUCH = (r"(?i)(don't|do not|doesn't|does not|no) (have|see|find|know|recogni[sz]e)|"
           r"not (part|available|found|set up|configured|something|listed|a device|recogni[sz]ed|known)|"
           r"can't find|cannot find|couldn't find|unable to find|no such|"
           r"isn't (a|an|part|in|listed)|not in (this|your|the) home|no information|no device|no record|"
           r"not equipped|no sensor|not detected|(can't|cannot|unable to) (report|check|determine|tell|see)")

def _time_close(reply: str, tolerance_min: int = 3) -> bool:
    """True when the reply states a clock time within a few minutes of now (a bare 'H:MM' passed before,
    so an invented time such as '10:30' counted as correct)."""
    m = re.search(r"\b(\d{1,2}):(\d{2})\s*([AaPp])?\.?[Mm]?\b", reply)
    if not m:
        return False
    hour, minute, ampm = int(m.group(1)), int(m.group(2)), (m.group(3) or "").lower()
    if ampm == "p" and hour < 12:
        hour += 12
    if ampm == "a" and hour == 12:
        hour = 0
    now = datetime.datetime.now()
    now_min = now.hour * 60 + now.minute
    candidates = {(hour * 60 + minute) % 1440}
    if not ampm and hour < 12:
        candidates.add(((hour + 12) * 60 + minute) % 1440)  # a bare 12-hour reading
    return any(min((c - now_min) % 1440, (now_min - c) % 1440) <= tolerance_min for c in candidates)


# (id, user text, must-match regex or callable(reply)->bool, must-not-match regex or None)
RECIPE_FLOW = [
    ("list_names", "Find three chicken curry recipes and give me just their names.",
     r"(?is)(?=.*Creamy Tarragon Chicken)(?=.*Ultimate Chicken Soup)", None),
    ("recall_first", "What was the name of the first recipe you found?", r"Creamy Tarragon Chicken", r"\(1\)"),
    ("recall_third", "And what was the third one?", r"Ultimate Chicken Soup", None),
    ("recall_count", "How many recipes did you find?", r"\b(3|three)\b", None),
    ("pick_ingredients", "Pick the second one and read me the ingredient list.",
     r"(?is)\(1\).*chicken breasts", None),
    ("recall_first_after_pick", "Remind me, what was the first recipe in that list?",
     r"Creamy Tarragon Chicken", r"\(1\)"),
    ("recall_picked", "Which recipe did I pick?", r"\(1\)", None),
    ("ingredient_qty", "How much salt does it need?", r"(?i)salt", None),
    ("repeat_step", "Repeat step two.", r"(?i)heat 1 tablespoon", None),
    ("repick_third", "Actually, pick the third one and read me the ingredients.",
     r"(?s)ingredients for Ultimate Chicken Soup", r"Tarragon"),
    ("recall_picked_after_repick", "Which recipe did I pick?", r"Ultimate Chicken Soup", None),
]

GENERAL = [
    ("capital", "What is the capital of France?", r"Paris", None),
    ("identity", "Who are you?", r"(?i)overwatch", None),
    ("math1", "What is two plus two times three?", r"\b(8|eight)\b", None),
    ("math2", "What is fifteen percent of eighty?", r"\b(12|twelve)\b", None),
    ("echo", "Say exactly: the quick brown fox.", r"(?i)quick brown fox", None),
    ("time", "What time is it?", lambda reply: _time_close(reply), None),
    ("no_device_state", "Is the flux capacitor switched on?", NO_SUCH, r"(?i)\bis (not )?(currently )?(switched|turned) (on|off)\b"),
    ("no_device_garage", "Is the garage door open?", NO_SUCH, None),
    ("no_device_action", "Turn on the flux capacitor.", NO_SUCH, r"(?i)(has been|have) (turned|switched)|done"),
    ("shopping", "What is on my shopping list?", r"(?i)(cheese|empty|nothing|no items|shopping list has)", None),
    ("saved_recipes", "What recipes do I have saved?", r"(?i)Here are \d+ saved recipes", r"more saved"),
    ("web_height", "Search the web for how tall Mount Everest is.", r"8[,. ]?8\d\d|29[,. ]?0\d\d", None),
    ("web_boiling", "Search the web for the boiling point of water in Celsius.", r"\b100\b", None),
    ("web_author", "Search the web for who wrote Pride and Prejudice.", r"Austen", None),
    ("web_light", "Search the web for the speed of light in kilometres per second.", r"299|300[, ]?000", None),
    ("web_capital", "Search the web for the capital of Australia.", r"Canberra", None),
]

# Breadth: questions no rule was written for. A pass needs a grounded, non-refusing answer; where the
# home has no data source (calendar) the pass is an honest "no access", never invented events.
_REFUSAL = (r"(?i)one moment|i will (check|search)|i'll (check|search)|let me (check|search)|"
            r"cannot|can't|don't have access|no access|have no (information|access)|"
            r"don't have (any )?information|unable to|no such device")


def _days_to_christmas() -> int:
    today = datetime.date.today()
    target = datetime.date(today.year, 12, 25)
    if target < today:
        target = datetime.date(today.year + 1, 12, 25)
    return (target - today).days


BREADTH = [
    ("area_temp", "What is the temperature in the garage?", r"(?i)degrees|°", NO_SUCH),
    ("area_humidity", "What's the humidity in the garage?", r"(?i)percent|%", NO_SUCH),
    ("motion_gate", "Is there any motion on the gate camera?", r"(?i)motion|clear|detect", NO_SUCH),
    ("date_today", "What's today's date?",
     r"(?is)(?=.*\b%s\b)(?=.*\b%d\b)" % (datetime.date.today().strftime("%B"), datetime.date.today().day), None),
    ("weekday", "What day of the week is it?", r"(?i)\b%s\b" % datetime.date.today().strftime("%A"), None),
    ("date_math", "How many days until Christmas?", r"\b%d\b" % _days_to_christmas(), None),
    ("weather_now", "What's the weather like today?",
     r"(?i)°|degrees|rain|sun|cloud|clear|shower|forecast|overcast|dry|wind|mild|cold|warm|cool|fog|snow|storm",
     _REFUSAL),
    ("sports_result", "Who won the football match last night?", r".{15,}", _REFUSAL),
    ("headlines", "What are the latest headlines?", r".{25,}", _REFUSAL),
    # The reply alone cannot prove the garden_tasks tool ran ("no tasks due" may be true). Verify tool use
    # in the llama.cpp capture or the HA log after a run; this check only rejects refusals/announcements.
    ("garden_tasks", "What garden tasks are due today?", r"(?i)task|due|nothing|none|no |garden",
     r"(?i)one moment|i will check|i'll check|let me check|cannot|can't|no access|check the garden"),
    ("calendar_honest", "What's on my calendar tomorrow?",
     r"(?i)(no|don't|do not|cannot|can't|not|unable).{0,50}calendar|calendar.{0,50}(not|no |isn't|unavailable)", None),
    ("joke", "Tell me a short joke.", r".{15,}", r"(?i)cannot|can't"),
]

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def say(token, text, conv_id):
    body = {"text": text, "language": "en", "agent_id": AGENT}
    if conv_id:
        body["conversation_id"] = conv_id
    req = urllib.request.Request(
        HA + "/api/conversation/process", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300, context=_ctx) as r:
        d = json.load(r)
    return (round(time.perf_counter() - t0, 1),
            ((d["response"].get("speech") or {}).get("plain") or {}).get("speech", ""),
            d.get("conversation_id"))


def run_scenario(token, turns, rep, rows):
    conv = None
    for cid, text, must, mustnot in turns:
        try:
            wall, reply, conv = say(token, text, conv)
        except Exception as exc:
            wall, reply = 0.0, f"ERROR {type(exc).__name__}: {exc}"
        matched = must(reply) if callable(must) else re.search(must, reply)
        ok = bool(matched) and not (mustnot and re.search(mustnot, reply))
        rows.append({"id": cid, "rep": rep, "user": text, "wall_s": wall, "ok": ok, "reply": reply})
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid:24} {wall:5.1f}s  {reply[:110]!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("--label", default="run")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--only", choices=["recipe", "general", "breadth"])
    ap.add_argument("--out")
    a = ap.parse_args()
    token = open(a.token_file, encoding="utf-8").read().strip()
    rows = []
    for rep in range(1, a.reps + 1):
        print(f"== rep {rep}")
        if a.only in (None, "recipe"):
            run_scenario(token, RECIPE_FLOW, rep, rows)
        for name, turns in (("general", GENERAL), ("breadth", BREADTH)):
            if a.only in (None, name):
                for turn in turns:
                    run_scenario(token, [turn], rep, rows)
    by = defaultdict(list)
    for r in rows:
        by[r["id"]].append(r)
    print("\n=== accuracy by check")
    for cid, rs in by.items():
        p = sum(r["ok"] for r in rs)
        print(f"{cid:26} {p}/{len(rs)}  avg {sum(r['wall_s'] for r in rs)/len(rs):5.1f}s")
    tot = sum(r["ok"] for r in rows)
    print(f"\nOVERALL {tot}/{len(rows)} = {100*tot/len(rows):.0f}%   total wall {sum(r['wall_s'] for r in rows):.0f}s")
    if a.out:
        json.dump({"label": a.label, "rows": rows}, open(a.out, "w", encoding="utf-8"), indent=2)
        print("wrote", a.out)


if __name__ == "__main__":
    main()
