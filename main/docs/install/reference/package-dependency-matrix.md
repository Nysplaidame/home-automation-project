---
title: Package Dependency Matrix
description: Packages and tools required by host during rebuild
tags: [install, packages, dependencies]
created: 2026-05-24
modified: 2026-06-10
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

## llm-host CT 114 containers

| Image | Purpose | Pull / start path | Verify |
|---|---|---|---|
| `ghcr.io/ggml-org/llama.cpp:server-vulkan` | Primary local LLM runtime and OpenAI-compatible API | `/opt/stacks/local-ai/docker-compose.yml` | `curl -s http://127.0.0.1:8081/v1/models` |
| `ghcr.io/open-webui/open-webui` | Internal web UI for local chat and model testing | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps open-webui` |
| `rhasspy/wyoming-whisper` | Wyoming STT server for Home Assistant voice | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps wyoming-whisper` |
| `rhasspy/wyoming-piper` | Wyoming TTS server for Home Assistant voice | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps wyoming-piper` |

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

## Garage Raspberry Pi desktop

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `firefox-esr` | Lean primary browser for HA, VentSys, Proxmox, Grafana, and project UIs | `apt install -y firefox-esr` | `firefox-esr --version` |
| `git curl wget jq tree rsync zip unzip` | Project files, downloads, API checks, and archive handling | `apt install -y git curl wget jq tree rsync zip unzip` | `git --version && curl --version && jq --version` |
| `htop btop` | Local resource monitoring | `apt install -y htop btop` | `htop --version && btop --version` |
| `dnsutils traceroute nmap iperf3 tcpdump` | Network diagnostics from the management VLAN | `apt install -y dnsutils traceroute nmap iperf3 tcpdump` | `dig -v && nmap --version && iperf3 --version` |
| `mosquitto-clients` | MQTT TLS subscribe/publish diagnostics | `apt install -y mosquitto-clients` | `mosquitto_sub --help` |
| `cifs-utils smbclient nfs-common` | NAS SMB/NFS client access | `apt install -y cifs-utils smbclient nfs-common` | `smbclient --version && showmount --version` |
| `python3 python3-venv python3-pip pipx python3-dev` | Isolated Python tooling for OLED, ESPHome, and experiments | `apt install -y python3 python3-venv python3-pip pipx python3-dev` | `python3 --version && pipx --version` |
| `i2c-tools python3-pil` | Case OLED setup support | `apt install -y i2c-tools python3-pil` | `i2cdetect -V` |
| `smartmontools nvme-cli` | NVMe health checks | `apt install -y smartmontools nvme-cli` | `smartctl --version && nvme version` |
