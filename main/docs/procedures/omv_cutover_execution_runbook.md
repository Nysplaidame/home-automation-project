---
title: OMV Cutover Execution Runbook
description: Command-by-command execution plan for HA backups, Immich storage, and optional Frigate NAS recording cutover
tags: [omv, nas, cutover, runbook, execution]
created: 2026-05-28
type: procedure
status: active
---

# OMV Cutover Execution Runbook

This runbook is the executable version of
`docs/procedures/omv_storage_cutover_checklist.md`.

Use it when OMV hardware is online and reachable at `192.168.40.50`.

## Scope

- In scope now:
  - HA backup target cutover to OMV
  - Immich storage cutover to OMV
  - Post-cutover validation and rollback readiness
- Optional/later:
  - Frigate recording cutover to OMV (only when cameras are live)

## Change window gates

Proceed only if all are true:

1. OMV responds from required clients (`VM 100`, `CT 111`, `VM 103` paths).
2. Current Proxmox backups are healthy (`keep-last=2`, recent successful logs).
3. Snapshots taken immediately before cutover for VMs `100`, `101`, `103`.
4. No unrelated maintenance is in progress.

## Phase A - Pre-checks

Run on: management laptop.

```powershell
Test-Connection 192.168.40.50 -Count 4
```

Run on: docker-host (`192.168.20.102`).

```bash
ping -c 3 192.168.40.50
showmount -e 192.168.40.50
```

Run on: frigate-nvr (`192.168.30.20`) (optional until Frigate is live).

```bash
ping -c 3 192.168.40.50
showmount -e 192.168.40.50
```

Expected:
- OMV reachable from required hosts.
- Expected exports visible (HA backups, Immich, Frigate, configs).

## Phase B - Pre-cutover snapshots

Run on: Proxmox (`192.168.10.10`).

```bash
vzdump 100 --mode snapshot --compress zstd --storage local
vzdump 101 --mode snapshot --compress zstd --storage local
vzdump 103 --mode snapshot --compress zstd --storage local
```

Expected:
- Backup logs end with `Finished Backup`.

## Phase C - Home Assistant backup target cutover (UI)

Run on: Home Assistant UI (`http://192.168.20.101:8123`).

1. `Settings -> System -> Storage -> Add Network Storage`
2. Add OMV NFS share for HA backups.
3. `Settings -> System -> Backups -> Automatic Backups`
4. Set daily `03:00`, keep `14`, location = OMV storage.
5. Trigger one manual backup and confirm write to OMV.

Validation:
- Backup job succeeds.
- New artifact visible on OMV backup share.

Rollback:
- Switch backup target back to local HA storage and rerun manual backup.

## Phase D - Immich storage cutover (VM 103)

Run on: docker-host (`192.168.20.102`).

```bash
apt-get update && apt-get install -y nfs-common
mkdir -p /mnt/omv/immich
mount -t nfs 192.168.40.50:/export/immich /mnt/omv/immich
findmnt /mnt/omv/immich
df -h /mnt/omv/immich
```

Add persistent mount:

```bash
cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d_%H%M%S)
echo "192.168.40.50:/export/immich /mnt/omv/immich nfs defaults,_netdev 0 0" >> /etc/fstab
mount -a
findmnt /mnt/omv/immich
```

Stop Immich and cut volumes to OMV path (based on your stack file):

```bash
cd /opt/stacks/immich
docker compose down
# edit docker-compose.yml volume paths to use /mnt/omv/immich
docker compose up -d
docker compose ps
```

Validation:
- Immich UI loads.
- Upload test succeeds.
- New media writes to OMV mount path.

Rollback:

```bash
cd /opt/stacks/immich
docker compose down
# restore previous compose volume paths
docker compose up -d
```

## Phase E - Frigate OMV recording cutover (optional/later)

Only execute after cameras and RTSP are live.

CT 111 is an unprivileged LXC. Do not mount NFS from inside the CT; direct NFS
mounts fail with `Operation not permitted`. Mount the OMV export on the Proxmox
host and bind-mount it into CT 111.

Run on: Proxmox host (`192.168.10.10`).

```bash
apt-get update && apt-get install -y nfs-common
mkdir -p /mnt/omv/frigate
mount -t nfs 192.168.40.50:/export/frigate /mnt/omv/frigate
findmnt /mnt/omv/frigate
df -h /mnt/omv/frigate
```

OMV already allows Proxmox host `192.168.10.10` to mount `/export/frigate`; a
temporary mount/write/read/delete/unmount test passed on 2026-06-28. Do not use
the broad parent `/export` mount for production recordings unless that wider
access is deliberately accepted.

Persist mount on the Proxmox host:

```bash
cp /etc/fstab /etc/fstab.bak.$(date +%Y%m%d_%H%M%S)
echo "192.168.40.50:/export/frigate /mnt/omv/frigate nfs defaults,_netdev 0 0" >> /etc/fstab
mount -a
```

Bind into CT 111:

```bash
pct set 111 -mp0 /mnt/omv/frigate,mp=/mnt/nas/frigate
pct reboot 111
pct exec 111 -- findmnt /mnt/nas/frigate
```

Then update `/opt/frigate/docker-compose.yml` to use:

`/mnt/nas/frigate:/media/frigate/recordings`

Validation:
- Frigate stays healthy.
- Recordings write to OMV path.

Rollback:
- Revert compose volume mapping to local storage and restart Frigate.
- Remove the CT mount point with `pct set 111 -delete mp0` only after Frigate
  is stopped or back on local storage.

## Phase F - Post-cutover validation

Run on: management laptop.

```powershell
curl -s -o NUL -w "HA %{http_code}`n" http://192.168.20.101:8123/
curl -s -o NUL -w "Immich %{http_code}`n" http://192.168.20.102:2283/
```

Run on: management laptop.

```powershell
bash main/scripts/monitoring/health_check.sh --json
```

Expected:
- HA/Immich reachable.
- Health-check core path remains green.
- OMV-backed backup and storage writes verified.

## Phase G - Documentation closure

After successful cutover, update:

- `main/TO-DO.md`
- `main/HANDOFF-2026-05-28-preflight-next.md`
- `main/docs/reference/service-matrix.md` (final OMV mount roles/paths)

Do not treat cutover complete until docs are updated.
