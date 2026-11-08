"""Download a stable release on Windows/WSL and publish an offline VM103 bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import urllib.request

ROOT = Path(os.environ.get('BAMBUDDY_STAGING_ROOT', 'K:/Documents/home-automation-update-staging/bambuddy'))
HOST = 'docker-host-lan'
REMOTE = '/var/lib/home-automation-updates/bambuddy'

def run(*args):
    return subprocess.check_output(args, text=True, encoding='utf-8').strip()

def version(value):
    if not re.fullmatch(r'v?\d+\.\d+\.\d+(?:\.\d+)?', value):
        raise ValueError('Not a numeric stable release version')
    return tuple(int(x) for x in value.lstrip('v').split('.'))

def ssh(command):
    return run('ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10', HOST, command)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    # Exclusive local file creation prevents overlapping manual/scheduled staging.
    lock = ROOT / 'stage.lock'
    with lock.open('a+') as handle:
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        request = urllib.request.Request('https://api.github.com/repos/maziggy/bambuddy/releases/latest', headers={'User-Agent': 'home-automation-bambuddy-updater'})
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.load(response)
        tag = release['tag_name']
        target = tag.lstrip('v')
        version(tag)
        if release['draft'] or release['prerelease']:
            raise ValueError('Refusing a draft or prerelease')
        current = json.loads(ssh('curl -fsS --max-time 10 http://127.0.0.1:8000/api/v1/updates/version'))['version']
        if version(target) <= version(current):
            print(f'No newer stable release: installed {current}, upstream {target}')
            return
        if version(target)[0] != version(current)[0]:
            raise RuntimeError(f'Major release {target} requires manual review; installed {current}')
        if args.check:
            print(f'Stable release available: {current} -> {target}')
            return
        if ssh(f'test -f {REMOTE}/ready.json && cat {REMOTE}/ready.json || true'):
            print('An update is already staged; waiting for installation before staging another.')
            return
        reference = f'ghcr.io/maziggy/bambuddy:{target}'
        docker = ('wsl', '-d', 'Ubuntu', '--', 'docker')
        subprocess.run((*docker, 'pull', '--platform', 'linux/amd64', reference), check=True)
        info = json.loads(run(*docker, 'image', 'inspect', reference))[0]
        if info['Os'] != 'linux' or info['Architecture'] != 'amd64':
            raise ValueError('Wrong image platform')
        image_id = info['Id']
        local_tag = f'bambuddy-staged:{target}-{image_id[7:19]}'
        run(*docker, 'tag', reference, local_tag)
        archive = ROOT / 'image.tar'
        # Stream to Windows; avoid relying on WSL's cached drive mounts.
        with archive.open('wb') as output:
            subprocess.run((*docker, 'save', local_tag), stdout=output, check=True)
        # Docker engines can identify an image by manifest or config digest.
        # Record both identities from the source engine and exported config.
        with tarfile.open(archive) as saved:
            entries = json.load(saved.extractfile('manifest.json'))
            if len(entries) != 1:
                raise ValueError('Expected a single-platform image archive')
            config_bytes = saved.extractfile(entries[0]['Config']).read()
            config_digest = 'sha256:' + hashlib.sha256(config_bytes).hexdigest()
        with archive.open('rb') as archive_handle:
            digest = hashlib.file_digest(archive_handle, 'sha256').hexdigest()
        metadata = {'schema': 1, 'version': target, 'image_id': image_id, 'config_digest': config_digest, 'local_tag': local_tag,
                    'archive_sha256': digest, 'archive_bytes': archive.stat().st_size,
                    'upstream_digest': next(x for x in info['RepoDigests'] if x.startswith('ghcr.io/maziggy/bambuddy@sha256:')), 'release_url': release['html_url']}
        manifest = ROOT / 'manifest.json'
        manifest.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        ssh(f'install -d -m 700 {REMOTE}/incoming')
        subprocess.run(('scp', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', str(archive), str(manifest), f'{HOST}:{REMOTE}/incoming/'), check=True)
        print(ssh('/usr/local/sbin/bambuddy-offline-update.py --publish'))
        archive.unlink()
        # Remove only this job's temporary tags; never prune the Docker engine.
        run(*docker, 'image', 'rm', local_tag, reference)
        print(f'Staged stable Bambuddy {target}; VM103 needs no registry access.')

if __name__ == '__main__':
    main()
