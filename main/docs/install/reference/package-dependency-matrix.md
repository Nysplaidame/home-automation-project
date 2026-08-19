---
title: Package Dependency Matrix
description: Packages and tools required by host during rebuild
tags: [install, packages, dependencies]
created: 2026-05-24
modified: 2026-08-09
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
| `rsync` | Docker-host app-data backup copies to OMV and manual config copies | `apt-get install -y rsync` | `rsync --version` |
| `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` | Docker Compose app runtime | Docker official apt repo install | `docker --version && docker compose version` |
| `jq openssl less` | Validate JSON safely, generate local runtime tokens, and review downloaded installer/Compose files before execution | `apt-get install -y jq openssl less` | `jq --version && openssl version && less --version` |
| `tailscale` | Daily remote access route host | Tailscale official install | `tailscale version` |

## llm-host CT 114 base packages

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `ca-certificates curl gnupg` | Signed Docker repository and HTTPS diagnostics | `apt-get install -y ca-certificates curl gnupg` | `curl --version` |
| `ufw fail2ban` | CT-local host firewall and SSH protection | `apt-get install -y ufw fail2ban` | `ufw status && fail2ban-client -t` |
| `mesa-vulkan-drivers vulkan-tools vainfo intel-gpu-tools` | Shared Intel GPU Vulkan/VA-API runtime and diagnostics | `apt-get install -y mesa-vulkan-drivers vulkan-tools vainfo intel-gpu-tools` | `vulkaninfo --summary && vainfo --display drm --device /dev/dri/renderD128` |
| `jq` | Parse and assert local AI API responses | `apt-get install -y jq` | `jq --version` |
| `docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` | CT 114 Compose runtime | Docker official apt repo install | `docker --version && docker compose version` |

## llm-host CT 114 containers

| Image | Purpose | Pull / start path | Verify |
|---|---|---|---|
| `ghcr.io/ggml-org/llama.cpp:server-vulkan` | Primary local LLM runtime and OpenAI-compatible API | `/opt/stacks/local-ai/docker-compose.yml` | `curl -s http://127.0.0.1:8081/v1/models` |
| `ghcr.io/open-webui/open-webui` | Internal web UI for local chat and model testing | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps open-webui` |
| `rhasspy/wyoming-whisper` | Wyoming STT server for Home Assistant voice | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps wyoming-whisper` |
| `rhasspy/wyoming-piper` | Wyoming TTS server for Home Assistant voice | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps wyoming-piper` |
| `rhasspy/wyoming-openwakeword` | Wyoming wake-word server for Home Assistant voice | `/opt/stacks/local-ai/docker-compose.yml` | `docker compose ps wyoming-openwakeword` |

## Proxmox host

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `ifupdown2` | Safe network reloads | `apt-get install -y ifupdown2` | `ifreload --help` |
| `xz-utils` | Decompress the verified HAOS KVM/Proxmox image before VM 100 disk import | `apt-get install -y xz-utils` | `xz --version` |
| `intel-gpu-tools` | iGPU diagnostics for Frigate | `apt-get install -y intel-gpu-tools` | `intel_gpu_top -h` |

## Frigate CT 111

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `ca-certificates curl gnupg` | Signed Docker repository and TLS diagnostics | `apt-get install -y ca-certificates curl gnupg` | `curl --version` |
| `ffmpeg` | `ffprobe` camera stream and codec validation | `apt-get install -y ffmpeg` | `ffprobe -version` |
| `intel-gpu-tools vainfo` | Shared Intel GPU and VA-API diagnostics | `apt-get install -y intel-gpu-tools vainfo` | `vainfo --display drm --device /dev/dri/renderD128` |
| `ufw fail2ban` | CT-local defense-in-depth for SSH and Frigate listeners | `apt-get install -y ufw fail2ban` | `ufw status && fail2ban-client -t` |
| `sqlite3` | Read-only Frigate database integrity/recovery diagnostics | `apt-get install -y sqlite3` | `sqlite3 --version` |

## OMV NAS

| Package | Purpose | Install command | Verify |
|---|---|---|---|
| `mdadm` | Existing Linux md array inventory and recovery diagnostics | Managed by the OMV installation; install only if absent with `apt-get install -y mdadm` | `mdadm --detail --scan` |
| `smartmontools` | Physical disk discovery and health summaries | Managed by OMV | `smartctl --scan-open` |
| `nfs-kernel-server` | Source-scoped Linux client exports | Enable/install through OMV UI | `exportfs -v` |
| `samba` | Private management SMB shares | Enable/install through OMV UI | `smbd --version` |
| `acl` | Narrow Frigate mapped-UID access and ACL diagnostics | `apt-get install -y acl` on the Proxmox host | `getfacl --version` |

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
