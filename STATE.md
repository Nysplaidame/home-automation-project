# Home Automation - STATE (read this first, every session)

Only mandatory start-of-session read. Keep under ~200 lines. `/handoff` replaces the START HERE block; history goes in `main/HANDOFF-*.md`.
Drafted 2026-11-11 from README.md, main/TO-DO.md and the latest handoff. The owner should review it; anything marked "unconfirmed" was not checked.

## ▶ START HERE (updated 2026-11-11, by Claude Sonnet 5.5, draft)

- **Branch / HEAD:** `codex/portal-refinement`, `ae605c2` "feat: record home automation project updates" (in sync with remote; the working tree has uncommitted changes, see below).
- **Just finished (per TO-DO, 4-10 Nov):** UI20261104-4 dashboard (normalised 360 opening, integer RPM/gas, flow arrows, FDM sensor reassignment); E2 host/identity repair (stale retained MQTT discovery removed, E2 back on `.52`); continuous discovery alerts and five-minute HA identity/E2 checks moved to VM102 systemd with ntfy.
- **In progress (exact stopping point):** verify that E2's HA host stays `.52` after the next normal HA restart or E2 reconnect and that `esphome/discover/ventsys-main-valve-1` is not republished. No NAS-stall capture is running; the paired SMB capture tooling is ready and waits for the owner to start it.
- **Waiting on the user:** camera reconnection and CCTV acceptance; physical tests (both external 360 touch inputs, loaded travel, restart retention on all boards, FDM print touch under servo load); declaring VentSys commissioned; starting the paired SMB capture just before the next affected work.
- **Next step (tier):** fix interrupted mode-release recovery (desired intent is saved before valve closures, so a retry can omit the released valves and shared paths) - Executor tier; then decide normal-mode fan speed after the last purge ends.
- **Touches:** `main/ventsys/`, `main/configs/esphome/`, `main/dashboards/`, `main/docs/`, `main/TO-DO.md`, `wiki/pages/`.
- **Uncommitted work to protect (unconfirmed what it is):** about 94 changes, including roughly 50 deleted files under `main/docs/` and `main/tools/`. Checkpoint before committing and ask the owner whether the deletions are intended.

## Current state

Canonical detail: `main/docs/reference/current-live-state.md`. Summary from README.md:

| Area | State |
|---|---|
| Network and router | 11 segments incl. isolated cloud-IoT VLAN 55; GL-MT6000 live on its management IP |
| Proxmox / HA VM | Proxmox VE 9 on the M1 Pro; HAOS VM 100 live with local-CA HTTPS |
| Frigate | Lifecycle repaired; cameras disconnected and disabled pending real-stream acceptance (owner-gated) |
| Docker host (VM 103) | Live; Bambuddy temporarily on host networking until the P1S/VLAN 35 path is reachable |
| Local AI (CT 114) | GPU llama.cpp, Open WebUI, Whisper, Piper, OpenWakeWord live |
| NAS (OMV) | Live on VLAN 40; storage paths used by Proxmox/HA/Immich |
| Remote access | Tailscale daily; WireGuard dormant fallback |
| VentSys dashboard | Authenticated HA card live, hardware under supervised testing |
| VentSys hardware | Not commissioned; some boards adopted and under test |
| VentSys HA packages / ESPHome | Written and staged; do not treat VentSys entities as live until hardware is adopted |
| NAS SMB stall investigation | Lead is open/create/lease coordination, not throughput; paired capture ready, no root cause claimed |

## Key locations

| What | Where |
|---|---|
| Wrapper layout | `README.md`, `AGENTS.md` (this repo root) |
| Project overview / index / tasks | `main/README.md`, `main/PROJECT-INDEX.md`, `main/TO-DO.md` |
| Live state | `main/docs/reference/current-live-state.md` |
| Handoffs | `main/HANDOFF-*.md` (latest: 2026-09-30 NAS transfer monitor) |
| Decisions | `main/docs/decisions/` |
| Wiki | `wiki/` (read `wiki/CLAUDE.md` first) |
| Fresh rebuild manual | `main/docs/install/START-HERE.md` |
| Archive | `main/_archive/` (single bounded historical area) |

## Rules worth repeating

- Canonical checkout is the K: Obsidian vault; other checkouts may lag.
- Never write the Samba password or the `.ha-token` file into tracked files.
- Do not bulk-read the repo; start from `main/PROJECT-INDEX.md`.
- If project docs and the wiki disagree, project docs win.

## Commands

Not confirmed. Deployment of dashboard files is a copy to the Home Assistant `config\www\` share after local validation (see AGENTS.md); `main/_verify.ps1` and `main/tools/playwright-smoke/` exist but their usage was not checked.
