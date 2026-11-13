---
title: Current Live State
description: Canonical inventory of deployed hosts, services, and deliberately deferred components
tags: [reference, current-state, infrastructure]
created: 2026-06-20
modified: 2026-10-19
type: reference
status: active
---

# Current Live State

This is the canonical current-state inventory. Rebuild manuals describe how to
build from blank and must link here rather than duplicating live-status claims.

**Code remediation, 2026-10-02:** canonical source fixes are tested but not
deployed. Read-only OMV inspection confirms active TransferPortal still imports
the older helper without ROOT_POLICY and its wrapper lacks isolated imports.
Matched checkpoint `20261002T211810Z` and isolated no-NIC VM restore/preview/copy
acceptance passed for saved and repaired generations; historical rows and source
hashes were preserved. The protected NAS checkpoint remains; the test VM/media
were removed. Live replacement is still outstanding. VentSys hardware commissioning gates remain disabled.
See [[../audits/2026-10-02-code-audit-verification]] and the TransferPortal manual.

**Bambuddy scheduled offline updates, 2026-10-02:** the owner authorized this
service exception. Windows task `Bambuddy Offline Release Staging` checks and
stages stable versioned images daily at09:00 while Admin is signed in, using
the existing Ubuntu WSL Docker engine and strict-host-key SSH. VM103's
`bambuddy-offline-update.timer` installs local bundles at04:30 with half-hourly
idle-gated retries through06:30, Europe/London, without registry pulls. Checkpoints
are on OMV under `/mnt/omv/docker-host-backups/bambuddy-updates`; three successful
update generations are retained. At10:47 BST the first manual1.2.5.5→1.2.5.6
run passed copied-data startup/migration with networking disabled, stopped-service
NAS backup, SQLite integrity, running image/network identity and P1S reconnection.
Host networking remains in place; no firewall change was made. Watchtower remains
monitor-only. Dynamic installed version/result is recorded in VM103's
`/var/lib/home-automation-updates/bambuddy/last-result.json`; unattended-window
acceptance remains open. See [[../procedures/bambuddy_offline_updates]].

**Scoped read-only refresh, 2026-10-02 10:37 BST:** the Windows collector reports
11/12 endpoint checks passing; Camera1 RTSP fails consistently with intentional
disconnection. OMV BatchMode management login works and all five disks report
SMART health passed at 30–47 C with no reported pending/offline-uncorrectable
sectors. md0 is `[UU]` and an existing consistency check is 46.7% complete;
this audit did not start or alter it. One current RAID member reports lifetime
UDMA CRC count 1; compare stable disk identities before inferring a change.
These checks do not prove application recovery or HTTP certificate trust.
September14–17 Proxmox access/import, VM102 isolated boot and Watchtower
server-delivery acceptance supersede their older blockers below; phone receipt
remains open. See [[../audits/2026-10-02-roadmap-code-file-audit]].

**CT114 read-only diagnosis, 2026-10-02 10:48 BST:** Fail2ban is not installed;
the earlier `inactive` description did not establish an installed service.
APT has no proxy; security/update metadata expired June26. Native cache-host
UFW logs prove rejected `.104 -> .102 TCP3142` requests. Cache report-page
loopback access works, but Debian upstream metadata through it returns503.
All seven AI containers remain running. The host-only permission/proxy repair
is prepared and tested locally, not deployed; see
[[../procedures/ct114-package-path-repair]].

**CT114 package-path refresh, 2026-10-04:** Fail2ban remains absent and no HTTP
APT proxy is configured. CT114's cache probe returns no HTTP response (timeout),
while apt-cacher-ng is active and loopback Debian InRelease still returns503.
Cached headers retain June19 dates/June26 expiry. The firewall rejection was
proven October2; this refresh does not independently re-prove its cause.
No firewall, package, proxy or service configuration was changed.

**Scoped update, 2026-09-10:** the troubleshooting dashboard evidence-age update
is deployed at management port8094, with live desktop/mobile verification and
a fresh Windows 12-pass/one-disconnected-camera-failure snapshot. This does not
refresh the whole-system September7 audit below. Proxmox collector deployment
and real mount/guest-backup acceptance remain blocked by SSH key denial. See
the current handoff for the deployment and IPv6 policy discrepancy.

**Read-only health refresh, 2026-09-07:** management workstation 12/13 endpoint
checks pass; Camera1 RTSP is the sole failure, consistent with intentional
camera disconnection. VM103 has 38 running containers, all defined health
checks healthy; app-data backup service reports success at 03:50:33 BST today.
Root disk is 75% used; Immich NFS is 60%. These are availability/job-result
observations, not new functional, certificate-trust or restore acceptance.
VM102 Fail2ban is active; CT114's is inactive and its APT cache/direct-HTTP
paths fail, with stale June security metadata. Watchtower remains monitor-only
but its ntfy delivery fails with attachment-policy error40014. Direct Proxmox
and OMV SSH keys are denied, so guest-backup freshness and SMART remain
unverified today. See the update review log and current handoff for limits.

**Router follow-up, 2026-09-04 16:48 BST:** authenticated LuCI/SSH confirms
vanilla OpenWrt **24.10.3**, kernel **6.6.104**. Workstation key access via
`home-router-lan` is installed and proven; private key remains outside the
vault. HomeAdmin is live at channel 100/HE80 (auto channel), with PC signal
around -76 dBm and 432 Mbps download PHY. The old Zyxel station is now disabled,
2.4 GHz APs are up, and LAN2/Hive appear on cloud-IoT VLAN 55 (`192.168.55.10`).
Those last changes were observed, not implemented or functionally accepted by
the throughput task. See the current handoff for measurement limits and the
separate repair task for service/Hive acceptance.

**Post-fibre recovery, 2026-09-04:** IPv4 internet and core services recovered.
Zen/Openreach WAN is untagged PPPoE on `eth1`; all 48 local DNS aliases pass.
VM 103 runs with 6144 MiB after a graceful restart; Homepage, AdGuard, Immich
and Dozzle respond again and all defined container health checks pass.
All five 2.4 GHz APs are up after disabling the retired Zyxel Wi-Fi station.
Proxmox reports 64 GB installed; earlier 32 GB notes are stale.

LAN2 is now untagged **VLAN 55 cloud_iot** with Hive reserved at
**192.168.55.10**; WAN forwarding only, router DHCP/DNS/NTP, no internal
forwarding. DHCP, bidirectional internet TLS traffic and router NTP are
verified. **Hive still appears offline in the owner's app**; prior issues
remain unresolved and application/account acceptance is pending.
OMV is directly on **LAN4 / VLAN40**, reachable with active NFS mounts.
The Zyxel switch/cameras are deliberately unplugged. The P1S (`Da Printor`) is
commissioned on VLAN35 through Bambuddy: its MQTT telemetry is live in Home
Assistant, the **P1S** dashboard is available at `/p1s-status`, and phone plus
persistent notifications are enabled. The direct printer camera and any
physical safety interlock work remain separate acceptance items.

**OrcaSlicer virtual-printer compatibility, 2026-10-29:** `Da Printor VP`
was working with the locally installed **OrcaSlicer 2.4.2** (build `8500fcdc`).
The subsequent **2.5.0-beta** reinstall completes the VP's LAN detect exchange
but returns `code=-1` before opening its MQTT session; connectivity, certificate
and access-code validation on the Bambuddy side passed. Keep the production
workflow on 2.4.2 until the newer Orca network path is separately accepted; do
not change P1S firmware, firewall, VLAN rules or Bambuddy configuration to
compensate for this desktop-client regression.

**IPv6 accepted 2026-09-11:** Zen now delegates `2a02:8013:781f::/48` by
DHCPv6-PD. The router requests the prefix only because Zen returns
`NoAddrsAvail` for IA_NA. A separate static interface uses the supplied ND
prefix and Zen's link-local next hop for the default route. Both interfaces
are up after a network reload; IPv4 and IPv6 internet pings pass at about
15 ms. The existing LAN interface receives a delegated global assignment;
restricted VLANs were not newly enabled for IPv6. Saved router source is
reconciled for this arrangement, PPPoE and VLAN55; compiler refuses missing
PPPoE credentials for deployment.
Preview builds are not deployed. See
[[../../HANDOFF-2026-07-27-portal-services]] for evidence, backups and limits.

Full state verification: **2026-08-09**. Core endpoint reachability, including
Recomp Tracker, was rechecked on **2026-08-19**; this does not replace the
recorded functional acceptance checks. Homepage's fixed mobile proxy routes and
their Tailscale grant were server-side rechecked on **2026-08-21**. The
canonical architecture references, diagrams, active setup guides and generated
Mermaid Viewer source were reconciled against that evidence and the tracked
configuration on **2026-08-25**. A management-workstation endpoint spot check
that day passed router, Frigate, docker-host, Bambuddy, MQTT TLS, Grafana, Kuma,
llama.cpp, OMV NFS and Frigate HTTPS; Home Assistant returned HTTPS `200` via
`curl -k`. The PowerShell health-check HTTP implementation was corrected after
it misreported that trusted-local-CA response as `HTTP 0`.

The Household admin workstation joined Tailscale on 2026-07-13 as
`household-admin-workstation` (`100.95.209.14`). Tailnet peer discovery and
WireGuard connectivity to docker-host pass, but the current tailnet ACL denies
service and SSH connections from the new device. Management-VLAN access remains
available through the explicit `192.168.20.0/24` route while ACL approval is
completed in the Tailscale admin console.

The canonical OpenWrt and service-matrix inventories contain 48 authoritative
`home.local` aliases. They were deployed to live OpenWrt on 2026-07-29 and
dnsmasq restarted successfully. The full
`scripts/validation/validate-home-local-dns.ps1 -DnsServer 192.168.10.1` run
passed all 48 aliases after temporarily disconnecting Mullvad's DNS leak
protection; Mullvad was reconnected immediately afterward. The now-redundant
workstation hosts entry for `homeassistant.home.local` was removed with an
elevated edit on 2026-07-29 and the Windows DNS cache was flushed.

## September 14 backup and recovery verification

GardenKeeper backup failure handling was repaired/deployed September12; the
latest unit status is success. MediaMTX's separate configuration-backup timer
is enabled for03:35, and its September14 run succeeded. Recording deletion stays
disabled per owner choice. September12 isolated source-build/database/API/Qdrant
proof is recorded in the current handoff; production application containers were
not replaced. These component tests do not certify full-system recovery.

## Compute

**October10 resource audit:** all eight configured guests inspected; production
100/102/103/111/114 running, rollback101/104 and restore9102 stopped. VM102 is
now2CPU/6GiB after a graceful shutdown/start (Grafana historical OOM September17);
Grafana/Influx/Kuma recovered. VM103 remains4CPU/10GiB and its root disk expanded
online64→128GiB, reducing filesystem use88→44%. CT111 is2CPU/6GiB after lifecycle repair, CT114
6CPU/28GiB, HA2CPU/6GiB. Actual usable memory is ample; cache-inclusive Proxmox
VM RAM percentages must not be interpreted as pressure. Host has~25GiB available;
root81% (64GiB local backups), thin data~26.7%, metadata~1.1%. No backups removed.

`resource-pressure-monitor.timer` runs every minute on Proxmox with actual
guest/cgroup usable memory, OOM deltas, PSI, CPU/load/blocked tasks, root/thin
capacity, new kernel disk/hang warnings and lost-coverage checks. All six systems
sample successfully. Debounced pressure/recovery and immediate event alerts
route to the existing authenticated ntfy monitoring topic; test accepted.
An hourly Codex watchdog checks monitor freshness/failure without duplicating
normal alerts. Source, thresholds, limitations and operations:
[[../procedures/resource_pressure_monitor]]. Phone presentation is not yet
independently verified. Frigate lifecycle repair is deployed; real-camera acceptance remains open.

October11: error handling improved—inventory timeouts retain fresh host/guest
collection with explicit degraded coverage; collection failures debounce and
recover, failed deliveries remain queued, OOM baselines survive missing samples.
Notifier cooldown moved from systemd start limiting to durable application
state, and the old failed status was cleared. Ten tests and live coverage pass.
The watchdog reads supported `--status` including health and pending delivery.

| ID | Kind | Name | Address | State | Role |
|---:|---|---|---|---|---|
| 100 | QEMU VM | home-assistant | `192.168.20.101` | Live | HAOS 2026.7.1, native HTTPS, MQTT, ESPHome and Assist |
| 101 | QEMU VM | frigate-nvr | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 102 | QEMU VM | monitoring | `192.168.60.10` | Live | Uptime Kuma, InfluxDB, Grafana and Telegraf |
| 103 | QEMU VM | docker-host | `192.168.20.102` | Live | Trusted Compose workloads and Tailscale routing |
| 104 | QEMU VM | llm-host | offline | Rollback only | Pre-LXC snapshot; `onboot=0` |
| 111 | unprivileged LXC | frigate-nvr | `192.168.30.20` | Live | Frigate 0.17.1, OpenVINO and VA-API on shared iGPU |
| 114 | unprivileged LXC | llm-host | `192.168.20.104` | Live | llama.cpp, Open WebUI and Wyoming voice services on shared iGPU |
| 9102 | QEMU VM | monitoring restore | offline | Stopped | Retained isolated restore guest |

VM 101 and VM 104 are retained temporarily as rollback points. Production DNS
and static addresses belong to CT 111 and CT 114. Never start either retired VM
while its replacement LXC is running.

## Home Assistant

- Configuration check passes on HAOS 2026.7.1.
- Native HA HTTPS is live at `https://192.168.20.101:8123` using
  `/ssl/fullchain.pem` and `/ssl/privkey.pem`, signed by local
  `/ssl/ca.crt` (`Home Local CA`). HTTP on port `8123` is no longer the active
  HA UI.
- `homeassistant.internal_url` is `http://ha-media.home.arpa:8124` (2026-11-11; set in `configuration.yaml` since 2026-11-13, because a UI-only value is overwritten by the YAML key on every restart): the docker-host `ha-media-proxy` that exposes only TTS/announcement media paths over plain HTTP for ESPHome voice satellites. It was found empty after the 2026.11 SSL-profile migration; HA ignores IP-only URLs under SSL, ESP32s cannot resolve `*.local` via unicast DNS, and stock Voice PE firmware does not trust the private CA. See `configs/docker-host/stacks/ha-media-proxy/README.md`;
  `external_url` is intentionally unset.
- Mosquitto, File Editor, Terminal & SSH and ESPHome Device Builder are live.
- The Home Assist pipeline uses Home Assistant's built-in conversation agent.
- The Overwatch Assist pipeline points at `llamacpp_conversation`, a local
  Home Assistant custom conversation agent for llama.cpp's OpenAI-compatible API.
  Since 2026-11-13 (decision 10, phase 1) it offers every configured tool API on every turn with one prompt
  (`configs/home-assistant/overwatch-prompt.txt`), plus its own `overwatch_utility` API (`calculate` for exact
  arithmetic, `date_info` for day counts and weekdays; appended automatically, no configuration). It answers in
  code, without the model: device state (one device, or up to three that fit a phrase such as "is the fan on" or
  "temperature in the garage"), recipe list/pick/recall, shopping, "say exactly", the time of day and
  today's/tomorrow's home weather (from `weather.forecast_home`). Other behaviour: assistant state is scoped to one
  turn (two satellites or users never share recipe/search data); the follow-up hint is sent as labelled untrusted
  reference data; `web_search` takes `news: true` (SearXNG news category, last day then week, "news" added to the
  query) and news answers read out three stories; a reply that merely describes a tool call ("Call web_search with…")
  is retried once with `tool_choice: "required"` (this llama.cpp build ignores the named-tool form); the prompt cache
  is warmed as each Assist satellite at start-up and after midnight, and that warm-up doubles as a canary
  (persistent notification if llama.cpp rejects the request); oversized string length bounds are stripped from tool
  schemas because llama.cpp rejects them ("failed to parse grammar"). `mealie_llm` now rejects recipe-import URLs
  that do not resolve to public addresses. Voice runs on the production `llama-cpp` container (30B, see Local AI);
  read `HANDOFF-2026-11-11-llm-igpu-speed.md` before changing the model, the prompt or any tool schema.
- The Voice PE `home-assistant-voice-0ae52a` runs the stock 26.9.0 firmware plus an on-device "Overwatch" wake word
  (flashed 2026-11-13 from `configs/esphome/home-assistant-voice-0ae52a.yaml` via the ESPHome Device Builder);
  Okay Nabu stays active in the first wake word slot until Overwatch is proven by voice.
- The bounded read-only SearXNG search tool, Mealie recipe tools, and Grocy
  add/list shopping-list tools are enabled for local LLM conversation agents
  through the `llamacpp_conversation` config.
  On 2026-07-07, docker-host firewall scope was updated so HA's Supervisor
  network `172.30.32.0/23` can reach SearXNG `8087/tcp`, Grocy `9283/tcp`, and
  Mealie `9925/tcp`; HA-side API proofs returned success for those backend
  paths. The Grocy voice path is intentionally limited to adding/listing
  shopping-list items, and a live Assist spoken prompt is still required before
  certifying the conversational path end to end.
- GardenKeeper and Household Hub LLM tool integrations are live. GardenKeeper
  owns deterministic garden-state and task operations with confirmation tokens;
  Household Hub exposes authenticated read-only knowledge and recipe research.
  Both use separate HA credentials, and authenticated backend probes passed on
  2026-07-13. A spoken Assist prompt is still required to certify model tool
  selection and speech output end to end.
- Mealie is live; Overwatch-to-Mealie recipe saving is not yet implemented.
- VentSys dashboard is deployed; most physical VentSys entities remain gated on
  hardware installation.
- October18–19: full 0–100 software range and HA mode targets are restored, and
  the authenticated custom-card replacement is live at `/dashboard-ventsys/0`
  (release `20261018-3`). Repository and deployed dashboard sources now match.
  The public config credential was removed and its dedicated token revoked;
  independent API verification returned HTTP401. Confirmed-state controls,
  unavailable/stale displays, smoke precedence, pressure units, raw gas/flow
  readings and desktop/phone layouts are validated. All ten schematic selectors
  worked in real HA; startup sent zero service calls. Both live 360 boards still
  advertise firmware range30–60, which the card enforces. No physical movement,
  firmware or endpoint calibration was changed. See [[../procedures/ventsys-dashboard]]
  for current operation, tests, private checkpoint and remaining hardware gates;
  [[../audits/2026-10-18-ventsys-dashboard]] retains the historical findings.
- On October 19 the Homepage Home & Security tab gained a VentSys Open tab
  entry through the existing HA `8188` proxy, preserving normal HA sign-in and
  current network scopes. Desktop navigation/mobile viewport checks passed;
  no control iframe or public credential was added. See the dashboard/Homepage
  manuals for the deployment and recovery evidence.
- October 19 owner correction: the 360 firmware is correct and the role swap
  was already completed in firmware/HA. Missing sensors/controllers reflect
  incomplete installation, not a request to repair/recommission them. The
  dashboard incorrectly matched legacy entity prefixes: FDM `.62` / MAC
  `a0:85:e3:ae:5b:c8` is registered under the native `ventsys_sla_360...` IDs;
  SLA `.61` / MAC `cc:ba:97:f0:e3:ec` under `ventsys_fdm_360...`. Builder command
  topics already match FDM/SLA correctly. Live release `20261019-1` swaps only the
  native read/confirmation bindings, retains logical topics, and treats the
  30–60 intake range as intended. Activated through normal HA sign-in after
  configuration validation and idle-script reload; 53 tests passed, live ranges
  and asset/package hashes verified. No firmware changes or actuator commands.
- October 19 backend `20261019-arbitration-1` is live alongside frontend
  `20261019-1`: named normal modes, valve helper and dashboard commands share
  `script.ventsys_normal_command`; every normal publish requires failsafe off
  and fire script idle. Fire response cancels normal execution before direct
  canonical publishes, including main fan 100%. Eight arbitration, 11 backend
  and three drift tests passed; isolated real HA no-MQTT probe passed contention,
  preemption and failsafe rejection. Temporary probe removed; production script
  reload performed idle, dispatcher loaded off and deployed hashes verified.
  No actuator commands or firmware changes. Direct MQTT/native controls remain
  outside this boundary; physical commissioning remains separate. Runtime source,
  checkpoint and rollback are in [[../procedures/ventsys-dashboard]].
- October 19 frontend `20261019-2` is live with dispatcher-aware availability,
  immediate unverified interruption on failsafe/fire/backend loss and explicit
  alarm/failsafe/fire note headings. Four new regressions; 24 browser tests and
  runtime contract checks passed. Connected live version and Ready/no commands
  verified. Backend remains `20261019-arbitration-1`; hardware unchanged.
- October 19 frontend `20261019-3` is live: Environment comparison table with
  Ambient/FDM/SLA columns and System log with dashboard-session events. Shared
  source/freshness/unit/alarm rules match the detailed sensors. 26 browser tests,
  desktop/mobile visual checks, runtime contract/drift checks and signed-in HA
  labels/version/no-command verification passed. Backend unchanged.
- October 19 frontend `20261019-4` is live with an additional Touch screen view
  at `/dashboard-ventsys/touch`. Original-style PrintAirPipe title/header, clock
  and bottom status strip restored with current/unmeasured status, plus touch
  pop-up controllers/modes/sensors/status/logs. Default view configuration and SVG
  layout retained. Main duct highlight overruns fixed and log entries enlarged.
  30 browser tests passed at normal/mobile and touch 800×480/1024×600; signed-in
  HA popup/view/config/hash acceptance passed. Physical screen not yet checked.
  Backend/firmware unchanged, no actuator commands. Recovery in the runbook.
- October 19 owner physical test reported stalled/nonresponsive intake controls,
  blocked mode menu and longstanding E2 failure. Frontend `20261019-5` / backend
  `20261019-command-repair-1` correct identified causes. Actual running firmware
  logs prove physical FDM `.62` / `a0:85:e3:ae:5b:c8` subscribes to legacy
  `ventsys/sla/360/control`; physical SLA `.61` / `cc:ba:97:f0:e3:ec` subscribes
  to `ventsys/fdm/360/control`. Earlier Builder-based "topics already correct"
  statements were wrong and are superseded. Dashboard/modes now match runtime.
  E2 `.52` / `ec:e3:34:b4:79:7c` uses `ventsys/sla/branch/control`; its HA entry
  wrongly pointed at `.51`, corrected through Reconfigure, native value recovered.
  Available-controller mode subsets are explicit and frozen at review; full modes
  still require all targets. Matching position targets may be explicitly resent.
  32 browser/22 model/13 backend/8 arbitration/3 drift tests and HA read-only
  command-plan/config/UI checks passed. No actuator commands or firmware changes;
  physical responsiveness after repair remains unverified. Earlier UI acceptance
  was not physical acceptance. See dashboard manual/checkpoint for evidence.
- October 19 frontend `20261019-6`: deep red closed/bright green open indicators,
  calibrated 360 endpoint colours and aligned System log/enclosure/booth bottoms.
  34 browser tests passed; visual-only, no backend/firmware/actuation change.

- November4 owner correction (supersedes earlier endpoint-pending statements):
  standard SLA/FDM print, enclosure/branch and main valves use 0–100% for both
  physical travel and display. The 360 intake remains the separate raw30–60 to
  display0–100 mapping. This is owner-reported; no physical feedback is fitted.
  Earlier bench notes and provisional pulse-window records are historical evidence,
  not a request to restrict travel or recalibrate established endpoints.
- The E2 five-minute Codex monitor was stopped and deleted at the owner's request
  on November4; prior healthy readings do not establish present availability.
- November4: frontend20261104-4 live in standard/touch: normalized360 opening
  (raw30/45/60 -> UI0/50/100), integer RPM/gas, fresh-flow arrow sequencing.
  Board CC:BA:97:F0:D0:C0 `.32` is FDM, not SLA; renamed firmware/HA and mapped
  exclusively to FDM readings, installed wiring retained. See board/dashboard manuals.
- November4: E2 native host again wrong `.51`; corrected through HA UI to `.52`.
  E2 uptime382515s/RSSI-72dBm and valid0 report ruled out a continuous Wi-Fi
  outage at inspection. Found live router MAIN-1/.51 reservation using E2 MAC;
  corrected MAIN-1 MAC and added proper E2/.52 reservation, dnsmasq reloaded,
  DNS/router reachability/HA host verified. Plausible discovery-confusion source,
  actual host-rewrite cause unproven. A five-minute Codex heartbeat monitored HA host, router reservation and
  connectivity temporarily; it was stopped and deleted at the owner’s request.
- November10 E2 recurrence: HA's stored ESPHome entry again pointed at MAIN-1
  `.51`, and E2 native entities had been unavailable since November5 21:11 UTC
  (with a brief state transition then). A direct encrypted API probe from the
  Windows host verified `.52` is E2 MAC `EC:E3:34:B4:79:7C` and `.51` is MAIN-1
  MAC `EC:E3:34:67:8C:9C`; HA terminal could open `.52:6053`. HA's graphical
  reconfigure form twice showed `.52` before submission yet aborted as if it
  reached MAIN-1. The equivalent authenticated HA config-flow REST request
  accepted `.52` and returned `reconfigure_successful`; HA storage then held
  `.52`, and fresh native E2 uptime, valve 0%, Wi-Fi -79 dBm and IP `.52`
  appeared. A subsequent broker audit found the cause: retained MQTT topic
  `esphome/discover/ventsys-main-valve-1` advertised name MAIN-1 and IP `.51`
  but carried E2 MAC `ece334b4797c`. HA's ESPHome MQTT discovery handler uses
  the advertised MAC to find the existing entry and updates its host from the
  payload. That stale record was cleared with an empty retained publish and a
  fresh subscription confirmed it absent; E2's HA entry remained `.52`.
  Current canonical E2 and MAIN-1 firmware set `discovery: false` and
  `discover_ip: false`, and router reservations pair each board with its proper
  MAC/IP. The retained message likely came from the earlier period when the
  E2 board ran MAIN-1 identity; its original publication time is unavailable.
  Recheck the retained topic and HA host if another recurrence is observed.
- November10 follow-up retained-topic audit: the obsolete
  `esphome/discover/ventsys-sla-sensor` record still advertised the former SLA
  name for MAC `CC:BA:97:F0:D0:C0` at `.32`, now the FDM enclosure sensor.
  Cleared it with an empty retained publish and verified a fresh subscription
  shows only `ventsys-fdm-sensor` (`.32`, matching MAC) and
  `ventsys-sla-airflow` (`.42`, MAC `CC:BA:97:F0:D3:10`) in
  `esphome/discover/#`. No retained `homeassistant/#` topics appeared.
  Sixteen retained `ventsys/#` state/airflow/alarm topics remain; they have no
  publication timestamps, so their age cannot be inferred from the broker
  snapshot. In particular `ventsys/sla/pipe_air/alarm_latched` says `latched`;
  this audit did not clear or reinterpret a safety latch.
- November10 standing monitor is now server-side on VM102, enabled
  `ventsys-monitor.service`, unprivileged and restarting on failure/boot.
  Continuous discovery capture plus five-minute HA host-roster/E2 checks send
  deduplicated incidents/recovery to ntfy `monitoring`; healthy checks are silent.
  MQTT, broker log stream, HA roster/telemetry and authenticated HTTPS ntfy test
  passed. Phone reception remains unverified. Desktop collector stopped and
  Codex heartbeat paused. Temporary broker debug/payload capture still needs
  explicit rollback; see `docs/procedures/ventsys-temporary-mqtt-logging.md`.
  At08:31UTC migrated both functions/state/evidence from interim VM103 to VM102.
  Verified MQTT, restricted SSH, HA telemetry, tests and ntfy HTTPS delivery
  acceptance. VM103 dedicated service/account/key/config/program/state/logs and
  newly installed Paho package removed; old key revoked in HA current/persistent
  authorization. Temporary broker debug capture remains active on HA/VM102.
- November4: both MAC-bound C6 intakes updated with GPIO2 external digital touch,
  LED1/servo0 preserved. SLA known raw60 restored WITHOUT PWM and survived
  accepted-image restart; final OTA retained SLA60 and FDM30 plus endpoints,
  PWM off. UI shows100/0 respectively. First post-update report loss and an
  early-restart OTA rollback are recorded separately in board procedure.
  Physical touch, loaded travel and full-system commissioning remain pending.
- October29: normal three-wire SLA print valve flashed/adopted in HA Garage:
  COM4, MAC `EC:E3:34:1B:DB:2C`, static `192.168.50.56`, ESPHome2026.4.5.
  Full4MB original firmware backup saved privately; four write hashes verified.
  MQTT TLS/native report verified: seed50%, endpoints0/100, PWM off, source
  None since boot; physical position unknown. GPIO16 servo/GPIO33 touch,
  provisional940–2000us pulse window. Canonical/build/Builder sources match.
  No movement command sent; calibration, touch/remote and loaded tests pending.
- October28: normal three-wire FDM print valve flashed over COM4, MAC
  `EC:E3:34:B4:76:A4`, static `192.168.50.55`, ESPHome2026.4.5; four upload
  hash checks passed. HA adopted it in Garage as VentSys FDM Print Valve.
  MQTT TLS and native dashboard report verified: display50%, endpoints0/100,
  PWM off, command source None since boot. This is restored command state,
  not measured physical position. GPIO16 servo/GPIO33 touch, provisional
  940–2000us pulse range; endpoint calibration and movement/load tests pending.
  Canonical and live Builder YAML match. October29 owner reports board unplugged;
  subsequent unavailability is expected until repowered. No actuation sent.

- The owner clarified on 2026-10-10 that VentSys is still under testing and has
  not been commissioned. Commissioning will be recorded only when the owner
  specifies it. A 2026-10-10 owner correction swaps the FDM/SLA 360 intake
  identities. HA device info verified the board labeled FDM at `.61` as MAC
  `CC:BA:97:F0:E3:EC` and the board labeled SLA at `.62` as MAC
  `A0:85:E3:AE:5B:C8`; the corrected target swaps the role names while keeping
  board IP/MAC pairs intact: FDM `.62` / `A0:85:E3:AE:5B:C8` and SLA `.61` /
  `CC:BA:97:F0:E3:EC`. The `.61` board (now assigned SLA) was
  compiled locally with ESPHome 2026.4.5 and flashed over USB COM8; esptool
  verified the write. Its application image SHA-256 is
  `E2AC048E49486C8675C5BF19266E0B827E1A6EB9B671AC61636FEBF85FA7CCAC`.
  HA showed `-55 dBm` Wi-Fi telemetry after the flash. At 09:52:11, HA logged
  the new Restart Board entity changing from `Unavailable` to `Unknown`, then
  displayed “Pressed”; activity details record no cause, which is not evidence
  of a button activation. No valve movement was commanded in that flash. The
  source DHCP reservations and all 360 firmware profiles now reflect the
  corrected target mapping. The ESPHome Builder copies were synchronized and
  SHA-256 checked. At the last check, Builder reported both 360 boards offline
  and HA showed an active P1S print, so no OTA was attempted. The live boards
  still run their prior names/topics; reflash each in place at its existing IP,
  then verify HA names, MACs, IPs and MQTT topics before using either valve.
  **Superseded October 19:** the owner confirms this firmware/HA role swap was
  already completed. The dashboard's retained-ID mapping was the remaining
  mismatch; do not repeat an OTA solely for that UI issue.
  Power Off and physical wake/reconnect acceptance remain pending; see
  [[../procedures/ventsys-board-power-controls]].
- On 2026-10-10, the owner reported MAIN-2's ESP32 internal-temperature reading
  sustained at or above 57°C for hours. The source firmware's LED notice/alarm/
  emergency thresholds are 60/70/80°C; no cause is established. Production
  firmware source now includes shared Power Off Board and Restart Board buttons
  (shutdown suspends network, sensing, telemetry and control until physical
  reset/power cycle). All six reachable boards have now been flashed with
  the feature under supervised testing; MAIN-2's high-temperature cause remains
  undiagnosed. See [[../procedures/ventsys-board-power-controls]].
- On 2026-10-09 the 360 intake ESP32-C6 later reassigned to SLA (MAC
  `cc:ba:97:f0:e3:ec`, then `192.168.50.61`) was connected as COM8 for a
  direction fault: both Open and
  Close visibly drove toward closed, although HA showed distinct targets.
  The v2 firmware called `turn_on()` on the raw LEDC float output before each
  `servo.write`, briefly selecting full duty. The revised firmware removes
  that call and uses `servo.detach` at endpoints. It compiled and flashed with
  verified hashes; HA reports build `2026-10-09 22:58:25 +0100`. Serial logs
  show Open 60 -> servo level +0.2 and Close 30 -> -0.4, each detached after
  one second. The operator then confirmed that Open and Close move in the
  correct physical directions. The linkage remains connected; endpoint travel
  is not yet calibrated.
- 2026-10-10 maintenance: all six reachable VentSys devices (.61 then-labeled FDM 360,
  .62 then-labeled SLA 360, .52 E2, .57 MAIN-2, .41 FDM airflow, .32 installed SLA sensor)
  received OTA firmware with shared restart/shutdown controls. All production
  valve source variants now persist commands/endpoints without boot motion;
  v2 MQTT/button paths also save through number.set. The SLA-profile 360 raw-LEDC fix
  is flashed; physical direction acceptance remains pending. Offline boards
  remain deployment targets. See [[../procedures/ventsys-board-power-controls]].
- Installed FDM sensor `.32`, MAC `CC:BA:97:F0:D0:C0`, uses BME680
  SDA4/SCL5 at `0x77`, 3.3 V CO on GPIO3, and a plain GPIO2 status LED.
  On 2026-11-10 the owner confirmed the CO module and 3.3 V supply. Firmware
  `configs/esphome/ventsys_fdm_sensor.yaml` was compiled with ESPHome 2026.9.1
  (build `11:02:34 +0000`, config hash `0x1585cc4c`) and encrypted OTA
  succeeded after native API MAC verification. Builder source matches. CO
  voltage, fault, detection, ratio and clean-air baseline button are exposed;
  the wrongly named smoke channel was removed. After 182 seconds uptime the
  CO voltage was approximately 0.140 V, CO and combined faults were off, and
  the ratio remained unknown with no baseline captured. The baseline and
  physical alarm/notification response remain to be verified. CO is qualitative and does not
  replace a certified alarm. The planned FDM-array-2 `.32` allocation conflicts
  and must be resolved before adoption.
- MAIN-2 final diagnostic build 10:25:40 BST adds reset reason, heap and loop
  telemetry. Independent power was stable beyond five minutes and one native
  restart recovered with saved 0/75/0 settings and PWM inactive within 7.7 s.
  PC USB control/power is a candidate cause of earlier reset failures, not
  proven. Repeated loaded cold-start testing remains required before duct use.
- The board formerly identified as Main Duct Valve 2 (`192.168.50.52`, MAC
  `ec:e3:34:b4:79:7c`) is now the E2/SLA branch valve in the garage diagram.
  On 2026-10-06, `ventsys_sla_branch_valve.yaml` was built from its calibrated
  three-wire-servo image, with ESPHome name `ventsys-sla-branch-valve`, friendly
  name `VentSys E2 Branch Valve`, and MQTT topics `ventsys/sla/branch/*`.
  The board keeps `.52` and the same MAC, 940–2000 µs endpoints, and indefinite
  PWM hold only for commands 1–99. The COM4 flash passed hash verification;
  HA reconnected under the same MAC/device record and showed Valve Position 0.
  The E2 MQTT number `number.sla_branch_valve` reported 0 after reload; the old
  `number.main_duct_valve_2` is unavailable and no longer defined in live MQTT
  YAML. At that point MAIN-2 was a separate uninstalled design position with
  no board or IP assigned. The obsolete Main Valve 2 ESPHome Builder YAML was
  removed before the later MAIN-2 board was installed.
  The following paragraphs retain bench history under the old name.
- On 2026-10-06 a different ESP32 D1 Mini, MAC `ec:e3:34:67:a0:18`, was
  assigned to MAIN-2 at `192.168.50.57`. The normal three-wire servo uses
  GPIO16; GPIO21 LED is active and GPIO33 touch toggle is enabled for its
  planned touch input. COM4 flashing of `ventsys_main_valve2.yaml` passed hash
  verification. The first native HA connection timed out while the network
  path settled; a later HA-to-board TCP trace proved port 6053 reachable, and
  the existing MAC-bound ESPHome entry was reconfigured from its old Valve 1
  role. Its title, device, and 21 native entity IDs now identify MAIN-2. The
  separate MQTT `number.main_duct_valve_2` was restored from the package and
  showed 50. The firmware reports a restored command with physical position
  unknown and PWM inactive; no range command was sent. Its initial 940–2000 µs
  command window matches E2 but MAIN-2 mechanical stops remain uncalibrated.
  A subsequent COM4 flash on 2026-10-06 installed the validated MQTT number
  parser, which accepts finite decimal positions such as `50.0` and rejects
  malformed or out-of-range payloads. HA confirmed firmware build
  `2026-10-06 14:46:12 +0100`, position 50, and PWM inactive after reboot.
  E2's corrected YAML was then flashed over COM4 on 2026-10-06 to its
  MAC `ec:e3:34:b4:79:7c`. HA confirmed firmware build
  `2026-10-06 14:48:31 +0100`, IP `192.168.50.52`, restored position 0,
  and PWM inactive after reboot. The live ESPHome YAML matches the source.
  The board's previous Valve 1 association leaves no installed MAIN-1 board
  verified in this session.
- On 2026-10-11, E1/FDM branch received a separate ESP32 D1 Mini, MAC
  `EC:E3:34:67:0D:28`, at static IP `192.168.50.53`. Its normal three-wire
  servo uses GPIO16 PWM and board 5 V/GND; GPIO21 LED and GPIO33 touch toggle
  are configured. The feedback ADC/network was removed from this firmware.
  `ventsys_fdm_branch_valve.yaml` was compiled with ESPHome 2026.4.5, flashed
  over COM4 with verified hashes, and copied to the live ESPHome Builder.
  The board joined HomeIoT, and HA adopted it as VentSys E1 Branch Valve in
  Garage with 26 native entities; the serial log confirmed HA's API connection.
  MQTT control/state topics remain `ventsys/fdm/branch/*`. The 940–2000 µs
  pulse window is copied from E2 only as a provisional calibration range;
  E1's horn is free and its physical valve stops have not been mapped. The
  position and endpoint numbers restore saved values, seed at 50 on a fresh
  board, and do not command PWM on boot. No movement command was sent during
  adoption. The system remains under testing and uncommissioned.
  On the following bench watch, GPIO33 generated repeated
  `Accepted Touch command: 50%` log entries and enabled PWM. The operator may
  have touched the exposed pin, so unintended triggering is not established.
  The reason for 50% was a configuration error: both fresh-board Open and
  Closed targets were seeded at 50 while awaiting calibration. The
  serial watch later ended with `Serial port closed`; the router removed E1
  at 23:52 BST for Wi-Fi inactivity, and E1 was unreachable at the next check
  despite COM4 being present. The serial/USB loss and Wi-Fi dropout are
  temporally related, but their cause is not established. E1 must not be
  treated as stable until connectivity is resolved. On 2026-10-12 the E1
  source was corrected to seed logical Open/Closed at 100/0, compiled and
  reflashed over COM4 with verified hashes. HA showed the new build online,
  Open 100, Closed 0, Valve Position 50, Last Command Source `None since boot`,
  and PWM Commanded Active off. No movement command was sent in this fix;
  physical E1 endpoints remain uncalibrated.
- On 2026-10-12, a separate ESP32 D1 Mini, MAC `EC:E3:34:67:8C:9C`, was
  assigned to MAIN-1 at static IP `192.168.50.51`. The owner confirmed the
  normal three-wire servo on GPIO16, GPIO21 LED, GPIO33 touch input and a free
  horn. The former MAIN-1 feedback-servo YAML was replaced by the current
  three-wire production profile: no GPIO35 input, feedback network, feedback
  sensor or position-mismatch entities. It retains commanded position and
  Open/Closed targets across resets, does not actuate on boot, includes
  Restart Board and Power Off Board, and uses `ventsys/main/valve1/*` MQTT
  topics. The provisional 940–2000 µs command window is copied from E2,
  with MAIN-1's physical stops still uncalibrated. ESPHome 2026.4.5 compiled
  and flashed over COM4 with verified hashes; the live Builder YAML matches
  canonical source. HA adopted the board in Garage as VentSys Main Duct Valve
  1 with 26 native entities, no feedback entities, Open/Closed 100/0, saved
  Valve Position 50 and PWM inactive. No movement command was sent.
- On 2026-11-06, SLA pipe air ESP32-C6 `CC:BA:97:F0:C3:0C` was flashed
  over COM3 with `ventsys_sla_pipe_air_sensor.yaml` using ESPHome 2026.9.1;
  factory-image hash verified. It runs at `192.168.50.37` with CO analog
  input on GPIO3 and BME680 I2C on GPIO4/5 at address `0x77` (bus scan
  confirmed). Encrypted API verified identity and live BME readings; HA
  adopted it in Garage as VentSys SLA Pipe Air Sensor with 33 entities.
  The CO voltage remained about 3.26–3.28 V after warm-up, producing a CO
  sensor fault and a latched alarm. This channel is not commissioned; inspect
  its 3V3/GND/analog wiring and sensor output before relying on CO alerts or
  clearing the latch. After a power cycle on 2026-11-07, the CO voltage
  fell to about 1.03 V after the 180 s warm-up; CO detected and CO sensor
  fault were both false, while the prior alarm latch remained true. The
  channel still needs physical verification and a clean-air baseline before
  commissioning. Builder YAML and included packages were synchronized.
  Later on 2026-11-07, HA reported `co_voltage` 3.307 V again, with
  `co_detected` and `co_sensor_fault` active. The improvement did not persist.
  Do not capture a baseline or acknowledge this active alarm; inspect the
  hardware and confirm a stable output first.
  A later encrypted API check after warm-up on November 7 read 3.3258 V,
  `co_detected: false`, `co_sensor_fault: true`, `alarm_latched: true` and
  `bme680_fault: false`. The sensor fault and latch persist; this is not a
  confirmed CO reading. Dashboard frontend `20261107-4` now displays the
  latch and CO fault as two orange incidents, with SLA BME680 readings and a
  CO label. Home Assistant loaded `ventsys_incidents.yaml` automations for
  SLA CO hardware fault and VentSys failsafe transitions. A labelled test
  publish to internal ntfy `monitoring` returned HTTP 200; mobile reception
  remains unverified because the phone subscription is disconnected.
  VentSys dashboard `20261107-6` additionally has a live read-only Diagnostics
  tab. It groups and searches 294 exposed HA entities, including CO voltage,
  BME680 readings, faults and available board/controller statistics. The live
  tab showed CO voltage about 3.33 V, fault on and detection off. HA state
  update age is displayed separately from board uptime; unchanged values may
  have an old HA timestamp.
  Dashboard `20261107-7` now surfaces SLA pipe board status dropout and a
  missing CO-voltage entity while the board is online. HA's loaded SLA pipe
  dropout automation sends an ntfy warning after two minutes offline and a
  recovery after 30 seconds online. Configuration check passed and the
  automation was `on`; no actual outage or phone receipt was tested.
  Dashboard `20261107-8` now treats all 12 adopted VentSys boards as expected
  online by default. Diagnostics has a per-board maintenance switch that
  persists across HA restarts; new switches start off. Maintenance suppresses
  that board's dropout ntfy alerts while retaining a blue dashboard indication
  and does not suppress CO hardware fault or failsafe notifications. Eleven
  boards use uptime availability in the new general dropout/recovery automation;
  the SLA pipe board keeps its separate status-based rule. Local assets and HA
  packages were deployed, HA configuration passed, all 12 helpers and the
  general automation loaded, and a live Main duct valve 1 on/off switch cycle
  updated the dashboard. Induced outage/recovery and phone receipt remain open.
  On 2026-11-08 the owner found the SLA CO sensor's packaging cover still in
  place and a possible stray wire strand bridging analog signal to VCC; both
  were removed. At 23:09 GMT, HA showed CO voltage about 0.300 V, CO detection
  off, CO sensor fault off, BME680 fault off, and the historical alarm latch
  still on. The CO Rs/R0 ratio remains unknown because no clean-air baseline
  has been captured. This is a plausible explanation for the earlier high and
  unstable voltage, not yet a validated diagnosis or CO commissioning result.
- On 2026-10-21, airflow identities were reassigned at the owner's request:
  FDM is `CC:BA:97:F0:E3:DC` at `192.168.50.41`; the previous FDM board
  `CC:BA:97:F0:D0:A0` is now Booth at `192.168.50.43`. Both run ESPHome
  2026.4.5 with GPIO0 Hall pulse/GPIO1 WS2812. FDM was flashed over COM5
  with verified factory-image hashes (build `08:50:23 +0100`, config hash
  `0x5846da5e`). Booth was OTA-updated only after encrypted API MAC verification
  (build `09:12:36 +0100`, hash `0x42ec9a4c`). The old Booth template's
  GPIO10/GPIO9 mapping was replaced with the reused board's actual FDM wiring.
  Both encrypted APIs independently confirmed names, MACs, IPs, HomeIoT and
  live zero pulse/wheel readings. MQTT configuration reports distinct FDM/Booth
  prefixes on TLS8883; broker delivery and physical pulse response were not
  independently verified. The temporary router neighbor pin used to target
  the old board was removed; the `.41` address conflict is resolved.
  Both Builder YAMLs match canonical source. HA native device/entity adoption
  and naming after the MAC/role change still need verification; do not treat
  the old FDM device-registry record as proof of the replacement's adoption.
  The separate planned FDM pipe-air sensor `.36` did not answer an API probe;
  the installed SLA enclosure sensor `.32` did. Build artifacts/secrets remain
  outside the vault in temporary staging. Physical commissioning remains open.
- On 2026-10-19, SLA airflow ESP32-C6 (MAC `CC:BA:97:F0:D3:10`) was flashed
  over COM9 with `ventsys_sla_airflow.yaml` (ESPHome 2026.4.5); flash hashes
  verified. It joined HomeIoT at static IP `192.168.50.42`, with ESPHome API
  port 6053 reachable, and HA adopted it in Garage as VentSys SLA Airflow
  Sensor. HA showed live pulse rate 0 pulses/s, wheel speed 0.0 rounds/s,
  Wi-Fi -68 dBm and matching firmware build/hash. The live Builder YAML hash
  matches canonical source. Pulse generation and physical airflow response
  remain untested; this is not commissioning acceptance.
  Later that day the owner clarified that the installed SLA board uses the
  same GPIO pair as FDM airflow: GPIO0 Hall pulse and GPIO1 external WS2812.
  The original SLA YAML had GPIO10/GPIO9. Corrected source compiled and was
  reflashed on COM9 with verified hashes; the Builder YAML hash matches the
  correction and API port 6053 is reachable. Four-blade pulses per revolution
  and low-flow LED timing have not yet been calibrated.
  Main Duct Valve 2 (`192.168.50.52`) was restored to the canonical production
  `ventsys_main_valve2.yaml` image over COM4 on 2026-09-26, with flash hash
  verification. The three production position controls were subsequently
  expanded from 40-60 to 0-100 and reflashed over COM4 with hash verification;
  HA confirmed min=0/max=100/step=1 for position, open position, and closed
  position. Open and Closed retain `restore_value: true`; their reported values
  are Open 100 and Closed 0. At the operator's request, direct Valve Position
  now starts at a **displayed** 100 on every boot (`restore_value: false`,
  `initial_value: 100`); boot does not call its servo action. The 2026-09-26
  COM4 flash passed hash verification, and HA reported Position 100 with live
  telemetry after reboot. This display value is not evidence of shaft angle.
  The operator later clarified that the earlier USB power removals were
  intentional. On 2026-09-27 a controlled PC USB unplug/replug left the board
  unavailable even though COM4 re-enumerated; one RST/EN press did not restore
  HA. Moving the USB plug to a 5 V/2 A-or-higher wall charger brought the board
  back without a serial reset. A second unplug/replug on charger power also
  rebooted into HA without intervention (uptime 4.861 s at 09:49:10 UTC,
  increasing thereafter), with Wi-Fi near -65 dBm and live feedback. This
  implicates the PC USB path but
  does not distinguish USB power delivery from data/control-line behavior.
  A subsequent charge-only cable on the same PC port allowed HA uptime to
  increase beyond two minutes with COM4 absent, making the data/control-line
  path a stronger candidate while leaving cable and power differences open.
  Independently, raw feedback fell to 0.075 V at 09:51:06 UTC before that
  cable swap. The operator found the feedback lead disconnected and reseated
  it with power off; raw feedback returned near 0.97-1.02 V and HA cleared the
  disconnected warning by 10:01 UTC. Do not use the derived feedback
  percentage as physical position until the replacement servo is calibrated.
  The valve linkage remains off. The operator reconnected the orange GPIO16
  servo signal lead before this second flash. Production feedback has varied
  during bench testing;
  the previous servo's calibration constants in the production YAML are not
  valid for the replacement B2122. The actual wiring is the ESP32 D1 Mini USB
  5 V/GND feeding the servo and LED through the documented splice/capacitor,
  with GPIO35 feedback through the 10k/20k/100nF network. See the current
  handoff for the unloaded test history. No new endpoint calibration was accepted.
  At the earlier 2026-09-27 bench check, the board was powered off with the
  orange GPIO16 servo signal lead disconnected. The free horn still moved
  clockwise on charger power-up with that lead disconnected, so an ESP32 PWM
  command is not required for the startup motion. The operator then tested a
  second, unused feedback servo of the same model: it also moved on power-up
  both with and without its feedback lead connected. A non-feedback servo did
  not move in the comparison test. This rules out the external feedback lead
  as necessary for the observed motion, but does not distinguish the feedback
  servo's floating PWM input, internal startup behavior, and supply transient.
  Current power and signal-lead connection after these swaps were not reported.
  Further repeated cycles are paused; the linkage remains off and physical
  position is uncalibrated.
  The connectorized second ESP32 D1 Mini was then reassigned as Main Duct
  Valve 1 (`ventsys-main-valve-1`, `192.168.50.51`) on 2026-09-27. Canonical
  `main/configs/esphome/ventsys_main_valve1.yaml` now uses the tested Valve 2
  control behavior under Valve 1 identity. The compiled image passed COM4
  flash hash verification with the servo fully disconnected; HA's native
  ESPHome integration entry was created and loaded, and Valve 1 entities
  appeared. The same YAML was copied to HA ESPHome Builder with matching
  SHA-256. The board has no LED and no feedback resistor/capacitor network.
  Its servo signal and feedback leads remain disconnected; HA's feedback
  disconnected warning and unknown derived feedback position are expected.
  Direct Valve Position initially displays 100 but does not establish or
  command physical position. Open and Closed initially show 50 on this new
  board. Do not actuate Valve 1 or treat it as calibrated until its wiring,
  supply, and physical travel have been checked.
  In the subsequent bench check, two feedback servos remained motionless and
  quiet while HA Valve Position commands changed from 100 through intermediate
  values and 0 back to 100; HA uptime continued increasing, so these commands
  did not reset the ESP32. The operator had connected the servo feedback lead
  directly to GPIO35 without the protection network and then disconnected it
  on request. The servo was later fully unplugged for supply measurements.
  Meter readings were approximately 1.15 V at both the unloaded servo
  connector and the ESP32 pin identified as 5 V, then 0.2 V at the pin
  identified as 3V3 relative to the same reported GND. The operator then found
  that TX and GND pins had been swapped. The earlier readings were therefore
  taken against the wrong reference and are invalid as rail measurements; the
  servo ground connection was also suspect. Correct the wiring with USB power
  off, leave feedback disconnected until a suitable input divider is fitted,
  and recheck unloaded 5 V/GND before further actuation.
  On 2026-09-28 the operator reported that, after correcting the new-board
  wiring, multiple servos now moved their free horns on power-up with more than
  one power source. The extent, direction and signal-lead connection for these
  new-board trials were not yet reported. This supersedes the earlier
  "no movement" comparison made with TX/GND swapped; it does not by itself
  isolate a floating signal from servo-internal startup behavior.
  Later bench tests found that the feedback servo still stepped
  clockwise at power-up with GPIO16 unplugged and a roughly 5.5 kΩ resistor
  from its orange input to GND. It also stepped with a separate 5 V supply,
  the same pull-down, and the ESP32 entirely disconnected. The operator chose
  a normal three-wire servo for the board on COM4. On 2026-10-04, inspection
  of its upload MAC (`ec:e3:34:b4:79:7c`) established that this board is HA's
  existing Main Duct Valve 2, not Valve 1. It had temporarily been flashed
  with the Valve 1 identity/IP (`192.168.50.51`); HA rejected the API
  connection because its Valve 1 entry expects MAC `ec:e3:34:67:a0:18`.
  The Valve 1 MQTT position/state topics nevertheless reported 100 while
  that temporary image was running. The operator confirmed the board should
  remain Valve 2. Valve 1's canonical YAML was restored to its previous
  feedback configuration. Valve 2's canonical YAML was changed to remove ADC
  feedback and mismatch/disconnect entities, retain its other controls, and
  restore the last commanded Valve Position from ESP32 preferences with prompt
  NVS writes. The operator states the valve is physically 100% open; 100 is
  the first-boot display seed. A restored/commanded number is an estimate,
  not measured valve position. The corrected Valve 2 image was compiled and
  flashed over COM4 with hash verification; HA's existing MAC-bound entry
  reconnected at `192.168.50.52` and showed Valve Position 100 with feedback
  entities removed. A follow-up image delays the MQTT reconnect publication
  until the client is ready: both the ESPHome position topic and the separate
  retained VentSys state topic then reported 100. After return to wall-charger
  power, HA remained online and showed 100. A commanded non-100 value followed
  by power-loss restoration and physical travel calibration remain untested.
  On 2026-10-05, with the normal servo linked to the valve, HA Close at the
  former 1000 µs endpoint left the valve about 5° short of closed. Supervised
  980 µs and 950 µs Close trials were quiet but still short. A 940 µs Close
  trial was accepted by the operator as good enough; no strain or buzz was
  reported for the prior two trials. The linked valve returns about 1–2°
  toward open after the 940 µs PWM releases, leaving a minimal gap. A supervised
  five-second hold kept it sealed while powered, and a second 200 ms 940 µs
  pulse after a one-second release still allowed the same return. The operator
  accepted this behavior and declined continuous holding torque. The temporary
  double-close test control was removed. The canonical Valve 2 YAML and HA Builder copy
  now set `min_level: 4.7%` (940 µs at 50 Hz), with the 2000 µs open endpoint
  unchanged. Each image was flashed on COM4 to MAC `ec:e3:34:b4:79:7c`
  with hash verification. The final image was compiled and flashed over COM4
  on 2026-10-05 with hash verification; HA showed it online at `.52`, Valve
  Position 0, and no double-close test button. On 2026-10-05, the operator
  requested indefinite holding torque at intermediate positions for a later
  loaded-pipe test while retaining endpoint release. A further image was
  compiled and flashed over COM4 to MAC `ec:e3:34:b4:79:7c` with verified
  hashes; HA showed build time 10:06:42 +0100 online at `.52` with Valve
  Position 0. This image keeps PWM active for commanded positions 1–99 and
  cancels a pending endpoint detach on each new command; commands to 0 or 100
  detach after one second. No valve movement or loaded intermediate hold was
  tested after that flash. After reboot, the saved number is display state:
  servo PWM is not restored until another movement command. Physical position
  remains unmeasured by the three-wire servo.
  On 2026-09-27, a second ESP32 D1 Mini on COM4 was flashed with the exact
  canonical production Valve 2 image for an isolated bench comparison. The
  saved build YAML SHA-256 matched the canonical YAML; ESPHome verified the
  flashed image hash. This new board has connectors and no LED, with no servo
  or feedback network attached at flash time. Its firmware uses the same
  Valve 2 network identity, so the original board must remain off while this
  test board is powered. In the first new-board check, the operator connected
  only servo 5 V and GND, left signal and feedback disconnected, and observed
  no horn movement on power-up. Whether the same servo and USB power source
  were used in the old-board comparison is pending confirmation.
- Repository and live HA core files, VentSys packages, mode scripts and dashboard
  have matching SHA-256 hashes. The valve contract is direct `0`/`50`, HA
  configuration validation passes, and HA restarted successfully on that source.
- Frigate integration in Home Assistant is live using Frigate API URL
  `http://192.168.30.20:5000`; all three cameras have Frigate entities and
  Advanced Camera Card CCTV views in HA.

## Frigate

**October 10 memory incident — recovered:** failed camera-capture retries
repeatedly connected/disconnected ZeroMQ configuration subscribers. Frigate's
idle configuration PUB socket was not processing pending connection cleanup
commands, retaining native connection allocations in the main process.
Native allocation tracing, a live recovery experiment, and a separate-process
reproduction confirmed this mechanism; it is not the upstream recording-manager
or embeddings-manager leak. Two `ZMQ_EVENTS` polls on that publisher followed
by `malloc_trim(0)` reduced main-process RSS from about 5.4 GiB to 593 MiB
without restarting. Python camera caches were empty and stats history bounded.

Before intervention CT 111 used 5.96/6 GiB, with no swap and only about 4 MiB
ordinary file cache. It had two historical OOM kills (one confirmed September
27), 23.46 billion file refaults and IO pressure near 99%. CT-local root reads
mapped to `dm-8` / `pve-vm--111--disk--0` on the NVMe. A five-second host sample
measured 11,784 reads/s and 459 MiB/s. Host load was 95/113/115 despite 21 GiB
available RAM; most sampled blocked tasks waited in `folio_wait_bit_common`.
October 8 kernel warnings also showed VM102 IO workers blocked over 122 seconds.
NVMe SMART passed, with zero media/integrity errors and error-log entries;
no matching NVMe timeout/reset or NFS-server failure was found in the bounded
kernel-log check. This was demonstrated CT-local cache thrashing, not evidence
of defective storage.

Initial recovery gave CT111 **12GiB RAM**, subsequently reassessed to **6GiB,
2 cores, no swap** after the lifecycle repair below. Its effective `memory.max`
and `memory.high` were checked; Docker was restarted to refresh its cached
memory denominator. All three deliberately disconnected cameras now have
`enabled: false` in both canonical and live YAML, preserving their stream,
detection, recording and credential definitions. The existing 0.17.1 image is
pinned to digest `1724960349dad0bd2ae8ec884171a6fd5755a4dc242a0e66cadbda9c0e85c99b`.
Frigate was recreated successfully; authenticated HTTPS still requires login,
API responds and no disabled-camera capture/process workers start. Host
one-minute load fell below 1 and blocked tasks to zero. Recordings remain
mounted from the expected OMV NFS export. Camera/inference/recording acceptance
is still deferred while hardware is disconnected.

At 20:56–20:57 BST main RSS was about 324 MiB, Docker working memory about
675 MiB/12 GiB, CT usage including usable file cache about 1.45 GiB, and
a five-second CT-root sample measured zero reads. No new OOM kills occurred.
An independent MQTT TLS client subscribed to Frigate availability and received
`online`. HA and Homepage HTTPS returned 200 and Kuma returned its normal 302.
Intel GPU utilization telemetry still logs `Failed to initialize PMU`
(`Operation not permitted`); this is separate from the proven retention issue.
Actual camera GPU decode/inference remained untested in this initial disabled-camera recovery state.
Final 20:59 BST check: healthy, zero Docker restart count, about 678 MiB working
memory and host one-minute load 0.19. Compose matches source; Frigate schema
passes and config structures match after masking host-only RTSP userinfo.

Subsequently deployed a tracked local lifecycle overlay on the pinned image:
`configs/frigate/patches/config_updater.py`. One owner thread creates, polls,
sends and closes the publisher socket; bounded synchronous requests serialize
API/MQTT multipart sends, with idle native cleanup every100ms. Three functional
tests and3600-reconnect isolated tests passed without forced trimming. The live
publisher handled12000 reconnects with only1.6MiB main RSS growth.
A separate network-isolated three720p/10fps camera test ran OpenVINO GPU
inference and H264 recording at~1.2GiB working memory, recovered from two FFmpeg
interruptions and remained healthy. This synthetic test does not certify real
RTSP, VA-API or long-term physical-camera load. CT111 returned to6GiB rather
than the emergency12GiB, retaining generous working-set/cache margin. Production
cameras remain disabled pending physical reconnection/real-stream acceptance.
The read-only Compose overlay survives recreation; port/retest or remove after
proving an equivalent upstream fix when changing images.
The 0.17.2 publisher source still lacks idle event polling; a version bump alone
is not proof. Evidence and rollback files remain host-only in CT 111 at
`/opt/frigate/incident-20261010/`. See the incident section of
[[../install/phases/04-frigate|Phase 04]] and the bounded reproduction at
`scripts/validation/frigate_zmq_idle_pub_repro.py`.

- CT 111 runs Frigate 0.17.1 live on the shared Intel iGPU.
- OpenVINO detector process uses the shared Intel iGPU.
- VA-API is configured and active for camera decoding.
- Historical three-camera baseline on VLAN 30 (currently deliberately
  disconnected): Camera 1 at `192.168.30.21` on switch
  port 2, Gate at `192.168.30.22` on port 4, and Patio at `192.168.30.23` on
  port 3. All three are ANNKE C500 cameras (`I51HJ`, firmware
  `v5.8.10 build 250917`), with previously verified RTSP main/substream paths
  sustaining approximately `10 fps`. Repeat that proof after reconnection.
- Camera RTSP auth required switching the camera from RTSP `Digest` to
  `Digest/Basic`; after that change, Frigate confirmed live ingest at roughly
  `10 fps` on the first bench camera using substream detect and mainstream
  record roles.
- Live CT 111 carries the accepted three-camera config and live
  `/opt/frigate/.env`; repository source now mirrors the three-camera layout
  with RTSP and MQTT secrets represented only as environment placeholders.
  `configs/frigate/config-baseline.yml` remains the no-camera migration-safe
  fallback.
- HA validates Frigate API version/stats and sees all three cameras through the
  Frigate integration. `/config/packages/frigate_camera_health_package.yaml`
  adds MQTT FPS sensors plus three-minute camera-offline and recovery alerts;
  alerts use persistent notifications and the tested operator mobile service.
- Frigate HTTPS UI is live on `https://192.168.30.20:8971`; auth is enabled.
  Plain HTTP to port `8971` is rejected, while HA continues to use the internal
  unauthenticated API on `http://192.168.30.20:5000`.
- On 2026-08-01, the Frigate `admin` password was recovered with the supported
  one-time `auth.reset_admin_password` flag, then changed and the flag removed
  before a final verified restart. The credential is not recorded in the
  repository. Live API checks confirmed MQTT enabled, all three camera streams
  healthy at about 8 fps, and detection enabled for the Gate and Patio cameras
  (Camera 1 detection remains disabled).
- Frigate HTTPS now uses a `Home Local CA` signed certificate mounted from
  `/opt/frigate/tls` into `/etc/letsencrypt/live/frigate`. The certificate SANs
  include `192.168.30.20`, `frigate.home.local`, `frigate-nvr`, and `frigate`.
  This replaced Frigate's generated `FRIGATE DEFAULT CERT` so trusted Android
  and Apple browsers should not show the local certificate as untrusted.
- Direct Frigate PWA access off-WiFi is live through docker-host Tailscale as a
  narrow approved `192.168.30.20/32` route with firewall access only to
  authenticated HTTPS port `8971`. A routed workstation validation on
  2026-07-29 received the expected `401` challenge from `8971`, while the
  unauthenticated API on port `5000` remained unreachable.
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

- October4 read-only `pct config 114` confirms allocated6 cores,28672 MiB RAM
  and swap0. Older4-core/10–20 GiB guide descriptions are superseded; no
  allocation was changed during this audit. Root-size/model facts below retain
  their separately recorded evidence.
- CT 114 runs llama.cpp `server-vulkan`, a dedicated llama.cpp embedding
  service, Open WebUI, Wyoming Whisper, Piper and OpenWakeWord.
- llama.cpp serves `home-assistant-llm` from
  `Qwen3-30B-A3B-Q4_K_M.gguf` at `192.168.20.104:8081/v1` (production `llama-cpp`
  container, `restart: unless-stopped`, since 2026-11-13); it runs with a
  `40960` token context (the model's training length), f16 KV cache, one slot,
  `--cache-ram 2048` (the default 8 GiB would OOM the CT), reasoning disabled
  for normal assistant output, and Vulkan on Intel Meteor Lake graphics. Compose:
  `configs/local-ai/docker-compose.yml` (deploy to `/opt/stacks/local-ai/`; the
  pre-switch file is `docker-compose.yml.bak-20261113-pre-30b` on CT 114).
- The 30B model file SHA-256 is
  `0d003f6662faee786ed5da3e31b29c978de5ae5d275c8794c606a7f3c01aa8f5`.
  The previous production model, `Qwen3-14B-128K-Q4_K_M.gguf` (SHA-256
  `e6ad1ba102ef53dbc88aa59bd1bf1b10aaff298fea8f1a91f99e4312f1194c81`), is kept in
  `./models` for rollback.
- A dedicated llama.cpp embeddings service serves `home-assistant-embedding`
  from `bge-small-en-v1.5-q8_0.gguf` at `192.168.20.104:8082/v1`; it returns
  384-dimensional embeddings and is source-scoped to docker-host for Household
  Hub.
- Live llama.cpp image digest:
  `ghcr.io/ggml-org/llama.cpp@sha256:4e784358f638549d95bd22fb814c1afeed1af71fbd4b70c25f23eae01caaa6af`.
- Wyoming STT (`wyoming-whisper`, port 10300) runs NVIDIA Parakeet TDT 0.6B v2 int8 via sherpa-onnx since 2026-11-05 (~0.2 s/command; faster-whisper `base-int8` kept for rollback), starting offline from model data pre-placed in `./whisper`.
- Metrocop Wyoming TTS `metrocop-tts` on port 10201 (voice-mixer stack); Piper also serves `en_GB-metrocop2-medium`.
- SearXNG: Brave/DuckDuckGo/Startpage are blocked upstream; Bing + Yandex enabled (2026-11-05).
- HA can reach ports 8081, 10200, 10300 and 10400 through source-scoped
  host and Docker firewall policy. HA uses `192.168.20.104:8081/v1` for the
  llama.cpp conversation agent.
- Docker-host can reach CT 114 ports 8081, 8082 and 3002 for Household Hub
  assistant integration. Household Hub production RAG uses CT 114 chat on 8081,
  embeddings on 8082, and local Qdrant on VM 103.
- SearXNG web search is reachable at docker-host port 8087, including from Home
  Assistant after the 2026-07-07 HA Supervisor-network docker-host firewall
  update.
- Voice Mixer (decision 09) is **live** since 2026-10-11 as container
  `voice-mixer` (`/opt/stacks/voice-mixer`, image `voice-mixer:local` with CPU
  RVC, `cpus 2`, `mem_limit 4g`) on `192.168.20.104:7860`. The stack holds the RVC
  model/index, 325 metropolice clips and the 697-clip dataset; the Piper voice is
  mounted read-only from `/opt/stacks/local-ai/piper`. Port `7860` is scoped by
  the `DOCKER-USER` block in `/usr/local/sbin/llm-host-firewall.sh` (backup
  `*.bak-20261010-*-pre-voice-mixer`). Piper→RVC on CPU takes ~30 s per sentence;
  the container idles at ~155 MB and peaked at ~0.5 GB. Homepage portal:
  `https://homepage.home.local:8210/` (docker-host UFW `8210`). docker-host
  Tailscale advertises `192.168.20.104/32`, approved and active 2026-10-11.
  Since 2026-11-05 the mixer uses the Metrocop bleep set at `clips/bleeps`
  (overwatch `on3` start; random end blip from three cuts of
  `prison_soldier_bunker1.wav` plus overwatch `off2`) and ships a `metrocop`
  preset (mid + 200/120 ms gaps, bleeps at speech level), which is the default
  preset (`default_preset`). Live config backup:
  `data/config.json.bak-20261105-pre-bleepset`. The running image
  `voice-mixer:local` was patched in place on CT 114 (files copied in and
  `docker commit`) because Docker Desktop is no longer installed on the desktop;
  the previous image is tagged `voice-mixer:pre-default-preset`. The next full
  rebuild from the repo supersedes the patch.
- Custom wake word: `wyoming-openwakeword` runs with `--custom-model-dir /custom`
  and loads `/opt/stacks/local-ai/openwakeword/overwatch.tflite` (trained
  2026-11-05, see `voice/wakeword/README.md`; threshold 0.5). Compose backup:
  `docker-compose.yml.bak-20261105-pre-overwatch-wakeword`. HA pipeline
  assignment is done in the UI.
- Incident 2026-10-08 → 2026-10-10 (resolved): CT 111 Frigate's main process
  reached ~5.3 GB RSS inside the 6 GiB CT limit (2 OOM kills), leaving ~60 MB
  page cache, so the CT re-read its own files constantly (~1,000 reads/s on the
  shared NVMe, CT I/O pressure ~99%, host load ~100 with ~78 D-state tasks in
  `dm_thin_find_block`). NVMe SMART healthy; thin pool 26% data / 1% metadata.
  CT 111 was temporarily raised to 12 GiB and Frigate restarted; on 2026-10-11
  the CT is back at its configured 6 GiB with ~1 GB in use, host load ~1–2 and no
  D-state tasks. The Frigate memory growth is unexplained and may recur.

## Docker host

**GardenKeeper recheck, 2026-10-04:** read-only API health/readiness and
authenticated status passed; ntfy and configured broker health returned 200.
No notification was sent. Nextcloud is absent from both API/worker configuration,
consistent with the existing undeployed Nextcloud state. Live API/worker containers
lack Docker healthchecks; source VM Compose contains them but is not rolled out.
Local audit repairs and CI remain undeployed. The current morning database dump
restored in isolation, but its empty operational tables/media do not establish
populated full-system recovery. See the GardenKeeper service manual for limits.

Pocketry1.5.1 is live as of2026-10-18 at `https://homepage.home.local:8211/`,
with the standard Homepage Tools card and Preview. VM103 serves the unmodified
workstation-built frontend from `/opt/stacks/pocketry`, loopback8098, explicit
bridge `10.240.33.0/24`. Hosting/HTTPS smoke checks and browser cutout3D passed.
Projects remain browser-local; export editable backups. Phone ACL8211 and
physical fit remain unverified. See [[../install/services/pocketry|Pocketry]].

Live workloads: Pocketry, Bambuddy, AdGuard Home, Immich, Homepage, Dozzle,
ntfy, SearXNG, Whoogle, Mealie, Grocy, Obsidian LiveSync/CouchDB, Watchtower
monitor-only, GardenKeeper, Household Hub, Gridfinity Layout Tool, Recomp
Tracker, MediaMTX, the staged Troubleshooting Dashboard and Telegraf.
MediaMTX `1.20.1` is live at `192.168.20.102:8554/tcp` on explicit bridge
`10.240.16.0/24`. HomeAdmin `192.168.10.0/24` is the only permitted source;
publisher and viewer credentials are separate and path-scoped. It relays the
compressed `garage-phone` RTSP stream without transcoding and records 30-minute
fMP4 segments to the OMV-backed
`/mnt/omv/media/phone-recordings/garage-phone/` path as UID/GID `1007:100`.
Authenticated publish/read, unauthenticated denial, live H.264 relay and a
decodable NAS recording passed on 2026-08-27; synthetic acceptance files were
removed afterward. Automatic recording deletion is disabled pending an owner
retention decision.
The Troubleshooting Dashboard is live at
`http://192.168.20.102:8094/` on explicit bridge `10.240.32.0/24`. Its host
bind and IPv4 `DOCKER-USER` policy allow Management VLAN `192.168.10.0/24` only.
The September10 deployment verified the evidence-age update with a fresh
Windows 12-pass/one-disconnected-camera-failure snapshot and live desktop/mobile
checks. Historical stop/start rollback passed August25; September's prior image
is retained but that rollback was not exercised. A pre-existing IPv6 Tailscale
RETURN rule for8094 contradicts the earlier blanket-denial description; the
current publication is IPv4-only and bridge IPv6 is disabled. Reconcile that
rule before any IPv6 publication.

October2 at21:21 BST: the live bind is still `192.168.20.102:8094`, its bridge
still has IPv6 disabled, and the IPv6 RETURN/DROP pair remains at rules32/33
with zero counters during inspection. Host IPv4 HTTP returns200. Windows IPv6
times out and monitoring VM102 fails to connect; those failures do not prove
the full audience-path deny policy. An isolated-tested explicit8094 IPv6 DROP
is prepared in local source only. Live reconciliation/persistence and client
acceptance remain open; see the [[../procedures/troubleshooting-dashboard-ipv6-publication-guard|IPv6 guard]].
Owner-approved Homepage Tools placement is live at `https://homepage.home.local/portal-preview/troubleshooting/`; existing
Homepage clients can use the fixed HTTPS path without a new DNS alias. Proxmox
SSH was authorized September14; a dedicated snapshot collector is installed,
and September15 required evidence validation and real-file browser import passed. The [written walkthroughs](../troubleshooting/diagnostic-walkthroughs.md)
retain offline diagnosis and Mermaid links alongside the app.
The September30 update expanded the deployed catalog to 37 routes, including
ten recurring-incident investigations. Search covers check instructions and
exact errors; `#route=<id>` and Copy route link share the selected investigation
without notes/evidence. P1S guidance now reflects commissioning and FTPS990.
The offline companion has 32 extended routes. Twenty model tests, all local
route selections and live desktop/mobile checks passed; this remains an
guide whose imported signals remain independent of live tools. October11 adds Resource Health and bounded connection tests; manual route signals still require their stated evidence.
October11 Resource Health is live in this app and linked from Homepage Monitoring
at `https://homepage.home.local/portal-preview/troubleshooting/#resource-health`.
The main alert collector stays on Proxmox. An independent minute publisher uses
a source-restricted, forced-command key to send metrics-only JSON to VM103;
VM103→Proxmox SSH remains blocked. A128MiB-capped unprivileged Python service
serves a Unix socket mounted into the existing container, without a new port.
The page displays host/guest usable memory, CPU, disk/pressure/OOM, stopped
inventory, incidents, freshness/coverage and queued/failed notification delivery.
Five-minute-old evidence is stale. Grafana/ntfy links provide history and alert
navigation; no new time-series integration was added.
Buttons and a diagnostic input support fixed-target ping, system DNS lookup,
allowlisted TCP ports and fixed HTTP health endpoints from VM103. Two concurrent
jobs,20checks/minute, bounded time/output and same-origin POST protections apply.
Guided TCP steps link to these tests; copied incident reports include live summary
and tab-local test output. No arbitrary shell or remediation is exposed. Twenty
model tests,10 API tests, live HTTPS tools, guided-route desktop/mobile checks and
API restart/socket continuity passed. Runtime/rollback details are in
[[../../apps/troubleshooting-dashboard/README|the troubleshooting service manual]].
The October11 troubleshooting extension adds TLS inspection/trust/expiry for
Homepage, HA, Frigate and Vault, nine sequential/cancellable diagnostic bundles
covering all37 investigations, and a30-day/1,000-event SQLite timeline on VM103.
Monitor observations, accepted delivery and requested-check summaries are
retained; user notes/imports and full transcripts remain tab-local. Event links
open existing Infrastructure Fleet/Central Logs dashboards around±10minutes.
Twenty-eight backend tests and live desktop/mobile extension flows passed.
The actual Home Local CA lacks the key-usage extension required by strict
Python3.13 validation(code92). The UI shows this warning separately from legacy
chain/hostname/date verification, which passed for all four HTTPS targets.
Public CA copy `/etc/troubleshooting-api/ca.crt` is root-owned; no private key is
shared. Planned trust-preserving CA maintenance remains open in
[[../procedures/ssl_tls_guide|the TLS guide]]. Runtime database, operations and
selected rollback are documented in the troubleshooting service manual.
Homepage is the central `Home Operations` navigation portal at
`https://homepage.home.local/`, using a `Home Local CA` certificate. The former
`http://192.168.20.102:3001/` endpoint remains live for rollback. Its Home,
Tools, Infrastructure, Monitoring,
Storage, Media and Operations tabs cover every user-facing portal and every
live docker-host container; Docker-backed cards expose container health and
expandable resource statistics. The header aligns the Home Operations title,
search, Portal runtime resources (the Homepage container, not host-wide CPU or
memory) and date/time, while Home starts with the reference links. Portal cards
use 50% translucent, elevated glass surfaces.
Tailscale remains in Home's Reference Links; its duplicate Infrastructure card was removed on 2026-10-11.
Each card also exposes a visible Preview action that opens an inline embedded
workspace below the active tab's portal cards, with working Reload, Close and
normal-link `Open tab` controls. Every configured service is attempted in the
iframe; Open tab remains the safe fallback if a target declines framing. The
cards with a routable application endpoint also expose a `Direct` action that
opens the same fixed HTTPS route as Preview in a separate tab, preserving
paths and query strings. Raw LAN destinations are confined to management
runbooks rather than mobile navigation. Vaultwarden remains
proxy-only because its raw listener is intentionally bound to loopback, and
status-only backend cards have no navigation action.
The Home Assistant `:8188` wrapper permits its own origin as an intermediate
frame ancestor in addition to the explicit outer Homepage origins. This keeps
the allowlist narrow while allowing HA's nested authenticated app ingress, such
as ESPHome Device Builder and File Editor, to render inside the HA preview.
Preview URLs also inherit the outer Homepage hostname: IP-based Homepage access
uses IP-based proxy previews, while `homepage.home.local` access retains that
hostname. This same-site pairing is required for Home Assistant's strict
Supervisor ingress cookie and avoids intermittent add-on `401` responses.

September 30 access repair: standalone `Direct` now follows the same fixed
HTTPS routing as Preview. Bambuddy browser/PWA uses proxy `8207`; native
Bambuddy Mobile retains Tailscale Serve `8181`. Nginx's old `8181` listener is
LAN-address-only, removing a confirmed wildcard/Serve bind conflict. The
tracked Homepage access-contract test must pass before navigation/listener
deployments. Split DNS and certificate-verified representative proxies passed;
the owner confirmed general phone mobile-data navigation works. Grocy's
remaining raw-backend redirect was separately repaired with a proxy Host/port
fix and the owner confirmed it works. A controlled reboot drill remains separate.
workspace is a sibling immediately after the complete card grid, closes before
tab changes, is margin-bounded and acts as a splitter/work area rather than a
popup. On 2026-07-26 its responsive desktop and mobile heights were doubled,
allowing page scroll so embedded applications have substantially more working
space. Header and card surfaces use a 50% translucent dark-teal/light-teal visual system with
restrained outline shadows; the header's adaptive search fills remaining space
between the title, runtime resource widget and date/time.
On 2026-07-29 the responsive header, navigation, service-card and background
rules were repaired and visually verified at `320`, `350`, `375`, `390`,
`430`, `480`, `768`, `900`, and `1280` px. The header no longer overlaps,
narrow navigation and cards keep consistent gaps/padding, and the expanding
mobile glow was removed without removing the dark network artwork. The 390 px
embedded-workspace controls were exercised successfully.
Follow-up checks against the reported edge cases passed at exactly `956` px and
`489` px: header controls now reflow below `1230` px without search/title
encroachment, and stacked service cards have a measured `10.4` px row gap.
On 2026-07-29, Tailscale split DNS was added so the canonical
`https://homepage.home.local/` name can be used locally and remotely: OpenWrt
returns `192.168.20.102` on home WiFi, while the OnePlus tailnet client is sent
to the identity-gated AdGuard listener at `100.94.122.18`, which returns the
docker-host Tailscale address. On 2026-08-21, every user-facing Homepage card
was changed from a private-address direct link to its named fixed HTTPS proxy
(`443` or `8180`-`8209`; qBittorrent remains the fixed same-origin
`/portal-preview/qbittorrent/` route). The OnePlus grant is limited to DNS,
`tcp/443`, and `tcp/8180`-`8209` on that node; it is not a broad VLAN route.
The same card links work on home WiFi with Tailscale off because DNS resolves
the canonical name to the LAN address and the proxies are LAN-allowed.
The preview loading veil is pointer-transparent and becomes a delayed-preview
notice after six seconds, so it cannot trap the embedded UI when a service
blocks or delays iframe loading. Desktop service groups consume a single row
where space permits. Cards at 330 px or narrower grow vertically and reserve a
bottom action row; wider cards keep Preview equally inset from the top and
bottom. Hover no longer moves the action over the status indicator. Navigation
tabs now have visually distinct raised default, hover/focus and selected states.
The dock placement routine changes its parent only when Homepage replaces the
active layout. This prevents the former mutation/re-append loop that repeatedly
detached the iframe, blanked otherwise valid previews and moved controls during
pointer clicks. Household Hub and Mermaid Viewer were visibly rendered in the
live embedded workspace after the 2026-07-26 correction; Reload and Close were
also exercised successfully.
On 2026-08-09, Household Hub's workbench search authentication was repaired.
The browser no longer stores or submits the production API token; the web
container's Nginx proxy injects the existing bearer credential server-side for
same-origin `/api/` requests. Direct container-to-API requests remain protected
and returned `401`, while live recipe and YouTube searches each returned six
candidates without a browser token. The production web image build and
`nginx -t` both passed before the container was recreated.
The same 2026-08-09 maintenance updated only the frontend lockfile resolutions
for transitive `nanoid` (`3.3.18`) and `postcss` (`8.5.26`). A fresh production
build reported zero npm vulnerabilities; live health and recipe-search probes
returned `200`, and direct unauthenticated API access continued to return `401`.
Household Hub recipe review and Mealie handoff are now confirmation-gated and
durable. Reviews persist a UUID plus candidate/search provenance; imports require
that UUID and the matching source URL, reject duplicate/in-progress handoffs,
and record imported or retryable failed state. Search candidates and
assistant-extracted drafts use the same two-step workbench flow. Alembic revision
`20260809_0002` is live with an empty `recipe_workflows` table after deployment;
no live Mealie import was performed during verification.
Household Hub now also has a live read-only Grocy overview at
`GET /api/integrations/grocy/overview`. It uses a separate
`household-hub-read-only` Grocy API key and an application-enforced GET-only
client; Grocy does not provide per-key endpoint scopes, so all mutation routes
remain absent from Household Hub. The live probe returned the five seeded
locations and correctly reported empty stock and shopping lists.
The Obsidian Markdown exporter is configured at container path
`/exports/obsidian`, backed by the persistent host outbox
`/opt/stacks/household-hub/data/obsidian-exports`. This does not write directly
to Self-hosted LiveSync's plugin-managed CouchDB. A disposable recipe export
created valid Markdown and was removed after verification. The API now requires
a persisted confirmation UUID whose candidate title and source URL match the
draft; an unconfirmed live probe returned `404` and left the outbox unchanged.
Nextcloud is not
deployed and has no CalDAV credential; the workbench now exposes its valid
dry-run `VTODO`/`VEVENT` payload as a downloadable `.ics` file without claiming
live upload.
The integration deployment passed 62 backend tests, Ruff with the pre-existing
`TRY004`/`ISC004` baseline exclusions, production API/web builds, live API
smokes, desktop interaction and a 390 px mobile layout check. The mobile check
also caught and repaired a pre-existing dark-on-dark button-label override;
the final browser console had no warnings or errors.
The docker-host app-data job now includes the Household Hub Markdown outbox.
Its dry-run passed and real NAS run `20260809T130054Z` completed successfully,
capturing the new Grocy key state and creating
`latest/household-hub-exports`.
A fixed-target `homepage-preview-proxy` Nginx sidecar is live on docker-host.
It terminates HTTPS on the LAN and Tailscale addresses at `443`; HTTPS preview
ports `8180`-`8209` are
host-firewall scoped to the established management,
LAN, automation and Tailscale sources; it cannot proxy arbitrary destinations.
GardenKeeper, Bambuddy and Whoogle visibly load through it after their upstream
frame-denial headers are replaced with portal-scoped CSP. On 2026-07-26, the
source- and port-scoped OpenWrt rules were deployed and Proxmox, OpenWrt, Zyxel
and OMV proxy listeners were verified from docker-host (`200`). Router LuCI
requires a separate INPUT rule because traffic addressed to OpenWrt itself is
not an inter-zone forward. The OpenWrt `3000/3001` forwarding rule is live.
The monitoring VM now permits only docker-host `192.168.20.102` to its Grafana
`3000/tcp` and Uptime Kuma `3001/tcp` published ports. Matching `DOCKER-USER`
returns are applied by the enabled `monitoring-firewall.service`, so Docker's
forwarding path remains restricted after reboot.
Home Assistant now loads its login UI through HTTPS preview `8188`, with the
upstream local-CA certificate verified and WebSocket upgrade preserved. The
direct `8123` login cookie is not shared with this distinct origin, so the first
embedded visit requires a normal one-time HA login. GardenKeeper and Mermaid
Viewer were also visibly rendered through the HTTPS portal, and Reload/Close
were exercised successfully.
Frigate, Proxmox, OpenWrt, Zyxel, Grafana, Uptime Kuma, OMV and Transfer Portal
all have Homepage health sources and render a status dot. Frigate, OpenWrt,
Zyxel, OMV and Transfer Portal were visibly healthy after revalidation;
Proxmox uses the fixed-target proxy health endpoint because ICMP from the
Homepage container was not reliable. Docker-host UFW permits the Homepage
bridge `10.240.1.0/24` to reach only gateway port `8299/tcp` for this check;
the rebuild rule is tracked in `docker-host-ufw-homepage-previews.sh`. Grafana
and Uptime Kuma return through HTTPS preview proxy ports `8202` and `8186`
respectively; their Homepage status dots are healthy.
Its local network SVG now has a slow background and ambient-glow drift; both
animations are disabled for `prefers-reduced-motion`.
Mermaid Viewer is live at `http://192.168.20.102:8092/` and is generated from
the canonical project diagrams. `main/apps/mermaid-viewer/` is its only
repository source tree: `src/` is editable source, `dist/` is the single
checked-in release artifact, and the colocated release command packages,
verifies, checkpoints and deploys the complete stack. It supports search, deep links, pan, zoom,
fit, 100% view, fullscreen, source inspection and an adaptive full-width
layout in both direct and embedded views. Its dark canvas, controls and panels
use elevated glass surfaces over a subtle technical grid and network glow.
GardenKeeper and Household Hub have matching subject-specific backgrounds and
the same raised-glass card/button treatment; their reusable source layers are
in `apps/custom-site-themes/`. The Transfer Portal source has the matching
style prepared but is not deployed until OMV management access is restored.
The portal uses only non-secret configuration and remains an internal/Tailscale
surface rather than an authentication boundary.
Gridfinity Layout Tool (`gridfinity-layout-tool-v4.342.0`) is live at
`http://192.168.20.102:8093`; its
`gridfinity.home.local` is in the deployed 48-alias inventory. It
serves a pinned externally built static release through Nginx on the fixed
`172.32.0.0/24` Docker subnet, avoiding the prior overlapping automatic bridge
allocation. A Windows per-user 09:00 daily autodeploy checks the locally
recorded release, builds a newer upstream tag externally, and uses the atomic
health-checked deployment/rollback workflow in
`docs/install/services/gridfinity-layout-tool.md`.
Recomp Tracker is live at `http://192.168.20.102:8420` for personal habits and
workout tracking, with the fixed Homepage HTTPS proxy at
`https://homepage.home.local:8209/` for portal navigation. Its source is tracked in
`configs/docker-host/stacks/recomp-tracker/`, its Docker bridge is explicitly
allocated as `10.240.31.0/24`, and its firewall permits only management, LAN
and Tailscale sources. Its HTTP endpoint returned `200` during the 2026-08-19
reachability recheck. On 2026-10-10, frontend release r14/v33 added local
English nutrition-label photo OCR with review and persistent collapsible
Diet/Food library sections (browser/device preferences); it fixes split-line
calorie extraction, reduces the language download by about 82%, reuses prepared
workers and corrects root service-worker scope for OCR caching. The container
and database integrity checks passed; direct HTTP and Homepage HTTPS mobile
browser checks proved reload persistence and synthetic-label OCR without
production writes. Real packaging and phone-camera performance remain
unverified. Release image, checkpoint and rollback are recorded below as part
of the current service state.
On 2026-10-13, r15/v34 corrected Diet totals for archived quantity-based
constants, which must use their recorded g/ml amount rather than a 100g
snapshot. A Diet day now visibly lists any archived constants that remain
checked and permits a deliberate per-day removal while retaining the audit
snapshot. The healthy service uses
`recomp-tracker:release-r15-20261013`
(`sha256:1af9a1c40438448979cd064f2c6071c45c190481208797c8c989fc7b03b783c6`);
the pre-correction checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-archived-constants-20261013.db`.
On 2026-10-19, r16/v35 added date-specific custom one-time meal estimates:
description, inclusion tick and manual calories/protein/carbs/fat. These count
only for their selected day, never create a Food Library record and are not
copied into a new day. Backend validation bounds their shape and values. The
healthy service now uses `recomp-tracker:release-r16-20261019`
(`sha256:86608efd4836d0cafd7349b4ccc3794de5a32d47000f6c55385f255c15f3f521`);
the pre-update checkpoint is
`/opt/stacks/recomp-tracker/data/recomp-pre-one-time-meals-20261019.db`.
VM 103 has a 64 GiB virtual disk and 8 GiB RAM. On 2026-07-13 both app stacks were rebuilt from verified source,
their scoped HA credentials were rotated, the Hub database was baselined at
Alembic revision `20260617_0001`, and authenticated assistant probes passed.

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

On 2026-07-29 OMV gained a dedicated `media` export for the populated
`14tb/Media` tree, restricted to docker-host `192.168.20.102`. Docker-host
mounts it at `/mnt/omv/media` with a persistent systemd automount. The dedicated
`media-service` identity (`1007:100`) passed create/read/delete validation in
the new isolated library and staging roots; no legacy media path was changed.

On 2026-09-28, the Windows `Y:` (`NAS`) and `Z:` (`14tb`) SMB session was
authenticated as OMV `nasadmin`. Both shares allowed writes, but existing
filesystem ACLs denied this account writes in parts of the trees, including
`14tb/Media/study & work/Courses/New`. The `nasadmin` ACL now grants read/write
on existing files and traversal/write on directories throughout both share
roots, with default ACLs for new descendants. Ownership and other named ACLs
were retained. OMV-side create/write/delete probes as `nasadmin` passed at both
roots and at `Courses/New`; a Windows Explorer write recheck is still pending.
Pre-change ACL backups are on OMV at
`/root/acl-backups/{14tb,NAS}-20260928T162931Z.acl.gz`.

The first media foundation is live on docker-host:

- Jellyfin `10.11.11` on `8096/tcp`, with films, series, music and the future
  `immich-curated` export mounted read-only; hardware transcoding is disabled.
- Calibre-Web on `8083/tcp`, with write access only to
  `books/calibre-library`.
- Atsumeru on `31337/tcp`, with write access only to
  `comics/atsumeru-library` and local application state.

Each stack has a source-scoped UFW/`DOCKER-USER` policy, a restart proof and a
non-overlapping explicit Docker subnet (`10.240.10.0/24` through
`10.240.12.0/24`). This is mandatory: the first Jellyfin Compose attempt
automatically chose `192.168.0.0/20`, overlapping the management VLAN and
temporarily removing VM 103 management reachability. The stack was stopped,
routes recovered and every new stack was assigned explicit `10.240.x.0/24`
IPAM before deployment resumed.

Controlled remediation on 2026-08-21 recreated every project bridge at its
canonical explicit allocation and name, including Household Hub's shared
SearXNG/Mealie/Grocy dependencies and the four-consumer `local-alerting`
network. All application, storage, dependency, VPN-egress and firewall checks
passed. The persistent firewall covers Bambuddy port `8000` on IPv4 and IPv6,
and the Bambuddy routed-UFW policy and empty `10.240.23.0/24` bridge are ready;
the Bambuddy container itself remains on host networking because the P1S ports
are currently unreachable from VM 103. This is the sole failing assertion in
the live security audit and the only remaining remediation step.

Vaultwarden `1.36.0` is live with its raw HTTP listener bound only to
`127.0.0.1:8222`. Production access is through the fixed Nginx proxy at
`https://vault.home.local` using a dedicated local-CA certificate, HSTS and a
no-framing policy. Sign-ups and the admin endpoint remain disabled. A
SQLite-consistent NAS backup passed two isolated restore exercises, including a
disposable registered account restored into a second temporary container with
database integrity, exact-account-count and HTTP health checks. Owner onboarding,
2FA/recovery and emergency-access policy remain gated on live local DNS.
Backup run `20260729T160804Z` added Jellyfin, Calibre-Web, Atsumeru, ntfy and
Vaultwarden application state to the existing NAS job; the restored Vaultwarden
database passed `PRAGMA integrity_check` before the disposable proof was removed.

The Mullvad/Gluetun + qBittorrent gateway is live on `8084/tcp` with explicit
Docker subnet `10.240.20.0/24`. qBittorrent shares Gluetun's network namespace,
uses NAS-backed `/downloads/incomplete` and `/downloads/complete`, and cannot see
quarantine or any final media/book/document library. Mullvad recognized the
tunnel and its public route differed from the host. Dropping Gluetun's `tun0`
interface blocked qBittorrent public egress while the Web UI and host egress
remained available; automatic tunnel recovery then passed. The stronger full
provider-stop test also failed closed while host and unrelated-container egress
continued. Its permanent Web UI credential is in Windows Credential Manager as
`home-automation/qbittorrent`. NAS backup run `20260801T144643Z` passed an
isolated restore proof for the credential hash and both download paths.

The controlled docker-host package window completed on 2026-08-01: Docker CE
and CLI `29.7.1`, containerd `2.2.6`, Buildx `0.36.0`, Compose `5.3.1`, Python
`3.13.5-2+deb13u4`, and Tailscale `1.98.10` were installed. No reboot was
required, no package remained upgradable, `dpkg --audit` was clean, all 33
pre-existing containers remained running, both OMV mounts were present and all
tested local/monitoring endpoints passed.

The 2026-07-29 VM reboot exposed an AdGuard/Tailscale boot race: Docker tried to
bind `100.94.122.18:53` before `tailscale0` owned the address, leaving AdGuard
half-created without port bindings. The enabled
`adguard-home-compose.service` now waits for the Tailscale address and force-
recreates the Compose stack. Local and Tailscale DNS listeners plus the UI were
revalidated after installation.

Paperless-ngx, Actual Budget, Scrypted, Portainer, a local
registry mirror and Node-RED remain decision-gated candidates.

## Monitoring

- Uptime Kuma, InfluxDB, Grafana and Telegraf are live on VM 102.
- Bambuddy Prometheus-format metrics are collected locally on docker-host by
  host-networked Telegraf through `127.0.0.1:8000/api/v1/metrics`, written to
  the existing `dockerhost` InfluxDB bucket, and presented by Grafana's
  provisioned `Bambuddy Metrics` dashboard. This adds no Prometheus server or
  inter-VLAN metrics exposure.
- Proxmox, HA, docker-host, DNS, core apps and local-AI endpoints are monitored.
- Alert routing through ntfy exists for configured Kuma monitors. Grafana also
  uses an authenticated `ntfy Monitoring` webhook as its default notification
  policy; a live Grafana test notification succeeded on 2026-07-29.
- On 2026-07-29, stale Kuma checks were repaired for HA native HTTPS and the
  llama.cpp models API. New ntfy-enabled checks for OMV web, OMV NFS, and all
  three camera hosts are live and `Up`.
- OpenWrt now permits only monitoring VM `192.168.60.10` to Frigate API TCP
  `5000`, OMV TCP `80`/`2049`, and ICMP for camera hosts `.21`-.23. The OMV and
  camera checks pass. CT 111 now also allows the monitoring VM to Frigate API
  TCP `5000`; a direct monitoring-VM probe and Kuma monitor 28 both returned
  HTTP `200` on 2026-08-01.
- Kuma monitor 34 and the OMV `smartctl -H` heartbeat service/timer are live for
  aggregate disk-health reporting. The 30-minute timer uses a host-only token
  file and narrow OMV-to-Kuma network path; the first accepted heartbeat on
  2026-07-29 reported `All 5 physical disks report healthy`.
- Kuma monitor 36 tracks docker-host app-data backup freshness with a 25-hour
  push window. The existing backup service invokes its host-only-token producer
  in `ExecStartPost`, so a heartbeat is sent only after a successful backup;
  the first `Docker-host app-data backup completed` heartbeat was accepted on
  2026-08-01.
- Grafana 13.0.1 has two initial metric alerts in `Infrastructure health`:
  docker-host root disk and Proxmox root storage, each warning above 85% for
  10 minutes. Both evaluated `Normal` after creation. The reset Grafana admin
  credential is stored in Windows Credential Manager under
  `home-automation/grafana`; it is not stored in this repository.
- ntfy has a separate read-only `mobile-monitoring` account for the `monitoring`
  and `watchtower` topics. Its generated credential is stored in Windows
  Credential Manager under `home-automation/ntfy-mobile`. Mobile access is
  Tailscale Serve HTTPS at `https://docker-host.tail7012a0.ts.net`; the
  Homepage proxy binds both its LAN and Tailscale address on port 443; Tailscale
  Serve continues to own its separate MagicDNS endpoint.
- October11 mobile resource-alert acceptance failed: ntfy accepted both labelled
  test messages at20:55:15 BST, while the owner received neither on mobile data
  with Tailscale connected. Its ntfy subscription was disconnected; server
  statistics showed zero subscribers. Tailnet HTTPS8444 health passed normal
  certificate validation on docker-host and subscriber ACLs remained correct.
  Phone connection-error diagnosis and background delivery proof remain open;
  server acceptance must not be presented as working phone alerts. Details:
  [[../install/services/ntfy|ntfy manual]]. CA migration is prepared in the TLS
  procedure, with embedded MQTT trust dependencies and Frigate deferred.
- The live docker-host app-data job now snapshots ntfy's `user.db` and
  `cache.db` through SQLite's backup API. A fresh NAS run and temporary restore
  smoke on 2026-07-29 passed integrity checks for both databases.
- OMV NFS TCP 2049 and Proxmox storage pressure are checked by
  `home-automation-health-check.timer`. Backup storage is intentionally on md0;
  the old 86-87% high-water warning was cleared by the 2026-07-05 Proxmox
  check showing `omv-backups` active at 54.21% used.
- OMV SMART monitoring is globally enabled with a 1,800-second check interval,
  a 5 C change threshold and a 55 C maximum alert. Monitoring is enabled on all
  five physical disks (`/dev/sda` through `/dev/sde`); all reported `Good` on
  2026-07-29 at 33-44 C. No new SMART self-test schedule was added.

## Backup storage

- OMV is live on Storage VLAN 40 at `192.168.40.50`.
- Final backup storage lives on md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/`.
- Frigate/NVR recordings target md0 at
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/CCTV/`.
- OMV exports NFS paths for Proxmox backups, HA backups, docker-host backups,
  config backups, Immich DB backups, Immich media, and Frigate/NVR recordings.
- `scripts/backup/backup_vault_to_nas.ps1` provides a guarded, additive
  robocopy helper for the project vault. Its default dry run against
  `\\192.168.40.50\NAS\configs\home-automation-project` enumerated about 11,700
  files (229 MB) successfully on 2026-07-29. No scheduled vault-backup task has
  been created; first execution and restore proof remain approval-gated.
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
- On 2026-07-28, switch ports 2-7 were standardized as PoE CCTV access ports:
  VLAN 30 untagged, PVID 30, and excluded from VLANs 1/10/40. Port 1 remains
  the tagged router trunk and port 8 remains the NAS access port with PVID 40.
  The change was saved to switch startup configuration. Live validation showed
  cameras on ports 2-4 at approximately 10 fps, including recovery of the gate
  camera at `192.168.30.22` after correcting port 4 and cycling only its PoE.
- On 2026-09-27, router `lan5` gained tagged VLAN 10 while retaining untagged
  VLAN 1 as its recovery PVID. The admin PC's Realtek Ethernet NIC uses VLAN ID
  10 and renewed DHCP to `192.168.10.132` with router/DNS `192.168.10.1`;
  source-bound Ethernet ping and SSH to the router passed. `lan3` remains the
  VLAN 1/10/30/40 managed-switch trunk. The switch remains disconnected, but
  OMV is directly attached to router `lan4` and answered a router-origin ping
  on `192.168.40.50`. The PC's persistent Ethernet routes now cover
  `192.168.20.0/24`, `192.168.30.0/24`, `192.168.40.50/32`, and
  `192.168.60.0/24`; both Y:/Z: SMB mappings returned `OK`, Homepage HTTPS
  returned `200`, and HA HTTPS answered on `8123`. Mullvad remains connected;
  its DNS leak protection still blocks direct queries to router DNS for
  `home.local` aliases while the VPN is active.
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

- Frigate reconnection/acceptance and expansion beyond the three existing ANNKE cameras, including any fourth
  camera, remaining motion/zone tuning, and later AI-rule decisions.
- Most VentSys physical hardware, remaining ESPHome adoption and full safety
  acceptance testing.
- P1S camera acceptance and any physical safety-interlock expansion beyond the
  present telemetry, dashboard and notification baseline.
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

October2: recurring Household Hub cold-checkpoint source, ten isolated tests and
service/timer templates are prepared. Live read-only preflight passes for the
expected NAS mount and all five current containers/three owned volumes. The job
is not installed/enabled and no new live checkpoint was made. September15 remains
one-off proof; [[../procedures/household-hub-coordinated-backup|manual generation, restore and outage scheduling]]
remain maintenance-gated acceptance work.

Migration snapshots named `pre-lxc-migration-20260620` exist for retired VM 101
and VM 104. Daily Proxmox jobs now retain 7 daily and 6 monthly generations on
`omv-backups`; projected retention fits the current md0-backed storage after
the 2026-07-05 capacity check, and both CT 111 and CT 114 have manual successful
proof after the `tmpdir=/var/tmp` change. Consult
`scripts/backup/backup_strategy.md`.

## Desktop SSH management — 2026-09-30

### Admin desktop routes — verified 2026-10-20

Five persistent project routes use gateway `192.168.10.1`, metric1:
`192.168.20.0/24`, `192.168.30.0/24`, `192.168.40.50/32`,
`192.168.60.0/24`, and the owner-added `192.168.35.200/32` printer exception.
The selected printer path is Ethernet; TCP8883/990/6000 passed with Mullvad
connected. Windows events show HomePrinters Wi-Fi connected October19 and
disconnected October20 at08:37, explaining previous direct access without a
saved printer route. Exact last successful Orca connection remains unknown;
application acceptance is pending. Inventory and recovery commands:
[[windows-admin-pc-routes|Windows admin PC project routes]].

Root key authentication from the Admin Windows desktop is verified with `ssh -o BatchMode=yes omv-lan`. The existing local SSH alias targets `192.168.40.50` as root using the desktop OMV Ed25519 identity. Its public key was added to `/root/.ssh/authorized_keys`, preserving existing entries; directory/file permissions are 700/600. No SSH service, password-login policy, firewall or SMB settings changed. Keep private keys and passwords outside tracked files. Live hostname returned `omvnas`. For transfer diagnostics, `vmstat` and `/proc/diskstats` are available; `iostat` is absent.

### OMV Print and Media storage

Both data mirrors were healthy at the last recorded acceptance. Windows Y: maps
Print and Z: maps Media. Media filesystem UUID is
`a8843f98-c937-48a8-aefa-4cd0fb80667c`; scoped NFS exports serve the media
libraries and backup clients. HA `nas_backups` and Proxmox `omv-backups`
retain their storage identities. Filebrowser uses the guarded Print/Media
composite view. Owner access and isolated backup restore checks passed. Native
application links on offline clients have not all been verified.

October2 at21:30 BST: the prepared host-local JSON collector produced one-off
read-only evidence for five disks, both expected UUID mounts, root capacity,
md0 and four active NAS daemons. All disks report SMART passed,30–42 C, with
no reported pending/uncorrectable/reallocated sectors. Lifetime CRC1 and a
separate historical threshold bitmask32 remain warnings; no new fault is inferred.
md0 has zero degraded members and idle sync action. Six isolated tests pass;
collector scheduling, metric shipping and NAS dashboard acceptance remain open.
See [[../procedures/omv-health-collector-preparation|source and deployment contract]].

- October20: VentSys frontend `20261019-7` live: cyan Environment glow,
  enclosure tops y263 and shared box bottoms y800 verified. Backend unchanged.
  Grouped mode/state redesign requested and semantics being confirmed; see
  `../procedures/ventsys-dashboard.md`. E2 again unavailable on browser observation.


- October20 VentSys frontend `20261020-3` and operating-mode package are live.
  Independent FDM/SLA Enclosure/Print/Purge intents and separate Booth compose
  shared paths; revision/concurrency/manual-conflict guards apply in HA. Purge
  levels2/4/6/8/10 request20/40/60/80/100%, strongest active request wins; physical
  mapping remains uncalibrated. Review steps/physical-position fields removed,
  labels enlarged. 38 Python +39 browser +24 model tests and HA config/template/UI
  checks passed without actuator commands. ntfy rules remain proposed, phone
  delivery and hardware acceptance open. E2 native unavailable; current entry
  host is `.51` despite prior `.52` recovery claim, and `.52` did not answer two
  HA-host pings. Canonical E2 MAC/IP unchanged. See service manual for rollback.


- October27 E2 reporting recovered: desktop COM4, MAC `ec:e3:34:b4:79:7c`,
  correct October10 firmware/hostname/topic and MQTT TLS at `.52` confirmed.
  HA's stale `.51` host was corrected through authenticated Reconfigure;
  persisted `.52` and native E2 branch0% on the unchanged dashboard verified.
  Ping failure did not mean offline; do not diagnose MQTT filtering from the
  router's generic WAN-block log prefix alone. No flash, firewall change or
  valve command. Remote actuation/physical travel acceptance remains separate.
  See dashboard manual for exact diagnosis and connection repair.

- October27 Setup/test release20261027-1 is implemented and tested, but NOT LIVE.
  39 Python +42 browser +24 model checks pass; valve-only reviewed subsets leave
  fans/intents unchanged, with active-mode/fan/failsafe and concurrency guards.
  Activation awaits attachable signed-in HA panel. Private prepared checkpoint
  `/config/backups/ventsys-setup-test-20261027-193629Z/`; live remains20261020-3.
  See dashboard service manual for exact resume/deployment/rollback steps.


- October27 Setup/test release20261027-1 is now LIVE after the signed-in panel
  was restored. HA config valid, all three script paths idle, resource version
  saved and five asset/three package hashes verified. Available valve tests are
  selectable; exact SLA targets/skips reviewed then cancelled without sending.
  Normal modes retain full-path guards. Tests:39 Python,42 browser,24 model.
  Private checkpoint `ventsys-setup-test-20261027-193629Z`; service manual has rollback.

### OMV SMB recycle access — 2026-11-04
Print and Media SMB bins retain files 30 days; unrestricted max size. Share extraoptions include `recycle:subdir_mode = 0770` so inherited Filebrowser ACLs are effective on new recycled directories. Existing recycle directory ACL masks were adjusted to give filebrowser access; this also activates other pre-existing named/group ACL entries. Backups before changes are on OMV at `/root/recycle-filebrowser-acl-20261104/` (ACL files and SMB share config). Samba deployment restarted smbd. Media disposable SMB delete then Filebrowser UI move restore passed; Print move restore tested as filebrowser OS identity. Newly created subfolder SMB deletion and service-identity restoration passed on both. Test folders remain at share roots. Restores for deleted files owned by other identities or inaccessible source files remain unverified; NFS and Filebrowser deletions bypass SMB recycle. Rollback: restore relevant SMB share extraoptions from backup through OMV, deploy Samba; restore ACLs with `setfacl --restore` using the matching saved ACL file after checking current state.

### Windows development-tool storage — 2026-11-04
Windows Admin user Conda config (`C:\Users\Admin\.condarc`) now prefers `K:\Documents\Cache Folders\conda\envs` and `...\conda\pkgs`, retaining C: fallback paths and existing voice310/facefusion environments. PlatformIO Core is fully migrated to the space-free `K:\Documents\Obsidian\home-automation-project\main\PlatformIO`: user `PLATFORMIO_CORE_DIR` resolves to that directory and `PLATFORMIO_PACKAGES_DIR` to its `packages` child, including tools, package cache, PlatformIO's virtual environment and the ESP-IDF dependency environment. The generated core is intentionally Git-ignored. On November5 the PlatformIO6.1.19 launcher was rebuilt at its existing version after the relocation, then `pio system info` and the global package inventory passed against this core (14 installed platform/tool dependencies); no PlatformIO, framework or toolchain versions were upgraded. A clean ESP-IDF/Arduino `ventsys-main-valve-1` rebuild completed from the K: core on November4, generating `firmware.bin` (1,139,344bytes) without using `C:\Users\Admin\.platformio`; no firmware was flashed. ESP-IDF rejects paths containing spaces, so the earlier `K:\Documents\Cache Folders\platformio` copy is not the active location. The original C: core was manually removed after this proof; restart VS Code/ESPHome or any open terminals so they inherit the new user settings. PlatformIO test junction `K:\PlatformIOCache` points at the earlier spaced folder and remains because automatic review blocked its removal; it is not the active package path. The Visual Studio temporary staging folder `C:\Users\Admin\AppData\Local\Temp\k1bdwnii` remains after the same review blocked deletion.

- November10 monitoring access audit: existing VM102 checks largely reachable, but missing MQTT/HTTPS/new-service router permissions recorded in `docs/audits/2026-11-10-monitoring-network-access.md`; router unchanged. Repaired OMV SMART heartbeat timeout caused by a missing DOCKER-USER allowance after chain rebuild; full source now preserves it and service ordering is explicit. Kuma recovered at08:22:55UTC, all five disks healthy.

- November10: confirmed VM102 access gaps closed with exact-source/destination router rules for HA MQTT8883 and VM103 HTTPS443/8193, Hub8100, Jellyfin8096, Calibre8083, Atsumeru31337 and qBittorrent8084. HTTPS host UFW rules persist. All eight TCP paths verified; protocol-level MQTT/HA/ntfy checks passed. Optional restricted endpoints in the audit remain intentionally outside these allowances.

- November11 Kuma monitors37–44 check the eight newly reachable endpoints.
  All latest states pass with ntfy routes and two retries configured. Existing
  local CA trust was added to Kuma for verified HTTPS checks. Owner completed
  Homepage browser checks. The deployed home-operations widget covers 43
  monitors and the heartbeat API reports 40 Up and 3 Down, the disconnected
  cameras. See the monitoring roadmap for rollback and delivery limits.

