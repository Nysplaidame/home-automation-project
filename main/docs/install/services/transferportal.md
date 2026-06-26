---
title: OMV Transfer Portal Service
description: Native OMV-hosted transfer portal for guarded local disk-to-disk rsync jobs
tags: [omv, nas, rsync, transferportal]
created: 2026-06-25
modified: 2026-06-25
type: service-runbook
status: active
---

# OMV Transfer Portal Service

Transfer Portal is a native OpenMediaVault service for local NAS disk-to-disk
copy and move workflows. It is not Docker and not an OMV plugin yet.

Source artifacts live in `apps/transferportal/`.

Live status as of 2026-06-25: installed on `OMVNAS`, active on port `8088`,
and smoke-tested with disposable source/destination folders.

## Placement

| Item | Value |
|---|---|
| Host | `OMVNAS` |
| IP | `192.168.10.147` |
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

```bash
cd /root/transferportal
./packaging/install-native-omv.sh /root/transferportal
```

Then edit:

```bash
nano /etc/transferportal/transferportal.env
systemctl start transferportal
systemctl status transferportal --no-pager -l
```

## Safety Rules

- Do not run the web app as root.
- Keep `/etc/sudoers.d/transferportal` limited to the root helper path.
- Do not expose the UI beyond the OMV management interface in v1.
- Keep job commands as generated argument arrays.
- For move mode, require dry-run/preview, successful verification, portal-level
  source deletion permission, and explicit confirmation.

## Validation

```bash
systemctl status transferportal --no-pager -l
sudo -u transferportal sudo -n /usr/local/lib/transferportal/root-helper <<<'{"action":"list-mounts","params":{}}'
curl -I http://192.168.10.147:8088/
```

The live service unit must keep `NoNewPrivileges=false`, because the
unprivileged web app uses sudo to call the allowlisted root helper. The unit's
`ReadWritePaths` must include `/srv/transferportal` and `/etc/systemd/system`
so the helper can create bind-mount directories and mount units.

## Smoke Test Record

2026-06-25 disposable `smoke` portal:

- dry-run job completed with exit `0`
- copy job completed with exit `0`
- completed copy retry finished with exit `0`
- stop test marked the job `interrupted` with exit `-15`
- interrupted retry completed with exit `0`

## Rollback

```bash
systemctl stop transferportal
systemctl disable transferportal
rm -f /etc/systemd/system/transferportal.service
rm -f /etc/sudoers.d/transferportal
systemctl daemon-reload
```

Do not remove `/srv/transferportal/*` bind mounts or portal directories while
an rsync job is active.
