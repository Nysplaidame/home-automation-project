---
title: Handoff - project audit and main/portal branch merge
description: State after the 2026-11-13 repository audit and the local merge of main into codex/portal-refinement
tags: [handoff, audit, git]
created: 2026-11-13
modified: 2026-11-13
type: handoff
status: active
---

# Handoff: project audit and `main` / `codex/portal-refinement` merge (2026-11-13)

## Where things stand

- The repository audit is complete. It covered the repository only (both
  branches); no live host was contacted.
- `main` and `codex/portal-refinement` had diverged at `ab81a70` (2026-07-16):
  `main` carried the voice stack, portal carried everything else (VentSys,
  monitoring, apps). They are now merged in **one local commit, `d41c0b6`**, on
  branch **`integrate/main-into-portal`**.
- Worktree holding that branch:
  `K:\Documents\Obsidian\home-automation-project\.claude\worktrees\project-audit-3135a5`
- **Nothing is pushed.** `codex/portal-refinement` (`8e8f8a6`) is unchanged.
  Local `main` was fast-forwarded to `3c913a1` (two voice commits from
  `claude/llm-igpu-speed-handoff-d9cffa`) and is two ahead of `origin/main`.
- Restore points: tags `pre-merge/main-20261113` (`5a6514c`) and
  `pre-merge/portal-20261113` (`8e8f8a6`).
- The primary checkout (on `codex/portal-refinement`) and the four `agent/00x`
  worktrees were not touched.

## How the 27 conflicts were resolved

Rule: keep portal's structure, carry over `main`'s facts (as the merge note in
`TO-DO.md` asked).

| Area | Resolution |
|---|---|
| Docs, diagrams, wiki (19 files) | Portal versions plus Voice Mixer, Tailscale host route `192.168.20.104/32` (five routes), CT 114 at 6c / 28 GiB |
| Homepage stack (`services.yaml`, `nginx.conf`, `custom.js`, `settings.yaml`) | Portal files plus Voice Mixer card, `8210` listener, `['192.168.20.104:7860', 8210]` port-map entry |
| SearXNG (`docker-compose.yml`, `README.md`) | `main`'s 2026.11.5 digest pin and engine notes on portal's structure |
| `configs/openwrt/dhcp-config.conf` | Both: portal's domains plus `ha-media.home.arpa` and the Voice PE lease |
| `configs/local-ai/system/llm-host-firewall.sh` | `main`'s loop including port `10201` |
| `llamacpp_conversation/__init__.py` | `main`'s `_trim_messages` flow and insert-before-last-user placement; portal's user-role "Untrusted reference data" wrapper for the hint |
| `wiki/log.md` | Portal log with `main`'s 2026-10-11 entry inserted in date order |

## Checks run on `d41c0b6`

- Pass: no conflict markers; `__init__.py` compiles; Homepage and SearXNG YAML
  parse; nginx braces balance with no duplicate listeners;
  `llm-host-firewall.sh` passes `bash -n`; links in the entry documents
  resolve; Voice Mixer tests (37 passed).
- Fails, and fails on the portal tip too:
  `configs/docker-host/stacks/homepage/tests/access-contract.cjs` - the
  Filebrowser card uses `http://192.168.40.50:3670/`, the test requires HTTPS
  hrefs on `homepage.home.local`.
- Not run: test suites for `home-operations-workbench`, `solar-observatory`,
  `transferportal`, `troubleshooting-dashboard`.

## Follow-up steps, in order

### 1. Land the merge (owner approval needed for each)

1. Fast-forward local `main` and `codex/portal-refinement` to `d41c0b6`. The
   primary checkout has `codex/portal-refinement` checked out with
   uncommitted `.agents/` changes, so update it from there
   (`git merge --ff-only integrate/main-into-portal`), not with `branch -f`.
2. Push `main` and `codex/portal-refinement`; then retire one so there is a
   single trunk.
3. Rebase `agent/003` to `agent/006` onto the merged tip (each is one or two
   commits ahead of portal; a dry run showed no conflicts between them). They
   exist only locally - push them or they are unprotected.

### 2. Verify merged sources against live before deploying from them

Resolved from git history only:

- Homepage: `config/services.yaml`, `preview-proxy/nginx.conf`,
  `config/custom.js` (VM 103, `/opt/stacks/homepage/`)
- SearXNG `docker-compose.yml` (VM 103)
- `configs/openwrt/dhcp-config.conf` (router)
- `configs/local-ai/system/llm-host-firewall.sh` (CT 114)
- `llamacpp_conversation/__init__.py` (HA) - the combined hint logic has not
  run in Home Assistant; test a recipe/web-search follow-up turn.
- Confirm Tailscale routes on docker-host: portal's docs said four, `main`
  (verified 2026-10-11) said five including `192.168.20.104/32`. The merge
  records five.
- Rebuild the Mermaid Viewer and redeploy `/opt/stacks/mermaid-viewer/dist`
  (open item in `TO-DO.md`).

### 3. Secret in git (owner action)

`.obsidian/plugins/obsidian-local-rest-api/data.json` is tracked and on GitHub
since 2026-05-08 with a 64-character API key and a TLS private key.

1. Owner regenerates the key and certificate in the plugin.
2. `git rm --cached` the file and add it to `.gitignore`.
3. Decide whether to purge it from history; rotation is the essential part.

### 4. Remaining unmerged work

- `claude/todo-list-review-6c88a1`: five Fail2ban commits (2026-07-31 to
  08-01) on neither line. It conflicts in 8 files because its `TO-DO.md` and
  live-state edits are stale. Lift only
  `configs/local-ai/system/llm-host-fail2ban-sshd.local`,
  `docs/procedures/fail2ban_host_rollout.md`,
  `docs/procedures/ids_ips_progression_plan.md` and any other new config
  sources; discard its task-list edits.

### 5. Documentation drift found by the audit

- `STATE.md`: cites HEAD `ae605c2` and "about 94 uncommitted changes"; both
  are out of date. Rewrite the START HERE block after the merge lands.
- Root `AGENTS.md`: says the checkout is `E:\home-automation-project`; it is
  `K:\Documents\Obsidian\home-automation-project`. Old `E:\`/`G:\` paths also
  in `docs/procedures/docker_host_patch_window_runbook.md` and
  `docs/install/services/obsidian-livesync.md`.
- Frontmatter `modified` dates lag by one to three months on `TO-DO.md`,
  both READMEs, `PROJECT-INDEX.md`, `current-live-state.md`,
  `service-matrix.md` and `access-matrix.md`.
- `TO-DO.md` is about 1,590 lines with roughly 350 done items around 170 open
  ones. Archive completed items; fix the "Phase 3 - VentSys, hardware
  pending" header and its unticked procurement boxes (boards are flashed and
  running); clear "Immediate next actions" (mostly done, still mentions
  `/opt/frigate/.env`); write dates with a year ("November4" style now).
- `PROJECT-INDEX.md` omits about 95 files under `main/docs` (install docs,
  audits, 20 procedures).
- Wiki: no pages for Solar Observatory or Obico; Vaultwarden has one mention.
- Decisions: number 06 is missing from the sequence; `openwrt_wireless_config.md`
  and `router-security-recommendations.md` are unnumbered.
- Fix the Filebrowser Homepage card (or the contract test) so
  `access-contract.cjs` passes.

### 6. Housekeeping

- Delete merged branches and worktrees once the trunk is settled:
  `claude/comfyui-reactor-install-cee0c7`, `claude/full-project-audit-7217e2`,
  `claude/gridfinity-docker-blank-screen-4c71f5`,
  `claude/mermaid-diagram-cleanup-ec1358`, `claude/voice-tools-prompt-c3a8c5`,
  `claude/llm-igpu-speed-handoff-d9cffa`, plus the April `claude/*` and
  `backup/*` branches if no longer wanted.
- `git count-objects` reports leftover `tmp_obj_*` files; run `git gc` when no
  agent is working.
- Repo weight (338 MB pack): `docs/audits/2026-07-full-system-audit/worktree-file-inventory.csv`
  (5 MB) and about 30 MB of Tesseract binaries under
  `configs/docker-host/stacks/recomp-tracker/static/ocr/`.
- `main/.obsidian/` is still tracked (flagged by the 2026-09-25 file audit);
  `cam_01_latest_check.jpg` came back at the repo root from `main` and can be
  removed.
- No CI: four apps have tests and nothing runs them automatically.

## Do not

- Do not push, force-move branches or delete worktrees without the owner's
  go-ahead.
- Do not deploy the seven merged config sources in step 2 before comparing
  them with the live hosts.
- Hardening items 3 to 8 in `TO-DO.md` (restore proof, credential rotation)
  remain open and owner-gated. Having no off-site backup copy is a recorded
  owner decision, not a gap.
