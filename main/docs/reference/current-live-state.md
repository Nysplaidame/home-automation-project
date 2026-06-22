---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-06-22
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Last verified: **2026-06-22**.

## Compute

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.6.4, MQTT, ESPHome and Assist |
| 101 | QEMU VM | frigate-nvr | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 102 | QEMU VM | monitoring | `192.168.60.10` | Live | Uptime Kuma, InfluxDB, Grafana and Telegraf |
| 103 | QEMU VM | docker-host | `192.168.20.102` | Live | Trusted Compose workloads and Tailscale routing |
| 104 | QEMU VM | llm-host | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 111 | unprivileged LXC | frigate-nvr | `192.168.30.20` | Live baseline | Frigate 0.17.1, OpenVINO and VA-API on shared iGPU |
| 114 | unprivileged LXC | llm-host | `192.168.20.104` | Live | Ollama, Open WebUI and Wyoming voice services on shared iGPU |

VM 101 and VM 104 are retained temporarily as rollback points. Production DNS
and static addresses belong to CT 111 and CT 114. Never start either retired VM
while its replacement LXC is running.

## Home Assistant

- Configuration check passes on HAOS 2026.6.4.
- Mosquitto, File Editor, Terminal & SSH and ESPHome Device Builder are live.
- Home and Overwatch Assist pipelines are functional.
- Overwatch has a bounded read-only SearXNG search tool.
- Mealie is live; Overwatch-to-Mealie recipe saving is not yet implemented.
- VentSys dashboard is deployed; most physical VentSys entities remain gated on
  hardware installation.
- Repository and live HA core files, VentSys packages, mode scripts and dashboard
  have matching SHA-256 hashes. The valve contract is direct `0`/`50`, HA
  configuration validation passes, and HA restarted successfully on that source.
- Frigate integration is deferred until cameras and the production Frigate
  MQTT/camera configuration are enabled.

## Frigate

- CT 111 runs a healthy migration-safe Frigate baseline.
- OpenVINO detector process uses the shared Intel iGPU.
- VA-API is configured for future camera decoding.
- Cameras and MQTT are intentionally disabled in the live baseline because RTSP
  credentials, camera models and final MQTT material are not yet available.
- No production recordings exist; OMV archive storage remains future work.
- Dormant NFS client/RPC units are disabled because this unprivileged LXC has no
  NFS mount; this removes the failed `run-rpc_pipefs.mount` unit. Re-enable the
  client only as part of an approved NAS-recordings cutover.

## Local AI

- CT 114 runs Ollama, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord.
- Ollama Vulkan identifies Intel Meteor Lake graphics and offloads 33/33 model
  layers to the iGPU.
- Whisper starts offline from persistent model/tokenizer data.
- HA can reach ports 11434, 10200, 10300 and 10400 through source-scoped host
  and Docker firewall policy.
- SearXNG web search is reachable at docker-host port 8087.

## Docker host

Live workloads: Bambuddy, AdGuard Home, Immich pre-flight, Homepage, Dozzle,
ntfy, SearXNG, Whoogle, Mealie, Grocy, Obsidian LiveSync/CouchDB, Watchtower
monitor-only and Telegraf. VM 103 has a 64 GiB virtual disk.

Paperless-ngx, Actual Budget, Scrypted, Vaultwarden, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors.
- OMV TCP 445 and Proxmox storage pressure are checked every five minutes by
  `home-automation-health-check.timer`. Seven backup generations project to
  294.51 GiB and pass the 2.12 TB target gate; the check still alerts because
  the larger shared filesystem is 87.34% used.

## Backup storage

- OMV is live at `192.168.10.147` and exports encrypted SMB share `New`.
- Proxmox storage `smb-backup-new` uses SMB 3.1.1 with sealing, a dedicated
  account and subdirectory `proxmox-backups`.
- Daily jobs cover VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00, snapshot
  mode, ZSTD and `keep-last=7`.
- Fresh VM 102 and CT 114 archives passed `zstd -t` on 2026-06-22. VM 102 also
  passed an isolated no-NIC restore/boot/guest-agent drill under temporary ID
  9102, which was purged after validation.
- Existing local archives remain retained during the transition.

## Not built or not production-ready

- Cameras, PoE switch and production Frigate camera/MQTT configuration.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S details and HA Bambuddy package deployment.
- HA HTTPS/same-origin proxy for embedded monitoring views.
- Overwatch-to-Mealie recipe ingestion and Grocy workflow/integration.
- Obsidian LiveSync client rollout; its Tailscale Serve HTTPS endpoint is live.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain seven generations on
`smb-backup-new`; projected retention fits, while the backing filesystem's
87.34% utilization remains a high-water warning. Consult
`scripts/backup/backup_strategy.md`.
