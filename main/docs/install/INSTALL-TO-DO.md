---
title: Installation Manual Suite To-Do
description: Companion checklist for completing and validating the fresh rebuild documentation suite
tags: [install, tasks, rebuild, documentation]
created: 2026-05-24
modified: 2026-08-24
type: task-list
status: active
---

# Installation Manual Suite To-Do

Use this checklist with [START-HERE.md](START-HERE.md). It tracks what remains
before the documentation suite is good enough to rebuild the system from zero
without live assistance.

## Completion standard

- [ ] A true beginner can identify the next document, target machine, user/shell context, command, expected result, and recovery path at every step.
- [x] Every command block has a `Run on:` label immediately before it
  (2026-08-09 automated audit: zero missing labels across active install docs).
- [x] Every placeholder used in an install command appears in
  [secrets-placeholder-ledger.md](reference/secrets-placeholder-ledger.md)
  (2026-08-09 audit: 52 unique active-install placeholders, zero missing).
- [x] Every package or dependency appears in [package-dependency-matrix.md](reference/package-dependency-matrix.md)
  (2026-08-24 install-command audit added the missing OpenWrt `ethtool`,
  workstation Node/npm, and Garage Pi virtual-environment dependencies).
- [x] Every risky service has a decision gate before deployment (2026-08-24:
  global public-exposure, credential-store, camera-bridge, low-code/agent and
  automatic-update gates plus the service promotion-boundary matrix).
- [ ] Every Tier 1-3 service has install, validation, backup, update, rollback, and troubleshooting coverage.
- [ ] The suite passes a dry-read from [START-HERE.md](START-HERE.md) through final validation.

## Phase Manual Expansion

- [x] Phase 00 operator basics: add examples for hardware inventory, IP plan, MAC addresses, and secret placeholders.
- [x] Phase 01 router/OpenWrt: add full fresh-flash path, first-flight deploy path, full deploy path, router-local NTP validation, and lan5 recovery drill.
- [x] Phase 02 Proxmox: add ISO verification, install checkpoints, storage layout choices, bridge/VLAN validation, and rollback notes.
- [x] Phase 03 Home Assistant: add HAOS install, onboarding, add-on installs, MQTT setup, Companion App setup, router-derived time config, HACS decision gate, and backup validation.
- [x] Phase 04 Frigate: expand CT 111 base/Docker/shared-iGPU guide with tested blank-to-live recovery examples.
- [x] Phase 05 docker-host: add VM baseline, Docker official repository install, Compose policy, `/opt/stacks/<service>/` layout, Tailscale host-route setup, UFW rules, and rollback.
- [x] Phase 05A local AI inference: align CT 114 Compose, shared-iGPU mapping, HA Assist integration and performance gates.
- [x] Phase 06 OMV NAS: add OMV install, disk wipe warning, filesystems, users, NFS/SMB shares, SMART monitoring, and HA/Frigate/Immich storage mounts.
- [x] Phase 07 Tier 1 apps: add full command-by-command deploy order for AdGuard Home, Immich, Homepage, and Dozzle.
- [x] Phase 08 Tier 2 apps: make every draft installable while keeping deployment approval gates explicit.
- [x] Phase 09 Tier 3/evaluate apps: ensure Vaultwarden, Portainer, Watchtower, registry mirror, and Node-RED cannot be made live without security/backup approval.
- [x] Phase 10 backups/monitoring/maintenance: add restore drills, maintenance windows, update policy, and alerting checks.
- [x] Phase 11 physical integrations: add camera, printer, ESPHome, VentSys wiring, first-flash, adoption, and safety-test sequences.
- [x] Phase 12 validation/troubleshooting: add an end-to-end acceptance test and one troubleshooting path per Tier 1 service.

## Router-Deploy Documentation Tasks

- [x] Document that router-deploy is router-only: network, DHCP, DNS, firewall, local hostnames, WireGuard fallback, router-local NTP, and validation artifacts.
- [x] Document that router-deploy does not deploy Docker services, OMV, Tailscale auth, or app stacks.
- [x] Add beginner notes for `first-flight` versus `full` profiles.
- [x] Add expected output examples for `lint.py`, `compile.py`, `deploy.ps1`, `test.ps1`, and `test-connectivity.ps1`.
- [x] Add a recovery drill for failed deploy, watchdog rollback, and physical lan5 recovery.

## Service Manual Coverage

- [x] AdGuard Home: install, first-run setup, router DNS fallback, blocklist policy, backup/export, monitoring, rollback.
- [x] Immich: install, `.env`, database volumes, OMV library path, backup, update, mobile app onboarding, rollback.
- [x] Homepage: install, service widgets, secrets handling, backup, rollback.
- [x] Dozzle: install, read-only Docker socket decision, auth/exposure decision, backup, rollback.
- [x] Paperless-ngx: install, scanner/import path, OCR dependencies, backup, retention, rollback.
- [x] Mealie: manual now covers named users, full application backup, portable
  recipe export, loopback-only isolated restore, updates and matching-data
  rollback. Live admin/export acceptance remains an operator action.
- [x] Grocy: manual now covers the disposable purchase/consume/correction/
  expiry workflow, pre-pilot checkpoint, isolated restore and version/data
  rollback. The live pilot remains an operator action.
- [x] Obsidian LiveSync: manual now covers backend rebuild, `K:` canonical-vault
  selection, Bitwarden/setup-URI separation, stop-before-initialise gate,
  two-device round trip, isolated CouchDB restore and wrong-source rollback.
  Client rollout remains parked while the canonical tree is dirty.
- [x] ntfy: install, topic policy, public/private exposure decision, backup, rollback.
- [x] Actual Budget: install, auth, backup/export, rollback.
- [x] Scrypted: hardware/camera decision gate, install, storage, HA/Frigate overlap, rollback.
- [x] SearXNG: install, instance secret, egress policy, rate-limit/abuse controls, backup, rollback.
- [x] Whoogle: install, egress policy, rate-limit/abuse controls, backup, rollback.
- [x] Vaultwarden: explicit security gate, HTTPS-only exposure, SQLite-consistent
  backup and two isolated restore proofs documented; owner onboarding/2FA/
  recovery remains an operational follow-up rather than a manual-coverage gap.
- [x] Portainer: explicit admin-surface gate, auth, backup, rollback.
- [x] Watchtower monitor-only: install, notifications, no automatic updates, rollback.
- [x] Local registry mirror: storage sizing, cache policy, backup/exclusion policy, rollback.
- [x] Node-RED: decision gate, credential secret handling, HA overlap, backup, rollback.

## Reference Completeness

- [x] Diagram library: replace stale exported/static diagrams with canonical Mermaid sources for architecture, install sequence, DNS/NTP, access, service placement, storage, and VentSys safety flow.
- [x] Rebuild state matrix: verify every phase maps
  blank/prepared/installed/configured/validated/live.
- [ ] Secrets ledger: add every router, HA, MQTT, Tailscale, Docker, OMV, app, camera, and printer placeholder.
- [x] Package matrix: every active `apt`/`opkg` install dependency plus the
  Garage Pi Python and Mermaid Viewer Node/npm build dependencies has install
  and verification coverage (2026-08-24 audit).
- [x] Command location legend: add UI-only contexts where no shell is used.
- [x] Version policy: volatile infrastructure, app, AI and client manuals now
  require official release lookup, immutable version recording and compatible
  data rollback before deployment (2026-08-24).
- [x] Decision gates: public exposure, password managers, camera bridges,
  low-code/agent automation, and automatic updates have explicit approvals and
  rollback requirements (2026-08-24).
- [ ] Service matrix: verify every planned app has host, port, URL, VLAN, Tailscale exposure, backup, monitoring, and runbook.
- [ ] ACL/access matrix: verify no undocumented path reaches Management, NVR, IoT, Printers, or Storage.
- [x] Local AI references: align CT 114 packages, firewall paths, monitoring checks and performance evidence.

## Current-State Annotations

- [x] Add current-state callouts for router first-flight deployed state.
- [x] Add current-state callouts for Proxmox, HAOS, Frigate base, docker-host, and Bambuddy live state.
- [x] Add current-state callout for OMV.
- [x] Add current-state callouts for cameras, Tier 1 apps, and VentSys hardware.
- [x] Add current-state callout for core HA tools: Mosquitto, ESPHome, Terminal & SSH, Studio Code Server/File Editor, and Companion App status.
- [x] Add canonical current-state callout for CT 114 after deployment.
- [x] Ensure current-state callouts never replace the fresh rebuild path
  (2026-08-09 phase-manual dry-read: callouts are separated from ordered fresh
  install/recovery steps).

## Sanity Checks

- [x] Run local Markdown link validation (2026-08-24: all 50 active install
  documents checked; zero broken local Markdown links).
- [x] Search for stale `Main/` paths (active docs clean; legacy `Main/` paths remain in `_archive/` historical files).
- [x] Search for stale Pi OS Lite NAS claims.
- [x] Search for Pi-hole-preferred claims.
- [x] Search for Google DNS fallback references.
- [x] Search for broad Tailscale/WireGuard storage subnet claims.
- [x] Search for unresolved placeholders outside approved examples (2026-08-24:
  52 active angle-bracket placeholders, all present in the secrets ledger;
  zero undocumented placeholders).
- [x] Confirm every command block has a `Run on:` label (2026-08-24: two newer
  omissions repaired; zero missing across active install docs, 66 PowerShell
  blocks parsed without errors and 311 shell blocks passed `bash -n`).
- [ ] Run router-deploy lint/compile after router config or router-deploy edits.
  - 2026-08-09 source audit: `validate-home-local-dns.ps1 -SkipLive` passed for
    48 aliases.
  - 2026-08-24 blocker revalidated with Windows `py -3`: lint, `first-flight`,
    and placeholder-tolerant `full`
    compile fail `architecture.docker_host_tailscale_egress_rule_present`;
    normal `full` compile also has unresolved WireGuard, device-MAC, and Wi-Fi
    placeholders. Do not deploy generated artifacts until both issues are fixed.

## Final Dry-Run

- [x] Start at [START-HERE.md](START-HERE.md).
- [x] Follow every phase link in order (2026-08-09: all 13 phase links and
  phase-local Markdown links resolve; sequence reviewed against the ownership
  and rebuild-state maps).
- [x] For each command, confirm the target machine and shell/user are obvious
  (2026-08-09 install-suite label and shell-language audit).
- [x] For each phase, confirm expected result and failure recovery are actionable
  (2026-08-09: all 13 phase manuals have a nearby expected-result contract for
  every shell/PowerShell block plus a bounded recovery/rehearsal path).
- [x] For each service, confirm deployment can be stopped before it becomes
  live (2026-08-24: `services/README.md` records the last safe stop and
  promotion evidence for all 23 service manuals).
- [x] Update this checklist with any missing steps found during the dry-run
  (router source blockers and live-only acceptance gates remain explicit).

2026-08-24 continuation result: the documentation structure, navigation,
placeholders and parsed command syntax pass. The suite-wide dry-read remains
open because the router-deploy architecture invariant still fails and the
manuals deliberately retain live/operator acceptance gates; a structural pass
is not a successful blank-hardware rebuild.
