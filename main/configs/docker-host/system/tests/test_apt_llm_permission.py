"""Execute under Linux/WSL; all UFW calls use an isolated fake executable."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "docker-host-ufw-apt-llm.sh"


@unittest.skipUnless(os.name == "posix", "requires POSIX shell")
class AptPermissionTests(unittest.TestCase):
    def invoke(self, args):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = root / "ufw"
            output = root / "calls"
            fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$TEST_CALLS"\n')
            fake.chmod(0o700)
            result = subprocess.run(
                ["/bin/sh", str(SCRIPT), *args],
                env=dict(os.environ, UFW_BIN=str(fake), TEST_CALLS=str(output)),
                capture_output=True, text=True,
            )
            return result, output.read_text().splitlines() if output.exists() else []

    def test_default_is_dry_run_and_host_scoped(self):
        result, calls = self.invoke([])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls, ["--dry-run", "allow", "in", "from", "192.168.20.104", "to", "192.168.20.102", "port", "3142", "proto", "tcp", "comment", "CT114 to APT cache"])

    def test_apply_requires_explicit_flag(self):
        result, calls = self.invoke(["--apply"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls[0], "allow")
        self.assertNotIn("route", calls)
        self.assertNotIn("reload", calls)

    def test_unknown_or_extra_arguments_never_invoke_ufw(self):
        for args in (["--force"], ["--apply", "extra"]):
            result, calls = self.invoke(args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(calls, [])
