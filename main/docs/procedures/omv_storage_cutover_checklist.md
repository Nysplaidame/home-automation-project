---
title: OMV Storage Cutover Checklist
description: Pre-flight cutover steps for HA, Immich, and Frigate when OMV NAS becomes live
tags: [omv, nas, storage, cutover]
created: 2026-05-28
type: procedure
status: active
modified: 2026-06-28
---

# OMV Storage Cutover Checklist

Use this checklist once OMV (`192.168.40.50`) is online and reachable from
Automation (`VLAN 20`) and NVR (`VLAN 30`) paths.

## 1) Pre-cutover validation

- Confirm OMV host responds on `192.168.40.50` from:
  - docker-host (`192.168.20.102`)
  - frigate VM (`192.168.30.20`)
  - HA path (manual UI check is acceptable)
- Confirm NFS exports exist for:
  - Home Assistant backups
  - Immich media
  - Frigate recordings archive
- Snapshot affected VMs before moving storage:
  - VM 100 (HAOS)
  - CT 111 (frigate-nvr)
  - VM 103 (docker-host)

## 2) Home Assistant backup target cutover

- In HA UI: `Settings -> System -> Storage -> Add Network Storage`
  - Protocol: NFS
  - Target: OMV backup export
- In HA UI: `Settings -> System -> Backups -> Automatic Backups`
  - Schedule daily (03:00)
  - Keep 14
  - Location: OMV-backed storage
- Verify first successful backup write to OMV and retention behavior.

## 3) Immich storage cutover (docker-host)

- Stop Immich stack on VM 103.
- Mount OMV media path for Immich on docker-host.
- Update stack volume mappings to OMV-backed media path.
- Start Immich stack and verify:
  - UI loads
  - uploads succeed
  - existing local placeholder path is not used for new media
- Keep local rollback copy until at least one successful backup cycle.

## 4) Frigate recording cutover (CT 111)

- Keep Frigate stopped until RTSP/MQTT/TLS prerequisites are complete.
- Do not try to mount NFS from inside CT 111. It is an unprivileged LXC and
  direct `mount -t nfs ...` fails with `Operation not permitted`.
- Mount the OMV NFS target on the Proxmox host, then bind-mount it into CT 111
  with a Proxmox `mp` entry.
- OMV exports `/export/frigate` to both CT 111 (`192.168.30.20`) and Proxmox
  host (`192.168.10.10`). A temporary Proxmox host mount/write/read/delete/
  unmount test passed on 2026-06-28.
- For unprivileged CT 111, ensure the mounted export grants write access to the
  CT root-mapped host UID `100000`, for example with
  `setfacl -m u:100000:rwx,d:u:100000:rwx /mnt/omv/frigate` on the Proxmox
  host after mounting the export.
- In `/opt/frigate/docker-compose.yml`, enable the NAS recordings volume:
  - `/mnt/nas/frigate:/media/frigate/recordings`
- Start Frigate and verify:
  - recordings write to OMV path
  - local `/opt/frigate/storage` remains staging/fallback only

## 5) Post-cutover checks

- Confirm router/firewall rules still match storage-flow intent.
- Run `scripts/monitoring/health_check.sh --json` and confirm core checks pass.
- Confirm backup artifacts are visible from OMV and are non-zero size.
- Update `TO-DO.md` and the active handoff with final cutover status.
