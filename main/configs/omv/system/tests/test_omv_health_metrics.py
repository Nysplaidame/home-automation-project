import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location("omv_metrics", Path(__file__).resolve().parents[1] / "omv-health-metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
NOW = datetime(2026, 10, 4, 12, tzinfo=timezone.utc)


def snapshot():
    return {"schemaVersion": "omv-health/1.0", "observedAt": NOW.isoformat(),
            "host": {"loadAverage": [1, 2, 3], "memoryBytes": {"MemTotal": 4096}},
            "storage": {"status": "observed", "disks": [{"identityHash": "a" * 32,
                "deviceObserved": "/dev/PRIVATE", "status": "warning", "temperatureC": 30,
                "counters": {"crc": 1, "pending": None}, "serial": "PRIVATE"}]},
            "raid": {"status": "observed", "arrays": [{"array": "md0", "status": "healthy", "degradedMembers": 0}]},
            "filesystems": [{"label": "nas", "status": "observed", "totalBytes": 8192, "availableBytes": 4096}],
            "services": [{"service": "smbd", "status": "healthy"}], "token": "PRIVATE"}


class MetricsTests(unittest.TestCase):
    def test_fresh_grouped_unique_gauges_and_allowlisted_fields(self):
        output = metrics.render(snapshot(), NOW)
        self.assertIn('omv_disk_status{disk="' + "a" * 32 + '"} 2', output)
        self.assertIn('omv_disk_attribute_count{attribute="crc",disk="' + "a" * 32 + '"} 1', output)
        self.assertNotIn("PRIVATE", output)
        self.assertNotIn('attribute="pending"', output)
        types, series = set(), set()
        for line in output.splitlines():
            if line.startswith("# TYPE"):
                name = line.split()[2]
                self.assertNotIn(name, types)
                types.add(name)
            else:
                identifier, value = line.rsplit(" ", 1)
                self.assertIn(identifier.split("{")[0], types)
                self.assertNotIn(identifier, series)
                series.add(identifier)
                float(value)
        self.assertTrue(output.endswith("\n"))

    def test_stale_future_and_ambiguous_time_never_emit_resources(self):
        for observed in ((NOW - timedelta(seconds=601)).isoformat(),
                         (NOW + timedelta(seconds=1)).isoformat(), "2026-10-04T12:00:00", None):
            value = snapshot()
            value["observedAt"] = observed
            output = metrics.render(value, NOW)
            self.assertIn("omv_snapshot_fresh 0", output)
            self.assertTrue(all(line.startswith(("#", "omv_snapshot_")) for line in output.splitlines()))
        value["observedAt"] = (NOW - timedelta(seconds=600)).isoformat()
        self.assertIn("omv_snapshot_fresh 1", metrics.render(value, NOW))

    def test_unknown_null_and_bad_numbers_never_become_healthy_zero(self):
        value = snapshot()
        disk = value["storage"]["disks"][0]
        disk.update(status="unknown", temperatureC=33, counters={"crc": 5})
        value["filesystems"][0].update(status="unknown")
        value["host"] = {"loadAverage": [True, float("nan"), -1], "memoryBytes": {"MemTotal": None}}
        output = metrics.render(value, NOW)
        self.assertIn('"} 0', output)
        for name in ("disk_temperature", "disk_attribute", "filesystem_bytes", "host_load", "host_memory"):
            self.assertNotIn("omv_" + name, output)
        disk.update(status="healthy", temperatureC=True, counters={"crc": False})
        output = metrics.render(value, NOW)
        self.assertNotIn("omv_disk_temperature", output)
        self.assertNotIn("omv_disk_attribute", output)

    def test_duplicate_untrusted_and_unbounded_identities_fail_closed(self):
        for mutate in (lambda v: v["storage"]["disks"].append(dict(v["storage"]["disks"][0])),
                       lambda v: v["services"][0].update(service='smbd"\nINJECT'),
                       lambda v: v["raid"].update(arrays=[{}] * 9),
                       lambda v: v.update(host=[])):
            value = snapshot()
            mutate(value)
            output = metrics.render(value, NOW)
            self.assertIn("omv_snapshot_valid 0", output)
            self.assertNotIn("omv_disk_", output)
        value = snapshot()
        value["storage"]["disks"][0]["identityHash"] = None
        output = metrics.render(value, NOW)
        self.assertIn("omv_disk_identity_missing 1", output)
        self.assertNotIn("omv_disk_status", output)

    def test_bounded_file_reader_and_duplicate_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_bytes(b"\xef\xbb\xbf" + json.dumps(snapshot()).encode())
            self.assertTrue(metrics.read_snapshot(path)[1])
            path.write_text('{"schemaVersion":"omv-health/1.0","schemaVersion":"evil"}')
            self.assertEqual(metrics.read_snapshot(path), (None, True))
            path.write_bytes(b"x" * (metrics.MAX_BYTES + 1))
            with self.assertRaises(OSError):
                metrics.read_snapshot(path)
            with self.assertRaises(OSError):
                metrics.read_snapshot(Path(directory) / "missing")
            if os.name == "posix":
                link = Path(directory) / "link"
                link.symlink_to(path)
                with self.assertRaises(OSError):
                    metrics.read_snapshot(link)
            self.assertIn("omv_snapshot_available 0", metrics.render(None, NOW, False))

    def test_unknown_inventory_suppresses_cached_disk_and_raid_readings(self):
        value = snapshot()
        value["storage"]["status"] = "unknown"
        value["raid"]["status"] = "unknown"
        output = metrics.render(value, NOW)
        self.assertIn("omv_storage_observed 0", output)
        self.assertIn("omv_raid_observed 0", output)
        self.assertNotIn("omv_disk_status", output)
        self.assertNotIn("omv_raid_status", output)

    def test_cli_reports_absent_invalid_and_stale_files_without_payload_leaks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            for content, available, valid in ((None, 0, 0), ("PRIVATE malformed", 1, 0),
                                              (json.dumps({**snapshot(), "observedAt": "2020-01-01T00:00:00Z"}), 1, 1)):
                if content is not None:
                    path.write_text(content)
                result = subprocess.run([sys.executable, "-B", spec.origin, str(path)], capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stderr, "")
                self.assertIn(f"omv_snapshot_available {available}", result.stdout)
                self.assertIn(f"omv_snapshot_valid {valid}", result.stdout)
                self.assertIn("omv_snapshot_fresh 0", result.stdout)
                self.assertNotIn("PRIVATE", result.stdout)
                self.assertNotIn("omv_disk_status", result.stdout)


if __name__ == "__main__":
    unittest.main()
