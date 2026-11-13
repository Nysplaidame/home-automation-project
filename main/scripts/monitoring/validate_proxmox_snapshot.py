#!/usr/bin/env python3
"""Validate a read-only Proxmox health-check JSON snapshot for dashboard use."""

from __future__ import annotations

import argparse
import json
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = (
    "ct111_root",
    "ct114_root",
    "frigate_mount",
    "backup_vm100",
    "backup_vm102",
    "backup_vm103",
    "backup_ct111",
    "backup_ct114",
)
VALID_STATUSES = {"pass", "fail", "warn", "unknown", "skipped"}


def status_of(value: Any) -> str:
    """Read either supported collector status shape without exposing details."""
    if isinstance(value, dict):
        value = value.get("status")
    return str(value or "unknown").strip().lower()


def validate_snapshot(snapshot: Any, require_pass: bool, *, now: datetime | None = None,
                      timestamp_offset: str | None = None, max_age_hours: float = 36) -> tuple[list[str], dict[str, str]]:
    """Return structural errors and the required evidence statuses."""
    errors: list[str] = []
    statuses: dict[str, str] = {}

    if not isinstance(snapshot, dict):
        return ["Top-level JSON value must be an object."], statuses

    if not isinstance(snapshot.get("timestamp"), str) or not snapshot["timestamp"].strip():
        errors.append("Missing non-empty timestamp.")
    if snapshot.get("collector") != "Proxmox host":
        errors.append("Collector must be exactly 'Proxmox host'.")

    if require_pass:
        try:
            if not 0 < max_age_hours < float("inf"):
                raise ValueError("invalid freshness window")
            if timestamp_offset and not re.fullmatch(r"[+-](?:(?:0\d|1[0-3]):[0-5]\d|14:00)", timestamp_offset):
                raise ValueError("invalid timezone offset")
            observed = datetime.fromisoformat(snapshot.get("timestamp", ""))
            if observed.tzinfo is None:
                if not timestamp_offset:
                    raise ValueError("timezone required")
                observed = datetime.fromisoformat(observed.isoformat() + timestamp_offset)
            current = now or datetime.now(timezone.utc)
            age = current - observed
            if age < -timedelta(minutes=5) or age > timedelta(hours=max_age_hours):
                errors.append("Acceptance requires a fresh observation within the evidence window (not future-dated).")
        except (ValueError, TypeError, OverflowError):
            errors.append("Acceptance requires a valid timestamp and explicit collector timezone; use --timestamp-offset for legacy local timestamps.")

    checks = snapshot.get("checks")
    if not isinstance(checks, dict):
        return errors + ["Missing checks object."], statuses

    for key in REQUIRED_CHECKS:
        if key not in checks:
            errors.append(f"Missing required check: {key}.")
            continue
        status = status_of(checks[key])
        statuses[key] = status
        if status not in VALID_STATUSES:
            statuses[key] = "invalid"
            errors.append(f"Invalid status for {key}.")
        elif require_pass and status != "pass":
            errors.append(f"Acceptance requires {key} to pass; observed {status}.")

    return errors, statuses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Path to health_check.sh --json output")
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Fail unless every required mount, capacity and backup-freshness check passes.",
    )
    parser.add_argument("--timestamp-offset", help="Collector UTC offset for legacy timestamps, e.g. +01:00")
    parser.add_argument("--max-age-hours", type=float, default=36, help="Maximum snapshot age for acceptance (default 36 hours)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        print(f"Snapshot not found: {args.snapshot}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"Snapshot is not valid JSON: {error.msg}", file=sys.stderr)
        return 2

    errors, statuses = validate_snapshot(snapshot, args.require_pass,
                                        timestamp_offset=args.timestamp_offset,
                                        max_age_hours=args.max_age_hours)
    print("Proxmox dashboard evidence")
    print("Collector requirement: Proxmox host")
    for key in REQUIRED_CHECKS:
        print(f"{key}: {statuses.get(key, 'missing')}")

    if errors:
        print("Result: NOT ACCEPTED")
        for error in errors:
            print(f"- {error}")
        return 1

    result = "ACCEPTANCE READY" if args.require_pass else "STRUCTURALLY VALID"
    print(f"Result: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
