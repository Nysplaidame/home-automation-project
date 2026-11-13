#!/usr/bin/env python3
"""Read-only, host-local OMV JSON snapshot; no shipping, writes or disk tests."""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DATASETS = {
    "nas": "fdb92af7-371c-4793-8d98-ff47e961498d",
    "14tb": "a8843f98-c937-48a8-aefa-4cd0fb80667c",
}
SERVICES = ("smbd", "nfs-server", "smartmontools", "mdmonitor")


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if len(result.stdout.encode("utf-8")) > 512 * 1024:
            return None, ""
        return result.returncode, result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None, ""


def number(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def mapping(value):
    return value if isinstance(value, dict) else {}


def smart_summary(payload, exit_code):
    """smartctl uses a bitmask; attribute/log warnings are not command failure."""
    if not isinstance(payload, dict):
        payload = {}
    identity = payload.get("wwn") or payload.get("serial_number")
    identifier = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:32] if identity else None
    standby = str(payload.get("power_mode", "")).lower() == "standby" or any(
        "standby" in str(message.get("string", "")).lower()
        for message in (mapping(payload.get("smartctl")).get("messages") or []) if isinstance(message, dict)
    )
    passed = mapping(payload.get("smart_status")).get("passed")
    counters = {}
    attributes = mapping(payload.get("ata_smart_attributes")).get("table") or []
    for code, name in ((5, "reallocated"), (197, "pending"), (198, "uncorrectable"), (199, "crc")):
        attribute = next((a for a in attributes if isinstance(a, dict) and a.get("id") == code), {})
        counters[name] = number(mapping(attribute.get("raw")).get("value"))
    if standby or exit_code is None or exit_code & 7:
        status = "unknown"
    elif passed is False or exit_code & 8:
        status = "failed"
    elif passed is not True:
        status = "unknown"
    elif exit_code & 240 or any(value and value > 0 for value in counters.values()):
        status = "warning"
    else:
        status = "healthy"
    temperature = mapping(payload.get("temperature")).get("current")
    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool) or not -20 <= temperature <= 150:
        temperature = None
    flags = [name for bit, name in ((16, "attribute_threshold"), (32, "attribute_threshold_history"),
                                    (64, "error_log"), (128, "self_test_log"))
             if isinstance(exit_code, int) and exit_code & bit]
    return {"identityHash": identifier, "status": status, "smartExitBitmask": exit_code,
            "diagnosticFlags": flags,
            "reason": "standby_not_woken" if standby else "read_only_smart",
            "smartPassed": passed if isinstance(passed, bool) else None,
            "temperatureC": temperature, "counters": counters}


def collect_disks(runner=command):
    code, raw = runner(["/usr/bin/lsblk", "-J", "-d", "-o", "NAME,TYPE,TRAN"])
    try:
        rows = json.loads(raw)["blockdevices"] if code == 0 else []
        names = [r["name"] for r in rows if isinstance(r, dict) and r.get("type") == "disk"]
        if len(names) > 32 or any(not isinstance(n, str) or not re.fullmatch(r"(?:sd[a-z]+|nvme\d+n\d+|mmcblk\d+)", n) for n in names):
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        return {"status": "unknown", "disks": []}
    disks = []
    for name in names:
        transport = next(r.get("tran") for r in rows if isinstance(r, dict) and r.get("name") == name)
        if transport != "sata":
            disks.append({"deviceObserved": "/dev/" + name, **smart_summary({}, None), "reason": "unreviewed_transport"})
            continue
        # Explicit ATA type avoids autodetection wake-ups. Exit unknown when the
        # ATA power check is unsupported instead of proceeding with SMART reads.
        code, raw = runner(["/usr/sbin/smartctl", "-d", "ata", "-n", "standby,2,2", "-j", "-i", "-H", "-A", "/dev/" + name])
        try:
            payload = json.loads(raw)
            summary = smart_summary(payload, code)
        except (ValueError, TypeError, AttributeError):
            summary = smart_summary({}, None)
        disks.append({"deviceObserved": "/dev/" + name, **summary})
    # Inventory success is distinct from health; absent disks never mean healthy.
    return {"status": "observed" if disks else "unknown", "disks": disks}


def read_small(path):
    try:
        with path.open() as source:
            content = source.read(65537)
        return content.strip() if len(content) <= 65536 else None
    except OSError:
        return None


def collect_raid(root=Path("/sys/block")):
    try:
        arrays = sorted(p for p in root.iterdir() if re.fullmatch(r"md\d+", p.name))[:8]
    except OSError:
        arrays = []
    records = []
    for array in arrays:
        values = {key: read_small(array / "md" / key) for key in ("array_state", "degraded", "raid_disks", "sync_action", "sync_completed")}
        degraded = int(values["degraded"]) if values["degraded"] and values["degraded"].isdigit() else None
        status = "failed" if degraded is not None and degraded > 0 else "healthy" if degraded == 0 and values["array_state"] in {"clean", "active", "active-idle"} else "unknown"
        records.append({"array": array.name, "status": status, "degradedMembers": degraded,
                        "state": values["array_state"], "syncAction": values["sync_action"], "syncCompleted": values["sync_completed"]})
    return {"status": "observed" if records else "unknown", "arrays": records}


def collect_filesystem(label, target, uuid, runner=command, usage=None):
    record = {"label": label, "mountpoint": target, "uuid": uuid, "status": "unknown", "totalBytes": None, "availableBytes": None}
    code, raw = runner(["/usr/bin/findmnt", "-J", "-T", target, "-o", "TARGET,UUID,FSTYPE"])
    try:
        observed = json.loads(raw)["filesystems"][0] if code == 0 else {}
        if observed.get("target") != target or (uuid and observed.get("uuid") != uuid):
            record["reason"] = "expected_mount_missing"
            return record
        state = (usage or os.statvfs)(target)
        record.update(status="observed", filesystem=observed.get("fstype"),
                      totalBytes=state.f_blocks * state.f_frsize, availableBytes=state.f_bavail * state.f_frsize)
    except (ValueError, TypeError, KeyError, IndexError, OSError):
        record["reason"] = "filesystem_read_unavailable"
    return record


def collect_services(runner=command):
    records = []
    for service in SERVICES:
        code, state = runner(["/usr/bin/systemctl", "is-active", service])
        status = "healthy" if code == 0 and state == "active" else "failed" if state in {"failed", "inactive"} else "unknown"
        records.append({"service": service, "status": status, "state": state if state in {"active", "inactive", "failed", "activating", "deactivating"} else "unknown"})
    return records


def snapshot():
    try:
        load = list(os.getloadavg())
    except OSError:
        load = None
    memory = {}
    for line in (read_small(Path("/proc/meminfo")) or "").splitlines():
        match = re.fullmatch(r"(MemTotal|MemAvailable):\s+(\d+) kB", line)
        if match:
            memory[match[1]] = int(match[2]) * 1024
    filesystems = [collect_filesystem("root", "/", None)] + [
        collect_filesystem(label, "/srv/dev-disk-by-uuid-" + uuid, uuid) for label, uuid in DATASETS.items()
    ]
    return {"schemaVersion": "omv-health/1.0", "observedAt": datetime.now(timezone.utc).isoformat(),
            "collector": "OMV host-local read-only preparation", "host": {"loadAverage": load, "memoryBytes": memory},
            "storage": collect_disks(), "raid": collect_raid(), "filesystems": filesystems,
            "services": collect_services(), "scope": "Point-in-time host/storage/service evidence; no backup, application, self-test or restore certification."}


if __name__ == "__main__":
    if os.name != "posix":
        raise SystemExit("Run this collector on the Linux OMV host.")
    print(json.dumps(snapshot()))
