"""Offline mount-boundary regressions; never reaches production paths."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'mediamtx-config-backup.sh'

class MountBoundaryTests(unittest.TestCase):
    def check_rejected(self, mount_status):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name,body in {'mountpoint':f'exit {mount_status}', 'findmnt':'printf "unexpected-server:/wrong-export\\n"', 'docker':'touch "'+str(root/'docker-called')+'"; exit 0'}.items():
                file=root/name
                file.write_text('#!/bin/sh\n'+body+'\n')
                file.chmod(0o755)
            result=subprocess.run(['/bin/sh',str(SCRIPT)],env=dict(os.environ,PATH=str(root)+':'+os.environ['PATH']),capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((root/'docker-called').exists())

    def test_missing_mount_stops_before_docker(self):
        self.check_rejected(1)

    def test_wrong_export_stops_before_docker(self):
        self.check_rejected(0)

if __name__=='__main__': unittest.main()
