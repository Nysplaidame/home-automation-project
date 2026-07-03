---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-07-03
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Last verified: **2026-07-03**.

## Compute

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.7.0, native HTTPS, MQTT, ESPHome and Assist |
| 101 | QEMU VM | frigate-nvr | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 102 | QEMU VM | monitoring | `192.168.60.10` | Live | Uptime Kuma, InfluxDB, Grafana and Telegraf |
| 103 | QEMU VM | docker-host | `192.168.20.102` | Live | Trusted Compose workloads and Tailscale routing |
| 104 | QEMU VM | llm-host | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 111 | unprivileged LXC | frigate-nvr | `192.168.30.20` | Live | Frigate 0.17.1, OpenVINO and VA-API on shared iGPU |
| 114 | unprivileged LXC | llm-host | `192.168.20.104` | Live | llama.cpp, Open WebUI and Wyoming voice services on shared iGPU |

VM 101 and VM 104 are retained temporarily as rollback points. Production DNS
and static addresses belong to CT 111 and CT 114. Never start either retired VM
while its replacement LXC is running.

## Home Assistant

- Configuration check passes on HAOS 2026.7.0.
- Native HA HTTPS is live at `https://192.168.20.101:8123` using
  `/ssl/fullchain.pem` and `/ssl/privkey.pem`, signed by local
  `/ssl/ca.crt` (`Home Local CA`). HTTP on port `8123` is no longer the active
  HA UI.
- `homeassistant.internal_url` is set to `https://192.168.20.101:8123`;
  `external_url` is intentionally unset.
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
- Frigate integration in Home Assistant is live using Frigate API URL
  `http://192.168.30.20:5000`; the first camera's Frigate entities and
  Advanced Camera Card CCTV views are available in HA.

## Frigate

- CT 111 runs Frigate 0.17.1 live on the shared Intel iGPU.
- OpenVINO detector process uses the shared Intel iGPU.
- VA-API is configured and active for camera decoding.
- One bench camera is now identified and reachable on VLAN 30: ANNKE C500
  (`I51HJ`, firmware `v5.8.10 build 250917`) at temporary DHCP address
  `192.168.30.108`, with verified RTSP main/substream paths and a planned
  reservation at `192.168.30.21`.
- Camera RTSP auth required switching the camera from RTSP `Digest` to
  `Digest/Basic`; after that change, Frigate confirmed live ingest at roughly
  `10 fps` on the first bench camera using substream detect and mainstream
  record roles.
- Live CT 111 carries the accepted one-camera config and live
  `/opt/frigate/.env`; repository source now mirrors the first-camera layout
  with RTSP and MQTT secrets represented only as environment placeholders.
  `configs/frigate/config-baseline.yml` remains the no-camera migration-safe
  fallback.
- HA validates Frigate API version/stats and sees the first camera through the
  Frigate integration.
- No production recordings exist; OMV archive storage remains future work.
- Dormant NFS client/RPC units are disabled because this unprivileged LXC has no
  NFS mount; this removes the failed `run-rpc_pipefs.mount` unit. Re-enable the
  client only as part of an approved NAS-recordings cutover.

## Local AI

- CT 114 runs llama.cpp `server-vulkan`, a dedicated llama.cpp embedding
  service, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord.
- llama.cpp serves `home-assistant-llm` from the reused local GGUF at
  `192.168.20.104:8081/v1`; the container reports Vulkan on Intel Meteor Lake
  graphics and responds to OpenAI-compatible chat completions.
- A dedicated llama.cpp embeddings service serves `home-assistant-embedding`
  from `bge-small-en-v1.5-q8_0.gguf` at `192.168.20.104:8082/v1`; it returns
  384-dimensional embeddings and is source-scoped to docker-host for Household
  Hub.
- Live llama.cpp image digest:
  `ghcr.io/ggml-org/llama.cpp@sha256:4e784358f638549d95bd22fb814c1afeed1af71fbd4b70c25f23eae01caaa6af`.
- Whisper starts offline from persistent model/tokenizer data.
- HA can reach ports 8081, 10200, 10300 and 10400 through source-scoped
  host and Docker firewall policy. HA uses `192.168.20.104:8081/v1` for the
  llama.cpp conversation agent.
- Docker-host can reach CT 114 ports 8081, 8082 and 3002 for Household Hub
  assistant integration. Household Hub production RAG uses CT 114 chat on 8081,
  embeddings on 8082, and local Qdrant on VM 103.
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
- Home Assistant previously had Supervisor backup mount `nas_backups` pointing
  at `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`;
  manual backup `manual-nfs-md0-test-20260626` (`8294da47.tar`, 69 MiB) wrote
  successfully to OMV. During the 2026-07-02 HA native HTTPS cutover,
  `ha mounts info` reported no active mounts, so the OMV HA backup mount needs
  revalidation/restoration before depending on it. The pre-TLS HA backup was
  created locally as `pre-ha-native-tls-20260702-db-excluded`, slug `04da1c7d`.
- On 2026-07-03, the Zyxel GS1900-8HP was moved from the temporary VLAN 30
  bench posture to the intended managed-switch layout: router `lan3` is a
  tagged trunk for VLANs 1/10/30/40, switch management is on VLAN 10 at
  `192.168.10.12`, the first camera is on untagged VLAN 30 port 2, and OMV is
  on untagged VLAN 40 port 8. Router ARP confirmed OMV at
  `a8:b8:e0:0a:93:7d` on VLAN 40. The GS1900 Save action was invoked after
  the cutover and the switch remained reachable at `192.168.10.12`.
- HA Supervisor mount `nas_backups` is active again and set as the default
  backup mount. Manual backup
  `post-switch-trunk-nas-backups-20260703-db-excluded`, slug `3e3b1ecb`,
  wrote successfully to `nas_backups` (102.01 MiB).
- HA automatic backups are configured for daily `03:00`, retained by count
  with `14` copies, and targeted only at `nas_backups`
  (`hassio.nas_backups`). The backup manager storage file was copied to
  `/config/.storage/backup.pre-auto-schedule-20260703-145639` before the
  direct storage edit and HA Core restart.
- Proxmox storage `omv-backups` uses NFSv3 to
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox`.
  It was active after the switch trunk cutover, with md0 still high at 86.64%
  used.
- Daily jobs cover VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00, snapshot
  mode, ZSTD, `keep-daily=7`, and `keep-monthly=6`.
- A manual VM 102 backup to `omv-backups` completed on 2026-06-26.
- Fresh VM 102 and CT 114 archives passed `zstd -t` on 2026-06-22. VM 102 also
  passed an isolated no-NIC restore/boot/guest-agent drill under temporary ID
  9102, which was purged after validation.
- Existing local archives remain retained during the transition.

## Not built or not production-ready

- Source-controlled Frigate first-camera config and broader camera rollout.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S details and HA Bambuddy package deployment.
- Same-origin HTTPS/reverse proxy for embedded monitoring views. HA native
  HTTPS is live, but Grafana/Kuma remain direct HTTP links rather than embedded
  iframes.
- Overwatch-to-Mealie recipe ingestion live prompt validation and Grocy
  workflow/integration.
- Obsidian LiveSync client rollout; its Tailscale Serve HTTPS endpoint is live.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain 7 daily and 6 monthly generations on
`omv-backups`; projected retention fits after the planned md0 cleanup, while
the current high utilization remains a warning. Consult
`scripts/backup/backup_strategy.md`.
