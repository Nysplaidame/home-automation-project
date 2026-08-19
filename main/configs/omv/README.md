# OMV Rebuild Sources

This directory contains sanitized, rebuildable OMV state and host-side backup
automation. It must not contain a live `/etc/openmediavault/config.xml`, user
password hashes, private keys, or other host secrets.

- `nfs-exports.json` records the intended live NFS dataset/client/root-mapping
  contract after the 2026-07-11 F-011 remediation.
- `system/omv-config-backup.sh` creates a root-only live OMV configuration and
  export evidence set on md0.
- `system/omv-config-backup.service` and `.timer` run that backup daily.

The full live backup contains sensitive OMV configuration and therefore stays
root-only on the unexported OMV path
`backups/configs/omv-config/runs/<timestamp>/`. The repository holds only this
sanitized contract and the reproducible backup mechanism.

The local md0 copy improves rebuild readiness but is not an independent or
off-site backup. That residual common-mode risk is owner-accepted.

