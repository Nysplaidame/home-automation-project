#!/usr/bin/env python3
"""VM103 offline receiver/updater. No registry calls, tokens or printer commands."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from datetime import datetime, timezone

ROOT = Path('/var/lib/home-automation-updates/bambuddy')
STACK = Path('/opt/stacks/bambuddy')
NAS = Path('/mnt/omv/docker-host-backups')
BACKUPS = NAS / 'bambuddy-updates'
PROBE = 'bambuddy-update-probe'
OVERRIDE = STACK / 'docker-compose.override.yml'

def run(*args, timeout=300):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        # Do not emit resolved Compose, application logs or credentials.
        raise RuntimeError(f'{args[0]} {args[1]} failed (exit {result.returncode})')
    return result.stdout.strip()

def compose(*args):
    return run('docker', 'compose', '--project-directory', str(STACK), *args)

def atomic_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    os.chmod(tmp, 0o600)
    tmp.replace(path)

def version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:\.\d+)?', value):
        raise ValueError('Invalid stable version')
    return tuple(int(x) for x in value.split('.'))

def validate_manifest(m):
    if m.get('schema') != 1:
        raise ValueError('Unknown manifest schema')
    version(m['version'])
    for field in ('image_id', 'config_digest'):
        if not re.fullmatch(r'sha256:[a-f0-9]{64}', m[field]):
            raise ValueError('Invalid image ID')
    if not re.fullmatch(r'bambuddy-staged:' + re.escape(m['version']) + r'-[a-f0-9]{12}', m['local_tag']):
        raise ValueError('Invalid local image tag')
    if not re.fullmatch(r'[a-f0-9]{64}', m['archive_sha256']):
        raise ValueError('Invalid archive hash')
    if not isinstance(m['archive_bytes'], int) or not 0 < m['archive_bytes'] < 4 * 1024**3:
        raise ValueError('Invalid archive size')
    if not re.fullmatch(r'ghcr.io/maziggy/bambuddy@sha256:[a-f0-9]{64}', m['upstream_digest']):
        raise ValueError('Invalid upstream digest')
    return m

def check_archive(directory, m):
    archive = directory / 'image.tar'
    if archive.is_symlink() or archive.stat().st_size != m['archive_bytes']:
        raise ValueError('Archive size or path mismatch')
    with archive.open('rb') as handle:
        if hashlib.file_digest(handle, 'sha256').hexdigest() != m['archive_sha256']:
            raise ValueError('Archive checksum mismatch')

def publish():
    if (ROOT / 'ready.json').exists():
        raise RuntimeError('A pending bundle already exists')
    incoming = ROOT / 'incoming'
    m = validate_manifest(json.loads((incoming / 'manifest.json').read_text()))
    check_archive(incoming, m)
    destination = ROOT / 'ready'
    if destination.exists():
        raise RuntimeError('Unexpected ready directory; inspect before continuing')
    incoming.rename(destination)
    atomic_json(ROOT / 'ready.json', m)
    print(f"Published verified offline bundle {m['version']}")

def metrics(text):
    values = {}
    for line in text.splitlines():
        match = re.fullmatch(r'(bambuddy_[a-z_]+)(?:\{(.*)\})? ([0-9.eE+-]+)', line)
        if match:
            labels = dict(re.findall(r'(\w+)="([^"\\]*)"', match[2] or ''))
            values.setdefault(match[1], []).append((labels, float(match[3])))
    return values

def require_idle(values):
    def scalar(name):
        rows = values.get(name, [])
        if len(rows) != 1:
            raise RuntimeError('Missing or ambiguous queue/printer metrics')
        return rows[0][1]
    total = scalar('bambuddy_printers_total')
    if total < 1 or scalar('bambuddy_printers_connected') != total:
        raise RuntimeError('Printer disconnected or unknown')
    for name in ('bambuddy_queue_pending', 'bambuddy_queue_printing'):
        if scalar(name) != 0:
            raise RuntimeError('Print queue is not empty')
    connections = {x['printer_id']: n for x, n in values.get('bambuddy_printer_connected', [])}
    states = {x['printer_id']: n for x, n in values.get('bambuddy_printer_state', [])}
    if len(states) != total or set(states) != set(connections):
        raise RuntimeError('Incomplete printer metrics')
    if any(connections[p] != 1 or states[p] not in (1, 4) for p in states):
        raise RuntimeError('Printer is busy or has an unsafe/unknown state')
    for name in ('bambuddy_bed_target_celsius', 'bambuddy_nozzle_target_celsius'):
        rows = values.get(name, [])
        if {x['printer_id'] for x, _ in rows} != set(states) or any(n != 0 for _, n in rows):
            raise RuntimeError('Printer has active or unknown heater targets')
    return set(states)

def get_json(path):
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/' + path, timeout=10) as response:
        return json.load(response)

def get_metrics():
    with urllib.request.urlopen('http://127.0.0.1:8000/api/v1/metrics', timeout=10) as response:
        return metrics(response.read().decode())

def queue_clear():
    # Metrics count pending/printing only; also exclude scheduled/waiting jobs.
    db = sqlite3.connect(f'file:{STACK}/data/bambuddy.db?mode=ro', uri=True)
    try:
        statuses = db.execute('SELECT DISTINCT status FROM print_queue').fetchall()
        if any(row[0] not in ('completed', 'failed', 'cancelled', 'skipped') for row in statuses):
            raise RuntimeError('Nonterminal print queue entries exist')
    finally:
        db.close()

def current_image():
    return json.loads(run('docker', 'inspect', 'bambuddy'))[0]

def sqlite_check(data):
    db = sqlite3.connect(f'file:{data}/bambuddy.db?mode=ro', uri=True)
    try:
        if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise RuntimeError('SQLite integrity check failed')
    finally:
        db.close()

def restore_checkpoint(directory):
    # Paths are fixed; replacement keeps failed migrated data for diagnosis.
    failed = ROOT / ('failed-data-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    failed.mkdir(mode=0o700)
    for name in ('data', 'logs'):
        (STACK / name).rename(failed / name)
    OVERRIDE.unlink(missing_ok=True)
    with tarfile.open(directory / 'stack.tar') as archive:
        archive.extractall(STACK, filter='fully_trusted')  # locally generated, root-owned checkpoint
    return failed

def override(image):
    OVERRIDE.write_text(f'services:\n  bambuddy:\n    image: {image}\n    pull_policy: never\n')
    os.chmod(OVERRIDE, 0o600)
    compose('config', '--quiet')

def health(expected_version, ids, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if get_json('updates/version')['version'] == expected_version:
                values = get_metrics()
                connected = {x['printer_id'] for x, n in values.get('bambuddy_printer_connected', []) if n == 1}
                if connected == ids and current_image()['State']['Running']:
                    return
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError('Version or printer-reconnection health check failed')

def probe(m, checkpoint):
    test_root = Path(tempfile.mkdtemp(prefix='probe-', dir=ROOT))
    try:
        with tarfile.open(checkpoint / 'stack.tar') as archive:
            members = [x for x in archive.getmembers() if x.name == 'data' or x.name.startswith('data/')]
            archive.extractall(test_root, members=members, filter='fully_trusted')
        run('docker', 'run', '-d', '--name', PROBE, '--network', 'none', '--restart', 'no',
            '--pull', 'never', '-e', 'PORT=8000', '-v', f'{test_root}/data:/app/data', m['local_tag'])
        code = 'import json,urllib.request; print(json.load(urllib.request.urlopen("http://127.0.0.1:8000/api/v1/updates/version",timeout=5))["version"])'
        for _ in range(36):
            try:
                if run('docker', 'exec', PROBE, 'python', '-c', code, timeout=10) == m['version']:
                    break
            except Exception:
                pass
            time.sleep(5)
        else:
            raise RuntimeError('Isolated copied-data startup/migration failed')
        run('docker', 'stop', '--time', '30', PROBE)
        sqlite_check(test_root / 'data')
    finally:
        subprocess.run(('docker', 'rm', '-f', PROBE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.rmtree(test_root)

def apply(check_only=False):
    if (ROOT / 'transaction.json').exists():
        raise RuntimeError('Interrupted update marker exists; use the manual recovery runbook')
    if (ROOT / 'blocked.json').exists():
        print('Previous bundle failed; automatic retry is blocked. See blocked.json.')
        return
    if not (ROOT / 'ready.json').exists():
        print('No staged release; nothing to install.')
        return
    m = validate_manifest(json.loads((ROOT / 'ready.json').read_text()))
    check_archive(ROOT / 'ready', m)
    old_version = get_json('updates/version')['version']
    if version(m['version']) <= version(old_version):
        raise RuntimeError('Refusing a same-version update or downgrade')
    if version(m['version'])[0] != version(old_version)[0]:
        raise RuntimeError('Major releases require manual review')
    try:
        ids = require_idle(get_metrics())
        queue_clear()
    except Exception as e:
        print(f'Deferred: {e}')
        return
    if check_only:
        print(f"Verified bundle {m['version']}; all printers idle, queue empty. No changes made.")
        return
    if run('findmnt', '-n', '-o', 'FSTYPE', '--target', str(NAS)) not in ('nfs', 'nfs4'):
        raise RuntimeError('NAS backup mount is unavailable')
    if shutil.disk_usage(ROOT).free < m['archive_bytes'] * 2 + 2 * 1024**3:
        raise RuntimeError('Insufficient local free space')
    if shutil.disk_usage(NAS).free < 5 * 1024**3:
        raise RuntimeError('Insufficient NAS backup space')
    old = current_image()
    if not old['State']['Running']:
        raise RuntimeError('Existing container is not running')
    # Confirm only the expected service and durable bind mounts before mutation.
    config = json.loads(compose('config', '--format', 'json'))
    if set(config['services']) != {'bambuddy'}:
        raise RuntimeError('Unexpected services in Bambuddy stack')
    binds = {x['Destination']: x['Source'] for x in old['Mounts'] if x['Type'] == 'bind'}
    if binds.get('/app/data') != str(STACK / 'data') or binds.get('/app/logs') != str(STACK / 'logs'):
        raise RuntimeError('Unexpected live data mounts')
    if OVERRIDE.exists() and not re.fullmatch(r'services:\n  bambuddy:\n    image: (?:bambuddy-staged:[0-9.a-f-]+|sha256:[a-f0-9]{64})\n    pull_policy: never\n', OVERRIDE.read_text()):
        raise RuntimeError('Unmanaged Compose override exists')
    run('docker', 'load', '-i', str(ROOT / 'ready' / 'image.tar'))
    print('Loaded checksummed image from the local inbox.', flush=True)
    image = json.loads(run('docker', 'image', 'inspect', m['local_tag']))[0]
    if image['Id'] not in (m['image_id'], m['config_digest']) or image['Architecture'] != 'amd64' or image['Os'] != 'linux':
        raise RuntimeError('Loaded image identity/platform mismatch')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    checkpoint = BACKUPS / stamp
    BACKUPS.mkdir(mode=0o700, exist_ok=True)
    # Save the prior image outside VM103 before stopping the app.
    checkpoint.mkdir(mode=0o700)
    run('docker', 'image', 'save', '-o', str(checkpoint / 'previous-image.tar'), old['Image'], timeout=600)
    os.chmod(checkpoint / 'previous-image.tar', 0o600)
    atomic_json(checkpoint / 'manifest.json', {'old_version': old_version, 'old_image': old['Image'], 'candidate': m})
    print('Saved previous image to NAS; confirming idle status for 65 seconds.', flush=True)
    # A second sample > stale timeout apart, plus one immediately before stop.
    time.sleep(65)
    try:
        if require_idle(get_metrics()) != ids:
            raise RuntimeError('Printer identities changed')
        queue_clear()
    except Exception as e:
        shutil.rmtree(checkpoint)
        print(f'Deferred after settling check: {e}')
        return
    atomic_json(ROOT / 'transaction.json', {'checkpoint': str(checkpoint), 'old_image': old['Image'], 'old_version': old_version})
    snapshot = False
    switched = False
    committed = False
    try:
        compose('stop', '--timeout', '30', 'bambuddy')
        if current_image()['State']['Running']:
            raise RuntimeError('Container did not stop')
        # Directory already holds the saved old image.
        save_checkpoint_files(checkpoint)
        snapshot = True
        print('Stopped-service checkpoint complete; testing copied data with networking disabled.', flush=True)
        probe(m, checkpoint)
        print('Isolated migration/startup passed; starting production candidate.', flush=True)
        switched = True
        override(m['local_tag'])
        compose('up', '-d', '--no-build', '--pull', 'never', 'bambuddy')
        health(m['version'], ids)
        if current_image()['Image'] != image['Id'] or current_image()['HostConfig']['NetworkMode'] != old['HostConfig']['NetworkMode']:
            raise RuntimeError('Running image or network mode mismatch')
        committed = True
        atomic_json(checkpoint / 'complete.json', {'version': m['version']})
        atomic_json(ROOT / 'last-result.json', {'result': 'installed', 'version': m['version'], 'checkpoint': str(checkpoint), 'at': stamp})
        (ROOT / 'transaction.json').unlink()
        (ROOT / 'ready.json').unlink()
        shutil.rmtree(ROOT / 'ready')
        # Retain three successful rollback checkpoints; never prune unrelated backups/images.
        completed = sorted(p for p in BACKUPS.iterdir() if re.fullmatch(r'\d{8}T\d{6}Z', p.name) and (p / 'complete.json').exists())
        for expired in completed[:-3]:
            shutil.rmtree(expired)
        prune_owned_images({old['Image'], image['Id']})
        print(f"Installed {m['version']}; version, database migration and printer reconnection passed. Checkpoint: {checkpoint}")
    except BaseException as error:
        if committed:
            raise RuntimeError('Release is healthy but receipt/retention cleanup failed; inspect runtime state before retrying') from error
        if switched:
            compose('stop', '--timeout', '30', 'bambuddy')
            if snapshot:
                restore_checkpoint(checkpoint)
            override(old['Image'])
        compose('up', '-d', '--no-build', '--pull', 'never', 'bambuddy')
        health(old_version, ids)
        atomic_json(ROOT / 'blocked.json', {'version': m['version'], 'reason': str(error), 'checkpoint': str(checkpoint)})
        (ROOT / 'transaction.json').unlink()
        raise RuntimeError('Candidate failed; old version recovered; bundle blocked from automatic retry') from error

def prune_owned_images(keep):
    try:
        tags = run('docker', 'image', 'ls', '--filter', 'reference=bambuddy-staged:*', '--format', '{{.Repository}}:{{.Tag}}').splitlines()
        for tag in tags:
            if not re.fullmatch(r'bambuddy-staged:\d+\.\d+\.\d+(?:\.\d+)?-[a-f0-9]{12}', tag):
                continue
            identity = json.loads(run('docker', 'image', 'inspect', tag))[0]['Id']
            if identity not in keep and not run('docker', 'ps', '-a', '--filter', f'ancestor={tag}', '--format', '{{.ID}}'):
                run('docker', 'image', 'rm', tag)
    except Exception:
        print('Owned-image cleanup deferred; installed release remains healthy.')

def save_checkpoint_files(directory):
    with tarfile.open(directory / 'stack.tar', 'w') as archive:
        for name in ('data', 'logs', '.env', 'docker-compose.yml', 'docker-compose.override.yml'):
            if (STACK / name).exists():
                archive.add(STACK / name, arcname=name)
    os.chmod(directory / 'stack.tar', 0o600)
    sqlite_check(STACK / 'data')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    os.umask(0o077)
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(RuntimeError('Termination requested')))
    with (ROOT / 'update.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        publish() if args.publish else apply(args.check)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
