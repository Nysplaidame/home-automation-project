"""Run the migration suite in a temporary OMV OS-disk fixture tree over SSH.

Only test code and selected sanitized source templates are transferred. No live
source/configuration file is edited, and no household dataset is copied.
"""
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
MAIN = HERE.parents[1]
files = {"main/tools/storage-migration/" + p.name: p.read_text(encoding="utf-8")
         for p in HERE.glob("*.py") if p.name != "run_linux_tests.py"}
files["main/tools/storage-migration/cutover-contract.json"] = (HERE / "cutover-contract.json").read_text()
for name in ("configs/omv/system/omv-config-backup.sh", "configs/omv/system/omv-config-backup.service",
             "configs/docker-host/system/mediamtx-config-backup.sh",
             "configs/docker-host/stacks/calibre-web/docker-compose.yml",
             "configs/omv/system/omv-health-snapshot.py",
             "apps/troubleshooting-dashboard/additional-routes.js"):
    files["main/" + name] = (MAIN / name).read_text(encoding="utf-8")
script = "FILES=" + repr(files) + "\n" + r'''
import pathlib,tempfile,subprocess,sys
with tempfile.TemporaryDirectory(prefix='storage-migration-tests-',dir='/root') as temporary:
    root=pathlib.Path(temporary)
    for name,body in FILES.items():
        path=root/name
        if root not in path.resolve().parents: raise ValueError('Fixture path escape')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(body,encoding='utf-8')
    tests=root/'main/tools/storage-migration'
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(tests),'-v'],
                          cwd=tests,capture_output=True,text=True)
    print(result.stdout,end='');print(result.stderr,end='')
    sys.exit(result.returncode)
'''
if __name__ == "__main__":
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "omv-lan", "python3 -"],
                            input=script, capture_output=True, text=True, encoding="utf-8", timeout=120)
    print(result.stdout, end=""); print(result.stderr, end="")
    raise SystemExit(result.returncode)
