---
title: "Project Task List"
category: source
tags: [tasks, implementation, phases, todo]
created: 2026-04-07
updated: 2026-09-14
status: stable
---

# Source: Project Task List

**Original file:** `main/TO-DO.md`
**Date ingested:** 2026-04-07; refreshed against the canonical task list on 2026-09-05
**Type:** task list (living document)

## Summary

Full implementation task list organised across project phases and operational
next steps. The router, Proxmox, Home Assistant, docker-host, Tailscale,
monitoring stack, Tier 1 docker-host apps, ntfy, Watchtower monitor-only,
Grafana dashboards, and several exporters are live or pre-flight live. OMV,
Frigate and the household-service foundations are deployed; the cameras are
currently disconnected, while the P1S and VentSys hardware remain uncommissioned.

On 2026-09-05, the task list linked the proposed
[[household-workshop-operations-roadmap|Household, Workshop and Operations
Product Roadmap]]. It sequences read-only operational evidence, a daily
household view, diagnostics/recovery evidence, food workflows, workshop
inventory and VentSys commissioning while preserving the established owners of
live household and safety state.

## Key Takeaways

- **Documentation:** September10 adds written companions to the app's five
  investigations, Mermaid links and a shared media-service operating manual.
  Router/recovery/cabling instructions are reconciled; a complete sequential
  rebuild and remaining service/legacy-command verification are still open.

- **Physical integration:** The cameras are currently disconnected; P1S setup
  and VentSys hardware adoption remain open despite the live service foundations.
- **Operational follow-up:** Apply the HA monitoring Grafana/Kuma direct-link snippet through the HA UI
- **Operational follow-up:** Add the monitoring VM Tailscale host route and
  routed UFW allowances so mobile clients can reach Grafana and Uptime Kuma
- **Operational follow-up:** Approve/retest the monitoring VM host route in
  Tailscale admin if mobile clients still cannot reach Grafana/Kuma
- **Update governance:** Schedule a controlled docker-host patch window for Docker engine/component and kernel package candidates
- **Phase 3 (VentSys):** 17 ESP32 boards to flash and adopt in ESPHome; sensors still to be purchased
- **Phase 5 (CCTV):** Three ANNKE cameras were proven and are currently disconnected; fourth-camera selection and reconnection acceptance remain open.
- **Phase 6 (Security):** HA HTTPS is live. VM102/VM103 Fail2ban are confirmed active; CT114 APT access and its Fail2ban rollout remain open. Proxmox historical rollout and OMV status require current evidence.
- **Ongoing:** Monthly backup health check; update MAC addresses in DHCP config when hardware arrives
- ESPHome device YAMLs for all 17 boards exist in `configs/esphome/`; only flashing remains
- **Troubleshooting:** The read-only dashboard is staged on management-only
  port `8094`; real Proxmox backup-snapshot acceptance and any DNS/Homepage
  exposure remain open
- **Product roadmap:** Start with a versioned read-only evidence contract;
  daily household, workshop and physical-integration features follow their
  respective data and hardware acceptance gates.

## Entities Mentioned

[[entities/gl-mt6000]], [[entities/proxmox]], [[entities/home-assistant]], [[entities/frigate]], [[entities/bambuddy]], [[entities/ventsys]], [[entities/esphome]], [[entities/openmediavault-nas]], [[entities/troubleshooting-dashboard]]

## Concepts Mentioned

[[concepts/vlan-segmentation]], [[concepts/mqtt-tls]]

## Contradictions / Updates

The old April source summary is superseded by current canonical state. OMV and
Frigate service foundations are deployed, but their physical-camera and safety
hardware follow-ups remain explicitly gated.

## September7 reconciliation

The canonical audit refreshed reachable-host evidence and recovered missing branch sources. Watchtower is monitor-only but ntfy delivery fails; CT114 package access fails with stale June metadata. Proxmox guest backups and OMV SMART are not freshly verified because workstation SSH access is denied. The [[home-operations-workbench]] accepts saved Windows/Proxmox health JSON with freshness safeguards. Recovery tabletop documentation is paper review, not live-drill acceptance.

## September 10 second documentation pass

The canonical manuals now include download-gateway and Recomp lifecycle
procedures, expanded MediaMTX recovery, and explicit Household Hub source/
database-backup gaps. The troubleshooting reference removes public dashboard
token and password-in-command advice, distinguishes ping/listener/transport
failures, and names shell contexts. VM103/VM102 creation and pre-NAS return
checkpoints are explicit; validation is source-only, not live rebuild proof.

## September 11 service lifecycle review

Canonical ntfy, Watchtower, SearXNG and Whoogle manuals now cover update,
backup, isolated restore and rollback with Mermaid links. The SearXNG effective
settings/template recovery gap remains open. Watchtower's error40014 and phone
notification acceptance are unresolved; documented procedures are not live
restore proof. The canonical install checklist retains the remaining source/backup dependencies.

The next bounded dependency pass separated Phase07 blank credential generation
from restore and returned Phase08 monitoring/backup-timer acceptance to Phase10.
MediaMTX has a protected manual configuration checkpoint procedure; off-VM
capture and retention are still open. Hub's historical migration/dump evidence
is a recovery lead, not confirmation of current source or backup completeness.

Phase10 now documents backup-unit and Kuma-heartbeat setup, mandatory dataset
inventory and the non-atomic `latest` mirror. Recovery selects a completed dated
run. VM/CT restore checks stop on failure and require network isolation; these
are documentation corrections, not newly executed restore evidence.

The final-phase dependency review corrects Watchtower configuration backup
coverage and Phase11's obsolete live-camera claim. Uncommissioned hardware
checks remain deferred while independent software checks proceed; partial
acceptance does not certify the complete physical installation.

## Consolidated September 11 coverage audit

Canonical INSTALL-TO-DO now classifies 42 named operational/roadmap entries:
24 written lifecycle paths, nine requiring further review, three missing
source/configuration coverage, and six gated candidates. This is a planning
inventory, not a completeness percentage or certification. Bambuddy and
GardenKeeper are the next documentation reviews; Hub/SearXNG/MediaMTX recovery
artifacts and actual restore acceptance remain separate dependencies.

The subsequent nine-row review supersedes those initial counts: 32 Written,
0 Review, 4 missing source/configuration and 6 Candidates. GardenKeeper's
application/migrations are missing and its dump pipeline can mask upstream
failure; a checked manual checkpoint is documented, script repair is queued.
Existing VM103 SSH key access was denied during read-only source discovery.
No authentication or live deployment changed; recovery evidence remains open.

The later VM103 access check corrected that diagnosis: the raw-IP command did
not select the existing configured key. `docker-host-lan` succeeded, and the
workstation SSH configuration now applies the same identity to the IP address.
Both routes were verified with strict host-key checking; no server authentication
changed. Source provenance remains open, but VM103 SSH access is available.

Live source discovery then located both application trees. Read-only metadata
confirmed GardenKeeper0001–0029 and Hub20260809_0002. Canonical runbooks now
record GardenKeeper's destructive prototype resets and Hub's Alembic startup
behavior; no migrations ran. Missing source now refers to provenance/off-host
recovery artifacts, not absence of the live tree.

Protected off-VM source/settings checkpoints now exist on the administrator's
workstation and have matching hashes. They are scoped recovery copies, not full
application-data backups or proven builds. SearXNG semantic settings review and
source provenance remain open; secret-bearing files were kept outside the vault.

## September 14 recovery execution update

The four artifact/configuration gaps now have tested recovery contracts: the
GardenKeeper backup repair passed seven tests and live execution; all six
recovered source builds passed, both PostgreSQL/rebuilt-API restores passed,
and two Hub Qdrant snapshots restored. SearXNG settings were semantically verified.
MediaMTX config backup is scheduled and verified; owner retained manual recording
review with deletion disabled. Audit now36 Written/6 Candidates, with full-system
and remaining workflow proofs explicitly separate. See canonical handoff for paths.
