"""Offline Linux regression tests: all Docker calls are mocked."""
import gzip
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "backup-gardenkeeper.sh"

class BackupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.backups = self.root / "backups"
        self.backups.mkdir()
        self.old = self.backups / "gardenkeeper-postgres-20000101T000000Z.sql.gz"
        self.old.write_bytes(b"preserve-on-failure")
        os.utime(self.old, (time.time()-30*86400,)*2)
        self.env = dict(os.environ, GARDENKEEPER_STACK_DIR=str(self.root), PATH=str(self.bin)+":"+os.environ["PATH"])

    def tearDown(self):
        self.tmp.cleanup()

    def stub(self, name, body):
        p = self.bin / name
        p.write_text("#!/bin/sh\n"+body+"\n")
        p.chmod(0o755)

    def run_backup(self):
        return subprocess.run(["/bin/sh", str(SCRIPT)], env=self.env, capture_output=True, text=True)

    def assert_failure(self):
        result = self.run_backup()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("backup written:", result.stdout)
        self.assertTrue(self.old.exists())
        self.assertEqual(list(self.backups.glob("*.sql.gz")), [self.old])
        self.assertFalse(list(self.backups.glob(".checkpoint.*")))
        self.assertFalse((self.backups / ".backup-lock").exists())

    def test_dump_failure_after_partial_output(self):
        self.stub("docker", "printf partial; exit 7")
        self.assert_failure()

    def test_empty_dump(self):
        self.stub("docker", "exit 0")
        self.assert_failure()

    def test_compressor_failure(self):
        self.stub("docker", "printf 'SELECT 1;' ")
        self.stub("gzip", "exit 9")
        self.assert_failure()

    def test_invalid_compressed_output(self):
        real_gzip = shutil.which("gzip")
        self.stub("docker", "printf 'SELECT 1;' ")
        self.stub("gzip", 'if [ "$1" = "-c" ]; then printf corrupt; else exec '+real_gzip+' "$@"; fi')
        self.assert_failure()

    def test_invalid_retention(self):
        self.env["GARDENKEEPER_BACKUP_RETENTION_DAYS"] = "-1"
        self.stub("docker", "exit 99")
        self.assert_failure()

    def test_concurrent_lock(self):
        (self.backups / ".backup-lock").mkdir()
        self.stub("docker", "exit 99")
        result = self.run_backup()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.old.exists())
        self.assertTrue((self.backups / ".backup-lock").exists())

    def test_success_publishes_then_prunes(self):
        self.stub("docker", "printf 'SELECT 1;' ")
        result = self.run_backup()
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list(self.backups.glob("*.sql.gz"))
        self.assertEqual(len(files), 1)
        self.assertFalse(self.old.exists())
        self.assertEqual(gzip.decompress(files[0].read_bytes()), b"SELECT 1;")
        self.assertEqual(files[0].stat().st_mode & 0o777, 0o600)
        self.assertFalse((self.backups / ".backup-lock").exists())

if __name__ == "__main__":
    unittest.main()
