import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import verify_copy


@unittest.skipUnless(os.name == "posix", "Linux descriptor and xattr verification")
class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.target = self.base / "target"
        self.source.mkdir()
        (self.source / ".hidden").write_bytes(b"alpha")
        (self.source / "empty").mkdir()
        self.report = self.base / "report.jsonl"

    def copy(self):
        shutil.copytree(self.source, self.target, symlinks=True)

    def check(self):
        result = verify_copy.verify(self.source, self.target, self.report)
        rows = [json.loads(line) for line in self.report.read_text().splitlines()]
        self.assertEqual(rows[-1]["status"], "complete")
        return result, [r["reason"] for r in rows if r["status"] == "issue"]

    def test_identical_hidden_and_empty(self):
        self.copy()
        result, _ = self.check()
        self.assertEqual(result, {"checked": 3, "issues": 0})

    def test_same_size_wrong_content(self):
        self.copy()
        (self.target / ".hidden").write_bytes(b"omega")
        shutil.copystat(self.source / ".hidden", self.target / ".hidden")
        self.assertIn("SHA256 differs", self.check()[1])

    def test_missing_and_unexpected(self):
        self.copy()
        (self.target / ".hidden").unlink()
        (self.target / "unexpected").write_bytes(b"x")
        reasons = self.check()[1]
        self.assertIn("missing destination entry", reasons)
        self.assertIn("unexpected destination entry", reasons)

    def test_permission_difference(self):
        self.copy()
        (self.target / ".hidden").chmod(0o600)
        (self.source / ".hidden").chmod(0o644)
        self.assertIn("metadata differs", self.check()[1])

    def test_xattr_difference(self):
        os.setxattr(self.source / ".hidden", "user.migration-test", b"one")
        self.copy()
        os.setxattr(self.target / ".hidden", "user.migration-test", b"two")
        self.assertIn("metadata differs", self.check()[1])

    def test_symlink_target_difference(self):
        (self.source / "link").symlink_to(".hidden")
        self.copy()
        (self.target / "link").unlink()
        (self.target / "link").symlink_to("outside")
        self.assertIn("Symlink targets differ", self.check()[1])

    def test_does_not_follow_symlink(self):
        (self.source / "link").symlink_to("/nonexistent/outside")
        self.copy()
        self.assertEqual(self.check()[0]["issues"], 0)

    def test_split_hardlink_group(self):
        os.link(self.source / ".hidden", self.source / "second")
        self.copy()
        self.assertIn("Source hardlink group was split", self.check()[1])

    def test_preserved_hardlink_group(self):
        os.link(self.source / ".hidden", self.source / "second")
        self.copy()
        (self.target / "second").unlink()
        os.link(self.target / ".hidden", self.target / "second")
        shutil.copystat(self.source, self.target)
        self.assertEqual(self.check()[0]["issues"], 0)

    def test_independent_files_accidentally_hardlinked(self):
        (self.source / "second").write_bytes(b"alpha")
        shutil.copystat(self.source / ".hidden", self.source / "second")
        self.copy()
        (self.target / "second").unlink()
        os.link(self.target / ".hidden", self.target / "second")
        shutil.copystat(self.source, self.target)
        self.assertIn("Independent source files became hardlinked", self.check()[1])

    def test_archived_socket_and_fifo(self):
        import socket
        self.copy()
        sockets = []
        for root in (self.source, self.target):
            os.mkfifo(root / "pipe")
            sock = socket.socket(socket.AF_UNIX)
            self.addCleanup(sock.close)
            sock.bind(str(root / "socket"))
            sockets.append(sock)
        for name in ("pipe", "socket"):
            shutil.copystat(self.source / name, self.target / name)
        shutil.copystat(self.source, self.target)
        self.assertEqual(self.check()[0]["issues"], 0)

    def test_sparse_file_materialisation_is_reported(self):
        with (self.source / "sparse").open("wb") as stream:
            stream.seek(2 * 1024 * 1024)
            stream.write(b"end")
        self.copy()
        self.assertIn("Sparse file became fully allocated", self.check()[1])

    @unittest.skipUnless(shutil.which("rsync") and shutil.which("setfacl"), "Requires rsync and ACL utilities")
    def test_rsync_metadata_roundtrip(self):
        import socket
        named = self.source / "space 日本語"
        named.write_bytes(b"content")
        os.setxattr(named, "user.migration-test", b"value")
        subprocess.run(["setfacl", "-m", "u:100000:r--", str(named)], check=True)
        os.link(self.source / ".hidden", self.source / "hardlink")
        os.symlink(".hidden", self.source / "relative-link")
        with (self.source / "sparse").open("wb") as stream:
            stream.seek(2 * 1024 * 1024)
            stream.write(b"end")
        os.mkfifo(self.source / "pipe")
        sock = socket.socket(socket.AF_UNIX)
        sock.bind(str(self.source / "socket"))
        sock.close()
        self.target.mkdir()
        command = ["rsync", "-aHAXSx", "--numeric-ids", "--protect-args", "--modify-window=-1",
                   "--", str(self.source) + "/", str(self.target) + "/"]
        subprocess.run(command[:1] + ["--dry-run"] + command[1:], check=True, capture_output=True)
        self.assertEqual(list(self.target.iterdir()), [])
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(self.check()[0]["issues"], 0)

    def test_source_changes_during_hashing(self):
        self.copy()
        original = verify_copy.digest
        calls = 0
        def mutate(fd):
            nonlocal calls
            value = original(fd)
            calls += 1
            if calls == 1:
                (self.source / ".hidden").write_bytes(b"omega")
            return value
        with patch("verify_copy.digest", side_effect=mutate):
            self.assertTrue(any("changed during comparison" in r for r in self.check()[1]))

    def test_existing_and_internal_reports_refused(self):
        self.copy()
        self.report.write_text("keep")
        with self.assertRaises(ValueError):
            verify_copy.verify(self.source, self.target, self.report)
        self.assertEqual(self.report.read_text(), "keep")
        with self.assertRaises(ValueError):
            verify_copy.verify(self.source, self.target, self.source / "report")

    def test_source_exclusion_does_not_hide_destination_extras(self):
        (self.source / "Print").mkdir()
        (self.source / "Print/retain").write_text("source only")
        self.copy()
        result = verify_copy.verify(self.source, self.target, self.report, {"Print"})
        self.assertGreater(result["issues"], 0)
        self.assertTrue((self.source / "Print/retain").exists())

    def test_root_alias_and_type_conflicts(self):
        self.copy()
        with self.assertRaises(ValueError):
            verify_copy.verify(self.source, self.source, self.report)
        (self.target / ".hidden").unlink()
        (self.target / ".hidden").mkdir()
        self.assertIn("Entry types differ", self.check()[1])


if __name__ == "__main__":
    unittest.main()
