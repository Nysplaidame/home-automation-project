#!/usr/bin/env python3
"""Replay captured Home Assistant requests against a llama-server and report server timings.

  python3 replay_bench.py --url http://127.0.0.1:8091 --file captured.jsonl [--max 10] [--cold]

--cold sets cache_prompt=false so every request pays full prompt processing (measures raw prompt
speed); without it, repeating a request shows warm-cache behaviour. Prints per-request
prompt tokens / ms / tok/s, generated tokens / tok/s and wall time, then totals.
"""
import argparse
import hashlib
import json
import time
import urllib.request


def load(path, limit):
    seen, out = set(), []
    for line in open(path, encoding="utf-8"):
        rec = json.loads(line)
        req = rec["request"]
        key = hashlib.md5(json.dumps(req.get("messages", [])[-3:], sort_keys=True).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        out.append(req)
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--file", required=True)
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--cold", action="store_true")
    ap.add_argument("--pick", default="", help="comma list of 1-based request numbers, e.g. 1,4,15")
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    reqs = load(a.file, a.max)
    if a.pick:
        reqs = [reqs[int(i) - 1] for i in a.pick.split(",") if 0 < int(i) <= len(reqs)]
    tot = {"pn": 0, "pms": 0.0, "gn": 0, "gms": 0.0, "wall": 0.0}
    for i, req in enumerate(reqs, 1):
        req = dict(req)
        req["stream"] = False
        if a.cold:
            req["cache_prompt"] = False
        t0 = time.perf_counter()
        r = urllib.request.Request(a.url.rstrip("/") + "/v1/chat/completions", data=json.dumps(req).encode(),
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=600) as resp:
            d = json.load(resp)
        wall = time.perf_counter() - t0
        t = d.get("timings") or {}
        pn, pms, gn, gms = t.get("prompt_n", 0), t.get("prompt_ms", 0), t.get("predicted_n", 0), t.get("predicted_ms", 0)
        for k, v in (("pn", pn), ("pms", pms), ("gn", gn), ("gms", gms), ("wall", wall)):
            tot[k] += v
        print(f"{i:2} prompt {pn:5} tok {pms/1000:6.1f}s ({(pn/(pms/1000)) if pms else 0:6.1f} tok/s) | "
              f"gen {gn:4} tok {gms/1000:5.1f}s ({(gn/(gms/1000)) if gms else 0:5.1f} tok/s) | wall {wall:5.1f}s")
    print(f"TOTAL {a.label}: prompt {tot['pn']} tok in {tot['pms']/1000:.1f}s = {tot['pn']/(tot['pms']/1000 or 1):.1f} tok/s; "
          f"gen {tot['gn']} tok in {tot['gms']/1000:.1f}s = {tot['gn']/(tot['gms']/1000 or 1):.1f} tok/s; wall {tot['wall']:.1f}s")


if __name__ == "__main__":
    main()
