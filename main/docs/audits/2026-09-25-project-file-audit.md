---
title: Project File and Structure Audit
description: Repository hygiene, deprecated-content, reference, and file-count review
created: 2026-09-25
modified: 2026-09-25
type: audit
status: complete
---

# Project File and Structure Audit — 2026-09-25

## Scope and safety boundary

This audit inspected the canonical `K:\Documents\Obsidian\home-automation-project`
checkout. It reviewed tracked and untracked file counts, generated data, archive
content, duplicate tracked content, explicit deprecated/stale markers, and local
Markdown links.

The checkout already contained a large unrelated working set (modified and
untracked project files). Those files were treated as owner work and were not
rewritten, moved, staged, or deleted by this audit.

## Baseline

| Measure | Result |
|---|---:|
| Tracked files | 761 before cleanup |
| Tracked files under `main/` | 622 before cleanup |
| Tracked Markdown files | 306 |
| Tracked archive files | 29 |
| Tracked archive size | about 0.67 MB |
| Physical files under `main/` | 19,039 at inspection time |
| Ignored ESPHome `_dev/.esphome` cache | about 2,800 files / 172.71 MB |
| Untracked dated Obico transfer tree | about 1,273 files / 341.34 MB |
| Ignored `.claude/worktrees` data | about 1,803 files / 94.76 MB |
| Ignored Google Drive upload staging | 4 files / about 15.90 MB |

The gap between 622 tracked `main/` files and 19,039 physical `main/` files is
mostly generated/build material, not an oversized canonical document set.

## Cleanup completed

1. Added `.obico-transfer-*/` to the root `.gitignore`. The dated transfer tree
   is local staging containing an extracted release and `release.zip`; it should
   not appear as thousands of repository candidates.
2. Removed
   `main/assets/3d-printing/skill-test-servo-wiring-no-led-v16/servo_wiring_no_led_v16 - copy.scad`.
   It was byte-for-byte identical to `servo_wiring_no_led_v16.scad`. Its only
   references were historical audit inventories.

No generated cache, transfer bundle, historical audit, handoff, live config,
deployment asset, or owner-authored uncommitted file was deleted.

## Findings

### 1. Generated local data dominates the apparent file count

The largest reductions in filesystem count come from local build and transfer
data, not from pruning canonical documentation. The ESPHome build cache is
already ignored correctly. The Obico transfer staging tree was not; the new
ignore rule closes that gap. Deleting either cache is optional local disk
maintenance and should happen only when no build or transfer is in progress.

### 2. The tracked archive is small and already bounded

`main/_archive/` contains 29 tracked files and is about 0.67 MB. It has an
explicit README that marks the contents as superseded. Removing it would reduce
file count slightly but save negligible space while discarding useful provenance.
Keep it unless repository-history retention is intentionally changed.

### 3. Mermaid Viewer duplication was consolidated

The exact-content copies formerly split between `main/apps/mermaid-viewer/` and
`main/configs/docker-host/stacks/mermaid-viewer/` were consolidated on
2026-09-25. `main/apps/mermaid-viewer/` is now the only source tree, `src/` is
editable source, and `dist/` is the single checked-in release artifact. The
colocated release command rebuilds, hashes, browser-verifies, checkpoints and
deploys the complete stack. The duplicate stack payload, old root-level frontend
copies and draft packaging directory were removed.

### 4. The long-running handoff was closed

Only three top-level handoff files exist, so the count is low, but
`HANDOFF-2026-07-27-portal-services.md` had grown across many later workstreams.
It was marked closed on 2026-09-25 with a compact current-state/resume section.
Durable Mermaid Viewer facts were moved into its service manual and
current-live-state, and the repository instructions now require new handoffs
only for genuinely active continuity work. The dated body remains historical
deployment and rollback evidence.

### 5. Two Obsidian configurations exist

The wrapper root has the active `.obsidian/` tree, while `main/.obsidian/` contains
three tracked JSON files. The root README defines the repository root as the
Obsidian vault wrapper, so the nested configuration may be legacy. Confirm which
folder is opened as a vault on every device before removing it. If all devices
open the repository root, delete `main/.obsidian/` and keep only the root config.

### 6. One root-level camera image lacks a current documentation reference

`cam_01_latest_check.jpg` is tracked at repository root and appears only in old
audit inventories. It is small (about 97 KB), but its placement is inconsistent.
Confirm whether it is still required evidence. If yes, move it under a named
`main/assets/evidence/<date>/` location and update provenance; if no, delete it.

### 7. Deprecated markers are mostly intentional history

Most `deprecated`, `obsolete`, `retired`, `legacy`, and `superseded` hits are
warnings or historical records, not abandoned files. The Recomp Tracker's old
Compose snippet was retired on 2026-09-25 after its handoff was reconciled with
the canonical standalone Compose and `.env.example` workflow.

### 8. Local Markdown link issues are confined to an older audit

A conservative inline Markdown-link check found four unresolved relative links,
all in `docs/audits/2026-06-system-audit/todo-disposition.md` (lines 300, 301,
304, and 365 at audit time). These are historical audit navigation defects, not
broken current entrypoints. Fix them if historical audits are expected to remain
navigable; otherwise preserve the report as captured evidence.

The repository uses Obsidian wikilinks to non-Markdown configs and scripts, so a
naive Markdown-only wikilink checker produces false positives. Future validation
should resolve all file extensions and ignore fenced code/examples.

## Recommended structure changes, in order

1. Confirm and remove the nested `main/.obsidian/` vault config if all devices use
   the repository root as the vault.
2. Decide whether the root camera image is evidence or residue; relocate or remove
   it accordingly.
3. Keep `_archive/` as one bounded historical area. Do not create additional
   archive trees; use Git history for disposable intermediate drafts.
4. Add a repository-aware link/reference check to `main/_verify.ps1`: validate
   Markdown relative links, Obsidian links to any tracked extension, duplicate
   tracked hashes, and unexpected untracked build roots. Keep historical-audit
   exceptions explicit.
5. Maintain the repository artifact policy now recorded in both `AGENTS.md`
   files and the root ignore rules: track source/config/runbook files and
   deliberate release artifacts; keep generated dependencies, caches, transfer
   archives, extracted releases and runtime state outside Git.

## Suggested deletion candidates requiring owner confirmation

| Candidate | Approximate impact | Why confirmation is needed |
|---|---:|---|
| `.obico-transfer-20260922/` | 1,273 files / 341.34 MB | May still be an active transfer or recovery source |
| `main/configs/esphome/_dev/.esphome/` | 2,800 files / 172.71 MB | Rebuildable cache, but a current bench compile may rely on it for speed |
| `.claude/worktrees/` | 1,803 files / 94.76 MB | Managed worktrees may belong to active sessions |
| `.tmp.driveupload/` | 4 files / 15.90 MB | Upload staging may still be in use |
| `main/.obsidian/` | 3 tracked files | Could still support a device that opens `main/` as its vault |
| `cam_01_latest_check.jpg` | 1 tracked file / 97 KB | Could be retained visual evidence despite missing current links |

These candidates were not removed during this audit.
