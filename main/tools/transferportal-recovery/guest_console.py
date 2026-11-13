#!/usr/bin/env python3
"""Quote all guest commands; transfer scripts in bounded chunks, never SSH secrets."""
import base64, json, shlex, subprocess, sys, time
from pathlib import Path
VM='9108'
def guest(command, timeout=30):
    args=['qm','guest','exec',VM,'--timeout',str(timeout),'--','/bin/bash','-lc',command]
    r=subprocess.run(['ssh','-o','BatchMode=yes','proxmox-lan',shlex.join(args)],capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode())
    result=json.loads(r.stdout)
    if result.get('exited') and result.get('exitcode'): raise RuntimeError(json.dumps(result))
    return result

def upload(source,target):
    assert target.startswith('/root/'), 'Only disposable guest root staging permitted'
    guest('umask 077; : > '+shlex.quote(target))
    data=base64.b64encode(Path(source).read_bytes()).decode()
    for start in range(0,len(data),4096):
        guest('printf %s '+shlex.quote(data[start:start+4096])+' | base64 -d >> '+shlex.quote(target))

if __name__=='__main__':
    if sys.argv[1]=='upload': upload(sys.argv[2],sys.argv[3]);print('Uploaded guest test artifact')
    elif sys.argv[1]=='exec': print(json.dumps(guest(sys.argv[2],1)))
    elif sys.argv[1]=='status':
        r=subprocess.run(['ssh','proxmox-lan','qm guest exec-status '+VM+' '+str(int(sys.argv[2]))],capture_output=True);print(r.stdout.decode());print(r.stderr.decode())
