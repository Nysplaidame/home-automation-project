---
title: July 2026 NFS Identity and Export Review
created: 2026-07-11
modified: 2026-07-11
type: audit-remediation-evidence
status: first-remediation-pass-complete
---

# NFS Identity and Export Review

This record refines F-011 using evidence gathered after the discovery freeze
and records the approved first remediation pass completed on 2026-07-11.

## Executed outcome

- Rollback evidence and hashes are retained on OMV at
  `/root/omv-nfs-f011-20260711T223802Z`. It contains pre/post OMV `config.xml`,
  generated and manual exports, shared-folder/NFS objects, bind mounts, ACLs,
  mountd state, and SHA-256 ledgers.
- The manual export of the nonexistent md0 `CCTV` path was removed. Current
  Frigate recording storage remains `/export/frigate` through Proxmox.
- The unused direct md0 `backups/immich-db` export was removed after docker-host
  fstab, mounts, systemd and stack files showed no consumer. The directory and
  existing data were not deleted.
- The stale OMV-managed `/export/ha-backups` alias was removed. HA remains
  active and default on the direct md0 `backups/home-assistant` export.
- Both unused `/export/configs` client entries and the manual direct md0
  `backups/configs` export were removed. No active client mounted them and the
  planned vault/config backup producer has not been implemented. The underlying
  directory was preserved.
- CT 111's direct Frigate export was removed because the unprivileged CT cannot
  mount NFS. `/export/frigate` is now exported only to Proxmox
  `192.168.10.10`, with ordinary `root_squash` and the existing UID 100000 ACL.
- The root-denial probe failed with `Permission denied` as required. UID 100000
  created and removed a file successfully with resulting owner/group
  `100000:100`; CT 111 and Frigate stayed healthy.
- The remaining `/export` entries are OMV's read-only, root-squashed NFS
  pseudo-root for `/export/immich` and `/export/frigate`, not a writable broad
  dataset export.
- Final cross-client validation passed: estate health `26/26`, HA `nas_backups`
  active, Proxmox backup and Frigate mounts active, docker-host Immich and app
  backup mounts active, Immich HTTP 200/healthy, and the app-data timer active.

Remaining `no_root_squash` exports are narrowly client-restricted but not yet
least-privilege complete: Proxmox backups, HA backups, docker-host app backups,
and Immich media. Each has a proved root-owned or mixed-owner write contract
and requires a dedicated identity migration rather than an option-only change.

## Pre-change advertised surface

`showmount -e 192.168.40.50` from Proxmox advertised eleven paths on
2026-07-11:

| Advertised path | Allowed client(s) | Observed active/intended consumer | Disposition |
|---|---|---|---|
| md0 `CCTV` | CT 111 | None; current Frigate uses `/export/frigate` through Proxmox | Legacy candidate; retire after OMV config backup and final mount check |
| md0 `backups/immich-db` | docker-host | None; current Immich database dumps are inside `/export/immich/backups` and a fresh recovery dump also exists under docker-host backups | Legacy candidate; verify no timer references it, then retire |
| md0 `backups/configs` | Management subnet and HA | No scheduled writer proved; vault-to-NAS task remains open | Keep change-gated until the intended config-backup writer is defined |
| md0 `backups/docker-host` | docker-host | `/mnt/omv/docker-host-backups` | Keep |
| md0 `backups/home-assistant` | HA | HA mount `nas_backups`, active and default | Keep |
| md0 `backups/proxmox` | Proxmox | Proxmox storage `omv-backups` | Keep |
| `/export` | Management subnet, docker-host, CT 111 and HA | OMV-generated read-only NFS pseudo-root | Narrow automatically as child exports are removed; retain only for current managed children |
| `/export/configs` | Management subnet and HA | No current writer proved | Duplicate/alias candidate; reconcile with md0 `backups/configs` |
| `/export/immich` | docker-host | `/mnt/omv/immich`, bound into `immich_server` as `/data` | Keep |
| `/export/frigate` | Proxmox and CT 111 | Proxmox `/mnt/omv/frigate`, bind-mounted into unprivileged CT 111 | Keep; first root-squash candidate |
| `/export/ha-backups` | HA | HA previously registered this alias, but current `ha mounts info` uses the direct md0 path | Legacy candidate; retire after confirming the registration is stale |

The earlier OMV web-console observation of six configured shares and the eleven
paths advertised by `mountd` are not equivalent. The OMV configuration,
generated `/etc/exports`, bind-mount state, and live `exportfs -v` output must be
captured together before deleting an entry.

## Numeric identity evidence

| Dataset | Current client path | Observed writer/owner identity | Root-squash implication |
|---|---|---|---|
| Frigate recordings | Proxmox `/mnt/omv/frigate`, CT bind `/mnt/nas/frigate` | Recording directories are UID/GID `100000:100000`; top-level share is `0:100`, mode `2775` | Normal `root_squash` should leave UID 100000 writes intact. Preserve the existing UID 100000 ACL and test fresh segment creation before and after the change. |
| Proxmox archives | `/mnt/pve/omv-backups` | Archives are `0:100`, modes `0664`/`0644`; Proxmox writes as root | A direct switch to ordinary root squash is likely to break backup creation or ownership. Design a dedicated mapped backup identity first. |
| HA backups | HA `nas_backups` direct md0 path | HA reports an active read-write NFS backup mount; the client-side numeric writer is not exposed by `ha mounts info` | Treat as root-dependent until a controlled temporary-file identity test proves otherwise. Do not change during an automatic-backup window. |
| Immich media | docker-host `/mnt/omv/immich` -> container `/data` | Mount and sampled media tree are `0:0`; `immich_server` has no explicit container user | Root squash would map the current writer and is likely disruptive. Migrate to a dedicated numeric service identity or explicit anonymous mapping before enabling it. |
| Docker-host app backups | `/mnt/omv/docker-host-backups` | Backup root is `0:100`; preserved content includes `5984:5984`, `1000:1000`, and `0:0` | The root-run rsync job preserves heterogeneous ownership. Root squash requires a script/identity redesign and restore-semantics review first. |
| Config backups | No live scheduled mount/writer proved | Unknown | Define the producer and numeric identity before keeping or enabling this export. |

## Staged remediation order and disposition

1. **Completed.** Capture OMV rollback evidence: `/etc/openmediavault/config.xml`, generated
   exports, `exportfs -v`, relevant shared-folder UUIDs, bind mounts, filesystem
   ACLs, and the exact command/UI rollback owner.
2. **Completed.** Recheck live mounts from Proxmox, HA, docker-host and CT 111. Treat mountd
   registrations as hints, not proof of a currently mounted filesystem.
3. **Completed with correction.** Retire the clearly unused `CCTV`,
   `immich-db`, `/export/ha-backups`, and config exports one at a time. The
   read-only OMV pseudo-root remains only for active managed child exports.
4. **Completed.** Pilot ordinary `root_squash` on `/export/frigate` while retaining the UID
   100000 ACL. Confirm new MP4 creation, Frigate health, retention deletion,
   playback, and lack of root-created files. Roll back immediately if any write
   path changes identity or fails.
5. **Open.** Design dedicated identities for Proxmox, HA, Immich and docker-host backups.
   These are migrations, not flag flips, because current writes are root-owned
   or preserve multiple numeric owners.
6. **Closed for now.** The unused configs exports are retired. Recreate one
   narrow export only if a concrete vault/config backup producer is implemented.

## Approval boundary

Any further root-mapping work can interrupt production media or backups. Each
remaining dataset requires a dedicated service-identity design, application
backup proof, an approved window, and a dataset-specific rollback/test card.
