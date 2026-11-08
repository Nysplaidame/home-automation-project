import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location("omv_snapshot", Path(__file__).resolve().parents[1] / "omv-health-snapshot.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class OmvSnapshotTests(unittest.TestCase):
    def test_smart_bitmask_warnings_identity_and_missing_attributes(self):
        value = {"serial_number": "SYNTHETIC-SERIAL", "smart_status": {"passed": True}, "temperature": {"current": 34}}
        result = collector.smart_summary(value, 0)
        self.assertEqual(result["status"], "healthy")
        self.assertIsNone(result["counters"]["pending"])
        self.assertNotIn("SYNTHETIC-SERIAL", json.dumps(result))
        self.assertEqual(result["identityHash"], collector.smart_summary(value, 0)["identityHash"])
        for code in (16, 32, 64, 128):
            self.assertEqual(collector.smart_summary(value, code)["status"], "warning")
        for code in (1, 2, 4, None):
            self.assertEqual(collector.smart_summary(value, code)["status"], "unknown")
        self.assertEqual(collector.smart_summary(value, 8)["status"], "failed")
        value["ata_smart_attributes"] = {"table": [{"id": 197, "raw": {"value": 1}}]}
        self.assertEqual(collector.smart_summary(value, 0)["status"], "warning")

    def test_standby_and_collection_do_not_wake_or_start_tests(self):
        calls = []
        def runner(args):
            calls.append(args)
            if "lsblk" in args[0]:
                return 0, json.dumps({"blockdevices": [{"name": "sda", "type": "disk", "tran": "sata"}]})
            return 2, json.dumps({"power_mode": "STANDBY"})
        result = collector.collect_disks(runner)
        self.assertEqual(result["disks"][0]["status"], "unknown")
        self.assertEqual(result["disks"][0]["reason"], "standby_not_woken")
        self.assertIn("-n", calls[1]); self.assertIn("standby,2,2", calls[1]); self.assertNotIn("-t", calls[1])
        self.assertIn("ata", calls[1])
        self.assertEqual(collector.collect_disks(lambda args: (1, ""))["status"], "unknown")

    def test_missing_mount_cannot_report_root_disk_capacity_as_nas(self):
        runner = lambda args: (0, json.dumps({"filesystems": [{"target": "/", "uuid": "other"}]}))
        def forbidden(path):
            self.fail("statvfs called for missing expected mount")
        result = collector.collect_filesystem("nas", "/srv/expected", "uuid", runner, forbidden)
        self.assertEqual(result["status"], "unknown"); self.assertIsNone(result["totalBytes"])
        runner = lambda args: (0, json.dumps({"filesystems": [{"target": "/srv/expected", "uuid": "uuid", "fstype": "ext4"}]}))
        result = collector.collect_filesystem("nas", "/srv/expected", "uuid", runner, lambda p: SimpleNamespace(f_blocks=100, f_bavail=20, f_frsize=4096))
        self.assertEqual(result["availableBytes"], 81920)

    def test_raid_degradation_is_separate_from_consistency_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); md = root / "md0" / "md"; md.mkdir(parents=True)
            for name, value in {"degraded": "0", "array_state": "active", "sync_action": "check"}.items():
                (md / name).write_text(value)
            result = collector.collect_raid(root)["arrays"][0]
            self.assertEqual(result["status"], "healthy"); self.assertEqual(result["syncAction"], "check")
            (md / "degraded").write_text("1")
            self.assertEqual(collector.collect_raid(root)["arrays"][0]["status"], "failed")
            (md / "degraded").unlink()
            self.assertEqual(collector.collect_raid(root)["arrays"][0]["status"], "unknown")

    def test_service_collection_only_calls_read_only_known_units(self):
        calls = []
        def runner(args):
            calls.append(args)
            return (0, "active") if args[-1] == "smbd" else (3, "inactive")
        result = collector.collect_services(runner)
        self.assertEqual(result[0]["status"], "healthy"); self.assertEqual(result[1]["status"], "failed")
        self.assertTrue(all(args[1] == "is-active" for args in calls))

    def test_malformed_disk_json_and_unsafe_device_names_stay_unknown(self):
        for raw in ('not-json', '{"blockdevices": null}', '{"blockdevices": [{"type":"disk","name":"../../etc/passwd"}]}'):
            calls = []
            def runner(args):
                calls.append(args)
                return 0, raw
            self.assertEqual(collector.collect_disks(runner)["status"], "unknown")
            self.assertEqual(len(calls), 1)
        value = {"smart_status": "malformed", "temperature": [], "ata_smart_attributes": None}
        self.assertEqual(collector.smart_summary(value, 0)["status"], "unknown")
        calls = []
        def unreviewed(args):
            calls.append(args)
            return 0, '{"blockdevices": [{"name":"sda","type":"disk","tran":"usb"}]}'
        result = collector.collect_disks(unreviewed)
        self.assertEqual(result["disks"][0]["reason"], "unreviewed_transport")
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
