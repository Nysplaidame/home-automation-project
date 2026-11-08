#!/usr/bin/env python3
"""Private atomic handoff for the fixed OMV collector; no metrics shipping."""
import importlib.util
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path

COLLECTOR = Path("/usr/local/libexec/home-automation/omv-health-snapshot.py")
OUTPUT = Path("/var/lib/home-automation/omv-health")
KEYS = {"schemaVersion", "observedAt", "collector", "host", "storage", "raid", "filesystems", "services", "scope"}


def encode_snapshot(snapshot, now=None):
    if not isinstance(snapshot, dict) or set(snapshot) != KEYS or snapshot.get("schemaVersion") != "omv-health/1.0":
        raise ValueError("Unsupported snapshot contract")
    stamp = datetime.fromisoformat(snapshot["observedAt"])
    current = now or datetime.now(timezone.utc)
    if stamp.tzinfo is None or not -30 <= (current - stamp).total_seconds() <= 300:
        raise ValueError("Snapshot time is ambiguous, future or stale")
    data = (json.dumps(snapshot, allow_nan=False, separators=(",", ":")) + "\n").encode()
    if len(data) > 512 * 1024:
        raise ValueError("Snapshot exceeds handoff limit")
    return data


def owned_directory(directory, uid):
    # Check every ancestor without resolving away symlinks. Parent ownership is
    # the boundary against replacing entries while the root producer is active.
    for item in (directory, *directory.parents):
        info = item.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != uid or info.st_mode & 0o022:
            raise ValueError("Handoff directory ancestry is unsafe")


def publish_snapshot(snapshot, directory, gid, required_uid=None):
    import fcntl
    uid = os.getuid() if required_uid is None else required_uid
    directory = Path(os.path.abspath(directory))
    # Atomic writes are not allowed to invent a new directory or widen its ACL.
    # In tests, a private fixture below /tmp is used with a bounded trust root.
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != uid or info.st_mode & 0o022:
        raise ValueError("Handoff directory is unsafe")
    data = encode_snapshot(snapshot)
    destination = directory / "snapshot.json"
    lock_fd = os.open(directory / ".publish.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    temporary = None
    try:
        lock_info = os.fstat(lock_fd)
        if not stat.S_ISREG(lock_info.st_mode) or lock_info.st_uid != uid or lock_info.st_nlink != 1 or lock_info.st_mode & 0o077:
            raise ValueError("Handoff lock is unsafe")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if destination.exists() or destination.is_symlink():
            previous = destination.lstat()
            if not stat.S_ISREG(previous.st_mode) or previous.st_uid != uid or previous.st_nlink != 1:
                raise ValueError("Existing snapshot is unsafe")
        fd, name = tempfile.mkstemp(prefix=".snapshot-", dir=directory)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
            # Readers cannot open the temporary file before its payload is complete.
            os.fchown(output.fileno(), uid, gid)
            os.fchmod(output.fileno(), 0o640)
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        temporary = None
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        os.close(lock_fd)


def main():
    if os.name != "posix" or os.geteuid() != 0:
        raise ValueError("Producer requires the reviewed Linux root service")
    import grp
    gid = grp.getgrnam("omv-metrics").gr_gid
    owned_directory(OUTPUT, 0)
    owned_directory(COLLECTOR.parent, 0)
    source = COLLECTOR.lstat()
    if not stat.S_ISREG(source.st_mode) or source.st_uid != 0 or source.st_nlink != 1 or source.st_mode & 0o022:
        raise ValueError("Collector source is not immutable root-owned code")
    spec = importlib.util.spec_from_file_location("omv_health_collector", COLLECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    publish_snapshot(module.snapshot(), OUTPUT, gid, required_uid=0)
    print("OMV snapshot published; no metrics shipped")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # No payload, paths from exceptions or underlying command output.
        print("OMV snapshot publication failed (" + type(error).__name__ + "); inspect service state", flush=True)
        raise SystemExit(1)
