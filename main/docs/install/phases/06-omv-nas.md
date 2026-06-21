---
title: Phase 06 - OMV NAS
description: OpenMediaVault NAS, shares, service users, storage health, and client mounts
tags: [install, omv, nas, storage]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 06 - OMV NAS

## Purpose

Build storage-focused OpenMediaVault at `192.168.40.50` for Home Assistant
backups, Frigate archive storage, Immich media, and config backups. OMV is not
the Docker app platform.

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

Run on: Frigate CT over SSH after OMV NFS shares exist.

```sh
apt-get install -y nfs-common
mkdir -p /mnt/nas/frigate
mount -t nfs 192.168.40.50:/export/frigate /mnt/nas/frigate
df -h /mnt/nas/frigate
```

Run on: docker-host over SSH after OMV Immich share exists.

```sh
apt-get install -y nfs-common
mkdir -p /mnt/omv/immich
mount -t nfs 192.168.40.50:/export/immich /mnt/omv/immich
df -h /mnt/omv/immich
```

## Explanation

OMV owns storage and shares. App containers stay on docker-host and consume OMV
mounts only where storage is needed.

## Expected result

- OMV UI loads.
- Shares exist for HA, Frigate, Immich, and configs.
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
```

## Failure recovery

- If OMV UI is unreachable, validate VLAN 40 IP and firewall host-only access.
- If mounts fail, test name resolution, then use the IP address directly.
- If permissions fail, fix OMV shared folder ACLs before changing client mounts.

## Completion checklist

- [ ] OMV installed at `192.168.40.50`.
- [ ] Hostnames resolve.
- [ ] Shares and service users exist.
- [ ] HA, Frigate, and docker-host storage paths are tested.
- [ ] OMV remains storage-focused.
