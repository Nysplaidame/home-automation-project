---
title: Installation Manual Suite - Start Here
description: Fresh-rebuild-first manual for replicating the home automation system without assistance
tags: [install, rebuild, runbook, beginner]
aliases: [Install Start Here, Rebuild Manual]
created: 2026-05-24
modified: 2026-05-25
type: install-guide
status: active
---

# Installation Manual Suite - Start Here

This is the canonical entrypoint for rebuilding the system from a blank environment.
It is written for a true beginner: each phase explains what you are building, where
commands run, what values you need, what success looks like, and where to go when
something fails.

Do not use this suite to deploy live changes casually. Treat every command block as
an intentional operation on a named machine.

## How to use this suite

1. Read the reference pages first.
2. Complete the phases in order.
3. Stop at every validation checklist until the expected result is true.
4. Use the current-state notes only to understand what has already been done in
   the existing project; the main path remains a fresh rebuild path.
5. Keep secrets out of Git. Record secret values in the password manager, not in
   this repository.

## Command location rule

Every command block must say where it runs. If a command block does not have a
`Run on:` line immediately before it, do not run it until the guide is fixed.

Use the location names in [command-location-legend.md](reference/command-location-legend.md).

## Reference pages

| Reference | Purpose |
|---|---|
| [INSTALL-TO-DO.md](INSTALL-TO-DO.md) | Companion checklist for finishing and validating the full manual suite |
| [manual-template.md](reference/manual-template.md) | Required structure for every phase and service manual |
| [command-location-legend.md](reference/command-location-legend.md) | Names each shell/UI context and how to recognize it |
| [rebuild-state-matrix.md](reference/rebuild-state-matrix.md) | Defines blank, prepared, installed, configured, validated, and live |
| [secrets-placeholder-ledger.md](reference/secrets-placeholder-ledger.md) | Central list of placeholders, where they are created, and where they are used |
| [package-dependency-matrix.md](reference/package-dependency-matrix.md) | Packages, hosts, purpose, install command, and verification command |
| [version-policy.md](reference/version-policy.md) | What is pinned, what uses latest lookup, and why |
| [decision-gates.md](reference/decision-gates.md) | Required approvals before risky or unresolved services become live |
| [Diagram library](../diagrams/README.md) | Canonical architecture, install-sequence, service-placement, DNS/NTP, storage, and VentSys diagrams |

## Sequential rebuild path

| Order | Phase | Manual | Deep-dive appendix |
|---|---|---|---|
| 0 | Operator basics, safety, hardware, network assumptions | [00-operator-basics.md](phases/00-operator-basics.md) | `README.md`, `bill-of-materials/` |
| 1 | Router/OpenWrt baseline | [01-router-openwrt.md](phases/01-router-openwrt.md) | `scripts/setup/router/` |
| 2 | Proxmox host and VM creation | [02-proxmox-host.md](phases/02-proxmox-host.md) | `scripts/setup/proxmox/proxmox_setup_guide.md` |
| 3 | Home Assistant baseline | [03-home-assistant.md](phases/03-home-assistant.md) | `scripts/setup/proxmox/ha_vm_setup_guide.md` |
| 4 | Frigate VM base | [04-frigate.md](phases/04-frigate.md) | `scripts/setup/proxmox/frigate_vm_setup_guide.md` |
| 5 | docker-host baseline and Tailscale | [05-docker-host.md](phases/05-docker-host.md) | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| 6 | OMV NAS storage | [06-omv-nas.md](phases/06-omv-nas.md) | `scripts/setup/nas/omv_nas_setup_guide.md` |
| 7 | Tier 1 docker-host apps | [07-tier1-apps.md](phases/07-tier1-apps.md) | [services/README.md](services/README.md) |
| 8 | Tier 2 app drafts | [08-tier2-apps.md](phases/08-tier2-apps.md) | [services/README.md](services/README.md) |
| 9 | Tier 3/evaluate app drafts | [09-tier3-evaluate.md](phases/09-tier3-evaluate.md) | [decision-gates.md](reference/decision-gates.md) |
| 10 | Backups, monitoring, maintenance, restore drills | [10-backups-monitoring-maintenance.md](phases/10-backups-monitoring-maintenance.md) | `scripts/backup/`, `docs/procedures/` |
| 11 | VentSys, printers, cameras, and physical integration | [11-physical-integrations.md](phases/11-physical-integrations.md) | `scripts/setup/ventsys/`, [diagram library](../diagrams/README.md) |
| 12 | End-to-end validation and troubleshooting | [12-validation-troubleshooting.md](phases/12-validation-troubleshooting.md) | `docs/troubleshooting/troubleshooting_reference.md` |

## Current project state callout

The existing live project is not blank. Router, Proxmox, Home Assistant, docker-host,
and Bambuddy have live state. OMV, Tier 1 services, most cameras, and much VentSys
hardware remain pending or planned. Use `TO-DO.md`, `PROJECT-INDEX.md`, the service
matrix, and handoff files to understand live state, but do not skip fresh rebuild
steps unless you have validated the equivalent state manually.

## Completion definition

The rebuild suite is complete when:

- Every phase reaches the `validated` state in the rebuild state matrix.
- Every service in `docs/reference/service-matrix.md` has an install path,
  validation path, backup note, and troubleshooting note.
- Every placeholder used in a command appears in the secrets placeholder ledger.
- Router validation passes after any router config edits.
- A beginner can start here, identify the next machine, run the next command,
  and know what success looks like without asking for context.
