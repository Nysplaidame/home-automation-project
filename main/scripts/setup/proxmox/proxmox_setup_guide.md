# Proxmox Host and Guest Setup Guide

## Production host

- MINISFORUM M1 Pro-125H, 32 GiB RAM, 1 TiB NVMe.
- Proxmox VE 9 at `192.168.10.10` on VLAN 10.
- `vmbr0` is VLAN-aware and the physical uplink is a tagged trunk.
- Current guests are listed in `configs/proxmox/guest-configs.md`.

## Build order

1. Install current Proxmox VE and apply updates.
2. Configure `vmbr0` as VLAN-aware and place the host address on VLAN 10.
3. Configure key-only SSH and record a physical recovery path.
4. Create VM 100 from the current HAOS image.
5. Create VM 102 and VM 103 from current Debian templates/images.
6. Create unprivileged CT 111 and CT 114 from a current Debian LXC template.
7. Apply per-guest VLAN/IP/resource settings from `guest-configs.md`.
8. Apply shared GPU mapping from `igpu_passthrough_guide.md`.
9. Configure backup jobs from `scripts/backup/backup_strategy.md`.

Do not use the archived all-in-one VM script: it creates the retired VM 101
Frigate architecture.

## Validation

Run on the Proxmox host:

```bash
pveversion
ip -br addr
qm list
pct list
pvesm status
cat /etc/pve/jobs.cfg
```

Expected production guests:

- running VMs: 100, 102, 103;
- running LXCs: 111, 114;
- stopped rollback VMs: 101, 104.

Never start VM 101 while CT 111 owns `192.168.30.20`, or VM 104 while CT 114
owns `192.168.20.104`.

## Recovery

- Guest-specific rebuild instructions live beside this guide.
- Current state: `docs/reference/current-live-state.md`.
- Backups and restore: `scripts/backup/backup_strategy.md`.
- Pre-LXC forensic instructions are archived and are not a rebuild path.
