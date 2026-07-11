#!/usr/bin/env python3
"""Generate deterministic, redacted inventories and task ledgers for the July audit."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import yaml


AUDIT_DIR = Path(__file__).resolve().parent
MAIN = AUDIT_DIR.parents[2]
ROOT = MAIN.parent


def git_paths(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args, "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def tracked_paths() -> set[str]:
    return set(git_paths("ls-files"))


def untracked_paths() -> set[str]:
    return set(git_paths("ls-files", "--others", "--exclude-standard"))


def ignored_paths() -> set[str]:
    return set(git_paths("ls-files", "--others", "--ignored", "--exclude-standard"))


def all_worktree_files() -> list[Path]:
    return sorted(
        (
            path
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(ROOT).parts
        ),
        key=lambda path: path.relative_to(ROOT).as_posix().lower(),
    )


def scope(rel: str) -> str:
    parts = Path(rel).parts
    if "_archive" in parts:
        return "historical"
    if parts and parts[0] == "wiki":
        return "wiki"
    if parts and parts[0] == "main":
        return "active"
    return "wrapper"


def category(rel: str) -> str:
    path = Path(rel)
    suffix = path.suffix.lower()
    normalized = rel.replace("\\", "/")
    if "__pycache__" in path.parts or suffix in {".pyc", ".pyo"}:
        return "cache/generated"
    if "/.codex/" in normalized or "/.obsidian/" in normalized:
        return "tool-metadata"
    if "/assets/vendor/" in normalized or "/custom_components/" in normalized:
        return "vendor/custom-component"
    if "/tools/router-deploy/generated/" in normalized:
        return "generated-router-artifact"
    if path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}:
        return "docker-compose"
    if suffix == ".md" or "/docs/" in normalized:
        return "documentation"
    if "/configs/" in normalized:
        return "configuration"
    if "/scripts/" in normalized or "/tools/" in normalized:
        return "script/tool"
    if "/dashboards/" in normalized:
        return "dashboard"
    if "/assets/" in normalized or suffix in {".stl", ".3mf", ".scad", ".png", ".svg"}:
        return "physical-design/asset"
    if "/apps/" in normalized:
        return "application"
    return "project"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_index(paths: list[Path]) -> dict[str, list[Path]]:
    names: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        if path.suffix.lower() == ".md":
            names[path.stem.lower()].append(path)
    return names


def resolve_link(source: Path, target: str, names: dict[str, list[Path]]) -> bool:
    target = target.split("|")[0].split("#")[0].strip().strip("<>")
    if not target or re.match(r"^(https?://|mailto:|app://)", target, re.I):
        return True
    if any(token in target for token in ("{{", "}}", "<", ">")):
        return True
    candidates = [source.parent / target]
    if not Path(target).suffix:
        candidates.append(source.parent / f"{target}.md")
    for base in (ROOT, MAIN, ROOT / "wiki", ROOT / "wiki" / "pages"):
        candidates.extend((base / target, base / f"{target}.md"))
    if any(candidate.exists() for candidate in candidates):
        return True
    if "/" in target.replace("\\", "/"):
        return False
    return bool(names.get(Path(target).stem.lower()))


def validate(path: Path, names: dict[str, list[Path]]) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    method = "existence/hash"
    try:
        if suffix == ".md":
            method = "UTF-8 decode and local-link resolution"
            text = path.read_text(encoding="utf-8-sig", errors="strict")
            without_code = re.sub(r"```.*?```", "", text, flags=re.S)
            targets = re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", without_code)
            targets += re.findall(r"(?<!!)\[\[([^\]]+)\]\]", without_code)
            broken = [target for target in targets if not resolve_link(path, target, names)]
            if broken:
                return method, "fail", f"{len(broken)} unresolved local link target(s)"
            return method, "pass", f"{len(targets)} link token(s) checked"
        if suffix == ".json":
            method = "JSON parse"
            json.loads(path.read_text(encoding="utf-8-sig"))
        elif suffix in {".yaml", ".yml"}:
            method = "YAML syntax parse (BaseLoader)"
            yaml.load(path.read_text(encoding="utf-8-sig"), Loader=yaml.BaseLoader)
        elif suffix == ".py":
            method = "Python AST parse"
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        elif suffix == ".ps1":
            method = "PowerShell parser (separate static test)"
        elif suffix == ".sh":
            method = "UTF-8 decode; shell/runtime checked separately"
            path.read_text(encoding="utf-8-sig")
        elif suffix in {".html", ".js", ".mermaid", ".conf", ".txt", ".example", ".service", ".timer"}:
            method = "UTF-8 decode/static review"
            path.read_text(encoding="utf-8-sig")
        else:
            return method, "present", "Binary or format-specific artifact"
        return method, "pass", "No syntax/read failure"
    except Exception as exc:
        return method, "fail", f"{type(exc).__name__}: {str(exc).splitlines()[0]}"


def write_artifact_inventories() -> tuple[int, int]:
    tracked = tracked_paths()
    untracked = untracked_paths()
    ignored = ignored_paths()
    files = all_worktree_files()
    relevant = [ROOT / rel for rel in sorted(tracked | untracked) if (ROOT / rel).is_file()]
    names = markdown_index(relevant)

    with (AUDIT_DIR / "worktree-file-inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["path", "git_state", "scope", "category", "extension", "bytes", "sha256"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            state = "tracked" if rel in tracked else "untracked" if rel in untracked else "ignored" if rel in ignored else "other"
            writer.writerow(
                {
                    "path": rel,
                    "git_state": state,
                    "scope": scope(rel),
                    "category": category(rel),
                    "extension": path.suffix.lower(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    with (AUDIT_DIR / "artifact-inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["path", "git_state", "scope", "category", "validation", "result", "notes"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for path in relevant:
            rel = path.relative_to(ROOT).as_posix()
            method, result, notes = validate(path, names)
            writer.writerow(
                {
                    "path": rel,
                    "git_state": "tracked" if rel in tracked else "untracked",
                    "scope": scope(rel),
                    "category": category(rel),
                    "validation": method,
                    "result": result,
                    "notes": notes,
                }
            )
    return len(relevant), len(files)


def extract_checklists(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    section = ""
    pattern = re.compile(r"\s*(?:\d+\.\s*)?(?:-\s*)?\[([ xX])\]\s*(.*)")
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
        match = pattern.match(line)
        if match:
            rows.append(
                {
                    "source": path.relative_to(MAIN).as_posix(),
                    "line": line_number,
                    "section": section,
                    "checked": match.group(1).lower() == "x",
                    "task": match.group(2).strip(),
                }
            )
    return rows


def task_disposition(row: dict[str, object]) -> tuple[str, str]:
    text = str(row["task"])
    lower = text.lower()
    if bool(row["checked"]):
        return "asserted-complete", "Checklist assertion; operational proof is controlled by the claim and live-evidence ledgers"
    if any(word in lower for word in ("park", "after ", "when ", "until ", "hardware", "blocked", "once ", "future", "arriv")):
        return "blocked/planned", "Explicit prerequisite, hardware dependency, or decision gate remains"
    return "open", "Unchecked with no automatic superseding evidence"


def write_task_ledgers() -> int:
    rows = extract_checklists(MAIN / "TO-DO.md") + extract_checklists(MAIN / "docs/install/INSTALL-TO-DO.md")
    out = [
        "# TODO Disposition Ledger",
        "",
        "Generated mechanically. Checked boxes are assertions, not live certification.",
        "",
        "| Source | Line | Section | Original | Initial disposition | Evidence basis |",
        "|---|---:|---|---|---|---|",
    ]
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        disposition, evidence = task_disposition(row)
        counts[disposition] += 1
        state = "checked" if row["checked"] else "unchecked"
        task = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (`\2`)", str(row["task"]))
        task = task.replace("|", "\\|")
        section = str(row["section"]).replace("|", "\\|")
        out.append(f"| `{row['source']}` | {row['line']} | {section} | {state}: {task} | `{disposition}` | {evidence} |")
    out.extend(["", "## Counts", "", *[f"- `{key}`: {value}" for key, value in sorted(counts.items())], f"- Total: {len(rows)}"])
    (AUDIT_DIR / "todo-disposition.md").write_text("\n".join(out) + "\n", encoding="utf-8")

    roadmap_sections = {"Docker-host app roadmap", "Home Assistant apps and enhancement roadmap", "Operational next steps", "Hardening and resilience roadmap"}
    planned = [row for row in rows if not row["checked"] and row["section"] in roadmap_sections]
    roadmap = [
        "# Roadmap Feasibility Disposition",
        "",
        "Initial mechanical classification; final feasibility is controlled by current vendor and live-state evidence.",
        "",
        "| Source line | Section | Roadmap item | Initial classification |",
        "|---:|---|---|---|",
    ]
    for row in planned:
        task = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (`\2`)", str(row["task"]))
        task = task.replace("|", "\\|")
        roadmap.append(f"| {row['line']} | {row['section']} | {task} | `requires-evidence-review` |")
    (AUDIT_DIR / "roadmap-disposition.md").write_text("\n".join(roadmap) + "\n", encoding="utf-8")
    return len(rows)


def main() -> None:
    relevant, worktree = write_artifact_inventories()
    todo_rows = write_task_ledgers()
    print(f"relevant_artifacts={relevant} worktree_files={worktree} todo_rows={todo_rows}")


if __name__ == "__main__":
    main()
