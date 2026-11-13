import importlib.util
import json
import unittest
import http.client
import socket
import tempfile
import threading
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parents[1]))
spec = importlib.util.spec_from_file_location("api", Path(__file__).parents[1] / "diagnostic_api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class DiagnosticTests(unittest.TestCase):
    def test_command_boundaries(self):
        for command in ["ping frigate", "dns docker", "tcp monitoring 3000", "http monitoring", 'tls docker', 'tls vault']:
            api.command_args(command)
        for command in [None, {}, "ping 1.1.1.1", "ping frigate;id", "tcp docker 22", "http router", "dns docker extra", "rm -rf /", "tcp docker 65536", "ping " + "x" * 100, 'tls nas', 'tls docker 443']:
            with self.assertRaises(ValueError):
                api.command_args(command)

    @patch.object(api.subprocess, "run")
    def test_ping_is_literal_bounded_and_truncated(self, run):
        run.return_value = MagicMock(returncode=1, stdout="x" * 9000, stderr="")
        result = api.probe("ping frigate")
        self.assertFalse(result["ok"])
        self.assertEqual(len(result["output"]), 6000)
        self.assertEqual(run.call_args.args[0][-1], "192.168.30.20")
        self.assertEqual(run.call_args.kwargs["timeout"], 7)
        self.assertNotIn("shell", run.call_args.kwargs)

    @patch.object(api.socket, "create_connection", side_effect=TimeoutError)
    def test_tcp_failure_is_evidence(self, connect):
        result = api.probe("tcp monitoring 3000")
        self.assertFalse(result["ok"])
        self.assertIn("Connection failed", result["output"])

    @patch.object(api.subprocess, "run", side_effect=api.subprocess.TimeoutExpired("ping", 7))
    def test_probe_timeout(self, run):
        self.assertEqual(api.probe("ping docker")["output"], "Check timed out.")

    @patch.object(api.Path, "stat", side_effect=FileNotFoundError)
    def test_missing_publication_is_failure(self, stat):
        with self.assertRaises(FileNotFoundError):
            api.resources()

    def test_redirects_not_followed(self):
        self.assertIsNone(api.NoRedirect().redirect_request(None, None, None, None, None, "http://127.0.0.1"))

    def test_bundle_commands_are_all_allowed_and_bounded(self):
        routes = []
        for bundle in api.BUNDLES.values():
            self.assertLessEqual(len(bundle['commands']), 4)
            for command in bundle['commands']:
                api.command_args(command)
            routes.extend(bundle['routes'])
        self.assertEqual(len(routes), 37)
        self.assertEqual(len(routes), len(set(routes)))

    def test_watchdog_status_does_not_create_missing_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'missing.sqlite3'
            with patch.object(api.event_history, 'DATABASE', path), patch.object(api, 'resources', side_effect=OSError):
                status = api.local_status()
            self.assertFalse(status['history']['available'])
            self.assertFalse(path.exists())
            self.assertIn('publication_error', status)


class ApiBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.history_patch = patch.object(api.event_history, 'DATABASE', Path(self.directory.name) / 'events.sqlite3')
        self.history_patch.start()
        self.path = self.directory.name + "/api.sock"
        self.server = api.Server(self.path, api.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.history_patch.stop()
        self.directory.cleanup()

    def request(self, method="POST", path="/api/probe", body=None, headers=None):
        connection = http.client.HTTPConnection("localhost", timeout=2)
        connection.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        connection.sock.connect(self.path)
        connection.request(method, path, json.dumps(body or {"command": "ping docker"}), headers or {})
        response = connection.getresponse()
        result = (response.status, json.loads(response.read()))
        connection.close()
        return result

    def headers(self):
        return {"Origin": "https://homepage.home.local", "X-Diagnostic-Request": "1", "Content-Type": "application/json"}

    @patch.object(api, "probe")
    def test_cross_origin_and_missing_header_rejected(self, probe):
        for headers in [{}, {**self.headers(), "Origin": "https://attacker.invalid"}, {"Origin": "https://homepage.home.local"}]:
            self.assertEqual(self.request(headers=headers)[0], 403)
        probe.assert_not_called()

    @patch.object(api, "probe")
    def test_invalid_commands_rejected_before_probe(self, probe):
        self.assertEqual(self.request(body={"command": "ping docker; id"}, headers=self.headers())[0], 400)
        probe.assert_not_called()

    @patch.object(api, "probe", return_value={"ok": True, "output": "connected"})
    def test_valid_request_and_global_rate_limit(self, probe):
        api.REQUEST_TIMES.clear()
        self.assertEqual(self.request(headers=self.headers())[0], 200)
        api.REQUEST_TIMES.extend([api.time.monotonic()] * 20)
        self.assertEqual(self.request(headers=self.headers())[0], 429)
        api.REQUEST_TIMES.clear()
        self.assertEqual(probe.call_count, 1)

    @patch.object(api, "resources", side_effect=RuntimeError("secret stderr"))
    def test_unavailable_monitor_is_sanitized(self, resources):
        status, data = self.request(method="GET", path="/api/resources")
        self.assertEqual(status, 503)
        self.assertNotIn("secret", json.dumps(data))

    @patch.object(api.event_history, 'history', side_effect=RuntimeError('private path'))
    def test_history_failure_is_explicit_and_sanitized(self, history):
        status, data = self.request(method='GET', path='/api/events')
        self.assertEqual(status, 503)
        self.assertNotIn('private', json.dumps(data))

    @patch.object(api.event_history, 'record_probe', side_effect=OSError('database full'))
    @patch.object(api, 'probe', return_value={'ok': True, 'output': 'connected'})
    def test_history_failure_does_not_fail_a_successful_probe(self, probe, record):
        api.REQUEST_TIMES.clear()
        status, data = self.request(headers=self.headers())
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        self.assertIn('history_error', data)


if __name__ == "__main__":
    unittest.main()
