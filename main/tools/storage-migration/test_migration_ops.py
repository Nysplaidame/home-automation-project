import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import migration_ops as ops


@unittest.skipUnless(os.name == "posix", "Linux atomic rename and journaling")
class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.data = self.base / "data"
        self.data.mkdir()
        (self.data / "Print").mkdir()
        (self.data / "Print/file").write_text("original")
        (self.data / "Print/empty").mkdir()
        self.root = ops.Root(self.data, None)
        self.addCleanup(self.root.close)
        self.state = self.base / "state"

    def prepare(self):
        return ops.prepare(self.root, self.state, [("Print/file", "file"), ("Print/empty", "empty")])

    def test_crash_after_rename_resumes_without_overwrite(self):
        self.prepare()
        with self.assertRaises(RuntimeError):
            ops.apply(self.root, self.state, interrupt_after=0)
        self.assertEqual((self.data / "file").read_text(), "original")
        ops.apply(self.root, self.state)
        ops.apply(self.root, self.state)
        self.assertEqual(self.root.names("Print"), [])
        self.assertEqual((self.data / "file").read_text(), "original")

    def test_interrupted_plan_can_roll_back(self):
        before = self.root.meta("Print")
        self.prepare()
        with self.assertRaises(RuntimeError):
            ops.apply(self.root, self.state, interrupt_after=0)
        ops.apply(self.root, self.state, reverse=True)
        self.assertEqual((self.data / "Print/file").read_text(), "original")
        self.assertFalse((self.data / "file").exists())
        self.assertEqual(self.root.meta("Print"), before)

    def test_late_destination_never_replaced(self):
        self.prepare()
        (self.data / "file").write_text("new destination")
        with self.assertRaises(ValueError):
            ops.apply(self.root, self.state)
        self.assertEqual((self.data / "file").read_text(), "new destination")
        self.assertEqual((self.data / "Print/file").read_text(), "original")

    def test_nonempty_wrapper_refused_then_empty_wrapper_removed(self):
        self.prepare()
        ops.apply(self.root, self.state)
        (self.data / "Print/late").write_text("retain")
        with self.assertRaises(ValueError):
            ops.remove_empty_wrapper(self.root, self.state, "Print")
        self.assertEqual((self.data / "Print/late").read_text(), "retain")
        (self.data / "Print/late").unlink()  # disposable fixture only
        ops.remove_empty_wrapper(self.root, self.state, "Print")
        ops.remove_empty_wrapper(self.root, self.state, "Print")
        self.assertFalse((self.data / "Print").exists())
        with self.assertRaises(ValueError):
            ops.apply(self.root, self.state, reverse=True)

    def test_partial_wrapper_plan_cannot_authorize_removal(self):
        ops.prepare(self.root, self.state, [("Print/file", "file")])
        ops.apply(self.root, self.state)
        (self.data / "Print/empty").rmdir()  # simulate an outside actor
        with self.assertRaises(ValueError):
            ops.remove_empty_wrapper(self.root, self.state, "Print")

    def test_torn_completion_record_is_recovered(self):
        self.prepare()
        with self.assertRaises(RuntimeError):
            ops.apply(self.root, self.state, interrupt_after=0)
        with (self.state / "journal.jsonl").open("ab") as stream:
            stream.write(b'{"event":"do')
        ops.apply(self.root, self.state)
        self.assertEqual(self.root.names("Print"), [])

    def test_unsafe_paths_and_duplicate_targets(self):
        for path in ["../outside", "/outside", "Print/../file"]:
            with self.assertRaises(ValueError):
                ops.relative(path)
        with self.assertRaises(ValueError):
            ops.prepare(self.root, self.state, [("Print/file", "file"), ("Print/empty", "FILE")])
        self.assertFalse(self.state.exists())

    def test_symlink_parent_refused(self):
        (self.data / "escape").symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(OSError):
            ops.prepare(self.root, self.state, [("Print/file", "escape/stolen")])
        self.assertTrue((self.data / "Print/file").exists())

    def test_activation_closes_rollback(self):
        self.prepare()
        ops.apply(self.root, self.state)
        ops.append_event(self.state / "journal.jsonl", {"event": "activated"})
        with self.assertRaises(ValueError):
            ops.apply(self.root, self.state, reverse=True)

    def test_wrong_root_refused(self):
        self.prepare()
        other = self.base / "other"
        other.mkdir()
        root = ops.Root(other, None)
        try:
            with self.assertRaises(ValueError):
                ops.apply(root, self.state)
        finally:
            root.close()

    def test_wrong_mount_uuid_rejected_before_opening_root(self):
        response = type("Result", (), {"stdout": json.dumps({"filesystems": [
            {"uuid": "wrong", "fstype": "ext4"}]})})()
        with patch("migration_ops.subprocess.run", return_value=response):
            with self.assertRaises(ValueError):
                ops.Root(self.data, "expected")

    def test_metadata_rollback(self):
        desired = self.root.meta("Print")
        desired["mode"] = 0o700
        before = self.root.meta("Print")
        ops.prepare(self.root, self.state, [], metadata={"Print": desired})
        ops.apply(self.root, self.state)
        self.assertEqual(self.root.meta("Print"), desired)
        ops.apply(self.root, self.state, reverse=True)
        self.assertEqual(self.root.meta("Print"), before)

    def test_copy_command_is_preview_without_destructive_flags(self):
        cmd = ops.copy_command("/source with spaces", "/target", exclude_print=True)
        self.assertIn("--dry-run", cmd)
        self.assertIn("--exclude=/Print/", cmd)
        self.assertNotIn("--delete", cmd)
        self.assertNotIn("--remove-source-files", cmd)
        self.assertEqual(cmd[-2:], ["/source with spaces/", "/target/"])


if __name__ == "__main__":
    unittest.main()
