#!/usr/bin/env python3
"""Root-only matched TransferPortal checkpoint; never backs up transfer data."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tarfile
from datetime import datetime, timezone

BASE = Path('/srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c/backups/transferportal-checkpoints')
ACTIVE = ('queued','running','verifying','waiting_for_delete_confirmation','deleting_source')
def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout

def idle():
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            args = (proc/'cmdline').read_bytes().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if args and (Path(os.fsdecode(args[0])).name == 'rsync' or b'transferportal.job_runner' in args or b'transferportal.root_helper' in args):
            raise RuntimeError('An rsync/helper/job-runner process is active; checkpoint deferred')
    conn = sqlite3.connect('file:/var/lib/transferportal/jobs.sqlite?mode=ro',uri=True)
    count = conn.execute('SELECT count(*) FROM jobs WHERE status IN (?,?,?,?,?)', ACTIVE).fetchone()[0]
    conn.close()
    if count:
        raise RuntimeError('Database contains active jobs; checkpoint deferred')

assert os.geteuid() == 0
mount = json.loads(run('findmnt','--json','--target',str(BASE.parent)))['filesystems'][0]
assert mount['target'] == str(BASE.parents[1]) and mount['fstype'] == 'ext4', 'Expected data disk not mounted'
assert run('systemctl','is-active','transferportal').strip() == 'active'
idle()
generation = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
BASE.mkdir(mode=0o700,exist_ok=True)
run('setfacl','-b',str(BASE)); run('setfacl','-k',str(BASE)); BASE.chmod(0o700)
out = BASE/generation
out.mkdir(mode=0o700)
run('systemctl','stop','transferportal')
try:
    idle()
    unit_paths = list(Path('/etc/systemd/system').glob('srv-transferportal*.mount'))
    unit_paths += list(Path('/etc/systemd/system/multi-user.target.wants').glob('srv-transferportal*.mount'))
    paths = ['/opt/transferportal','/etc/transferportal','/var/lib/transferportal','/var/log/transferportal',
             '/usr/local/lib/transferportal','/etc/sudoers.d/transferportal','/etc/systemd/system/transferportal.service']
    paths += [str(p) for p in unit_paths]
    archive = out/'checkpoint.tar.gz'
    run('tar','--acls','--xattrs','--numeric-owner','-czf',str(archive),'-C','/',*[p.lstrip('/') for p in paths])
    archive.chmod(0o600)
    conn=sqlite3.connect('file:/var/lib/transferportal/jobs.sqlite?mode=ro',uri=True)
    integrity=conn.execute('PRAGMA integrity_check').fetchall()
    assert integrity == [('ok',)]
    counts={table:conn.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in ('jobs','audit_log')}
    conn.close()
    manifest={'generation':generation,'sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),
              'sqlite_integrity':'ok','counts':counts,'included_paths':paths,
              'mount_snapshot':run('findmnt','--json','--output','TARGET,SOURCE,FSTYPE,OPTIONS'),
              'service_unit':run('systemctl','cat','transferportal'),
              'note':'Stopped matched app/config/database/log/helper/policy. Not transfer-data backup.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (out/'manifest.json').chmod(0o600)
    with tarfile.open(archive) as tf:
        assert tf.getmember('var/lib/transferportal/jobs.sqlite').size>0
    print(json.dumps({'checkpoint':str(out),'sha256':manifest['sha256'],'counts':counts,'integrity':'ok'}))
finally:
    run('systemctl','start','transferportal')
    assert run('systemctl','is-active','transferportal').strip()=='active'
    print('Production service resumed')
