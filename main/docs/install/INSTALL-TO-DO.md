---
title: Installation Manual Suite To-Do
description: Companion checklist for completing and validating the fresh rebuild documentation suite
tags: [install, tasks, rebuild, documentation]
created: 2026-05-24
modified: 2026-05-27
type: task-list
status: active
---

# Installation Manual Suite To-Do

Use this checklist with [START-HERE.md](START-HERE.md). It tracks what remains
before the documentation suite is good enough to rebuild the system from zero
without live assistance.

## Completion standard

- [ ] A true beginner can identify the next document, target machine, user/shell context, command, expected result, and recovery path at every step.
- [ ] Every command block has a `Run on:` label immediately before it.
- [ ] Every placeholder used in a command appears in [secrets-placeholder-ledger.md](reference/secrets-placeholder-ledger.md).
- [ ] Every package or dependency appears in [package-dependency-matrix.md](reference/package-dependency-matrix.md).
- [ ] Every risky service has a decision gate before deployment.
- [ ] Every Tier 1-3 service has install, validation, backup, update, rollback, and troubleshooting coverage.
- [ ] The suite passes a dry-read from [START-HERE.md](START-HERE.md) through final validation.

## Phase Manual Expansion

- [ ] Phase 00 operator basics: add examples for hardware inventory, IP plan, MAC addresses, and secret placeholders.
- [x] Phase 01 router/OpenWrt: add full fresh-flash path, first-flight deploy path, full deploy path, router-local NTP validation, and lan5 recovery drill.
- [ ] Phase 02 Proxmox: add ISO verification, install checkpoints, storage layout choices, bridge/VLAN validation, and rollback notes.
- [ ] Phase 03 Home Assistant: add HAOS install, onboarding, add-on installs, MQTT setup, Companion App setup, router-derived time config, HACS decision gate, and backup validation.
- [ ] Phase 04 Frigate: add Debian base install, Docker install, Frigate compose, `.env` creation, camera placeholders, HTTPS requirement, and HA integration validation.
- [x] Phase 05 docker-host: add VM baseline, Docker official repository install, Compose policy, `/opt/stacks/<service>/` layout, Tailscale host-route setup, UFW rules, and rollback.
- [ ] Phase 06 OMV NAS: add OMV install, disk wipe warning, filesystems, users, NFS/SMB shares, SMART monitoring, and HA/Frigate/Immich storage mounts.
- [x] Phase 07 Tier 1 apps: add full command-by-command deploy order for AdGuard Home, Immich, Homepage, and Dozzle.
- [ ] Phase 08 Tier 2 apps: make every draft installable while keeping deployment approval gates explicit.
- [ ] Phase 09 Tier 3/evaluate apps: ensure Vaultwarden, Portainer, Watchtower, registry mirror, and Node-RED cannot be made live without security/backup approval.
- [ ] Phase 10 backups/monitoring/maintenance: add restore drills, maintenance windows, update policy, and alerting checks.
- [ ] Phase 11 physical integrations: add camera, printer, ESPHome, VentSys wiring, first-flash, adoption, and safety-test sequences.
- [ ] Phase 12 validation/troubleshooting: add an end-to-end acceptance test and one troubleshooting path per Tier 1 service.

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
- [ ] Paperless-ngx: install, scanner/import path, OCR dependencies, backup, retention, rollback.
- [ ] Mealie: install, users, backups, import/export, rollback.
- [x] ntfy: install, topic policy, public/private exposure decision, backup, rollback.
- [ ] Actual Budget: install, auth, backup/export, rollback.
- [ ] Scrypted: hardware/camera decision gate, install, storage, HA/Frigate overlap, rollback.
- [ ] Vaultwarden: explicit security gate, backup/encryption, exposure decision, restore test.
- [ ] Portainer: explicit admin-surface gate, auth, backup, rollback.
- [x] Watchtower monitor-only: install, notifications, no automatic updates, rollback.
- [ ] Local registry mirror: storage sizing, cache policy, backup/exclusion policy, rollback.
- [ ] Node-RED: decision gate, credential secret handling, HA overlap, backup, rollback.

## Reference Completeness

- [x] Diagram library: replace stale exported/static diagrams with canonical Mermaid sources for architecture, install sequence, DNS/NTP, access, service placement, storage, and VentSys safety flow.
- [ ] Rebuild state matrix: verify every phase maps blank/prepared/installed/configured/validated/live.
- [ ] Secrets ledger: add every router, HA, MQTT, Tailscale, Docker, OMV, app, camera, and printer placeholder.
- [ ] Package matrix: add every package used in command blocks with install and verification commands.
- [ ] Command location legend: add UI-only contexts where no shell is used.
- [ ] Version policy: mark volatile app docs that require official latest lookup before deployment.
- [ ] Decision gates: add final approvals for public exposure, password managers, camera bridges, low-code automation, and automatic updates.
- [ ] Service matrix: verify every planned app has host, port, URL, VLAN, Tailscale exposure, backup, monitoring, and runbook.
- [ ] ACL/access matrix: verify no undocumented path reaches Management, NVR, IoT, Printers, or Storage.

## Current-State Annotations

- [x] Add current-state callouts for router first-flight deployed state.
- [x] Add current-state callouts for Proxmox, HAOS, Frigate base, docker-host, and Bambuddy live state.
- [ ] Add current-state callouts for pending OMV, cameras, Tier 1 apps, and VentSys hardware.
- [ ] Add current-state callout for core HA tools: Mosquitto, ESPHome, Terminal & SSH, Studio Code Server/File Editor, and Companion App status.
- [ ] Ensure current-state callouts never replace the fresh rebuild path.

## Sanity Checks

- [ ] Run local Markdown link validation.
- [ ] Search for stale `Main/` paths.
- [ ] Search for stale Pi OS Lite NAS claims.
- [ ] Search for Pi-hole-preferred claims.
- [ ] Search for Google DNS fallback references.
- [ ] Search for broad Tailscale/WireGuard storage subnet claims.
- [ ] Search for unresolved placeholders outside approved examples.
- [ ] Confirm every command block has a `Run on:` label.
- [ ] Run router-deploy lint/compile after router config or router-deploy edits.

## Final Dry-Run

- [ ] Start at [START-HERE.md](START-HERE.md).
- [ ] Follow every phase link in order.
- [ ] For each command, confirm the target machine and shell/user are obvious.
- [ ] For each phase, confirm expected result and failure recovery are actionable.
- [ ] For each service, confirm deployment can be stopped before it becomes live.
- [ ] Update this checklist with any missing steps found during the dry-run.
