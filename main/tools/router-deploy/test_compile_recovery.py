"""Offline regression checks for post-fibre deploy safety; uses dummy secrets only."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("router_compile", Path(__file__).with_name("compile.py"))
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class RecoveryCompileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.secrets = root / "secrets.json"
        self.out = root / "generated"
        for attr, value in (("SECRETS_PATH", self.secrets), ("OUT_DIR", self.out)):
            p = patch.object(module, attr, value)
            p.start()
            self.addCleanup(p.stop)

    def compile(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return module.compile_artifacts(**kwargs)

    def test_missing_wan_credentials_block_every_deploy_profile(self):
        for profile in ("first-flight", "full"):
            self.assertEqual(self.compile(profile=profile), 1)
        self.assertFalse(self.out.exists())

    def test_first_flight_injects_dummy_wan_and_preserves_isolation(self):
        self.secrets.write_text(json.dumps(dict(zip(module.WAN_SECRET_KEYS, ("dummy@zen", "dummy-password")))))
        self.assertEqual(self.compile(profile="first-flight"), 0)
        network = (self.out / "network.uci").read_text()
        self.assertIn("option username 'dummy@zen'", network)
        summary = json.loads((self.out / "summary.json").read_text())
        self.assertTrue(summary["invariants"]["lan2_only_cloud_vlan"])
        self.assertTrue(summary["architecture_invariants"]["cloud_only_wan_forwarding"])
        self.assertEqual(summary["counts"]["vlan_count"], 11)

    def test_unsafe_wan_secret_is_rejected_without_artifacts(self):
        for value in ("bad'quote", "bad\nline", "bad\rline", "bad\x00nul"):
            self.secrets.write_text(json.dumps({module.WAN_SECRET_KEYS[0]: "dummy@zen", module.WAN_SECRET_KEYS[1]: value}))
            self.assertEqual(self.compile(profile="first-flight"), 1)
        self.assertFalse(self.out.exists())

    def test_regressed_wan_or_lan2_fails_invariants(self):
        original = (module.CONF_DIR / "vlan-config.conf").read_text(encoding="utf-8")
        for broken in (original.replace("option device 'eth1'", "option device 'wan'"), original.replace("option vlan '55'", "option vlan '10'")):
            checks = module._validate_invariants(module.parse_uci_declarative(broken))
            self.assertTrue(any(v is False for v in checks.values()))

if __name__ == "__main__":
    unittest.main()
