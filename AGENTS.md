# Home Automation Project Agent Guide

## Project Shape

- This repository root is an Obsidian wrapper.
- This project is worked on from multiple devices/checkouts. The canonical
  checkout is `K:\Documents\Obsidian\home-automation-project` — it is the
  Obsidian vault and the source of truth.
- Other devices have their own separate checkouts (e.g. `E:\home-automation-project`
  in a Codex desktop environment) which may lag behind or diverge from K:.
  Treat non-K: paths as local working copies, not canonical, unless told
  otherwise. Older `G:\home-automation-project` context is stale.
- If it is unclear which device or checkout is in play, ask rather than
  assume — do not silently treat a non-canonical path as authoritative.
- Active project work lives under `main/`.
- The project also contains a separate LLM-maintained wiki under `wiki/`.

## Live Home Assistant Access

- Home Assistant Samba is reachable at `\\192.168.20.101`.
- Use the `homeassistant` Samba account via Windows Credential Manager; do not write the password into tracked files.
- Deploy dashboard files directly to `\\192.168.20.101\config\www\` after local edits and validation.

## Read First

1. Read `README.md` to understand the wrapper layout.
2. For active project work, read `main/README.md`, `main/PROJECT-INDEX.md`, and `main/TO-DO.md`.
3. If resuming live work or handling deployment state, read the most relevant current file in `main/HANDOFF-*.md`.
4. If the task concerns the wiki, read `wiki/CLAUDE.md` before editing anything under `wiki/`.

## Canonical Sources

- Project overview: `main/README.md`
- Documentation index: `main/PROJECT-INDEX.md`
- Current task list: `main/TO-DO.md`
- Session handoffs: `main/HANDOFF-*.md`
- Durable decisions: `main/docs/decisions/`
- Wiki operating rules: `wiki/CLAUDE.md`

## Rules

- Do not bulk-read the entire repository.
- Prefer targeted reads based on `main/PROJECT-INDEX.md`.
- Keep durable project state in project files, not in chat-only memory.
- When work materially changes current state, update the relevant handoff, task list, or decision document rather than creating a parallel summary.
- If work changes durable concepts, entities, or relationships, update the project wiki after canonical docs are current.
- If wiki claims conflict with project docs, project docs win and the wiki should be repaired.
