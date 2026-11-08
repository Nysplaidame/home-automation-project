"""Bounded SQLite event summaries; independent of alert delivery."""
import json
import math
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DATABASE = Path('/var/lib/troubleshooting-api/events.sqlite3')
RETENTION = 30 * 86400
MAX_EVENTS = 1000


@contextmanager
def database(path=None):
    connection = sqlite3.connect(str(path or DATABASE), timeout=1)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, timestamp REAL NOT NULL, kind TEXT NOT NULL, event_key TEXT NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL, detail TEXT NOT NULL)')
        connection.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        connection.execute('INSERT OR IGNORE INTO metadata VALUES (?, ?)', ('started_at', json.dumps(time.time())))
        with connection:
            yield connection
    finally:
        connection.close()


def metadata(connection, key, default=None):
    row = connection.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()
    return json.loads(row[0]) if row else default


def put_metadata(connection, key, value):
    connection.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', (key, json.dumps(value, allow_nan=False)))


def append(connection, kind, key, severity, title, detail='', timestamp=None):
    stamp = time.time() if timestamp is None else timestamp
    if not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
        raise ValueError('Invalid event timestamp')
    connection.execute('INSERT INTO events(timestamp,kind,event_key,severity,title,detail) VALUES (?,?,?,?,?,?)',
                       (stamp, kind[:32], str(key)[:100], severity[:16], title[:180], detail[:800]))
    connection.execute('DELETE FROM events WHERE timestamp < ?', (time.time() - RETENTION,))
    connection.execute('DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY id DESC LIMIT ?)', (MAX_EVENTS,))


def record_probe(result, path=None):
    with database(path) as connection:
        append(connection, 'diagnostic', result['command'], result.get('severity') or ('pass' if result['ok'] else 'fail'),
               result['command'], f"VM103 requested check · {result['duration_ms']} ms\n{result['output'][:700]}", result['timestamp'])


def monitor_conditions(data):
    snapshot, status = data['snapshot'], data['status']
    conditions = {}
    for key, description in snapshot.get('errors', {}).items():
        conditions['coverage:' + key] = ['warn', 'Coverage degraded: ' + key, str(description)]
    for key, state in status.get('active_or_pending', {}).items():
        if state.get('active'):
            conditions['incident:' + key] = ['fail', 'Active monitor incident: ' + key, 'Threshold incident reported by the primary monitor.']
        if state.get('pending') or state.get('undelivered'):
            conditions['queue:' + key] = ['warn', 'Notification queued: ' + key, 'Pending retry or delivery; acceptance is not yet confirmed.']
    for key in status.get('delivery_errors', []):
        conditions['delivery:' + key] = ['fail', 'Notification delivery failed: ' + key, 'The primary monitor will retry.']
    health = status.get('collector_health', {})
    if health.get('failures') or health.get('active'):
        conditions['collector'] = ['fail' if health.get('active') else 'warn', 'Collector failure observed', str(health.get('last_error', 'See primary monitor journal.'))]
    if health.get('pending') or health.get('delivery_error'):
        conditions['collector-delivery'] = ['warn', 'Collector notification pending', str(health.get('pending') or 'Delivery failed; retry pending.')]
    return conditions


def record_monitor(data, path=None):
    snapshot = data['snapshot']
    stamp = snapshot['timestamp']
    if not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
        raise ValueError('Invalid sample timestamp')
    with database(path) as connection:
        previous = metadata(connection, 'monitor', {})
        # Duplicate/older publication cannot invent recoveries or overwrite baselines.
        if stamp < previous.get('timestamp', 0):
            return
        conditions = monitor_conditions(data)
        if not previous:
            append(connection, 'monitor', 'baseline', 'info', 'Monitor history started', 'Current observations only; earlier incidents are not reconstructed.')
        if previous.get('boot_id') and snapshot.get('boot_id') != previous['boot_id']:
            append(connection, 'monitor', 'boot', 'info', 'Proxmox boot changed', 'OOM counters and other cumulative values may have reset.')
        for key, value in conditions.items():
            if key not in previous.get('conditions', {}) or value[0] != previous['conditions'][key][0]:
                prefix = 'Present at history start: ' if not previous else ''
                append(connection, 'monitor', key, value[0], prefix + value[1], value[2])
        for key, value in previous.get('conditions', {}).items():
            if key not in conditions:
                append(connection, 'monitor', key, 'pass', 'Cleared: ' + value[1], 'Absent from the latest monitor state. Notification acceptance does not prove phone display.')
        accepted = data.get('recent_notifications', {})
        for key, sent in accepted.items():
            if previous and isinstance(sent, (int, float)) and sent > previous.get('accepted', {}).get(key, 0) and sent >= metadata(connection, 'started_at', 0):
                append(connection, 'monitor', 'accepted:' + key, 'info', 'Notification accepted: ' + key, 'The monitor recorded successful ntfy delivery; phone display is not verified.', sent)
        put_metadata(connection, 'monitor', {'timestamp': stamp, 'boot_id': snapshot.get('boot_id'), 'conditions': conditions, 'accepted': accepted})


def record_viewer(problem, path=None):
    with database(path) as connection:
        previous = metadata(connection, 'viewer', 'initial')
        if previous == problem:
            return
        if problem:
            append(connection, 'viewer', 'publication', 'warn', 'Viewer evidence unavailable', problem)
        elif previous and previous != 'initial':
            append(connection, 'viewer', 'publication', 'pass', 'Viewer evidence recovered', 'Fresh publication is available again. Primary alerts operate independently.')
        put_metadata(connection, 'viewer', problem)


def history(path=None):
    with database(path) as connection:
        connection.execute('DELETE FROM events WHERE timestamp < ?', (time.time() - RETENTION,))
        rows = connection.execute('SELECT id,timestamp,kind,event_key AS key,severity,title,detail FROM events ORDER BY timestamp DESC,id DESC LIMIT 100').fetchall()
        return {'events': [dict(row) for row in rows], 'total': connection.execute('SELECT COUNT(*) FROM events').fetchone()[0],
                'started_at': metadata(connection, 'started_at'), 'retention_days': 30, 'max_events': MAX_EVENTS}
