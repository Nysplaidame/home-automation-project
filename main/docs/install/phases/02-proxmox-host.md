---
title: Phase 02 - Proxmox Host
description: Proxmox host baseline and VM shell creation
tags: [install, proxmox, vm]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 02 - Proxmox Host

## Purpose

Install and harden Proxmox on the MINISFORUM M1 Pro-125H host, configure the VLAN-aware bridge,
and create the VM shells used by Home Assistant, Frigate, monitoring, and
docker-host.

## Runs on

Proxmox host shell at `192.168.10.10` after network setup.

## Prerequisites

- Router phase validated.
- MINISFORUM host connected to the router trunk port.
- Proxmox installer media prepared.
- `<ADMIN_SSH_PUBLIC_KEY>` available.

## Inputs

- `<ADMIN_SSH_PUBLIC_KEY>`

## Commands

Run on: Proxmox host shell.

```sh
apt-get update
apt-get install -y ifupdown2
pveversion
ip -br link
ip -br addr
```

Run on: Proxmox host shell after creating guests from the relevant per-service guide.

```sh
qm list
pct list
```

## Explanation

`ifupdown2` allows safer network reloads. The former all-in-one VM script is
archived because it would recreate Frigate as VM 101. Use
`configs/proxmox/guest-configs.md` and the individual VM/LXC guides.

CT 114 `llm-host` is documented separately in Phase 05A and
`scripts/setup/proxmox/llm_host_setup_guide.md`.

## Expected result

- Proxmox host is reachable on VLAN 10 at `192.168.10.10`.
- `vmbr0` is VLAN-aware.
- VM and LXC guests match `configs/proxmox/guest-configs.md`.

## Validation

Run on: Proxmox host shell.

```sh
pveversion
qm list
pct list
cat /etc/network/interfaces
```

## Failure recovery

- If Proxmox loses network access, use local console access and restore the
  previous `/etc/network/interfaces` backup.
- If a VM script step fails, stop and compare with
  `scripts/setup/proxmox/proxmox_setup_guide.md`.

## Completion checklist

- [ ] Proxmox web UI loads.
- [ ] VLAN-aware bridge is configured.
- [ ] SSH key access works.
- [ ] VM shells are created or manually documented.
- [ ] Optional VM 104 local AI plan is either deferred or followed from Phase 05A.
