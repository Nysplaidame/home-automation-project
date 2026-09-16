# OpenMediaVault NAS Setup Guide

**Device:** NAS hardware running OpenMediaVault
**IP:** 192.168.40.50 - VLAN 40 (Storage)
**Port:** lan4 on GL-MT6000 (VLAN 40 untagged)
**Purpose:** storage for Home Assistant backups, Frigate archive storage, Immich library storage, and config/vault backups

> VLAN 40 has no internet access by default. Perform OS install and package
> updates before final isolation, or use a documented temporary maintenance
> path. OMV is storage-focused and is not the Docker app platform.

---

## Phase 1 - Install OMV

1. Install OpenMediaVault on the NAS boot device.
2. Use wired Ethernet only.
3. Set hostname: `omv-nas`.
4. Set timezone/locale: `Europe/London`.
5. Set the management address to:

| Field | Value |
|---|---|
| IP | `192.168.40.50/24` |
| Gateway | `192.168.40.1` |
| DNS | `192.168.40.1` |

6. Note the Ethernet MAC address and update the `omv-nas` reservation in
   `configs/openwrt/dhcp-config.conf`.

Expected router names:

```text
omv-nas.home.local -> 192.168.40.50
omv.home.local     -> 192.168.40.50
nas.home.local     -> 192.168.40.50
```

---

## Phase 2 - Storage

Create storage in OMV using the web UI:

1. `Storage -> Disks`: confirm all drives appear.
2. `Storage -> SMART`: enable SMART monitoring for data drives.
3. `Storage -> File Systems`: create or mount the data filesystem.
4. `Storage -> Shared Folders`: create:

Live verification on 2026-07-29 found global SMART polling enabled every 1,800
seconds with a 5 C change threshold and 55 C maximum alert. All five physical
disks (`/dev/sda` through `/dev/sde`) have per-device monitoring enabled and
reported `Good` at 33-44 C. No additional SMART self-test schedule was created.

| Shared folder | Purpose |
|---|---|
| `ha-backups` | Home Assistant network backup target |
| `frigate` | Frigate archive/recording target after cameras are live |
| `immich` | Immich upload/library storage |
| `configs` | Project config and vault backup target |

Keep Frigate live recordings on MINISFORUM local storage first. Move to OMV only
after camera retention, disk load, and restore expectations are clear.

---

## Phase 3 - Users And Permissions

Create service users with least-needed access:

| User | Access |
|---|---|
| `ha-backup` | read/write to `ha-backups` |
| `frigate` | read/write to `frigate` |
| `immich` | read/write to `immich` |
| `vault-backup` | read/write to `configs` |
| admin user | management access only |

Store passwords in Bitwarden. Do not commit share passwords, OMV admin
passwords, SSH keys, or Tailscale auth material.

---

## Phase 4 - NFS And SMB Shares

Enable NFS for Linux-to-Linux paths:

| Export | Allowed client |
|---|---|
| `ha-backups` | `192.168.20.101` |
| `frigate` | `192.168.30.20` |
| `immich` | `192.168.20.102` |
| `configs` | `192.168.10.0/24`, `192.168.20.101` |

Enable SMB only where useful for management clients:

| SMB share | Allowed clients |
|---|---|
| `configs` | Management VLAN clients |
| `ha-backups` | Management VLAN clients, read-only unless restore work needs write |

Do not expose the whole storage VLAN over Tailscale or WireGuard. Remote access
to OMV should be a host route to `192.168.40.50/32` only.

---

## Phase 5 - Home Assistant Network Storage

In Home Assistant:

`Settings -> System -> Storage -> Add Network Storage`

| Field | Value |
|---|---|
| Name | `NAS Backups` |
| Server | `192.168.40.50` |
| Protocol | NFS |
| Remote path | `/export/ha-backups` or the OMV export path shown in the UI |
| Usage | Backup |

Then configure automatic backups:

| Field | Value |
|---|---|
| Schedule | Daily |
| Time | `03:00` |
| Keep | 14 backups |
| Location | `NAS Backups` |

---

## Phase 6 - Frigate Storage

CT 111 is an unprivileged LXC, so it cannot mount NFS directly. Prepare the OMV
Frigate export, then mount it on the Proxmox host and bind-mount it into CT 111
when the camera/recording cutover is approved.

Current live note: OMV allows Proxmox host `192.168.10.10` to mount
`/export/frigate`; a temporary mount/write/read/delete/unmount test from
Proxmox passed on 2026-06-28.

On `proxmox`:

```bash
mkdir -p /mnt/omv/frigate
mount -t nfs 192.168.40.50:/export/frigate /mnt/omv/frigate
df -h /mnt/omv/frigate
```

After testing, add the host mount to `/etc/fstab`, bind it into CT 111 at
`/mnt/nas/frigate` with `pct set 111 -mp0 /mnt/omv/frigate,mp=/mnt/nas/frigate`,
and update the Frigate Compose volume from local storage to `/mnt/nas/frigate`.

---

## Phase 7 - Immich Storage

Immich runs on docker-host, not OMV. Mount or bind the OMV-backed `immich`
storage into the Immich stack under:

```text
/opt/stacks/immich/
```

Document the final mount path in `docs/reference/service-matrix.md` before
starting the stack.

---

## Monitoring

Minimum monitoring targets:

- OMV ping at `192.168.40.50`
- OMV web UI
- SMART status
- filesystem free space
- NFS reachability from HA, Frigate, and docker-host
- successful HA backup writes

The source-controlled Kuma SMART heartbeat is under
`configs/omv/system/omv-smart-kuma-heartbeat.*`. It runs `smartctl -H` against
every disk returned by `smartctl --scan-open` and reports aggregate state to a
monitor-specific Kuma push URL stored only in
`/etc/default/omv-smart-kuma-heartbeat` with mode `0600`. The timer cadence is
30 minutes and the corresponding Kuma interval is 2,100 seconds.

As of 2026-07-29, the files and secret are installed on OMV but the timer and
Kuma monitor 34 are deliberately disabled/paused. Enable them only after the
OMV-to-Kuma exception in `configs/monitoring/system/monitoring-firewall.sh` is
deployed and a manual service run reports all five disks healthy.

---

## Transfer Portal Runbook

Use this pattern when you need to move data between two local OMV-backed disks
without going through the network.

The native v1 web service source lives in `apps/transferportal/`, with the
install and operation runbook in `docs/install/services/transferportal.md`.
Do not deploy or restart that service while a manual rsync transfer is active
unless the operator has explicitly approved the interruption risk.

### Portal layout

Create two bind-mounted portal paths:

| Portal path | Backing volume | Purpose |
|---|---|---|
| `/srv/transferportal/source` | source filesystem | read-only mental model for the source disk |
| `/srv/transferportal/destination` | destination filesystem | writable target for the copy |

The portal directories themselves are just mount points. The real data lives on
the underlying filesystems.

### Copy command

Run the copy on the OMV server itself:

```bash
rsync -aHAX --numeric-ids --info=progress2 /srv/transferportal/source/ /srv/transferportal/destination/
```

Recommended if you want a resumable session:

```bash
nohup rsync -aHAX --numeric-ids --info=progress2 /srv/transferportal/source/ /srv/transferportal/destination/ >/tmp/transferportal-rsync.log 2>&1 &
```

### What happens if it is interrupted

- Files that already finished copying remain on the destination.
- By default, `rsync` writes an in-progress file to a temporary name and only
  renames it into place after the file completes.
- If the transfer is interrupted, an in-progress file is normally discarded or
  left as a temporary file, not trusted as a completed destination file.
- Re-running the same `rsync` command is safe; it will compare source and
  destination again and continue from the current state.
- For large files where preserving partial progress matters, add an explicit
  partial policy such as `--partial-dir=.rsync-partial`.

### Monitoring

Use these checks while the transfer runs:

```bash
pgrep -af 'rsync'
tail -f /tmp/transferportal-rsync.log
du -sh /srv/transferportal/source /srv/transferportal/destination
```

### Verification

After the copy finishes:

```bash
find /srv/transferportal/source -type f | wc -l
find /srv/transferportal/destination -type f | wc -l
```

If the destination count matches the source count and the copy completed
without errors, the transfer is complete.

---

## Completion Checklist

- [ ] OMV installed and hostname set to `omv-nas`.
- [ ] Static IP set to `192.168.40.50/24`.
- [ ] MAC added to `configs/openwrt/dhcp-config.conf`.
- [x] `omv-nas.home.local`, `omv.home.local`, and `nas.home.local` resolve.
- [ ] Data filesystem mounted.
- [ ] Shared folders created: `ha-backups`, `frigate`, `immich`, `configs`.
- [ ] Service users created with least-needed permissions.
- [ ] NFS exports scoped to approved clients.
- [ ] SMB scoped to Management VLAN where needed.
- [ ] HA network storage configured and backup test completed.
- [ ] Frigate mount tested but not made primary until cameras are live.
- [ ] Immich storage path documented before deployment.
- [x] SMART monitoring enabled on all five physical disks.
- [ ] Confirm the intended disk-usage alert thresholds and notification path.

## Quick Reference

| Item | Value |
|---|---|
| IP | `192.168.40.50` |
| Hostname | `omv-nas` |
| VLAN | 40 Storage |
| Web UI | `http://192.168.40.50/` or `http://omv.home.local/` |
| Tailscale route | `192.168.40.50/32` via docker-host |
| WireGuard fallback route | `192.168.40.50/32` only |
