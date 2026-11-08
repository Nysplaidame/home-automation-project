#!/usr/bin/env python3
"""Bounded snapshot-to-Prometheus stdout adapter; no collection or shipping."""
import json
import math
import os
import re
import stat
import sys
from datetime import datetime, timezone

MAX_BYTES = 512 * 1024
DEFAULT_PATH = "/var/lib/home-automation/omv-health/snapshot.json"
STATUS = {"healthy": 1, "warning": 2, "failed": 3}
SERVICES = {"smbd", "nfs-server", "smartmontools", "mdmonitor"}


def numeric(value, minimum=0, maximum=2**63 - 1):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and minimum <= value <= maximum)


def records(value, key, limit, allowed):
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError("invalid records")
    seen = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("invalid record")
        identifier = row.get(key)
        if identifier is None and key == "identityHash":
            continue
        if not isinstance(identifier, str) or not allowed(identifier) or identifier in seen:
            raise ValueError("invalid identity")
        seen.add(identifier)
    return value


def render(payload, now=None, available=True):
    """Buffer everything before output so invalid input cannot emit partial health."""
    now = now or datetime.now(timezone.utc)
    samples = {}

    def emit(name, value, labels=None):
        suffix = ""
        if labels:
            # All callers use fixed keys and validated, bounded label vocabularies.
            suffix = "{" + ",".join(f'{key}="{val}"' for key, val in sorted(labels.items())) + "}"
        samples.setdefault("omv_" + name, []).append(f"omv_{name}{suffix} {value}")

    valid, fresh, age = 0, 0, None
    try:
        if not isinstance(payload, dict) or payload.get("schemaVersion") != "omv-health/1.0":
            raise ValueError("invalid schema")
        observed = datetime.fromisoformat(payload["observedAt"].replace("Z", "+00:00"))
        if observed.tzinfo is None:
            raise ValueError("missing timezone")
        age = (now - observed).total_seconds()
        host, storage, raid = (payload[k] for k in ("host", "storage", "raid"))
        if any(not isinstance(v, dict) for v in (host, storage, raid)):
            raise ValueError("invalid sections")
        disks = records(storage.get("disks"), "identityHash", 32, lambda v: bool(re.fullmatch(r"[0-9a-f]{32}", v)))
        arrays = records(raid.get("arrays"), "array", 8, lambda v: bool(re.fullmatch(r"md\d{1,3}", v)))
        mounts = records(payload.get("filesystems"), "label", 3, lambda v: v in {"root", "nas", "14tb"})
        services = records(payload.get("services"), "service", 4, lambda v: v in SERVICES)
        valid, fresh = 1, int(0 <= age <= 600)
        if fresh:
            emit("storage_observed", int(storage.get("status") == "observed"))
            emit("raid_observed", int(raid.get("status") == "observed"))
            emit("disk_identity_missing", sum(r.get("identityHash") is None for r in disks))
            for row in disks if storage.get("status") == "observed" else []:
                if row.get("identityHash") is None:
                    continue
                labels = {"disk": row["identityHash"]}
                state = STATUS.get(row.get("status"), 0)
                emit("disk_status", state, labels)
                if not state:
                    continue
                if numeric(row.get("temperatureC"), -20, 150):
                    emit("disk_temperature_celsius", row["temperatureC"], labels)
                counters = row.get("counters")
                if isinstance(counters, dict):
                    for key in ("crc", "pending", "uncorrectable", "reallocated"):
                        value = counters.get(key)
                        if isinstance(value, int) and numeric(value):
                            emit("disk_attribute_count", value, {**labels, "attribute": key})
            for row in arrays if raid.get("status") == "observed" else []:
                labels = {"array": row["array"]}
                state = STATUS.get(row.get("status"), 0)
                emit("raid_status", state, labels)
                if state and isinstance(row.get("degradedMembers"), int) and numeric(row["degradedMembers"], 0, 1024):
                    emit("raid_degraded_members", row["degradedMembers"], labels)
            for row in mounts:
                labels = {"dataset": row["label"]}
                observed_mount = row.get("status") == "observed"
                emit("filesystem_observed", int(observed_mount), labels)
                for field, kind in (("totalBytes", "total"), ("availableBytes", "available")):
                    if observed_mount and numeric(row.get(field)):
                        emit("filesystem_bytes", row[field], {**labels, "kind": kind})
            for row in services:
                emit("service_status", STATUS.get(row.get("status"), 0), {"service": row["service"]})
            load = host.get("loadAverage")
            if isinstance(load, list) and len(load) == 3:
                for window, value in zip(("1m", "5m", "15m"), load):
                    if numeric(value, 0, 1e6):
                        emit("host_load", value, {"window": window})
            memory = host.get("memoryBytes")
            if isinstance(memory, dict):
                for field, kind in (("MemTotal", "total"), ("MemAvailable", "available")):
                    if numeric(memory.get(field)):
                        emit("host_memory_bytes", memory[field], {"kind": kind})
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
        samples.clear()
        valid, fresh, age = 0, 0, None
    emit("snapshot_available", int(available))
    emit("snapshot_valid", valid)
    emit("snapshot_fresh", fresh)
    if age is not None and numeric(age, -1e12, 1e12):
        emit("snapshot_age_seconds", age)
    return "".join(f"# TYPE {name} gauge\n" + "\n".join(lines) + "\n" for name, lines in sorted(samples.items()))


def read_snapshot(path):
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise OSError("not a regular file")
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise OSError("oversized snapshot")
    try:
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate JSON key")
                result[key] = value
            return result

        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object), True
    except (ValueError, UnicodeError, RecursionError):
        return None, True


def main():
    if len(sys.argv) > 2:
        raise SystemExit("Usage: omv-health-metrics.py [snapshot.json]")
    try:
        payload, available = read_snapshot(sys.argv[1] if len(sys.argv) == 2 else DEFAULT_PATH)
    except OSError:
        payload, available = None, False
    sys.stdout.write(render(payload, available=available))


if __name__ == "__main__":
    main()
