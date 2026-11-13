---
title: TO-DO completed items archive (to 2026-11-13)
description: Completed checklist items moved out of main/TO-DO.md on 2026-11-13; nothing open was moved
tags: [tasks, archive]
created: 2026-11-13
modified: 2026-11-13
type: archive
status: archived
---

# Completed TO-DO items (archived 2026-11-13)

Moved verbatim from [[TO-DO]], grouped by the section they came from. Open items stay in TO-DO.


# Project Task List

- [x] Integrate Kuma status on Homepage Home, verify its status data and
  complete notification routes/retries for the eight new checks.
- [x] Add tested offline firmware-report comparator and MAC-guarded read-only
  capture; image-acceptance verification remains manual and OTA coupling pending.
- [x] November4 owner confirms standard print, enclosure and main valve physical
  and displayed travel is 0–100%; 360 intakes remain a distinct raw30–60 mapping.
- [x] November4: deploy UI20261104-4 normalized360 opening, integer RPM/gas,
  upward flow arrows and FDM sensor reassignment (firmware and HA labels).
- [x] November4: repair recurring E2 HA host and stale router MAC reservation;
  temporary connection/identity monitor later stopped by owner; cause unproven.
- [x] Investigate recurring E2 HA `.51` host rewrite: retained MQTT ESPHome
  discovery for MAIN-1 advertised `.51` with E2's MAC. Removed that stale
  retained record on November10 and verified it absent. Direct HA config-flow
  correction restored E2 `.52` and fresh telemetry. Graphical reconfigure had
  twice aborted against MAIN-1 even after showing `.52`.
- [x] November10 retained-discovery follow-up: remove obsolete
  `ventsys-sla-sensor` advertisement for the board now assigned to FDM `.32`;
  fresh broker subscription contains only the matching FDM sensor and SLA
  airflow discovery identities. Preserve retained VentSys state/alarm topics.
- [x] November10: migrate continuous discovery alerts/capture and five-minute
  HA identity/E2 checks to VM102 systemd with ntfy; interim VM103 install removed. Desktop collector stopped
  and Codex heartbeat paused; temporary broker logging rollback remains open.
- [x] November4: both C6 intake GPIO2 digital touch firmware updated; SLA60
  known-command reference restored without PWM and accepted-image restart verified.
- [x] October20: deploy VentSys independent grouped modes and purge strengths,
  single value confirmation and larger entity labels. See dashboard service manual.
- [x] October27: resolve E2 identity/host discrepancy: COM4 MAC verified, MQTT TLS
  online at `.52`, HA reconfigured from `.51`; native dashboard0% recovered.
- [x] October28: flash/adopt normal FDM print valve COM4, MAC
  `EC:E3:34:B4:76:A4`, `.55`; native report and MQTT TLS verified.
- [x] October29: flash/adopt normal SLA print valve COM4, MAC
  `EC:E3:34:1B:DB:2C`, `.56`; original4MB backup, write hashes, MQTT TLS and
  command-free native startup verified. Physical movement/load testing remains pending.
- [x] October27: activate explicit VentSys Setup/test option for available valves,
  reviewed exact targets/skips, fan exclusion, intent locks and bounded reports.
  Live review/cancel verified without commands; normal mode full-path checks kept.

## Next project steps

- [x] November 6: flash SLA pipe air ESP32-C6 `CC:BA:97:F0:C3:0C` on COM3
  with BME680 SDA/SCL on GPIO4/5 (I2C address `0x77`) and CO on GPIO3;
  verify factory-image hash, encrypted API, BME readings, and HA adoption in Garage.
- [x] November 7: deploy VentSys Clear alarms popup listing live latched boards,
  with per-board acknowledgment blocked for active alarms and faults.
- [x] November 7: add read-only VentSys Diagnostics tab with searchable live
  HA entity states, CO voltage and board/controller stats; live view verified
  with 294 exposed entities. Add rail/servo supply telemetry only after hardware
  and firmware expose those measurements.
- [x] November 7: deploy SLA pipe board dropout warning and two-minute ntfy
  alert with 30-second recovery, plus dashboard warning for its CO-voltage
  entity disappearing while the board is online. Live rule loading verified;
  induced outage and phone receipt remain untested.
- [x] Define a 12-board expected-online VentSys roster and per-board maintenance
  switches. Deploy general dropout/recovery ntfy for 11 boards; SLA pipe keeps
  its separate rule. Live maintenance on/off control verified. Critical
  non-board entity availability still needs its own severity rules.
- [x] October21: reassign old FDM airflow `CC:BA:97:F0:D0:A0` to Booth `.43`
  by MAC-verified OTA; flash replacement `CC:BA:97:F0:E3:DC` as FDM `.41`
  over COM5 with verified hashes. Both encrypted APIs confirm correct identity
  and live zero-flow readings; Builder sources synchronized.
- [x] October 19: flash SLA airflow ESP32-C6 `CC:BA:97:F0:D3:10` over COM9,
  verify hashes and API reachability at `.42`, adopt in HA Garage and sync
  Builder YAML. Correct GPIO0 pulse/GPIO1 LED mapping and reflash with verified
  hashes after owner wiring clarification. Physical airflow/pulse response and
  four-blade pulses per revolution still need testing.
- [x] October18: restore full 0–100 VentSys dashboard/control range and all
  mode-script open targets; deploy the narrow live patch, validate HA config,
  reload scripts and verify served bytes. No physical movement test performed.
- [x] October 18–19: deploy the authenticated VentSys card, remove/revoke the
  exposed credential, replace optimistic/offline/stale displays, correct smoke
  precedence and pressure/gas/flow semantics, add exact native controller
  inventory and serialized reviewed commands, and validate desktop/phone and
  keyboard operation. 20 model + 10 backend + 19 browser tests passed; real HA
  startup sent no commands. See [[docs/procedures/ventsys-dashboard]].
- [x] October 19: add VentSys to Homepage Home & Security with Open tab through
  the existing authenticated HA proxy. Navigation, 390 px action bounds and
  served card bytes passed; no new port, credential or control iframe added.
- [x] October 19: activate and verify `20261019-1` through normal HA sign-in:
  bind FDM `.62`/`a0:85:e3:ae:5b:c8` to legacy `ventsys_sla_360...` entity IDs,
  and SLA `.61`/`cc:ba:97:f0:e3:ec` to legacy `ventsys_fdm_360...` IDs. Keep the
  already-correct MQTT topics and accepted 30–60 firmware unchanged. Show
  uninstalled devices as expected setup notes. See [[docs/procedures/ventsys-dashboard]].
- [x] October 19: add read-only semantic mode-script deployment comparison;
  three regression tests passed. Live comparison isolates fire-safe speed drift;
  all 12 manual modes and helper match. See dashboard audit/runbook.
- [x] October 19: deploy backend `20261019-arbitration-1`: shared normal
  dispatcher, per-publish failsafe gate and fire preemption; reconcile explicit
  fire-response main-fan 100%. Eight arbitration + 11 backend + three drift tests
  and isolated real-HA no-MQTT contention/preemption probe passed.
- [x] October 19: deploy frontend `20261019-2` with dispatcher busy/unavailable
  messages, immediate takeover interruption and explicit alarm headings. Four new
  regressions; 24 browser tests passed; real HA connected/ready, no commands.
- [x] October 19: deploy frontend `20261019-3`: three-column Environment
  comparison (Ambient/FDM/SLA) and System log with actual session events.
  26 browser tests passed; desktop/mobile and signed-in HA verified; no commands.
- [x] October 19: deploy separate seven-inch touch view, preserving standard
  layout and all diagram coordinates. Restore original-style title/header and
  bottom status bar with truthful telemetry; fix protruding highlight strips and
  enlarge log text. 30 browser tests passed; live popup/config/hash checks passed.
- [x] October 19 owner-reported control failure repair: verify running-firmware
  intake subscriptions and correct crossed command topics in dashboard/all modes;
  reconfigure E2 HA host `.51`→`.52`; allow exact reviewed available-controller
  mode subsets and explicit same-target resends. Deploy frontend `20261019-5` /
  backend `20261019-command-repair-1`; software/HA read-only validation passed.
- [x] October 19: restore saturated valve colours and align four diagram box
  bottoms in frontend `20261019-6`; 34 browser tests passed, visual-only change.
- [x] October11: deploy Resource Health on the existing VM103 troubleshooting
  app and add Homepage Monitoring entry; retain independent Proxmox alerts and
  VLAN restrictions. Add named ping/DNS/TCP/HTTP checks, console input/output,
  route TCP buttons and incident-report evidence.20 model and10 API tests plus
  desktop/mobile guided and HTTPS live-tools smoke passed.
- [x] October11: add certificate trust/expiry checks, nine guided bundles for
  all37 investigations, and bounded30-day/1,000-event history with timed
  Grafana/log links. Backend and live desktop/mobile extension checks passed;
  primary alerts remain independent.
- [x] Plan Home Local CA replacement/distribution with critical CA key-usage
  extension. Strict Python3.13 verification flags current CA code92; separate
  legacy chain/name/date verification passes for Homepage/HA/Frigate/Vault.
  See [[docs/procedures/ssl_tls_guide|TLS procedure]]; preserve endpoint/client
  trust during a staged maintenance rollout.
- [x] October11: harden resource-monitor timeout/retry/recovery handling;
  remove notifier start-limit latch, preserve fresh partial coverage and OOM
  baselines, queue undelivered incidents through recovery, add supported status
  output and update watchdog. Ten tests and live six-system collection passed.
- [x] October10: audit all VMs/CTs after Frigate recovery; increase VM102 to6GiB
  after a historical Grafana OOM, expand VM103 root online to128GiB, deploy the
  every-minute host/guest pressure monitor and hourly collector watchdog.
  Six-system coverage and authenticated ntfy test passed. See
  [[docs/procedures/resource_pressure_monitor]].
- [x] October4: add saved Recomp routine schedule projection and versioned
  four-source Today bundle, retaining three-source compatibility. Weekday/move
  semantics, unknown completion/readiness and privacy boundaries pass45 unit
  tests and three1440/320px browser suites. No personal records fetched or writes;
  household pilot, diagnostic/recovery composition and live release remain open.
  See [[docs/procedures/read-only-product-release-plan]].
- [x] October4: combine saved GardenKeeper, Grocy and Mealie sources in one
  explicit local bundle. Independent freshness, unavailable isolation, atomic
  rejection and reserved source summaries pass38 unit tests plus three browser
  suites at1440/320px. No API requests or source writes; real-data pilot, Recomp
  and diagnostic/recovery composition remain open under
  [[docs/procedures/read-only-product-release-plan]].
- [x] October4: implement saved Mealie meal-plan import from its verified public
  paginated schema. Explicit date selection, privacy, freshness and unknown
  ingredient availability survive; partial pages do not certify coverage.
  All33 unit tests and three1440/320px browser suites pass. No household records,
  credentials or source writes; real-data pilot/live release remain open under
  [[docs/procedures/read-only-product-release-plan]].
- [x] October4: unify strict saved-source time validation; health imports can
  no longer mark24:00 rollover or slightly future observations healthy.
  Microsecond source timestamps remain supported. All28 unit tests and three
  desktop/320px browser suites pass, including backup/recovery unknown states.
  No live changes; [[docs/procedures/read-only-product-release-plan]].
- [x] October4: fix local Workbench overlapping-import state: Clear,
  demonstration and newer selections invalidate earlier reads and errors.
  Dependency counters now state their scope. Controlled delayed-read browser
  checks pass at1440/320px, along with25 unit tests and all three browser suites.
  See [[docs/procedures/read-only-product-release-plan]]; no live deployment.
- [x] October4: implement saved GardenKeeper task imports in the existing local
  Workbench, against the verified read-only API schema. Only pending tasks,
  validated UTC due times and scoped freshness survive; private fields are
  omitted. All25 unit tests, dedicated1440/320px checks and general/recovery/Grocy
  browser regressions pass. Shared credential-fragment filtering and list
  indentation are repaired. Real-data pilot and live release remain open under
  [[docs/procedures/read-only-product-release-plan]].
- [x] October4: implement local Solar Observatory foundations: Horizons fixtures,
  interpolation, shared path transforms, camera maths, expiring read-only
  safety receiver and local cache publication. Typecheck and 25 tests pass;
  no dashboard/card or live deployment changes. See
  [[docs/procedures/ventsys_solar_screensaver]].
- [x] October4: add the single-renderer Earth/Moon, Jupiter/Io and Saturn
  geometry preview. Build, 26 unit tests and seven Chromium tests pass at
  compact desktop/mobile sizes; screenshot review corrected Saturn framing.
  It remains a local matte-geometry study, not a deployed screensaver.
- [x] October4: wire the separate read-only Solar Observatory candidate host
  and labelled simulation harness. Build, 29 unit and 14 browser tests pass,
  including heartbeat expiry and reload-persistent alert acknowledgement.
  No authenticated HA acceptance or deployment is claimed.
- [x] October4: add local NASA Earth/Moon 2K surface maps and a muted
  photographic ESO Milky Way backdrop, visible credits and bounded shared
  texture loading with geometry fallback. Orientation remains illustrative;
  other bodies and rings still need final assets.
- [x] October4: implement approximate IAU Earth/Moon surface attitude and
  bounded UTC-to-TDB conversion. Build, 49 unit and 19 browser tests pass;
  independent SPICE fixtures verify the model, not precision navigation accuracy.
  Time coverage ends July1 2027 pending leap-second review. No live changes.
- [x] October4 audit batch: repair four historical navigation targets and all11
  unresolved wiki links, with source-backed optional-tool stubs and corrected
  RAG methodology wording. Review20 existing deleted paths without restoring
  deliberate copies; retained Mermaid release passes five hashes and16-diagram
  desktop/mobile browser verification. See
  [[docs/audits/2026-10-02-roadmap-code-file-audit]].
  Reproduce the complete local TransferPortal suite with external dependencies:
  62 pass,2 Windows symlink skips; live hardening remains undeployed.
- [x] October4: reconcile monitoring-roadmap historical/live wording and refresh
  CT114 package-path blockers read-only. Fail2ban/proxy remain absent; CT114
  cache probe times out and loopback upstream metadata still returns503.
  No deployment; [[docs/procedures/ct114-package-path-repair]] retains the gates.
  Read-only Proxmox configuration also confirms6 cores/28 GiB/no swap; conflicting
  current AI-host guide/wiki descriptions and rebuild parameters are corrected.
- [x] October4 batch: prepare guarded current-state Flux queries, independent
  producer/timer input and a consolidated manual acceptance/rollback checklist.
  Nineteen synthetic cases (32 actual Flux executions) verify retained-value
  suppression, age expiry, partial evidence, no-data and unit-state handling.
  No bucket writes or live configuration changes; end-to-end delivery and UI
  acceptance remain open under [[docs/procedures/omv-health-collector-preparation]].
- [x] October4: prepare the dedicated OMV-local Telegraf input fragment and
  repeatable synthetic parser rehearsal. All five cases match exact labels,
  fields and values using Telegraf1.38.3 in output-free test mode;18 Linux tests
  remain passing. OMV consumer permissions, delivery and dashboard acceptance
  remain open under [[docs/procedures/omv-health-collector-preparation]].
- [x] October4: prepare the OMV snapshot-to-Prometheus stdout adapter with
  missing/invalid/stale signals, bounded stable labels and unknown readings
  omitted. All18 Linux tests pass. Integration, shipping and live activation
  remain open; see [[docs/procedures/omv-health-collector-preparation]].
- [x] October4: prepare OMV atomic snapshot publisher and restricted service/timer
  templates. Eleven Linux tests and unit syntax checks pass; no live install,
  group, schedule or metrics shipping. See [[docs/procedures/omv-health-collector-preparation]].
- [x] October2: repair verified code-audit source defects in TransferPortal,
  router tooling, HA integrations, VentSys templates, displays and monitoring.
  See [[docs/audits/2026-10-02-code-audit-verification|repair evidence and limits]].
- [x] October2: TransferPortal matched stopped NAS checkpoint and isolated VM
  restore/history/preview/copy/helper-denial acceptance passed for both generations.
  Evidence: [[docs/audits/2026-10-02-code-audit-verification]]. Test VM removed.
- [x] October 2: audit roadmap/source/files and add the repeatable Git-aware
  checker at `tools/repository-audit/`; fix Transfer Portal's predictable
  session-secret fallback locally, Hub lint and the Obico manual link. See
  [[docs/audits/2026-10-02-roadmap-code-file-audit|Audit and verification]].
  Production deployment and full feature acceptance are separate.
- [x] October2: diagnose CT114 package/security/Fail2ban state read-only and
  prepare the host-only cache permission helper, proxy template and tested
  [[docs/procedures/ct114-package-path-repair|repair procedure]]. No live changes.
  Fail2ban is absent, June security indexes expired, UFW blocks CT114 cache
  access and cache upstream metadata currently returns503.
- [x] October2: prepare recurring coordinated Hub backup logic, ten isolated
  tests and service/timer templates; live read-only mount/container preflight passes.
  See [[docs/procedures/household-hub-coordinated-backup|activation and rollback]].
- [x] October2: curate seven dated recovery records for the local Workbench
  and generate a scope-preserving offline index using `recovery-pack.mjs`.
  Twelve unit tests and desktop/320px import checks pass. Historical backup
  success stays stale; component/boot restore proof does not certify full recovery.
  Live evidence adapters, complete emergency-pack coverage and deployment remain open.
- [x] October2: prepare saved Hub Grocy overview conversion for local Today at
  Home imports. Sixteen Workbench tests and desktop/320px fresh/stale/unavailable
  checks pass; notes/unknown fields are omitted and best-before semantics preserved.
  Real-data pilot, live adapters and integrated product acceptance remain open.
- [x] October2: accept saved Grocy envelopes directly in the existing file picker,
  recalculating freshness on import. Verify BOM files, error/oversize handling,
  previous-evidence preservation and Clear at desktop/320px; no CLI step required.
- [x] October2: build the portable recovery runbook pack for seven curated
  systems with 13 selected documents, clickable index, link manifest and checksums.
  Twenty unit tests and independent verification of all17 checksummed files pass.
  Omitted dependencies are explicit; full-estate executable recovery stays open.
- [x] October2: inspect dashboard8094 IPv6 bind/bridge/rules/counters and prepare
  the tested source-only deny policy. Current publish is IPv4-only; failed client
  probes do not certify firewall denial. See the IPv6 publication guard procedure.
- [x] October2: prepare the host-local OMV JSON collector and six isolated tests;
  verify a live one-off read-only snapshot for load/memory, five disks, md0,
  exact UUID mounts and four daemon states. Preserve historical SMART warnings.
  Scheduling, least-privilege shipping and NAS dashboard delivery remain open.
- [x] Reconcile the current non-hardware roadmap against September15–17 evidence
  and create bounded contracts for the first read-only household release,
  recovery readiness, hardening/resilience, SMB case-collision recovery, the
  dashboard IPv6 guard, and the VentSys card/page bridge (2026-09-18). These
  plans do not authorize live deployment, credential rotation, firewall edits,
  deletion, or safety controls.
- [x] September16: scheduled Watchtower report reached ntfy; corrected the
  available-update count from Updated to Stale after comparing the report with
  scan logs. Isolated stale-image delivery test passed; correction deployed.
- [x] September15–16: coordinated Hub cold backup/restore passed; ten executable
  images preserved; all six app images also rebuilt offline from source using
  preserved base images, Python wheels and npm cache. Runbooks contain NAS paths.
- [x] September16: persist GardenKeeper journal media at the effective
  `/data/journal-media` path. The zero-file host directory is now root-only,
  mounted into the recreated API and included in the normal OMV app-data backup;
  API health/ready passed and worker/web were unchanged. A matched-dump/current-
  image isolated synthetic upload survived API recreation with the same hash.
- [x] Verify September15 archives: VM100/102/103 decompression plus VMA verify,
  CT111/114 decompression plus tar traversal. Last result durably recorded
  September16. These checks do not establish application-consistent recovery.
- [x] September17: execute the documented isolated monitoring VM102 restore
  drill from `vzdump-qemu-102-2026_09_17-02_01_27.vma.zst` into freshly checked
  ID9102 on `local-lvm`. The copy had no NIC, `onboot: 0`, no inherited startup,
  passthrough or hook; the serial console emitted no output, but its guest agent
  became ready after about 100 seconds and proved Debian 13 plus mounted EFI and root
  filesystems. Guest-agent shutdown passed. Leave the stopped temporary ID9102 in
  place pending explicit owner confirmation before any destruction.
- [x] Verify dedicated Proxmox workstation SSH after owner key installation
  (2026-09-14); collect fresh snapshot and pass all eight required capacity,
  mount and backup-freshness checks. Dashboard model acceptance also passed.
- [x] Complete browser import using fresh September15 Proxmox JSON through the
  existing live desktop/mobile smoke suite. Integrity/restore proof is separate.
- [x] Install dedicated Proxmox dashboard snapshot command at
  /usr/local/sbin/home-automation-dashboard-snapshot; preserve scheduled probes.
- [x] Add Vaultwarden direct card to Homepage Home & Security (2026-09-14);
  normal browser DNS/TLS verified. No iframe, onboarding or auth changes.
- [x] Obtain Proxmox JSON through the owner-authorized SSH session; September14
  dedicated key login and required evidence validation now pass.
- [x] Complete the September12–14 recovery batch: GardenKeeper backup repair/
  seven tests/live success, SearXNG semantic template verification, six recovered
  source builds, isolated PostgreSQL/API and Qdrant restores, MediaMTX scheduled
  configuration checkpoint/restore and owner-selected manual recording review.
- [x] Preserve offline source-build dependencies and prove coordinated Hub
  multi-store recovery (September15–16); full-system integration proof remains open.
- [x] Capture protected off-VM GardenKeeper/Hub scoped source snapshots and
  SearXNG settings; verify hashes (2026-09-11). Source provenance, complete build
  inputs, semantic settings review and isolated restore still remain.
- [x] Locate live GardenKeeper/Hub source and inspect migration contracts/schema
  metadata read-only (2026-09-11). Preserve destructive-reset/startup migration
  boundaries in runbooks. Provenance/off-host source and restore proof remain.
- [x] Restore missing Vaultwarden SNI route and verify the correct certificate
  with normal browser validation (2026-09-11; explicit DNS mapping).
- [x] Owner chose to preserve Mullvad DNS/filtering and handle exact local names
  separately (2026-09-12); see DNS resolver decision.
- [x] Apply local Vaultwarden hosts entry and verify normal browser HTTPS
  (September14). September15 confirms Mullvad custom DNS remains disabled
  with the same content filters; public DNS behavior was preserved.
- [x] Distinguish DNS/network/TLS/timeout collector failures and add VPN/SNI
  troubleshooting guidance (2026-09-11). Revocation availability remains separate.
- [x] Correct VM103 workstation SSH identity selection (2026-09-11): alias and
  raw-IP access both verified with the existing key and strict host-key checking.
  Resume GardenKeeper/Hub source discovery; no server authentication changes.
- [x] Consolidate all 42 named service/roadmap entries into the installation
  checklist coverage audit (2026-09-11): now 36 Written, 0 Review, 0 missing
  source/configuration, 6 Candidates. No percentage or full rebuild certification.
- [x] Finish the audit's nine review rows: eight now have written lifecycle
  boundaries; GardenKeeper requires its missing application/migration source.
- [x] Repair GardenKeeper dump failure handling and prove isolated import/API
  recovery from the recovered source snapshot. Upstream Git provenance remains
  unknown; the snapshot hashes identify the tested recovery generation.
- [x] Reconcile Phase09/11/12 backup coverage, hardware deferrals and native
  command failure handling (2026-09-11); independent software acceptance remains
  distinct from full physical/rebuild proof.
- [x] Add Phase10 backup/heartbeat installation prerequisites, dated-run recovery
  guidance and fail-stopping VM/CT restore checks (2026-09-11 source review).
  Full rebuild and live backup/restore acceptance remain open.
- [x] Repair Phase07/08 blank-build versus recovery sequencing and document
  MediaMTX protected manual config capture (2026-09-11). Recurring/off-VM backup,
  retention, Hub source recovery and full rebuild acceptance remain open.
- [x] Expand ntfy, Watchtower, SearXNG and Whoogle lifecycle manuals against
  tracked source, with Mermaid links (2026-09-11). Backup/restore boundaries
  and notification failures remain explicit; no new live acceptance claimed.
- [x] Recover SearXNG effective settings, preserve a sanitized source template,
  and establish protected off-VM configuration backup. Semantic loading verified
  the sanitized snapshot on 2026-09-12; see the SearXNG service manual. No new
  live search acceptance is implied.
- [x] Add troubleshooting evidence-age checks, visibly separate example data,
  preserve recorded observations and show dated planned-offline context.
  Local model/browser verification passed (2026-09-10); collector sources now
  emit timezone-aware timestamps.
- [x] Deploy troubleshooting evidence-age/context UI to the existing
  management-only stack (2026-09-10). Live desktop/mobile checks pass, and
  the updated Windows collector produces a usable timestamp and 12/13 passes.
- [x] Install dedicated Proxmox dashboard collector through authorized SSH
  (September14); fresh mount/backup evidence and browser import pass September15.
  Preserve the original scheduled monitor and its different probe set.
- [x] Simplify all 11 canonical Mermaid diagrams, preserve dedicated detail
  views and explicit deferred states, verify desktop/mobile rendering, and
  publish the diagram bundle to the existing internal viewer (2026-09-10).
- [x] Reconcile overview and historical planning baselines with September
  recovery: deliberately disconnected cameras, 64GB Proxmox RAM, VLAN55/Hive,
  direct LAN4 OMV and PPPoE WAN. See the 2026-09-07 health audit in the current
  handoff; the household/workshop roadmap already reflects deferred hardware.
- [x] Review the uncommitted September work in bounded change
  groups; reconcile the five missing commits on
  `origin/claude/todo-list-review-6c88a1` against current evidence before
  integrating branches. Missing Fail2ban sources/runbook and verified Proxmox/
  CT114 MAC reservations were recovered; newer proxy and September source
  were retained. Preserve this reviewed work as separate feature-branch commits.
- [x] Refresh the read-only update/backup evidence available through current
  access; see the 2026-09-07 update review. VM103 app-data backup succeeded;
  The September7 access gap was historical: Proxmox SSH and fresh guest-backup
  evidence now pass; OMV SMART proof remains separate.
- [x] Obtain fresh Proxmox guest-backup evidence through owner-authorized SSH.
- [x] Obtain OMV SMART evidence through restored `omv-lan` key access on
  October 2: five disks passed, 30–47 C, no reported pending/uncorrectable sectors;
  md0 `[UU]` with an existing consistency check running. This is not restore or
  disk self-test proof; stable disk identity is needed before CRC comparisons.
- [x] Repair Watchtower-to-ntfy notification delivery: September15–17 server
  acceptance and corrected scheduled counts supersede September6/7 error40014.
  Retain the no-attachments policy; owner phone receipt remains separately open.
- [x] Restore HomeGuest 2.4 GHz broadcast after its UCI section type was
  invalid; `phy0-ap4` and SSID activation validated after a wireless reload
  (2026-09-05). See the current handoff.
- [x] Install dedicated workstation router SSH key and verify root access via
  `home-router-lan`, preserving the existing laptop key (2026-09-04).
- [x] Post-fibre VM103 recovery: restore 6144 MiB RAM, graceful restart,
  recover Homepage/AdGuard/Immich/Dozzle and verify NFS/container health.
- [x] Retire disconnected Zyxel Wi-Fi uplink; all five 2.4 GHz APs restored.
- [x] Repair WAN6 device mapping and required IPv6 control-traffic firewall.
- [x] Activate Zen IPv6 and verify it live (2026-09-11): DHCPv6-PD leases the
  supplied `/48`; the supplied ND `/64` and Zen link-local gateway provide the
  WAN address/default route. IPv4 and IPv6 internet pings pass after reload.
- [x] Reconcile rebuild WAN with untagged PPPoE on eth1; fail deployment when
  local PPPoE secrets are missing. Lint, previews and four regression tests pass.
- [x] OMV verified directly on LAN4; LAN2 moved to isolated cloud IoT VLAN55,
  Hive reserved at 192.168.55.10 with DHCP/NTP and internet traffic verified.
- [x] Set up P1S on HomePrinters: commissioned VLAN35/Bambuddy MQTT, HA
  dashboard and notification baseline are recorded in current-live-state.
  Camera and physical safety-interlock acceptance remain separate.
   - [x] Remove the now-redundant workstation hosts entry for
     `homeassistant.home.local` and flush the Windows DNS cache (completed
     2026-07-29)

### Household, workshop and operations product roadmap

  - [x] Build and verify the local, import-only [[apps/home-operations-workbench/README|Home Operations Workbench]] proof of concept for Today, diagnostics, recovery, meal availability and VentSys commissioning. It has no live integration or deployment path yet.
  - [x] Add offline Windows/Proxmox health-snapshot adapters with explicit
    timestamp/freshness handling, unknown missing checks and separate
    backup/integrity/restore evidence; unit and desktop/mobile browser tests
    pass on 2026-09-07. No service credentials or live collection added.
  - [x] Record the September recovery tabletop review in
    [[docs/audits/2026-07-full-system-audit/08-resilience-test-cards]] for major
    host, network, storage, application, monitoring and credential-loss scenarios.
    This is paper review; live drills and owner-selected RPO/RTO remain gated.
  - [x] September14–15: collect and validate the Proxmox snapshot and accept
    its real mount/backup evidence through the dashboard browser import. Fresh
    future snapshots and application-consistent restores remain separate.

### Tier 1 - near-term core

- [x] Validate Tailscale from an off-LAN client after docker-host auth and route approval
- [x] Deploy AdGuard Home under `/opt/stacks/adguard-home/`
- [x] Deploy Immich under `/opt/stacks/immich/` with OMV-backed upload/library storage at `/mnt/omv/immich`
- [x] Deploy Homepage under `/opt/stacks/homepage/`
- [x] Upgrade Homepage into the `Home Operations` portal with Home, Tools,
  Infrastructure, Monitoring, Storage, Media and Operations tabs; all
  user-facing services, live Docker workload status, reference links, quick
  search, header resource status, responsive layout, local visual assets and
  explicit host validation are deployed and desktop/mobile verified on
  2026-07-24
- [x] Add visible portal-card preview controls and an inline embedded workspace
  below the active tab's portal cards, with a contained split/work area and an
  `Open tab` fallback; deployed and refined 2026-07-25
- [x] Repair Homepage preview toolbar delegation, use a real external link,
  stop the MutationObserver from continuously detaching/re-appending the iframe,
  make narrow cards grow into a dedicated Preview action row, and strengthen
  tab navigation states; Household Hub and Mermaid Viewer visibly rendered and
  Reload/Close live-verified 2026-07-26
- [x] Close the embedded workspace before Homepage tab changes and place it as
  a sibling after the complete active card grid; live-verified on Home, Tools
  and Infrastructure 2026-07-26
- [x] Double the responsive embedded-workspace height on desktop and mobile so
  framed applications have a larger scrollable work area; deployed and
  live-verified 2026-07-26
- [x] Deploy trusted local-CA HTTPS for Homepage on `443`, retain HTTP `3001` as
  rollback, convert fixed preview listeners to HTTPS, add mixed-content-safe
  wrappers for every configured HTTP portal, and add Home Assistant on `8188`;
  HA login screen, GardenKeeper, Mermaid Viewer, Reload and Close were
  live-verified on 2026-07-26. The first HA login on the distinct `8188` origin
  remains a normal one-time user authentication step.
- [x] Repair Homepage narrow/intermediate viewport layout using explicit `320`, `350`,
  `375`, `390`, `430`, `480` and tablet-width visual checks: make the title, search,
  resource and date/time cards reflow into a clean header without overlap or
  edge contact; add consistent gaps between stacked navigation buttons; keep
  text and controls inside every header, navigation and service card with equal
  left/right padding; preserve readable service-card spacing; and remove the
  light teal/blue background band or glow that expands downward as the viewport
  narrows while retaining the intended dark network artwork. Recheck desktop
  widths after the mobile correction. Deployed and visually verified at all
  listed widths plus `768`, `900`, and `1280` px on 2026-07-29; the 390 px
  embedded-workspace controls were also exercised successfully. Follow-up at
  the reported `956` px and `489` px widths confirmed no title/search overlap
  and measured `10.4` px vertical gaps between stacked service cards.
- [x] Confirm `https://homepage.home.local/` from mobile data after reconnecting
  the OnePlus to Tailscale; split DNS, the enabled AdGuard rewrite, tailnet
  HTTPS/DNS grants, explicit listeners, and host firewall rules were deployed
  and user-validated on 2026-07-29
- [x] Add a fixed-target, UFW-scoped Homepage preview proxy and restore framed
  GardenKeeper, Bambuddy and Whoogle views; upgraded to HTTPS and expanded to
  all configured preview targets on 2026-07-26
- [x] Deploy narrow OpenWrt rules for docker-host preview/status access to
  Proxmox `8006`, router/switch HTTP, Frigate API `5000`, monitoring
  `3000/3001`, and OMV/Transfer `80/8088`; Proxmox/OpenWrt/Zyxel/Frigate/OMV/
  Transfer paths and proxy ports `8183`/`8184`/`8185`/`8187` verified live on
  2026-07-26
- [x] Permit docker-host `192.168.20.102` to reach Grafana `3000/tcp` and Uptime
  Kuma `3001/tcp` in the monitoring VM host firewall, then verify proxy `8186`
  and both Homepage status dots. On 2026-07-26 the source-scoped UFW and
  `DOCKER-USER` rules were verified from docker-host (`200` Grafana, `302` Kuma;
  HTTPS proxy `8202=200`, `8186=302`) and made reboot-persistent with
  `monitoring-firewall.service`.
- [x] Replace Mermaid Viewer placeholders with all 11 canonical sources and add
  search, deep links, pan, zoom, fit, 100% view and fullscreen; deployed and
  render-verified 2026-07-24
- [x] Apply subject-specific, code-native backgrounds to the custom portal,
  Mermaid Viewer, GardenKeeper and Household Hub; portal motion respects
  reduced-motion preferences, deployed 2026-07-24
- [x] Deploy Vaultwarden behind its dedicated local-CA HTTPS hostname with a
  loopback-only raw listener, disabled sign-ups/admin endpoint, source-scoped
  access and two isolated SQLite restore proofs (including a disposable account);
  completed 2026-07-29. Do not embed it or expose its raw HTTP port.
- [x] Audit every portal for both direct navigation and embedded-preview
  behaviour. Record service health, HTTPS/mixed-content, authentication and
  `X-Frame-Options`/CSP framing results; fix reachability or use the normal
  link rather than weakening a service's frame protections. Mermaid Viewer and
  Household Hub are confirmed directly embeddable after repairing the portal's
  iframe re-parent loop. GardenKeeper, Bambuddy, Whoogle, Proxmox, OpenWrt,
  Zyxel and OMV are confirmed via the fixed-target proxy. Continue with the
  monitoring VM host-firewall exception, then test the remaining portals. The
  audit was completed on 2026-07-26; direct navigation remains the fallback when
  a service's own framing policy prevents embedding.
- [x] Repair qBittorrent's embedded preview and direct HTTPS entry after its
  legacy WebUI failed inside a port-based iframe. It now uses Homepage's
  same-origin `/portal-preview/qbittorrent/` route plus a minimal parent-window
  compatibility bridge; the authenticated Transfers view rendered with no new
  console errors on 2026-08-01.
- [x] Create and prove the dedicated OMV media export, then deploy source-scoped
  Jellyfin (read-only libraries), Calibre-Web and Atsumeru foundations with
  explicit non-overlapping Docker IPAM, restart proofs and NAS-backed app-data
  backup; completed 2026-07-29.
- [x] Complete the prepared Mullvad/Gluetun/qBittorrent gateway: securely install
  the generated WireGuard private key/address, start the stack, set separate
  incomplete/complete paths, rotate the qBittorrent Web UI credential, prove
  tunnel egress and the fail-closed kill switch, then prove NAS config backup and
  restore. Quarantine promotion remains a manual host-side step; qBittorrent has
  no final-library mount. Completed 2026-08-01; optional allow-listed Autobrr
  dispatch follows only after this proof. NZBGet and aria2 remain separate
  decisions.
- [x] Repair the AdGuard/Tailscale reboot race with an enabled systemd Compose
  gate that waits for the Tailscale address and force-recreates the stack; local
  and Tailscale DNS port bindings were revalidated on 2026-07-29.
- [x] Deploy Dozzle under `/opt/stacks/dozzle/`
- [x] Add docker-host `DOCKER-USER` guard so Dozzle is management-only despite Docker published-port forwarding
- [x] Add Uptime Kuma checks for Homepage and Dozzle
- [x] Add Uptime Kuma checks for AdGuard DNS and UI
- [x] Add Uptime Kuma check for Immich UI
- [x] Add docker-host `DOCKER-USER` guard for Immich UI on `2283`
- [x] Expand docker-host VM disk to 32 GiB
- [x] Add repo-side rebuild templates for live docker-host stacks and host firewall

### Tier 2 - roadmap candidates

- [x] Deploy Mealie under `/opt/stacks/mealie/` (live 2026-06-21)
- [x] Deploy Grocy for pantry/fridge/freezer stock and expiry tracking
- [x] Seed Grocy household data model with core locations, quantity units, and product groups; service health reconfirmed on 2026-07-07 (`HTTP/1.1 302 Found` login redirect), database checkpoint created, and OMV app-data backup run `20260707T125454Z` captured the change
- [x] Add Grocy voice shopping-list support to Home Assistant Assist with add/list-only LLM tools, dedicated Grocy API key, HA/dockerd firewall allowances, direct HA-to-Grocy API proof, and OMV app-data backup run `20260707T132647Z`
- [x] Add Household Hub's separate-key, read-only Grocy overview for locations, stock/expiry and the active shopping list; live API/UI verified 2026-08-09 with all five seeded locations and no mutation routes
- [x] Activate Household Hub's persistent, confirmation-gated Obsidian Markdown staging outbox without writing into LiveSync CouchDB; valid export smoke completed, disposable note removed, and an unconfirmed live write rejected without a file on 2026-08-09
- [x] Add the Household Hub Markdown outbox to the docker-host NAS app-data job; dry-run and real backup `20260809T130054Z` passed
- [x] Add downloadable `.ics` fallback for Household Hub Nextcloud CalDAV dry-runs; live upload remains gated on an actual Nextcloud deployment and app credential
- [x] Install and prove docker-host app-data backup to OMV `backups/docker-host` covers Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dumps; completed on 2026-07-07 after deploying the live OpenWrt `Docker Host to OMV NFS` rule, mounting `/mnt/omv/docker-host-backups`, running backup `20260706T231304Z`, restore-smoking to `/tmp`, and enabling the daily `03:45` systemd timer
- [x] Deploy ntfy internal-only under `/opt/stacks/ntfy/`
- [x] Configure Uptime Kuma ntfy notifications through a dedicated write-only topic
- [x] Deploy SearXNG direct-access pre-flight under `/opt/stacks/searxng/`
- [x] Deploy Whoogle direct-access pre-flight under `/opt/stacks/whoogle/`

### Tier 3 - evaluate carefully

- [x] Evaluate and deploy Vaultwarden only after a backup/security review.
  Vaultwarden is live behind dedicated local-CA HTTPS with raw HTTP bound to
  loopback only; two isolated SQLite restore proofs passed on 2026-07-29.
  Owner onboarding remains separately gated on live `vault.home.local` DNS.
- [x] Deploy Watchtower in monitor-only mode only

### Core HA tools

- [x] Install Home Assistant Companion App on operator phones using `docs/procedures/home_assistant_companion_app_guide.md`
- [x] Test push notifications and actionable notification acknowledgements
- [x] Trust the local Home Assistant CA on the operator Android phone and confirm the app connects to `https://192.168.20.101:8123`
- [x] Keep Mosquitto as the required MQTT broker add-on
- [x] Keep ESPHome as the required VentSys firmware/adoption add-on
- [x] Keep Terminal & SSH available for HA-side diagnostics

### High-value candidates

- [x] Install HACS only after a current HA backup exists
- [x] Evaluate Advanced Camera Card / former Frigate Card with the first live
  Frigate camera; manual HACS-layout asset install is live under
  `/config/www/community/advanced-camera-card`. The CCTV dashboard now uses it
  as the primary first-camera card, with the HA image provider plus Frigate
  status/toggle entities exposed beside it.

## Immediate next actions (unblocked right now)

- [x] Create `/opt/stacks/bambuddy/.env` on docker-host from `.env.example`
- [x] Add the real MQTT password
- [x] Start Bambuddy with `docker compose up -d` from `/opt/stacks/bambuddy`
- [x] Confirm Bambuddy UI at `http://192.168.20.102:8000`
- [x] Commission P1S MQTT telemetry in Bambuddy and verify the authenticated TLS relay
- [x] Deploy the instantiated P1S Home Assistant package, dashboard and phone-notification automations
- [x] Confirm the live Bambuddy MQTT topics and P1S serial mapping in Home Assistant
- [x] Remove deprecated InfluxDB connection/auth keys from HA YAML after confirming the UI-managed Influx connection
- [x] Design `apt-cacher-ng` on docker-host for package caching
- [x] Deploy `apt-cacher-ng` on docker-host and test with frigate-nvr
- [x] Move Bambuddy MQTT relay from 1883 to TLS 8883 and verify retained `bambuddy/status`

### Configuration (all complete)

- [x] 10-segment architecture designed ✅
- [x] `vlan-config.conf` — bridge, VLANs, interfaces, WireGuard ✅
- [x] `firewall-config.conf` — zones, inter-VLAN rules, VentSys ports ✅
- [x] `dhcp-config.conf` — scopes, reservations, DNS ✅
- [x] `wireless-config.conf` — 5 SSIDs, channel plan, WPA3/WPA2 ✅
- [x] Router setup phases 1–8 documented ✅
- [x] Network testing guide written ✅
- [x] WireGuard fallback guide written ✅
- [x] MQTT 1883→8883 deployment note added to firewall config ✅
- [x] VLAN 1 port assignment bug fixed in Phase 2 script ✅
- [x] Country code corrected GB in Phase 5 script ✅
- [x] PVID notation (u vs u*) fixed in Phase 2 script ✅

### Deployment

- [x] Flash/configure GL-MT6000 with router phases 1–8
- [x] Run router validation/tests from management IP (`test.ps1`: PASS=62/WARN=0/FAIL=0; `test-connectivity.ps1`: PASS=74/WARN=0/FAIL=0)
- [x] Confirm no live valve-1 temporary plain-MQTT firewall exception exists; keep source as TLS `8883`-only for VentSys MQTT
- [x] Remove stale valve-1 firewall-source drift items after parity verification

### Proxmox

- [x] Install Proxmox VE on MINISFORUM M1 Pro-125H
- [x] Configure vmbr0 VLAN-aware bridge, trunk on enp1s0
- [x] Set static IP 192.168.10.10 on vmbr0.10
- [x] Retire PCI iGPU passthrough/IOMMU requirement in favour of shared LXC device mapping
- [x] Retire the pre-LXC `vm-setup.sh`; `guest-configs.md` holds the current inventory
- [x] Move VMs 100/102/103 and CTs 111/114 to `omv-backups` with `keep-daily=7,keep-monthly=6`; 2026-07-05 check shows VM backups current, `omv-backups` at 54.21% used, and the LXC backup job fixed with `tmpdir=/var/tmp` after NFS temp-dir permission failures; manual CT 111 and CT 114 proofs passed on 2026-07-05/06
- [x] Replace VM 104 with CT 114 `llm-host` at 192.168.20.104; retain stopped VM as rollback
- [x] Keep `llm-host` and `openwebui` DNS aliases on 192.168.20.104
- [x] After the 64GB RAM upgrade, resize CT 114 and move `home-assistant-llm` to Qwen3-14B-128K Q4_K_M with a 64k context; API smoke test passed on 2026-07-07
- [x] Build the Metrocop Voice Mixer (`apps/voice-mixer`: voicefx library, Gradio UI, presets, CLI, 37 tests) and verify it on the desktop with dataset, Piper and Piper→RVC sources (2026-10-10)
- [x] Relieve CT 111 Frigate memory exhaustion (host-wide I/O thrash 2026-10-08 → 10): temporary 12 GiB + Frigate restart; CT back at 6 GiB with ~1 GB used, host load ~1–2
- [x] Decision 09 approved; CT 114 headroom checked (16.5/28 GiB), image built and verified offline (`--network none`: Piper 3.2 s, CPU RVC 29.6 s), stack assets + compose staged in `/opt/stacks/voice-mixer`, `7860` `DOCKER-USER` block live (2026-10-10)
- [x] Voice Mixer live on CT 114 `:7860` (LAN + CPU RVC verified) with Homepage portal entry `https://homepage.home.local:8210/` (preview-proxy, `services.yaml`, docker-host UFW `8210`) (2026-10-11)
- [x] Tailscale route `192.168.20.104/32` advertised by docker-host and approved (verified in `PrimaryRoutes` 2026-10-11)
- [x] When `codex/portal-refinement` merges `main`: it rewrote the Homepage template, the network/Proxmox diagrams and the Mermaid Viewer generator, so resolve conflicts by keeping its structure and carrying over the 2026-10-11 facts: Voice Mixer node + Homepage portal `8210`; Tailscale host routes now five incl. `192.168.20.104/32` and Frigate `192.168.30.20/32` approved; Wyoming Piper `10200` / Whisper `10300` (were swapped); CT 114 `6c / 28 GiB`; Homepage `services.yaml`/`nginx.conf` taken from live. (merged on `integrate/main-into-portal`, 2026-11-13)
- [x] Resync the stale repo Homepage template (`configs/docker-host/stacks/homepage/`) with the live portal on VM 103: compose, config, custom CSS/JS, preview-proxy; secrets/TLS excluded (2026-10-10)
- [x] Metrocop Wyoming TTS (`voice_mixer/wyoming_tts.py`, container `metrocop-tts` in `/opt/stacks/voice-mixer`, port `10201`, HA + monitoring only via UFW/DOCKER-USER): Piper `en_GB-metrocop2-medium` → `data/tts/metrocop.json` preset (no RVC), random end blip per announcement, ~1 s render (2026-11-05)
- [x] Metrocop Piper voice v2 trained (northern-English source, `-pi -1`, 2,459 clips, 400 epochs; best `epoch=387 val_mel=0.3386`) → `voice/tools/out/en_GB-metrocop2-medium.onnx`; approved by listening (2026-11-05)
- [x] Voice Mixer: `bleeps.gap_static` fills bleep gaps with radio static (no digital-silence dropout); metrocop preset `gap_pre_ms` 200 → 80 (2026-11-05)
- [x] `en_GB-metrocop2-medium` installed in CT 114 Wyoming Piper (`/opt/stacks/local-ai/piper`, plain voice without radio FX) (2026-11-05)
- [x] Voice PE `home-assistant-voice-0ae52a` on IoT VLAN 50 (`HomeIoT`) at `192.168.50.108`; mDNS discovery does not cross VLANs, so added to HA's ESPHome integration by IP (like the VentSys boards); assistant select set to `Overwatch` (2026-11-11).
- [x] Voice PE replies play: HA `internal_url` -> `ha-media-proxy` (docker-host 8124), router DNS `ha-media.home.arpa`, IoT->proxy rule, DHCP reservation `.108` (2026-11-11); re-fixed 2026-11-13: the UI-only value had been overridden by the YAML `internal_url` on restart, now set in `configuration.yaml`
- [x] Overwatch speed 3a/3b deployed 2026-11-12: Overwatch pipeline prefers local intents; direct web-search route in `llamacpp_conversation` (web search 26.5 s -> ~10 s, time 7.4 s -> 0.5 s)
- [x] Model-free device-state route deployed 2026-11-12 (`llamacpp_conversation`): "is X on/open?" and "what is the X temperature?" answered in code (~21 s -> 0.0 s); unknown devices get "I have no device called X"
- [x] Phase 1 of `docs/decisions/10-overwatch-voice-routing-architecture.md` deployed 2026-11-12/13: every tool on every turn, stable cached prefix, new prompt, warm-up with failure canary (78% -> 91% on the shared checks; first deploy rolled back, see handoff)
- [x] `gardenkeeper_llm` and `household_hub_llm` custom components copied from live HA into `configs/home-assistant/custom_components/` (2026-11-12)
- [x] Voice PE wake word: custom microWakeWord "Overwatch" built into the Voice PE firmware (stock 26.9.0 package + model, `configs/esphome/home-assistant-voice-0ae52a.yaml`) and flashed over the air 2026-11-13; enabled in "Wake word 2" with Okay Nabu kept in slot 1

### Home Assistant VM (VM 100)

- [x] Start VM 100, complete HAOS onboarding wizard
- [x] Set static IP 192.168.20.101 via nmcli
- [x] Install add-ons: Mosquitto, File Editor, Terminal, ESPHome
- [x] Configure MQTT integration on TLS (`localhost:8883`); keep plaintext `1883` only for explicit bootstrap exceptions
- [x] Copy `ventsys_ha_package.yaml` and `ventsys_ha_scripts.yaml` to `/config/packages/`
- [x] Do not copy `ventsys_ha_optional.yaml` yet (load only after its prerequisites are met)
- [x] Copy `dashboards/ventsys-dashboard.html` to `/config/www/ventsys-dashboard.html`
- [x] Generate Long-Lived Token → paste into `HA_CONFIG.token` in live dashboard copy
- [x] Confirm dashboard shows ◉ HA LIVE
- [x] Enable HA 2FA (TOTP)
- [x] Copy `dashboards/ventsys-card-wrapper.html` to `/config/www/ventsys-card-wrapper.html`
- [x] Add a Lovelace iframe/panel view that uses the VentSys card wrapper
- [x] Configure NAS as HA backup mount and verify manual backup write to OMV
- [x] Set HA automatic backup schedule: daily 03:00, keep 14, location `nas_backups`
- [x] Validate router-local NTP for non-HA-managed restricted devices
- [x] Stage HACS custom integration `2.0.5` manually at `/config/custom_components/hacs`
- [x] Restart Home Assistant after staging HACS and verify the HACS setup flow opens
- [x] Complete HACS setup in HA and finish GitHub device authentication

### Frigate (CT 111; VM 101 retained only for rollback)

- [x] Create VM 101 from Debian 13 cloud image (hostname: frigate-nvr, SSH only)
- [x] Set static cloud-init IP 192.168.30.20
- [x] Note MAC and add to dhcp-config.conf (`BC:24:11:9C:25:87`)
- [x] Install Docker (official repo)
- [x] Deploy `configs/frigate/config.yml` to `/opt/frigate/config/`
- [x] Stage `/opt/frigate/.env` from template with `FRIGATE_MQTT_PASSWORD` set and secure permissions (`600`)
- [x] Set current bench-camera `FRIGATE_RTSP_PASSWORD` in `/opt/frigate/.env`; replace later if camera credentials are rotated
- [x] Stage MQTT CA trust for Frigate at `/opt/frigate/certs/ca-cert.pem` and verify TLS (`Verify return code: 0`)
- [x] Create host dirs: `mkdir -p /opt/frigate/db`
- [x] Start Frigate 0.17.1 on CT 111; first-camera live baseline now supersedes the original no-camera migration-safe baseline
- [x] Update source-controlled `configs/frigate/config.yml` from the accepted
  first-camera live config without embedding RTSP or MQTT secrets
- [x] Configure HTTPS/SSL for Frigate UI before regular use
- [x] Confirm Frigate UI over HTTPS/SSL: `https://192.168.30.20:8971/api/version` requires auth and plain HTTP to port `8971` is rejected
- [x] Configure initial go2rtc/WebRTC/audio behavior for the first camera:
  named main/sub restreams are live, Advanced Camera Card uses the Frigate
  go2rtc provider, and the browser negotiates WebRTC with video plus PCMU audio
- [x] Replace Lumen-first Apple viewing plan with HA Companion App + Frigate PWA first, with Lumen/Viewu/Kapal as optional later evaluations only
- [x] Stage Frigate HA custom integration `v5.15.4` manually at `/config/custom_components/frigate`
- [x] Restart Home Assistant after staging Frigate and verify the Frigate setup flow opens
- [x] Complete Frigate setup in HA at API URL `http://192.168.30.20:5000`
- [x] Enable Frigate MQTT over TLS to HA Mosquitto so Frigate HA entities are live
- [x] Add first-camera IR-cut mode controls in HA using ANNKE/Hikvision ISAPI
  digest auth, with `day`, `night`, `auto`, and `schedule` options exposed on
  the CCTV dashboard
- [x] Add first-camera supplemental light and guarded two-way audio settings to
  the CCTV dashboard. Supplemental light exposes mode plus white/IR brightness;
  two-way audio exposes enable plus speaker/microphone volume, but actual
  browser talkback still requires HTTPS/secure-context testing.
- [x] Manage VM 103 as `docker-host` via `scripts/setup/proxmox/docker_host_setup_guide.md`
- [x] Deploy Bambuddy as `/opt/stacks/bambuddy` on docker-host
- [x] Confirm Bambuddy UI at http://192.168.20.102:8000
- [x] Add Frigate integration in HA
- [x] Remove stale ONVIF integration entry for the first camera from HA; use
  the Frigate entity path for the CCTV dashboard
- [x] Read-only inspect current Frigate review/event/motion history for
  `cam_01_annke_c500` before tuning. On 2026-07-07, Codex confirmed the
  `proxmox` SSH profile reaches CT 111 and Frigate API `0.17.1`; object
  detection is currently disabled, the event table has no object events,
  review history contains only three historical alert segments, and all current
  recording segments are motion-marked with zero object segments. CT-local
  Frigate storage was near full; the OMV recording cutover is now complete, so
  broader tuning can proceed with detection/zone re-enable tests.
- [x] Deploy the instantiated `bambuddy_p1s_package.yaml` to `/config/packages/` on HA
- [x] Replace the P1S serial placeholder in the live package
- [x] Confirm P1S telemetry, print-state entities and Bambuddy connectivity in HA
- [x] Map shared Intel render/card devices into unprivileged CT 111 and CT 114; PCI passthrough/IOMMU is not required

### Wiring

- [x] Calibrate the E2 branch board's linked normal-servo endpoints: 940 µs closed
  (operator-accepted small springback after PWM release) and 2000 µs fully
  open, with one-second endpoint detach and no double-close compensation. Its HA
  position is the last command, not measured feedback. Earlier feedback-servo
  tests are superseded by the three-wire servo; details are in
  `docs/reference/current-live-state.md`.

### ESPHome flashing and adoption

  - [x] Correct Main Duct Valve 2's device identity by flashing
    `ventsys_main_valve2.yaml`; completed over COM4 on 2026-09-25. Serial and HA
    verification confirmed `.52`, GPIO35 feedback, Valve 2 entities and
    `ventsys/main/valve2/*`; stale native Valve 1 registry IDs were removed.
  - [x] Fully erase and reinstall Main Duct Valve 2 after an apparent dropout;
    completed over COM4 on 2026-09-25. The fresh factory image passed write
    verification, Wi-Fi/MQTT/API reconnection, and one complete temperature-alert
    sequence without a reboot or connectivity loss. No movement was commanded.
  - [x] Reflash the MAC-bound Valve 2 board on COM4 on 2026-10-04 with the
    three-wire servo image; verify HA online at `.52`, Valve Position 100,
    feedback entities removed, and retained ESPHome/VentSys MQTT state at 100.
  - [x] Reassign MAC `ec:e3:34:b4:79:7c` from the provisional Main Valve 2
    identity to E2/SLA branch on 2026-10-06. Flash
    `ventsys_sla_branch_valve.yaml` at `.52`, move MQTT control/state to
    `ventsys/sla/branch/*`, and verify the same HA device is online.
  - [x] Assign the separate board MAC `ec:e3:34:67:a0:18` to MAIN-2 on
    2026-10-06. Flash `ventsys_main_valve2.yaml` over COM4 at `.57`, verify
    native HA and MQTT control/diagnostic entities, and correct the board's
    previous Valve 1 HA registry identity. No movement commanded.
  - [x] Flash and adopt E1/FDM branch board MAC `EC:E3:34:67:0D:28` at `.53`
    on 2026-10-11, using the normal three-wire servo image without feedback.
    HA identifies it as VentSys E1 Branch Valve in Garage; no servo command
    was sent during adoption.
  - [x] Correct E1's logical Open/Closed defaults from 50/50 to 100/0;
    compile and reflash over COM4 on 2026-10-12. HA confirmed targets 100/0,
    position 50, and PWM inactive. No motion command was sent.
  - [x] Flash and adopt MAIN-1 board MAC `EC:E3:34:67:8C:9C` at `.51` on
    2026-10-12 with the normal three-wire servo profile and no feedback ADC.
    HA shows 26 native entities, Open/Closed 100/0, position 50 and PWM off.
    No movement command was sent.
  - [x] Flash the compiled E2 MQTT number-parser correction over COM4 on
    2026-10-06; HA confirmed the new build online at `.52`, restored position
    0, and PWM inactive after reboot.
- [x] Create remaining controller YAMLs -- all exist in `configs/esphome/`:
  ventsys_main_valve1/2, fdm/sla_branch_valve, fdm/sla_print_valve, fdm/sla_360_valve (8 valves), ventsys_booth_fan.yaml (spray fan)
- [x] Keep `ventsys_main_valve1.yaml` on MQTT `8883` with
  `certificate_authority: !secret mqtt_ca_cert`; the historical plaintext-1883
  migration task is obsolete
- [x] Remove valve-1 temporary plain-MQTT firewall follow-up task because no live/source `1883` exception is present
- [x] OTA flash the SLA-profile 360 intake raw-LEDC correction on 2026-10-10; owner later identified that board as the SLA unit.
- [x] Integrate position persistence into all production valve variants and restart/shutdown into production firmware and controller bundles; configuration and source gates pass.
- [x] OTA update all six reachable boards (.61/.62/.52/.57/.41/.32); verify native identity/build and board controls. Restore installed SLA sensor's archived C6 wiring and BME680 0x77; valid readings and fault=false confirmed.
- [x] Add shared native Power Off Board and Restart Board buttons to production VentSys ESPHome firmware sources, including shared sensor firmware. Power Off enters deep sleep; waking requires physical reset/power cycling. See [[docs/procedures/ventsys-board-power-controls]].
- [x] Compile and flash the 360 intake C6 at `.61` over COM8 on 2026-10-10. esptool confirmed MAC `CC:BA:97:F0:E3:EC` and verified written data; HA showed fresh Wi-Fi telemetry. The owner later corrected this board's identity to SLA. No valve movement was commanded. At 09:52:11, HA logged the new Restart Board entity changing from `Unavailable` to `Unknown` and displayed “Pressed”; activity details record no cause, so this is not evidence of button activation.
- [x] Sync the ESPHome Builder FDM/SLA 360 v2 configs with canonical sources after correcting the role/IP/MAC mapping.
- [x] Harden dashboard page-init to use command-free renderers; static/mock contract tests prove initialization cannot enter an MQTT publish path

## Phase 4 — Storage ⏳

- [x] Migrate live OMV hardware/storage to VLAN 40 at `192.168.40.50`; capacity warning cleared by the 2026-07-05 `omv-backups` check at 54.21% used, and the managed-switch recable/trunk path is live
- [x] Follow `omv_nas_setup_guide.md` storage/user/share/export setup while preserving existing SMB shares
- [x] Configure NFS exports (Frigate, HA, Immich, configs shares)
- [x] Warm Frigate OMV export for future unprivileged CT cutover: allow Proxmox host `192.168.10.10` to mount `/export/frigate` and verify temporary write/read/delete/unmount
- [x] Keep Frigate "live" recordings on MINISFORUM local storage first during first-camera proving; superseded by the 2026-07-07 OMV recording cutover
- [x] Mount OMV Frigate export on Proxmox, bind-mount it into CT 111 at `/mnt/nas/frigate`, update docker-compose.yml volume, add the required UID `100000` ACL for the unprivileged CT root mapping, recreate Frigate, and verify fresh recordings write to OMV
- [x] Add OMV as HA network storage → verify backup writes successfully
- [x] Add a guarded, dry-run-by-default robocopy helper for the vault at
  `scripts/backup/backup_vault_to_nas.ps1`; source/destination and boundary
  checks passed against the live `NAS\configs` path on 2026-07-29
- [x] Verify SMART monitoring on NAS drives: global polling is enabled every
  1,800 seconds with 5 C change/55 C maximum alerts; all five physical disks
  are individually monitored and reported `Good` at 33-44 C on 2026-07-29. No
  new SMART self-test schedule was added.

## Phase 5 — NVR / Cameras ⏳

- [x] October 10: diagnose and recover CT 111 memory/file-cache thrashing.
  Confirmed idle ZeroMQ configuration publisher retains capture-reconnect
  cleanup work; live event-drain experiment and isolated reproduction pass.
  CT temporarily received12GiB; after lifecycle repair it is reassessed to6GiB.
  Existing image is pinned, and disconnected cameras are
  disabled in source/live configuration. See `docs/install/phases/04-frigate.md`.
- [x] Deploy permanent local single-owner configuration publisher lifecycle
  repair. Functional tests,3600 isolated and12000 live reconnects passed;
  synthetic three720p/10fps OpenVINO/recording and two capture recoveries passed.
  Working set~1.2GiB supports6GiB with generous cache/workload margin.
- [x] Bench-test first camera on the Zyxel switch: ANNKE C500 (`I51HJ`, firmware `v5.8.10 build 250917`) now reserved at `192.168.30.21`, with verified RTSP `/Streaming/Channels/101` and `/Streaming/Channels/102`, router-local NTP, and cloud access disabled
- [x] Deploy router `lan3` as the managed-switch trunk after the GS1900 baseline was configured; keep future switch access-port changes gated and labelled
- [x] Mount the first three cameras and run CAT6 to PoE switch access ports on
  VLAN 30; retain ports 5-7 for the remaining/future camera rollout
- [x] Assign live camera addresses and switch ports: Camera 1 is
  `192.168.30.21`/port 2, Gate is `192.168.30.22`/port 4, and Patio is
  `192.168.30.23`/port 3; `192.168.30.24` remains planned for the next camera
- [x] Standardize Zyxel ports 2-7 as saved PoE VLAN 30 access ports and add
  debounced HA offline/recovery alerts for the three live cameras
- [x] Mirror the three live main/sub RTSP paths and go2rtc streams in
  `configs/frigate/config.yml`
- [x] Confirm all three installed camera streams are visible and sustaining
  approximately `10 fps` in Frigate; fourth camera remains future scope

## Phase 6 — Security hardening

- [x] Set up MQTT TLS (8883) — broker listener live, CA/broker certs installed, authenticated TLS pub/sub verified
- [x] Keep router source TLS-oriented for MQTT: no valve-specific `1883` exception exists, and remaining clients should migrate to `8883` without reintroducing plain-MQTT router rules
- [x] Enable Home Assistant native HTTPS with the local `Home Local CA` on
  2026-07-02; browser, Companion App, CCTV, Frigate integration, VentSys
  assets, monitoring links and the rollback path were validated.
- [x] Configure Fail2ban on docker-host (`sshd` jail baseline live at `/etc/fail2ban/jail.d/docker-host-sshd.local`)
- [x] Configure Fail2ban on Frigate VM (`sshd` jail baseline live at `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`)
- [x] Deploy monitoring VM on VLAN 60 (Uptime Kuma, InfluxDB, Grafana, Telegraf)
- [x] Create baseline Uptime Kuma monitors for core infrastructure
- [x] Forward OpenWrt syslog to Telegraf/InfluxDB
- [x] Export Home Assistant state history to InfluxDB
- [x] Configure Grafana InfluxDB datasource and baseline Home Automation dashboard
- [x] Configure Proxmox native metrics export to InfluxDB and add `Proxmox Resource Overview` Grafana dashboard
- [x] Deploy docker-host Telegraf host/container metrics to InfluxDB bucket `dockerhost`
- [x] Add Docker-host/container panels to `Proxmox Resource Overview`
- [x] Add the provisioned `Infrastructure Fleet` Grafana dashboard from the
  existing Proxmox and docker-host metrics (five running guests, CPU, disk,
  state and guest CPU history)
- [x] Expand the provisioned `Central Logs` dashboard with Bambuddy and
  docker-host error tables plus OpenWrt warning/error syslog
- [x] Collect Bambuddy Prometheus-format metrics locally through docker-host
  Telegraf and add the provisioned Grafana `Bambuddy Metrics` dashboard
- [x] Restore OMV desktop management key access (September30); read-only SMART/
  RAID evidence refreshed October 2.
- [x] Add `Service Availability`, `Network DNS`, and `Security Posture` Grafana dashboards
- [x] Export Uptime Kuma monitor state to InfluxDB bucket `uptimekuma`
- [x] Export docker-host Fail2ban counters to InfluxDB bucket `dockerhost`
- [x] Add HA Monitoring page/sidebar entry with direct links to Grafana and Kuma
- [x] Deploy internal ntfy notification service for future HA/Kuma/Grafana alerts
- [x] Repair stale Uptime Kuma checks on 2026-07-29: Home Assistant now checks
  native HTTPS with the private-CA error ignored, and the retired Ollama
  `11434/api/tags` check now targets llama.cpp `8081/v1/models`; both returned
  `200 OK` immediately after save
- [x] Set Uptime Kuma's primary base URL to
  `http://uptime-kuma.home.local:3001` and create the initial `core`, `network`,
  `storage`, `security`, `ai`, and `apps` tag taxonomy
- [x] Add host-scoped OpenWrt rules from monitoring VM `192.168.60.10` to
  Frigate API TCP `5000`, OMV web/NFS TCP `80`/`2049`, and ICMP for the three
  camera addresses. `fw4 check` passed before restart and live nft counters
  confirmed every new rule was exercised on 2026-07-29.
- [x] Add direct Kuma checks for OMV web, OMV NFS, and all three live camera
  hosts with the ntfy notification channel enabled; every check returned `Up`
  after the narrow OpenWrt rules were deployed.
- [x] Allow Frigate API TCP `5000` from `192.168.60.10` in CT 111's host
  firewall and revalidate Kuma monitor 28. The host rule was applied on
  2026-08-01; a monitoring-VM probe returned HTTP `200` and the re-enabled
  `Frigate API Health` monitor returned `200 - OK`.
- [x] Finish the OMV SMART push heartbeat: monitor 34, the OMV
  `smartctl -H` producer, host-only token file, 30-minute systemd timer, narrow
  OpenWrt rule, and VM 102 `DOCKER-USER` exception are live. The first accepted
  heartbeat on 2026-07-29 reported all five physical disks healthy.
- [x] Add a docker-host app-data backup-freshness push heartbeat: Kuma monitor
  36 expects a heartbeat within 25 hours, and the backup service sends it only
  through `ExecStartPost` after a successful run. Its first live `Up` heartbeat
  was accepted on 2026-08-01.
- [x] Create a read-only ntfy `mobile-monitoring` subscriber for `monitoring`
  and `watchtower`, store its generated password in Windows Credential Manager,
  and validate authenticated subscription from docker-host. A real Android
  notification over Tailscale remains the final phone-side acceptance check.
- [x] Add the authenticated Grafana `ntfy Monitoring` contact point, make it the
  default notification policy, and add initial 85%/10-minute metric alerts for
  docker-host root disk and Proxmox root storage. Both rules evaluated `Normal`
  and Grafana's test notification reached ntfy on 2026-07-29. SMART is routed
  through Kuma monitor 34 and backup freshness through Kuma monitor 36.
- [x] Deploy and restore-smoke the repo's SQLite-consistent ntfy addition to the
  docker-host app-data backup job. A fresh NAS run completed on 2026-07-29 and
  restored copies of both `user.db` and `cache.db` passed SQLite integrity checks.
- [x] Retain the HA HTTPS certificate and rollback artefacts for renewal and
  recovery; the native HTTPS cutover is live.
- [x] Keep monitoring operational posture as direct-link access from HA, with embedding intentionally parked for now
- [x] Add an external health signal for monitoring VM (HA-side check) so Kuma-down is still detected
- [x] Deploy AdGuard Home on docker-host as selected DNS filtering engine
- [x] Add/validate router DNS enforcement rules for filtering coverage and public fallback
- [x] Add monitoring for the DNS filtering service before making it the only resolver path
- [x] Verify historical pre-NAS Proxmox local backup job for VMs 100/101/102/103; current recurring guest backups now use OMV `omv-backups`
- [x] Run staged core health baseline and confirm required live services are green (`health_check.sh --json`: PASS=11/FAIL=0; hardware-dependent checks skipped/unknown until devices exist)

## Ongoing / maintenance

- [x] October18: deploy Pocketry1.5.1 with matching Homepage Tools card;
  hosting smoke checks and browser cutout3D passed. See `docs/install/services/pocketry.md`.
- [x] Enable Bambuddy-only scheduled offline updates via workstation/WSL staging
  and VM103 idle-gated timer; first1.2.5.5→1.2.5.6 update passed NAS checkpoint,
  isolated copied-data migration, image/network identity and P1S reconnection
  on2026-10-02. See `docs/procedures/bambuddy_offline_updates.md`.
- [x] Repair September 30 mobile Homepage standalone navigation: use the same
  scoped HTTPS routes as Preview, separate Bambuddy browser `8207` from native
  Serve `8181`, and add `homepage/tests/access-contract.cjs` as a release gate.
- [x] Owner confirmed September 30 general phone mobile-data acceptance.
- [x] Owner confirmed Grocy's follow-up Host/redirect fix works on the phone.
- [x] Expand the live troubleshooting dashboard to 37 routes from recurring
  conversation themes; add guidance search and shareable route links, correct
  commissioned P1S/FTPS990 context, regenerate offline routes and verify
  model plus desktop/mobile behavior (2026-09-30).
- [x] Verify CT 111/114 backup behavior after adding `tmpdir=/var/tmp` to the
  Proxmox LXC backup job; CT 111 manual proof passed on 2026-07-05 and CT 114
  manual proof passed on 2026-07-06
- [x] Rebuild/recreate Recomp Tracker with durable null-session recovery and
  reliability/UI/alarm improvements; deployed 2026-09-17 using the installed
  runtime and a source-only build (see stack HANDOFF.md).
- [x] October 3: synthetic GardenKeeper PostgreSQL dump/restore and separately
  copied journal media passed isolated API, notification and calendar restart
  acceptance. See `tools/gardenkeeper-recovery/README.md`. The full-system/live
  integration and real-user recovery gate above remains open.
- [x] Close confirmed VM102 network access gaps for MQTT8883, ntfyHTTPS8193, HomepageHTTPS443, Hub8100 and approved media/download services; move both VentSys monitoring functions to VM102 and remove dedicated VM103 installation/key/credentials/state.
- [x] Finish Kuma/Homepage integration. Eight checks37–44 are Up with ntfy
  and two retries; local CA trust, status page and Home widget are deployed.
  See monitoring roadmap November11 section.
- [x] November10: repair OMV SMART heartbeat by preserving its existing Kuma3001 allowance through monitoring Docker firewall rebuild; verify sender success and Kuma recovery.
