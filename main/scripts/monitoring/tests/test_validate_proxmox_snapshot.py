import importlib.util
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_proxmox_snapshot.py"
SPEC = importlib.util.spec_from_file_location("validate_proxmox_snapshot", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


def accepted_snapshot():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "collector": "Proxmox host",
        "checks": {key: "pass" for key in validator.REQUIRED_CHECKS},
    }


class ValidateProxmoxSnapshotTests(unittest.TestCase):
    def test_acceptance_rejects_stale_ambiguous_and_future_evidence(self):
        for stamp in ["2020-01-01T00:00:00Z", "2026-09-07 12:00:00", "invalid",
                      (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()]:
            snapshot = accepted_snapshot()
            snapshot["timestamp"] = stamp
            errors, _ = validator.validate_snapshot(snapshot, require_pass=True)
            self.assertTrue(errors)

    def test_legacy_timestamp_requires_explicit_collector_offset(self):
        snapshot = accepted_snapshot()
        snapshot["timestamp"] = "2026-09-07 22:00:00"
        errors, _ = validator.validate_snapshot(snapshot, require_pass=True,
            now=datetime(2026, 9, 7, 21, 30, tzinfo=timezone.utc), timestamp_offset="+01:00")
        self.assertEqual(errors, [])

    def test_accepts_complete_passing_snapshot(self):
        errors, statuses = validator.validate_snapshot(accepted_snapshot(), require_pass=True)
        self.assertEqual(errors, [])
        self.assertEqual(set(statuses), set(validator.REQUIRED_CHECKS))

    def test_reports_missing_required_check(self):
        snapshot = accepted_snapshot()
        del snapshot["checks"]["backup_ct114"]
        errors, _ = validator.validate_snapshot(snapshot, require_pass=True)
        self.assertIn("Missing required check: backup_ct114.", errors)

    def test_refuses_non_passing_evidence_at_acceptance_gate(self):
        snapshot = accepted_snapshot()
        snapshot["checks"]["frigate_mount"] = {"status": "warn", "detail": "ignored"}
        errors, statuses = validator.validate_snapshot(snapshot, require_pass=True)
        self.assertIn("Acceptance requires frigate_mount to pass; observed warn.", errors)
        self.assertEqual(statuses["frigate_mount"], "warn")

    def test_rejects_non_proxmox_collector(self):
        snapshot = accepted_snapshot()
        snapshot["collector"] = "Windows management workstation"
        errors, _ = validator.validate_snapshot(snapshot, require_pass=True)
        self.assertIn("Collector must be exactly 'Proxmox host'.", errors)


if __name__ == "__main__":
    unittest.main()
