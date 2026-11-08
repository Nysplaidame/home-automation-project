#!/usr/bin/env python3
"""Bounded read-only diagnostics over a local Unix socket. No shell commands."""
import collections
import http.server
import json
import os
import socket
import socketserver
import ssl
import sys
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
import event_history

TARGETS = {
    "proxmox": {"label": "Proxmox host", "ip": "192.168.10.10", "dns": "proxmox.home.local", "ports": [8006]},
    "router": {"label": "Router", "ip": "192.168.10.1", "dns": "router.home.local", "ports": [80]},
    "homeassistant": {"label": "Home Assistant / VM100", "ip": "192.168.20.101", "dns": "homeassistant.home.local", "ports": [8123]},
    "monitoring": {"label": "Monitoring / VM102", "ip": "192.168.60.10", "dns": "grafana.home.local", "ports": [3000, 3001, 8086], "url": "http://192.168.60.10:3000/api/health"},
    "docker": {"label": "Docker / VM103", "ip": "192.168.20.102", "dns": "homepage.home.local", "ports": [443, 8085, 8094], "url": "http://192.168.20.102:8085/v1/health"},
    "frigate": {"label": "Frigate / CT111", "ip": "192.168.30.20", "dns": "frigate.home.local", "ports": [8971, 5000], "url": "http://192.168.30.20:5000/api/version"},
    "ai": {"label": "AI / CT114", "ip": "192.168.20.104", "dns": "openwebui.home.local", "ports": [3002], "url": "http://192.168.20.104:3002/health"},
    "nas": {"label": "NAS", "ip": "192.168.40.50", "dns": "omv.home.local", "ports": [80, 445]},
}
TARGETS['docker']['tls'] = {'ip': '192.168.20.102', 'port': 443, 'name': 'homepage.home.local'}
TARGETS['homeassistant']['tls'] = {'ip': '192.168.20.101', 'port': 8123, 'name': 'homeassistant.home.local'}
TARGETS['frigate']['tls'] = {'ip': '192.168.30.20', 'port': 8971, 'name': 'frigate.home.local'}
TARGETS['vault'] = {'label': 'Vaultwarden HTTPS', 'ip': '192.168.20.102', 'dns': 'vault.home.local', 'ports': [443], 'tls': {'ip': '192.168.20.102', 'port': 443, 'name': 'vault.home.local'}}
CA_FILE = '/etc/troubleshooting-api/ca.crt'
BUNDLES = {
    'portal': {'label': 'Homepage connection and certificate', 'routes': ['homepage', 'portal-navigation', 'proxy-redirect', 'listener-collision', 'frontend-cache', 'tls', 'remote'], 'commands': ['dns docker', 'tcp docker 443', 'tls docker', 'http docker']},
    'ha': {'label': 'Home Assistant supporting services', 'routes': ['home-assistant', 'automations', 'ventsys', 'esphome-identity'], 'commands': ['dns homeassistant', 'tcp homeassistant 8123', 'tls homeassistant']},
    'camera': {'label': 'Frigate service and certificate', 'routes': ['camera', 'phone-relay'], 'commands': ['dns frigate', 'tcp frigate 8971', 'tls frigate', 'http frigate']},
    'network': {'label': 'Local DNS and network path', 'routes': ['internet', 'dns', 'dns-after-reboot'], 'commands': ['ping router', 'dns docker', 'tcp docker 443', 'tls docker']},
    'monitoring': {'label': 'Monitoring and notification listeners', 'routes': ['monitoring', 'notifications'], 'commands': ['tcp monitoring 3000', 'http monitoring', 'tcp monitoring 3001', 'http docker']},
    'docker': {'label': 'Shared Docker host', 'routes': ['docker', 'docker-build', 'updates', 'guests', 'photos', 'media', 'downloads', 'sync', 'household', 'p1s', 'printer-queue'], 'commands': ['ping docker', 'dns docker', 'tcp docker 443', 'tls docker']},
    'storage': {'label': 'NAS and shared host listeners', 'routes': ['backups', 'storage', 'app-backup', 'smb-access', 'nas-speed'], 'commands': ['ping nas', 'tcp nas 445', 'tcp nas 80', 'ping docker']},
    'ai': {'label': 'Local AI supporting listeners', 'routes': ['local-ai', 'voice'], 'commands': ['ping ai', 'tcp ai 3002', 'http ai', 'tcp homeassistant 8123']},
    'vault': {'label': 'Vault connection and certificate', 'routes': ['vault'], 'commands': ['dns vault', 'tcp vault 443', 'tls vault']},
}
ORIGINS = {"https://" + host for host in ["homepage.home.local", "192.168.20.102", "100.94.122.18", "docker-host", "docker-host.home.local", "docker-host.tail7012a0.ts.net"]}
ORIGINS.add("http://192.168.20.102:8094")
SLOTS = threading.BoundedSemaphore(2)
RATE_LOCK = threading.Lock()
REQUEST_TIMES = collections.deque()


def command_args(command):
    if not isinstance(command, str) or len(command) > 100:
        raise ValueError("Use ping, dns, tcp or http followed by a listed target.")
    words = command.lower().split()
    if len(words) not in (2, 3) or words[0] not in ("ping", "dns", "tcp", "http", "tls") or words[1] not in TARGETS:
        raise ValueError("Use: ping TARGET, dns TARGET, tcp TARGET PORT, http TARGET or tls TARGET.")
    action, target = words[:2]
    config = TARGETS[target]
    port = None
    if action == "tcp":
        if len(words) != 3 or not words[2].isdigit() or int(words[2]) not in config["ports"]:
            raise ValueError("Choose a listed TCP port for this target.")
        port = int(words[2])
    elif len(words) != 2 or (action == "http" and "url" not in config) or (action == 'tls' and 'tls' not in config):
        raise ValueError("This action is unavailable for the selected target.")
    return action, target, config, port


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def tls_check(config):
    endpoint = config['tls']
    name, port, address = endpoint['name'], endpoint['port'], endpoint['ip']
    # Read the public leaf without sending HTTP or credentials, then separately
    # establish verified chain/name trust. This inspection is never a health request.
    inspection = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    inspection.check_hostname = False
    inspection.verify_mode = ssl.CERT_NONE
    with socket.create_connection((address, port), timeout=1.5) as connection:
        with inspection.wrap_socket(connection, server_hostname=name) as secure:
            certificate = secure.getpeercert(binary_form=True)
    decoded = subprocess.run(['/usr/bin/openssl', 'x509', '-inform', 'DER', '-noout', '-dates', '-subject', '-issuer', '-ext', 'subjectAltName', '-fingerprint', '-sha256'], input=certificate, capture_output=True, timeout=1)
    if decoded.returncode or len(decoded.stdout) > 12000:
        raise OSError('Certificate parsing failed')
    fields = decoded.stdout.decode('utf-8', errors='replace')
    expires = next((line.partition('=')[2] for line in fields.splitlines() if line.startswith('notAfter=')), None)
    if expires is None:
        raise OSError('Certificate expiry unavailable')
    days = (ssl.cert_time_to_seconds(expires) - time.time()) / 86400
    verification = ssl.create_default_context()
    try:
        verification.load_verify_locations(cafile=CA_FILE)
    except OSError:
        return False, 'unknown', f'TLS {name}:{port} via {address}\nTrust store unavailable; chain/hostname trust cannot be assessed.\nExpires in {days:.1f} days\n{fields}'
    trusted = False
    compatibility_warning = False
    trust_message = 'Not verified'
    try:
        with socket.create_connection((address, port), timeout=1.5) as connection:
            with verification.wrap_socket(connection, server_hostname=name):
                trusted = True
                trust_message = 'PASS: chain and hostname verified using system roots + Home Local CA.'
    except ssl.SSLCertVerificationError as error:
        trust_message = f'FAILED: certificate verification code {error.verify_code}: {error.verify_message}'
        if error.verify_code == 92:
            # Diagnose this legacy CA format separately. Chain, date and name
            # verification remain enabled; the strict result stays visible.
            compatibility = ssl.create_default_context()
            compatibility.load_verify_locations(cafile=CA_FILE)
            compatibility.verify_flags &= ~ssl.VERIFY_X509_STRICT
            try:
                with socket.create_connection((address, port), timeout=1.5) as connection:
                    with compatibility.wrap_socket(connection, server_hostname=name):
                        trusted = True
                        compatibility_warning = True
                        trust_message += '\nLegacy compatibility: chain, hostname and dates verified. CA key-usage extension needs planned certificate maintenance.'
            except ssl.SSLCertVerificationError as legacy_error:
                trust_message += f'\nLegacy compatibility FAILED: {legacy_error.verify_message}'
    output = f'TLS {name}:{port} via {address}\nTrust: {trust_message}\nExpires in {days:.1f} days' + (' — renewal due within 30 days' if 0 < days <= 30 else '') + '\n' + fields
    return trusted and days > 0, 'fail' if not trusted or days <= 0 else 'warn' if compatibility_warning or days <= 30 else 'pass', output


def probe(command):
    action, target, config, port = command_args(command)
    started = time.monotonic()
    ok = False
    severity = None
    output = ""
    try:
        if action == "ping":
            result = subprocess.run(["/usr/bin/ping", "-n", "-c", "3", "-W", "1", "-w", "5", config["ip"]], capture_output=True, text=True, timeout=7)
            ok = result.returncode == 0
            output = result.stdout + result.stderr
        elif action == "dns":
            # Resolver calls can block; keep them in a separately timed process.
            result = subprocess.run(["/usr/bin/python3", "-c", "import socket,sys; print('\\n'.join(sorted({r[4][0] for r in socket.getaddrinfo(sys.argv[1],None)})))", config["dns"]], capture_output=True, text=True, timeout=5)
            ok = result.returncode == 0
            output = f"System resolver lookup: {config['dns']}\n" + (result.stdout if ok else "DNS resolution failed.")
        elif action == "tcp":
            with socket.create_connection((config["ip"], port), timeout=4):
                ok = True
                output = f"Connected to {config['ip']}:{port}. This establishes a TCP listener, not application health."
        elif action == 'tls':
            ok, severity, output = tls_check(config)
        else:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
            request = urllib.request.Request(config["url"], headers={"User-Agent": "Home-Diagnostics/1"})
            with opener.open(request, timeout=4) as response:
                # Do not return response bodies, cookies or authorization challenges.
                ok = 200 <= response.status < 300
                output = f"GET {config['url']}\nHTTP {response.status}. Response body omitted."
    except urllib.error.HTTPError as error:
        output = f"HTTP {error.code}. Redirects are not followed; authentication may be required."
    except subprocess.TimeoutExpired:
        output = "Check timed out."
    except (OSError, urllib.error.URLError) as error:
        output = f"Connection failed ({type(error).__name__}). Check routing, firewall and listener."
    return {"command": command, "target": target, "ok": ok, "severity": severity or ('pass' if ok else 'fail'), "output": output[:6000], "duration_ms": round((time.monotonic() - started) * 1000), "timestamp": time.time(), "source": "VM103 diagnostic service"}


def resources():
    path = Path("/var/lib/troubleshooting-api/resources.json")
    if path.stat().st_size > 200000:
        raise RuntimeError("Invalid monitor response.")
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("snapshot"), dict):
        raise RuntimeError("Invalid monitor response.")
    return data


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "HomeDiagnostics"

    def log_message(self, fmt, *args):
        # Paths, status codes only; never user input or SSH stderr.
        pass

    def reply(self, status, payload):
        body = json.dumps(payload, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/targets":
            self.reply(200, {"targets": TARGETS, "bundles": BUNDLES, "source": "VM103 diagnostic service"})
        elif self.path == '/api/events':
            try:
                self.reply(200, event_history.history())
            except Exception:
                self.reply(503, {'error': 'Event history unavailable. Checks and primary alerts operate independently.'})
        elif self.path == "/api/resources":
            if not SLOTS.acquire(blocking=False):
                self.reply(429, {"error": "Diagnostics busy. Try again shortly."})
                return
            try:
                self.reply(200, resources())
            except Exception:
                self.reply(503, {"error": "Monitor reader unavailable. Alerts run independently on Proxmox."})
            finally:
                SLOTS.release()
        else:
            self.reply(404, {"error": "Unknown endpoint."})

    def do_POST(self):
        if self.path != "/api/probe":
            self.reply(404, {"error": "Unknown endpoint."})
            return
        if self.headers.get("Origin") not in ORIGINS or self.headers.get("X-Diagnostic-Request") != "1":
            self.reply(403, {"error": "Open diagnostics through the approved Homepage or management address."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 512 or self.headers.get_content_type() != "application/json":
                raise ValueError("Expected a small JSON command.")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object.")
            command = payload.get("command")
            command_args(command)
        except (ValueError, TypeError):
            self.reply(400, {"error": "Use a supported action, listed target and listed port."})
            return
        with RATE_LOCK:
            now = time.monotonic()
            while REQUEST_TIMES and now - REQUEST_TIMES[0] >= 60:
                REQUEST_TIMES.popleft()
            if len(REQUEST_TIMES) >= 20:
                self.reply(429, {"error": "Limit: 20 checks per minute. Wait and retry."})
                return
            REQUEST_TIMES.append(now)
        if not SLOTS.acquire(blocking=False):
            self.reply(429, {"error": "Two checks already running. Try again shortly."})
            return
        try:
            result = probe(command)
            try:
                event_history.record_probe(result)
            except Exception:
                result['history_error'] = 'Check completed, but its history summary could not be saved.'
            self.reply(200, result)
        finally:
            SLOTS.release()


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    request_queue_size = 8

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(10)
        return connection, address


def observe_viewer():
    while True:
        try:
            try:
                sample = resources()['snapshot']['timestamp']
                age = time.time() - sample
                problem = 'Published monitor sample is older than five minutes or has an invalid clock.' if not -30 <= age <= 300 else None
            except Exception:
                problem = 'Metrics publication is missing or unreadable.'
            event_history.record_viewer(problem)
        except Exception as error:
            print('Event history observer failed: ' + type(error).__name__, flush=True)
        time.sleep(60)


def local_status():
    """Supported read-only watchdog status; never creates/prunes database state."""
    result = {'ca_readable': os.access(CA_FILE, os.R_OK)}
    try:
        data = resources()
        result['sample_age_seconds'] = round(time.time() - data['snapshot']['timestamp'])
        result['publication_age_seconds'] = round(time.time() - Path('/var/lib/troubleshooting-api/resources.json').stat().st_mtime)
    except Exception:
        result['publication_error'] = 'Snapshot unavailable'
    try:
        with sqlite3.connect(event_history.DATABASE.as_uri() + '?mode=ro', uri=True, timeout=1) as connection:
            count, last = connection.execute('SELECT COUNT(*),MAX(timestamp) FROM events').fetchone()
        result['history'] = {'available': True, 'count': count, 'last_event': last}
    except Exception:
        result['history'] = {'available': False, 'error': 'History unavailable'}
    return result


if __name__ == "__main__":
    if sys.argv[1:] == ['--status']:
        print(json.dumps(local_status(), indent=2))
        raise SystemExit(0)
    if sys.argv[1:]:
        raise SystemExit('Supported option: --status')
    threading.Thread(target=observe_viewer, daemon=True).start()
    path = "/run/troubleshooting-api/api.sock"
    if os.path.exists(path):
        os.unlink(path)
    with Server(path, Handler) as server:
        # Directory restricts access to the mounted local proxy socket.
        os.chmod(path, 0o666)
        server.serve_forever()
