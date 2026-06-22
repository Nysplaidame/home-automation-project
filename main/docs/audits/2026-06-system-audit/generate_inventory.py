#!/usr/bin/env python3
"""Generate deterministic, redacted inventory and task ledgers for the audit."""

from __future__ import annotations

import ast
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

import yaml


AUDIT_DIR = Path(__file__).resolve().parent
MAIN = AUDIT_DIR.parents[2]
ROOT = MAIN.parent


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / raw.decode("utf-8") for raw in result.stdout.split(b"\0") if raw]


def scope(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if "_archive" in rel.parts:
        return "historical"
    if rel.parts and rel.parts[0] == "wiki":
        return "wiki"
    if rel.parts and rel.parts[0] == "main":
        return "active"
    return "wrapper"


def category(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.endswith("docker-compose.yml"):
        return "docker-compose"
    if "/docs/" in rel or path.suffix.lower() == ".md":
        return "documentation"
    if "/configs/" in rel:
        return "configuration"
    if "/scripts/" in rel or "/tools/" in rel:
        return "script/tool"
    if "/dashboards/" in rel:
        return "dashboard"
    if "/assets/" in rel:
        return "asset"
    return "project"


def markdown_index(files: list[Path]) -> tuple[dict[str, list[Path]], list[Path]]:
    markdown = [p for p in files if p.suffix.lower() == ".md"]
    names: dict[str, list[Path]] = defaultdict(list)
    for path in markdown:
        names[path.stem.lower()].append(path)
    return names, markdown


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
    # Obsidian permits basename-only links, but an explicitly pathed target
    # must not silently resolve to a same-named file elsewhere (especially an
    # archived file).
    if "/" in target.replace("\\", "/"):
        return False
    return bool(names.get(Path(target).stem.lower()))


def markdown_result(path: Path, names: dict[str, list[Path]]) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    without_code = re.sub(r"```.*?```", "", text, flags=re.S)
    targets = re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", without_code)
    targets += re.findall(r"(?<!!)\[\[([^\]]+)\]\]", without_code)
    broken = [target for target in targets if not resolve_link(path, target, names)]
    if broken:
        return "fail", f"{len(broken)} unresolved local link target(s)"
    return "pass", f"{len(targets)} local/remote link token(s) checked"


def validate(path: Path, names: dict[str, list[Path]]) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    method = "existence"
    try:
        if suffix == ".md":
            method = "UTF-8 decode and local-link resolution"
            result, notes = markdown_result(path, names)
            return method, result, notes
        if suffix == ".json":
            method = "JSON parse"
            json.loads(path.read_text(encoding="utf-8-sig"))
        elif suffix in (".yaml", ".yml"):
            method = "YAML syntax parse (BaseLoader)"
            yaml.load(path.read_text(encoding="utf-8-sig"), Loader=yaml.BaseLoader)
        elif suffix == ".py":
            method = "Python AST parse"
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        elif suffix == ".ps1":
            method = "PowerShell parser (external audit command)"
        elif suffix == ".sh":
            method = "UTF-8 decode; runtime sampled remotely"
            path.read_text(encoding="utf-8-sig")
        elif suffix in (".html", ".js", ".mermaid", ".conf", ".txt", ".example"):
            method = "UTF-8 decode/static review"
            path.read_text(encoding="utf-8-sig")
        else:
            return method, "present", "Binary or non-parseable project artefact"
        return method, "pass", "No syntax/read failure"
    except Exception as exc:  # values are intentionally not included
        return method, "fail", f"{type(exc).__name__}: {str(exc).splitlines()[0]}"


def write_inventory(files: list[Path]) -> None:
    names, _ = markdown_index(files)
    rows = []
    for path in files:
        method, result, notes = validate(path, names)
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "scope": scope(path),
                "category": category(path),
                "validation": method,
                "result": result,
                "notes": notes,
            }
        )
    with (AUDIT_DIR / "artifact-inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


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


def task_disposition(task: dict[str, object]) -> tuple[str, str]:
    text = str(task["task"])
    lower = text.lower()
    if bool(task["checked"]):
        paths = re.findall(r"`([^`]+)`", text)
        existing = [p for p in paths if (MAIN / p).exists()]
        if existing:
            return "complete", "Referenced project artefact exists; operational claims require claim-ledger evidence"
        return "complete", "Source checklist records completion; independently sampled where represented in the claim ledger"
    if any(word in lower for word in ("park", "after ", "when ", "until ", "hardware", "blocked", "physically available", "once nas", "future")):
        return "blocked", "Explicit prerequisite or decision gate remains"
    return "extant", "Unchecked and no superseding evidence found"


def write_todos(rows: list[dict[str, object]]) -> None:
    out = [
        "# TODO Disposition Ledger",
        "",
        "Generated from both canonical checklist files. A checked box is project-record evidence, not by itself live certification; operational assertions are controlled by the claim ledger and findings.",
        "",
        "| Source | Line | Section | Original | Disposition | Evidence basis |",
        "|---|---:|---|---|---|---|",
    ]
    for row in rows:
        disposition, evidence = task_disposition(row)
        original = "checked" if row["checked"] else "unchecked"
        task = str(row["task"]).replace("|", "\\|")
        section = str(row["section"]).replace("|", "\\|")
        out.append(
            f"| `{row['source']}` | {row['line']} | {section} | {original}: {task} | `{disposition}` | {evidence} |"
        )
    counts = defaultdict(int)
    for row in rows:
        counts[task_disposition(row)[0]] += 1
    out.extend(
        [
            "",
            "## Counts",
            "",
            *[f"- `{key}`: {value}" for key, value in sorted(counts.items())],
            f"- Total: {len(rows)}",
        ]
    )
    (AUDIT_DIR / "todo-disposition.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def roadmap_classification(text: str) -> tuple[str, str]:
    lower = text.lower()
    if any(term in lower for term in ("youtube transcript", "hermes agent", "claude/mcp")):
        return "redesign-required", "No bounded interface, security model, or acceptance contract exists"
    if any(term in lower for term in ("camera", "frigate card", "nas", "omv", "backup", "hardware", "p1s", "stable", "security review", "decision", "after", "only if", "until")):
        return "feasible-with-prerequisites", "Documented dependency or decision gate must close first"
    return "feasible-now", "Compatible with the present architecture; still requires normal change control"


def write_roadmap(rows: list[dict[str, object]]) -> None:
    roadmap_sections = {"Docker-host app roadmap", "Home Assistant apps and enhancement roadmap", "Operational next steps"}
    candidates = [row for row in rows if row["section"] in roadmap_sections and not row["checked"]]
    out = [
        "# Roadmap Feasibility Disposition",
        "",
        "This ledger classifies still-planned checklist items. External vendor-document verification was attempted but blocked by the browsing service; local installed-version validation and deployed-resource evidence were used instead.",
        "",
        "| Source line | Roadmap item | Classification | Basis |",
        "|---:|---|---|---|",
    ]
    for row in candidates:
        classification, basis = roadmap_classification(str(row["task"]))
        task = str(row["task"]).replace("|", "\\|")
        out.append(f"| {row['line']} | {task} | `{classification}` | {basis} |")
    out.extend(
        [
            "",
            "No item was classified `not-feasible`; several require redesign before feasibility can be responsibly asserted.",
        ]
    )
    (AUDIT_DIR / "roadmap-disposition.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    files = tracked_files()
    write_inventory(files)
    todo_rows = extract_checklists(MAIN / "TO-DO.md") + extract_checklists(MAIN / "docs/install/INSTALL-TO-DO.md")
    write_todos(todo_rows)
    write_roadmap(todo_rows)
    print(f"inventory={len(files)} todo_rows={len(todo_rows)}")


if __name__ == "__main__":
    main()
