"""Stage, activate and secure the authenticated VentSys card without actuator calls.

Uses the existing Samba session. For later releases set VENTSYS_HA_TOKEN in
the process environment from a private credential source; never a public file.
The migration fallback reads the old credential only from HA's private backup
after staging. The secure phase revokes that exact dedicated dashboard token.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import urllib.error
import urllib.request
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed
import yaml
from validate_ventsys_contract import script_drift

ROOT = Path(__file__).resolve().parents[1]
LIVE = Path(r'\\192.168.20.101\config')
BASE = 'https://192.168.20.101:8123'
VERSION = '20261107-8'
FILES = ['ventsys-card.js','ventsys-model.mjs','ventsys-modes.mjs','ventsys-dashboard.css','ventsys-schematic.svg']
RESOURCE = '/local/ventsys-v2/ventsys-card.js?v=' + VERSION
CTX = ssl.create_default_context()
# Keep chain and hostname verification; the installed legacy CA lacks key usage.
CTX.verify_flags &= ~ssl.VERIFY_X509_STRICT

def credential(backup=None):
    if os.environ.get('VENTSYS_HA_TOKEN'):
        return os.environ['VENTSYS_HA_TOKEN']
    path = backup/'ventsys-config.js' if backup else LIVE/'www/ventsys-config.js'
    match = re.search(r'''\btoken\s*:\s*['"]([^'"]+)['"]''',path.read_text(encoding='utf-8-sig'))
    if not match: raise RuntimeError('Use a private VENTSYS_HA_TOKEN process environment value; no public credential is configured')
    return match[1]

def api(path, token=None, data=None):
    headers = {'Content-Type':'application/json'}
    if token: headers['Authorization'] = 'Bearer ' + token
    req = urllib.request.Request(BASE+path, headers=headers, data=None if data is None else json.dumps(data).encode())
    with urllib.request.urlopen(req,context=CTX,timeout=25) as response:
        raw = response.read()
        return json.loads(raw) if response.headers.get_content_type() == 'application/json' else raw

class HA:
    def __init__(self, token): self.token=token; self.id=0
    def __enter__(self):
        self.ws=connect(BASE.replace('https:','wss:')+'/api/websocket',ssl=CTX,proxy=None,open_timeout=15)
        self.ws.recv(timeout=15);self.ws.send(json.dumps({'type':'auth','access_token':self.token}))
        if json.loads(self.ws.recv(timeout=15)).get('type')!='auth_ok': raise RuntimeError('HA authentication failed')
        return self
    def __exit__(self,*args): self.ws.close()
    def call(self,kind,**fields):
        self.id+=1;self.ws.send(json.dumps({'id':self.id,'type':kind,**fields}))
        while True:
            result=json.loads(self.ws.recv(timeout=20))
            if result.get('id')==self.id: break
        if not result.get('success'): raise RuntimeError('HA '+kind+': '+result.get('error',{}).get('code','unknown error'))
        return result.get('result')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def no_running_scripts(token):
    states=api('/api/states',token)
    if any(s['entity_id'].startswith('script.') and s['state']=='on' for s in states): raise RuntimeError('Defer script reload while a script is running')
    return states

def stage():
    token=credential(); no_running_scripts(token)
    expected=yaml.safe_load((ROOT/'configs/home-assistant/ventsys_ha_scripts_arbitrated.yaml').read_text(encoding='utf-8'))['script']
    live=yaml.safe_load((LIVE/'packages/ventsys_ha_scripts.yaml').read_text(encoding='utf-8'))['script']
    if script_drift(expected,live): raise RuntimeError('Deploy and verify the matching arbitration backend before staging dashboard assets')
    operating='ventsys_operating_modes.yaml'
    if yaml.safe_load((ROOT/'configs/home-assistant'/operating).read_text(encoding='utf-8')) != yaml.safe_load((LIVE/'packages'/operating).read_text(encoding='utf-8')):
        raise RuntimeError('Deploy and verify matching independent operating-mode helpers/scripts before staging dashboard assets')
    backup=LIVE/'backups'/('ventsys-dashboard-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%SZ'))
    backup.mkdir(parents=True)
    for name in ['ventsys-dashboard.html','ventsys-card-wrapper.html','ventsys-config.js']:
        shutil.copy2(LIVE/'www'/name,backup/name)
    destination=LIVE/'packages/ventsys_dashboard_package.yaml'
    if destination.exists(): shutil.copy2(destination,backup/destination.name)
    with HA(token) as ha:
        (backup/'lovelace-dashboard.json').write_text(json.dumps(ha.call('lovelace/config',url_path='dashboard-ventsys'),indent=2),encoding='utf-8')
        resources=ha.call('lovelace/resources')
        (backup/'lovelace-resources.json').write_text(json.dumps(resources,indent=2),encoding='utf-8')
    shutil.copyfile(ROOT/'configs/home-assistant/ventsys_dashboard_package.yaml',destination)
    check=api('/api/config/core/check_config',token,{})
    if check.get('result')!='valid': raise RuntimeError('HA configuration is not valid; activation stopped')
    api('/api/services/script/reload',token,{})
    script=api('/api/states/script.ventsys_dashboard_command',token)
    if script.get('state')!='off': raise RuntimeError('Dashboard command script did not load idle')
    assets=LIVE/'www/ventsys-v2';assets.mkdir(exist_ok=True)
    for name in FILES:
        shutil.copyfile(ROOT/'dashboards'/name,assets/name)
        if api('/local/ventsys-v2/'+name)!= (ROOT/'dashboards'/name).read_bytes(): raise RuntimeError('Served asset mismatch: '+name)
    with HA(token) as ha:
        existing=[r for r in resources if r['url'].split('?')[0]==RESOURCE.split('?')[0]]
        if existing: resource=ha.call('lovelace/resources/update',resource_id=existing[0]['id'],url=RESOURCE,res_type='module')
        else: resource=ha.call('lovelace/resources/create',url=RESOURCE,res_type='module')
    manifest={'version':VERSION,'backup':str(backup),'phase':'staged','resource':resource,'hashes':{name:digest(assets/name) for name in FILES},'ha_config':'valid'}
    (backup/'release.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('STAGED:',backup)

def activate(backup):
    token=credential(backup)
    manifest=json.loads((backup/'release.json').read_text(encoding='utf-8'))
    for name,sha in manifest['hashes'].items():
        if digest(LIVE/'www/ventsys-v2'/name)!=sha: raise RuntimeError('Staged asset changed: '+name)
    with HA(token) as ha:
        config=ha.call('lovelace/config',url_path='dashboard-ventsys')
        desired=yaml.safe_load((ROOT/'configs/home-assistant/ventsys_dashboard_views.yaml').read_text(encoding='utf-8'))
        for view in desired['views']:
            index=next((i for i,item in enumerate(config['views']) if item.get('path')==view['path']),None)
            if index is None: config['views'].append(view)
            else: config['views'][index]={**config['views'][index],**view}
        ha.call('lovelace/config/save',url_path='dashboard-ventsys',config=config)
        if ha.call('lovelace/config',url_path='dashboard-ventsys')!=config: raise RuntimeError('HA dashboard read-back mismatch')
    for name in ['ventsys-dashboard.html','ventsys-card-wrapper.html']:shutil.copyfile(ROOT/'dashboards'/name,LIVE/'www'/name)
    manifest['phase']='active-awaiting-live-acceptance';(backup/'release.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('ACTIVE: /dashboard-ventsys/0; verify live UI before secure phase.')

def refresh(backup):
    """Update tested assets with a new immutable version before acceptance."""
    token=credential(backup)
    manifest=json.loads((backup/'release.json').read_text(encoding='utf-8'))
    for name in FILES:
        shutil.copyfile(ROOT/'dashboards'/name,LIVE/'www/ventsys-v2'/name)
        if api('/local/ventsys-v2/'+name)!=(ROOT/'dashboards'/name).read_bytes(): raise RuntimeError('Served asset mismatch: '+name)
    with HA(token) as ha:
        resources=ha.call('lovelace/resources')
        resource=next(r for r in resources if r['url'].split('?')[0]==RESOURCE.split('?')[0])
        resource=ha.call('lovelace/resources/update',resource_id=resource['id'],url=RESOURCE,res_type='module')
    manifest.update(version=VERSION,resource=resource,hashes={name:digest(LIVE/'www/ventsys-v2'/name) for name in FILES},live_ui_accepted=False)
    (backup/'release.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('REFRESHED: tested asset hashes and HA resource version updated; repeat live acceptance.')

def secure(backup):
    manifest=json.loads((backup/'release.json').read_text(encoding='utf-8'))
    if not manifest.get('live_ui_accepted'): raise RuntimeError('Record live_ui_accepted only after real HA card acceptance')
    # Always revoke the exposed legacy token, even if management uses another credential.
    legacy=re.search(r'''\btoken\s*:\s*['"]([^'"]+)['"]''',(backup/'ventsys-config.js').read_text(encoding='utf-8-sig'))[1]
    issuer=json.loads(base64.urlsafe_b64decode(legacy.split('.')[1]+'==='))['iss']
    token=credential(backup)
    with HA(token) as ha:
        metadata=next((r for r in ha.call('auth/refresh_tokens') if r['id']==issuer),None)
        if not metadata or metadata.get('client_name')!='VentSys Dashboard': raise RuntimeError('Legacy token identity does not match the dedicated dashboard credential')
        for p in (LIVE/'www').glob('*ventsys*'):
            if p.is_file() and legacy.encode() in p.read_bytes() and p.name!='ventsys-config.js':
                shutil.move(str(p),str(backup/('public-'+p.name)))
        (LIVE/'www/ventsys-config.js').write_text('// Public compatibility file. Authentication is owned by Home Assistant.\nwindow.VENTSYS_CONFIG = Object.freeze({});\n',encoding='utf-8')
        try:
            ha.call('auth/delete_refresh_token',refresh_token_id=issuer)
        except ConnectionClosed:
            # Revoking the current token can close its WebSocket before the
            # result frame arrives. The independent HTTP 401 check below is
            # authoritative; a closed socket alone is never accepted as proof.
            pass
    try: api('/api/',legacy)
    except urllib.error.HTTPError as error:
        if error.code!=401: raise
    else: raise RuntimeError('Revoked token was still accepted')
    if legacy.encode() in api('/local/ventsys-config.js'): raise RuntimeError('Public credential still present')
    manifest['phase']='secured';manifest['legacy_token_revoked']=True
    (backup/'release.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('SECURED: public credential removed; dedicated legacy token returns HTTP 401.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('phase',choices=['stage','activate','refresh','secure']);parser.add_argument('--backup',type=Path)
    args=parser.parse_args()
    if args.phase=='stage':stage()
    elif not args.backup:parser.error('--backup is required after staging')
    elif args.phase=='activate':activate(args.backup)
    elif args.phase=='refresh':refresh(args.backup)
    else:secure(args.backup)
