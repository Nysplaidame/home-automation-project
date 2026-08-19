---
title: OMV Configuration Backup Remediation
created: 2026-07-11
modified: 2026-07-11
type: audit-remediation-evidence
status: live-local-backup-proved
---

# OMV Configuration Backup Remediation

This record addresses the achievable local portion of F-009. It does not claim
an independent/off-site copy; that common-mode risk remains owner-accepted.

## Live implementation

- Script: `/usr/local/sbin/omv-config-backup`
- Unit: `/etc/systemd/system/omv-config-backup.service`
- Timer: `/etc/systemd/system/omv-config-backup.timer`
- Schedule: daily `01:30` with up to ten minutes randomized delay and
  `Persistent=true`
- Destination:
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/configs/omv-config`
- Permissions: root-only directory/run mode `0700`; evidence files `0600`
- Unit hardening: `NoNewPrivileges`, private `/tmp`, protected home/system, and
  a single bounded md0 write path

Each run captures the sensitive full OMV `config.xml`, generated/manual NFS
exports, fstab, effective exports, mount inventory, NFS service/share objects,
and shared-folder objects. The full output stays on OMV and is not committed.

## Proof

The first self-verifying run is
`runs/20260711T224614Z`. Its relative SHA-256 ledger passed for all ten captured
files. The initial run was rejected because its ledger recorded temporary
absolute paths; after the script was fixed and the valid run passed, only that
known-invalid first run was removed.

The deployed files have these SHA-256 values:

- script: `51f578a925a8b31ccee089a917326e9079045ee9d642ac67fd40b9d46b4f8218`
- service: `04eb24d9319311f2939838f6bc2583876df7b33abd7c78867335417ca6f5a18f`
- timer: `095ec5f5470b8de5ea0c181a4c882b217555c599f283fc79442e1c9bf6426299`

The service ended with `Result=success`, `ExecMainStatus=0`; the timer is active
and its first scheduled run is 2026-07-12 at approximately `01:30` BST.

## Rebuildable source

Sanitized source is under `configs/omv/`. `nfs-exports.json` records the live
dataset/client/root-mapping contract without credentials. The full OMV XML is
deliberately excluded from Git because it can contain account/security state.

