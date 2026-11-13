---
title: "OpenMediaVault NAS"
category: entity
tags: [storage, nas, omv, openmediavault, backups]
created: 2026-05-23
updated: 2026-10-27
sources: [project-readme, project-todo]
status: active
---

# OpenMediaVault NAS

**Type:** device/service - storage appliance
**Status:** Live on Storage VLAN 40
**Related:** [[entities/home-assistant]], [[entities/frigate]], [[entities/docker-host]], [[concepts/tailscale-remote-access]], [[concepts/wireguard-vpn]]

## Overview

**October27 current:** both data mirrors healthy. Print contents are at Y root,
Media contains migrated non-Print/service data; SMB mappings are Print/Media.
Scoped NFS exports and backup clients now use Media, including HA default
nas_backups and Proxmox omv-backups. Filebrowser shows both through a guarded
composite view. Owner access and fresh backup/isolated restore checks passed.
Verified retained originals/quarantines retired October27 23:19 GMT; about654GiB
freed on Y. Operational text references corrected; offline/native embedded links
remain a documented acceptance limit. Older
dated topology below is historical. Canonical [[../../../main/docs/reference/current-live-state]]
holds the operational details and acceptance limits.

OpenMediaVault is the project's live NAS at `192.168.40.50` on VLAN 40. It
provides storage shares for Home Assistant
backups, Frigate archive storage, Immich media, and configuration backups.

OMV is storage-focused. It is not the Docker app platform; app containers belong
on [[entities/docker-host]] under `/opt/stacks/<service>/`.

## Key Properties

- IP: `192.168.40.50`
- VLAN: 40 (Storage)
- Physical path: router `lan4`, untagged VLAN 40/PVID 40; owner confirmed
  2026-09-04. GS1900 port 8 is spare storage access. See
  [[../../../main/docs/reference/physical-port-and-cabling]].
- DNS names: `omv-nas.home.local`, `omv.home.local`, `nas.home.local`
- Shares: `ha-backups`, `frigate`, `immich`, `configs`
- Scoped media NFS exports to docker-host with qBittorrent
  `incoming/incomplete`, `incoming/complete`, and separate manual quarantine
- Windows `Y:` (`Print`) and `Z:` (`Media`) shares use `nasadmin`; named ACLs now
  give that account read/write access across both share trees, including
  `Media/study & work/Courses/New`. See
  [[../../../main/docs/reference/current-live-state]] for validation and rollback.
- Access: HA, Frigate, docker-host/Immich, and Management only
- Remote access: host route `192.168.40.50/32` via Tailscale; WireGuard fallback also host-only
- SMART: global 1,800-second polling; 5 C change and 55 C maximum alerts; all
  five physical disks monitored and `Good` at 33-44 C on 2026-07-29
- Vault backup: guarded dry-run helper exists for the `configs` share; no
  scheduled vault-backup task has been created
- Monitoring: Uptime Kuma web and NFS TCP `2049` checks are live, ntfy-enabled,
  and returned `Up` from VLAN 60 on 2026-07-29
- SMART heartbeat: aggregate `smartctl -H` service/timer and Kuma monitor 34
  are live; the narrow VM 102 host-firewall path accepted the first healthy
  heartbeat on 2026-07-29

- Desktop SSH: root key login via local alias `omv-lan` verified 2026-09-30; existing public key installed while preserving other entries. See [[../../../main/scripts/setup/nas/omv_nas_setup_guide]] for management access. Credentials remain outside the vault.

## Open Questions

- [ ] Run the first approved vault copy and restore-to-temporary-folder proof
  before creating any schedule.
- [ ] Continue monthly SMART health checks.

## Change Log

- 2026-10-21: reconciled new Media array and warm-copy stage from canonical
  audit/current-live-state. Targeted storage relationship lint confirms old
  shares remain live, one missing new-array member is intentional, and current
  md0 is not degraded. No raw sources changed.
- 2026-10-04 batch: prepared three guarded Flux queries and independent exact
  producer/timer input, with consolidated manual acceptance/rollback requirements.
  Nineteen synthetic cases (32 Flux executions) pass without bucket access.
  Current readings do not fall back to retained healthy data; observation age
  continues increasing between collections. Failed producer and no delivery
  remain separate signals, and inactive one-shot state does not certify success.
  OMV D-Bus permissions, delivery and Grafana UI/alerts remain unaccepted.
  [[../../../main/docs/procedures/omv-health-collector-preparation]]
- 2026-10-04: dedicated OMV-local Telegraf input prepared and five synthetic
  parser cases passed against the existing monitoring binary (Telegraf1.38.3).
  Exact labels/fields/values survive; stale/invalid/absent evidence does not
  export resource readings. A separate stdin-configured test process had no
  outputs or production configuration changes. OMV consumer deployment and
  authenticated delivery remain open under
  [[../../../main/docs/procedures/omv-health-collector-preparation]].
- 2026-10-04: local snapshot-to-Prometheus stdout adapter prepared;18 Linux
  tests pass across collector, publisher and adapter. Absent/invalid/stale
  snapshots emit explicit signals without resource readings; hashed identities
  and bounded labels avoid raw device/serial disclosure. Unknown readings stay
  unknown. No listener, integration or delivery was installed. Canonical contract:
  [[../../../main/docs/procedures/omv-health-collector-preparation]].
- 2026-10-04: atomic snapshot publisher and restricted service/timer templates
  are prepared;11 Linux tests and unit syntax checks pass. Group/device/
  capability/cadence acceptance, installation and metrics shipping remain open.
  Canonical scope: [[../../../main/docs/procedures/omv-health-collector-preparation]].

- 2026-10-02 evening: prepared host-local `omv-health/1.0` JSON collector passes
  six isolated tests and live one-off read-only collection. Five disks report
  SMART passed,30–42 C; lifetime CRC1 and a historical threshold flag remain
  warnings without new-fault inference. md0 has zero degraded members and idle
  sync, both expected data UUID mounts are observed and four daemons active.
  Stable identities are hashed; raw serials/WWNs omitted. No schedule, shipping,
  dashboard or NAS policy was deployed. Canonical contract:
  [[../../../main/docs/procedures/omv-health-collector-preparation]].

- 2026-10-02: Existing desktop key login and all five SMART health results
  passed. Disks were 30–47 C with no reported pending/offline-uncorrectable
  sectors; md0 `[UU]` had an existing consistency check running. This is no
  restore/self-test certification. Match stable disk identity before comparing
  CRC counters. Canonical evidence: [[../../../main/docs/audits/2026-10-02-roadmap-code-file-audit]].
- 2026-09-28: Recorded the full `nasadmin` SMB filesystem access on both mapped
  shares after OMV-side create/write/delete validation.
- 2026-09-04: Corrected attachment to router LAN4 from owner confirmation.
  The August switch-port-8 claim below is superseded; devices were unplugged
  during fibre installation and live availability was not retested.

- 2026-08-25: Recorded the live GS1900 port 8 attachment and corrected the
  SMART heartbeat from staged to live.
- 2026-08-01: Recorded the live OMV-backed qBittorrent staging/quarantine
  boundary and successful isolated config restore from the docker-host backup.
- 2026-07-29: Added the live OMV web/NFS Kuma checks after deploying the narrow
  monitoring-VLAN firewall path.
- 2026-07-29: Synced live VLAN/DNS/storage state, verified SMART monitoring on all five disks, and recorded the dry-run-only vault backup helper.
- 2026-05-23: Page created after project selected OMV over the old Raspberry Pi NAS direction.

- 2026-10-02 code remediation: live TransferPortal remains on the older helper
  without ROOT_POLICY; canonical source repairs are tested but undeployed.
  Root-owned files do not resolve its permissive helper behavior. Matched stopped
  checkpoint `20261002T211810Z` and no-NIC VM restore/preview/copy acceptance
  have now passed for saved and repaired generations. Historical rows and source
  hashes survived; disposable VM/media were removed. Live replacement remains open.
  [[../../../main/docs/audits/2026-10-02-code-audit-verification]]
