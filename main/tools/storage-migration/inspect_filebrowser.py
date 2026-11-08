"""Read-only, credential-filtered inspection of a stable BoltDB byte snapshot.

No live database connection or write is made. Refuses unsupported/corrupt pages.
This is discovery evidence, not a transactional backup or authorization editor.
"""
import hashlib
import json
from pathlib import Path
import struct


def inspect(path):
    path = Path(path)
    if path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError("Unexpectedly large database")
    for _ in range(3):
        data = path.read_bytes()
        if data == path.read_bytes():
            break
    else:
        raise ValueError("Database changed while reading")
    def fnv(value):
        checksum = 14695981039346656037
        for byte in value:
            checksum = ((checksum ^ byte) * 1099511628211) & ((1 << 64) - 1)
        return checksum
    page_size = struct.unpack_from("<I", data, 24)[0]
    if not 1024 <= page_size <= 65536:
        raise ValueError("Unsupported page size")
    metas = []
    for offset in (0, page_size):
        value = data[offset+16:offset+80]
        if len(value) != 64:
            continue
        magic, version, size, _ = struct.unpack_from("<IIII", value)
        if (magic == 0xed0cdaed and version == 2 and size == page_size and
                fnv(value[:56]) == struct.unpack_from("<Q", value, 56)[0]):
            metas.append((struct.unpack_from("<Q", value, 48)[0], struct.unpack_from("<Q", value, 16)[0]))
    if not metas:
        raise ValueError("No valid metadata checksum")
    transaction, root = max(metas)
    visited, users, bucket_names = set(), [], []
    def entries(blob, offset):
        if offset + 16 > len(blob):
            raise ValueError("Bad page bounds")
        _, flags, count, _ = struct.unpack_from("<QHHI", blob, offset)
        for index in range(count):
            location = offset + 16 + index * 16
            if flags & 1:
                _, _, page = struct.unpack_from("<IIQ", blob, location)
                yield from read_page(page)
            elif flags & 2:
                flag, position, key_size, value_size = struct.unpack_from("<IIII", blob, location)
                begin, end = location + position, location + position + key_size + value_size
                if end > len(blob):
                    raise ValueError("Bad leaf bounds")
                yield flag, blob[begin:begin+key_size], blob[begin+key_size:end]
            else:
                raise ValueError("Unsupported page flags")
    def read_page(page):
        if page in visited or len(visited) > 4096:
            raise ValueError("Repeated or excessive page traversal")
        visited.add(page)
        yield from entries(data, page * page_size)
    safe = {"name", "source", "path", "root", "scope", "scopes", "sources", "permissions", "perm", "admin", "id", "username"}
    def filtered(value):
        if isinstance(value, list):
            return [filtered(v) for v in value]
        if isinstance(value, dict):
            return {k: filtered(v) for k, v in value.items()
                    if k.lower() in safe or isinstance(v, bool)}
        return value if isinstance(value, (str, int, bool, type(None))) else None
    def bucket(items, prefix):
        if len(prefix) > 2048:
            raise ValueError("Excessive bucket nesting")
        for flags, key, value in items:
            name = key.decode("utf-8", errors="replace")
            if flags & 1:
                page = struct.unpack_from("<Q", value)[0]
                label = prefix + "/" + name
                bucket_names.append(label)
                bucket(read_page(page) if page else entries(value[16:], 0), label)
            else:
                try:
                    record = json.loads(value)
                except (ValueError, UnicodeError):
                    continue
                if isinstance(record, dict) and "username" in record:
                    users.append({"selected": filtered({k: v for k, v in record.items()
                                  if k.lower() in {"username", "id", "scopes", "scope", "permissions", "perm"}})})
    bucket(read_page(root), "")
    return {"snapshot_sha256": hashlib.sha256(data).hexdigest(), "transaction": transaction,
            "users": users, "bucket_names": bucket_names,
            "method": "two identical reads, valid Bolt metadata checksums, selected non-credential fields only"}


if __name__ == "__main__":
    print(json.dumps(inspect("/var/lib/filebrowser/database.db"), indent=2))
