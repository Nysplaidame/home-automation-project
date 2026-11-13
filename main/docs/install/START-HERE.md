---
title: Installation Manual Suite - Start Here
description: Fresh-rebuild-first manual for replicating the home automation system without assistance
tags: [install, rebuild, runbook, beginner]
aliases: [Install Start Here, Rebuild Manual]
created: 2026-05-24
modified: 2026-09-14
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

The [consolidated coverage audit](INSTALL-TO-DO.md#consolidated-coverage-audit--september-11) tracks all 42 named service/roadmap
entries: 36 now have written lifecycle paths and six remain gated candidates.
The four source/configuration gaps have tested recovery artifacts or configuration
contracts as of September14; individual workflow and full-system proof remain open.
Written coverage is not verified rebuild or current restore acceptance.

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
| [garage-pi-desktop-setup-guide.md](garage-pi-desktop-setup-guide.md) | Optional garage Raspberry Pi desktop/operator station, OLED display, project access, and experimental AI readiness |
| [oled-screen-setup-guide.md](oled-screen-setup-guide.md) | Detailed OLED status display setup used by the garage Pi case |
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
| 4 | Frigate LXC baseline | [04-frigate.md](phases/04-frigate.md) | `scripts/setup/proxmox/frigate_vm_setup_guide.md` |
| 5 | docker-host baseline and Tailscale | [05-docker-host.md](phases/05-docker-host.md) | `scripts/setup/proxmox/docker_host_setup_guide.md` |
| 5A | Optional local AI inference | [05a-local-ai.md](phases/05a-local-ai.md) | `scripts/setup/proxmox/llm_host_setup_guide.md`, `docs/procedures/local_ai_performance_testing.md` |
| 6 | OMV NAS storage | [06-omv-nas.md](phases/06-omv-nas.md) | `scripts/setup/nas/omv_nas_setup_guide.md` |
| 7 | Tier 1 docker-host apps | [07-tier1-apps.md](phases/07-tier1-apps.md) | [services/README.md](services/README.md) |
| 8 | Tier 2 apps | [08-tier2-apps.md](phases/08-tier2-apps.md) | [services/README.md](services/README.md) |
| 9 | Tier 3/evaluate app drafts | [09-tier3-evaluate.md](phases/09-tier3-evaluate.md) | [decision-gates.md](reference/decision-gates.md) |
| 10 | Backups, monitoring, maintenance, restore drills | [10-backups-monitoring-maintenance.md](phases/10-backups-monitoring-maintenance.md) | `scripts/backup/`, `docs/procedures/` |
| 11 | VentSys, printers, cameras, and physical integration | [11-physical-integrations.md](phases/11-physical-integrations.md) | `scripts/setup/ventsys/`, [diagram library](../diagrams/README.md) |
| 12 | End-to-end validation and troubleshooting | [12-validation-troubleshooting.md](phases/12-validation-troubleshooting.md) | `docs/troubleshooting/troubleshooting_reference.md` |

## Return checkpoints during a blank rebuild

Some phases establish a service before its storage or physical dependencies
exist. Record the foundation as configured and the dependent checks as deferred;
return to them when the prerequisite is ready. Do not treat a deferred check
as passed or invent a temporary production dependency to satisfy it.

| Initial phase | Foundation to establish | Return after |
|---|---|---|
| 02 Proxmox | Host, tagged management, storage and guest creation plan; a blank host need not already contain later guests | Each guest's own phase creates and validates it |
| 04 Frigate | CT111, shared GPU, no-camera baseline | Phase06 for OMV recording mount; Phase10 for archive/restore; physical camera reconnection for stream/playback proof |
| 05 docker-host | Create VM103 through the linked cloud-image steps, then install Debian dependencies, Docker and access policy | Phase06/10 for NAS archive and restore proof |
| 05A local AI | CT114 and model/voice service baseline | Phase06/10 for off-host archive and isolated restore |
| 09 Tier3 foundations | Preserve Vaultwarden data and Watchtower configuration separately | Phase10 job installation/heartbeat and isolated restore acceptance |
| 11 physical integration | Record disconnected/uncommissioned devices explicitly; perform only authorized connected-device tests | Hardware commissioning; independent Phase12 software checks can proceed |
| 07/08 app foundations | Prepare services with manual checkpoints; preserve existing credentials on recovery | Phase10 for recurring backup timer, VM102 monitors, alert delivery and promotion evidence |
| 10 monitoring/backups | Create VM102 using the linked monitoring appendix before testing its stack | Service and physical commissioning for functional monitors and alert delivery |

## Current project state callout

The existing project is not blank. Use [Current Live State](../reference/current-live-state.md)
for dated deployment evidence and remaining acceptance gaps. The September
baseline uses untagged Zen PPPoE on `eth1`, eleven network segments including
Hive/cloud IoT on LAN2/VLAN55, Proxmox directly on the LAN1 trunk, and OMV
directly on LAN4/VLAN40. The Zyxel and three cameras are deliberately
disconnected; P1S is uncommissioned and VentSys hardware acceptance is pending.
Service reachability does not establish household onboarding or restore proof.

Follow the [physical cabling map](../reference/physical-port-and-cabling.md)
and [Mermaid topology](../diagrams/network/physical-port-and-cabling.mermaid),
not older handoff layouts. Do not skip fresh rebuild steps without validating
the equivalent state. For an incident, start with the
[written diagnostic walkthroughs](../troubleshooting/diagnostic-walkthroughs.md)
or the [cross-system reference](../troubleshooting/troubleshooting_reference.md).
These remain usable when the troubleshooting app or its host is unavailable.

## Documentation dry-read status

The 2026-08-24 continuation pass resolved all local install-document links,
command-location labels and placeholder-ledger references. All 311 active shell
blocks pass `bash -n`, and all 66 PowerShell blocks parse. Mealie, Grocy and
Obsidian LiveSync now have explicit operator, isolated-restore and rollback
paths; the service index records the last safe pre-live stop for every service.

This is not yet a complete blank-hardware dry run. September recovery records
supersede the August Tailscale-invariant blocker: source lint and compiler
regression tests pass. Both deployment profiles require real PPPoE credentials;
full deployment also needs the remaining real WireGuard, device-MAC and Wi-Fi
inputs. A placeholder-tolerant preview is never a deployment artifact. Follow
[Phase 12](phases/12-validation-troubleshooting.md) for current acceptance rules.

The 2026-09-10 documentation continuation reconciles the network/recovery
instructions and provides written companions to all five app investigations,
with Mermaid links. It is a source review, not a new live health check or
completed rebuild. Remaining work stays in [INSTALL-TO-DO.md](INSTALL-TO-DO.md).

## Completion definition

The rebuild suite is complete when:

- Every phase reaches the `validated` state in the rebuild state matrix.
- Every service in `docs/reference/service-matrix.md` has an install path,
  validation path, backup note, and troubleshooting note.
- Every placeholder used in a command appears in the secrets placeholder ledger.
- Router validation passes after any router config edits.
- A beginner can start here, identify the next machine, run the next command,
  and know what success looks like without asking for context.
