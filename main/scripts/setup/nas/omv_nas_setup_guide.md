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

On `frigate-nvr`:

```bash
mkdir -p /mnt/nas/frigate
mount -t nfs 192.168.40.50:/export/frigate /mnt/nas/frigate
df -h /mnt/nas/frigate
```

After testing, add the mount to `/etc/fstab` and update the Frigate Compose
volume from local storage to `/mnt/nas/frigate`.

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

---

## Completion Checklist

- [ ] OMV installed and hostname set to `omv-nas`.
- [ ] Static IP set to `192.168.40.50/24`.
- [ ] MAC added to `configs/openwrt/dhcp-config.conf`.
- [ ] `omv-nas.home.local`, `omv.home.local`, and `nas.home.local` resolve.
- [ ] Data filesystem mounted.
- [ ] Shared folders created: `ha-backups`, `frigate`, `immich`, `configs`.
- [ ] Service users created with least-needed permissions.
- [ ] NFS exports scoped to approved clients.
- [ ] SMB scoped to Management VLAN where needed.
- [ ] HA network storage configured and backup test completed.
- [ ] Frigate mount tested but not made primary until cameras are live.
- [ ] Immich storage path documented before deployment.
- [ ] SMART and disk usage monitoring enabled.

## Quick Reference

| Item | Value |
|---|---|
| IP | `192.168.40.50` |
| Hostname | `omv-nas` |
| VLAN | 40 Storage |
| Web UI | `http://192.168.40.50/` or `http://omv.home.local/` |
| Tailscale route | `192.168.40.50/32` via docker-host |
| WireGuard fallback route | `192.168.40.50/32` only |
