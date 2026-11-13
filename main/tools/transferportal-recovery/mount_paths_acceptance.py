#!/usr/bin/env python3
"""Supplemental real systemd path test, only in the disposable no-NIC VM."""
import json, subprocess
from pathlib import Path

def run(*args,input=None):
    return subprocess.run(args,check=True,capture_output=True,input=input)
def helper(action,params):
    return json.loads(run('runuser','-u','transferportal','--','sudo','-n','/usr/local/lib/transferportal/root-helper',input=json.dumps({'action':action,'params':params}).encode()).stdout)
assert len(list(Path('/sys/class/net').iterdir())) == 1
src=Path('/mnt/recovery-fixture/source 100% "photos"');src.mkdir()
dst=Path('/mnt/recovery-fixture/destination 100% "photos"');dst.mkdir()
(src/'proof.txt').write_text('correct mount source, not a literal outer-quote directory\n')
slug='recovery-special'
assert helper('create-portal',{'slug':slug,'source_path':str(src),'destination_path':str(dst)})['ok']
assert Path('/srv/transferportal',slug,'source/proof.txt').read_bytes()==(src/'proof.txt').read_bytes()
Path('/srv/transferportal',slug,'destination/proof.txt').write_text('destination bind verified')
assert (dst/'proof.txt').read_text()=='destination bind verified'
for suffix in ('source','destination'):
    unit=run('systemd-escape','--path','--suffix=mount','/srv/transferportal/'+slug+'/'+suffix).stdout.decode().strip()
    run('systemctl','disable','--now',unit)
    Path('/etc/systemd/system',unit).unlink()
run('systemctl','daemon-reload')
result=Path('/root/transferportal-recovery-result.json');data=json.loads(result.read_text());data['systemd_literal_paths']={'spaces':True,'percent':True,'embedded_quotes':True,'source_and_destination_verified':True};result.write_text(json.dumps(data,indent=2))
print('PASS: real systemd bind mounts preserve spaces, percent signs and embedded quotes')
