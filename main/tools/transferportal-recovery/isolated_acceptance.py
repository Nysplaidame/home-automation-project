#!/usr/bin/env python3
"""Run ONLY in disposable no-NIC VM, via guest-agent console."""
import hashlib, json, os, shutil, sqlite3, subprocess, tarfile, time
from pathlib import Path
import urllib.request, urllib.parse, http.cookiejar
MEDIA=Path('/mnt/recovery-media')
RESULT=Path('/root/transferportal-recovery-result.json')
def run(*args, **kwargs):
    return subprocess.run(args,check=True,capture_output=True,**kwargs)
def snapshot(path):
    return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
def helper(action,params):
    r=run('runuser','-u','transferportal','--','sudo','-n','/usr/local/lib/transferportal/root-helper',input=json.dumps({'action':action,'params':params}).encode())
    return json.loads(r.stdout)
def database(path):
    c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True)
    assert c.execute('PRAGMA integrity_check').fetchone()==('ok',)
    rows={t:c.execute('SELECT * FROM '+t+' ORDER BY id').fetchall() for t in ('jobs','audit_log')};c.close();return rows

assert os.geteuid()==0
assert not [p for p in Path('/sys/class/net').iterdir() if p.name!='lo'], 'VM must have no NIC'
assert not run('ip','route').stdout.strip(), 'VM must have no routes'
mounts=json.loads(run('findmnt','--json').stdout)
assert not any(x in json.dumps(mounts) for x in ('nfs','cifs')), 'No production shares allowed'
run('systemctl','mask','transferportal.service')
manifest=json.loads((MEDIA/'manifest.json').read_text())
assert hashlib.sha256((MEDIA/'checkpoint.tar.gz').read_bytes()).hexdigest()==manifest['sha256']
saved=Path('/root/recovery-saved');saved.mkdir(mode=0o700,exist_ok=True)
run('tar','--acls','--xattrs','--numeric-owner','-xzf',str(MEDIA/'checkpoint.tar.gz'),'-C',str(saved))
original=database(saved/'var/lib/transferportal/jobs.sqlite')
assert {t:len(rows) for t,rows in original.items()}==manifest['counts']
# Never install production mount units, environment, or service unit.
for rel in ('opt/transferportal','usr/local/lib/transferportal','etc/sudoers.d/transferportal'):
    source=saved/rel;dest=Path('/')/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    if source.is_dir(): shutil.copytree(source,dest,dirs_exist_ok=True)
    else: shutil.copy2(source,dest)
if subprocess.run(['id','transferportal'],capture_output=True).returncode:
    run('useradd','--system','--home-dir','/var/lib/transferportal','--shell','/usr/sbin/nologin','transferportal')
for path in ('/etc/transferportal','/var/lib/transferportal','/var/log/transferportal','/srv/transferportal'):
    Path(path).mkdir(parents=True,exist_ok=True)
run('chown','-R','transferportal:transferportal','/var/lib/transferportal')
run('chown','root:transferportal','/var/log/transferportal');run('chmod','0750','/var/log/transferportal')
run('chmod','0440','/etc/sudoers.d/transferportal');run('visudo','-cf','/etc/sudoers.d/transferportal')
# Package-matched offline rsync libraries, without replacing guest system libraries.
runtime=Path('/opt/recovery-rsync');runtime.mkdir(exist_ok=True)
run('tar','-xzf',str(MEDIA/'rsync-runtime.tar.gz'),'-C',str(runtime))
Path('/usr/local/bin/rsync').write_text('#!/bin/sh\nexport LD_LIBRARY_PATH=/opt/recovery-rsync/lib/x86_64-linux-gnu\nexec /opt/recovery-rsync/usr/bin/rsync "$@"\n')
Path('/usr/local/bin/rsync').chmod(0o755)
run('rsync','--version')
fixture=Path('/mnt/recovery-fixture');fixture.mkdir(exist_ok=True)
run('mount','-t','tmpfs','-o','size=64m','tmpfs',str(fixture))
python='/opt/transferportal/venv/bin/python'
site=Path(run(python,'-I','-c','import transferportal; print(transferportal.__path__[0])').stdout.decode().strip())
results={'candidate_root_helper_sha256':hashlib.sha256(Path('/root/recovery-root-helper.py').read_bytes()).hexdigest() if Path('/root/recovery-root-helper.py').exists() else None,'checkpoint':manifest['generation'],'checkpoint_sha256':manifest['sha256'],
         'isolation':{'no_nic':True,'no_routes':True,'no_nas_mounts':True},'history_counts':manifest['counts'],'generations':[]}
for generation in ('saved','candidate'):
    if generation=='candidate':
        candidate=Path('/root/recovery-candidate');candidate.mkdir(exist_ok=True)
        run('tar','-xzf',str(MEDIA/'candidate.tar.gz'),'-C',str(candidate))
        shutil.copytree(candidate/'transferportal',site,dirs_exist_ok=True)
        if Path('/root/recovery-root-helper.py').exists():
            shutil.copy2('/root/recovery-root-helper.py',site/'root_helper.py')
        shutil.copy2(candidate/'packaging/root-helper','/usr/local/lib/transferportal/root-helper')
        Path('/usr/local/lib/transferportal/root-helper').chmod(0o755)
    shutil.copy2(saved/'var/lib/transferportal/jobs.sqlite','/var/lib/transferportal/jobs.sqlite')
    run('chown','transferportal:transferportal','/var/lib/transferportal/jobs.sqlite')
    src=fixture/generation/'source';dst=fixture/generation/'destination'
    src.mkdir(parents=True);dst.mkdir(parents=True)
    (src/'nested').mkdir();(src/'sample.txt').write_text('restore acceptance fixture\n');(src/'nested/data.bin').write_bytes(bytes(range(256))*4096)
    (dst/'keep.txt').write_text('destination extra must survive\n')
    before=snapshot(src);extras=snapshot(dst)
    slug='recovery-'+generation
    config={'bind_host':'127.0.0.1','bind_port':8099,'database_path':'/var/lib/transferportal/jobs.sqlite',
      'log_dir':'/var/log/transferportal','helper_path':'/usr/local/lib/transferportal/root-helper',
      'portal_base':'/srv/transferportal','session_secret_file':'/etc/transferportal/test-session.secret',
      'portals':[{'slug':slug,'display_name':'Disposable restore fixture','source_path':str(src),'destination_path':str(dst),
      'allow_source_delete':False,'allow_destination_delete':False,'metadata_policy':'compatible','enabled':True}]}
    run(python,'-c','import yaml,sys,json; open("/etc/transferportal/config.yaml","w").write(yaml.safe_dump(json.loads(sys.argv[1])))',json.dumps(config))
    Path('/etc/transferportal/test-session.secret').write_text('isolated-test-session-only-'+'a'*48)
    run('chmod','0750','/etc/transferportal');run('chown','root:transferportal','/etc/transferportal')
    for name in ('config.yaml','test-session.secret'):
        run('chown','root:transferportal','/etc/transferportal/'+name);run('chmod','0640','/etc/transferportal/'+name)
    assert helper('create-portal',{'slug':slug,'source_path':str(src),'destination_path':str(dst)})['ok']
    env=os.environ.copy();env.update(TRANSFERPORTAL_CONFIG='/etc/transferportal/config.yaml',TRANSFERPORTAL_ADMIN_PASSWORD='disposable-acceptance-only')
    proc=subprocess.Popen(['runuser','-u','transferportal','--','/opt/transferportal/venv/bin/uvicorn','transferportal.app:create_app','--factory','--host','127.0.0.1','--port','8099'],env=env,stdout=open('/root/recovery-'+generation+'.log','wb'),stderr=subprocess.STDOUT)
    try:
        jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        def request(path,data=None):
            req=urllib.request.Request('http://127.0.0.1:8099'+path,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers={'Origin':'http://127.0.0.1:8099'})
            return client.open(req,timeout=5)
        for _ in range(40):
            try: request('/login');break
            except Exception: time.sleep(.25)
        else: raise RuntimeError('App failed startup')
        request('/login',{'username':'admin','password':'disposable-acceptance-only'}).read()
        assert request('/jobs').status==200
        assert database(Path('/var/lib/transferportal/jobs.sqlite'))==original, 'History changed on read'
        ids=[]
        for route in ('/jobs/dry-run','/jobs/copy'):
            response=request(route,{'portal_slug':slug});job_id=int(response.url.rsplit('/',1)[-1]);ids.append(job_id)
            for _ in range(100):
                request('/jobs/'+str(job_id)).read()
                conn=sqlite3.connect('/var/lib/transferportal/jobs.sqlite');row=conn.execute('SELECT status,exit_code,command_json FROM jobs WHERE id=?',(job_id,)).fetchone();conn.close()
                if row[0] in ('completed','failed','interrupted'): break
                time.sleep(.1)
            assert row[:2]==('completed',0),row[:2]
            if route.endswith('dry-run'):
                assert '--dry-run' in json.loads(row[2]); assert snapshot(dst)==extras,'Preview changed destination'
        assert snapshot(src)==before,'Copy changed source'
        after=snapshot(dst)
        assert all(after[k]==v for k,v in before.items()) and all(after[k]==v for k,v in extras.items())
        history=database(Path('/var/lib/transferportal/jobs.sqlite'))
        assert all(history[t][:len(original[t])]==original[t] for t in original),'Historical rows mutated'
        denials=[]
        if generation=='candidate':
            for option in ('--delete','--remove-source-files','--rsync-path=sh'):
                denied=helper('run-rsync',{'command':['rsync',option,'/srv/transferportal/'+slug+'/source/','/srv/transferportal/'+slug+'/destination/'],'log_path':'/var/log/transferportal/deny.log','status_path':'/var/log/transferportal/deny.status.json'})
                assert not denied['ok'];denials.append(option)
            denied=helper('run-rsync',{'command':['rsync','-r','/etc/','/srv/transferportal/'+slug+'/destination/'],'log_path':'/var/log/transferportal/deny.log','status_path':'/var/log/transferportal/deny.status.json'})
            assert not denied['ok'];denials.append('outside-portal-path')
        results['generations'].append({'name':generation,'job_ids':ids,'preview_unchanged_destination':True,'copy_hashes_match':True,'source_unchanged':True,'destination_extra_retained':True,'history_preserved':True,'helper_denials':denials,'fixture_files':len(before)})
    finally:
        proc.terminate();proc.wait(timeout=10)
    # Test mounts only; no production mount units have ever been restored.
    for endpoint in ('source','destination'):
        unit=run('systemd-escape','--path','--suffix=mount','/srv/transferportal/'+slug+'/'+endpoint).stdout.decode().strip()
        run('systemctl','disable','--now',unit)
        Path('/etc/systemd/system',unit).unlink()
    run('systemctl','daemon-reload')
RESULT.write_text(json.dumps(results,indent=2));RESULT.chmod(0o600)
print(json.dumps(results))
