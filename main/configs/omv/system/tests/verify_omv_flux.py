#!/usr/bin/env python3
"""Run prepared queries on synthetic arrays only; never read/write buckets."""
import argparse
import csv
import io
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

QUERIES = Path(__file__).resolve().parents[2] / "grafana" / "queries"


def point(field, value, stamp, **labels):
    return {"_measurement": "omv_health", "source": "omvnas", "schema": "omv-health/1.0",
            "_time": stamp.isoformat(), "_field": field, "_value": float(value),
            "disk": labels.get("disk", ""), "service": labels.get("service", "")}


def flags(stamp, available=1, valid=1, fresh=1, age=0):
    values = [("available", available), ("valid", valid), ("fresh", fresh)]
    if valid and age is not None:
        values.append(("age_seconds", age))
    return [point("omv_snapshot_" + name, value, stamp) for name, value in values]


def unit(stamp, name, active, load=0):
    return [{**point(field, value, stamp), "_value": int(value), "_measurement": "omv_health_unit", "name": name}
            for field, value in (("active_code", active), ("load_code", load))]


def fixture_query(source, rows, now):
    expressions = []
    for row in rows:
        parts = [f'{key}: time(v: {json.dumps(value)})' if key == "_time" else f"{key}: {json.dumps(value)}"
                 for key, value in row.items()]
        expressions.append("{" + ", ".join(parts) + "}")
    # Keep range/filter/guard logic intact, replace only bucket access.
    replacement = "array.from(rows: [" + ",\n".join(expressions) + "])"
    query, count = re.subn(r'from\(bucket: "\$\{omv_bucket\}"\)', lambda _: replacement, source)
    if count != 1 or "from(bucket:" in query or "to(bucket:" in query:
        raise ValueError("query must contain exactly one synthetic source and no bucket access")
    return 'import "array"\noption now = () => time(v: ' + json.dumps(now.isoformat()) + ')\n' + query


def parsed_rows(raw):
    # Annotated CSV can contain multiple independently headed tables.
    header = None
    rows = []
    for row in csv.reader(io.StringIO(raw)):
        if not row or row[0].startswith("#"):
            continue
        if len(row) > 1 and row[1] == "result":
            header = row
        elif header:
            rows.append(dict(zip(header, row)))
    return rows


def verify(command):
    now = datetime.now(timezone.utc)
    old, new = now - timedelta(seconds=20), now - timedelta(seconds=2)
    retained = flags(old) + [point("omv_disk_temperature_celsius", 31, old, disk="a" * 32)]
    cases = [
        ("fresh", retained + flags(new) + [point("omv_disk_temperature_celsius", 32, new, disk="a" * 32)], 1, {("omv_disk_temperature_celsius", 32.0)}),
        ("stale_over_old_healthy", retained + flags(new, fresh=0), 2, set()),
        ("invalid_over_old_healthy", retained + flags(new, valid=0, fresh=0), 3, set()),
        ("absent_over_old_healthy", retained + flags(new, available=0, valid=0, fresh=0), 4, set()),
        ("partial_flags_over_old_healthy", retained + [point("omv_snapshot_fresh", 1, new)], 0, set()),
        ("unknown_disk_drops_old_temperature", retained + flags(new) + [point("omv_disk_status", 0, new, disk="a" * 32)], 1, {("omv_disk_status", 0.0)}),
        ("collection_without_resource", retained + flags(new), 1, set()),
        ("resource_without_flags", [point("omv_disk_temperature_celsius", 32, new, disk="a" * 32)], None, set()),
        ("shipping_silence", flags(now - timedelta(minutes=3)), None, set()),
        ("wrong_source", [{**row, "source": "other"} for row in flags(new)], None, set()),
        ("age_expires_between_collections", flags(new, age=599) + [point("omv_disk_temperature_celsius", 32, new, disk="a" * 32)], 2, set()),
        ("age_at_exact_ceiling", flags(new, age=598) + [point("omv_disk_temperature_celsius", 32, new, disk="a" * 32)], 1, {("omv_disk_temperature_celsius", 32.0)}),
        ("missing_age", flags(new, age=None) + [point("omv_disk_temperature_celsius", 32, new, disk="a" * 32)], 0, set()),
    ]
    results = []
    for name, rows, state, resources in cases:
        for filename in ("snapshot-state.flux", "current-resources.flux"):
            query = fixture_query((QUERIES / filename).read_text(), rows, now)
            run = subprocess.run(command, input=query, text=True, capture_output=True, timeout=25)
            if run.returncode:
                # Engine errors relate to synthetic query text, never credentials.
                raise ValueError(f"{name}/{filename}: " + run.stderr[:1500])
            actual = parsed_rows(run.stdout)
            if filename == "snapshot-state.flux":
                values = [float(row["_value"]) for row in actual]
                if values != ([] if state is None else [float(state)]):
                    raise ValueError(f"incorrect snapshot state for {name}: {values}")
            else:
                values = {(row["_field"], float(row["_value"])) for row in actual}
                if values != resources or len(actual) != len(resources):
                    raise ValueError(f"retained/missing resource readings for {name}: {values}")
        results.append({"case": name, "queries": 2, "status": "passed"})
    service, timer = "omv-health-snapshot.service", "omv-health-snapshot.timer"
    unit_cases = [
        ("idle_producer_active_timer", unit(new, service, 2) + unit(new, timer, 0), {service: 5, timer: 1}),
        ("failed_producer_active_timer", unit(old, service, 2) + unit(new, service, 3) + unit(new, timer, 0), {service: 3, timer: 1}),
        ("stopped_timer", unit(old, timer, 0) + unit(new, timer, 2), {timer: 2}),
        ("missing_unit", unit(new, service, 2, load=2), {service: 0}),
        ("running_producer", unit(new, service, 4), {service: 4}),
        ("unit_shipping_silence", unit(now - timedelta(minutes=3), timer, 0), {}),
    ]
    for name, rows, expected in unit_cases:
        query = fixture_query((QUERIES / "producer-state.flux").read_text(), rows, now)
        run = subprocess.run(command, input=query, text=True, capture_output=True, timeout=25)
        if run.returncode:
            raise ValueError(f"{name}/producer-state.flux: " + run.stderr[:1500])
        actual = parsed_rows(run.stdout)
        values = {row["name"]: float(row["_value"]) for row in actual}
        if values != expected or len(actual) != len(expected):
            raise ValueError(f"incorrect independent unit state for {name}")
        results.append({"case": name, "queries": 1, "status": "passed"})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ssh", required=True, help="Existing monitoring SSH alias; existing container credential stays remote")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", args.ssh):
        parser.error("use a bounded SSH host alias")
    remote = ("docker exec -i influxdb sh -c 'export INFLUX_TOKEN=\"$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN\"; "
              "exec influx query --host http://localhost:8086 --org homelab --raw --file /dev/stdin'")
    command = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", args.ssh, remote]
    try:
        print(json.dumps({"rehearsal": "synthetic Flux; no bucket access", "results": verify(command)}, indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
