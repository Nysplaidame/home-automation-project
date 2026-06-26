# Backup Strategy and Procedures
# Covers: Proxmox snapshots, HA backups, Frigate retention, config file backup, recovery

---

## Backup layers overview

| Layer | What | Where stored | Schedule | Retention |
|---|---|---|---|---|
| Proxmox VM backup | VM disks 100/102/103 | OMV `New/proxmox-backups` (`smb-backup-new`) | Daily 02:00 | 7 generations |
| Proxmox LXC backup | CT 111/114 root filesystems | OMV `New/proxmox-backups` (`smb-backup-new`) | Daily 04:00 | 7 generations |
| HA native backup | HA config, add-ons, automations | HA local + NAS | Daily 03:00 | 14 days on NAS |
| Frigate recordings | Camera footage | NAS `/mnt/nas/frigate` | Continuous | 7 days motion, 14 days events |
| Frigate LXC state | OS disk, DB, cache, compose/config | MINISFORUM NVMe on CT 111 | Continuous | Rebuildable + config-backed |
| Config file backup | Safety vault YAML/configs | NAS /mnt/nas/configs | Daily via rsync | 30 days |
| GitHub | Safety vault docs + configs | GitHub repo | On push | Full history |

---

## Layer 1 — Proxmox VM snapshots

### Schedule (already configured per proxmox_setup_guide.md)

`Datacenter → Backup → Add`

| Field | Value |
|---|---|
| Storage | `smb-backup-new` (SMB 3.1.1 with sealing required) |
| Schedule | `02:00` (daily) |
| Selection | VMs 100, 102, 103 |
| Mode | Snapshot |
| Compression | ZSTD |
| Max backups | 7 generations |
| Email | your@email.com (optional) |

The storage maps OMV share `New`, subdirectory `proxmox-backups`. Proxmox keeps
the credential in its protected storage configuration; it must never be copied
into this repository or command examples.

Current pre-NAS check on 2026-05-27:

- Backup job is enabled for VMs `100,101,102,103`.
- Schedule is daily at `02:00`.
- Storage is `local`.
- Retention is `keep-last=2`.
- Latest 2026-05-27 logs for VMs `100`, `101`, `102`, and `103` all ended with
  `Finished Backup`.

Current policy after the 2026-06-22 SMB remediation:

- 02:00 job: VMs `100,102,103`, `keep-last=7`, storage `smb-backup-new`.
- 04:00 job: CTs `111,114`, `keep-last=7`, storage `smb-backup-new`.
- VM 101 and VM 104 are stopped rollback artefacts with migration snapshots;
  they are intentionally excluded from recurring backups.
- The CIFS mount negotiates SMB 3.1.1 with `seal`; TCP 445 and storage pressure
  are checked every five minutes by `home-automation-health-check.timer`.
- Fresh VM 102 and CT 114 archives completed on 2026-06-22 and passed `zstd -t`.
- VM 102 was restored under temporary ID 9102, had its NIC removed before boot,
  answered through QEMU Guest Agent, then was shut down and purged.
- Existing local archives remain until all fresh guest backups and retention
  observation are complete.
- The measured daily set is 45,175,709,568 bytes; seven generations project to
  294.51 GiB and remain well below 80% of the 2.12 TB target. Residual risk: the
  larger shared filesystem backing `New` was already 87.34% used on 2026-06-22,
  so the conservative health high-water policy alerts until capacity is
  reclaimed, expanded, or that policy is explicitly changed.
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
vzdump 100 --mode snapshot --compress zstd --storage smb-backup-new
vzdump 111 --mode snapshot --compress zstd --storage smb-backup-new
vzdump 114 --mode snapshot --compress zstd --storage smb-backup-new
vzdump 102 --mode snapshot --compress zstd --storage smb-backup-new
vzdump 103 --mode snapshot --compress zstd --storage smb-backup-new
```

### Restore a VM or LXC

`Datacenter → Storage → smb-backup-new → Backups → select backup → Restore`

Or from shell:
```bash
# List available backups
ls /mnt/pve/smb-backup-new/dump/

# Restore VM 100 from backup
qmrestore /mnt/pve/smb-backup-new/dump/vzdump-qemu-100-*.vma.zst 100 --force

# Restore an LXC to its original ID only after stopping/removing a conflicting guest
pct restore 111 /mnt/pve/smb-backup-new/dump/vzdump-lxc-111-*.tar.zst
```

---

## Layer 2 — Home Assistant native backups

### Automatic backup to NAS

Configure in HA:
1. Add NAS as storage: `Settings → System → Storage → Add Network Storage`
   - Server: `192.168.40.50`, Protocol: NFS, Path: `/mnt/nas/ha-backups`
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
# On frigate-nvr VM
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

## Layer 5 — GitHub (config version control)

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
# FIX #16: Proxmox vzdump backups are stored on the MINISFORUM local NVMe
# (Storage: "local", path: /var/lib/vz/dump/) per the backup schedule above —
# NOT on the NAS. The NAS path /mnt/nas/ha-backups holds HA native backups only
# (the .tar files created by HA itself). If the MINISFORUM NVMe is recoverable, mount
# it and restore from there. If the SSD is lost, rebuild from scratch using the
# setup guides + HA's own backup (Step 3) — that is the real disaster-recovery path.

# --- If the original SSD is intact and you can attach it to the new machine ---
# Mount the old SSD's LVM (adjust device/VG name as needed):
vgimportclone /dev/sdX     # import old volume group
lvs                         # list logical volumes
# Then locate backups at /var/lib/vz/dump/ on the imported volume
# and restore normally:
qmrestore /old-ssd-mount/var/lib/vz/dump/vzdump-qemu-100-*.vma.zst 100
qmrestore /old-ssd-mount/var/lib/vz/dump/vzdump-qemu-101-*.vma.zst 101

# --- If the SSD is unrecoverable ---
# Skip to Step 3 — rebuild both VMs from scratch using the setup guides,
# then restore HA from its NAS backup. Frigate needs no data restore
# (recordings are on the NAS; Frigate DB rebuilds itself on first run).
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

- [ ] Proxmox: verify 2 recent backups exist in `Datacenter → Storage → local → Backups` while the temporary local pre-NAS policy is active
- [ ] HA: open `Settings → System → Backups` — confirm most recent is < 25 hours old
- [ ] NAS: `df -h /mnt/nas` — confirm usage < 80%
- [ ] NAS: `smartctl -a /dev/sda` — confirm drive health is PASSED
- [ ] GitHub: `git log --oneline -5` — confirm recent pushes
- [ ] Test restore: verify backup integrity - `ls -lh /mnt/nas/ha-backups/*.tar` (confirm non-zero), then `tar -tzf \ | tail -10` (should list config files). Annual full restore drill on spare hardware is recommended.
