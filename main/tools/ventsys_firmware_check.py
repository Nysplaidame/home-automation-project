#!/usr/bin/env python3
"""Compare independently captured native valve reports; never controls devices."""
import argparse
import json
import math
from pathlib import Path

FIELDS = ("position", "open", "closed")

def validate(report):
    if not isinstance(report, dict) or not isinstance(report.get("mac"), str):
        raise ValueError("Missing board identity")
    if report.get("pwm_active") is not False:
        raise ValueError("PWM must be reported inactive")
    for field in FIELDS:
        value = report.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError(f"Invalid or unavailable {field} report")
    if report["closed"] >= report["open"] or not report["closed"] <= report["position"] <= report["open"]:
        raise ValueError("Invalid endpoint or position range")
    if report.get("accepted_image") is not True:
        raise ValueError("Firmware image acceptance is not confirmed")
    return report

def compare(before, after):
    validate(before); validate(after)
    failures = []
    if before["mac"].casefold() != after["mac"].casefold(): failures.append("Board MAC changed")
    for field in FIELDS:
        if before[field] != after[field]: failures.append(f"{field} changed: {before[field]} -> {after[field]}")
    return failures

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path); parser.add_argument("after", type=Path)
    args = parser.parse_args()
    try:
        failures = compare(json.loads(args.before.read_text(encoding="utf-8")), json.loads(args.after.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"INDETERMINATE: {exc}"); return 2
    if failures:
        print("FAIL: " + "; ".join(failures)); return 1
    print("PASS: identity, command, endpoints and inactive PWM match; physical position remains unverified."); return 0

if __name__ == "__main__": raise SystemExit(main())
