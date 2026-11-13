import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("omv_publish", Path(__file__).resolve().parents[1] / "omv-health-publish.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def snapshot():
    return {"schemaVersion": "omv-health/1.0", "observedAt": datetime.now(timezone.utc).isoformat(),
            "collector": "synthetic", "host": {}, "storage": {"status": "unknown"}, "raid": {},
            "filesystems": [], "services": [], "scope": "fixture only"}


class EncodingTests(unittest.TestCase):
    def test_stale_ambiguous_extra_fields_and_nonfinite_values_are_refused(self):
        for value in ({**snapshot(), "observedAt": "2026-01-01T00:00:00+00:00"},
                      {**snapshot(), "observedAt": "2026-10-04T10:00:00"},
                      {**snapshot(), "token": "PRIVATE-MARKER"}, {**snapshot(), "host": {"load": float("nan")}}):
            with self.assertRaises(ValueError):
                publisher.encode_snapshot(value)


@unittest.skipUnless(os.name == "posix", "requires Linux permissions and flock")
class AtomicPublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def publish(self, value=None):
        publisher.publish_snapshot(value or snapshot(), self.root, os.getgid())

    def test_atomic_replacement_has_private_permissions_and_no_temporary_file(self):
        self.publish()
        target = self.root / "snapshot.json"
        self.assertEqual(target.stat().st_mode & 0o777, 0o640)
        inode = target.stat().st_ino
        updated = snapshot(); updated["storage"] = {"status": "observed"}
        self.publish(updated)
        self.assertNotEqual(target.stat().st_ino, inode)
        self.assertEqual(json.loads(target.read_text())["storage"]["status"], "observed")
        self.assertEqual(list(self.root.glob(".snapshot-*")), [])

    def test_failed_replace_retains_prior_timestamp_and_cleans_temporary_file(self):
        self.publish()
        prior = (self.root / "snapshot.json").read_bytes()
        with patch.object(publisher.os, "replace", side_effect=OSError("synthetic failure")):
            with self.assertRaises(OSError):
                self.publish()
        self.assertEqual((self.root / "snapshot.json").read_bytes(), prior)
        self.assertEqual(list(self.root.glob(".snapshot-*")), [])

    def test_symlink_hardlink_and_writable_directory_are_refused(self):
        outside = self.root / "outside"; outside.write_text("unchanged")
        target = self.root / "snapshot.json"
        target.symlink_to(outside)
        with self.assertRaises(ValueError): self.publish()
        target.unlink(); os.link(outside, target)
        with self.assertRaises(ValueError): self.publish()
        self.assertEqual(outside.read_text(), "unchanged")
        target.unlink(); self.root.chmod(0o770)
        with self.assertRaises(ValueError): self.publish()

    def test_held_lock_prevents_overlapping_publication(self):
        import fcntl
        self.publish()
        previous = (self.root / "snapshot.json").read_bytes()
        with (self.root / ".publish.lock").open("r+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError): self.publish()
        self.assertEqual((self.root / "snapshot.json").read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
