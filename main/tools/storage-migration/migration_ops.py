"""Guarded staging and journaled same-filesystem moves. No disk formatting.

Production callers must supply the exact filesystem UUID; None is reserved for
temporary test fixtures. Original source files are never deleted by this module.
"""
import ctypes
import errno
try:
    import fcntl
except ImportError:
    fcntl = None
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
from contextlib import contextmanager


def relative(value):
    if not isinstance(value, str) or value.startswith("/") or any(
            part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError("Unsafe relative path")
    return value


def synced_json(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=True, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class Root:
    def __init__(self, path, uuid):
        if os.name != "posix":
            raise ValueError("Run on Linux")
        raw = Path(path)
        if raw.is_symlink() or not raw.is_dir():
            raise ValueError("Root must be an existing non-symlink directory")
        self.path = raw.resolve()
        self.uuid = uuid
        if uuid is not None:
            found = subprocess.run(
                ["findmnt", "-J", "--mountpoint", str(self.path), "-o", "TARGET,UUID,FSTYPE"],
                check=True, capture_output=True, text=True)
            mounts = json.loads(found.stdout)["filesystems"]
            if len(mounts) != 1 or mounts[0].get("uuid") != uuid or mounts[0].get("fstype") != "ext4":
                raise ValueError("Wrong UUID, filesystem or missing exact mount")
        self.fd = os.open(self.path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        self.device = os.fstat(self.fd).st_dev
        self.inode = os.fstat(self.fd).st_ino

    def close(self):
        os.close(self.fd)

    @contextmanager
    def parent(self, path):
        parts = PurePosixPath(relative(path)).parts
        fd = os.dup(self.fd)
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = next_fd
                if os.fstat(fd).st_dev != self.device:
                    raise ValueError("Nested filesystem")
            yield fd, parts[-1]
        finally:
            os.close(fd)

    def info(self, path):
        if path == ".":
            return {"inode": str(self.inode), "kind": stat.S_IFDIR}
        try:
            with self.parent(path) as (parent, name):
                value = os.stat(name, dir_fd=parent, follow_symlinks=False)
                if value.st_dev != self.device:
                    raise ValueError("Nested filesystem")
                return {"inode": str(value.st_ino), "kind": stat.S_IFMT(value.st_mode)}
        except FileNotFoundError:
            return None

    @contextmanager
    def directory(self, path):
        if path == ".":
            fd = os.dup(self.fd)
        else:
            with self.parent(path) as (parent, name):
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            if os.fstat(fd).st_dev != self.device:
                raise ValueError("Nested filesystem")
            yield fd
        finally:
            os.close(fd)

    def names(self, path):
        with self.directory(path) as fd:
            return sorted(os.listdir(fd))

    def meta(self, path):
        with self.directory(path) as fd:
            value = os.fstat(fd)
            return {"mode": stat.S_IMODE(value.st_mode), "uid": value.st_uid, "gid": value.st_gid,
                    "mtime_ns": str(value.st_mtime_ns),
                    "xattrs": {name: os.getxattr(fd, name).hex() for name in os.listxattr(fd)}}

    def set_meta(self, path, value):
        with self.directory(path) as fd:
            current = os.fstat(fd)
            os.fchown(fd, value["uid"], value["gid"])
            os.fchmod(fd, value["mode"])
            for name in os.listxattr(fd):
                if name not in value["xattrs"]:
                    os.removexattr(fd, name)
            for name, encoded in value["xattrs"].items():
                os.setxattr(fd, name, bytes.fromhex(encoded))
            os.utime(fd, ns=(current.st_atime_ns, int(value["mtime_ns"])))
            os.fsync(fd)
        if self.meta(path) != value:
            raise ValueError("Directory metadata restoration failed")

    def rename(self, source, target):
        with self.parent(source) as (a, src), self.parent(target) as (b, dst):
            if any(name.casefold() == dst.casefold() for name in os.listdir(b)):
                raise FileExistsError("Destination or case alias appeared")
            libc = ctypes.CDLL(None, use_errno=True)
            function = getattr(libc, "renameat2", None)
            if function is None:
                raise RuntimeError("Atomic no-replace renameat2 is required")
            function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            function.restype = ctypes.c_int
            if function(a, os.fsencode(src), b, os.fsencode(dst), 1):
                code = ctypes.get_errno()
                raise OSError(code, os.strerror(code))
            os.fsync(a)
            os.fsync(b)


def hash_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def receipt(path, expected_target):
    """Accept only a complete zero-issue verifier report for this exact tree."""
    first = last = None
    count = 0
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if first is None:
                first = row
            if last and last.get("status") == "complete":
                raise ValueError("Data after receipt completion")
            if row.get("status") == "issue":
                raise ValueError("Verification issues remain")
            count += row.get("status") == "checked"
            last = row
    if (not first or first.get("status") != "start" or first.get("schema") != 2 or
            Path(first.get("target", "")).resolve() != Path(expected_target).resolve() or
            not last or last.get("status") != "complete" or last.get("issues") != 0 or
            last.get("checked") != count or not count):
        raise ValueError("Incomplete or wrong-target verification receipt")
    return {"path": str(Path(path).resolve()), "sha256": hash_file(path)}


def prepare(root, state, moves, metadata=None, verified_report=None, evidence_target=None):
    """Seal a move plan before applying it; snapshot existing touched parents."""
    state = Path(state).resolve()
    if root.path == state or root.path in state.parents or state.exists():
        raise ValueError("State must be new and outside the data root")
    actions, parents, parent_identities, parent_children = [], {}, {}, {}
    virtual_sources = set()
    targets = set()
    for source, target in moves:
        relative(source); relative(target)
        if source == target or source.startswith(target + "/") or target.startswith(source + "/"):
            raise ValueError("Overlapping rename paths")
        source_info = root.info(source)
        if not source_info or root.info(target) is not None:
            raise ValueError("Missing source or occupied destination")
        if source in virtual_sources:
            raise ValueError("Source used twice")
        if target.casefold() in targets:
            raise ValueError("Destination used twice")
        virtual_sources.add(source)
        targets.add(target.casefold())
        actions.append({"kind": "rename", "source": source, "target": target, "identity": source_info})
        for path in (str(PurePosixPath(source).parent), str(PurePosixPath(target).parent)):
            if path not in parents:
                parents[path] = root.meta(path)
                parent_identities[path] = root.info(path)
                parent_children[path] = root.names(path)
    for path, desired in (metadata or {}).items():
        identity = {"inode": str(root.inode), "kind": stat.S_IFDIR} if path == "." else root.info(path)
        original = path
        if identity is None:
            incoming = [a for a in actions if a["kind"] == "rename" and a["target"] == path]
            if len(incoming) == 1:
                identity = incoming[0]["identity"]
                original = incoming[0]["source"]
        if not identity or identity["kind"] != stat.S_IFDIR:
            raise ValueError("Metadata target is not an existing directory")
        actions.append({"kind": "metadata", "path": path, "identity": identity,
                        "before": root.meta(original), "desired": desired})
    evidence = receipt(verified_report, evidence_target) if verified_report else None
    state.mkdir(mode=0o700)
    config = {"root": str(root.path), "uuid": root.uuid, "root_inode": str(root.inode),
              "actions": actions, "parents": parents, "parent_identities": parent_identities,
              "parent_children": parent_children, "receipt": evidence}
    synced_json(state / "plan.json", config)
    return config


def events(path):
    if not path.exists():
        return []
    # A torn final record may be discarded: the preceding durable intent is
    # enough to recover whether an atomic rename happened.
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    result, length = [], 0
    for index, line in enumerate(lines):
        try:
            row = json.loads(line)
        except (ValueError, UnicodeError):
            if index != len(lines) - 1 or line.endswith(b"\n"):
                raise ValueError("Corrupt journal")
            with path.open("r+b") as stream:
                stream.truncate(length); stream.flush(); os.fsync(stream.fileno())
            break
        if not line.endswith(b"\n"):
            # Complete JSON without newline was not a completed journal write.
            with path.open("r+b") as stream:
                stream.truncate(length); stream.flush(); os.fsync(stream.fileno())
            break
        result.append(row)
        length += len(line)
    return result


def append_event(path, row):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")
        stream.flush(); os.fsync(stream.fileno())
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def apply(root, state, reverse=False, interrupt_after=None):
    state = Path(state).resolve()
    lock = os.open(state / "lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        plan = json.loads((state / "plan.json").read_text())
        if (plan["root"] != str(root.path) or plan["uuid"] != root.uuid or
                plan["root_inode"] != str(root.inode)):
            raise ValueError("Plan root identity differs")
        log = state / "journal.jsonl"
        history = events(log)
        if any(row["event"] in {"activated", "wrapper-removed"} for row in history):
            raise ValueError("Activation/cleanup closes automatic namespace rollback")
        if any(row["event"] == "rollback-start" for row in history) and not reverse:
            raise ValueError("Rollback already started")
        if reverse and not any(row["event"] == "rollback-start" for row in history):
            append_event(log, {"event": "rollback-start"})
        # A crash may have happened between rename and its completion record.
        eligible = {row["index"] for row in history if row["event"] == "intent"}
        indexes = range(len(plan["actions"]) - 1, -1, -1) if reverse else range(len(plan["actions"]))
        for index in indexes:
            action = plan["actions"][index]
            if reverse and index not in eligible:
                continue
            completed_event = "undone" if reverse else "done"
            if any(row["event"] == completed_event and row.get("index") == index for row in history):
                continue
            append_event(log, {"event": "undo-intent" if reverse else "intent", "index": index})
            if action["kind"] == "rename":
                source, target = action["source"], action["target"]
                if reverse:
                    source, target = target, source
                a, b = root.info(source), root.info(target)
                if a == action["identity"] and b is None:
                    root.rename(source, target)
                elif a is None and b == action["identity"]:
                    pass
                else:
                    raise ValueError("Ambiguous rename state; refusing replacement or data loss")
            else:
                path = action["path"]
                actual = {"inode": str(root.inode), "kind": stat.S_IFDIR} if path == "." else root.info(path)
                if actual != action["identity"]:
                    raise ValueError("Metadata directory identity changed")
                root.set_meta(path, action["before"] if reverse else action["desired"])
            if interrupt_after == index:
                raise RuntimeError("Injected interruption after mutation, before receipt")
            row = {"event": completed_event, "index": index}
            append_event(log, row); history.append(row)
        if reverse:
            # Renames change parent mtimes. Restore the pre-plan parent state
            # only after all inverse renames finish.
            for path, value in plan["parents"].items():
                root.set_meta(path, value)
        append_event(log, {"event": "rolled-back" if reverse else "complete"})
    finally:
        os.close(lock)


def remove_empty_wrapper(root, state, wrapper):
    """Only after every recorded rename completed and destinations retain identity."""
    relative(wrapper)
    state = Path(state).resolve()
    lock = os.open(state / "lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _remove_empty_wrapper(root, state, wrapper)
    finally:
        os.close(lock)


def _remove_empty_wrapper(root, state, wrapper):
    plan = json.loads((state / "plan.json").read_text())
    if (plan["root"] != str(root.path) or plan["uuid"] != root.uuid or
            plan["root_inode"] != str(root.inode)):
        raise ValueError("Wrong wrapper root")
    history = events(state / "journal.jsonl")
    if not any(row["event"] == "complete" for row in history) or any(
            row["event"] in {"rollback-start", "activated"} for row in history):
        raise ValueError("Completed unactivated move receipts required")
    actions = [a for a in plan["actions"] if a["kind"] == "rename"]
    if not actions or any(not a["source"].startswith(wrapper + "/") for a in actions):
        raise ValueError("Plan does not move exactly this wrapper's children")
    direct = {a["source"][len(wrapper)+1:] for a in actions
              if "/" not in a["source"][len(wrapper)+1:]}
    if direct != set(plan["parent_children"].get(wrapper, [])):
        raise ValueError("Plan did not cover all original wrapper children")
    for action in actions:
        if (root.info(action["source"]) is not None or
                root.info(action["target"]) != action["identity"]):
            raise ValueError("Moved entry reconciliation failed")
    current = root.info(wrapper)
    prior_intent = any(row["event"] == "wrapper-intent" and row.get("path") == wrapper for row in history)
    if current is None:
        if not prior_intent:
            raise ValueError("Wrapper disappeared without a journaled removal")
        append_event(state / "journal.jsonl", {"event": "wrapper-removed", "path": wrapper})
        return
    if current != plan["parent_identities"].get(wrapper):
        raise ValueError("Wrapper identity changed")
    if root.names(wrapper):
        raise ValueError("Wrapper is not empty")
    append_event(state / "journal.jsonl", {"event": "wrapper-intent", "path": wrapper})
    with root.parent(wrapper) as (fd, name):
        os.rmdir(name, dir_fd=fd)  # Never recursive; any late entry blocks it.
        os.fsync(fd)
    append_event(state / "journal.jsonl", {"event": "wrapper-removed", "path": wrapper})


def copy_command(source, target, exclude_print=False, execute=False, checksum=False):
    command = ["rsync", "-aHAXSx", "--numeric-ids", "--protect-args", "--modify-window=-1",
               "--partial", "--stats", "--fsync"]
    if checksum:
        command.append("--checksum")
    if not execute:
        command.append("--dry-run")
    if exclude_print:
        command += ["--exclude=/Print/"]
    return command + ["--", str(source) + "/", str(target) + "/"]
