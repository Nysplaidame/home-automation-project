---
title: July 2026 Backup and Recovery Matrix
created: 2026-07-10
modified: 2026-07-10
type: audit-evidence
status: discovery-frozen
---

# Backup and Recovery Matrix

`Archive present` is deliberately different from `restore proved`. No isolated
restore was authorized during discovery, so every untested restore remains an
open recovery risk.

| Authoritative dataset | Current protection | Schedule / retention | Encryption / failure domain | Proved restore | Provisional RPO / RTO | Decision |
|---|---|---|---|---|---|---|
| Proxmox host configuration | Repository scripts/docs plus live `/etc/pve`; no dedicated export proved | None proved | Git remote and local host; secrets separate | No | Undefined / undefined | High gap |
| VM 100 HAOS | `vzdump` to OMV | 02:00; 7 daily + 6 monthly policy, 6 archives observed | NFS in same estate; encryption not proved | No | 24h / 4h target proposed | Archive current, restore unproved |
| VM 102 monitoring | `vzdump` to OMV | 02:00; policy as above, 7 archives observed | Same OMV and trust domain | No | 24h / 4h proposed | Archive current, app consistency unproved |
| VM 103 Docker host | `vzdump` to OMV | 02:00; policy as above, 6 archives observed | Same OMV and trust domain | No | 24h / 4h proposed | Archive current |
| CT 111 Frigate root/config/DB | `vzdump` to OMV; external NFS media excluded by design | 04:00; 4 archives observed | Same OMV; bind/NFS content separate | No | 24h / 4h proposed | Root archive current; media restore separate |
| CT 114 local AI | `vzdump` to OMV | 04:00; 4 archives observed | Same OMV and trust domain | No | 24h / 8h proposed | Archive current; large models slow recovery |
| HA settings/database/SSL | Native automatic backup to OMV | Daily 03:00; retain 14 | Location outside HA but same OMV; encryption state not proved | No | 24h / 2h proposed | Current but partial |
| HA apps/add-ons | VM backup only; excluded from native automatic backup | VM schedule only | Same OMV | No | 24h / 4h proposed | Documentation contradicts live selection |
| Mosquitto app data | VM backup only | VM schedule | Same OMV | No | 24h / 4h proposed | No app-level restore proof |
| ESPHome source and device secrets | Repository plus VM backup; live secrets ledger | Git plus VM schedule | Git history and Windows/local credentials | No | 24h / 8h proposed | Device recovery unproved |
| Frigate recordings | OMV RAID1 production storage; not an independent backup | Continuous with 7/14-day policy | Same md0, online and client-writable | No | Policy retention / 8h proposed | RAID is availability, not backup |
| Frigate config and SQLite DB | CT archive plus repository config | CT schedule | Same OMV | No | 24h / 4h proposed | Source/live detect drift unresolved |
| Camera configuration/firmware | Documentation only; no sanitized export proved | None | Physical device single copy | No | Undefined / undefined | High rebuild gap |
| Immich media | Intended OMV NFS; current mount failed | No separate backup proved | Production md0 only | No | Undefined / undefined | High data-loss gap |
| Immich PostgreSQL | Local Docker host; exported OMV path exists but is not mounted/used | VM backup only | Same VM plus OMV VM archive | No | 24h / 8h proposed | No database dump proof |
| Mealie | App-data export plus VM backup | 03:45 daily; retention from script | OMV online NFS, same trust domain | Prior smoke evidence exists; not rerun in this audit | 24h / 4h proposed | Current copy, independence missing |
| Grocy | App-data export plus VM backup | 03:45 daily | Same OMV | Prior smoke evidence; not rerun | 24h / 4h proposed | Current copy |
| Obsidian LiveSync/CouchDB | App-data export plus VM backup | 03:45 daily | Same OMV | Prior smoke evidence; not rerun | 24h / 4h proposed | Current copy |
| GardenKeeper PostgreSQL/app data | Daily dump plus app-data export and VM backup | Daily around app backup | Same OMV | Prior smoke evidence; not rerun | 24h / 4h proposed | Current but live source lacks Git provenance |
| Household Hub PostgreSQL | VM backup only | VM schedule | Same VM/OMV domain | No | 24h / 8h proposed | Missing app-data export and source provenance |
| Household Hub Qdrant/Redis | VM backup only | VM schedule | Same VM/OMV domain | No | 24h / 8h proposed | Missing service-level backup |
| Bambuddy state | VM backup only | VM schedule | Same VM/OMV domain | No | 24h / 8h proposed | Missing canonical stack and serial placeholder |
| Monitoring Influx/Grafana/Kuma | VM 102 backup; old manual Kuma DB copies | VM schedule; old manual copies stop in June | Same OMV | No | 24h / 8h proposed | No app-consistent current exports |
| OpenWrt configuration | Canonical source approximates intent; no live sysupgrade backup found | Git only | Git remote; live-only drift not captured safely | No | Undefined / undefined | High source/live gap |
| Managed-switch configuration | No authenticated export proved | None | Device only | No | Undefined / undefined | Critical rebuild blocker for VLAN/PoE |
| OMV configuration | Live `/etc/openmediavault/config.xml`; exported configs directory empty | None proved | OMV host only | No | Undefined / undefined | High rebuild gap |
| OMV md0 data | RAID1 only plus selected VM/app archives on same array | Continuous/scheduled | Same chassis, controller, power, ACL and ransomware domain | No | Dataset-specific / undefined | No independent copy |
| Certificates and CA | Repository procedures plus Windows and live copies; private-key handling not fully mapped | Manual long-lived validity | Multiple hosts; revocation unavailable/unproved | No | Undefined / 8h proposed | Inventory exists, recovery/rotation unproved |
| Git repository | Remote `main` matched baseline commit | On push | Remote external failure domain; repository contains historic secret | Clone implicit, not tested here | Last push / 2h proposed | Available but requires secret-history cleanup decision |
| Windows credential vault | Local Windows credential store | OS/profile dependent | Independent copy/recovery not proved | No | Undefined / undefined | Access continuity gap |
| Physical BOM/wiring/calibration | Repository docs only | On edit | Git remote | No physical acceptance | Design-only / undefined | Blocked until hardware exists |

## Schedule and consistency risks

- VM backups begin at 02:00, HA native backup at 03:00, docker app-data at
  03:45, and CT backups at 04:00. The latter two can overlap on OMV and on
  application disks.
- `vzdump` completion proves archive creation, not database application
  consistency or restorable application identity.
- CT bind/NFS mount content is not necessarily included in container archives;
  Proxmox documents that bind/device mount content requires separate protection.
- Online NFS targets with `sec=sys` and `no_root_squash` remain inside the
  production/ransomware blast radius.
- CT 111 capacity pressure and VM/CT temporary work can turn backup jobs into a
  service-availability or space-exhaustion event.

## Required restore proofs

### Completed archive-stream gate

On 2026-07-10, the newest 2026-07-09 archive for each active guest (VMs
100/102/103 and CTs 111/114) passed a low-priority `zstd -t` stream check. The
fail-fast sequential loop reached CT 114, proving the first four checks; CT 114
was then repeated with captured `rc=0` in 101 seconds because the first wrapper
timed out after losing its output channel. No temporary process remained.

This validates compressed-frame integrity only. It does not validate VMA/tar
contents, guest configuration, databases, external bind/NFS data, bootability,
application identity, or RTO.

### Still required

The original correctness contract called for one isolated VM and CT restore,
HA plus app recovery, SQLite/PostgreSQL/CouchDB recovery, media-metadata proof,
and reconstruction of OpenWrt/OMV/switch configuration. The operator has
confirmed that isolated restores and an off-site/independent copy are not
possible with available resources. Those gates are therefore owner-accepted
residual risks, not pending actions and not passes.

Achievable remediation is limited to keeping local jobs current and monitored,
retaining the passed archive-stream checks, improving app-native/config copies,
documenting rebuild steps, reducing online backup write exposure, and avoiding
schedule/capacity failures. See `12-owner-decisions.md`.
