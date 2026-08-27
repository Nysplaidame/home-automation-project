---
title: Phase 06 - OMV NAS
description: OpenMediaVault installation, preservation gates, filesystems, shares, NFS/SMB, SMART, client mounts, backups, and recovery
tags: [install, omv, nas, storage]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 06 - OMV NAS

## Purpose

Build or recover the storage-focused OpenMediaVault host at `192.168.40.50`,
without erasing existing arrays or confusing service permissions with filesystem
permissions. Provide tested storage paths for:

- Proxmox VM/LXC backups;
- Home Assistant native backups;
- Frigate recordings through a Proxmox-host mount and CT bind mount;
- Immich media and database backups;
- docker-host application backups;
- project/config backups;
- approved media libraries.

OMV remains the storage platform. Application containers run on docker-host,
not on OMV, except for deliberately approved native OMV utilities documented in
their own runbooks.

## Current-state callout

[current-live-state.md](../../reference/current-live-state.md) records the live
system: OMV is on VLAN 40, md0 carries the backup/CCTV hierarchy, HA and Proxmox
backups are active, docker-host mounts are live, Frigate records to OMV, and all
five physical disks were SMART-healthy at the last recorded check. This manual
is still the blank/recovery path; each new rebuild needs fresh evidence.

## Runs on

- Admin laptop for ISO verification, DNS, SMB, and reachability tests.
- OMV installer/local console for installation and network recovery.
- OMV web UI for disks, filesystems, users, shared folders, NFS/SMB, SMART, and
  notification settings.
- OMV shell for read-only inventory and targeted diagnostics.
- Proxmox host shell, Home Assistant UI, docker-host SSH, and CT 111 for client
  mount/write/restore proofs.

## Mandatory rebuild-mode gate

Choose and record exactly one mode before touching a disk:

| Mode | Meaning | Allowed disk action |
|---|---|---|
| **Preserve existing data** | OMV OS/boot device is being repaired or replaced; md arrays/data filesystems already contain project data | reinstall only the positively identified OS disk; assemble/import and mount data filesystems without formatting |
| **Blank new storage** | every selected data disk is new/empty and the operator has approved the final RAID/filesystem design | create array/filesystem only in OMV UI after serial-number and capacity review |

The current project defaults to **Preserve existing data**. Never infer that a
disk is blank because OMV does not show a filesystem, an array is degraded, a
mount is absent, or Windows cannot browse a share.

## Stop conditions

Stop before installation or storage changes if:

- the boot disk and every data disk are not distinguishable by model, serial,
  capacity, and connection path;
- a proposed erase/format/RAID-create action includes any existing md0 member or
  data disk;
- the only copy of needed data is on the disks being changed;
- the managed-switch VLAN 40 access port and local console path are unknown;
- OMV shared folders are being recreated over existing paths without first
  checking their contents and current OMV database references;
- NFS access is being broadened to a VLAN when a single host is sufficient;
- an NFS client is expected to authenticate with an SMB/service password;
- an ACL change would be made recursively across a populated media/data root
  without a documented owner-impact review;
- a failed mount would cause an application to write into an ordinary local
  directory at the same mountpoint.

Destructive disk, array, or filesystem actions require explicit operator
approval at the OMV UI when the exact target is visible. This guide deliberately
does not provide a shell command that wipes or formats a disk.

## Prerequisites

- Router and managed switch provide an untagged VLAN 40 access port.
- OMV host has a separate system/boot disk from all data disks.
- Phase 00 inventory contains disk serials and the storage recovery decision.
- `<OMV_ADMIN_PASSWORD>` is stored in the password manager.
- Service-specific SMB passwords are stored only if SMB is actually adopted;
  NFS paths use source scope plus Unix UID/GID permissions, not these passwords.
- Current data/backup inventory and [backup strategy](../../../scripts/backup/backup_strategy.md)
  have been reviewed.

## Inputs

- `<OMV_ADMIN_PASSWORD>`
- `<OMV_HA_PASSWORD>`, `<OMV_FRIGATE_PASSWORD>`, and
  `<OMV_IMMICH_PASSWORD>` only for an explicitly configured SMB identity; they
  are not NFS credentials.
- Hostname `omv-nas`
- Address `192.168.40.50/24`, gateway/DNS `192.168.40.1`
- Current production md0 data path:
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d`

The UUID above documents current production. A genuinely new filesystem will
have a different UUID; record it in canonical state and update dependent paths
instead of attempting to force the old UUID.

## 1. Capture the pre-install disk and array inventory

If the existing OMV OS still boots, capture this before reinstalling. These
commands are read-only.

Run on: OMV shell.

```bash
hostnamectl
lsblk -e7 -o NAME,PATH,SIZE,TYPE,FSTYPE,FSVER,LABEL,UUID,MODEL,SERIAL,MOUNTPOINTS
blkid
cat /proc/mdstat
mdadm --detail --scan 2>/dev/null || true
findmnt -rno SOURCE,FSTYPE,TARGET,OPTIONS
smartctl --scan-open
```

Expected evidence:

- one separately identified OMV system disk;
- every data disk's stable serial/model/capacity;
- md array name, members, UUID, state, and filesystem UUID where applicable;
- current mountpoints and export-bearing paths;
- all physical disks visible to SMART.

Store the inventory outside OMV. Do not include passwords, SMB secrets, or
private keys. If the system does not boot, collect equivalent evidence from a
trusted rescue environment before selecting an installer target.

## 2. Download and verify the official OMV installer

Use the current stable OpenMediaVault dedicated-drive ISO for x86/AMD64 unless
the hardware requires the documented Debian installation variant. OMV is not
supported as an LXC/container installation.

Run on: Admin laptop.

```powershell
$omvIso = 'C:\Users\Admin\Downloads\openmediavault-VERSION-amd64.iso'
if (-not (Test-Path -LiteralPath $omvIso)) {
    throw "OMV ISO not found: $omvIso"
}
$omvHash = (Get-FileHash -LiteralPath $omvIso -Algorithm SHA256).Hash.ToLowerInvariant()
if ($omvHash -notmatch '^[0-9a-f]{64}$') {
    throw 'Calculated OMV SHA-256 is malformed.'
}
$omvHash
```

Replace the illustrative `VERSION` filename with the actual download. Expected
output is one 64-character hexadecimal value matching the checksum published
for that exact official ISO. On mismatch, delete/redownload; never continue by
disabling verification.

## 3. Install OMV on the separate system disk

Run on: OMV installer/local console.

1. Disconnect data disks when practical, or positively identify them from the
   external inventory before selecting the system disk.
2. Install only to the dedicated OMV system disk.
3. Use wired Ethernet, hostname `omv-nas`, `Europe/London`, and a temporary
   installer network suitable for completing updates.
4. Reboot and confirm the console displays the expected address.
5. Open the web UI using the installer-reported address, change the default web
   password immediately to `<OMV_ADMIN_PASSWORD>`, and store it.
6. Create a non-privileged administrative user through OMV UI, grant only the
   approved SSH/sudo groups, test it, then disable routine direct-root SSH.

Expected result:

- system boots from the dedicated OS disk;
- web UI loads and default credentials no longer work;
- local console remains usable for `omv-firstaid` recovery;
- no data disk was partitioned, formatted, or added to a new array by the OS
  installation.

## 4. Set and validate VLAN 40 networking

Run on: OMV web UI.

Configure the wired interface with:

| Field | Value |
|---|---|
| IPv4 | static `192.168.40.50/24` |
| Gateway | `192.168.40.1` |
| DNS | `192.168.40.1` |
| IPv6 | project policy; do not leave an unreviewed alternate management path |

Apply while local console remains open.

Run on: OMV shell.

```bash
ip -brief address
ip route
getent hosts omv.home.local
ping -c 3 192.168.40.1
```

Expected result: the physical interface owns `.50/24`, default route points to
`.1`, local DNS returns `.50`, and all router pings succeed.

Run on: Admin laptop.

```powershell
Resolve-DnsName omv.home.local -Server 192.168.10.1
Resolve-DnsName nas.home.local -Server 192.168.10.1
Test-NetConnection 192.168.40.50 -Port 80
```

Expected result: both names resolve to `192.168.40.50` and the management web
port is reachable only from an approved source.

If access is lost, use local console `omv-firstaid` to inspect/reset network
configuration. Do not move the NAS onto an untagged user LAN as a hidden
permanent workaround.

## 5. Update before final network isolation

Use a documented temporary maintenance path if VLAN 40 has no general internet
access. Remove that path immediately after updates and prove normal storage-only
isolation again.

Run on: OMV shell during the approved update window.

```bash
apt-get update
apt-get full-upgrade
omv-salt deploy list-dirty
dpkg-query -W -f='${Package}\t${Version}\n' openmediavault
```

Expected result: package operations finish without repository errors,
`list-dirty` is empty after all saved UI changes have been applied, and
`dpkg-query` identifies the installed OMV package/version. If dirty states are
listed, return to the web UI, review the pending changes, and use **Apply**;
do not blindly deploy an unknown state list over the remote network session.
Record versions and whether a reboot is required.

After reboot, rerun network checks and confirm the temporary WAN/update rule is
gone. Do not mix Debian testing/unstable or Ubuntu repositories into OMV.

## 6. Import existing storage or create approved blank storage

### Preserve-existing-data path

Run on: OMV web UI.

1. Open **Storage -> Disks** and reconcile every serial with the saved inventory.
2. Confirm the existing md array is assembled and healthy/degraded state is
   understood before mounting anything.
3. Open **Storage -> Filesystems** and mount the existing filesystem through
   OMV UI so it enters OMV's configuration database.
4. Do not choose **Create**, **Delete**, **Wipe**, or a new RAID action.
5. Confirm existing directories are visible before creating shared-folder
   objects that reference them.

### Blank-new-storage path

Run on: OMV web UI after explicit disk/RAID approval.

1. Reconcile every selected blank disk by serial and capacity.
2. Record the approved RAID/filesystem design and failure tolerance.
3. Create the array/filesystem only in the UI and wait for initialization/sync.
4. Record the new filesystem UUID and mountpoint.
5. Do not create shares until array/filesystem health is normal.

Run on: OMV shell after either path.

```bash
cat /proc/mdstat
findmnt -rno SOURCE,FSTYPE,TARGET,OPTIONS | grep '/srv/'
df -hT | grep -E 'Filesystem|/srv/'
```

Expected result:

- the intended array/filesystem is mounted through OMV under `/srv/`;
- capacity matches the inventory/design;
- no unexpected disk is an array member;
- a preserving rebuild shows existing directories and data before shares are
  exposed.

If an array is degraded, do not remove/re-add members reflexively. Capture
`mdadm --detail`, SMART, kernel logs, and seek approval for the exact replacement
disk workflow.

## 7. Reconcile the directory and shared-folder model

OMV shared folders are database objects pointing at paths on a filesystem. They
do not move data when their parent/path changes. In preserve mode, select the
existing directory; do not create a case-variant duplicate such as `media` next
to `Media`.

Required logical objects and current intent:

| OMV logical object | Backing path intent | Consumer |
|---|---|---|
| `proxmox-backups` | md0 `backups/proxmox` | Proxmox `.10.10` |
| `ha-backups` | md0 `backups/home-assistant` | HA `.20.101` |
| `docker-host-backups` | md0 `backups/docker-host` | docker-host `.20.102` |
| `config-backups` | md0 `backups/configs` | approved management/backup jobs |
| `frigate` | md0 `CCTV` | Proxmox host mount for CT 111 |
| `immich` | approved Immich media root | docker-host `.20.102` |
| `media` | canonical populated media root on the 14 TB filesystem | approved docker-host media services |

Run on: OMV shell before adding/repointing objects.

```bash
find /srv -mindepth 1 -maxdepth 2 -type d -printf '%p\n' | sort
findmnt -rno SOURCE,FSTYPE,TARGET,OPTIONS | awk '$3 == "/srv" || index($3, "/srv/") == 1'
```

Expected result: intended existing paths are visible exactly once with their
case preserved. The directory listing is evidence only; create/reconcile shared
folders in OMV UI so services reference OMV database UUIDs.

Run on: OMV shell after UI reconciliation.

```bash
omv-confdbadm read --prettify conf.system.sharedfolder
```

Expected output contains one object per intended logical share with the correct
filesystem reference and relative path. If output contains case-colliding or
unknown objects, stop before enabling SMB/NFS and investigate; do not delete
either path until rollback and ownership are documented.

## 8. Create least-privilege identities

Run on: OMV web UI.

- Create management/SMB users through **Users**, using lowercase names and
  `/usr/sbin/nologin` unless shell access is specifically required.
- Grant shared-folder **Permissions** for service login access.
- Remember that OMV Permissions do not change underlying filesystem ownership
  or ACLs; verify both layers when a write fails.
- Do not create password users for NFS-only clients. NFS relies on source scope
  and Unix UID/GID behavior.
- Keep OMV web administration separate from data-share identities.

Expected result: each identity can access only its approved share/protocol; an
unapproved identity is denied. Record account ownership in the password manager,
not in Git.

## 9. Configure source-scoped NFS exports

Configure NFS through OMV UI. Use one host or narrow source per share. Keep
`root_squash` unless a documented workload proves otherwise; CT 111 uses mapped
UID `100000`, not NFS root.

| Export/path | Client source | Access |
|---|---:|---|
| Proxmox backups (md0 `backups/proxmox`) | `192.168.10.10` | read/write |
| HA backups (md0 `backups/home-assistant`) | `192.168.20.101` | read/write |
| `/export/frigate` | `192.168.10.10` | read/write |
| `/export/immich` | `192.168.20.102` | read/write |
| docker-host backups (md0 `backups/docker-host`) | `192.168.20.102` | read/write |
| approved media export | `192.168.20.102` | read-only or per-service scoped write roots |

Do not export Frigate directly to CT 111 and do not export the broad `/export`
pseudo-root as a production write target.

Run on: OMV shell.

```bash
exportfs -v
showmount -e 127.0.0.1
ss -lntup | grep -E ':(111|2049|20048|32765|32766|32767)[[:space:]]' || true
```

Expected result: every export shows only its approved client/source and intended
read/write options. NFS listeners exist only after the service is enabled.

Negative proof is mandatory: from one non-approved source, the mount must fail.
Do not weaken source scope merely to make `showmount` or a test client succeed.

## 10. Configure management-only SMB where needed

Use SMB for human/config management paths, not as a substitute for the Linux
service NFS mounts above.

Run on: OMV web UI.

1. Enable SMB and add only approved shared-folder objects.
2. Set shares private (`guest allowed: no`).
3. Grant write only to the intended management/backup identity.
4. Avoid whole-disk root shares unless an explicit maintenance decision requires
   one; remove or disable them after the maintenance task.
5. Apply changes and test both allowed and denied identities.

Run on: Admin laptop.

```powershell
Get-SmbConnection | Where-Object ServerName -eq '192.168.40.50'
Test-NetConnection 192.168.40.50 -Port 445
```

Expected result: TCP 445 is reachable from an approved management client and
the connection uses the intended OMV identity. Confirm an unapproved user or
source cannot browse the share. If Windows confuses case-only names, disconnect
all mappings/sessions before concluding that a directory was recreated.

## 11. Enable SMART and storage monitoring

Run on: OMV web UI.

1. Enable global SMART polling.
2. Enable monitoring for every physical disk that supports pass-through SMART.
3. Configure temperature-change and maximum-temperature notifications.
4. Do not add an aggressive self-test schedule without checking drive workload
   and array behavior.
5. Configure notification delivery and perform a test notification.

Current project defaults are a 1,800-second poll, 5 C change notification, and
55 C maximum. Treat them as project policy to verify, not proof of current disk
health.

Run on: OMV shell.

```bash
smartctl --scan-open
while read -r device rest; do
  printf '%s: ' "$device"
  smartctl -H "$device" | grep -E 'SMART overall-health|SMART Health Status'
done < <(smartctl --scan-open)
cat /proc/mdstat
```

Expected result: every intended physical disk reports a healthy SMART summary
and the array has no unexpected degraded/resync state. A healthy SMART result
does not replace array/filesystem/capacity checks.

The source-controlled Kuma heartbeat files are under
`configs/omv/system/omv-smart-kuma-heartbeat.*`. Store the push URL only in the
mode-`0600` environment file. Enable the timer only after the narrow OMV-to-Kuma
firewall path and a manual healthy run pass.

## 12. Add Proxmox backup storage and prove restoreability

Run on: Proxmox host shell.

```bash
apt-get update
apt-get install -y nfs-common
showmount -e 192.168.40.50
```

Expected result: the exact Proxmox backup export is visible to `.10.10`.

Run on: Proxmox host shell.

```bash
pvesm add nfs omv-backups \
  --server 192.168.40.50 \
  --export /srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox \
  --content backup \
  --options vers=3 \
  --prune-backups keep-daily=7,keep-monthly=6

pvesm status | awk 'NR == 1 || $1 == "omv-backups"'
df -hT /mnt/pve/omv-backups
```

Expected result: `omv-backups` is `active`, reports NFS storage, and has enough
headroom for the documented retention policy. If the filesystem UUID changed,
use the actual approved export path and update canonical state.

Run on: Proxmox host shell during an approved proof window.

```bash
vzdump 102 --storage omv-backups --mode snapshot --compress zstd
latest_vm102="$(find /mnt/pve/omv-backups/dump -maxdepth 1 -type f -name 'vzdump-qemu-102-*.vma.zst' -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)"
test -n "$latest_vm102" && test -s "$latest_vm102"
zstd -t "$latest_vm102"
```

Expected result: backup log ends successfully, the latest archive is non-zero,
and `zstd -t` reports no error. Complete the existing isolated no-NIC restore
procedure before declaring the storage recovery-proven.

## 13. Add Home Assistant network backup storage

Run on: Home Assistant UI.

1. Open **Settings -> System -> Storage -> Add network storage**.
2. Name it `nas_backups`, choose NFS and usage **Backup**.
3. Server: `192.168.40.50`.
4. Remote path:
   `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`
   for the current md0 filesystem, or the newly recorded equivalent after a
   genuine filesystem replacement.
5. Connect, then select it as the automatic-backup location.
6. Schedule daily `03:00`, retain 14 copies, and create a manual proof backup.

Run on: Home Assistant Terminal & SSH app.

```bash
ha mounts info
ha backups list
```

Expected result: `nas_backups` reports active/writable/default as intended and
the new backup appears with a slug and non-error state. Also verify a non-zero
file on OMV; an HA catalog row alone is not write proof.

Rollback test: select local HA storage, create one local backup, then return to
`nas_backups` and create a fresh NAS backup. Record both results without editing
HA `.storage` files directly.

## 14. Mount Immich and docker-host backup exports

Run on: docker-host over SSH.

```bash
apt-get update
apt-get install -y nfs-common
install -d -m 0755 /mnt/omv/immich /mnt/omv/docker-host-backups

mount -t nfs -o nfsvers=3,proto=tcp \
  192.168.40.50:/export/immich /mnt/omv/immich
mount -t nfs -o nfsvers=3,proto=tcp \
  192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host \
  /mnt/omv/docker-host-backups

findmnt -T /mnt/omv/immich
findmnt -T /mnt/omv/docker-host-backups

for target in /mnt/omv/immich /mnt/omv/docker-host-backups; do
  probe="${target}/.docker-host-write-test-$(date +%s)"
  printf 'docker-host mount proof\n' >"$probe"
  grep -Fx 'docker-host mount proof' "$probe"
  rm -f "$probe"
done
```

Expected result: both paths report the exact OMV source and NFSv3; each
temporary proof can be written, read, and removed. Before adding fstab entries,
create a timestamped `/etc/fstab` backup and reject duplicate exact lines.

Run on: docker-host over SSH.

```bash
cp -a /etc/fstab "/etc/fstab.pre-omv-$(date +%Y%m%dT%H%M%S)"

immich_line='192.168.40.50:/export/immich /mnt/omv/immich nfs nfsvers=3,proto=tcp,_netdev,nofail,timeo=50,retrans=2 0 0'
backup_line='192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host /mnt/omv/docker-host-backups nfs nfsvers=3,proto=tcp,_netdev,nofail,timeo=50,retrans=2 0 0'

grep -Fqx "$immich_line" /etc/fstab || printf '%s\n' "$immich_line" >>/etc/fstab
grep -Fqx "$backup_line" /etc/fstab || printf '%s\n' "$backup_line" >>/etc/fstab

mount -a
findmnt -T /mnt/omv/immich
findmnt -T /mnt/omv/docker-host-backups
```

Expected result: `mount -a` exits `0`, each line appears exactly once, and both
mounts retain their intended source. Run the service-specific write/backup and
restore smoke tests before starting automatic jobs.

Mount-failure recovery: stop any service whose target would become a local
directory, unmount partial state, restore the timestamped fstab, run
`systemctl daemon-reload`, and re-run `mount -a`. Prove local paths are not being
used as accidental storage before restarting applications.

## 15. Mount and bind Frigate recordings

CT 111 is unprivileged and must not mount NFS. Proxmox owns the NFS client.

Run on: Proxmox host shell.

```bash
apt-get install -y nfs-common acl
install -d -m 0755 /mnt/omv/frigate
mount -t nfs -o nfsvers=3,proto=tcp \
  192.168.40.50:/export/frigate /mnt/omv/frigate
findmnt -T /mnt/omv/frigate
```

Expected result: source is exactly `/export/frigate` on OMV. Perform a temporary
host write/read/delete test before persistence.

Run on: Proxmox host shell.

```bash
probe="/mnt/omv/frigate/.proxmox-write-test-$(date +%s)"
printf 'frigate mount proof\n' >"$probe"
grep -Fx 'frigate mount proof' "$probe"
rm -f "$probe"

setfacl -m u:100000:rwx,d:u:100000:rwx /mnt/omv/frigate
getfacl -p /mnt/omv/frigate | grep -E 'user:100000:rwx|default:user:100000:rwx'

pct set 111 --mp0 /mnt/omv/frigate,mp=/mnt/nas/frigate
pct reboot 111
pct exec 111 -- findmnt -T /mnt/nas/frigate
```

Expected result: host test is removed, UID `100000` has access/default ACLs,
and CT 111 sees the Proxmox bind mount. Then perform CT write/read/delete and a
fresh Frigate segment proof from Phase 04 before enabling normal recording.

Persist the Proxmox NFS mount with a reviewed, non-duplicated fstab entry using
the same `_netdev,nofail,timeo=50,retrans=2` pattern:

Run on: Proxmox host shell.

```bash
cp -a /etc/fstab "/etc/fstab.pre-frigate-$(date +%Y%m%dT%H%M%S)"
frigate_line='192.168.40.50:/export/frigate /mnt/omv/frigate nfs nfsvers=3,proto=tcp,_netdev,nofail,timeo=50,retrans=2 0 0'
grep -Fqx "$frigate_line" /etc/fstab || printf '%s\n' "$frigate_line" >>/etc/fstab
mount -a
findmnt -T /mnt/omv/frigate
```

Expected result: `mount -a` exits `0`, the fstab entry appears exactly once,
and `findmnt` reports the OMV export. If the host mount is absent, stop CT
111/Frigate rather than allowing writes into an unmounted local path.

## 16. Back up OMV configuration and prove OS recovery

OMV does not provide a general supported configuration-restore button. Keep
`/etc/openmediavault/config.xml` and package/disk inventories as restricted
reference material for a clean reinstall; do not assume copying the XML alone
is a complete restore.

Run on: OMV shell.

```bash
checkpoint="$(date +%Y%m%dT%H%M%S)"
install -d -m 0700 /root/omv-recovery
install -m 0600 /etc/openmediavault/config.xml "/root/omv-recovery/config.xml-${checkpoint}"
dpkg-query -W -f='${binary:Package}\t${Version}\n' >"/root/omv-recovery/packages-${checkpoint}.tsv"
lsblk -e7 -o NAME,SIZE,FSTYPE,LABEL,UUID,MODEL,SERIAL >"/root/omv-recovery/disks-${checkpoint}.txt"
test -s "/root/omv-recovery/config.xml-${checkpoint}"
```

Expected result: restricted, non-zero configuration, package, and disk reference
files exist. Copy them to the approved config-backup target without exposing
them through a public/guest share.

OS recovery rehearsal/tabletop:

1. identify the OS disk from saved serials;
2. confirm data disks would remain disconnected/unselected during reinstall;
3. reinstall OMV on a spare/disposable boot disk or document the exact console
   sequence without touching production data;
4. mount/assemble an approved test filesystem through OMV UI;
5. recreate one disposable shared-folder/NFS object from the reference;
6. verify allowed/denied client behavior, then remove only the disposable test
   object.

Production data-array reassembly is not a casual drill. Until performed during
a real recovery or on equivalent spare media, record **OS recovery tabletop
complete; production array re-import unproven**.

## 17. End-to-end restore proofs

Storage is complete only when consumers can restore without overwriting live
state:

- Proxmox: restore a selected VM archive to a temporary ID with its NIC removed,
  boot/check it, then remove the temporary guest after approval.
- Home Assistant: restore a native backup into an isolated disposable HAOS VM.
- docker-host: restore app-data into temporary directories/containers and run
  database integrity or application health checks.
- Frigate: restore CT/config/database into a stopped temporary CT and verify the
  OMV recording path separately; never start duplicate network identity.
- project vault: copy a selected NAS backup into a temporary local folder and
  compare representative files without overwriting the working vault.

Record backup identifier, restore target, date, result, and cleanup. A visible
archive, `tar` listing, checksum, or successful write test is useful evidence
but does not replace the matching isolated restore proof.

## End-of-phase validation

Run on: OMV shell.

```bash
hostnamectl --static
ip -brief address
cat /proc/mdstat
df -hT | grep -E 'Filesystem|/srv/'
exportfs -v
smartctl --scan-open
omv-confdbadm read --prettify conf.system.sharedfolder
systemctl --failed
```

Expected result: OMV identity/address are correct, the approved filesystems or
array are healthy, exports/shared folders match policy, all disks are visible
to SMART, and no unexplained service is failed.

Run on: Proxmox host shell.

```bash
pvesm status | awk 'NR == 1 || $1 == "omv-backups"'
findmnt -T /mnt/omv/frigate
pct exec 111 -- findmnt -T /mnt/nas/frigate
```

Expected result: `omv-backups` is active, the Proxmox Frigate NFS mount is
remote, and CT 111 sees its bind-mounted recording target.

Run on: docker-host over SSH.

```bash
findmnt -T /mnt/omv/immich
findmnt -T /mnt/omv/docker-host-backups
systemctl list-timers docker-host-app-data-backup.timer
```

Expected result: both docker-host targets resolve to their intended remote NFS
exports and the app-data backup timer has a next/last run entry.

Run on: Home Assistant Terminal & SSH app.

```bash
ha mounts info
ha backups list
```

Expected result: the OMV network storage reports connected and at least one
current backup is listed on the intended destination.

Run on: Admin laptop.

```powershell
Resolve-DnsName omv.home.local -Server 192.168.10.1
Test-NetConnection 192.168.40.50 -Port 80
Test-NetConnection 192.168.40.50 -Port 445
```

Expected result:

- correct hostname/IP/DNS and management-source access;
- intended array/filesystems mounted with healthy capacity/state;
- shared folders map to correct existing paths without case collisions;
- NFS/SMB allow and deny tests match source/user policy;
- all physical disks report acceptable SMART health;
- Proxmox, HA, docker-host, Immich, and Frigate mounts/writes are proven;
- consumers have current backups plus isolated restore evidence;
- no unexplained failed service remains;
- OMV remains storage-focused and no unapproved application stack was added.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| Installer target uncertain | Cancel and reconcile disk serial/model/capacity. | Exact separate OS disk identified. |
| Existing data disk appears blank | Stop; inspect md/partition/filesystem metadata from rescue/OMV. | Existing ownership/state understood without formatting. |
| Array degraded | Capture mdadm/SMART/kernel evidence; approve exact replacement workflow. | Array state normal or accepted degraded-read window documented. |
| OMV UI/network lost | Use local console `omv-firstaid`; restore VLAN 40 settings. | DNS, web, gateway checks pass again. |
| Filesystem mounted outside OMV | Import/mount it through OMV UI rather than manual persistent fstab. | Filesystem appears in OMV DB and shared-folder selector. |
| Shared folder points to wrong path | Disable dependent exports first; repoint without moving/deleting data. | OMV DB and filesystem path agree. |
| Case-collision in SMB | Disconnect client sessions; inspect server-side inodes/names; use reversible approved rename/removal only. | One canonical path remains and clients remount cleanly. |
| SMB permission denied | Check OMV service permission and filesystem POSIX/ACL separately. | Intended user writes; unapproved user remains denied. |
| NFS mount denied | Check exact export source, protocol/version, OpenWrt, and UID/GID. | Approved host mounts; negative host still fails. |
| NFS mount disappears | Stop dependent app before local fallback writes; restore mount/fstab. | `findmnt` exact source passes before restart. |
| Frigate permission denied | Verify Proxmox mount, CT `mp0`, UID 100000 access/default ACL. | CT write/delete and fresh MP4 segment pass. |
| Proxmox backup fails | Inspect NFS capacity/logs and LXC `tmpdir=/var/tmp`; do not clear active locks blindly. | Fresh archive and integrity/restore proof pass. |
| HA mount disappears | Re-add via HA UI, select default, create manual proof backup. | `ha mounts info` and OMV file both prove write. |
| SMART/temperature alert | Identify exact serial/device and array role before action. | Replacement/monitor decision documented; array checked. |
| OMV OS disk fails | Reinstall only OS disk, use saved config/inventory as reference, import existing data through UI. | Shares/exports recreated and allow/deny tests pass. |
| Restore proof fails | Preserve live source; retry a known backup in a new isolated target. | Workload-specific health/integrity passes before cleanup. |

## Completion checklist

- [ ] Rebuild mode and every disk serial/role are recorded outside OMV.
- [ ] Official installer hash matches and only the separate OS disk is selected.
- [ ] OMV web/local-console recovery and non-root administration are proven.
- [ ] VLAN 40 address, DNS, gateway, and management-source access pass.
- [ ] Existing array/filesystem is imported without formatting, or blank-storage design is explicitly approved and created.
- [ ] Shared-folder objects map to the intended existing paths with no case collision.
- [ ] Service users are least-privilege and NFS is not treated as password-authenticated.
- [ ] NFS exports pass approved-host and denied-host tests.
- [ ] SMB passes approved-user/source and denied-user/source tests.
- [ ] SMART covers every physical disk and notification delivery is tested.
- [ ] `omv-backups` passes fresh archive, integrity, and isolated restore proof.
- [ ] HA `nas_backups` passes external write and isolated restore proof.
- [ ] Immich and docker-host backup mounts persist without accidental local fallback.
- [ ] Frigate Proxmox mount, UID 100000 ACL, CT bind, and fresh segment pass.
- [ ] Restricted OMV config/package/disk recovery references exist off-host.
- [ ] OMV OS recovery tabletop is recorded; any unproven production-array step is explicit.
- [ ] No unapproved Docker/application platform was added to OMV.

Continue to [Phase 07 - Tier 1 Apps](07-tier1-apps.md) after storage consumers
and their isolated restore paths are accepted.
