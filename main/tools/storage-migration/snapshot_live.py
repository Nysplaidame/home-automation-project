"""Frozen inode/metadata baseline for already-accepted Media data.

Not a copy proof or content backup. Used only after initial Z full verification
and activation, to prove Y's no-overwrite merge preserves existing Media inodes.
"""
import json
import os
from pathlib import Path
import stat

import verify_copy


def snapshot(root, report):
    report = Path(report).resolve()
    if report.exists() or root.path == report or root.path in report.parents:
        raise ValueError("New external evidence path required")
    counts = {"checked": 0, "issues": 0}
    with report.open("x", encoding="utf-8") as output:
        def emit(row):
            output.write(json.dumps(row, ensure_ascii=True) + "\n")
            counts["issues"] += row["status"] == "issue"
        emit({"status": "start", "schema": 2, "layout": "identity-baseline", "uuid": root.uuid,
              "source": str(root.path), "target": str(root.path),
              "source_exclude_top": [".household-migration"],
              "warning": "Quiesced published-data identity baseline; not a copy or hash proof"})
        def visit(path):
            try:
                if path == ".":
                    value = os.fstat(root.fd)
                    attrs = verify_copy.attributes(root.fd, None)
                else:
                    with root.parent(path) as (fd, name):
                        value = os.stat(name, dir_fd=fd, follow_symlinks=False)
                        attrs = verify_copy.attributes(fd, name)
                if value.st_dev != root.device:
                    raise ValueError("Nested filesystem")
                fingerprint = [str(v) for v in (value.st_dev, value.st_ino, value.st_size,
                                                 value.st_mtime_ns, value.st_ctime_ns)]
                row = {"status": "checked", "path": path, "kind": stat.S_IFMT(value.st_mode),
                       "metadata": verify_copy.metadata(value, attrs), "bytes": value.st_size,
                       "source_identity": [str(value.st_dev), str(value.st_ino)], "source_links": value.st_nlink,
                       "target_generation": fingerprint, "source_generation": fingerprint,
                       "allocated_bytes": {"source": value.st_blocks*512, "target": value.st_blocks*512},
                       "verification": "existing-inode"}
                if stat.S_ISDIR(value.st_mode):
                    for name in root.names(path):
                        if path == "." and name == ".household-migration":
                            continue
                        visit(name if path == "." else path + "/" + name)
                elif stat.S_ISLNK(value.st_mode):
                    with root.parent(path) as (fd, name):
                        row["link_target"] = os.readlink(name, dir_fd=fd)
                elif not (stat.S_ISREG(value.st_mode) or stat.S_ISSOCK(value.st_mode) or stat.S_ISFIFO(value.st_mode)):
                    raise ValueError("Unsupported special entry")
                if path == ".":
                    after = os.fstat(root.fd)
                else:
                    with root.parent(path) as (fd, name):
                        after = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if verify_copy.generation(after) != verify_copy.generation(value):
                    raise ValueError("Entry changed during baseline capture")
                counts["checked"] += 1
                emit(row)
            except (OSError, ValueError) as exc:
                emit({"status": "issue", "path": path, "reason": str(exc)})
        visit(".")
        emit({"status": "complete", **counts})
        output.flush(); os.fsync(output.fileno())
    return counts
