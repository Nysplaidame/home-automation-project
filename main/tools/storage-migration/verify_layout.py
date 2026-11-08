"""Verify the final Media namespace against complete staged-copy receipts.

Uses disk-backed indexing, full SHA256 and metadata comparison. No deletion.
The original source disks are not required to remain mounted for this check.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

import migration_ops as ops
from plan_layout import destination
import verify_copy

MERGES = {"backups", "_codex_diagnostics",
          "_codex_diagnostics/actual-necrons-20261001-215428",
          "_codex_diagnostics/focused-20261001-213336",
          "_codex_diagnostics/sevenzip-20261001-213911"}


def mapped_path(volume, path, identity_layout=False):
    if path == ".":
        return "." if volume == "Z" else None
    name = path.removeprefix("./")
    ops.relative(name)
    if identity_layout:
        if volume != "Z":
            raise ValueError("Only published Z may use identity-baseline layout")
        return name
    mapped = destination(volume, name)
    if mapped is None:
        return None
    if mapped[0] != "Z":
        raise ValueError("Unexpected Print data in non-Print copy receipt")
    return mapped[1]


def verify(root, receipts, database, report, sealed_quarantines=()):
    database, report = Path(database).resolve(), Path(report).resolve()
    if database.exists() or report.exists() or any(
            root.path == p or root.path in p.parents for p in (database, report)):
        raise ValueError("Evidence paths must be new and outside the destination")
    db = sqlite3.connect(database)
    try:
        db.executescript("""
        CREATE TABLE expected (path TEXT PRIMARY KEY, folded TEXT UNIQUE, volume TEXT,
                               evidence TEXT, seen INTEGER DEFAULT 0);
        CREATE TABLE links (direction TEXT, key TEXT, value TEXT, PRIMARY KEY(direction,key));
        """)
        for volume, receipt in receipts:
            header, end, count, issues = None, None, 0, 0
            identity_layout = False
            with Path(receipt).open(encoding="utf-8") as stream:
                for line in stream:
                    row = json.loads(line)
                    if header is None:
                        header = row
                        identity_layout = header.get("layout") == "identity-baseline"
                        excluded = [".household-migration"] if identity_layout else (["Print"] if volume == "Y" else [])
                        if (header.get("status") != "start" or header.get("schema") != 2 or
                                header.get("source_exclude_top") != excluded or
                                (identity_layout and (volume != "Z" or header.get("uuid") != root.uuid))):
                            raise ValueError("Unsupported or incorrectly scoped receipt")
                    if end:
                        raise ValueError("Receipt data follows completion")
                    if row["status"] == "issue":
                        issues += 1
                    if row["status"] == "complete":
                        end = row
                    if row["status"] != "checked":
                        continue
                    count += 1
                    path = mapped_path(volume, row["path"], identity_layout)
                    if path is None:
                        continue
                    old = db.execute("SELECT path,volume,evidence FROM expected WHERE folded=?", (path.casefold(),)).fetchone()
                    if old:
                        previous = json.loads(old[2])
                        if (old[0] != path or old[1] == volume or path not in MERGES or
                                row["kind"] != stat.S_IFDIR or previous["kind"] != stat.S_IFDIR):
                            raise ValueError("Unapproved final namespace collision: " + path)
                        if volume == "Y":
                            db.execute("UPDATE expected SET volume=?,evidence=? WHERE path=?", (volume, json.dumps(row), path))
                    else:
                        db.execute("INSERT INTO expected(path,folded,volume,evidence) VALUES (?,?,?,?)",
                                   (path, path.casefold(), volume, json.dumps(row)))
                    if count % 10000 == 0:
                        db.commit()
            if not end or end.get("issues") != 0 or issues or end.get("checked") != count or not count:
                raise ValueError("Incomplete or failed staged-copy receipt")
        db.commit()
        counts = {"checked": 0, "issues": 0}
        def empty_tree(path):
            if path in sealed_quarantines:
                return True  # Session validated its complete inode/generation seal.
            with root.directory(path) as fd:
                for name in os.listdir(fd):
                    info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                    if not stat.S_ISDIR(info.st_mode) or info.st_dev != root.device:
                        return False
                    if not empty_tree(path + "/" + name):
                        return False
            return True
        with report.open("x", encoding="utf-8") as output:
            def emit(row):
                output.write(json.dumps(row, ensure_ascii=True) + "\n")
                counts["issues"] += row["status"] == "issue"
            emit({"status": "start", "root": str(root.path), "uuid": root.uuid,
                  "receipts": [(v, str(p)) for v, p in receipts]})
            def visit(path):
                fd = None
                try:
                    info = os.fstat(root.fd) if path == "." else None
                    if path != ".":
                        with root.parent(path) as (parent, name):
                            info = os.stat(name, dir_fd=parent, follow_symlinks=False)
                    if info.st_dev != root.device:
                        raise ValueError("Nested filesystem")
                    expected = db.execute("SELECT volume,evidence FROM expected WHERE path=?", (path,)).fetchone()
                    if not expected:
                        if path in {".household-migration", "lost+found"} and stat.S_ISDIR(info.st_mode) and empty_tree(path):
                            emit({"status": "empty-system-directory", "path": path}); return
                        raise ValueError("Unexpected destination entry")
                    volume, encoded = expected
                    wanted = json.loads(encoded)
                    db.execute("UPDATE expected SET seen=1 WHERE path=?", (path,))
                    if stat.S_IFMT(info.st_mode) != wanted["kind"]:
                        raise ValueError("Entry type differs")
                    if path == ".":
                        parent, name = root.fd, None
                        attrs = verify_copy.attributes(parent, name)
                    else:
                        with root.parent(path) as (parent, name):
                            attrs = verify_copy.attributes(parent, name)
                    if verify_copy.metadata(info, attrs) != wanted["metadata"]:
                        raise ValueError("Final metadata differs")
                    if stat.S_ISDIR(info.st_mode):
                        for name in root.names(path):
                            visit(name if path == "." else path + "/" + name)
                    elif stat.S_ISREG(info.st_mode):
                        with root.parent(path) as (parent, name):
                            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
                        if verify_copy.generation(os.fstat(fd)) != verify_copy.generation(info):
                            raise ValueError("Entry changed before hashing")
                        if wanted.get("verification") == "existing-inode":
                            actual = [str(v) for v in (info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)]
                            if actual != wanted["target_generation"][1:]:
                                raise ValueError("Previously accepted Media inode changed during merge")
                        elif info.st_size != wanted["bytes"] or verify_copy.digest(fd) != wanted["sha256"]:
                            raise ValueError("Final size or SHA256 differs")
                        if info.st_blocks * 512 >= info.st_size and wanted["allocated_bytes"]["source"] * 2 < info.st_size:
                            raise ValueError("Sparse file became fully allocated")
                        source_key = json.dumps([volume, wanted["source_identity"]])
                        target_key = json.dumps([str(info.st_dev), str(info.st_ino)])
                        pairs = []
                        if wanted["source_links"] > 1:
                            pairs.append(("source", source_key, target_key))
                        if info.st_nlink > 1:
                            pairs.append(("target", target_key, source_key))
                        for direction, key, value in pairs:
                            previous = db.execute("SELECT value FROM links WHERE direction=? AND key=?", (direction,key)).fetchone()
                            if previous and previous[0] != value:
                                raise ValueError("Final hardlink relationship differs")
                            db.execute("INSERT OR IGNORE INTO links VALUES (?,?,?)", (direction,key,value))
                        if verify_copy.generation(os.fstat(fd)) != verify_copy.generation(info):
                            raise ValueError("Entry changed during hashing")
                    elif stat.S_ISLNK(info.st_mode):
                        with root.parent(path) as (parent, name):
                            if os.readlink(name, dir_fd=parent) != wanted["link_target"]:
                                raise ValueError("Final symlink target differs")
                    elif not (stat.S_ISSOCK(info.st_mode) or stat.S_ISFIFO(info.st_mode)):
                        raise ValueError("Unsupported special entry")
                    if path == ".":
                        after = os.fstat(root.fd)
                    else:
                        with root.parent(path) as (parent, name):
                            after = os.stat(name, dir_fd=parent, follow_symlinks=False)
                    if verify_copy.generation(after) != verify_copy.generation(info):
                        raise ValueError("Entry changed during final verification")
                    counts["checked"] += 1
                    emit({"status": "checked", "path": path})
                except (OSError, ValueError) as exc:
                    emit({"status": "issue", "path": path, "reason": str(exc)})
                finally:
                    if fd is not None:
                        os.close(fd)
            visit(".")
            for (path,) in db.execute("SELECT path FROM expected WHERE seen=0"):
                emit({"status": "issue", "path": path, "reason": "Missing final entry"})
            emit({"status": "complete", **counts})
            output.flush(); os.fsync(output.fileno())
        db.commit()
        return counts
    finally:
        db.close()
