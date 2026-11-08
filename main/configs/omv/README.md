# OMV Rebuild Sources

This directory contains sanitized, rebuildable OMV state and host-side backup
automation. It must not contain a live `/etc/openmediavault/config.xml`, user
password hashes, private keys, or other host secrets.

**October27 live state supersedes older dated execution notes:** both data
mirrors healthy. Y maps Print with flattened root; Z maps Media. Immich/Frigate,
three backup exports and dormant configs/ha-backups binds use Media UUID
`a8843f98-c937-48a8-aefa-4cd0fb80667c`. All old physical backup exports retired.
HA nas_backups default and Proxmox omv-backups storage identity preserved.
Filebrowser uses guarded `/srv/filebrowser/{Print,Media}` composite, generated
Podman UID994:100/account/port preserved. Fresh backup/isolated restore checks
passed; see migration audit/current-live-state for exact proof and limits.
Retained originals/quarantines are private and not yet deleted.

- `nfs-exports.json` records the intended live NFS dataset/client/root-mapping
  contract after the 2026-07-11 F-011 remediation.
- `system/omv-config-backup.sh` creates a root-only live OMV configuration and
  export evidence set on the Media mirror.
- `system/omv-config-backup.service` and `.timer` run that backup daily.
- `system/omv-health-snapshot.py` is a prepared host-local JSON collector for
  load/memory, SMART, RAID, exact UUID mounts and selected daemon state. Six
  isolated tests and a live one-off read-only run pass; no schedule or metrics
  shipping is installed. See [[../../docs/procedures/omv-health-collector-preparation]].
- October4: `system/omv-health-publish.py` and snapshot service/timer templates
  prepare an atomic0640 file handoff for a dedicated consumer group. Eleven
  Linux tests and unit syntax checks pass; group/device/capability/cadence
  acceptance and all live installation/shipping remain open under that procedure.

- October4: `system/omv-health-metrics.py` prepares bounded snapshot conversion
  to Prometheus stdout with explicit absent/invalid/stale signals, stable disk
  labels and omitted unknown readings. All18 Linux tests pass; no listener,
  integration configuration or metrics delivery has been installed.

- October4: `system/omv-health-telegraf-input.conf` prepares the dedicated
  OMV-local exec input. `system/tests/verify_telegraf_metrics.py` passes five
  isolated parser cases against the monitoring binary (Telegraf1.38.3), with
  exact tag/field/value matching and no outputs or production configuration changes.

- October4 batch: `grafana/queries/` prepares current-state/freshness/unit queries;
  `system/omv-health-systemd-input.conf` prepares independent producer/timer
  observations. Nineteen synthetic Flux cases (32 executions) pass with no
  bucket access; current data cannot fall back to an older healthy generation.
  Manual least-privilege, authenticated delivery and dashboard acceptance/rollback
  remain open under the canonical procedure.

The full live backup contains sensitive OMV configuration and therefore stays
root-only on the unexported OMV path
`backups/configs/omv-config/runs/<timestamp>/`. The repository holds only this
sanitized contract and the reproducible backup mechanism.

The local md0 copy improves rebuild readiness but is not an independent or
off-site backup. That residual common-mode risk is owner-accepted.

## Print / Media transition — October21

**Current October25 state:** Z share is Media on new filesystem UUID
`a8843f98-c937-48a8-aefa-4cd0fb80667c`; five scoped media NFS exports replace
the broad `/export/media`. VM103 consumers switched and running; owner confirmed
application acceptance. Original Z was cleanly retired and its exact partition
serial `3GHV81YE` added as second Media member after full proof. Mirror is
rebuilding; md0/Y stays healthy and unchanged. No independent old-Z rollback
copy remains (owner-waived). Y warm copy is queued behind healthy mirror.
See the audit for exact evidence; earlier preparation states below are historical.

New Media RAID1 `/dev/md/media` (currently md127), MD UUID
`fd8de871:2fcb43a8:d97ff800:008ccb6b`, has only fourth-disk serial `3HG402GN`
partition1 and one intentionally missing slot. New ext4 filesystem UUID
`a8843f98-c937-48a8-aefa-4cd0fb80667c`, label Media, is registered/mounted
through OMV; mdadm/fstab/initramfs were deployed. Existing md0 and original Z
remain intact; current exports/backup paths above remain live until cutover.

Original-Z warm staging copy completed successfully October22 23:30 BST via
`household-storage-copy-z-20261021.service`, with private state under
`/root/household-storage-state-20261021/`. Do not add original Z until cold
copy/hash/layout and service verification pass. Follow
[[../../docs/audits/2026-10-20-storage-migration/README]] and
[[../../tools/storage-migration/cutover-runbook]]. No share/path switch yet.
October23 final-sync/hash runner is active under
`household-storage-cold-z-20261023.service`. Original Z and all bind aliases
are read-only; Filebrowser/TransferPortal are stopped/runtime-masked. VM103
media consumers are stopped and old NFS mount unmounted/runtime-masked. Exact
before-state and recovery evidence on each host is private under
`/root/household-storage-cold-z-20261023/`; do not restart writers until the
runbook's proof and mount gates pass.
