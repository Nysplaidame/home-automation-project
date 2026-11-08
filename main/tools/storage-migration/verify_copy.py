"""Linux-only, read-only comparison of a staged copy in its original layout.

Writers must be stopped externally. Evidence is never deletion authorization.
No copy, rename, repair, or delete operation is provided.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import stat


def identity(value):
    return value.st_dev, value.st_ino


def generation(value):
    return identity(value), value.st_size, value.st_mtime_ns, value.st_ctime_ns


def attributes(parent, name):
    path = f"/proc/self/fd/{parent}" + ("/" + name if name else "")
    return {key: hashlib.sha256(os.getxattr(path, key, follow_symlinks=not bool(name))).hexdigest()
            for key in os.listxattr(path, follow_symlinks=not bool(name))}


def metadata(value, attrs):
    return {"mode": stat.S_IMODE(value.st_mode), "uid": value.st_uid,
            "gid": value.st_gid, "mtime_ns": str(value.st_mtime_ns), "xattrs": attrs}


def digest(fd):
    result = hashlib.sha256()
    while True:
        chunk = os.read(fd, 4 * 1024 * 1024)
        if not chunk:
            return result.hexdigest()
        result.update(chunk)


def verify(source, target, report, source_exclude_top=()):
    if os.name != "posix" or not Path("/proc/self/fd").is_dir():
        raise ValueError("Run on Linux; descriptor-anchored metadata checks are required")
    roots = [Path(source), Path(target)]
    if any(p.is_symlink() or not p.is_dir() for p in roots):
        raise ValueError("Source and target must be existing non-symlink directories")
    roots = [p.resolve() for p in roots]
    source_exclude_top = set(source_exclude_top)
    if any(not name or "/" in name or name in {".", ".."} for name in source_exclude_top):
        raise ValueError("Exclusions must be exact top-level names")
    if roots[0] == roots[1] or any(roots[i] in roots[1-i].parents for i in (0, 1)):
        raise ValueError("Source and target must be distinct and non-nested")
    report = Path(report)
    if report.is_symlink() or report.exists():
        raise ValueError("Report must be a new file")
    report = report.resolve()
    if any(root == report or root in report.parents for root in roots):
        raise ValueError("Report must be outside both trees")
    counts = {"checked": 0, "issues": 0}
    source_links, target_links = {}, {}
    flags = os.O_RDONLY | os.O_NOFOLLOW
    with ExitStack() as stack:
        stream = stack.enter_context(report.open("x", encoding="utf-8"))
        def emit(row):
            stream.write(json.dumps(row, ensure_ascii=True) + "\n")
            if row["status"] == "issue":
                counts["issues"] += 1
        emit({"status": "start", "schema": 2, "source": str(roots[0]), "target": str(roots[1]),
              "source_exclude_top": sorted(source_exclude_top),
              "warning": "Requires externally stopped writers; does not authorize deletion"})
        fds = []
        for root in roots:
            fd = os.open(root, flags | os.O_DIRECTORY)
            stack.callback(os.close, fd)
            fds.append(fd)
        devices = [os.fstat(fd).st_dev for fd in fds]

        def compare(parents, names, relative):
            opened = []
            try:
                before = [os.stat(name, dir_fd=fd, follow_symlinks=False) if name
                          else os.fstat(fd) for fd, name in zip(parents, names)]
                if any(value.st_dev != devices[i] for i, value in enumerate(before)):
                    raise ValueError("Nested filesystem encountered")
                kinds = [stat.S_IFMT(value.st_mode) for value in before]
                if kinds[0] != kinds[1]:
                    raise ValueError("Entry types differ")
                attrs = [attributes(fd, name) for fd, name in zip(parents, names)]
                metas = [metadata(value, attr) for value, attr in zip(before, attrs)]
                if metas[0] != metas[1]:
                    emit({"status": "issue", "path": relative, "reason": "metadata differs",
                          "source": metas[0], "target": metas[1]})
                def fingerprint(value):
                    return [str(v) for v in (value.st_dev, value.st_ino, value.st_size,
                                              value.st_mtime_ns, value.st_ctime_ns)]
                row = {"status": "checked", "path": relative, "metadata": metas[0],
                       "kind": kinds[0], "source_identity": [str(before[0].st_dev), str(before[0].st_ino)],
                       "source_links": before[0].st_nlink,
                       "source_generation": fingerprint(before[0]), "target_generation": fingerprint(before[1])}
                if stat.S_ISLNK(before[0].st_mode):
                    links = [os.readlink(name, dir_fd=fd) for fd, name in zip(parents, names)]
                    if links[0] != links[1]:
                        raise ValueError("Symlink targets differ")
                    row["link_target"] = links[0]
                elif stat.S_ISREG(before[0].st_mode) or stat.S_ISDIR(before[0].st_mode):
                    for i, (parent, name) in enumerate(zip(parents, names)):
                        fd = os.open(name, flags | (os.O_DIRECTORY if stat.S_ISDIR(before[0].st_mode) else 0),
                                     dir_fd=parent) if name else os.dup(parent)
                        opened.append(fd)
                        if generation(os.fstat(fd)) != generation(before[i]):
                            raise ValueError("Entry changed before opening")
                    if stat.S_ISDIR(before[0].st_mode):
                        sets = [set(os.listdir(fd)) for fd in opened]
                        if relative == ".":
                            sets[0] -= source_exclude_top
                        for name in sorted(sets[0] - sets[1]):
                            emit({"status": "issue", "path": relative + "/" + name,
                                  "reason": "missing destination entry"})
                        for name in sorted(sets[1] - sets[0]):
                            emit({"status": "issue", "path": relative + "/" + name,
                                  "reason": "unexpected destination entry"})
                        for name in sorted(sets[0] & sets[1]):
                            compare(opened, [name, name], relative + "/" + name)
                    else:
                        if before[0].st_size != before[1].st_size:
                            raise ValueError("File sizes differ")
                        hashes = [digest(fd) for fd in opened]
                        if hashes[0] != hashes[1]:
                            raise ValueError("SHA256 differs")
                        row["sha256"] = hashes[0]
                        row["bytes"] = before[0].st_size
                        allocated = [value.st_blocks * 512 for value in before]
                        row["allocated_bytes"] = {"source": allocated[0], "target": allocated[1]}
                        if allocated[0] * 2 < before[0].st_size and allocated[1] >= before[1].st_size:
                            raise ValueError("Sparse file became fully allocated")
                        a, b = [identity(value) for value in before]
                        if before[0].st_nlink > 1:
                            previous = source_links.setdefault(a, b)
                            if previous != b:
                                raise ValueError("Source hardlink group was split")
                        if before[1].st_nlink > 1:
                            previous = target_links.setdefault(b, a)
                            if previous != a:
                                raise ValueError("Independent source files became hardlinked")
                elif stat.S_ISSOCK(before[0].st_mode) or stat.S_ISFIFO(before[0].st_mode):
                    row["special_type"] = "socket" if stat.S_ISSOCK(before[0].st_mode) else "fifo"
                else:
                    raise ValueError("Unsupported special entry requires review")
                after = [os.stat(name, dir_fd=fd, follow_symlinks=False) if name
                         else os.fstat(fd) for fd, name in zip(parents, names)]
                if any(generation(x) != generation(y) for x, y in zip(before, after)):
                    raise ValueError("Entry changed during comparison")
                if opened and any(generation(os.fstat(fd)) != generation(before[i])
                                  for i, fd in enumerate(opened)):
                    raise ValueError("Opened entry changed during comparison")
                counts["checked"] += 1
                emit(row)
            except (OSError, ValueError) as exc:
                emit({"status": "issue", "path": relative, "reason": str(exc)})
            finally:
                for fd in opened:
                    os.close(fd)
        compare(fds, [None, None], ".")
        emit({"status": "complete", **counts,
              "warning": "Comparison only; no automatic cleanup authorization"})
        stream.flush()
        os.fsync(stream.fileno())
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--source-exclude-top", action="append", default=[],
                        help="Exact source-only top-level name; destination extras still fail")
    parser.add_argument("--writers-stopped", action="store_true",
                        help="Attest that external writers have been stopped; tool cannot enforce this")
    args = parser.parse_args()
    if not args.writers_stopped:
        parser.error("Stop external writers before final verification")
    result = verify(args.source, args.target, args.report, args.source_exclude_top)
    print(json.dumps(result))
    return 2 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
