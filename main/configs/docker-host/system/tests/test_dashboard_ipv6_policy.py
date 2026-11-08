"""Run source ruleset against isolated recording executables, never real rules."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "docker-host-firewall.sh"


@unittest.skipUnless(os.name == "posix", "requires POSIX shell")
class DashboardIPv6PolicyTests(unittest.TestCase):
    def test_dashboard_new_ipv6_connections_drop_without_tailnet_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / "calls"
            for name in ("iptables", "ip6tables"):
                command = root / name
                command.write_text('#!/bin/sh\nprintf "%s" "${0##*/}" >> "$POLICY_CALLS"\nprintf " %s" "$@" >> "$POLICY_CALLS"\nprintf "\\n" >> "$POLICY_CALLS"\n')
                command.chmod(0o700)
            # Normalize checkout line endings without editing the maintained file.
            source = root / "policy.sh"
            source.write_text(SCRIPT.read_text())
            result = subprocess.run(["/bin/sh", str(source)],
                                    env=dict(os.environ, PATH=str(root), POLICY_CALLS=str(log)),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            calls = log.read_text().splitlines()
        ipv6 = [call for call in calls if call.startswith("ip6tables -A")]
        rules = [call for call in ipv6 if "--ctorigdstport 8094 " in call]
        self.assertEqual(rules, ["ip6tables -A DOCKER-USER -p tcp -m conntrack --ctorigdstport 8094 -j DROP"])
        self.assertLess(ipv6.index(rules[0]), ipv6.index("ip6tables -A DOCKER-USER -j RETURN"))
        self.assertIn("ip6tables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN", ipv6)
        expected_ports = {2283, 3001, 5984, 8000, 8080, 8081, 8083, 8084, 8085, 8087, 8088, 8090, 8091, 8092, 8093, 8096, 8100, 8420, 8554, 9283, 9925, 31337}
        returns = [call for call in ipv6 if "-i tailscale0 " in call and call.endswith("-j RETURN")]
        self.assertEqual({int(call.split("--ctorigdstport ")[1].split()[0]) for call in returns}, expected_ports)
