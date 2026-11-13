#!/usr/bin/env python3
"""Explicit one-shot parser rehearsal; fixtures only, no output destinations."""
import argparse
import base64
import importlib.util
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("omv_metrics", ROOT / "omv-health-metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


def fixture(now):
    return {"schemaVersion": "omv-health/1.0", "observedAt": now.isoformat(),
            "host": {"loadAverage": [0.25, 0.5, 1], "memoryBytes": {"MemTotal": 4096, "MemAvailable": 2048}},
            "storage": {"status": "observed", "disks": [
                {"identityHash": "a" * 32, "status": "warning", "temperatureC": 35,
                 "counters": {"crc": 1, "pending": 0, "reallocated": None}, "serial": "PRIVATE-MARKER"},
                {"identityHash": "b" * 32, "status": "unknown", "temperatureC": 36}]},
            "raid": {"status": "observed", "arrays": [{"array": "md0", "status": "healthy", "degradedMembers": 0}]},
            "filesystems": [{"label": "nas", "status": "observed", "totalBytes": 8192, "availableBytes": 4096},
                            {"label": "14tb", "status": "unknown", "totalBytes": 16384}],
            "services": [{"service": "smbd", "status": "healthy"}, {"service": "nfs-server", "status": "failed"}]}


def expected_samples(text):
    result = {}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        match = re.fullmatch(r'(omv_\w+)(?:\{(.*)\})? (.+)', line)
        if not match:
            raise ValueError("invalid fixture exposition")
        raw_labels = match[2] or ""
        if raw_labels and not re.fullmatch(r'\w+="[a-z0-9-]+"(?:,\w+="[a-z0-9-]+")*', raw_labels):
            raise ValueError("unexpected fixture labels")
        labels = dict(re.findall(r'(\w+)="([a-z0-9-]+)"', raw_labels))
        labels.update(source="omvnas", schema="omv-health/1.0")
        key = (match[1], tuple(sorted(labels.items())))
        if key in result:
            raise ValueError("duplicate fixture sample")
        result[key] = float(match[3])
    return result


def actual_samples(output):
    result = {}
    timestamps = set()
    for line in output.splitlines():
        if line.startswith("> "):
            line = line[2:]
        if not line.startswith("omv_health,"):
            raise ValueError("unexpected test output")
        measurement, fields, timestamp = line.split(" ")
        if not timestamp.isdigit():
            raise ValueError("missing ingestion timestamp")
        timestamps.add(timestamp)
        labels = tuple(sorted(tag.split("=", 1) for tag in measurement.split(",")[1:]))
        for field in fields.split(","):
            name, value = field.split("=", 1)
            key = (name, tuple((k, v) for k, v in labels))
            if key in result:
                raise ValueError("duplicate parsed sample")
            result[key] = float(value)
    if len(timestamps) != 1:
        raise ValueError("collection samples must share one ingestion timestamp for dashboard gating")
    return result


def test_config(text):
    # Only renderer-produced synthetic bytes are encoded. No user shell text.
    encoded = base64.b64encode(text.encode()).decode("ascii")
    command = f"/bin/sh -c 'printf %s {encoded} | base64 -d'"
    template = (ROOT / "omv-health-telegraf-input.conf").read_text()
    template, count = re.subn(r"^  commands = .*", "  commands = [" + json.dumps(command) + "]", template, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("expected one input command")
    return '[agent]\n  omit_hostname = true\n' + template


def verify(command):
    now = datetime.now(timezone.utc)
    fresh = fixture(now)
    stale = {**fresh, "observedAt": (now - timedelta(seconds=601)).isoformat()}
    future = {**fresh, "observedAt": (now + timedelta(seconds=1)).isoformat()}
    results = []
    for name, payload, available in (("fresh_with_unknown", fresh, True), ("stale", stale, True),
                                      ("future", future, True), ("malformed", {}, True), ("missing", None, False)):
        text = metrics.render(payload, now, available)
        expected = expected_samples(text)
        completed = subprocess.run(command, input=test_config(text), text=True, capture_output=True, timeout=25)
        if completed.returncode or "E!" in completed.stderr or "PRIVATE-MARKER" in completed.stdout:
            raise ValueError(f"Telegraf rejected {name}; inspect isolated test diagnostics")
        actual = actual_samples(completed.stdout)
        if actual != expected:
            raise ValueError(f"parsed labels/fields/values differ for {name}")
        results.append({"case": name, "samples": len(actual), "status": "passed"})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssh", help="Explicit existing SSH alias for monitoring host; runs docker exec telegraf --test only")
    parser.add_argument("--telegraf", default="telegraf", help="Local Linux Telegraf executable when --ssh is absent")
    args = parser.parse_args()
    if args.ssh:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", args.ssh):
            parser.error("use a bounded SSH host alias")
        command = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", args.ssh,
                   "docker", "exec", "-i", "telegraf", "telegraf", "--test", "--config", "/dev/stdin"]
    else:
        command = [args.telegraf, "--test", "--config", "/dev/stdin"]
    try:
        print(json.dumps({"rehearsal": "parser-only synthetic fixtures", "results": verify(command)}, indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
