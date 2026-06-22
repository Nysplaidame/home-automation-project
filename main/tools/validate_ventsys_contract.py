#!/usr/bin/env python3
"""Validate the VentSys command contract without contacting production MQTT."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml"
DASHBOARD = ROOT / "dashboards/ventsys-dashboard.html"


def actions(node):
    """Yield action dictionaries from nested HA sequence/parallel structures."""
    if isinstance(node, list):
        for item in node:
            yield from actions(item)
    elif isinstance(node, dict):
        if "action" in node:
            yield node
        for key in ("sequence", "parallel", "choose", "default"):
            if key in node:
                yield from actions(node[key])


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_scripts() -> int:
    document = yaml.safe_load(SCRIPTS.read_text(encoding="utf-8"))
    scripts = document["script"]
    helper = scripts["ventsys_ramp_valve"]
    helper_actions = list(actions(helper["sequence"]))
    if len(helper_actions) != 1 or helper_actions[0]["action"] != "mqtt.publish":
        fail("valve helper must contain exactly one MQTT publish")
    if any(key in helper for key in ("repeat", "delay")):
        fail("valve helper contains a ramp/delay primitive")

    tested = 0
    for name, script in scripts.items():
        if name == "ventsys_ramp_valve":
            continue
        valve_writes = []
        for action in actions(script.get("sequence", [])):
            if action.get("action") != "script.ventsys_ramp_valve":
                continue
            data = action.get("data", {})
            target = data.get("target")
            topic = data.get("topic", "")
            if target not in (0, 50):
                fail(f"{name} publishes unsupported valve target {target!r}")
            if not topic.endswith("/control"):
                fail(f"{name} has an invalid valve topic {topic!r}")
            valve_writes.append((topic, str(target)))

        duplicates = [topic for topic, count in Counter(t for t, _ in valve_writes).items() if count > 1]
        if duplicates:
            fail(f"{name} writes a valve topic more than once: {duplicates}")
        tested += 1

    print(f"PASS: mock MQTT contract validated for {tested} mode scripts")
    return tested


def validate_dashboard() -> None:
    html = DASHBOARD.read_text(encoding="utf-8")
    init = re.search(r"// Initialise all butterfly[\s\S]*?// ── Flow sensor colour", html)
    if not init:
        fail("dashboard initialization block not found")
    if "updateValveVisual(id, 0)" in init.group() or "haPublish(" in init.group():
        fail("dashboard initialization can enter a command/publish path")

    for start, end in (
        ("function renderValveVisual", "function updateValveVisual"),
        ("function renderIntakeVisual", "function updateIntakeVisual"),
    ):
        block = html.split(start, 1)[1].split(end, 1)[0]
        if "haPublish(" in block:
            fail(f"{start} is not command-free")
    print("PASS: dashboard initialization uses command-free renderers")


if __name__ == "__main__":
    validate_scripts()
    validate_dashboard()
