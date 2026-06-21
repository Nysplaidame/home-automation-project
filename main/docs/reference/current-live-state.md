---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-06-20
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Last verified: **2026-06-20**.

## Compute

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.6.3, MQTT, ESPHome and Assist |
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

- Configuration check passes on HAOS 2026.6.3.
- Mosquitto, File Editor, Terminal & SSH and ESPHome Device Builder are live.
- Home and Overwatch Assist pipelines are functional.
- Overwatch has a bounded read-only SearXNG search tool.
- Recipe-to-Obsidian/Mealie saving is not implemented.
- VentSys dashboard is deployed; most physical VentSys entities remain gated on
  hardware installation.
- Frigate integration is deferred until cameras and the production Frigate
  MQTT/camera configuration are enabled.

## Frigate

- CT 111 runs a healthy migration-safe Frigate baseline.
- OpenVINO detector process uses the shared Intel iGPU.
- VA-API is configured for future camera decoding.
- Cameras and MQTT are intentionally disabled in the live baseline because RTSP
  credentials, camera models and final MQTT material are not yet available.
- No production recordings exist; OMV archive storage remains future work.

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
ntfy, SearXNG, Whoogle, Watchtower monitor-only and Telegraf.

Paperless-ngx, Mealie, Actual Budget, Scrypted, Vaultwarden, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors.
- NAS monitoring remains a dashboard shell until OMV is built.

## Not built or not production-ready

- OMV NAS and NAS-backed backups/storage.
- Cameras, PoE switch and production Frigate camera/MQTT configuration.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S details and HA Bambuddy package deployment.
- HA HTTPS/same-origin proxy for embedded monitoring views.
- Obsidian recipe ingestion or Mealie deployment.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs cover VMs 100/102/103 with two generations and
CTs 111/114 with one interim local generation; consult
`scripts/backup/backup_strategy.md`.
