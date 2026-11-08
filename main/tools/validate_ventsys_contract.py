#!/usr/bin/env python3
"""Validate the VentSys command contract without contacting production MQTT."""

from __future__ import annotations

import re
import argparse
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


def script_drift(canonical, deployed):
    """Compare execution settings, ignoring presentation and selector metadata.

    Preserve sequence ordering and all nested action data: an omitted command,
    guard or delay is operational drift even when final targets would match.
    """
    presentation = {'alias', 'icon', 'description', 'fields'}
    def execution(script):
        return {key: value for key, value in script.items() if key not in presentation}
    return [name for name in sorted(set(canonical) | set(deployed))
            if name not in canonical or name not in deployed
            or execution(canonical[name]) != execution(deployed[name])]


def validate_deployed_scripts(path, arbitrated=False):
    source = yaml.safe_load(SCRIPTS.read_text(encoding='utf-8'))
    if arbitrated:
        source = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml').read_text(encoding='utf-8'))
    canonical = source['script']
    deployed = yaml.safe_load(path.read_text(encoding='utf-8'))['script']
    drift = script_drift(canonical, deployed)
    if drift:
        fail('deployed script execution differs: ' + ', '.join(drift))
    print('PASS: deployed script execution matches canonical source (read-only comparison)')


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
            if target not in (0, 100):
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
    from generate_ventsys_dashboard_contract import expected_modes
    import json
    launch = DASHBOARD.read_text(encoding="utf-8")
    card = (ROOT / 'dashboards/ventsys-card.js').read_text(encoding='utf-8')
    modes = (ROOT / 'dashboards/ventsys-modes.mjs').read_text(encoding='utf-8')
    actual = json.loads(modes.split('export const MODE_EXPECTED = ', 1)[1].split(';', 1)[0])
    if actual != expected_modes():
        fail('dashboard mode expectations differ from canonical scripts; regenerate contract')
    if 'ventsys-config.js' in launch or 'new WebSocket' in card or 'postMessage(' in card:
        fail('dashboard still uses public credentials or the obsolete frame bridge')
    if '/dashboard-ventsys/0' not in launch:
        fail('legacy launch URL must lead to authenticated HA')
    package = yaml.safe_load((ROOT / 'configs/home-assistant/ventsys_dashboard_package.yaml').read_text(encoding='utf-8'))
    wrapper = package['script']['ventsys_dashboard_command']
    if wrapper['mode'] != 'single':
        fail('dashboard command wrapper must serialize requests')
    dispatch = next(step for step in wrapper['sequence'] if 'choose' in step)
    if dispatch['default'][0]['action'] != 'script.ventsys_normal_command':
        fail('direct dashboard commands must use the shared normal dispatcher')
    print('PASS: authenticated dashboard launch, fixed command boundary and 12 generated mode expectations')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-scripts', type=Path,
                        help='Optional deployed YAML path to read and compare; never runs scripts')
    parser.add_argument('--arbitrated', action='store_true', help='Compare against compiled arbitration runtime')
    args = parser.parse_args()
    validate_scripts()
    validate_dashboard()
    # Check real sensor publication independently of the mode command contract.
    package = (ROOT / "ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml").read_text(encoding="utf-8")
    base = (ROOT / "configs/esphome/ventsys_air_sensor_base.yaml").read_text(encoding="utf-8")
    for enclosure in ("fdm", "sla"):
        firmware = (ROOT / f"configs/esphome/ventsys_{enclosure}_array_1.yaml").read_text(encoding="utf-8")
        for measurement in ("temperature", "smoke", "iaq"):
            if f'mqtt_topic_prefix: "ventsys/{enclosure}/array_1"' not in firmware or f'state_topic: "ventsys/{enclosure}/array_1/{measurement}"' not in package or '${mqtt_topic_prefix}/' + measurement not in base:
                fail(f"{enclosure} primary-array {measurement} publication mismatch")
    print("PASS: primary array temperature/smoke/IAQ topics match HA subscriptions")
    if args.live_scripts:
        validate_deployed_scripts(args.live_scripts, args.arbitrated)
    print("PENDING: pressure-difference publishers, secondary-array safety coverage, physical endpoint and power-cut acceptance; safety commissioning is not certified")
