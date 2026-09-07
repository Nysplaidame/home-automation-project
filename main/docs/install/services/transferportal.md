---
title: OMV Transfer Portal Service
description: Native OMV-hosted transfer portal for guarded local disk-to-disk rsync jobs
tags: [omv, nas, rsync, transferportal]
created: 2026-06-25
modified: 2026-09-05
type: service-runbook
status: active
---

# OMV Transfer Portal Service

Transfer Portal is a native OpenMediaVault service for guarded local NAS
disk-to-disk copy workflows. Move remains disabled until its verification and
separately confirmed source-deletion lifecycle is fully integrated. It is not
Docker and not an OMV plugin yet.

Source artifacts live in `apps/transferportal/`.

Live status as of 2026-06-25: installed on `OMVNAS`, active on port `8088`,
and smoke-tested with disposable source/destination folders. After the
2026-06-26 VLAN 40 migration, the service bind address should be
`192.168.40.50`.

Repository hardening prepared on 2026-09-05 is not live until explicitly
deployed and revalidated on OMV. Until that deployment, do not use destination
deletion, Retry, Move, or portal remapping on the live service.

## Placement

| Item | Value |
|---|---|
| Host | `OMVNAS` |
| IP | `192.168.40.50` |
| Service user | `transferportal` |
| App path | `/opt/transferportal` |
| Config | `/etc/transferportal/config.yaml` |
| State | `/var/lib/transferportal/jobs.sqlite` |
| Logs | `/var/log/transferportal/` |
| systemd unit | `transferportal.service` |
| Helper | `/usr/local/lib/transferportal/root-helper` |

## Install

Copy `apps/transferportal/` to a temporary path on OMV after the current manual
rsync transfer is finished or during a quiet window. The install script does not
stop existing rsync jobs, but avoid changing portal mounts while a transfer is
active.

Run on: OMV shell from the staged TransferPortal source directory.

```bash
cd /root/transferportal
./packaging/install-native-omv.sh /root/transferportal
```

Then edit:

Run on: OMV shell.

```bash
nano /etc/transferportal/transferportal.env
systemctl start transferportal
systemctl status transferportal --no-pager -l
```

## Safety Rules

- Do not run the web app as root.
- Keep `/etc/sudoers.d/transferportal` limited to the root helper path.
- Do not expose the UI beyond the OMV management interface in v1.
- Keep job commands as generated argument arrays. The root helper must accept
  only its compiled portal/log policy, allowlisted rsync arguments, exact portal
  endpoints, and currently mounted source/destination bind paths.
- Preview commands must contain `--dry-run` and cannot be promoted through
  Retry. Retry is limited to failed/interrupted jobs and rebuilds the command
  from the current portal policy.
- Destination deletion and `--inplace` remain disabled until the helper can
  enforce destructive permissions from a root-owned portal policy.
- Keep move mode disabled until dry-run verification, portal-level source
  deletion permission, and a separate post-copy confirmation are implemented.

## Validation

Run on: OMV shell.

```bash
systemctl status transferportal --no-pager -l
sudo -u transferportal sudo -n /usr/local/lib/transferportal/root-helper <<<'{"action":"list-mounts","params":{}}'
curl -I http://192.168.40.50:8088/
```

The live service unit must keep `NoNewPrivileges=false`, because the
unprivileged web app uses sudo to call the allowlisted root helper. The unit's
`ReadWritePaths` must include `/srv/transferportal` and `/etc/systemd/system`
so the helper can create bind-mount directories and mount units.

## Smoke Test Record

2026-06-25 disposable `smoke` portal:

- dry-run job completed with exit `0`
- copy job completed with exit `0`
- historical completed-copy retry finished with exit `0`; this behavior is now
  intentionally rejected because only failed/interrupted jobs are retryable
- stop test marked the job `interrupted` with exit `-15`
- interrupted retry completed with exit `0`

## Rollback

Run on: OMV shell.

```bash
systemctl stop transferportal
systemctl disable transferportal
rm -f /etc/systemd/system/transferportal.service
rm -f /etc/sudoers.d/transferportal
systemctl daemon-reload
```

Do not remove `/srv/transferportal/*` bind mounts or portal directories while
an rsync job is active.
