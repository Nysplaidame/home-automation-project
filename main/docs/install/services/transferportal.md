---
title: OMV Transfer Portal Service
description: Native OMV-hosted transfer portal for guarded local disk-to-disk rsync jobs
tags: [omv, nas, rsync, transferportal]
created: 2026-06-25
modified: 2026-10-02
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

- October 2 source hardening removes the predictable development session secret.
  Startup now requires a non-empty secret of at least 32 characters from
  `/etc/transferportal/session.secret` or `TRANSFERPORTAL_SESSION_SECRET`.
  The native installer already generates the secret file. An empty existing
  file fails startup even if the environment has a secret; repair the configured
  file rather than hiding that fault. This source change is not deployed or a
  live-session credential rotation. Verify the file without printing its content
  before a bounded deployment; never reuse the test-only secret.
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

## Checkpoint, isolated restore and update

The Rollback section above retires the service; it is not data restoration.
Before an update, wait for every transfer to finish and verify no helper/rsync
process is still using a portal. Stop the web service only after this check.
Preserve a stopped copy of `jobs.sqlite` and any SQLite sidecars, `/etc/transferportal/`
including protected environment, logs, installed source revision, service unit,
root helper, sudoers policy and portal mount-unit definitions. Store the matched
checkpoint outside the OMV OS disk with permissions intact. Job history is not
backup of either transfer source or destination data.

Restore copies into a disposable VM with no production NAS mounts or routes.
Keep the service/helper disabled while checking SQLite integrity, schema and
configuration. Replace every portal path with a disposable source/destination;
do not restore production mount units or execute queued/retryable jobs. Install
the saved application/helper/policy together, then verify the read-only job
history and one disposable preview/copy. Confirm hashes and unchanged source;
Move/deletion remain disabled. Record job, checkpoint and policy generation.

Test the new generation in that VM before live maintenance, including schema
compatibility and helper denial behavior. If it fails, keep production unchanged.
For a failed live update, stop new requests after active transfers are resolved,
preserve failed state and restore the previous application/helper/policy plus
matching stopped database/config. Verify current mounts before restarting.
Never replay historical jobs to simulate recovery. Database rollback does not
undo a filesystem copy or deletion. September hardening deployment remains a
separate gate until its live acceptance is recorded.

See [backup flow](../../diagrams/storage/storage-and-backup-flow.mermaid) and
[access policy](../../diagrams/network/security-access-flow.mermaid).

## October 2 source hardening and live comparison

Read-only inspection confirms the live service is active and still imports an
older helper without ROOT_POLICY from its installed Python site-package. The
root-owned wrapper also lacks isolated import mode. Canonical source now adds
safe systemd path serialization, `python -I` helper execution, same-origin writes
and bounded login failures; 62 local tests pass (two symlink checks skipped).
These fixes and September policy hardening are **not deployed**. The checkpoint
and isolated restore/copy gate passed on October2 as recorded below. Root ownership
alone does not compensate for the older permissive helper.

For a reverse proxy that changes backend Host, set `TRANSFERPORTAL_ALLOWED_ORIGINS`
to the exact comma-separated browser origins, including scheme and explicit
port where applicable. Direct access uses its own request origin by default.
Originless write clients must be updated deliberately; never configure `*`.
The five-failure/300-second login throttle is in-memory per service process and
client address, so proxy clients may share a bucket. Existing HTTP transport
and password storage are separate migration tasks. Full evidence and remaining
gates: [[../../audits/2026-10-02-code-audit-verification]].

## Accepted recovery exercise — October2

Protected matched checkpoint `20261002T211810Z` is on the OMV data disk under
`backups/transferportal-checkpoints/20261002T211810Z/`. Archive SHA-256 is
`adc422398b6e183b4bf4966b7c552f4dff40560961030edf85c899eb4e49dea7`;
manifest and acceptance.json are beside it. Production was idle, briefly stopped
for capture and resumed. No application/policy generation was replaced.

A disposable no-NIC/no-route/no-NAS VM passed restore/integrity/history checks
for nine jobs and30 audit rows, real dry-run/copy with unchanged source and
matching destination hashes for saved and repaired generations, retained
destination extras, and repaired-helper denial checks. Production environment
and mount units were not activated; test configuration used fresh credentials
and a tmpfs fixture. The test corrected literal systemd path serialization and
verified spaces/percent/embedded quotes with real mounts. VM and transfer media
were removed; the checkpoint remains.

Recovery prerequisite is satisfied. Before later live maintenance, check idle
state again and take a fresh matched checkpoint if DB/config/source have changed.
Deploy app, installed Python package, isolated wrapper and policy together;
verify the effective import path and ROOT_POLICY, mounts, authentication, history
and bounded helper denial without modifying production transfer data. See
[[../../audits/2026-10-02-code-audit-verification|complete evidence and limits]].
