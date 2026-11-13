"""Real local TLS handshakes using disposable test certificates, not live secrets."""
import importlib.util
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
spec = importlib.util.spec_from_file_location('api', Path(__file__).parents[1] / 'diagnostic_api.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class TLSChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.directory.name)
        def openssl(*args):
            subprocess.run(['/usr/bin/openssl', *args], cwd=cls.root, check=True, capture_output=True, timeout=10)
        openssl('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-subj', '/CN=Disposable Test CA', '-days', '365', '-keyout', 'ca.key', '-out', 'ca.crt', '-addext', 'keyUsage=critical,keyCertSign,cRLSign')
        openssl('req', '-newkey', 'rsa:2048', '-nodes', '-subj', '/CN=test.home.local', '-keyout', 'leaf.key', '-out', 'leaf.csr')
        openssl('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-subj', '/CN=Disposable Legacy CA', '-days', '365', '-keyout', 'legacy.key', '-out', 'legacy.crt')
        (cls.root / 'extensions').write_text('subjectAltName=DNS:test.home.local\nbasicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\n')
        for name, days in [('valid', '120'), ('soon', '10'), ('expired', '0')]:
            openssl('x509', '-req', '-in', 'leaf.csr', '-CA', 'ca.crt', '-CAkey', 'ca.key', '-CAcreateserial', '-days', days, '-extfile', 'extensions', '-out', name + '.crt')
        openssl('x509', '-req', '-in', 'leaf.csr', '-CA', 'legacy.crt', '-CAkey', 'legacy.key', '-CAcreateserial', '-days', '120', '-extfile', 'extensions', '-out', 'legacy-leaf.crt')

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def check(self, certificate, name='test.home.local', trust=True, legacy=False):
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen(2)
        listener.settimeout(5)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(self.root / (certificate + '.crt')), str(self.root / 'leaf.key'))
        def serve():
            for _ in range(3 if legacy else 2):
                connection, _ = listener.accept()
                try:
                    with context.wrap_socket(connection, server_side=True):
                        pass
                except ssl.SSLError:
                    connection.close()
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        try:
            with patch.object(api, 'CA_FILE', str(self.root / ('legacy.crt' if legacy else 'ca.crt')) if trust else '/etc/ssl/certs/ca-certificates.crt'):
                return api.tls_check({'tls': {'ip': '127.0.0.1', 'port': listener.getsockname()[1], 'name': name}})
        finally:
            thread.join(timeout=6)
            listener.close()

    def test_trusted_certificate_and_hostname(self):
        ok, severity, output = self.check('valid')
        self.assertTrue(ok)
        self.assertEqual(severity, 'pass')
        self.assertIn('chain and hostname verified', output)
        self.assertIn('sha256 fingerprint', output.lower())

    def test_near_expiry_is_a_warning(self):
        ok, severity, output = self.check('soon')
        self.assertTrue(ok)
        self.assertEqual(severity, 'warn')
        self.assertIn('renewal due', output)

    def test_expired_certificate_fails(self):
        ok, severity, output = self.check('expired')
        self.assertFalse(ok)
        self.assertEqual(severity, 'fail')

    def test_wrong_hostname_fails(self):
        ok, severity, output = self.check('valid', name='wrong.home.local')
        self.assertFalse(ok)
        self.assertIn('hostname', output.lower())

    def test_unknown_ca_fails(self):
        ok, severity, output = self.check('valid', trust=False)
        self.assertFalse(ok)
        self.assertEqual(severity, 'fail')

    def test_legacy_ca_is_visible_warning_with_separate_trust(self):
        ok, severity, output = self.check('legacy-leaf', legacy=True)
        self.assertTrue(ok)
        self.assertEqual(severity, 'warn')
        self.assertIn('verification code 92', output)
        self.assertIn('Legacy compatibility: chain, hostname and dates verified', output)

    def test_legacy_ca_does_not_hide_wrong_hostname(self):
        ok, severity, output = self.check('legacy-leaf', name='wrong.home.local', legacy=True)
        self.assertFalse(ok)
        self.assertEqual(severity, 'fail')


if __name__ == '__main__':
    unittest.main()
