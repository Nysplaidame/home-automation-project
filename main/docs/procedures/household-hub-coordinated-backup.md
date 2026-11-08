# Household Hub recurring coordinated checkpoint

## Prepared state — October 2, 2026

Source and isolated verification are complete; the script and units are **not
installed or enabled**. Read-only execution through `docker-host-lan` passed
against `/opt/stacks/household-hub`: API, web, PostgreSQL, Redis and Qdrant are
running, the three named-volume mappings/ownership labels match and the exact
OMV NFS export is mounted. No other running container uses these data volumes.
The worker container is absent. This check did not stop services or create a backup.

The existing September15 matched checkpoint/isolated restore remains the live
proof; see [[../../configs/docker-host/stacks/household-hub/README]]. Recurring
coverage and a restore of a generation made by this new job remain unproven.

## Source contract

- Script: [[../../configs/docker-host/system/household-hub-coordinated-backup.py]].
  Default invocation is read-only. `--execute` requires root, a nonblocking
  host lock and the exact mounted OMV export; a directory on the root disk fails.
- Units: [[../../configs/docker-host/system/household-hub-coordinated-backup.service]]
  and [[../../configs/docker-host/system/household-hub-coordinated-backup.timer]].
  The proposed 04:15 time is the Docker host's local timezone, subject to outage
  approval and conflict review. `Persistent=false` avoids a daytime catch-up outage.
- Ten isolated Linux tests cover stop/restart ordering, initially stopped worker,
  archive/stop/mount/health/restart failures, state-file flush failure, private
  permissions/checksums and a real tar/gzip round trip. These do not prove live
  Docker interruption or NFS durability under server failure.

The job records exact IDs, image IDs and original running states in protected
`original-state.json` before stopping anything. It stops web/worker/API first,
then stores, verifies stable project membership and stopped containers before
each store archive, and rejects forced/OOM store shutdowns. A concurrent deployment,
export writer or external process modifying volume files must be excluded by
the maintenance window; there is no lock shared with those processes.

It captures three cold volumes plus `.env`, `infra/docker` and
`data/obsidian-exports`. These archives contain credentials and personal data.
Directories are 0700; files 0600. No payload or inspect environment is logged.
It restarts the original running stores first, then original API/worker/web;
an absent or originally stopped worker stays absent/stopped. Store restart
failure keeps writers stopped. Other writer restarts are attempted even when
one fails. Docker healthchecks and internal API HTTP200 must pass where present;
Qdrant without a configured healthcheck is checked for running state only.
This is not full application/integration recovery certification.

Checksums are verified and files/directories flushed before a COMPLETE marker
and final timestamp-directory publication under
`/mnt/omv/docker-host-backups/household-hub-coordinated/`. Consumers must ignore
**every `.pending-*` directory**, even one containing COMPLETE after a failed
publication. No retention pruning, image rebuild, migration or Compose recreation
is performed. Full OS/app source/image recovery still needs the existing bundles.

## Maintenance-gated activation

Do not execute or enable these units outside an approved Hub outage window.
First verify backup free space, NFS health, host timezone/schedule conflicts,
source/image recovery availability and console access. Exclude deployments and
all external writes for the entire cold-copy interval. Large archives extend
the outage; no production duration has been measured for this script.

Copy reviewed source to a private staging directory on VM103, then install:

```sh
install -o root -g root -m 0750 household-hub-coordinated-backup.py /usr/local/sbin/household-hub-coordinated-backup.py
install -o root -g root -m 0644 household-hub-coordinated-backup.service /etc/systemd/system/
install -o root -g root -m 0644 household-hub-coordinated-backup.timer /etc/systemd/system/
systemd-analyze verify /etc/systemd/system/household-hub-coordinated-backup.service /etc/systemd/system/household-hub-coordinated-backup.timer
systemctl daemon-reload
/usr/local/sbin/household-hub-coordinated-backup.py
```

Only in the approved window, run the service manually before scheduling it:

```sh
systemctl start household-hub-coordinated-backup.service
systemctl status household-hub-coordinated-backup.service --no-pager
journalctl -u household-hub-coordinated-backup.service --no-pager -n 40
```

For the newly published timestamp directory, verify `COMPLETE`, run
`sha256sum -c SHA256SUMS` inside it and confirm all five original containers
and normal browser/API behavior. Prove an isolated restore using the existing
matched-store procedure before claiming recovery coverage. Confirm the approved
timer time and host timezone before `systemctl enable --now
household-hub-coordinated-backup.timer`; record the first scheduled result in
the service manual and live-state inventory. Scheduling is a separate acceptance
step, not part of source preparation.

## Failure and rollback

Ordinary errors and one TERM/INT/HUP attempt original-container resume. No
COMPLETE is published when copy, validation or restart fails. Protected pending
state is retained for diagnosis; never restore partial generations. The service
does not force-kill the process on stop, and has no overall start timeout;
archive subprocesses have individual timeouts. Investigate an unexpectedly long
run before stopping it. Repeated signals, SIGKILL, host loss or NFS hangs can
prevent cleanup: console access and manual recovery remain essential.

Disable the timer to prevent further interruptions:
`systemctl disable --now household-hub-coordinated-backup.timer`. This does not
stop an already running job. For manual recovery, read the private latest
pending `original-state.json`, inspect its recorded IDs/images and restart only
originally running containers in PostgreSQL/Redis/Qdrant then API/worker/web
order. If a store is unhealthy, keep writers stopped and follow the matched
restore procedure. Do not recreate containers or migrate schemas as a restart
shortcut. Remove installed units only after the job has exited and production
state is verified; preserve checkpoint generations and original-state evidence.
