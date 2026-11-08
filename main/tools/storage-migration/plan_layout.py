"""Read-only Print/Media layout inventory; never copies, renames or deletes.

Write the SQLite evidence outside the source trees and outside the repository.
This is a planning snapshot, NOT deletion authority or a verified copy manifest.
"""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat


def destination(volume, relative):
    parts = PurePosixPath(relative).parts
    if volume not in {"Y", "Z"} or not parts or relative.startswith("/"):
        raise ValueError("Expected Y/Z and a nonempty relative path")
    if any(p in {"", ".", ".."} for p in relative.split("/")):
        raise ValueError("Unsafe path component")
    if volume == "Y":
        if parts[0] == "Print":
            return None if len(parts) == 1 else ("Y", "/".join(parts[1:]))
        return "Z", relative
    if parts[0] != "Media":
        return "Z", relative
    if len(parts) == 1:
        return None
    if parts[1:3] == ("books", "calibre-library"):
        return "Z", "/".join(parts[2:])
    return "Z", "/".join(parts[1:])


def file_kind(mode):
    for check, name in [
        (stat.S_ISREG, "file"), (stat.S_ISDIR, "directory"),
        (stat.S_ISLNK, "symlink"), (stat.S_ISSOCK, "socket"),
        (stat.S_ISFIFO, "fifo"), (stat.S_ISCHR, "character"),
        (stat.S_ISBLK, "block"),
    ]:
        if check(mode):
            return name
    return "unknown"


def roots_and_output(y_root, z_root, output):
    roots = {}
    for label, raw in (("Y", y_root), ("Z", z_root)):
        p = Path(raw)
        if p.is_symlink() or not p.is_dir():
            raise ValueError(f"{label} must be an existing non-symlink directory")
        roots[label] = p.resolve()
    if (roots["Y"] == roots["Z"] or roots["Y"] in roots["Z"].parents
            or roots["Z"] in roots["Y"].parents):
        raise ValueError("Source roots must be distinct and non-nested")
    output = Path(output)
    if output.is_symlink() or output.exists():
        raise ValueError("Output must be a new file; existing evidence is never overwritten")
    output = output.resolve()
    if not output.parent.is_dir():
        raise ValueError("Output parent must already exist")
    if any(root == output or root in output.parents for root in roots.values()):
        raise ValueError("Evidence output must be outside both source roots")
    for label, wrapper in (("Y", "Print"), ("Z", "Media")):
        p = roots[label] / wrapper
        if p.is_symlink() or not p.is_dir():
            raise ValueError(f"Missing or symlinked {label}/{wrapper} wrapper")
    calibre = roots["Z"] / "Media" / "books" / "calibre-library"
    if calibre.is_symlink() or not calibre.is_dir():
        raise ValueError("Missing or symlinked Calibre source library")
    return roots, output


def inventory(y_root, z_root, output):
    roots, output = roots_and_output(y_root, z_root, output)
    # Exclusive creation prevents accidental replacement of earlier evidence.
    with output.open("xb"):
        pass
    db = sqlite3.connect(output)
    try:
        db.executescript("""
        CREATE TABLE metadata (name TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE entries (
            volume TEXT, relative TEXT, target_volume TEXT, target TEXT,
            target_key TEXT, kind TEXT, bytes INTEGER, allocated_bytes INTEGER,
            device TEXT, inode TEXT, links INTEGER, mode INTEGER,
            uid INTEGER, gid INTEGER, mtime_ns TEXT, ctime_ns TEXT,
            link_target TEXT, PRIMARY KEY(volume, relative));
        CREATE INDEX destinations ON entries(target_volume, target_key);
        CREATE TABLE issues (category TEXT, volume TEXT, path TEXT, detail TEXT);
        """)
        db.execute("INSERT INTO metadata VALUES ('status','incomplete')")
        for name, root in roots.items():
            db.execute("INSERT INTO metadata VALUES (?,?)", (name, str(root)))
        db.commit()
        since_commit = 0
        for volume, root in roots.items():
            device = root.stat().st_dev
            pending = [root]
            while pending:
                directory = pending.pop()
                try:
                    with os.scandir(directory) as iterator:
                        children = list(iterator)
                except OSError as exc:
                    db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                               ("read-error", volume, str(directory), str(exc)))
                    continue
                for entry in children:
                    relative = Path(entry.path).relative_to(root).as_posix()
                    try:
                        # DirEntry.stat can report st_dev=0 on Windows.
                        info = os.stat(entry.path, follow_symlinks=False)
                        kind = file_kind(info.st_mode)
                        if info.st_dev != device:
                            db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                                       ("nested-mount", volume, relative, "Not traversed"))
                            continue
                        mapped = destination(volume, relative)
                        target_volume, target = mapped or (None, None)
                        link = os.readlink(entry.path) if kind == "symlink" else None
                        if link and (link.startswith("/") or ".." in PurePosixPath(link).parts):
                            db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                                       ("symlink-review", volume, relative, link))
                        if kind in {"unknown", "character", "block"}:
                            db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                                       ("special-review", volume, relative, kind))
                        db.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                   (volume, relative, target_volume, target,
                                    target.casefold() if target else None, kind,
                                    info.st_size, getattr(info, "st_blocks", 0) * 512,
                                    str(info.st_dev), str(info.st_ino), info.st_nlink,
                                    stat.S_IMODE(info.st_mode), info.st_uid, info.st_gid,
                                    str(info.st_mtime_ns), str(info.st_ctime_ns), link))
                        if kind == "directory":
                            pending.append(Path(entry.path))
                        since_commit += 1
                        if since_commit >= 10000:
                            db.commit()
                            since_commit = 0
                    except (OSError, ValueError) as exc:
                        db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                                   ("read-error", volume, relative, str(exc)))
        collisions = db.execute("""
            SELECT target_volume, target_key FROM entries WHERE target IS NOT NULL
            GROUP BY target_volume, target_key HAVING count(*) > 1
        """).fetchall()
        for volume, key in collisions:
            rows = db.execute("""
                SELECT volume,relative,target,kind,mode,uid,gid FROM entries
                WHERE target_volume=? AND target_key=?
            """, (volume, key)).fetchall()
            if len({r[2] for r in rows}) > 1:
                category = "case-collision"
            elif any(r[3] != "directory" for r in rows):
                category = "leaf-collision"
            else:
                category = "directory-merge-review"
            db.execute("INSERT INTO issues VALUES (?,?,?,?)",
                       (category, volume, key, json.dumps(rows)))
        # Every mapped ancestor directory has its own entry, so a file
        # obstructing a parent is already a leaf collision above.
        db.execute("UPDATE metadata SET value='planning-snapshot' WHERE name='status'")
        db.commit()
        summary = {
            "output": str(output),
            "entries": db.execute("SELECT count(*) FROM entries").fetchone()[0],
            "issues": dict(db.execute("SELECT category,count(*) FROM issues GROUP BY category")),
            "warning": "Live snapshot only. No hashes, ACL/xattr capture, copy verification or deletion authorization.",
        }
        return summary
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--y-root", required=True)
    parser.add_argument("--z-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = inventory(args.y_root, args.z_root, args.output)
    print(json.dumps(result, indent=2))
    return 2 if result["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
