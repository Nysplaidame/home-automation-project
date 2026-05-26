---
title: Package Dependency Matrix
description: Packages and tools required by host during rebuild
tags: [install, packages, dependencies]
created: 2026-05-24
modified: 2026-05-24
type: reference
status: active
---

# Package Dependency Matrix

## OpenWrt router

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `wireguard-tools` | Dormant fallback VPN | `opkg install wireguard-tools` | `wg --version` |
| `qrencode` | Optional client QR codes | `opkg install qrencode` | `qrencode --version` |
| `tcpdump` | Packet diagnostics | `opkg install tcpdump` | `tcpdump --version` |
| `iperf3` | Network testing | `opkg install iperf3` | `iperf3 --version` |

## Debian VMs and docker-host

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `qemu-guest-agent` | Proxmox guest status and clean shutdown | `apt-get install -y qemu-guest-agent` | `systemctl status qemu-guest-agent` |
| `ca-certificates curl gnupg` | Secure apt repositories | `apt-get install -y ca-certificates curl gnupg` | `curl --version` |
| `ufw` | Host firewall | `apt-get install -y ufw` | `ufw status` |
| `nfs-common` | Mount OMV NFS shares | `apt-get install -y nfs-common` | `showmount --version` |
| `docker-ce docker-ce-cli containerd.io docker-compose-plugin` | Docker Compose app runtime | Docker official apt repo install | `docker --version && docker compose version` |
| `tailscale` | Daily remote access route host | Tailscale official install | `tailscale version` |

## Proxmox host

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `ifupdown2` | Safe network reloads | `apt-get install -y ifupdown2` | `ifreload --help` |
| `intel-gpu-tools` | iGPU diagnostics for Frigate | `apt-get install -y intel-gpu-tools` | `intel_gpu_top -h` |

## Admin laptop

| Tool | Purpose | Verify |
|---|---|---|
| SSH client | Access router, Proxmox, VMs, OMV | `ssh -V` |
| Browser | Web UIs | Load Proxmox, HA, OMV |
| Git | Repository work | `git --version` |
| Text editor | Manual config edits | Open repo files |
