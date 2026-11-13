#!/usr/bin/env python3
"""Cold Hub checkpoint. Default is read-only preflight; --execute interrupts Hub.

No retention deletion, image rebuild, Compose up or migration command is run.
Deploy/start only through the coordinated-backup maintenance procedure.
"""
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "household-hub"
STORES = {"postgres": "/var/lib/postgresql/data", "redis": "/data", "qdrant": "/qdrant/storage"}
WRITERS = ("web", "worker", "api")
EXPECTED_NFS = "192.168.40.50:/export/backups-docker-host"


class BackupError(RuntimeError):
    pass


def run(args, timeout=60):
    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        # Do not emit inspect environments, command stderr or protected payloads.
        raise BackupError(f"{args[0]} operation failed") from exc


def durable(path):
    """Flush a file or directory before publishing a generation."""
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class Engine:
    def __init__(self, target, stack):
        self.target = Path(target)
        self.stack = Path(stack)

    def mount(self):
        fields = run(["findmnt", "-n", "-o", "SOURCE,FSTYPE,TARGET", "-T", str(self.target)]).split()
        if len(fields) != 3 or fields[0] != EXPECTED_NFS or fields[1] not in {"nfs", "nfs4"} or Path(fields[2]) != self.target:
            raise BackupError("Expected OMV backup mount is unavailable")
        if self.target.is_symlink() or not self.target.is_dir():
            raise BackupError("Backup target must be the real mounted directory")

    def inspect(self, container_id):
        return json.loads(run(["docker", "inspect", container_id]))[0]

    def discover(self):
        self.mount()
        for relative in (".env", "infra/docker", "data/obsidian-exports"):
            source = self.stack / relative
            if not source.exists() or source.is_symlink():
                raise BackupError("Required deployment/export input is missing or symlinked")
        ids = run(["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={PROJECT}"]).split()
        services = {}
        for container_id in ids:
            item = self.inspect(container_id)
            labels = item["Config"].get("Labels", {})
            service = labels.get("com.docker.compose.service")
            if labels.get("com.docker.compose.project") != PROJECT or service not in {*STORES, *WRITERS} or service in services:
                raise BackupError("Unexpected or duplicate Hub container")
            if item["State"].get("Paused") or item["State"].get("Restarting"):
                raise BackupError("Hub is not in a stable checkpoint state")
            record = {"id": item["Id"], "image": item["Image"], "was_running": item["State"]["Running"]}
            if service in STORES:
                mounts = [m for m in item["Mounts"] if m["Destination"] == STORES[service]]
                if len(mounts) != 1 or mounts[0]["Type"] != "volume":
                    raise BackupError("Store must have exactly one named data volume")
                volume = json.loads(run(["docker", "volume", "inspect", mounts[0]["Name"]]))[0]
                volume_labels = volume.get("Labels") or {}
                if volume_labels.get("com.docker.compose.project") != PROJECT or volume_labels.get("com.docker.compose.volume") != service + "-data":
                    raise BackupError("Unexpected store volume ownership")
                source = Path(volume["Mountpoint"])
                if source.is_symlink() or not source.is_dir() or source != Path(mounts[0]["Source"]):
                    raise BackupError("Store volume mapping is invalid")
                record.update(volume=volume["Name"], source=str(source), destination=STORES[service])
            services[service] = record
        if not {*STORES, "api", "web"}.issubset(services):
            raise BackupError("Required Hub containers are absent")
        if any(services[s]["was_running"] for s in WRITERS if s in services) and not all(services[s]["was_running"] for s in STORES):
            raise BackupError("Running writers require all original stores running")
        volumes = {services[s]["volume"] for s in STORES}
        for container_id in run(["docker", "ps", "-q"]).split():
            item = self.inspect(container_id)
            if item["Id"] not in {r["id"] for r in services.values()} and any(
                m.get("Name") in volumes for m in item["Mounts"]
            ):
                raise BackupError("Another running container uses a Hub data volume")
        return services

    def stop(self, record):
        run(["docker", "stop", "--time", "30", record["id"]], timeout=45)

    def running(self, record):
        return self.inspect(record["id"])["State"]["Running"]

    def quiesced(self, services):
        observed = self.discover()
        if {k: v["id"] for k, v in observed.items()} != {k: v["id"] for k, v in services.items()}:
            raise BackupError("Hub container membership changed during checkpoint")
        if any(self.running(record) for record in services.values()):
            raise BackupError("A Hub writer/store is still running")
        for service in STORES:
            state = self.inspect(services[service]["id"])["State"]
            if state.get("OOMKilled") or state.get("ExitCode") == 137:
                raise BackupError("Store stopped uncleanly; checkpoint rejected")

    def ready(self, record):
        deadline = time.monotonic() + 60
        while True:
            state = self.inspect(record["id"])["State"]
            if state["Running"] and state.get("Health", {}).get("Status", "healthy") == "healthy":
                return
            if time.monotonic() >= deadline:
                raise BackupError("Original Hub container did not become ready")
            time.sleep(2)

    def start(self, record):
        if self.inspect(record["id"])["Image"] != record["image"]:
            raise BackupError("Original image identity changed")
        run(["docker", "start", record["id"]])
        self.ready(record)

    def archive(self, destination, source, members):
        self.mount()
        run(["tar", "--numeric-owner", "-czf", str(destination), "-C", str(source), "--", *members], timeout=1800)
        os.chmod(destination, 0o600)
        run(["gzip", "-t", str(destination)], timeout=1800)
        try:
            subprocess.run(["tar", "-tzf", str(destination)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
        except (OSError, subprocess.SubprocessError) as exc:
            raise BackupError("Archive traversal failed") from exc
        self.mount()

    def health(self, services):
        if services["api"]["was_running"]:
            run(["docker", "exec", services["api"]["id"], "python", "-c",
                 "import urllib.request; r=urllib.request.urlopen('http://127.0.0.1:8091/health',timeout=10); assert r.status==200"], timeout=20)


def restore(engine, services):
    failures = []
    for service in STORES:
        if services[service]["was_running"]:
            try:
                engine.start(services[service])
            except Exception:
                failures.append(service)
    if failures:
        raise BackupError("Store restart failed; writers kept stopped for console recovery")
    for service in ("api", "worker", "web"):
        if service in services and services[service]["was_running"]:
            try:
                engine.start(services[service])
            except Exception:
                failures.append(service)
    if failures:
        raise BackupError("Writer restart failed; operator recovery required")
    engine.health(services)


def checkpoint(engine, services, stage):
    """Stage stays incomplete on any failure; originals are resumed in finally."""
    (stage / "original-state.json").write_text(json.dumps(services, indent=2) + "\n")
    os.chmod(stage / "original-state.json", 0o600)
    durable(stage / "original-state.json")
    durable(stage)
    try:
        for service in (*WRITERS, *STORES):
            if service in services and services[service]["was_running"]:
                engine.stop(services[service])
        engine.quiesced(services)
        for service in STORES:
            engine.quiesced(services)
            engine.archive(stage / (service + ".tar.gz"), services[service]["source"], ["."])
        engine.archive(stage / "deployment-and-exports.tar.gz", engine.stack,
                       [".env", "infra/docker", "data/obsidian-exports"])
        engine.quiesced(services)
    finally:
        restore(engine, services)
    engine.mount()
    manifest = {"schemaVersion": 1, "project": PROJECT, "timestamp": datetime.now(timezone.utc).isoformat(),
                "scope": "cold matched volumes and deployment/exports; not restore proof", "services": services}
    (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    checksums = []
    for file in sorted(stage.iterdir()):
        if file.is_file():
            os.chmod(file, 0o600)
            durable(file)
            digest = hashlib.sha256()
            with file.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            checksums.append(f"{digest.hexdigest()}  {file.name}\n")
    (stage / "SHA256SUMS").write_text("".join(checksums))
    os.chmod(stage / "SHA256SUMS", 0o600)
    durable(stage / "SHA256SUMS")
    # Re-read before marking the generation complete.
    for line in checksums:
        expected, name = line.strip().split("  ", 1)
        digest = hashlib.sha256()
        with (stage / name).open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            raise BackupError("Checkpoint checksum verification failed")
    engine.mount()
    (stage / "COMPLETE").write_text("validated cold checkpoint; production resume passed\n")
    os.chmod(stage / "COMPLETE", 0o600)
    durable(stage / "COMPLETE")
    durable(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--target", default="/mnt/omv/docker-host-backups")
    parser.add_argument("--stack", default="/opt/stacks/household-hub")
    args = parser.parse_args()
    engine = Engine(args.target, args.stack)
    if not args.execute:
        services = engine.discover()
        print(json.dumps({"mode": "read-only preflight", "services": sorted(services),
                          "running": sorted(k for k, v in services.items() if v["was_running"])}))
        return
    if os.geteuid() != 0:
        raise BackupError("Execution requires root and an approved maintenance window")
    os.umask(0o077)
    with open("/run/lock/household-hub-coordinated-backup.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BackupError("Another coordinated checkpoint holds the lock") from exc
        services = engine.discover()
        parent = engine.target / "household-hub-coordinated"
        if parent.is_symlink():
            raise BackupError("Checkpoint directory must not be symlinked")
        parent.mkdir(mode=0o700, exist_ok=True)
        os.chmod(parent, 0o700)
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stage = parent / (".pending-" + name)
        stage.mkdir(mode=0o700)
        os.chmod(stage, 0o700)
        checkpoint(engine, services, stage)
        destination = parent / name
        if destination.exists():
            raise BackupError("Checkpoint generation already exists")
        stage.rename(destination)
        durable(parent)
        print("Complete coordinated checkpoint; originals resumed. No retention deletion.")


if __name__ == "__main__":
    def interrupted(signum, frame):
        raise BackupError("Checkpoint interrupted; attempting original-container resume")
    for event in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(event, interrupted)
    try:
        main()
    except Exception as exc:
        category = str(exc) if isinstance(exc, BackupError) else "Unexpected failure"
        print(f"{category}. Inspect protected staging and original service state.", flush=True)
        raise SystemExit(1)
