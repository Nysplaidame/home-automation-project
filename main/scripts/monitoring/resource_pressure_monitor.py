#!/usr/bin/env python3
"""Bounded Proxmox-local pressure checks; authenticated ntfy, durable debounce.

No dependencies, disk scans, restarts, or remediation. Secrets stay in /etc.
Guest-agent reads use fixed /proc commands and bounded timeouts.
"""
import argparse
import fcntl
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

STATE = Path('/var/lib/resource-pressure-monitor')
CONFIG = Path('/etc/resource-pressure-monitor.json')
COLLECTION_ERRORS = (OSError, ValueError, KeyError, IndexError, TypeError,
                     ZeroDivisionError, RuntimeError, subprocess.TimeoutExpired)
PROC_COMMAND = ('cat /proc/meminfo; echo __MEMPSI__; cat /proc/pressure/memory; '
                'echo __IOPSI__; cat /proc/pressure/io; echo __VMSTAT__; '
                'cat /proc/vmstat; echo __DISK__; df -P /')


def command(args, timeout=8, allow_empty=False):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                            check=False)
    if result.returncode and not (allow_empty and result.returncode == 1
                                 and not result.stdout.strip() and not result.stderr.strip()):
        raise RuntimeError('command failed: ' + args[0])
    return result.stdout


def pairs(text):
    return {line.split()[0].rstrip(':'): int(line.split()[1])
            for line in text.splitlines() if len(line.split()) >= 2
            and line.split()[1].isdigit()}


def psi(text):
    return {line.split()[0]: float(dict(item.split('=') for item in
            line.split()[1:])['avg60']) for line in text.splitlines() if line.strip()}


def guest_sample(raw):
    mem, rest = raw.split('__MEMPSI__', 1)
    memory, rest = rest.split('__IOPSI__', 1)
    io, rest = rest.split('__VMSTAT__', 1)
    vm, disk = rest.split('__DISK__', 1)
    values = pairs(mem)
    return {'available_pct': 100 * values['MemAvailable'] / values['MemTotal'],
            'available_mib': values['MemAvailable'] / 1024,
            'memory_psi': psi(memory).get('some', 0),
            'io_psi': psi(io).get('some', 0),
            'oom': pairs(vm).get('oom_kill', 0),
            'disk_pct': int(disk.strip().splitlines()[-1].split()[-2].rstrip('%'))}


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def notify(config, title, body, priority=3):
    request = urllib.request.Request(config['url'], data=body.encode(), method='POST',
        headers={'Authorization': 'Bearer ' + config['token'], 'Title': title,
                 'Priority': str(priority), 'Tags': 'warning'})
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError('notification rejected')
    print('notification accepted: ' + title)


def evaluate(snapshot, previous):
    """Return (key, bad, description, immediate); never use cached VM RAM %."""
    checks = []
    for name, sample in snapshot['samples'].items():
        checks.extend([
            (name + ':memory', sample['available_pct'] < 10 or sample['available_mib'] < 256,
             f"{name}: usable memory {sample['available_pct']:.1f}% / {sample['available_mib']:.0f} MiB", False),
            (name + ':memory-psi', sample['memory_psi'] >= 10,
             f"{name}: memory stall avg60 {sample['memory_psi']:.1f}%", False),
            (name + ':io-psi', sample['io_psi'] >= 20,
             f"{name}: disk stall avg60 {sample['io_psi']:.1f}%", False),
        ])
        if sample.get('disk_pct') is not None:
            checks.append((name + ':disk', sample['disk_pct'] >= 85,
                           f"{name}: root filesystem {sample['disk_pct']}% full", False))
        old = previous.get('samples', {}).get(name)
        delta = sample['oom'] - old['oom'] if old else 0
        # Only deltas: boot resets and historical OOMs are not new incidents.
        checks.append((name + ':oom', delta > 0,
                       f'{name}: {delta} new OOM kill(s)', True))
        if 'limit_pct' in sample:
            checks.append((name + ':limit', sample['noncache_pct'] >= 85 or
                           (sample['limit_pct'] >= 95 and sample['available_pct'] < 10),
                f"{name}: cgroup memory {sample['limit_pct']:.1f}% of limit; "
                f"anon + shared memory {sample['noncache_pct']:.1f}%", False))
    checks.extend([
        ('host:blocked', snapshot['blocked'] >= 8,
         f"Host: {snapshot['blocked']} processes blocked on disk", False),
        ('host:load', snapshot['load'] >= 2 * snapshot['cpus'],
         f"Host: load {snapshot['load']:.1f} on {snapshot['cpus']} CPUs", False),
        ('host:thin-pool', snapshot['thin_pct'] >= 80,
         f"Host: LVM thin pool {snapshot['thin_pct']:.1f}% allocated", False),
        ('host:thin-metadata', snapshot['thin_metadata_pct'] >= 70,
         f"Host: LVM thin metadata {snapshot['thin_metadata_pct']:.1f}% allocated", False),
    ])
    for name in snapshot['expected'] + ['collector:inventory']:
        checks.append((name + ':availability', name in snapshot['errors'],
                       name + ': ' + snapshot['errors'].get(name, 'sampling healthy'), False))
    for row in snapshot.get('inventory', []) if snapshot.get('inventory_valid', True) else []:
        if row['status'] == 'running':
            checks.append((str(row['vmid']) + ':cpu', row.get('cpu', 0) >= .95,
                           f"Guest {row['vmid']}: CPU {100 * row.get('cpu', 0):.1f}%", False))
    warning = snapshot.get('kernel_warning')
    old_warning = previous.get('kernel_warning')
    checks.append(('host:kernel-warning', bool(warning and warning != old_warning),
                   'Host kernel: ' + (warning or 'no new disk/hang warning'), True))
    return checks


def transition(checks, previous, now):
    """Three samples + 120 seconds, recovery after three good samples.

    Re-alert every hour; failed delivery leaves last_sent unchanged for retry.
    OOM events latch pending until delivery succeeds.
    """
    states = dict(previous)
    messages = []
    for key, bad, description, immediate in checks:
        state = dict(states.get(key, {}))
        if immediate:
            if bad:
                state['pending'] = description
            if state.get('pending'):
                messages.append((key, 'Kernel disk or hang warning' if key == 'host:kernel-warning'
                                 else 'OOM detected', state['pending'], 5, 'event'))
        elif bad:
            state['bad_count'] = state.get('bad_count', 0) + 1
            state['good_count'] = 0
            state.setdefault('bad_since', now)
            if (state['bad_count'] >= 3 and now - state['bad_since'] >= 120
                    and (not state.get('active') or now - state.get('last_sent', 0) >= 3600)):
                messages.append((key, 'Resource pressure', description, 4, 'alert'))
        else:
            state['bad_count'] = 0
            state.pop('bad_since', None)
            state['good_count'] = state.get('good_count', 0) + 1
            if state.get('active') and state['good_count'] >= 3:
                messages.append((key, 'Resource pressure recovered', description, 3, 'recover'))
        states[key] = state
    return states, messages


def collect(config, previous=None):
    previous = previous or {}
    samples = {'host': guest_sample(command(['/bin/sh', '-c', PROC_COMMAND]))}
    errors = {}
    inventory_valid = True
    try:
        resources = json.loads(command(['pvesh', 'get', '/cluster/resources', '--type', 'vm',
                                        '--output-format', 'json'], timeout=10))
        if not isinstance(resources, list) or any(not isinstance(r, dict) or
                not str(r.get('vmid', '')).isdigit() or r.get('type') not in ('lxc', 'qemu')
                or 'status' not in r for r in resources):
            raise ValueError('invalid inventory')
    except COLLECTION_ERRORS as error:
        inventory_valid = False
        # Last-known identities let us collect FRESH guest counters. Cached CPU
        # and CT disk usage must not be evaluated or described as current.
        resources = previous.get('inventory', [])
        errors['collector:inventory'] = 'Proxmox inventory unavailable (' + type(error).__name__ + ')'
    expected = list(config['expected_guests'])
    inventory = {str(row['vmid']): row for row in resources}
    for vmid, row in inventory.items():
        if row['status'] != 'running':
            if vmid in expected:
                errors[vmid] = 'expected guest is stopped'
            continue
        if vmid not in expected:
            expected.append(vmid)
        try:
            if row['type'] == 'lxc':
                base = Path('/sys/fs/cgroup/lxc') / vmid
                stat = pairs((base / 'memory.stat').read_text())
                limit = int((base / 'memory.max').read_text())
                used = int((base / 'memory.current').read_text())
                sample = {'available_pct': 100 * (limit - used + stat.get('inactive_file', 0)) / limit,
                          'available_mib': (limit - used + stat.get('inactive_file', 0)) / 1048576,
                          'memory_psi': psi((base / 'memory.pressure').read_text()).get('some', 0),
                          'io_psi': psi((base / 'io.pressure').read_text()).get('some', 0),
                          'oom': pairs((base / 'memory.events').read_text()).get('oom_kill', 0),
                          'disk_pct': 100 * row['disk'] / row['maxdisk'] if inventory_valid else None,
                          'limit_pct': 100 * used / limit,
                          'noncache_pct': 100 * (stat.get('anon', 0) + stat.get('shmem', 0)) / limit}
            elif vmid in config.get('ssh_guests', {}):
                entry = config['ssh_guests'][vmid]
                raw = command(['ssh', '-i', entry['key'], '-o', 'BatchMode=yes',
                    '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=3',
                    '-o', 'UserKnownHostsFile=/etc/resource-pressure-monitor-known-hosts',
                    entry['target'], PROC_COMMAND], timeout=7)
                sample = guest_sample(raw)
            else:
                result = json.loads(command(['qm', 'guest', 'exec', vmid, '--timeout', '4',
                                             '--', '/bin/sh', '-c', PROC_COMMAND], timeout=7))
                if not result.get('exited') or result.get('exitcode') != 0:
                    raise RuntimeError('guest agent sample incomplete')
                sample = guest_sample(result['out-data'])
            samples[vmid] = sample
        except COLLECTION_ERRORS:
            errors[vmid] = 'resource sample unavailable (bounded timeout or guest agent failure)'
    for vmid in expected:
        if vmid not in inventory:
            errors[vmid] = 'expected guest missing from inventory'
    thin = command(['lvs', '--noheadings', '-o', 'data_percent,metadata_percent', 'pve/data']).split()
    # Bound both the interval and output. Historical October 8 hangs must not
    # generate a fresh incident at installation or on every timer tick.
    since = max(int(previous.get('timestamp', 0)), int(time.time()) - 120)
    kernel = command(['journalctl', '-k', '-b', '--since', '@' + str(since),
                      '--grep', 'blocked for more than|hung task|I/O error|nvme.*timeout|nvme.*reset',
                      '-o', 'json', '-n', '20', '--no-pager'], timeout=5, allow_empty=True)
    warnings = [json.loads(line) for line in kernel.splitlines() if line.strip()]
    warning = (warnings[-1]['__REALTIME_TIMESTAMP'] + ': ' + warnings[-1]['MESSAGE'][:500]
               if warnings else None)
    return {'timestamp': time.time(), 'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'samples': samples, 'expected': expected, 'errors': errors,
            'inventory': resources, 'inventory_valid': inventory_valid,
            'load': os.getloadavg()[0], 'cpus': os.cpu_count(),
            'blocked': pairs(Path('/proc/stat').read_text())['procs_blocked'],
            'thin_pct': float(thin[0]), 'thin_metadata_pct': float(thin[1]), 'kernel_warning': warning}


def collector_health(config, error=None, immediate=False, now=None):
    """Durable failure/recovery delivery without a systemd rate-limit latch."""
    now = time.time() if now is None else now
    STATE.mkdir(mode=0o700, exist_ok=True)
    with (STATE / 'health.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = STATE / 'collector-health.json'
        health = json.loads(path.read_text()) if path.exists() else {}
        if error:
            health['failures'] = health.get('failures', 0) + 1
            health.setdefault('failed_since', now)
            # Only the exception class/reason is retained: command output,
            # credentials and arbitrary exception text must never be published.
            health['last_error'] = error
            if (immediate or (health['failures'] >= 3 and now - health['failed_since'] >= 120)):
                if not health.get('active') or now - health.get('last_sent', 0) >= 3600:
                    health['pending'] = 'failure'
            if health.get('pending') == 'recovery':
                health.pop('pending')
        else:
            health['last_success'] = now
            health['failures'] = 0
            health.pop('failed_since', None)
            if health.get('active'):
                health['pending'] = 'recovery'
            elif health.get('pending') == 'failure':
                # Undelivered incident still gets reported, including that it
                # has recovered; do not silently lose it when ntfy returns.
                health['pending'] = 'recovered-incident'
        atomic_json(path, health)
        kind = health.get('pending')
        if kind:
            title = {'failure':'Resource monitor FAILED', 'recovery':'Resource monitor recovered',
                     'recovered-incident':'Resource monitor incident recovered'}[kind]
            body = ('Proxmox collector failure: ' + health.get('last_error', 'unknown')
                    if kind == 'failure' else 'Proxmox resource collection is healthy again.' +
                    (' A previous failure notification could not be delivered.'
                     if kind == 'recovered-incident' else ''))
            try:
                notify(config, title, body, 5 if kind == 'failure' else 3)
            except (OSError, RuntimeError):
                health['delivery_error'] = True
                print('collector-health delivery failed; pending retry')
            else:
                health['active'] = kind == 'failure'
                health['last_sent'] = now
                health.pop('pending', None)
                health.pop('delivery_error', None)
        atomic_json(path, health)
        return health


def run_check(config):
    """Keep previous samples on collection failure; never fake fresh success."""
    STATE.mkdir(mode=0o700, exist_ok=True)
    path = STATE / 'state.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    try:
        snapshot = collect(config, previous.get('snapshot', {}))
    except COLLECTION_ERRORS as error:
        collector_health(config, type(error).__name__)
        print('collection unavailable; retry next minute: ' + type(error).__name__)
        return
    if previous.get('snapshot', {}).get('boot_id') != snapshot['boot_id']:
        previous = {}
    # Missing guest samples must not reset OOM baselines across a coverage gap.
    baseline = previous.get('snapshot', {}).copy()
    baseline['samples'] = previous.get('last_samples', baseline.get('samples', {}))
    checks = evaluate(snapshot, baseline)
    states, messages = transition(checks, previous.get('checks', {}), snapshot['timestamp'])
    outbox = {key:tuple(value['undelivered']) for key,value in states.items()
              if value.get('undelivered')}
    outbox.update({message[0]:message for message in messages})
    messages = sorted(outbox.values(), key=lambda message: -message[3])
    for key, title, body, priority, kind in messages:
        states[key]['undelivered'] = [key, title, body, priority, kind]
    last_samples = dict(baseline['samples'])
    last_samples.update(snapshot['samples'])
    def save(delivery_errors):
        atomic_json(path, {'snapshot':snapshot, 'checks':states,
                          'last_samples':last_samples, 'delivery_errors':delivery_errors})
    save(previous.get('delivery_errors', []))
    atomic_json(STATE / 'latest.json', snapshot)
    delivery_errors = []
    for key, title, body, priority, kind in messages[:4]:
        if kind == 'alert' and states[key].get('bad_count') == 0:
            title = 'Resource pressure incident recovered'
            body += '. Condition recovered before notification delivery.'
            kind = 'recovered-incident'
        try:
            notify(config, title, body, priority)
        except (OSError, RuntimeError):
            print('notification delivery failed; will retry: ' + key)
            delivery_errors.append(key)
            continue
        states[key]['last_sent'] = snapshot['timestamp']
        states[key].pop('undelivered', None)
        if kind == 'event':
            states[key].pop('pending', None)
        else:
            states[key]['active'] = kind == 'alert'
        # Checkpoint each accepted send so a later timeout does not resend it.
        save(delivery_errors)
    save(delivery_errors)
    collector_health(config)
    print(f"sample complete: {len(snapshot['samples'])} systems; {len(snapshot['errors'])} unavailable")


def status():
    state = json.loads((STATE / 'state.json').read_text())
    latest = json.loads((STATE / 'latest.json').read_text())
    health_path = STATE / 'collector-health.json'
    return {'age_seconds':round(time.time()-latest['timestamp']),
            'coverage':len(latest['samples']), 'errors':latest['errors'],
            'active_or_pending':{k:v for k,v in state['checks'].items()
                                 if v.get('active') or v.get('pending') or v.get('undelivered')},
            'delivery_errors':state.get('delivery_errors', []),
            'collector_health':json.loads(health_path.read_text()) if health_path.exists() else {},
            'load':latest['load'], 'blocked':latest['blocked']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-notification', action='store_true')
    parser.add_argument('--failure', action='store_true')
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    if args.status:
        print(json.dumps(status(), indent=2))
        return
    config = json.loads(CONFIG.read_text())
    if args.test_notification:
        notify(config, 'Resource monitor TEST', 'Test delivery from Proxmox. No incident.')
    elif args.failure:
        collector_health(config, 'unexpected collector exit (see service journal)', immediate=True)
    else:
        run_check(config)


if __name__ == '__main__':
    main()
