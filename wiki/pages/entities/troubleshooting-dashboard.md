---
title: "Troubleshooting Dashboard"
category: entity
tags: [software, troubleshooting, dashboard, docker-host, diagnostics]
created: 2026-08-25
updated: 2026-10-11
sources: [project-readme, project-todo, troubleshooting-reference]
status: active
---

# Troubleshooting Dashboard

**Type:** service - read-only diagnostic guide
**Status:** Live with owner-approved Homepage preview; Proxmox snapshot acceptance passed September15
**Related:** [[entities/docker-host]], [[entities/proxmox]],
[[entities/monitoring-vm]], [[entities/homepage]]

## Overview

The Troubleshooting Dashboard provides 37 read-only routes across network/access,
hosts/storage, home/devices, monitoring/maintenance and applications/data.
Search and collapsible categories lead to ordered checks with execution hosts,
expected observations and failure interpretation. It imports health JSON locally;
manual route evidence remains explicit. October11 adds separate Resource Health and bounded connection tests; imported evidence stays browser-local and no remediation is exposed. The original five walkthroughs and the
[[main/docs/troubleshooting/extended-app-routes|32 extended routes]] are available
offline when the dashboard host fails.

## Resource Health and interactive diagnostics

Homepage Monitoring now links to the live Resource Health section. The Proxmox
alert timer remains independent. A separate minute publisher sends sanitized
metrics through a source-restricted forced-command key to VM103; its VLAN policy
still blocks VM103→Proxmox SSH. An unprivileged Unix-socket API serves the
existing app without another VM, CT or listener. Samples older than five minutes
are stale. Incidents, coverage, queued delivery and collector failures are visible.

Named console commands and buttons provide ping, system DNS, listed TCP ports
and fixed HTTP health endpoints from VM103. Tests are bounded and rate-limited;
route TCP steps expose an explicit VM103 alternative. Reports can include live
summary and connection output, without changing imported route assessments.
TLS checks cover four HTTPS names and show strict verification separately from
legacy compatibility; the current Home Local CA lacks a required key-usage
extension. Nine cancellable bundles cover all37 investigations without changing
imported assessments. A bounded30-day/1,000-event timeline records monitor
transitions, notification acceptance, viewer freshness and requested-check
summaries. Notes/imports and full transcripts stay tab-local. Existing Grafana
resource/log dashboards open around±10minutes from an event. History starts at
deployment. Canonical runtime and rollback:
[[../../../main/apps/troubleshooting-dashboard/README]].

## Key Properties

- Route search includes commands, interpretations and exact errors; all search
  terms must match. `#route=<id>` links share the investigation only.
- September30 adds ten recurring-incident routes and corrects P1S guidance to
  the commissioned deployment and implicit FTPS990. Manual-only signals still
  require independent evidence; the route catalog does not probe services.

- Host: [[entities/docker-host]] VM 103 at `192.168.20.102`.
- Homepage URL: `https://homepage.home.local/portal-preview/troubleshooting/`
  under Tools > Troubleshooting, with Preview and Open tab.
- Direct management URL: `http://192.168.20.102:8094/`.
- Stack path: `/opt/stacks/troubleshooting-dashboard/`.
- Docker network: explicit `10.240.32.0/24` bridge.
- Access: the Homepage HTTPS path serves existing Homepage clients. Direct
  IPv4 publication is Management VLAN `192.168.10.0/24`
  only. September10 found a pre-existing IPv6 Tailscale RETURN rule requiring
  reconciliation before IPv6 publication; the current bridge has IPv6 disabled.
- Data sources: Windows `health_check.ps1 -Full -Json` and Proxmox-host
  `health_check.sh --json`.
- Missing or skipped evidence remains `Needs evidence`. The deployed September10
  update also requires timezone-qualified evidence within a 36-hour review
  window; stale, future or ambiguous timestamps cannot establish current health.
- Written offline companions in the canonical troubleshooting directory retain
  the original five investigations with Mermaid links, plus the extended guide; see [[sources/troubleshooting-reference]].

## Acceptance State

- August25 Windows snapshot passed 13/13; September10 fresh evidence has
  12 passes and one camera failure consistent with recorded disconnection.
- Desktop and mobile browser flows passed against the staged service.
- Container uses a read-only root filesystem, drops all capabilities before
  adding only Nginx's required identity capabilities, and enables
  `no-new-privileges`.
- Stop/start rollback removed the listener and network, failed closed, then
  recreated the service with the same access boundaries.
- Owner approved the [[entities/homepage]] card on 2026-09-11; no new DNS alias.

## Open Questions

- October2 read-only IPv6 inspection reconfirms the IPv4-only8094 listener and
  IPv6-disabled bridge. The live Tailscale RETURN/fallback DROP remain present,
  with zero counters at inspection. Failed Windows/monitoring IPv6 connections
  do not certify audience-path denial. Tested local source now stages explicit
  denial; live/persistent reconciliation stays maintenance-gated. Canonical
  procedure: [[../../../main/docs/procedures/troubleshooting-dashboard-ipv6-publication-guard]].

- [x] Authorize the workstation key on [[entities/proxmox]] and accept real
  mount/backup-age JSON through the dashboard browser flow (September15).
- [x] Owner-approved Homepage preview deployed on 2026-09-11.

## Change Log

- 2026-09-11: Expanded and deployed 27 searchable routes; 17 model tests and
  live desktop/mobile route checks passed. Offline guide generated from app
  definitions; no new live probes or remediation. Canonical app/handoff wins.

- 2026-09-10: Reconciled the deployed freshness update, Windows evidence,
  Proxmox collector/access gap and IPv6 discrepancy against the current
  handoff; linked the written troubleshooting companion through its source page.

- 2026-08-25: Staged live on management-only port `8094`; Windows snapshot,
  desktop/mobile flow, access-denial checks and rollback proof passed.

- 2026-09-11: Added VPN/client DNS comparison and SNI isolation guidance; Windows collector now distinguishes DNS, connection, TLS and timeout errors. Vault SNI route restored; workstation DNS choice remains open. See canonical portal handoff.

- 2026-09-12: Owner selected unchanged Mullvad public DNS/filtering with separate exact local hosts entries. Vault entry helper is prepared; live application needs Administrator PowerShell. See [[main/docs/decisions/04-dns-resolver-and-adblocking|DNS resolver decision]]. Direct router DNS probes remain separate evidence.

- 2026-09-14: Owner-installed Proxmox key works; fresh host snapshot passes all eight required capacity/mount/backup-age checks and dashboard model validation. Visual import remains open; freshness is not restore proof. Dedicated snapshot command installed; scheduled monitor preserved.

- 2026-09-15: Fresh Proxmox evidence passed required validator checks and real-file import through the live desktop/mobile browser smoke suite. Earlier file-picker acceptance gap is closed; archive integrity and isolated restore remain separate proof.
