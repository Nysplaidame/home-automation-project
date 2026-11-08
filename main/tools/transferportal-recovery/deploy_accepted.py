#!/usr/bin/env python3
"""Bounded offline deployment of the isolated-accepted generation on OMV."""
import hashlib, importlib.metadata, json, os, shutil, sqlite3, subprocess, sys, tarfile, time
from pathlib import Path
import urllib.request, urllib.error, urllib.parse, http.cookiejar
GEN='20261002T213135Z'
RELEASE=Path('/root/transferportal-release-'+GEN)
CHECKPOINT=Path('/srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c/backups/transferportal-checkpoints')/GEN
APP=Path('/opt/transferportal');STAGE=Path('/opt/transferportal.next-'+GEN);PREVIOUS=Path('/opt/transferportal.previous-'+GEN)
BASEURL='http://192.168.40.50:8088'
def run(*args,input=None):
    return subprocess.run(args,check=True,capture_output=True,input=input)
def db_rows():
    conn=sqlite3.connect('file:/var/lib/transferportal/jobs.sqlite?mode=ro',uri=True)
    assert conn.execute('PRAGMA integrity_check').fetchone()==('ok',)
    rows={t:conn.execute('SELECT * FROM '+t+' ORDER BY id').fetchall() for t in ('jobs','audit_log')}
    conn.close();return rows

def idle():
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try: args=(p/'cmdline').read_bytes().split(b'\0')
        except (FileNotFoundError,PermissionError,ProcessLookupError):continue
        if args and (Path(os.fsdecode(args[0])).name=='rsync' or b'transferportal.job_runner' in args or b'transferportal.root_helper' in args):raise RuntimeError('Transfer/helper active; abort')
    c=sqlite3.connect('file:/var/lib/transferportal/jobs.sqlite?mode=ro',uri=True)
    assert c.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running','verifying','waiting_for_delete_confirmation','deleting_source')").fetchone()==(0,)
    c.close()

def helper(action,params):
    return json.loads(run('runuser','-u','transferportal','--','sudo','-n','/usr/local/lib/transferportal/root-helper',input=json.dumps({'action':action,'params':params}).encode()).stdout)

assert os.geteuid()==0
assert APP.resolve()==APP and not STAGE.exists() and not PREVIOUS.exists()
manifest=json.loads((CHECKPOINT/'manifest.json').read_text())
assert hashlib.sha256((CHECKPOINT/'checkpoint.tar.gz').read_bytes()).hexdigest()==manifest['sha256']
idle();before=db_rows()
assert {t:len(rows) for t,rows in before.items()}==manifest['counts']
mounts_before=run('findmnt','--json','--output','TARGET,SOURCE,FSTYPE,OPTIONS').stdout
old_env=Path('/etc/transferportal/transferportal.env').read_bytes()
old_wrapper=Path('/usr/local/lib/transferportal/root-helper').read_bytes()
old_sudoers=Path('/etc/sudoers.d/transferportal').read_bytes()
secret_hash=hashlib.sha256(Path('/etc/transferportal/session.secret').read_bytes()).hexdigest()
config_hash=hashlib.sha256(Path('/etc/transferportal/config.yaml').read_bytes()).hexdigest()
candidate=RELEASE/'candidate';candidate.mkdir(mode=0o700)
run('tar','-xzf',str(RELEASE/'candidate.tar.gz'),'-C',str(candidate))
hashes=json.loads((RELEASE/'source-hashes.json').read_text())
for name,digest in hashes.items():assert hashlib.sha256((candidate/name).read_bytes()).hexdigest()==digest
shutil.copytree(APP,STAGE,symlinks=True)
for sub in ('transferportal','packaging'):
    destination=STAGE/sub
    if destination.exists():shutil.rmtree(destination)
    shutil.copytree(candidate/sub,destination)
for name in ('pyproject.toml','README.md'):shutil.copy2(candidate/name,STAGE/name)
python=str(STAGE/'venv/bin/python')
site=Path(run(python,'-I','-c','import transferportal;print(transferportal.__path__[0])').stdout.decode().strip())
assert site.is_relative_to(STAGE/'venv') and site.name=='transferportal'
shutil.rmtree(site);shutil.copytree(candidate/'transferportal',site)
run(python,'-I','-m','pip','check')
run(python,'-I','-c','from transferportal.root_helper import ROOT_POLICY; from transferportal.app import create_app; assert str(ROOT_POLICY.portal_base)=="/srv/transferportal"')
assert run(python,'-I','-c','import importlib.metadata;print(importlib.metadata.version("transferportal"))').stdout.strip()==b'0.1.0'
run('visudo','-cf',str(candidate/'packaging/sudoers/transferportal'))
idle();run('systemctl','stop','transferportal')
swapped=False
try:
    idle();assert db_rows()==before, 'History changed during staging; abort'
    APP.rename(PREVIOUS);STAGE.rename(APP);swapped=True
    shutil.copy2(candidate/'packaging/root-helper','/usr/local/lib/transferportal/root-helper')
    Path('/usr/local/lib/transferportal/root-helper').chmod(0o755)
    shutil.copy2(candidate/'packaging/sudoers/transferportal','/etc/sudoers.d/transferportal')
    Path('/etc/sudoers.d/transferportal').chmod(0o440)
    # Existing credentials and unrelated host settings are preserved byte-for-byte.
    lines=old_env.decode().splitlines()
    existing=next((line.split('=',1)[1] for line in lines if line.startswith('TRANSFERPORTAL_ALLOWED_ORIGINS=')), '')
    origins=[s.strip().strip('"') for s in existing.split(',') if s.strip()]
    if 'https://homepage.home.local:8201' not in origins:origins.append('https://homepage.home.local:8201')
    lines=[line for line in lines if not line.startswith('TRANSFERPORTAL_ALLOWED_ORIGINS=')]
    lines.append('TRANSFERPORTAL_ALLOWED_ORIGINS='+','.join(origins))
    Path('/etc/transferportal/transferportal.env').write_text('\n'.join(lines)+'\n')
    run('visudo','-cf','/etc/sudoers.d/transferportal')
    run('systemctl','start','transferportal')
    for _ in range(40):
        try:
            assert urllib.request.urlopen(BASEURL+'/login',timeout=2).status==200;break
        except Exception:time.sleep(.25)
    else:raise RuntimeError('Service startup failed')
    assert run('systemctl','is-active','transferportal').stdout.strip()==b'active'
    assert db_rows()==before
    assert hashlib.sha256(Path('/etc/transferportal/session.secret').read_bytes()).hexdigest()==secret_hash
    assert hashlib.sha256(Path('/etc/transferportal/config.yaml').read_bytes()).hexdigest()==config_hash
    assert run('findmnt','--json','--output','TARGET,SOURCE,FSTYPE,OPTIONS').stdout==mounts_before
    imported=Path(run('/opt/transferportal/venv/bin/python','-I','-c','import transferportal.root_helper as h;assert hasattr(h,"ROOT_POLICY");print(h.__file__)').stdout.decode().strip())
    assert hashlib.sha256(imported.read_bytes()).hexdigest()==hashes['transferportal/root_helper.py']
    assert b' -I -m ' in Path('/usr/local/lib/transferportal/root-helper').read_bytes()
    assert helper('list-mounts',{})['ok']
    denied=[]
    for option in ('--delete','--remove-source-files','--rsync-path=sh'):
        result=helper('run-rsync',{'command':['rsync',option,'/srv/transferportal/smoke/source/','/srv/transferportal/smoke/destination/'],'log_path':'/var/log/transferportal/denial.log','status_path':'/var/log/transferportal/denial.status.json'})
        assert not result['ok'];denied.append(option)
    for headers in ({},{'Origin':'https://attacker.invalid'}):
        req=urllib.request.Request(BASEURL+'/logout',data=b'',headers=headers)
        try:urllib.request.urlopen(req);raise AssertionError('Write should be denied')
        except urllib.error.HTTPError as exc:assert exc.code==403
    # Credentials loaded only within the service's existing environment; never printed.
    auth_code='''import os,json,urllib.request,urllib.parse,http.cookiejar,sqlite3
base="http://192.168.40.50:8088"
c=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
p=os.environ.get("TRANSFERPORTAL_ADMIN_PASSWORD")
if p:
 req=urllib.request.Request(base+"/login",data=urllib.parse.urlencode({"username":os.environ.get("TRANSFERPORTAL_ADMIN_USER","admin"),"password":p}).encode(),headers={"Origin":"https://homepage.home.local:8201"})
 assert c.open(req).url.rstrip("/")==base
 assert c.open(base+"/jobs").status==200
 print("LOGIN_HISTORY_OK")
else: print("HASH_ONLY_LOGIN_REQUIRES_BROWSER")
'''
    # systemd transient service reads the protected EnvironmentFile; no secret argv.
    script=RELEASE/'login-check.py';script.write_text(auth_code);script.chmod(0o700)
    auth=run('systemd-run','--quiet','--wait','--pipe','--property=EnvironmentFile=/etc/transferportal/transferportal.env','/opt/transferportal/venv/bin/python',str(script)).stdout.decode().strip()
    assert auth=='LOGIN_HISTORY_OK', 'Automated login not proved'
    assert db_rows()==before
    record={'generation':GEN,'checkpoint_sha256':manifest['sha256'],'source_hashes':hashes,'effective_helper_import':str(imported),
      'service_active':True,'history_preserved':True,'counts':manifest['counts'],'mounts_preserved':True,'config_preserved':True,
      'session_secret_preserved':True,'root_policy_present':True,'isolated_wrapper':True,'helper_denials':denied,
      'originless_foreign_writes_denied':True,'homepage_origin_login_history_passed':True,
      'previous_app_path':str(PREVIOUS),'live_transfer_data_modified':False}
    (CHECKPOINT/'deployment.json').write_text(json.dumps(record,indent=2));(CHECKPOINT/'deployment.json').chmod(0o600)
    print(json.dumps(record))
except Exception:
    run('systemctl','stop','transferportal')
    if swapped:
        failed=Path('/opt/transferportal.failed-'+GEN);APP.rename(failed);PREVIOUS.rename(APP)
    Path('/etc/transferportal/transferportal.env').write_bytes(old_env)
    Path('/usr/local/lib/transferportal/root-helper').write_bytes(old_wrapper)
    Path('/etc/sudoers.d/transferportal').write_bytes(old_sudoers)
    run('systemctl','start','transferportal')
    print('Previous application/helper/environment restored; live DB untouched',file=sys.stderr)
    raise
