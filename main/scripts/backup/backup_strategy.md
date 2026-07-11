# Backup Strategy and Procedures
# Covers: Proxmox snapshots, HA backups, Frigate retention, config file backup, recovery

---

## Backup layers overview

| Layer | What | Where stored | Schedule | Retention |
|---|---|---|---|---|
| Proxmox VM backup | VM disks 100/102/103 | OMV md0 NFS `backups/proxmox` (`omv-backups`) | Daily 02:00 | 7 daily + 6 monthly |
| Proxmox LXC backup | CT 111/114 root filesystems | OMV md0 NFS `backups/proxmox` (`omv-backups`) | Daily 04:00 | 7 daily + 6 monthly |
| HA native backup | HA config, add-ons, automations | OMV md0 NFS `backups/home-assistant` | Daily 03:00 | 7 daily + 6 monthly |
| Frigate recordings | Camera footage | OMV md0 NFS `/export/frigate` through the Proxmox-host bind mount | Continuous | Frigate retention policy |
| Frigate LXC state | OS disk, DB, cache, compose/config | MINISFORUM NVMe on CT 111 | Continuous | Rebuildable + config-backed |
| Docker-host app data | Mealie, Grocy, LiveSync, GardenKeeper stack data/dumps | OMV md0 NFS `backups/docker-host` | Daily 03:45 | 14 days of timestamped runs plus `latest` |
| Config file backup | Safety vault YAML/configs | GitHub is current; preserved OMV `backups/configs` directory is not exported | Not implemented | Define a narrow producer/export before enabling |
| GitHub | Safety vault docs + configs | GitHub repo | On push | Full history |
| OMV host configuration | Sensitive OMV XML plus export/mount/share evidence | Root-only md0 `backups/configs/omv-config` | Daily 01:30 | Timestamped runs; local same-array protection only |

---

## Layer 1 — Proxmox VM snapshots

### Schedule (already configured per proxmox_setup_guide.md)

`Datacenter → Backup → Add`

| Field | Value |
|---|---|
| Storage | `omv-backups` (NFSv3 to OMV md0 `backups/proxmox`) |
| Schedule | `02:00` (daily) |
| Selection | VMs 100, 102, 103 |
| Mode | Snapshot |
| Compression | ZSTD |
| Retention | `keep-daily=7,keep-monthly=6` |
| Email | your@email.com (optional) |

The storage maps OMV md0 path
`/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox`
over NFS. There is no Proxmox SMB credential in the final path.

Historical pre-NAS check from 2026-05-27:

- Backup job was enabled for VMs `100,101,102,103`.
- Schedule was daily at `02:00`.
- Storage was `local`.
- Retention was `keep-last=2`.
- Latest 2026-05-27 logs for VMs `100`, `101`, `102`, and `103` all ended with
  `Finished Backup`.

Current policy after the 2026-06-26 NFS/md0 migration:

- 02:00 job: VMs `100,102,103`, `keep-daily=7,keep-monthly=6`, storage `omv-backups`.
- 04:00 job: CTs `111,114`, `keep-daily=7,keep-monthly=6`, storage
  `omv-backups`, `tmpdir=/var/tmp` so unprivileged LXC backup temp files stay
  on Proxmox local storage instead of the NFS dump directory.
- VM 101 and VM 104 are stopped rollback artefacts with migration snapshots;
  they are intentionally excluded from recurring backups.
- NFS TCP 2049 and storage pressure are checked by
  `home-automation-health-check.timer`.
- Fresh VM 102 and CT 114 archives completed on 2026-06-22 and passed `zstd -t`.
- On 2026-07-05, `omv-backups` was active and no longer capacity-constrained:
  `pvesm status` reported 54.21% used. Scheduled VM backups for 100/102/103
  completed that morning.
- VM 102 was restored under temporary ID 9102, had its NIC removed before boot,
  answered through QEMU Guest Agent, then was shut down and purged.
- Existing local archives remain until all fresh guest backups and retention
  observation are complete.
- The measured daily VM set is roughly 28-30 GiB, excluding LXC payload changes.
  The requested 7 daily + 6 monthly policy still fits comfortably at the
  2026-07-05 md0-backed capacity level. Keep Frigate/NVR recording retention
  conservative until the full camera set and OMV recording cutover are stable.
- The 2026-07-05 scheduled CT 111/114 backups failed before the `tmpdir` fix
  because unprivileged LXC backup could not enter the NFS-backed temp directory.
  Manual proofs with `--tmpdir /var/tmp` succeeded for both containers: CT 111
  produced a 23 GiB archive on 2026-07-05, and CT 114 produced a 15.30GB archive
  on 2026-07-06 in `00:23:30`.
- The CT 114 proof emitted Proxmox thin-pool warnings: autoextend protection is
  not enabled and summed thin volume sizes exceed pool capacity. This did not
  block the backup, but `local-lvm` pressure should stay on the monthly health
  checklist before major guest growth.
- Obsolete VM 101 recurring archives were removed on 2026-06-21 after CT backup
  validation; the stopped VM disk and migration snapshot remain available.

Restore-readiness drill on 2026-05-28:

- Confirmed latest `2026-05-28` archives exist for VMs `100`, `101`, `102`,
  and `103` in `/var/lib/vz/dump`.
- Ran `zstd -t` integrity checks on each latest archive (all passed).
- Confirmed each matching backup log includes `Finished Backup`.

### Manual snapshot before major changes

```bash
# In Proxmox shell before any risky change
vzdump 100 --mode snapshot --compress zstd --storage omv-backups
vzdump 111 --mode snapshot --compress zstd --storage omv-backups
vzdump 114 --mode snapshot --compress zstd --storage omv-backups
vzdump 102 --mode snapshot --compress zstd --storage omv-backups
vzdump 103 --mode snapshot --compress zstd --storage omv-backups
```

### Restore a VM or LXC

`Datacenter → Storage → omv-backups → Backups → select backup → Restore`

Or from shell:
```bash
# List available backups
ls /mnt/pve/omv-backups/dump/

# Restore VM 100 from backup
qmrestore /mnt/pve/omv-backups/dump/vzdump-qemu-100-*.vma.zst 100 --force

# Restore an LXC to its original ID only after stopping/removing a conflicting guest
pct restore 111 /mnt/pve/omv-backups/dump/vzdump-lxc-111-*.tar.zst
```

---

## Layer 2 — Home Assistant native backups

### Automatic backup to NAS

Configure in HA:
1. Add NAS as storage: `Settings → System → Storage → Add Network Storage`
   - Server: `192.168.40.50`, Protocol: NFS, Path: `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`
2. Set schedule: `Settings → System → Backups → Automatic Backups`
   - Schedule: Daily, Time: 03:00, Keep: 14, Location: NAS Backups

### Manual backup before HA updates

`Settings → System → Backups → Create Backup`

Name it with context, e.g. `pre-update-2026-03-07`.

### What is included in HA backups

- `/config/` — all YAML, packages, automations, scripts
- Add-on data (Mosquitto database, ESPHome configs, etc.)
- `.storage/` — entity registry, device registry, dashboards
- Secrets (encrypted in the backup)

### Restore HA from backup

`Settings → System → Backups → select backup → Restore`

Or if HA won't boot, use the recovery page at `http://192.168.20.101` (pre-login).

---

## Layer 3 — Frigate recordings

### Storage model

Use a hybrid layout:

- Keep CT 111 itself on the MINISFORUM NVMe.
- Keep Frigate's database, cache, and service state local to CT 111.
- Store recordings directly on the NAS once `/mnt/nas/frigate` is available.
- Treat `/opt/frigate/storage` as a staging/fallback path, not the long-term
  archive target.

Frigate manages its own retention automatically per `configs/frigate/config.yml`:
- **Motion segments:** kept 7 days
- **Event clips (objects detected):** kept 14 days
- **Snapshots:** kept 14 days

Recordings are stored at `/mnt/nas/frigate` (NAS) or `/opt/frigate/storage` (local fallback).

Why this split:

- NVMe is better reserved for VM disks, Frigate DB/cache, HA, docker-host, llm-host model data, and future VMs.
- The NAS has the right capacity profile for continuous video retention.
- Direct-to-NAS recording avoids the extra complexity of recording locally first
  and then archiving later.

### Check recording storage usage

```bash
# On frigate-nvr CT
df -h /mnt/nas/frigate
du -sh /mnt/nas/frigate/*
```

### Adjust retention

Edit `/opt/frigate/config/config.yml` `record.retain.days` and `record.events.retain.default`, then:
```bash
cd /opt/frigate && docker compose restart frigate
```

---

## Layer 4 — Config file backup (rsync to NAS)

The safety vault on your Windows machine is the authoritative source for all configs. Back it up to the NAS daily.

### Setup rsync from Windows to NAS

On your Windows machine, create a scheduled task or run manually:

```powershell
# PowerShell — rsync via WSL or use robocopy
# Option A: WSL rsync
wsl rsync -avz --delete \
    "/mnt/v/home-automation-safety/" \
    "admin@192.168.40.50:/mnt/nas/configs/home-automation-safety/"

# Option B: robocopy (native Windows)
robocopy "\\VBoxSvr\home-automation-safety" "\\192.168.40.50\nas-configs\home-automation-safety" \
    /MIR /Z /W:5 /LOG:"C:\Users\%USERNAME%\Desktop\backup.log"
```

### Setup automatic daily backup (Task Scheduler)

1. Open Task Scheduler → Create Basic Task
2. Name: `Safety Vault NAS Backup`
3. Trigger: Daily, 04:00
4. Action: Start a program → `robocopy.exe`
5. Arguments: `"\\VBoxSvr\home-automation-safety" "\\192.168.40.50\nas-configs\home-automation-safety" /MIR /Z`

---

## Layer 5 — Docker-host app data backup

Docker-host now carries household services whose data is not fully represented
by Proxmox VM backup alone during day-to-day restore work. The app-data backup
job is live and restore-smoked as of 2026-07-07.

Read-only checks on 2026-07-06:

- `/opt/stacks/mealie/data`: `15M`
- `/opt/stacks/grocy/config`: `4.2M`
- `/opt/stacks/obsidian-livesync/data`: `152K`
- `/opt/stacks/gardenkeeper/backups`: `36K`, with daily
  `gardenkeeper-postgres-*.sql.gz` dumps through 2026-07-06
- `findmnt` showed the existing Immich OMV mount at `/mnt/omv/immich`; no
  mounted `backups/docker-host` target was proven in this initial check.
- Proxmox `showmount -e 192.168.40.50` showed OMV exports
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host`
  to `192.168.20.102`.

Live proof on 2026-07-07:

- The live OpenWrt `Docker Host to OMV NFS` rule was added from the existing
  source intent, allowing docker-host `192.168.20.102` to OMV
  `192.168.40.50` ports `111`, `2049`, `20048`, and `32765-32767`.
- Docker-host now mounts
  `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host`
  at `/mnt/omv/docker-host-backups` with NFSv3.
- A write test to the mount succeeded.
- Dry-run completed without writing a real run directory.
- Real backup run `20260706T231304Z` wrote `20M` under `runs/` and updated
  `latest/` with Mealie, Grocy, Obsidian LiveSync, and GardenKeeper copies.
- Restore smoke copied `latest/` into `/tmp/docker-host-backup-restore-smoke-*`,
  verified `mealie.db`, `grocy.db`, LiveSync shard directory, and at least one
  GardenKeeper `gardenkeeper-postgres-*.sql.gz`, then removed the temp copy.
- `docker-host-app-data-backup.timer` is enabled and active, next firing daily
  at `03:45` local time.

Target OMV location:

- OMV md0 export/share: `backups/docker-host`
- Docker-host mount path: `/mnt/omv/docker-host-backups`

Repo-side deployment templates:

- `configs/docker-host/system/docker-host-app-data-backup.sh`
- `configs/docker-host/system/docker-host-app-data-backup.service`
- `configs/docker-host/system/docker-host-app-data-backup.timer`
- `scripts/backup/proxmox-lxc-backup-guard.sh` for Proxmox-host read-only
  audit and explicit stale LXC backup lock cleanup.

The script refuses to run unless `/mnt/omv/docker-host-backups` is a mounted
filesystem. Install it only during an approved docker-host maintenance/change
window because it adds a persistent NFS mount, installs a systemd timer, and
writes backup data to OMV.

Planned mount:

```fstab
192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host /mnt/omv/docker-host-backups nfs nfsvers=3,proto=tcp,_netdev,nofail,timeo=50,retrans=2 0 0
```

Approved live install sequence:

```sh
mkdir -p /mnt/omv/docker-host-backups
printf '%s\n' '192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host /mnt/omv/docker-host-backups nfs nfsvers=3,proto=tcp,_netdev,nofail,timeo=50,retrans=2 0 0' >> /etc/fstab
mount /mnt/omv/docker-host-backups
install -m 0755 docker-host-app-data-backup.sh /usr/local/sbin/docker-host-app-data-backup.sh
install -m 0644 docker-host-app-data-backup.service /etc/systemd/system/docker-host-app-data-backup.service
install -m 0644 docker-host-app-data-backup.timer /etc/systemd/system/docker-host-app-data-backup.timer
systemctl daemon-reload
DOCKER_HOST_APP_BACKUP_DRY_RUN=1 /usr/local/sbin/docker-host-app-data-backup.sh
/usr/local/sbin/docker-host-app-data-backup.sh
systemctl enable --now docker-host-app-data-backup.timer
systemctl list-timers docker-host-app-data-backup.timer
```

Do not append the fstab line twice. If the mount command fails, remove the new
line before rebooting docker-host.

Initial service paths:

| Service | Source path | Consistency note |
|---|---|---|
| Mealie | `/opt/stacks/mealie/data/` | SQLite app data; stop the container or use an app export before file-level backup/restore |
| Grocy | `/opt/stacks/grocy/config/` | Includes Grocy config and database; stop the container before file-level backup/restore |
| Obsidian LiveSync | `/opt/stacks/obsidian-livesync/data/` | CouchDB backend; synchronization is not a backup, and Git remains the project history layer |
| GardenKeeper | `/opt/stacks/gardenkeeper/backups/` | Local PostgreSQL dump timer output; restore from a selected compressed SQL dump |

Validation pattern:

```sh
# On docker-host, after confirming the OMV mount path
test -d /opt/stacks/mealie/data
test -d /opt/stacks/grocy/config
test -d /opt/stacks/obsidian-livesync/data
test -d /opt/stacks/gardenkeeper/backups
du -sh /opt/stacks/mealie/data /opt/stacks/grocy/config /opt/stacks/obsidian-livesync/data /opt/stacks/gardenkeeper/backups

# Dry-run before enabling a scheduled copy
rsync -aH --delete --dry-run /opt/stacks/mealie/data/ <omv-mount>/mealie/data/
rsync -aH --delete --dry-run /opt/stacks/grocy/config/ <omv-mount>/grocy/config/
rsync -aH --delete --dry-run /opt/stacks/obsidian-livesync/data/ <omv-mount>/obsidian-livesync/data/
rsync -aH --delete --dry-run /opt/stacks/gardenkeeper/backups/ <omv-mount>/gardenkeeper/backups/

# Template dry-run after installation
DOCKER_HOST_APP_BACKUP_DRY_RUN=1 /usr/local/sbin/docker-host-app-data-backup.sh
```

Restore smoke pattern:

1. Restore into a temporary directory first, not over the live stack.
2. Confirm expected database/config files exist and are non-zero.
3. For SQLite-backed services, stop the container before replacing the live
   data directory, then start it and check the local endpoint.
4. For CouchDB, prefer a clean container stop before file-level restore or use a
   CouchDB-native replication/export method if the live service is still
   running.

Completion criteria:

- [x] Live OpenWrt `Docker Host to OMV NFS` allow rule verified before retrying
  the mount.
- [x] OMV `backups/docker-host` mount path verified from docker-host.
- [x] Dry-run covers Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dump paths.
- [x] Scheduled job or timer enabled and logged.
- [x] One restore smoke test completed to a temporary directory.

---

## Proxmox LXC backup lock guard

Failed or interrupted LXC snapshot backups can leave Proxmox state that blocks a
later container start, especially stale `lock: snapshot-delete` entries or a
leftover `vzdump` snapshot marker. Do not clear these blindly: the lock may be
protecting an active backup/delete task.

Use this guard after any failed CT backup, before restarting CT 111/114 after a
backup failure, and during the monthly backup health check.

Read-only audit:

```sh
# On Proxmox host
sh scripts/backup/proxmox-lxc-backup-guard.sh
```

Approved cleanup, only if the audit shows no active `vzdump` or snapshot-delete
process:

```sh
# On Proxmox host, for the affected CT only
sh scripts/backup/proxmox-lxc-backup-guard.sh --apply 111
pct start 111
pct status 111
```

Guardrail policy:

- Never run `pct unlock` just because a guest is inconveniently locked.
- First check for active `vzdump`, `snapshot-delete`, `pct snapshot`,
  `pct delsnapshot`, `pct restore`, and related `lxc-usernsexec` processes.
- Only auto-handle known backup-related locks: `backup`, `snapshot`, and
  `snapshot-delete`.
- Treat any other lock as manual-review only.
- After cleanup, rerun the CT backup manually and confirm the log removed the
  temporary snapshot successfully before closing the incident.

---

## Layer 6 — GitHub (config version control)

> **G6 — Personal URL warning:** The repo URL below is specific to one account.
> Update it if you fork or move the project. Ensure `secrets.yaml` and any file
> containing passwords, API keys, or certificates are in `.gitignore` before
> pushing — they must never appear in a public repository.

The vault is already linked to GitHub (`github.com/Nysplaidame/home-automation-project`).

Push changes after any config edit session:

```bash
cd \\VBoxSvr\home-automation-safety
git add -A
git commit -m "Update: <brief description>"
git push
```

---

## Local NAS transfer portal

When you need to move data between two OMV-attached disks without using the
network, use the transfer portal pattern documented in
`scripts/setup/nas/omv_nas_setup_guide.md`.

The native OMV service implementation is tracked in `apps/transferportal/`;
its install and rollback runbook is `docs/install/services/transferportal.md`.
Keep any existing manual rsync job running until it completes unless the
operator explicitly asks to stop it.

### Operating rule

- Use bind-mounted portal paths such as `/srv/transferportal/source` and
  `/srv/transferportal/destination`.
- Run `rsync` on the OMV server itself so the data copy stays local.
- Treat the portal as a copy workflow, not a logical link workflow.

### Interruption behavior

- Already copied files remain on the destination.
- In-progress files are normally temporary until complete.
- Re-running `rsync` is the normal recovery path.
- For large files where preserving partial progress matters, use an explicit
  partial-file policy such as `--partial-dir=.rsync-partial`.

---

## Recovery runbook — MINISFORUM hardware failure

If the MINISFORUM host dies completely:

### Step 1 — Replace hardware and reinstall Proxmox

Any x86-64 machine with 8GB+ RAM and 128GB+ SSD will work.
Follow `scripts/setup/proxmox/proxmox_setup_guide.md` phases A–C.

### Step 2 — Restore VM backups from NAS

```bash
# Proxmox vzdump backups are stored on OMV md0 NFS storage `omv-backups`.
# Recreate the Proxmox storage entry during rebuild, confirm it mounts at
# /mnt/pve/omv-backups, then restore VMs and LXCs from the dump directory.

# Confirm NAS backup storage is mounted
pvesm status
ls -lh /mnt/pve/omv-backups/dump/

# Restore examples
qmrestore /mnt/pve/omv-backups/dump/vzdump-qemu-100-*.vma.zst 100
qmrestore /mnt/pve/omv-backups/dump/vzdump-qemu-102-*.vma.zst 102
qmrestore /mnt/pve/omv-backups/dump/vzdump-qemu-103-*.vma.zst 103
pct restore 111 /mnt/pve/omv-backups/dump/vzdump-lxc-111-*.tar.zst
pct restore 114 /mnt/pve/omv-backups/dump/vzdump-lxc-114-*.tar.zst

# --- If the original SSD is intact and you can attach it to the new machine ---
# Mount the old SSD's LVM only if you need a fallback archive or guest disk that
# predates the OMV-backed policy:
vgimportclone /dev/sdX     # import old volume group
lvs                         # list logical volumes

# --- If the SSD is unrecoverable ---
# Restore from `omv-backups` first. If the NAS backups are also unavailable,
# rebuild from the setup guides and restore HA from its native NAS backup in
# Step 3.
```

### Step 3 — Restore HA config from HA backup

If restoring HA from scratch:
1. Boot fresh HAOS on VM 100
2. Complete onboarding with the same admin credentials
3. `Settings → System → Backups → Upload Backup` → select the most recent `.tar` from the NAS

### Step 4 — Restore MAC addresses

New VMs will have new MAC addresses. Update:
- `configs/openwrt/dhcp-config.conf` — home-assistant and frigate-nvr host entries
- Follow the MAC update procedure in `scripts/setup/ventsys/esphome_adoption_guide.md`
  (get new MAC from `ip link show` on each VM, update dhcp-config.conf, then push
  the router config via the router setup guide)

### Step 5 — Verify VentSys devices

ESPHome devices on VLAN 50 will reconnect automatically once HA is back and the MQTT broker is up. Check the ESPHome add-on — all previously adopted devices should come back online within a few minutes.

---

## Backup health checklist (run monthly)

- [ ] Proxmox: verify recent VM and CT backups exist in `Datacenter → Storage → omv-backups → Backups`
- [ ] HA: open `Settings → System → Backups` — confirm most recent is < 25 hours old
- [ ] NAS from Proxmox: `df -h /mnt/pve/omv-backups` — confirm usage < 80%
- [ ] NAS: `smartctl -a /dev/sda` — confirm drive health is PASSED
- [ ] GitHub: `git log --oneline -5` — confirm recent pushes
- [ ] Test restore: verify backup integrity - `ls -lh /mnt/nas/ha-backups/*.tar` (confirm non-zero), then `tar -tzf \ | tail -10` (should list config files). Annual full restore drill on spare hardware is recommended.
