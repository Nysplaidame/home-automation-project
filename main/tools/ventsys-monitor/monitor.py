#!/usr/bin/env python3
"""Read-only identity checks and temporary discovery attribution recorder."""
import base64
import json
import logging
import logging.handlers
import os
from pathlib import Path
import ssl
import subprocess
import threading
import time
import urllib.request
import paho.mqtt.client as mqtt

ROOT = Path('/var/lib/ventsys-monitor')
CONFIG = Path('/etc/ventsys-monitor/config.json')

def normalized(mac):
    return str(mac).lower().replace(':', '').replace('-', '')

def mismatch(payload, roster):
    mac = normalized(payload.get('mac', ''))
    expected = roster.get(mac)
    if expected is None:
        return 'Unknown discovery MAC: ' + mac
    if payload.get('name') != expected['name'] or payload.get('ip') != expected['ip']:
        return f"Discovery conflict: {mac}, observed {payload.get('name')} at {payload.get('ip')}; expected {expected['name']} at {expected['ip']}"
    return None

def make_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(ROOT / (name + '.jsonl'), maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)sZ %(message)s')
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log

class Monitor:
    def __init__(self, config):
        self.config = config
        self.roster = {normalized(x['mac']): x for x in config['roster']}
        self.lock = threading.RLock()
        self.log = make_logger('health')
        self.discovery = make_logger('discovery')
        self.broker = make_logger('broker')
        self.ctx = ssl.create_default_context(cadata=config['ca'])
        # Existing local CA predates the keyUsage extension required by Python
        # 3.13 strict mode. Retain chain and hostname verification, matching
        # the existing desktop TLS clients until the planned CA migration.
        self.ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        try:
            self.state = json.loads((ROOT / 'state.json').read_text())
        except FileNotFoundError:
            self.state = {}
        self.mqtt_connected = False
        self.broker_connected = False
        self.started = time.time()
        self.last_reconcile = 0
        self.seen = {}
        self.pending = []

    def save(self):
        path = ROOT / 'state.tmp'
        path.write_text(json.dumps(self.state))
        path.replace(ROOT / 'state.json')

    def notify(self, text):
        req = urllib.request.Request(self.config['ntfy_url'], data=text.encode(), headers={
            'Authorization': 'Basic ' + base64.b64encode((self.config['ntfy_user'] + ':' + self.config['ntfy_password']).encode()).decode(),
            'Title': 'VentSys identity monitor', 'Tags': 'warning',
        })
        with urllib.request.urlopen(req, context=self.ctx, timeout=15) as response:
            response.read()

    def incident(self, key, problem, threshold=1):
        with self.lock:
            old = self.state.get(key, {})
            if problem:
                count = old.get('count', 0) + 1
                old.update(count=count, detail=problem)
                if count >= threshold and old.get('sent') != problem:
                    try:
                        self.notify(problem)
                        old['sent'] = problem
                        self.log.info('alert %s %s', key, problem)
                    except Exception as exc:
                        self.log.error('notification failed %s', type(exc).__name__)
                self.state[key] = old
            elif old:
                if old.get('sent'):
                    try:
                        self.notify('Recovered: ' + old['sent'])
                    except Exception as exc:
                        self.log.error('recovery notification failed %s', type(exc).__name__)
                        return
                    self.log.info('recovery %s', key)
                self.state.pop(key, None)
            self.save()

    def ssh(self, command):
        return ['ssh', '-i', '/etc/ventsys-monitor/ha_ed25519',
                '-o', 'UserKnownHostsFile=/etc/ventsys-monitor/known_hosts',
                '-o', 'StrictHostKeyChecking=yes', '-o', 'BatchMode=yes',
                '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=30',
                '-o', 'ServerAliveCountMax=2', 'root@192.168.20.101', command]

    def broker_loop(self):
        while True:
            try:
                with subprocess.Popen(self.ssh('logs'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                    for line in proc.stdout:
                        if 'Error:' in line or 'Permission denied' in line:
                            self.broker_connected = False
                        else:
                            self.broker_connected = True
                        if any(x in line for x in ('esphome/discover/', 'New client', 'New connection', 'disconnected', 'Error:', 'Permission denied')):
                            self.broker.info(line.rstrip())
                        # A received discovery publish provides publisher identity.
                        # Subscriber replay alone never does.
                        if 'Received PUBLISH from ' in line and 'esphome/discover/' in line:
                            self.broker.info('LIVE_DISCOVERY_PUBLISH evidence captured')
                self.broker_connected = False
            except Exception as exc:
                self.broker_connected = False
                self.log.error('broker stream %s', type(exc).__name__)
            time.sleep(10)

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt_connected = rc == 0
        if rc == 0:
            client.subscribe('esphome/discover/#', qos=1)
            self.discovery.info('connected; initial retained replay follows')

    def on_disconnect(self, client, userdata, rc):
        self.mqtt_connected = False

    def on_message(self, client, userdata, msg):
        if self.config.get('capture_payloads', True):
            self.discovery.info(json.dumps({'topic': msg.topic, 'retain': bool(msg.retain), 'qos': msg.qos, 'payload': msg.payload.decode('utf-8', 'replace')}))
        with self.lock:
            self.seen[msg.topic] = msg.payload.decode('utf-8', 'replace')
            self.pending.append((msg.topic, self.seen[msg.topic]))

    def reconcile_discovery(self):
        with self.lock:
            pending = self.pending[:]
            self.pending.clear()
            for topic, payload in pending:
                if not payload:
                    problem = None
                else:
                    try:
                        problem = mismatch(json.loads(payload), self.roster)
                    except (ValueError, AttributeError):
                        problem = 'Invalid discovery payload on ' + topic
                self.incident('discovery:' + topic, (problem + '; topic=' + topic) if problem else None)

    def check(self):
        # Retry failed notifications and reconcile retained identities even
        # when the publisher does not send another message.
        with self.lock:
            self.pending.extend(self.seen.items())
        self.reconcile_discovery()
        self.incident('mqtt-access', None if self.mqtt_connected else 'MQTT capture disconnected', 2)
        if self.config.get('capture_broker', True):
            self.incident('broker-access', None if self.broker_connected else 'Broker attribution log stream unavailable', 2)
        try:
            raw = subprocess.check_output(self.ssh('snapshot'), timeout=25, stderr=subprocess.DEVNULL)
            entries = {normalized(e['mac']): e for e in json.loads(raw)}
            for mac, expected in self.roster.items():
                entry = entries.get(mac)
                problem = None
                if entry is None:
                    problem = 'HA ESPHome entry missing: ' + expected['name']
                elif entry['host'] != expected['ip'] or entry['name'] != expected['name']:
                    problem = f"HA identity conflict: {mac}, observed {entry['name']} at {entry['host']}; expected {expected['name']} at {expected['ip']}"
                self.incident('host:' + mac, problem)
            self.incident('ha-snapshot', None)
        except Exception as exc:
            self.incident('ha-snapshot', 'HA identity snapshot failed: ' + type(exc).__name__, 2)
        try:
            req = urllib.request.Request('https://192.168.20.101:8123/api/states', headers={'Authorization': 'Bearer ' + self.config['ha_token']})
            with urllib.request.urlopen(req, context=self.ctx, timeout=20) as response:
                states = {x['entity_id']: x for x in json.load(response)}
            e2 = states.get('sensor.ventsys_e2_branch_valve_uptime', {})
            maintenance = states.get('input_boolean.ventsys_maintenance_sla_branch', {}).get('state') == 'on'
            offline = e2.get('state') in (None, 'unknown', 'unavailable')
            self.incident('e2-offline', 'E2 native telemetry unavailable outside maintenance' if offline and not maintenance else None, 2)
            self.incident('ha-api', None)
        except Exception as exc:
            self.incident('ha-api', 'HA telemetry check failed: ' + type(exc).__name__, 2)
        with self.lock:
            (ROOT / 'status.json').write_text(json.dumps({'checked_at': time.time(), 'started_at': self.started, 'mqtt_connected': self.mqtt_connected, 'broker_connected': self.broker_connected, 'incident_keys': list(self.state)}))

    def run(self):
        if self.config.get('capture_broker', True):
            threading.Thread(target=self.broker_loop, daemon=True).start()
        client = mqtt.Client(client_id='ventsys-server-discovery-monitor')
        client.username_pw_set(self.config['mqtt_user'], self.config['mqtt_password'])
        client.tls_set_context(self.ctx)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message
        client.connect_async('192.168.20.101', 8883)
        client.loop_start()
        time.sleep(5)
        while True:
            self.reconcile_discovery()
            if time.time() - self.last_reconcile >= 300:
                self.check()
                self.last_reconcile = time.time()
            time.sleep(1)

if __name__ == '__main__':
    Monitor(json.loads(CONFIG.read_text())).run()
