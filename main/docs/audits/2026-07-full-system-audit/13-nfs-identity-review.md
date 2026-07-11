---
title: July 2026 NFS Identity and Export Review
created: 2026-07-11
modified: 2026-07-11
type: audit-remediation-evidence
status: read-only-review-change-gated
---

# NFS Identity and Export Review

This record refines F-011 using read-only evidence gathered after the discovery
freeze. It does not authorize an OMV export, ACL, mount, or service change.

## Current advertised surface

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
| `/export` | Management subnet, docker-host, CT 111 and HA | No consumer should require the export root | Broad legacy candidate; retire only after OMV-side open-client and config review |
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

## Staged remediation order

1. Capture OMV rollback evidence: `/etc/openmediavault/config.xml`, generated
   exports, `exportfs -v`, relevant shared-folder UUIDs, bind mounts, filesystem
   ACLs, and the exact command/UI rollback owner.
2. Recheck live mounts from Proxmox, HA, docker-host and CT 111. Treat mountd
   registrations as hints, not proof of a currently mounted filesystem.
3. Retire only the clearly unused aliases, one at a time: direct `CCTV`, direct
   `immich-db`, `/export/ha-backups`, and the broad `/export` root. Re-run
   positive application checks and negative unauthorized-client checks after
   each change.
4. Pilot ordinary `root_squash` on `/export/frigate` while retaining the UID
   100000 ACL. Confirm new MP4 creation, Frigate health, retention deletion,
   playback, and lack of root-created files. Roll back immediately if any write
   path changes identity or fails.
5. Design dedicated identities for Proxmox, HA, Immich and docker-host backups.
   These are migrations, not flag flips, because current writes are root-owned
   or preserve multiple numeric owners.
6. Reconcile the two configs exports only after the vault/config backup producer
   is implemented or explicitly retired.

## Approval boundary

The next live action is an OMV configuration/export change and can interrupt
recording or backup writes. It requires an approved window, OMV administrative
access, saved rollback evidence, and a completed F-011 resilience test card.

