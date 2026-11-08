"""Read-only reference inventory. Writes only local audit evidence.

Does not emit complete config lines, credentials, database contents, or keys.
Live scans are bounded to configuration/source roots; limitations are explicit.
"""
import concurrent.futures
import csv
import json
import os
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
PATTERN = r"""(?i)(?:(?<![a-z0-9_])[YZ]:[\\/]+[^\s"'<>|;,)}\]]*|(?<!:)(?:\\\\|//)192\.168\.40\.50[\\/]+[^\s"'<>|;,)}\]]*|/srv/dev-disk-by-uuid-[a-z0-9-]+(?:/[^\s"'<>|;,)}\]]*)?|/(?:export/(?:media|immich|frigate|ha-backups|configs)|mnt/(?:omv|nas)|srv/transferportal)(?:/[^\s"'<>|;,)}\]]*)?|calibre-library|a216b8bb-708e-4342-a5be-a415cdc465fa|fdb92af7-371c-4793-8d98-ff47e961498d)"""
RX = re.compile(PATTERN)
ROOTS = [
    Path(r"K:\Documents\Obsidian\home-automation-project"),
    Path(r"K:\Documents\Obsidian\household-hub"),
]
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next",
        ".pytest_cache", ".mypy_cache", ".ruff_cache"}

def disposition(path):
    name = str(path).replace("\\", "/").lower()
    if "/worktrees/" in name:
        return "other-checkout"
    if "/_archive/" in name or "/audits/" in name:
        return "historical-evidence"
    if name.startswith("wiki/"):
        return "wiki"
    if any(s in name for s in ["/vendor/", "/dist/", "/build/"]):
        return "generated-or-vendor"
    if any(s in name for s in ["/tests/", "/test_"]):
        return "test-fixture"
    if name.startswith("tmp_"):
        return "local-operational-script"
    return "canonical-review"

def local_scan():
    rows, errors, count = [], [], 0
    for root in ROOTS:
        command = ["rg", "--files", "--hidden", "--no-ignore", str(root)]
        for name in SKIP:
            command += ["-g", "!**/" + name + "/**"]
        candidates = subprocess.run(command,
                                    capture_output=True, text=True, check=True).stdout.splitlines()
        for filename in candidates:
                p = Path(filename)
                if OUT in p.parents or any(s in p.parts for s in SKIP):
                    continue
                if p.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml", ".toml",
                    ".ini", ".conf", ".cfg", ".py", ".sh", ".ps1", ".js", ".ts", ".tsx",
                    ".html", ".csv", ".xml", ".service", ".timer", ".mount", ".automount",
                    ".env", ".example", ".mermaid", ".mjs", ".cmd", ".bat"} and p.name not in {
                    "fstab", "exports", "Dockerfile", ".gitignore", "root-helper"}:
                    continue
                try:
                    if p.stat().st_size > 8_000_000:
                        continue
                    data = p.read_bytes()
                    if b"\0" in data[:4096]:
                        continue
                    count += 1
                    for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
                        hits = sorted(set(RX.findall(line)))
                        if hits:
                            rows.append({"file": str(p.relative_to(root)), "repository": root.name,
                                         "line": n, "references": " | ".join(hits),
                                         "historical": "_archive" in p.parts or "audits" in p.parts,
                                         "disposition": disposition(p.relative_to(root))})
                except OSError as e:
                    errors.append(str(e))
    with (OUT / "repository-references.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["repository", "file", "line", "references", "historical", "disposition"])
        w.writeheader()
        w.writerows(rows)
    return {"text_files_scanned": count, "matching_lines": len(rows),
            "matching_files": len({(r["repository"], r["file"]) for r in rows}), "errors": errors}

REMOTE = r'''
import os, re, json, subprocess
rx = re.compile(PATTERN)
rows, errors, skipped = [], [], 0
skip = {".git", "node_modules", ".venv", "venv", "__pycache__", "proc", "sys",
        "cache", "Cache", "logs", "log", "models", "backups", "runs", "recordings",
        "upload", "library", "thumbs", "encoded-video", "pgdata"}
exts = {".conf",".cfg",".ini",".json",".yaml",".yml",".sh",".py",".ps1",".xml",
        ".service",".timer",".mount",".automount",".env",".js",".toml",".list",".exports"}
special = {"fstab","exports","crontab","config","config.xml","storage.cfg",
           "jobs.cfg",".env","root-helper","config.yaml","config.json"}
for root in ["/etc", "/opt", "/usr/local", "/root", "/home", "/var/spool/cron"]:
    if not os.path.exists(root): continue
    for cur, dirs, files in os.walk(root, onerror=lambda e: errors.append(str(e))):
        dirs[:] = [d for d in dirs if d not in skip]
        for name in files:
            p = os.path.join(cur, name)
            if not (os.path.splitext(name)[1] in exts or name in special or
                    "/cron" in cur or "systemd" in cur or cur.startswith("/usr/local")): continue
            try:
                if os.path.islink(p) or os.stat(p).st_size > 4000000:
                    skipped += 1
                    continue
                with open(p, "rb") as f: data = f.read()
                if b"\0" in data[:4096]: continue
                for n, line in enumerate(data.decode("utf-8",errors="replace").splitlines(),1):
                    hits=sorted(set(rx.findall(line)))
                    if hits: rows.append({"file":p,"line":n,"references":hits})
            except OSError as e: errors.append(str(e))
def run(args):
    p=subprocess.run(args,capture_output=True,text=True,timeout=40)
    return {"exit":p.returncode,"stdout":p.stdout,"stderr":p.stderr}
result={"references":rows,"errors":errors,"skipped_large_or_symlink":skipped,
        "mounts":run(["findmnt","-t","nfs,nfs4","-o","TARGET,SOURCE,OPTIONS"]),
        "timers":run(["systemctl","list-timers","--all","--no-pager"])}
for engine in ["docker","podman"]:
    if subprocess.run(["sh","-c","command -v "+engine],capture_output=True).returncode: continue
    p=subprocess.run([engine,"ps","-aq"],capture_output=True,text=True)
    ids=p.stdout.split()
    if ids:
        p=subprocess.run([engine,"inspect"]+ids,capture_output=True,text=True)
        if p.returncode==0:
            result[engine]=[{"name":c.get("Name"),"state":c.get("State",{}).get("Status"),
                            "mounts":c.get("Mounts",[]),
                            "compose_workdir":c.get("Config",{}).get("Labels",{}).get("com.docker.compose.project.working_dir")}
                           for c in json.loads(p.stdout)]
print(json.dumps(result))
'''

def host_scan(alias):
    code = "PATTERN = " + repr(PATTERN) + "\n" + REMOTE
    p = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                        alias, "python3 -"], input=code, capture_output=True,
                       text=True, timeout=180)
    if p.returncode:
        result = {"error": p.stderr, "exit": p.returncode}
    else:
        try:
            result = json.loads(p.stdout)
        except ValueError:
            result = {"error": "Non-JSON response", "stderr": p.stderr}
    (OUT / (alias + ".json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return {"host": alias, "references":len(result.get("references",[])),
            "error":result.get("error"),"read_errors":len(result.get("errors",[]))}

if __name__ == "__main__":
    summary = {"local": local_scan()}
    hosts = ["omv-lan", "docker-host-lan", "proxmox-lan", "monitoring-lan", "llm-host-lan"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        summary["hosts"] = list(pool.map(host_scan, hosts))
    (OUT / "scan-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
