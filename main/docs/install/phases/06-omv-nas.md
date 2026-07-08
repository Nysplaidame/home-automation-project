---
title: Phase 06 - OMV NAS
description: OpenMediaVault NAS, shares, service users, storage health, and client mounts
tags: [install, omv, nas, storage]
created: 2026-05-24
modified: 2026-07-06
type: install-guide
status: active
---

# Phase 06 - OMV NAS

## Purpose

Build storage-focused OpenMediaVault at `192.168.40.50` for Home Assistant
backups, Proxmox guest backups, future Frigate archive storage, Immich media,
docker-host app-data backups, and config backups. OMV is not the Docker app
platform.

## Runs on

- OMV web UI.
- OMV shell only for diagnostics.
- Client hosts when testing NFS/SMB mounts.

## Prerequisites

- Router storage VLAN configured.
- NAS hardware and drives installed.
- `<OMV_ADMIN_PASSWORD>` and service-user passwords ready.

## Inputs

- `<OMV_ADMIN_PASSWORD>`
- `<OMV_HA_PASSWORD>`
- `<OMV_FRIGATE_PASSWORD>`
- `<OMV_IMMICH_PASSWORD>`

## Commands

Run on: Admin laptop.

```powershell
Test-Connection 192.168.40.50 -Count 4
```

Run on: Proxmox host shell after OMV Frigate NFS share exists.

```sh
apt-get install -y nfs-common
mkdir -p /mnt/omv/frigate
mount -t nfs 192.168.40.50:/export/frigate /mnt/omv/frigate
df -h /mnt/omv/frigate
umount /mnt/omv/frigate
```

Do not mount NFS directly inside unprivileged CT 111. For the future recording
cutover, mount the OMV Frigate export on the Proxmox host and bind-mount it into
CT 111 only after the camera set is stable.

Run on: docker-host over SSH after OMV Immich share exists.

```sh
apt-get install -y nfs-common
mkdir -p /mnt/omv/immich
mount -t nfs 192.168.40.50:/export/immich /mnt/omv/immich
df -h /mnt/omv/immich
```

Run on: docker-host over SSH after OMV `backups/docker-host` export exists and
the live backup install is approved.

```sh
apt-get install -y nfs-common rsync
mkdir -p /mnt/omv/docker-host-backups
mount -t nfs 192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host /mnt/omv/docker-host-backups
mountpoint -q /mnt/omv/docker-host-backups
```

## Explanation

OMV owns storage and shares. App containers stay on docker-host and consume OMV
mounts only where storage is needed.

## Expected result

- OMV UI loads.
- Shares exist for Proxmox backups, HA backups, future Frigate recordings,
  Immich media, docker-host backups, and configs.
- Service users have least-required access.
- SMART/storage health is visible in OMV.

## Validation

Run on: Admin laptop.

```powershell
nslookup omv.home.local 192.168.10.1
nslookup nas.home.local 192.168.10.1
```

Run on: docker-host over SSH.

```sh
findmnt /mnt/omv/immich || true
findmnt /mnt/omv/docker-host-backups || true
```

## Failure recovery

- If OMV UI is unreachable, validate VLAN 40 IP and firewall host-only access.
- If mounts fail, test name resolution, then use the IP address directly.
- If permissions fail, fix OMV shared folder ACLs before changing client mounts.

## Completion checklist

- [ ] OMV installed at `192.168.40.50`.
- [ ] Hostnames resolve.
- [ ] Shares and service users exist.
- [ ] Proxmox, HA, Immich, and docker-host backup storage paths are tested.
- [ ] Frigate OMV recording path is warmed but not cut over until cameras are stable.
- [ ] OMV remains storage-focused.
