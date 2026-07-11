---
title: July 2026 Sanitized Live Evidence
created: 2026-07-10
modified: 2026-07-10
type: audit-evidence
status: discovery-frozen
---

# Sanitized Live Evidence

Evidence was collected read-only between 2026-07-09 and 2026-07-10 in the
Europe/London timezone. Secret values, camera credentials, session tokens,
private keys, and raw conversation logs are excluded.

## Network and trust plane

| Component | Observed state | Audit consequence |
|---|---|---|
| OpenWrt | Live VLAN 50 remains internally named `iot_sensors`; source renamed it `HomeIoT`. Old-name interface, DHCP, Wi-Fi, MQTT allow, DNS/internet deny, and self-ping checks pass. New-name full test fails 9 checks. | Current live segmentation works, but deploying current source without a migration plan is unsafe. |
| Router TLS | TLS 1.3, self-signed `OpenWrt` certificate, no management-IP SAN, expires 2026-10-21. | Windows trust fails; replacement is approval-gated. |
| Tailscale router | Advertises four narrow `/32` routes: HA, Frigate, OMV, and monitoring. Shields Up and web client are disabled. | Route approval and tailnet ACL/grant policy could not be read because the admin session had expired. |
| WireGuard | Present only as dormant/fallback intent. | Failover is unproved and requires a controlled test. |
| Managed switch | Login surface reachable over HTTP; TLS is 1.2 with a generic self-signed certificate and no SAN. Credentials were not available in-session. | VLAN/PVID/trunk/PoE and save-to-startup state remain unverified. |
| OMV management | HTTP management is live; no listener on 443. | Administrative credentials and configuration traverse the management VLAN without TLS. |
| Client CA | Home Local CA is present in the Windows current-user root store. | HA works in the browser; Frigate shows client-specific Schannel/revocation behaviour despite a correct IP SAN. |

Official Docker guidance confirms that published container traffic is diverted
before UFW's normal chains. Therefore Docker-host and monitoring access claims
must be proved at `DOCKER-USER` and the router, not inferred from UFW status.

## Proxmox

- Proxmox VE 9.1.9, kernel 7.0.0-3-pve, approximately 62 GiB RAM.
- VMs 100, 102, and 103 and CTs 111 and 114 are running; VMs 101 and 104 are
  stopped rollback/retired guests.
- VM configuration has larger memory values than the running guests will use
  until their next approved restart.
- `/` is 81% used while `pvesm local` reports 76%; the five-minute health
  script checks the latter and reports all 15 checks healthy.
- `local-lvm` thin data is 22.78% overall, but CT 111's individual volume is
  99.81% allocated.
- No host failed units, guest locks, or snapshots were observed.
- PVE TLS has a correct IP/DNS SAN and expires 2028-03-07, but the Windows
  client does not trust the PVE CA.

## Home Assistant

- Core 2026.7.1, Supervisor 2026.06.2, HAOS 18.1; supported and healthy.
- `ha core check` passes; native HTTPS is active.
- The active HA, VentSys, script, scene, automation, and custom conversation
  source is behaviourally aligned with the repository, apart from comments,
  descriptions, and order. Activation of the newest conversation code after a
  restart was not proven.
- `nas_backups` is the default active NFS backup target. Automatic backups run
  daily at 03:00 and retain 14, but include HA settings and SSL only; add-ons
  are not selected. The last complete run was 2026-07-09 03:00.
- Started apps include Mosquitto, File Editor, Terminal & SSH, ESPHome, Samba,
  and Sonarr. MQTT IO is stopped. Advanced SSH & Web Terminal is in error
  because its host port conflicts with the core SSH app; it is still boot-auto,
  host-networked, manager-role, Docker-API-enabled, and AppArmor-disabled.
- Sonarr 0.5.0 consumes about 231 MB and is undocumented in the canonical
  service, access, and backup model.
- 438 entities were observed, 215 disabled; large groups include ESPHome,
  Frigate, and mobile entities.
- Detailed conversation/tool traces are being written to HA logs. Review found
  a shopping request routed to recipe history and a recipe-substitution phrase
  causing a bounded import write attempt without a safe confirmation flow.
  Private household content is intentionally omitted.

## Frigate and CCTV

- Frigate 0.17.1 is healthy on CT 111; its image digest was recorded and the
  release contains upstream security fixes for raw-config and cross-camera
  authorization.
- Root filesystem is 93% used (about 2.2 GiB free); the CT thin volume reports
  99.81% allocated.
- About 20.4 GiB of pre-cutover recordings remain on local storage. Current
  recordings are being written to OMV NFS; 18 new NFS files appeared in a
  15-minute observation and no new local recording did.
- One camera is reachable through authenticated vendor APIs. Firmware is
  V5.8.10 build 250917. The camera runs near 10 fps; the detector process is
  alive but live detection is disabled.
- Live config explicitly disables detection; repository config does not, so a
  redeploy could change behaviour.
- MQTT is enabled over TLS on 8883; recording keeps motion for 7 days and
  alerts/detections for 14 days.
- Desktop and mobile HA CCTV views load and stream. The primary view is unnamed
  and initial rendering takes roughly 11 seconds with a DOM transition timeout
  logged by the browser.
- Frigate's certificate has correct IP/DNS SANs and expires 2028-10-07.

## Docker host applications

- Debian 13, root 67%, 3.8 GiB RAM with about 1.2 GiB available and no swap.
- Twenty-seven containers were observed. Immich is restart-looping/unhealthy
  because `/mnt/omv/immich` failed to mount at boot on 2026-07-06. The local
  fallback directory is empty, so no media was silently written to the root
  disk. NFS reachability works now, but remount/restart is remediation.
- Immich's environment file and several Mealie secret files are readable more
  broadly than necessary on the host. Values were not collected.
- App-data backup runs at 03:45 and currently captures Mealie, Grocy,
  LiveSync, and GardenKeeper. It does not capture Household Hub PostgreSQL,
  Qdrant, Redis, Bambuddy, or Immich.
- Household Hub and GardenKeeper live source trees have no `.git` provenance.
  Household Hub and Bambuddy lack equivalent canonical repository stacks.
- Live Compose matches source for AdGuard, Dozzle, GardenKeeper, Grocy,
  Homepage, Mealie, LiveSync, SearXNG, Telegraf, and Whoogle. Immich, ntfy, and
  Watchtower differ.
- UFW is default-deny and `DOCKER-USER` is populated with source-scoped rules.
  Negative tests remain required. About 25.5 GB of Docker images is
  reclaimable, but no prune was performed.

## OMV and storage

- Debian 13 and OMV 8.4.0-3. `md0` is a clean 14.55 TiB RAID1 at 58% usage;
  all four observed disks report SMART passed.
- Monthly md checks, filesystem scrub, and trim timers exist.
- `omv-hddfanctrl.service` and two quota units are failed.
- NFS exports include duplicate/legacy paths and multiple client-restricted
  `no_root_squash` exports.
- Three bind mounts reference deleted source paths, including the `/export/configs`
  and `/export/ha-backups` aliases. Current HA uses a separate direct backup
  path and remains operational.
- Current Frigate media is under the md0 `frigate` path, not the documented
  `CCTV/` path. A legacy direct `CCTV` export is still advertised.
- `/etc/openmediavault/config.xml` exists, but no copy was found under storage;
  the exported `backups/configs` directory is empty. No regular OMV restore
  workflow is documented by the vendor beyond retaining this configuration as
  rebuild reference.
- Transfer Portal is enabled but has restarted more than 46,000 times because
  its unit binds the obsolete address `192.168.10.147:8088` instead of the
  current OMV address.

## Monitoring and operations

- Monitoring VM: Debian 13, root 22%, 1.9 GiB RAM with about 644 MiB available,
  no swap, no failed host units.
- Grafana, InfluxDB, Telegraf, and Kuma are live; only Kuma declares a
  container health check. Grafana dashboards render current data.
- Kuma has 27 active monitors: 24 up and three down. The down monitors are HA
  using a stale HTTP probe, the real Immich outage, and a retired Ollama API.
  There is no monitor for the active llama.cpp chat API.
- `DOCKER-USER` is empty on the monitoring host even though Docker ports are
  published to the monitoring address. Router enforcement is therefore the
  only confirmed network control.
- Monitoring data is protected only by the VM 102 backup. Kuma has only old
  manual database copies; no current scheduled app-consistent export was found.
- The Proxmox health script produces a false-green estate summary: it skips the
  deployed Frigate UI, misses CT 111 disk pressure and current application
  outages, and checks `pvesm local` instead of root filesystem usage.

## Local AI and voice

- CT 114 is healthy with six containers: chat and embedding llama.cpp
  services, Open WebUI, Whisper, Piper, and OpenWakeWord.
- Root is 34%; 20 GiB RAM has only about 2.4 GiB available and no swap under
  current model load. iGPU mappings are active.
- Chat and embedding models are locally present. No error-like container logs
  were found in the prior 24 hours.
- Images for llama.cpp, Open WebUI, and Wyoming services use floating tags;
  Wyoming services have no explicit health checks.
- UFW retains obsolete Ollama 11434 allows even though Ollama is absent.
- Tool-routing evidence shows that the architectural rule “AI must not control
  safety-critical logic directly” exists in design, but adversarial prompt and
  authorization tests have not been run.

## Backup observations

- Proxmox jobs run VMs 100/102/103 at 02:00 and CTs 111/114 at 04:00 to OMV,
  keeping 7 daily and 6 monthly. Latest jobs completed and archive counts are
  6, 7, 6, 4, and 4 respectively.
- OMV backup storage is 58% used. Low-priority `zstd -t` checks reached and
  passed the newest 2026-07-09 archive for each active guest (VMs 100/102/103
  and CTs 111/114). CT 114 was repeated with captured result `rc=0` in 101
  seconds after the initial SSH wrapper lost its output channel. This proves
  compressed-stream integrity only; no isolated restore was run.
- The docker-host app-data job starts at 03:45 while CT backups start at 04:00,
  creating shared OMV and application I/O overlap.
- Backups, production media, and many configuration copies share OMV/md0 and
  the same trust domain. No independent/off-site critical-data copy was proved.

## Access not obtained or tests not run

- Managed-switch authenticated configuration and persistence.
- Tailnet route approval, ACL/grant policy, and identity ownership.
- Upstream-router configuration and power/UPS behaviour.
- Password-manager uniqueness/recovery status beyond account-class evidence.
- Physical VentSys hardware, electrical isolation, calibration, and emergency
  actuation; hardware is not yet available.
- Isolated restores, firewall deny tests, DNS interruption, route withdrawal,
  camera outage, NFS outage, HA/Frigate restart, and shared-iGPU saturation.

These are explicit blockers, not silent passes.
