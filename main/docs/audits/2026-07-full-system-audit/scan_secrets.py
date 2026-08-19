#!/usr/bin/env python3
"""Redacted current-tree and Git-history secret scan for audit evidence."""

from __future__ import annotations

import csv
import math
import re
import subprocess
from collections import Counter
from pathlib import Path


AUDIT_DIR = Path(__file__).resolve().parent
MAIN = AUDIT_DIR.parents[2]
ROOT = MAIN.parent
TEXT_SUFFIXES = {
    "", ".cer", ".cfg", ".conf", ".crt", ".csv", ".env", ".example",
    ".html", ".ini", ".js", ".json", ".key", ".md", ".mmd", ".mermaid",
    ".pem", ".properties", ".ps1", ".py", ".service", ".sh", ".sql",
    ".toml", ".txt", ".xml", ".yaml", ".yml",
}
PLACEHOLDER_TERMS = (
    "placeholder", "change_me", "changeme", "example", "replace", "your_",
    "xxx", "!secret", "${", "{{", "<", "redacted", "dummy", "test-only",
)
PATTERNS = {
    "private-key-pem": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "credential-field": re.compile(
        r"(?i)[\"']?(api[_-]?key|password|passwd|token|secret|private[_-]?key|client[_-]?secret|authorization)[\"']?\s*[:=]\s*[\"']?([^\s,}\"']{8,})"
    ),
}


def run(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        list(args), cwd=ROOT, input=input_bytes, check=True, capture_output=True
    ).stdout


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(term in lowered for term in PLACEHOLDER_TERMS)


def entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def scan_text(text: str) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    for name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(2) if name == "credential-field" else match.group(0)
            if name == "credential-field" and is_placeholder(value):
                continue
            line = text.count("\n", 0, match.start()) + 1
            signal = "non-placeholder"
            if name == "credential-field" and len(value) >= 20 and entropy(value) >= 3.5:
                signal = "high-entropy-non-placeholder"
            findings.append((line, name, signal))
    return findings


def worktree_files() -> list[str]:
    """Return tracked, relevant untracked, and non-generated ignored text."""
    raw = run("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    ignored = run("git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
    files = {item.decode("utf-8") for item in raw.split(b"\0") if item}
    generated_parts = {"node_modules", ".esphome", "build", "dist", "vendor", "__pycache__"}
    for item in ignored.split(b"\0"):
        if not item:
            continue
        rel = item.decode("utf-8")
        if generated_parts.isdisjoint(Path(rel).parts):
            files.add(rel)
    return sorted(files)


def current_scan() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for rel in worktree_files():
        path = ROOT / rel
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (UnicodeDecodeError, OSError):
            continue
        for line, kind, signal in scan_text(text):
            rows.append({"scope": "current", "object": "WORKTREE", "path": rel, "line": line, "kind": kind, "signal": signal})
    return rows


def history_scan() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    objects = run("git", "rev-list", "--objects", "--all").decode("utf-8", errors="replace").splitlines()
    seen: set[str] = set()
    for entry in objects:
        oid, _, rel = entry.partition(" ")
        if not rel or oid in seen or Path(rel).suffix.lower() not in TEXT_SUFFIXES:
            continue
        seen.add(oid)
        check = run("git", "cat-file", "--batch-check=%(objecttype) %(objectsize)", input_bytes=(oid + "\n").encode()).decode().strip().split()
        if len(check) != 2 or check[0] != "blob" or int(check[1]) > 5_000_000:
            continue
        try:
            text = run("git", "cat-file", "blob", oid).decode("utf-8-sig")
        except (UnicodeDecodeError, subprocess.CalledProcessError):
            continue
        for line, kind, signal in scan_text(text):
            rows.append({"scope": "history", "object": oid[:12], "path": rel, "line": line, "kind": kind, "signal": signal})
    return rows


def main() -> None:
    rows = current_scan() + history_scan()
    fields = ["scope", "object", "path", "line", "kind", "signal"]
    with (AUDIT_DIR / "secret-scan-redacted.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    current = sum(row["scope"] == "current" for row in rows)
    history = sum(row["scope"] == "history" for row in rows)
    print(f"redacted_candidates_current={current} history_blob_candidates={history}")


if __name__ == "__main__":
    main()
