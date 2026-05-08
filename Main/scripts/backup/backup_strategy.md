# Backup Strategy and Procedures
# Covers: Proxmox snapshots, HA backups, Frigate retention, config file backup, recovery

---

## Backup layers overview

| Layer | What | Where stored | Schedule | Retention |
|---|---|---|---|---|
| Proxmox snapshot | Entire VM disk (100 only) | MINIX local SSD (`/var/lib/vz/dump`) | Daily 02:00 | 3 snapshots |
| HA native backup | HA config, add-ons, automations | HA local + NAS | Daily 03:00 | 14 days on NAS |
| Frigate recordings | Camera footage | NAS `/mnt/nas/frigate` | Continuous | 7 days motion, 14 days events |
| Frigate VM state | OS disk, DB, cache, compose/config | MINIX NVMe on VM 101 | Continuous | Rebuildable + config-backed |
| Config file backup | Safety vault YAML/configs | NAS /mnt/nas/configs | Daily via rsync | 30 days |
| GitHub | Safety vault docs + configs | GitHub repo | On push | Full history |

---

## Layer 1 — Proxmox VM snapshots

### Schedule (already configured per proxmox_setup_guide.md)

`Datacenter → Backup → Add`

| Field | Value |
|---|---|
| Storage | `local` (stores backup on MINIX SSD) |
| Schedule | `02:00` (daily) |
| Selection | VM 100 only |
| Mode | Snapshot |
| Compression | ZSTD |
| Max backups | 3 |
| Email | your@email.com (optional) |

This is intentionally scoped to VM 100. The MINIX NVMe is being treated as
compute/state storage, not as the long-retention home for large media workloads.
Frigate recordings should live on the NAS directly once it is online.

### Manual snapshot before major changes

```bash
# In Proxmox shell before any risky change
vzdump 100 --mode snapshot --compress zstd --storage local
vzdump 101 --mode snapshot --compress zstd --storage local
vzdump 103 --mode snapshot --compress zstd --storage local
```

### Restore a VM

`Datacenter → Storage → local → Backups → select backup → Restore`

Or from shell:
```bash
# List available backups
ls /var/lib/vz/dump/

# Restore VM 100 from backup
qmrestore /var/lib/vz/dump/vzdump-qemu-100-*.vma.zst 100 --force
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

- Keep VM 101 itself on the MINIX NVMe.
- Keep Frigate's database, cache, and service state local to VM 101.
- Store recordings directly on the NAS once `/mnt/nas/frigate` is available.
- Treat `/opt/frigate/storage` as a staging/fallback path, not the long-term
  archive target.

Frigate manages its own retention automatically per `configs/frigate/config.yml`:
- **Motion segments:** kept 7 days
- **Event clips (objects detected):** kept 14 days
- **Snapshots:** kept 14 days

Recordings are stored at `/mnt/nas/frigate` (NAS) or `/opt/frigate/storage` (local fallback).

Why this split:

- NVMe is better reserved for VM disks, Frigate DB/cache, HA, docker-host, and future VMs.
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

## Recovery runbook — MINIX hardware failure

If the MINIX dies completely:

### Step 1 — Replace hardware and reinstall Proxmox

Any x86-64 machine with 8GB+ RAM and 128GB+ SSD will work.
Follow `scripts/setup/proxmox/proxmox_setup_guide.md` phases A–C.

### Step 2 — Restore VM backups from NAS

```bash
# FIX #16: Proxmox vzdump backups are stored on the MINIX local SSD
# (Storage: "local", path: /var/lib/vz/dump/) per the backup schedule above —
# NOT on the NAS. The NAS path /mnt/nas/ha-backups holds HA native backups only
# (the .tar files created by HA itself). If the MINIX SSD is recoverable, mount
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

- [ ] Proxmox: verify 3 recent backups exist in `Datacenter → Storage → local → Backups`
- [ ] HA: open `Settings → System → Backups` — confirm most recent is < 25 hours old
- [ ] NAS: `df -h /mnt/nas` — confirm usage < 80%
- [ ] NAS: `smartctl -a /dev/sda` — confirm drive health is PASSED
- [ ] GitHub: `git log --oneline -5` — confirm recent pushes
- [ ] Test restore: verify backup integrity - `ls -lh /mnt/nas/ha-backups/*.tar` (confirm non-zero), then `tar -tzf \ | tail -10` (should list config files). Annual full restore drill on spare hardware is recommended. (L-12 fix: replaced impractical 'restore to test VM' guidance - MINIX has no spare capacity)
