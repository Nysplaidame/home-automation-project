import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import assert_mounts
import assert_local_mounts
import render_cutover


class CutoverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "rendered"
        self.uuid = "11111111-2222-4333-8444-555555555555"

    def test_render_scoped_exports_and_backup_guards(self):
        names = render_cutover.render(self.uuid, self.out)
        self.assertIn("desired-omv-contract.json", names)
        data = json.loads((self.out / "desired-omv-contract.json").read_text())
        self.assertEqual(len(data["exports"]), 10)
        self.assertEqual(len({e["name"] for e in data["exports"]}), 10)
        self.assertNotIn("media", {e["name"] for e in data["exports"]})
        self.assertTrue(all(e["relative"] and e["relative"] != "/" for e in data["exports"]))
        backup = (self.out / "omv-config-backup.sh").read_text()
        self.assertNotIn("/dev/md0", backup)
        self.assertIn(self.uuid, backup)
        self.assertIn("--mountpoint", backup)
        calibre_patch = self.out / "calibre-web.compose.patch"
        calibre_source = render_cutover.MAIN / "configs/docker-host/stacks/calibre-web/docker-compose.yml"
        self.assertIn("/mnt/omv/calibre-library:/books", calibre_patch.read_text() if calibre_patch.exists()
                      else calibre_source.read_text())
        self.assertIn("backups-docker-host", (self.out / "mediamtx-config-backup.sh").read_text())
        if os.name == "posix":
            for name in ("omv-config-backup.sh", "mediamtx-config-backup.sh"):
                subprocess.run(["sh", "-n", str(self.out / name)], check=True)

    def test_old_or_invalid_uuid_and_existing_output_refused(self):
        for value in (render_cutover.OLD_Y, render_cutover.OLD_Z, "invalid"):
            with self.assertRaises(ValueError):
                render_cutover.render(value, self.out)
        self.out.mkdir()
        with self.assertRaises(ValueError):
            render_cutover.render(self.uuid, self.out)

    def test_mount_guard_rejects_local_fallback_and_wrong_export(self):
        for record in ({"source": "/dev/sda", "fstype": "ext4"},
                       {"source": "192.168.40.50:/export/media", "fstype": "nfs"}):
            result = type("Result", (), {"returncode": 0, "stdout": json.dumps({"filesystems": [record]})})()
            with patch("assert_mounts.subprocess.run", return_value=result):
                self.assertTrue(assert_mounts.check({"/mnt/media": "192.168.40.50:/export/calibre-library"}))

    def test_mount_guard_accepts_only_exact_remote_mount(self):
        result = type("Result", (), {"returncode": 0, "stdout": json.dumps({"filesystems": [
            {"source": "192.168.40.50:/export/calibre-library", "fstype": "nfs"}]})})()
        with patch("assert_mounts.subprocess.run", return_value=result):
            self.assertEqual(assert_mounts.check({"/mnt/calibre": "192.168.40.50:/export/calibre-library"}), [])

    def test_local_guard_refuses_subdirectory_and_wrong_uuid(self):
        for record in ({"source": "/dev/md0[hidden]", "fstype": "ext4", "uuid": "right"},
                       {"source": "/dev/md0", "fstype": "ext4", "uuid": "wrong"}):
            result = type("Result", (), {"returncode": 0, "stdout": json.dumps({"filesystems": [record]})})()
            with patch("assert_local_mounts.subprocess.run", return_value=result):
                self.assertEqual(assert_local_mounts.check({"/srv/view": "right"}), ["/srv/view"])


if __name__ == "__main__":
    unittest.main()
