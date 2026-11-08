# Bambuddy staged offline updates

The owner authorized scheduled Bambuddy updates and an internet-separated staging
area on 2026-10-02. This is a Bambuddy-only exception to intentional maintenance;
Watchtower remains monitor-only and other services retain their existing policy.

## Placement and schedule

- Windows task `Bambuddy Offline Release Staging`: daily 09:00 on the owner's
  workstation while Admin is signed in; missed staging runs catch up when
  available. It uses the existing Ubuntu WSL Docker engine and strict-host-key
  SSH alias `docker-host-lan`. No new SSH account or private key is installed.
- Workstation staging: `K:\Documents\home-automation-update-staging\bambuddy`.
  Transfer archives are outside the Obsidian vault. Docker save is streamed to
  Windows, avoiding WSL drive-cache assumptions.
- VM103 inbox: `/var/lib/home-automation-updates/bambuddy`, root-only. One pending
  image bundle at a time; partial transfers stay in `incoming/`, and only a
  verified bundle gets an atomic `ready.json` publication marker.
- VM103 timer `bambuddy-offline-update.timer`: daily at 04:30, 05:00, 05:30,
  06:00 and 06:30 **Europe/London**. A busy/unknown printer defers to the next
  window; no daytime catch-up after reboot. No bundle means no changes.
- NAS checkpoints: `/mnt/omv/docker-host-backups/bambuddy-updates/<UTC timestamp>`.
  Retain the last three successful update checkpoints. Failed checkpoints and
  failed migrated data remain for investigation and block automatic retry.

The workstation downloads the latest non-draft/non-prerelease GitHub release's
versioned `ghcr.io/maziggy/bambuddy:<version>` image for `linux/amd64`. Numeric
versions must increase within the installed major version; a major release needs
manual review. The bundle records release URL, upstream digest, source/config
image identities, archive size and SHA-256. Docker's engine formats can identify
images by manifest or config digest; the receiver accepts either recorded digest.
SSH protects the transfer; checksums detect corruption, not an independently
trusted publisher signature.

VM103 executes `docker load`, then `docker compose up -d --no-build --pull never`.
It never calls `docker pull`, GitHub, or a registry. No router/host firewall change
is part of this workflow. This provides an update path without granting VM103
registry egress; it does not claim all existing VM103 WAN exceptions are removed.

## Safety and recovery contract

Before stopping Bambuddy, require complete metrics for all configured printers:
connected, IDLE or FINISH, zero bed/nozzle targets, and an empty pending/printing
queue. Also read the queue database read-only and reject every nonterminal queue
status. Sample twice, 65 seconds apart (longer than Bambuddy's stale-MQTT timeout),
with the second check immediately before stopping. Disconnection, missing fields,
unknown states, PAUSE, FAILED, PREPARE and SLICING defer the update. No printer
control command or API credential is needed.

The NAS must be mounted as NFS and have at least 5 GiB free; VM103 must have
twice the image archive size plus 2 GiB free. Only a single-service Bambuddy stack
with the expected data/log bind mounts and an absent or updater-owned Compose
override is accepted. Preserve the running network mode, ports, protected `.env`
and original Compose; no bridge migration is included.

Save the prior image to NAS first. Stop Bambuddy gracefully and save `data/`,
`logs/`, `.env`, Compose and any prior override in protected `stack.tar`; check
SQLite integrity. Start the candidate against a copied database in a temporary
container with **network none**, no published ports and no restart policy. Verify
the candidate version and migrated-copy SQLite integrity, then remove the probe.
The candidate cannot reach production printers/MQTT/HA during this test.

Production receives an updater-owned `docker-compose.override.yml` with the exact
local staged tag and `pull_policy: never`. Require the expected running image,
application version, unchanged network mode and reconnection of the same printer
IDs. On candidate failure, stop it, preserve failed migrated data, restore the
matched old data/config checkpoint, and restart the old image offline. Never run
an old binary against potentially migrated candidate data. Block the failed
bundle until an operator investigates it. On success remove the transfer tar and
retain only current/previous updater-owned local image tags when unused; never
prune unrelated Docker images.

This is a practical quiet-window gate, not an atomic lock on a physical printer:
a print started directly from a slicer between the final sample and shutdown can
race it. Do not deliberately start prints during the update window. Bambuddy
monitoring/virtual-printer features are unavailable during checkpoint and probe.
There is no new phone-notification channel; status is in the system journal,
Windows staging log and updater receipt. Host shutdown/power loss can leave a
transaction marker; subsequent scheduled runs stop for operator recovery.

## Installation and verification

Sources:

- `scripts/maintenance/bambuddy-stage-update.py`
- `scripts/maintenance/install-bambuddy-staging-task.ps1`
- `scripts/maintenance/bambuddy-offline-update.py`
- `scripts/maintenance/test_bambuddy_offline_update.py`
- `configs/docker-host/system/bambuddy-offline-update.{service,timer}`

Install the receiver at `/usr/local/sbin/bambuddy-offline-update.py`, executable
mode0700, and units under `/etc/systemd/system/`, mode0644. Then run
`systemd-analyze verify`, `systemctl daemon-reload`, and
`systemctl enable --now bambuddy-offline-update.timer`. Register the Windows task
with `scripts/maintenance/install-bambuddy-staging-task.ps1`; it resolves the
installed Python executable and runs under the existing interactive user.

On Windows, check for a release or stage it manually:

```powershell
python main/scripts/maintenance/bambuddy-stage-update.py --check
python main/scripts/maintenance/bambuddy-stage-update.py
Get-ScheduledTaskInfo -TaskName 'Bambuddy Offline Release Staging'
```

Inside VM103:

```sh
/usr/local/sbin/bambuddy-offline-update.py --check
systemctl list-timers bambuddy-offline-update.timer
journalctl -u bambuddy-offline-update.service -n 40 --no-pager
cat /var/lib/home-automation-updates/bambuddy/last-result.json
```

`--check` verifies the bundle and current idle/queue gates without loading,
stopping or changing the service. An explicitly requested immediate update uses
`systemctl start bambuddy-offline-update.service`; the full gates still apply.
Staging failures return a nonzero Task Scheduler result and preserve diagnostics
in `stage.log` (rotated at1 MiB, one previous log). Local SSH access, workstation
internet, WSL Docker availability and user sign-in are staging dependencies.

Run the eight safety/rollback tests with Python3.13 on Linux from a disposable
directory containing the receiver and test file. They mock live service actions
and use temporary data; never attach a production Docker socket to a test app.

## Operator recovery

Disable both schedules before manual recovery. On Windows:

```powershell
Disable-ScheduledTask -TaskName 'Bambuddy Offline Release Staging'
```

On VM103:

```sh
systemctl disable --now bambuddy-offline-update.timer
systemctl status bambuddy-offline-update.service --no-pager
cat /var/lib/home-automation-updates/bambuddy/transaction.json
cat /var/lib/home-automation-updates/bambuddy/blocked.json
```

A missing marker is normal. Inspect the recorded checkpoint and ensure no updater
process remains. Confirm the printer is physically idle before stopping/recovering.
If `stack.tar` was never completed, the original stopped data is still the recovery
source: preserve it and restart the prior image. Do not extract an incomplete tar.
For a complete checkpoint, preserve the failed data/log directories, load
`previous-image.tar`, restore `stack.tar` into `/opt/stacks/bambuddy`, and set the
override image to the checkpoint manifest's exact `old_image` with pull_policy
never. Start only Bambuddy using `--no-build --pull never`. Verify old version,
SQLite and printer/MQTT reconnection before clearing transaction/block markers.
Retain failure evidence until its cause is resolved; release replacement or
discarding a failed pending bundle is a deliberate operator action. Re-enable
both schedules after recovery verification.

References: [Bambuddy Docker updates](https://wiki.bambuddy.cool/getting-started/docker/#updating),
[Docker image save](https://docs.docker.com/reference/cli/docker/image/save/),
[Docker image load](https://docs.docker.com/reference/cli/docker/image/load/).
