"""Experiment: ONE stable prefix (lean prompt + every tool seen in live traffic) for every utterance.

Runs inside CT 114 against the 30B (via the capture proxy). Only the model is called; no tool is executed,
so nothing in the home changes. Reports, per utterance: first tool chosen vs expected, prompt tokens that
actually had to be processed (prompt_n) vs reused from cache (cache_n), and wall time of the first call.
"""
import json
import time
import urllib.request

URL = "http://127.0.0.1:8081/v1/chat/completions"
rows = [json.loads(l) for l in open("/root/cap/captured.jsonl")]

tools = {}
for r in rows:
    for t in r["request"].get("tools") or []:
        tools.setdefault(t["function"]["name"], t)
tools["web_search"] = {"type": "function", "function": {
    "name": "web_search",
    "description": ("Search the internet for current or detailed information. Use this for recipes, news, "
                    "recommendations, products, documentation, and facts that may have changed. Base the "
                    "answer on the returned sources."),
    "parameters": {"type": "object", "properties": {"query": {"type": "string",
                                                              "description": "Focused web search query"}},
                   "required": ["query"]}}}
TOOLS = list(tools.values())

with_ctx = [r for r in rows if r["request"].get("tools")
            and "Static Context" in str(r["request"]["messages"][0].get("content", ""))]
_s = with_ctx[-1]["request"]["messages"][0]["content"]
HA_TAIL = _s[_s.index("Static Context"):]  # Static Context + HA intent-tool rules, whatever the prompt length

import sys
VARIANTS = {
    "v1": (
        "You are Overwatch, the voice assistant for this home. Speak tersely and formally, in plain sentences "
        "suitable for text to speech.\n"
        "Use tools for anything that depends on live data or the real world: home state and control, the current "
        "date and time, the shopping list, saved recipes, and weather, news or any fact that may have changed "
        "(use web_search). Never state a device value, the date, the time or a current fact without a tool "
        "result. Answer general knowledge, arithmetic and conversation directly without tools. If no tool can "
        "answer, say what is missing."
    ),
    "v2": (
        "You are Overwatch, the voice assistant for this home. Speak tersely and formally, in plain sentences "
        "for text to speech.\n"
        "You have tools; pick by topic and call them instead of refusing:\n"
        "- Home devices, sensors, rooms, readings, or whether something is on, open or running: call "
        "homeassistant__GetLiveContext, even when the device is not in the list below.\n"
        "- Current date or time, or any date arithmetic: call llm__GetDateTime. You have no clock of your own.\n"
        "- Weather, forecasts, news, sports results, prices, opening hours, or anything that may have changed: "
        "call web_search. Never say you cannot check; search.\n"
        "- The shopping list: use the Grocy tools, not the todo tools. Saved recipes: use the Mealie tools.\n"
        "- Switching or setting devices: use the Hass tools.\n"
        "Answer general knowledge, arithmetic and chat directly. After a tool result, answer briefly from that "
        "result only."
    ),
}
LEAN = VARIANTS[sys.argv[1] if len(sys.argv) > 1 else "v1"]
SYSTEM = LEAN + "\n" + HA_TAIL

GLC, DT, WS = "homeassistant__GetLiveContext", "llm__GetDateTime", "web_search"
BATTERY = [
    ("fan_state", "Is the inline fan on?", {GLC}),
    ("area_temp", "What is the temperature in the garage?", {GLC}),
    ("garage_door", "Is the garage door open?", {GLC}),
    ("time", "What time is it?", {DT}),
    ("days_xmas", "How many days until Christmas?", {DT}),
    ("weather", "What's the weather like today?", {WS, GLC}),
    ("rain", "Will it rain tomorrow?", {WS, GLC}),
    ("news", "Who won the football match last night?", {WS}),
    ("recipes", "What recipes do I have saved?", {"find_saved_recipes"}),
    ("shop_read", "What is on my shopping list?", {"list_grocy_shopping_list"}),
    ("shop_add", "Add milk to my shopping list.", {"add_grocy_shopping_item"}),
    ("web", "Search the web for the capital of Australia.", {WS}),
    ("control", "Turn on the inline fan.", {"intent__HassTurnOn"}),
    ("volume", "Set the volume to thirty percent.", {"media_player__HassSetVolume"}),
    ("chat", "What is the capital of France?", set()),
    ("echo", "Say exactly: the quick brown fox.", set()),
    ("math", "What is fifteen percent of eighty?", set()),
    ("calendar", "What's on my calendar tomorrow?", set()),
    ("motion", "Is there any motion on the gate camera?", {GLC}),
    ("humidity", "What's the humidity in the garage?", {GLC}),
    ("how_warm", "How warm is it in the garage?", {GLC}),
    ("headlines", "What are the latest headlines?", {WS}),
    ("joke", "Tell me a short joke.", set()),
]


def tok(text):
    req = urllib.request.Request("http://127.0.0.1:8081/tokenize", data=json.dumps({"content": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    return len(json.load(urllib.request.urlopen(req, timeout=60))["tokens"])


def ask(user):
    body = {"model": "home-assistant-llm", "temperature": 0.1, "max_tokens": 96, "tools": TOOLS,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t0 = time.time()
    d = json.load(urllib.request.urlopen(req, timeout=300))
    wall = time.time() - t0
    msg = d["choices"][0]["message"]
    calls = [c["function"]["name"] for c in msg.get("tool_calls") or []]
    tm = d.get("timings", {})
    return calls, msg.get("content") or "", wall, tm


print("ha_tail tokens:", tok(HA_TAIL), "| tools:", len(TOOLS), "tool tokens:", tok(json.dumps(TOOLS)), "system tokens:", tok(SYSTEM))
ok_total = n_total = 0
for pass_no, order in enumerate((BATTERY, list(reversed(BATTERY))), start=1):
    print(f"== pass {pass_no}")
    for cid, text, expected in order:
        calls, content, wall, tm = ask(text)
        got = set(calls)
        ok = (got == set() and not expected) or (bool(got) and got <= expected and bool(expected))
        ok_total += ok
        n_total += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {cid:12} {wall:5.1f}s new={tm.get('prompt_n')!s:>5} cached={tm.get('cache_n')!s:>5} "
              f"gen={tm.get('predicted_n')!s:>3} call={sorted(got) or '-'} text={content[:60]!r}")
print(f"TOOL CHOICE {ok_total}/{n_total}")
