#!/usr/bin/env python3
"""Re-score a saved accuracy.py run against the CURRENT check patterns (so a checker fix applies to old runs).

  python rescore.py accuracy-baseline-prephase1-2026-11-12.json [more.json ...]

The stored replies are unchanged; only the pass/fail decision is recomputed. Prints raw vs rescored
totals per group and lists every row whose verdict changed, so a rescoring is never silent.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

import accuracy as A

CHECKS = {c[0]: c for table in (A.RECIPE_FLOW, A.GENERAL, A.BREADTH) for c in table}
GROUP = {c[0]: name for name, table in (("recipe", A.RECIPE_FLOW), ("general", A.GENERAL), ("breadth", A.BREADTH))
         for c in table}


# Checks whose expected answer depends on the day or the clock when the run happened.
TIME_DEPENDENT = {"time", "date_today", "weekday", "date_math"}


def verdict(check_id: str, reply: str, stored: bool) -> bool:
    _, _, must, mustnot = CHECKS[check_id]
    if callable(must) or check_id in TIME_DEPENDENT:
        # These cannot be re-evaluated on another day or time, so the verdict recorded during the run stands.
        return stored
    matched = re.search(must, reply)
    return bool(matched) and not (mustnot and re.search(mustnot, reply))


def main() -> None:
    for path in sys.argv[1:]:
        rows = json.load(open(path, encoding="utf-8"))["rows"]
        raw, fixed = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        changed = []
        for r in rows:
            if r["id"] not in CHECKS:
                continue
            new = verdict(r["id"], r["reply"], r["ok"])
            g = GROUP[r["id"]]
            raw[g][0] += r["ok"]
            raw[g][1] += 1
            fixed[g][0] += new
            fixed[g][1] += 1
            if new != r["ok"]:
                changed.append((r["id"], r["ok"], new, r["reply"][:90]))
        print(f"== {path}")
        for g in ("recipe", "general", "breadth"):
            if raw[g][1]:
                print(f"  {g:8} raw {raw[g][0]}/{raw[g][1]}  rescored {fixed[g][0]}/{fixed[g][1]}")
        tot_raw = sum(v[0] for v in raw.values())
        tot_fixed = sum(v[0] for v in fixed.values())
        n = sum(v[1] for v in fixed.values())
        print(f"  TOTAL    raw {tot_raw}/{n} = {100*tot_raw/n:.0f}%  rescored {tot_fixed}/{n} = {100*tot_fixed/n:.0f}%")
        for cid, old, new, reply in changed:
            print(f"    changed {cid}: {'PASS' if old else 'FAIL'} -> {'PASS' if new else 'FAIL'}  {reply!r}")


if __name__ == "__main__":
    main()
