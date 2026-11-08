"""Seal and validate retained staging-only extras; never deletes data."""
import json
import os
from pathlib import Path
import stat

import migration_ops as ops


def nodes(root, start):
    pending = [start]
    while pending:
        path = pending.pop()
        with root.parent(path) as (fd, name):
            value = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if value.st_dev != root.device:
            raise ValueError("Nested filesystem in quarantine")
        yield {"path": path, "kind": stat.S_IFMT(value.st_mode),
               "generation": [str(v) for v in (value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)]}
        if stat.S_ISDIR(value.st_mode):
            pending += [path + "/" + name for name in root.names(path)]


def seal(root, prefix, report):
    count = 0
    with Path(report).open("x", encoding="utf-8") as output:
        output.write(json.dumps({"status": "start", "prefix": prefix, "uuid": root.uuid}) + "\n")
        for row in nodes(root, prefix):
            output.write(json.dumps(row, ensure_ascii=True) + "\n"); count += 1
        output.write(json.dumps({"status": "complete", "entries": count}) + "\n")
        output.flush(); os.fsync(output.fileno())
    return {"prefix": prefix, "report": str(report), "sha256": ops.hash_file(report), "entries": count}


def validate(root, record, session_prefix):
    prefix = record["prefix"]
    if not prefix.startswith(session_prefix + "/quarantine-") or ops.hash_file(record["report"]) != record["sha256"]:
        raise ValueError("Wrong or changed quarantine evidence")
    expected, end = {}, None
    with open(record["report"], encoding="utf-8") as stream:
        first = json.loads(next(stream))
        if first != {"status": "start", "prefix": prefix, "uuid": root.uuid}:
            raise ValueError("Quarantine mount identity mismatch")
        for line in stream:
            row = json.loads(line)
            if end:
                raise ValueError("Data after quarantine completion")
            if row.get("status") == "complete":
                end = row; continue
            if row["path"] in expected:
                raise ValueError("Duplicate quarantine entry")
            expected[row["path"]] = row
    if not end or end["entries"] != len(expected) or record["entries"] != len(expected):
        raise ValueError("Incomplete quarantine evidence")
    for row in nodes(root, prefix):
        if expected.pop(row["path"], None) != row:
            raise ValueError("Quarantined entry changed")
    if expected:
        raise ValueError("Quarantined entry disappeared")
    return prefix
