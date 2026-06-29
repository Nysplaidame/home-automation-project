---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-06-28
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Last verified: **2026-06-26**.

## Compute

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.6.4, MQTT, ESPHome and Assist |
| 101 | QEMU VM | frigate-nvr | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 102 | QEMU VM | monitoring | `192.168.60.10` | Live | Uptime Kuma, InfluxDB, Grafana and Telegraf |
| 103 | QEMU VM | docker-host | `192.168.20.102` | Live | Trusted Compose workloads and Tailscale routing |
| 104 | QEMU VM | llm-host | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 111 | unprivileged LXC | frigate-nvr | `192.168.30.20` | Live baseline | Frigate 0.17.1, OpenVINO and VA-API on shared iGPU |
| 114 | unprivileged LXC | llm-host | `192.168.20.104` | Live | llama.cpp, Open WebUI and Wyoming voice services on shared iGPU |

VM 101 and VM 104 are retained temporarily as rollback points. Production DNS
and static addresses belong to CT 111 and CT 114. Never start either retired VM
while its replacement LXC is running.

## Home Assistant

- Configuration check passes on HAOS 2026.6.4.
- Mosquitto, File Editor, Terminal & SSH and ESPHome Device Builder are live.
- The Home Assist pipeline uses Home Assistant's built-in conversation agent.
- The Overwatch Assist pipeline points at `llamacpp_conversation`, a local
  Home Assistant custom conversation agent for llama.cpp's OpenAI-compatible API.
- The bounded read-only SearXNG search tool and Mealie recipe tools are enabled
  for local LLM conversation agents through the `llamacpp_conversation` config.
  A live Overwatch UI/voice prompt is still required before certifying the
  conversational path end to end.
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

- CT 114 runs llama.cpp `server-vulkan`, Open WebUI, Wyoming Whisper, Piper and
  OpenWakeWord.
- llama.cpp serves `home-assistant-llm` from the reused local GGUF at
  `192.168.20.104:8081/v1`; the container reports Vulkan on Intel Meteor Lake
  graphics and responds to OpenAI-compatible chat completions.
- Live llama.cpp image digest:
  `ghcr.io/ggml-org/llama.cpp@sha256:4e784358f638549d95bd22fb814c1afeed1af71fbd4b70c25f23eae01caaa6af`.
- Whisper starts offline from persistent model/tokenizer data.
- HA can reach ports 8081, 10200, 10300 and 10400 through source-scoped
  host and Docker firewall policy. HA uses `192.168.20.104:8081/v1` for the
  llama.cpp conversation agent.
- SearXNG web search is reachable at docker-host port 8087.

## Docker host

Live workloads: Bambuddy, AdGuard Home, Immich, Homepage, Dozzle,
ntfy, SearXNG, Whoogle, Mealie, Grocy, Obsidian LiveSync/CouchDB, Watchtower
monitor-only and Telegraf. VM 103 has a 64 GiB virtual disk.

Immich now uses the OMV-backed NFS mount at `/mnt/omv/immich` for uploads and
library storage. Its database remains local under `/opt/stacks/immich/postgres`.

Paperless-ngx, Actual Budget, Scrypted, Vaultwarden, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors.
- OMV NFS TCP 2049 and Proxmox storage pressure are checked by
  `home-automation-health-check.timer`. Backup storage is intentionally on md0;
  capacity remains tight until the planned cleanup frees roughly 4 TiB.

## Backup storage

- OMV is live on Storage VLAN 40 at `192.168.40.50`.
- Final backup storage lives on md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/`.
- Frigate/NVR recordings target md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/CCTV/`.
- OMV exports NFS paths for Proxmox backups, HA backups, docker-host backups,
  config backups, Immich DB backups, Immich media, and Frigate/NVR recordings.
- The Frigate export is discoverable from CT 111, but CT 111 is an unprivileged
  LXC and cannot mount NFS directly. OMV now also allows Proxmox host
  `192.168.10.10` to mount `/export/frigate`; a temporary Proxmox mount,
  write/read/delete, and unmount test passed on 2026-06-28. Future recording
  cutover should mount the OMV Frigate export on the Proxmox host and
  bind-mount it into CT 111.
- Home Assistant has an active Supervisor backup mount `nas_backups` pointing at
  `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`;
  manual backup `manual-nfs-md0-test-20260626` (`8294da47.tar`, 69 MiB) wrote
  successfully to OMV.
- Proxmox storage `omv-backups` uses NFSv3 to
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox`.
- Daily jobs cover VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00, snapshot
  mode, ZSTD, `keep-daily=7`, and `keep-monthly=6`.
- A manual VM 102 backup to `omv-backups` completed on 2026-06-26.
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
- Overwatch-to-Mealie recipe ingestion live prompt validation and Grocy
  workflow/integration.
- Obsidian LiveSync client rollout; its Tailscale Serve HTTPS endpoint is live.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain 7 daily and 6 monthly generations on
`omv-backups`; projected retention fits after the planned md0 cleanup, while
the current high utilization remains a warning. Consult
`scripts/backup/backup_strategy.md`.
