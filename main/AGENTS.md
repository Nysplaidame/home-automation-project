# Home Automation Main Tree Guide

## Read First

1. Read `README.md` for the live project overview.
2. Read `PROJECT-INDEX.md` to choose the smallest relevant document set.
3. Read `TO-DO.md` when the task depends on current priorities or remaining work.
4. Read a `HANDOFF-*.md` file only when resuming live operational state or a prior implementation thread.

## Working Rules

- Treat `README.md`, `PROJECT-INDEX.md`, `TO-DO.md`, and `docs/decisions/` as the main durable project record.
- The canonical checkout is `K:\Documents\Obsidian\home-automation-project`. Other device paths, including E:, are separate working copies, not authoritative without explicit context.
- For Home Assistant dashboard/config deploys, use Samba at `\\192.168.20.101\config\www\` with the `homeassistant` credential stored in Windows Credential Manager; never store the Samba password in tracked files.
- Prefer updating existing docs over adding duplicate summaries.
- For deployment or live-system work, preserve exact commands, validation, and rollback notes in the relevant handoff or procedure file.
- Keep durable service facts in the relevant service manual and
  `docs/reference/current-live-state.md`. When an implementation thread ends,
  close its handoff with a short current-state/resume section. Create another
  handoff only when genuinely active session work needs continuity; do not let
  handoffs become permanent chronological service logs.
- Track source, configuration, runbooks, and deliberately selected release
  artifacts only. Ignore or store outside the vault build caches, extracted
  release trees, transfer archives, generated dependency trees, and local
  runtime state. Add narrow ignore rules for new generated paths.
- Use `_archive/` as the only bounded historical area. Do not create additional
  archive trees; use Git history for disposable drafts and intermediate copies.
- Use the wiki only when the task is explicitly about the wiki knowledge base.
- After meaningful work, check whether durable concepts or entity relationships changed enough to require a wiki update.
- Include a touch-toggle input in new valve and intake firmware by default, even when the touch hardware is not yet fitted, unless the user specifies otherwise. Use the board's appropriate touch-capable pin; GPIO33 is the current E2 and MAIN-2 ESP32 D1 Mini mapping. Document separately whether the physical touch input is installed.
