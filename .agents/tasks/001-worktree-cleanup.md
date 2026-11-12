---
id: 001
title: Remove merged worktrees (Home Automation)
status: done        # proposed → approved → running → done | blocked
tier: mechanical
agent: script           # no model: a deterministic script does the work
script_cmd: & '{python}' -I '{agent_ops}/tools/worktrees/clean.py' --repo '{repo}' --apply; & '{python}' -I '{agent_ops}/tools/worktrees/clean.py' --repo '{repo}' --verify
created: 2026-11-11
---

## Goal
Get rid of the 4 worktrees that are clean and fully merged. The other 3 hold uncommitted or unmerged work and are left alone. Nothing that exists only in a worktree is lost.

## What it does
1. A worktree is removed only if it has no uncommitted or untracked files and every commit on it is already in a base branch (`origin/main`, `main`, `master`, or the main checkout's branch).
2. Its branch is deleted with `git branch -d`, which refuses if anything is unmerged. Dead entries are pruned.
3. Every removal is logged with its commit hash in `agent-ops/state/worktree-clean-<date>.json`; a branch comes back with `git branch <name> <hash>`.
4. Never uses `--force`; locked worktrees and the main checkout are skipped.

Preview any time, changing nothing: `python agent-ops/tools/worktrees/clean.py --repo "<this repo>"`

## Acceptance
- [ ] `clean.py --verify` exits 0: no safe-to-remove worktree left.

## Result
**Script (2026-11-11):** status `done` (exit 0).

```
3 worktrees: 0 safe to remove, 3 kept
  KEEP   claude/full-project-audit-7217e2                   K:/Documents/Obsidian/home-automation-project/.claude/worktrees/eloquent-fermi-be507b  (1 uncommitted or untracked files)
  KEEP   claude/gridfinity-docker-blank-screen-4c71f5       K:/Documents/Obsidian/home-automation-project/.claude/worktrees/gridfinity-docker-blank-screen-4c71f5  (8 uncommitted or untracked files)
  KEEP   claude/mermaid-diagram-cleanup-ec1358              K:/Documents/Obsidian/home-automation-project/.claude/worktrees/mermaid-diagram-cleanup-ec1358  (6 uncommitted or untracked files)
removed 4, failed 0; log: K:\Documents\Obsidian\agent-ops\state\worktree-clean-2026-11-11.json
0 safe-to-remove worktrees left
```
