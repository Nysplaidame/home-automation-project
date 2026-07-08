---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-07-07
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

Last verified: **2026-07-07**.

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
- The bounded read-only SearXNG search tool, Mealie recipe tools, and Grocy
  add/list shopping-list tools are enabled for local LLM conversation agents
  through the `llamacpp_conversation` config.
  On 2026-07-07, docker-host firewall scope was updated so HA's Supervisor
  network `172.30.32.0/23` can reach SearXNG `8087/tcp`, Grocy `9283/tcp`, and
  Mealie `9925/tcp`; HA-side API proofs returned success for those backend
  paths. The Grocy voice path is intentionally limited to adding/listing
  shopping-list items, and a live Assist spoken prompt is still required before
  certifying the conversational path end to end.
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
  (`I51HJ`, firmware `v5.8.10 build 250917`) at reserved address
  `192.168.30.21`, with verified RTSP main/substream paths.
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
- Frigate HTTPS UI is live on `https://192.168.30.20:8971`; auth is enabled.
  Plain HTTP to port `8971` is rejected, while HA continues to use the internal
  unauthenticated API on `http://192.168.30.20:5000`.
- Frigate HTTPS now uses a `Home Local CA` signed certificate mounted from
  `/opt/frigate/tls` into `/etc/letsencrypt/live/frigate`. The certificate SANs
  include `192.168.30.20`, `frigate.home.local`, `frigate-nvr`, and `frigate`.
  This replaced Frigate's generated `FRIGATE DEFAULT CERT` so trusted Android
  and Apple browsers should not show the local certificate as untrusted.
- Direct Frigate PWA access off-WiFi is staged through docker-host Tailscale as
  a narrow `192.168.30.20/32` route with firewall access only to authenticated
  HTTPS port `8971`. The route still needs Tailscale admin-console approval and
  mobile-data validation before it is treated as complete.
- Recordings now write to OMV NFS storage. Proxmox mounts
  `192.168.40.50:/export/frigate` at `/mnt/omv/frigate`, CT 111 has
  `mp0: /mnt/omv/frigate,mp=/mnt/nas/frigate`, and Frigate maps
  `/mnt/nas/frigate:/media/frigate/recordings`. The cutover was validated on
  2026-07-07 with fresh MP4 segments under
  `/mnt/nas/frigate/2026-07-07/13/cam_01_annke_c500/`.
- CT-local `/opt/frigate/storage` remains the local media root/fallback for
  non-recording data. The OMV export has an ACL for host UID `100000`, which is
  CT 111's unprivileged root mapping; without that ACL Frigate could mount the
  export but could not create dated recording folders.
- Dormant NFS client/RPC units remain disabled inside CT 111 because the CT
  does not mount NFS directly.

## Local AI

- CT 114 runs llama.cpp `server-vulkan`, a dedicated llama.cpp embedding
  service, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord.
- llama.cpp serves `home-assistant-llm` from
  `Qwen3-14B-128K-Q4_K_M.gguf` at `192.168.20.104:8081/v1`; it runs with a
  `65536` token context, Q8 KV cache, reasoning disabled for normal assistant
  output, and Vulkan on Intel Meteor Lake graphics.
- The Qwen3 model file SHA-256 is
  `e6ad1ba102ef53dbc88aa59bd1bf1b10aaff298fea8f1a91f99e4312f1194c81`.
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
- SearXNG web search is reachable at docker-host port 8087, including from Home
  Assistant after the 2026-07-07 HA Supervisor-network docker-host firewall
  update.

## Docker host

Live workloads: Bambuddy, AdGuard Home, Immich, Homepage, Dozzle,
ntfy, SearXNG, Whoogle, Mealie, Grocy, Obsidian LiveSync/CouchDB, Watchtower
monitor-only and Telegraf. VM 103 has a 64 GiB virtual disk.

2026-07-05 docker-host guest-agent check:

- Root filesystem: `63G` total, `37G` used, `24G` available (`62%`).
- Immich OMV mount is present at `/mnt/omv/immich`
  (`192.168.40.50:/export/immich`, NFSv3).
- Mealie returned `HTTP/1.1 200 OK` on `127.0.0.1:9925`.
- Grocy returned `HTTP/1.1 302 Found` on `127.0.0.1:9283`; its local API
  returned HTTP `200` with the dedicated HA voice key on 2026-07-07.
- Obsidian LiveSync/CouchDB returned `HTTP/1.1 401 Unauthorized` on
  `127.0.0.1:5984`.

Immich now uses the OMV-backed NFS mount at `/mnt/omv/immich` for uploads and
library storage. Its database remains local under `/opt/stacks/immich/postgres`.
Mealie, Grocy, Obsidian LiveSync, and GardenKeeper now have documented
app-data or dump backup source paths targeting OMV `backups/docker-host`. A
read-only docker-host check on 2026-07-06 confirmed the source directories
exist: Mealie `15M`, Grocy `4.2M`, LiveSync `152K`, and GardenKeeper local
dumps `36K`. Proxmox confirmed OMV exports `backups/docker-host` to
`192.168.20.102`.

On 2026-07-07, the live OpenWrt `Docker Host to OMV NFS` rule was deployed,
docker-host mounted the OMV export at `/mnt/omv/docker-host-backups` using
NFSv3, and the first real app-data backup run `20260706T231304Z` wrote `20M`
under `runs/` while updating `latest/`. Restore smoke copied `latest/` to a
temporary directory, verified Mealie `mealie.db`, Grocy `grocy.db`, LiveSync
shards, and a GardenKeeper compressed SQL dump, then removed the temp copy.
`docker-host-app-data-backup.timer` is enabled and active for daily `03:45`
local runs. After the Grocy voice API key was added, backup run
`20260707T132647Z` completed and updated `latest/` to `22M`.

Paperless-ngx, Actual Budget, Scrypted, Vaultwarden, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors.
- OMV NFS TCP 2049 and Proxmox storage pressure are checked by
  `home-automation-health-check.timer`. Backup storage is intentionally on md0;
  the old 86-87% high-water warning was cleared by the 2026-07-05 Proxmox
  check showing `omv-backups` active at 54.21% used.

## Backup storage

- OMV is live on Storage VLAN 40 at `192.168.40.50`.
- Final backup storage lives on md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/`.
- Frigate/NVR recordings target md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/CCTV/`.
- OMV exports NFS paths for Proxmox backups, HA backups, docker-host backups,
  config backups, Immich DB backups, Immich media, and Frigate/NVR recordings.
- The Frigate export is mounted on the Proxmox host and bind-mounted into CT
  111 for recordings. CT 111 remains unprivileged and must not mount NFS
  directly.
- Home Assistant previously had Supervisor backup mount `nas_backups` pointing
  at `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`;
  manual backup `manual-nfs-md0-test-20260626` (`8294da47.tar`, 69 MiB) wrote
  successfully to OMV. During the 2026-07-02 HA native HTTPS cutover,
  `ha mounts info` reported no active mounts; this was resolved on 2026-07-03
  by restoring `nas_backups` and proving fresh writes. The pre-TLS HA backup was
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
- Fresh post-cutover proof on 2026-07-03 confirmed `nas_backups` still active,
  writable, and default. Manual backup
  `post-cutover-nas-backups-proof2-20260703-db-excluded`, slug `db7946c4`,
  wrote to `nas_backups` with `homeassistant_exclude_database: true`
  (81.51 MiB).
- HA automatic backups are configured for daily `03:00`, retained by count
  with `14` copies, and targeted only at `nas_backups`
  (`hassio.nas_backups`). The backup manager storage file was copied to
  `/config/.storage/backup.pre-auto-schedule-20260703-145639` before the
  direct storage edit and HA Core restart.
- Proxmox storage `omv-backups` uses NFSv3 to
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/proxmox`.
  It was active on 2026-07-05: `pvesm status` reported total
  `15501464576 KiB`, used `8403021824 KiB`, available `7098426368 KiB`
  (`54.21%`), and `df -h /mnt/pve/omv-backups` showed about `15T` total,
  `7.9T` used and `6.7T` available.
- Daily jobs cover VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00, snapshot
  mode, ZSTD, `keep-daily=7`, and `keep-monthly=6`.
- A manual VM 102 backup to `omv-backups` completed on 2026-06-26. Scheduled
  VM backups for 100, 102 and 103 completed again on 2026-07-05.
- The 2026-07-05 scheduled CT 111/114 backups initially failed because the
  unprivileged LXC backup process could not enter the NFS-backed temporary dump
  directory. The CT backup job
  `a8c84d38-2a73-4d9d-bf34-111114000001` now has `tmpdir: /var/tmp`; a manual
  CT 111 backup using that setting produced
  `vzdump-lxc-111-2026_07_05-23_11_08.tar.zst` (`23G`) on `omv-backups`.
  A manual CT 114 backup using the same setting then completed on 2026-07-06:
  `vzdump-lxc-114-2026_07_06-00_13_59.tar.zst`, archive size `15.30GB`,
  finished in `00:23:30`, with the temporary snapshot removed successfully.
  Proxmox warned that thin-pool autoextend protection is not enabled and that
  summed thin volume sizes exceed pool capacity; keep watching `local-lvm`
  pressure before large guest growth.
- Fresh VM 102 and CT 114 archives passed `zstd -t` on 2026-06-22. VM 102 also
  passed an isolated no-NIC restore/boot/guest-agent drill under temporary ID
  9102, which was purged after validation.
- Existing local archives remain retained during the transition.

## Not built or not production-ready

- Broader Frigate camera rollout beyond the first ANNKE bench camera, including
  new-camera validation, source updates, motion/zone tuning, and AI rules.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S details and HA Bambuddy package deployment.
- Same-origin HTTPS/reverse proxy for embedded monitoring views. HA native
  HTTPS is live, but Grafana/Kuma remain direct HTTP links rather than embedded
  iframes.
- Overwatch-to-Mealie recipe ingestion live prompt validation and remaining
  Grocy pilot product workflow testing.
- Obsidian LiveSync client wizard and second-device rollout; backend database,
  CORS preflight, local plugin install, backup proof, and Tailscale Serve
  mapping are live, but the admin laptop did not resolve the tailnet hostname
  during the 2026-07-07 check.

## Rollback and backup warning

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain 7 daily and 6 monthly generations on
`omv-backups`; projected retention fits the current md0-backed storage after
the 2026-07-05 capacity check, and both CT 111 and CT 114 have manual successful
proof after the `tmpdir=/var/tmp` change. Consult
`scripts/backup/backup_strategy.md`.
