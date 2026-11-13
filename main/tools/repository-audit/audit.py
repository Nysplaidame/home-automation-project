"""Read-only Git-aware file audit; ignores dependency/cache trees by construction.

Reports candidates, not permission to delete. JSON output contains paths and
diagnostics, never source snippets or credential values. Run from any directory.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[3]


def git_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root, capture_output=True, check=True,
    )
    paths = set(result.stdout.decode("utf-8").split("\0")) - {""}
    # Untracked embedded repositories are emitted as directories by Git.
    # Inventory their versioned/candidate files using their own ignore policy.
    for name in tuple(paths):
        child = root / name
        if child.is_dir() and (child / ".git").exists():
            paths.remove(name)
            paths.update(name.rstrip("/") + "/" + entry for entry in git_paths(child))
    return sorted(paths)


def prose_lines(text: str):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, re.sub(r"`[^`]*`", "", line)


def audit(root: Path) -> dict:
    names = git_paths(root)
    existing = [name for name in names if (root / name).is_file()]
    by_name = defaultdict(list)
    hashes = defaultdict(list)
    issues = defaultdict(list)
    counts = Counter()
    for name in existing:
        path = root / name
        by_name[path.name.casefold()].append(name)
        by_name[path.stem.casefold()].append(name)
    for name in existing:
        path = root / name
        try:
            data = path.read_bytes()
        except OSError:
            issues["unreadable"].append(name)
            continue
        counts["files"] += 1
        counts["bytes"] += len(data)
        if data:
            hashes[hashlib.sha256(data).hexdigest()].append(name)
        if path.suffix.lower() not in {".md", ".py", ".json", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".yaml", ".yml", ".sh", ".ps1", ".conf", ".html"}:
            continue
        try:
            content = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            issues["non_utf8"].append(name)
            continue
        historical = name.startswith("main/_archive/") or "/docs/audits/" in name
        generated = any(part in path.parts for part in ("dist", "vendor"))
        if not generated:
            for line_number, line in enumerate(content.splitlines(), 1):
                if re.match(r"^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----$", line.strip()):
                    issues["private_key_candidates"].append({"file": name, "line": line_number})
        if not historical and not generated:
            if path.suffix == ".py":
                try:
                    ast.parse(content, filename=name)
                    counts["python_syntax"] += 1
                except SyntaxError as exc:
                    issues["syntax"].append({"file": name, "line": exc.lineno, "kind": "python"})
            elif path.suffix == ".json":
                try:
                    json.loads(content)
                    counts["json_syntax"] += 1
                except ValueError:
                    issues["syntax"].append({"file": name, "kind": "json"})
            elif path.suffix in {".yaml", ".yml"} and yaml is not None:
                try:
                    list(yaml.compose_all(content))
                    counts["yaml_syntax"] += 1
                except yaml.YAMLError:
                    issues["syntax"].append({"file": name, "kind": "yaml"})
        if path.suffix != ".md":
            continue
        counts["markdown"] += 1
        for line_number, line in prose_lines(content):
            for match in re.finditer(r"!?\[[^\]]*\]\((<[^>]*>|[^\s)]*)(?:\s+\"[^\"]*\")?\)", line):
                target = match.group(1).strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith(("#", "//", "/")) or not parsed.path:
                    continue
                # Angle brackets/templates are example syntax, not file references.
                if any(token in target for token in ("<", ">", "{", "}")):
                    continue
                if not (path.parent / unquote(parsed.path)).exists():
                    key = "historical_links" if historical else "broken_links"
                    issues[key].append({"file": name, "line": line_number, "target": target})
            for match in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", line):
                target = match.group(1).split("#", 1)[0]
                if not target or any(c in target for c in "<>{}"):
                    continue
                options = [path.parent / target, root / target, root / "main" / target, root / "wiki" / target, root / "wiki/pages" / target]
                if any(p.exists() or any(p.with_suffix(p.suffix + ext).exists() for ext in (".md", ".mermaid", ".yaml", ".yml", ".py", ".ps1", ".sh", ".conf", ".html", ".js", ".json")) for p in options):
                    continue
                candidates = set(by_name.get(Path(target).name.casefold(), []))
                qualified = {candidate for candidate in candidates if candidate.casefold().endswith((target.casefold(), target.casefold() + ".md"))}
                if len(qualified) == 1:
                    continue
                if len(candidates) == 1:
                    continue
                key = "historical_wikilinks" if historical else "unresolved_wikilinks"
                issues[key].append({"file": name, "line": line_number, "target": target, "candidates": len(candidates)})
    issues["missing_tracked"] = [name for name in names if not (root / name).exists()]
    issues["generated_candidates"] = [name for name in existing if any(
        part in {"node_modules", "__pycache__", ".pytest_cache", ".esphome", ".venv", "coverage"}
        for part in Path(name).parts
    )]
    issues["duplicate_groups"] = [group for group in hashes.values() if len(group) > 1]
    return {"scope": str(root), "counts": dict(counts), "issues": dict(issues)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    result = audit(ROOT)
    encoded = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
        print(json.dumps({"counts": result["counts"], "findings": {k: len(v) for k, v in result["issues"].items()}}))
    else:
        print(encoded)
    return int(bool(result["issues"].get("syntax") or result["issues"].get("unreadable")))


if __name__ == "__main__":
    raise SystemExit(main())
