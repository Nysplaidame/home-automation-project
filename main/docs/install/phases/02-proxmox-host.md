---
title: Phase 02 - Proxmox Host
description: Proxmox ISO verification, host installation, storage, VLAN-aware networking, and guest-shell checkpoints
tags: [install, proxmox, vm]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 02 - Proxmox Host

## Purpose

Install Proxmox VE on the MINISFORUM M1 Pro-125H, preserve a local-console
recovery path, configure the VLAN-aware bridge, validate storage, and create
only the guest shells defined by the current inventory.

This is a fresh-rebuild path. The current production state is recorded in
[current-live-state.md](../../reference/current-live-state.md); do not infer a
blank-install step from a live-state note.

## Runs on

- Admin laptop for ISO download/checksum and remote validation.
- Proxmox installer UI using a local keyboard and display.
- Proxmox host shell, initially from the local console and later over SSH.
- Proxmox web UI at `https://192.168.10.10:8006/` after management networking
  is validated.

## Decision gate and stop conditions

This phase erases the selected installation disk. Continue only when:

- the MINISFORUM boot disk is positively identified by model, capacity, and
  serial number;
- anything that must survive has a separate, readable backup;
- local keyboard/display recovery is available;
- the managed-switch port can be kept as temporary VLAN 10 access during
  installation and deliberately changed to the approved trunk afterward;
- the router at `192.168.10.1` and its Phase 01 recovery path are working;
- the operator accepts the single-NVMe LVM-thin layout described below.

Stop if the installer shows multiple indistinguishable disks, the only backup
is on the disk being erased, or the switch-port state is unknown.

## Prerequisites

- Phase 01 router validation complete.
- MINISFORUM M1 Pro-125H, 32 GiB or more RAM, and 1 TiB NVMe recorded in the
  Phase 00 inventory.
- Proxmox ISO and matching checksum downloaded from the official Proxmox
  download page.
- USB installer prepared only after checksum verification.
- `<ADMIN_SSH_PUBLIC_KEY>` available from the approved password-manager record.
- [guest-configs.md](../../../configs/proxmox/guest-configs.md) reviewed.

## Inputs

- `<ADMIN_SSH_PUBLIC_KEY>`
- Hostname: `proxmox`
- Management address: `192.168.10.10/24`
- Management gateway/DNS during installation: `192.168.10.1`
- Management VLAN: `10`
- Physical host interface: confirm at install time; production inventory names
  it `enp1s0`, but never assume an interface name after a reinstall.

## 1. Verify the installer ISO

Download the ISO and the checksum published for that same release. Do not copy
a hash from a third-party page or from a different ISO version.

Run on: Admin laptop.

```powershell
$isoPath = 'C:\Users\Admin\Downloads\proxmox-ve.iso'
if (-not (Test-Path -LiteralPath $isoPath)) {
    throw "ISO not found: $isoPath"
}
$isoHash = (Get-FileHash -LiteralPath $isoPath -Algorithm SHA256).Hash.ToLowerInvariant()
$isoHash
```

Expected output is exactly 64 hexadecimal characters, for example:

```text
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

The example is deliberately not a real release checksum. Compare `$isoHash`
character-for-character with the official checksum for the downloaded filename.

Run on: Admin laptop.

```powershell
if ($isoHash -notmatch '^[0-9a-f]{64}$') {
    throw 'The calculated SHA-256 value is malformed.'
}
'ISO hash has a valid SHA-256 shape; manual official-value comparison is still required.'
```

Expected output:

```text
ISO hash has a valid SHA-256 shape; manual official-value comparison is still required.
```

If the official and calculated values differ, delete the ISO, download it again
over a trusted connection, and recalculate. Do not write the mismatched image to
USB and do not disable verification.

## 2. Install from local console

Before booting the installer, configure the host's switch port as an untagged
VLAN 10 access port. This provides a simple initial management path. The port is
changed to the approved tagged trunk only during the bridge cutover below.

Run on: Proxmox installer UI.

1. Select **Install Proxmox VE (Graphical)**.
2. Confirm the target disk by model/capacity against the Phase 00 inventory.
3. Use the default ext4/LVM-thin layout for the single 1 TiB NVMe unless a new
   storage decision has been approved and documented.
4. Set country, time zone, keyboard layout, root password, and a monitored admin
   email.
5. Select the physical Ethernet port connected to the VLAN 10 access port.
6. Set hostname `proxmox`, address `192.168.10.10/24`, gateway
   `192.168.10.1`, and DNS `192.168.10.1`.
7. Recheck the summary, especially the destructive target disk, before choosing
   **Install**.

Expected checkpoints:

- the installer completes without an I/O or package error;
- the first boot displays `https://192.168.10.10:8006/` on the console;
- the console login accepts the root credential;
- `ip -brief address` shows the temporary management address;
- the admin laptop can ping the host while its switch port is still VLAN 10
  access.

Do not select ZFS merely because it is available. A single-disk ZFS pool adds
memory and recovery tradeoffs without redundancy. A future storage redesign is
a separate decision and restore exercise.

## 3. Record the clean-install checkpoint

Run on: Proxmox host shell at the local console.

```bash
pveversion --verbose
ip -brief link
ip -brief address
findmnt -no SOURCE,FSTYPE,TARGET /
findmnt -no SOURCE,FSTYPE,TARGET /var/lib/vz
pvesm status
```

Expected output characteristics:

- `pveversion` identifies the installed Proxmox VE major release;
- exactly one intended physical uplink is `UP`;
- the temporary management path owns `192.168.10.10/24`;
- `local` is active for ISO/template/backup-type content;
- `local-lvm` is active for VM disks and LXC root filesystems.

Record the actual output and install date in the rebuild log. Version numbers
are evidence, not values to copy blindly into a later rebuild.

## 4. Update the host and install the network dependency

Use the repository appropriate to the operator's Proxmox subscription. Do not
silence repository authentication errors by mixing release suites or adding an
untrusted mirror.

Run on: Proxmox host shell at the local console.

```bash
apt-get update
apt-get full-upgrade
apt-get install -y ifupdown2
pveversion
ifreload --help >/dev/null && echo 'ifupdown2 ready'
```

Expected final output includes:

```text
ifupdown2 ready
```

Review any kernel or bootloader prompt before accepting it. If a reboot is
requested, reboot while the simple VLAN 10 access path and local console are
still available, then rerun the clean-install checkpoint.

## 5. Install the admin SSH public key

The following command is run from the admin laptop and transmits only the
approved public key. If `ssh-copy-id` is unavailable on Windows, paste the
public key through the Proxmox local console into `/root/.ssh/authorized_keys`
with permissions `0700` on `.ssh` and `0600` on `authorized_keys`.

Run on: Admin laptop.

```powershell
$publicKeyPath = Join-Path $env:USERPROFILE '.ssh/id_ed25519.pub'
$publicKey = (Get-Content -LiteralPath $publicKeyPath -Raw).Trim()
if ($publicKey -notmatch '^ssh-(ed25519|rsa)\s+') {
    throw 'Approved OpenSSH public key was not found.'
}
$publicKey | ssh root@192.168.10.10 "umask 077; mkdir -p /root/.ssh; cat >> /root/.ssh/authorized_keys"
```

Expected result: the pipeline exits `0` without echoing the key back or
reporting a remote permission error.

Run on: Admin laptop.

```powershell
ssh -o BatchMode=yes root@192.168.10.10 'hostname; pveversion'
```

Expected output starts with:

```text
proxmox
pve-manager/...
```

Do not disable password authentication until key login has succeeded in a
second terminal and local console access has been reconfirmed.

## 6. Convert the management port to a VLAN-aware trunk

The production host uses unaddressed `vmbr0` over the physical trunk and owns
its management address on `vmbr0.10`. Guest NICs attach to `vmbr0` with their
VLAN tags set in Proxmox.

Before editing, identify the physical interface by MAC address and switch port.

Run on: Proxmox host shell at the local console.

```bash
ip -brief link
bridge link
cp -a /etc/network/interfaces "/root/interfaces.pre-vlan-$(date +%Y%m%dT%H%M%S)"
ls -l /root/interfaces.pre-vlan-*
```

Expected result: the intended physical interface is identified and a non-empty,
timestamped backup exists under `/root/`.

Run on: Proxmox host shell at the local console.

```text
Edit /etc/network/interfaces so the physical NIC is manual, vmbr0 is an
unaddressed VLAN-aware bridge over that NIC, and vmbr0.10 owns:

    address 192.168.10.10/24
    gateway 192.168.10.1

Retain the installer-generated loopback and source/include lines.
```

This is an operator edit, not a copy/paste configuration block: the physical
interface name must come from the current host. The resulting bridge stanza
must include `bridge-ports`, `bridge-stp off`, `bridge-fd 0`, and
`bridge-vlan-aware yes`.

Keep the local console open. Change the managed-switch port from temporary
untagged VLAN 10 access to the approved trunk carrying VLANs
`1,10,20,30,35,40,50,60,70,99`, with management VLAN 10 tagged.

Run on: Proxmox host shell at the local console.

```bash
ifreload -a --syntax-check
```

Expected result: the command returns to the prompt with exit code `0` and no
syntax error. `--syntax-check` parses the interfaces file without applying it;
it is the documented long form of `ifreload -s`. If the installed command does
not expose this option in `ifreload --help`, stop and use the Proxmox web UI
pending-changes validator; do not experiment with an unknown reload option on
the live interface.

Run on: Proxmox host shell at the local console.

```bash
ifreload -a
ip -brief address | grep -E '^(vmbr0|vmbr0\.10)[[:space:]]'
ping -c 3 192.168.10.1
```

Expected output characteristics:

- `vmbr0` is up and has no management IPv4 address;
- `vmbr0.10` owns `192.168.10.10/24`;
- all three router pings succeed.

Run on: Admin laptop.

```powershell
Test-Connection -ComputerName 192.168.10.10 -Count 3
ssh -o BatchMode=yes root@192.168.10.10 "ip -brief address | grep -E '^(vmbr0|vmbr0\\.10)[[:space:]]'"
```

Expected result: all three probes return and SSH prints the expected bridge
address lines without prompting for a password.

Only close the local console after both remote checks pass.

### Network rollback rehearsal

The rollback path is the local console, not the network that is being changed.
During the rebuild window, prove the path by keeping the timestamped backup and
performing this sequence if the remote validation fails:

Run on: Proxmox host shell at the local console.

```bash
cp -a /root/interfaces.pre-vlan-YYYYMMDDTHHMMSS /etc/network/interfaces
ifreload -a
ip -brief address
ping -c 3 192.168.10.1
```

Replace the example backup filename with the exact file printed earlier. Return
the switch port to the temporary VLAN 10 access state at the same time. Expected
result: `192.168.10.10/24` returns on the pre-cutover interface/bridge and the
router ping succeeds. Record the rehearsal result and timestamp. Never claim
this rollback tested from the existence of a backup file alone.

The production host was documented live on `vmbr0.10` in the canonical task
state, but this blank-to-trunk rollback rehearsal still requires fresh evidence
on the next rebuild.

## 7. Validate storage choices

Run on: Proxmox host shell.

```bash
pvesm status
lvs -o lv_name,vg_name,lv_size,data_percent,metadata_percent
df -h / /var/lib/vz
```

Expected result:

- `local` and `local-lvm` are `active`;
- root/local storage retains free space for ISOs, templates, logs, and temporary
  restore work;
- thin-pool data and metadata percentages are reported, not `100%`;
- no OMV/NFS storage is assumed until Phase 06 configures and validates it.

Do not store irreplaceable application data only on `local-lvm`. Phase 10 owns
backup jobs and restore proofs; Phase 06 owns OMV/NFS storage.

## 8. Create only the current guest shells

Use [guest-configs.md](../../../configs/proxmox/guest-configs.md) and the
individual phase guides. Do not use the archived all-in-one VM script: it would
recreate retired Frigate VM 101 and does not represent the current LXC design.

Creation order:

1. VM 100 Home Assistant - Phase 03.
2. CT 111 Frigate - Phase 04.
3. VM 103 docker-host - Phase 05.
4. CT 114 local AI - Phase 05A.
5. OMV storage integration - Phase 06.
6. VM 102 monitoring - Phase 10.

Run on: Proxmox host shell after the relevant guest guides have been followed.

```bash
qm list
pct list
```

Expected steady-state inventory:

```text
VMs: 100 home-assistant, 102 monitoring, 103 docker-host
LXCs: 111 frigate-nvr, 114 llm-host
```

Retired VM IDs 101 and 104 may exist only as stopped, disconnected rollback
identities during a migration. On a clean rebuild they are not production
targets. Never start a retired VM while its replacement owns the same IP.

## End-of-phase validation

Run on: Proxmox host shell.

```bash
pveversion
ip -brief address | grep -E '^(vmbr0|vmbr0\.10)[[:space:]]'
bridge vlan show
pvesm status
qm list
pct list
systemctl --failed
```

Expected result: Proxmox version and intended bridge/VLAN state print, required
storage is `active`, expected guests are listed, and the failed-unit list is
empty or every entry is explained before continuing.

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.10.10 -Port 8006
ssh -o BatchMode=yes root@192.168.10.10 'hostname; pveversion'
```

Expected result:

- Proxmox web UI TCP 8006 is reachable from an approved management client;
- SSH key authentication works without a password prompt;
- `vmbr0.10` owns the host management address and `vmbr0` is VLAN-aware;
- local storage is active and has headroom;
- no failed systemd unit is unexplained;
- any created guest matches the canonical ID, type, VLAN, resources, and
  startup policy.

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| ISO hash mismatch | Delete and redownload the ISO; compare against the official hash for the exact filename. | Hashes match exactly. |
| Wrong disk is selected | Cancel before installation; identify disks by model/capacity/serial. | Target matches Phase 00 inventory. |
| Installer cannot reach gateway | Keep switch port as VLAN 10 access; recheck cable, NIC, gateway, and duplicate IP. | Console and admin-laptop ping both pass. |
| Update repository errors | Correct subscription/release repository configuration; do not mix suites. | `apt-get update` completes without repository errors. |
| VLAN cutover loses remote access | Use local console, restore the timestamped interfaces file, and return the switch port to VLAN 10 access. | Local and remote management checks pass again. |
| `local-lvm` missing/inactive | Stop guest creation; inspect `pvesm status`, `lvs`, and installer storage choice. | Expected storage is active with headroom. |
| Guest has wrong VLAN/resources | Keep it stopped; compare `qm config`/`pct config` with `guest-configs.md`. | Config matches before first boot. |
| Retired VM conflicts with an LXC | Stop the retired VM and disable `onboot`; confirm the production guest alone owns the address. | Only intended guest responds and inventory is reconciled. |

## Completion checklist

- [ ] ISO SHA-256 matches the official checksum for the exact release file.
- [ ] Destructive target disk and external backup were confirmed.
- [ ] Clean-install version, network, and storage checkpoint was recorded.
- [ ] Proxmox updates and `ifupdown2` installation completed without errors.
- [ ] SSH key access works and local console recovery remains available.
- [ ] `vmbr0` is VLAN-aware and `192.168.10.10/24` is on `vmbr0.10`.
- [ ] Remote bridge validation passed from the admin laptop.
- [ ] Network rollback path was rehearsed and the result recorded.
- [ ] `local` and `local-lvm` are active with safe headroom.
- [ ] Created guest shells match `guest-configs.md`; retired VM architecture was not recreated.
- [ ] No unexplained failed systemd units remain.

Continue to [Phase 03 - Home Assistant](03-home-assistant.md) after the host
baseline is validated. Phase 04, 05, 05A, and 10 add their guests in the order
shown above.
