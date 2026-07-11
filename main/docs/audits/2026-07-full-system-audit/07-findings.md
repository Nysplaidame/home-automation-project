---
title: July 2026 Findings Register
created: 2026-07-10
modified: 2026-07-10
type: audit-findings
status: discovery-frozen
---

# Findings Register

Severity reflects current impact and credible failure/abuse paths, not effort.
No listed corrective action was performed during discovery.

## F-001 — Tracked active credential and private key

- **Severity:** Critical
- **Evidence:** `.obsidian/plugins/obsidian-local-rest-api/data.json` is tracked,
  contains a non-empty API credential and private-key material, and is present
  in four historical commits. Values are excluded.
- **Affected assets:** Obsidian REST endpoint, repository clones, Git history,
  any client trusting the embedded certificate/key.
- **Impact:** Anyone with repository read access may impersonate or access the
  service within its reachable boundary; history preserves exposure after a
  normal file deletion.
- **Root cause:** Runtime plugin state and cryptographic material were committed
  as project metadata without a secret exclusion/rotation workflow.
- **Corrective action:** Determine exposure scope, disable or bind-restrict if
  necessary, rotate the API credential and certificate/private key, remove the
  file from tracking, add an ignore/template policy, and decide whether a
  coordinated history rewrite is warranted.
- **Dependencies / rollback:** Requires Obsidian client reconfiguration and
  repository-collaborator coordination. Keep a tested replacement before
  revoking the old identity; history rewrite requires clone coordination.
- **Retest gate:** Current and full-history secret scans contain no live value;
  old credentials fail; authorized client works with the replacement; listener
  scope matches documented intent.

## F-002 — Immich is unavailable after an NFS mount failure

- **Severity:** High
- **Evidence:** `mnt-omv-immich.mount` has failed since 2026-07-06; Immich is
  restart-looping/unhealthy and reports missing media markers. The fallback
  directory is empty and NFS is currently reachable.
- **Affected assets:** Immich server, media access, Docker host, OMV Immich
  export, monitoring.
- **Impact:** Service outage; an unsafe recovery could write media to the VM
  root or create split-brain paths.
- **Root cause:** Boot-time NFS mount uses unbounded/default options and the
  application starts without a hard verified mount prerequisite.
- **Corrective action:** Prove media path integrity, adopt bounded explicit NFS
  options and systemd ordering, make container startup conditional on the
  mount, then mount and restart in an approved window.
- **Dependencies / rollback:** Requires current database/media backup proof and
  an Immich window. Roll back Compose/fstab and stop the app if marker or path
  validation fails.
- **Retest gate:** Correct mount is active across reboot simulation; marker
  exists; Immich is healthy; no local fallback writes; positive and negative
  storage-loss tests pass.

## F-003 — Router source/live VLAN 50 identity drift

- **Severity:** High
- **Evidence:** Source compiles `HomeIoT`; live UCI/firewall uses
  `iot_sensors`. New-name tests fail 9 checks while direct old-name service and
  deny/allow checks pass.
- **Affected assets:** OpenWrt, VLAN 50 DHCP/Wi-Fi/firewall, VentSys scripts,
  MQTT-only isolation, router deploy tooling.
- **Impact:** A routine source deployment may break VLAN 50 or partially
  replace firewall objects, causing loss of devices or unintended access.
- **Root cause:** Human-facing rename was committed before a live migration and
  dependent scripts were not migrated as one transaction.
- **Corrective action:** Choose a durable internal identifier, model the full
  UCI/firewall migration, update all consumers, preview a delta, back up live
  config, and execute only in an approved router window.
- **Dependencies / rollback:** Requires client inventory, router backup, local
  console/recovery access, and VentSys validation. Rollback restores the exact
  pre-change UCI package set.
- **Retest gate:** Preview is idempotent; live source parity passes; VLAN
  positive and deny tests pass; Wi-Fi clients rejoin; old identifier has no
  unexplained consumers.

## F-004 — Frigate CT storage is near exhaustion

- **Severity:** High
- **Evidence:** CT 111 root is 93% used with about 2.2 GiB free; its thin volume
  is 99.81% allocated. Approximately 20.4 GiB of old local recordings remain.
- **Affected assets:** CT 111, Frigate database/config, Proxmox thin storage,
  recording continuity.
- **Impact:** Write failure, database corruption, failed upgrade/backup, or CT
  outage. Thin allocation pressure can be abrupt even when pool-wide use is low.
- **Root cause:** Pre-cutover recordings were retained after NFS recording
  became active, and monitoring does not check the guest/volume threshold.
- **Corrective action:** The operator has declared pre-OMV local footage
  disposable. In remediation, verify the exact old local path and current NFS
  writer, delete only the approved old recordings, then add guest and
  thin-volume alerts; right-size only if cleanup is insufficient.
- **Dependencies / rollback:** Footage disposal is approved in principle but
  execution is deferred to remediation. Deletion is irreversible and has no
  footage rollback; current OMV recordings and Frigate DB/config are excluded.
- **Retest gate:** Root and thin usage are below agreed thresholds, current
  recordings remain on NFS, Frigate DB passes checks, and alerts fire in a
  synthetic threshold test.

## F-005 — No representative restore or independent critical-data copy

- **Severity:** High
- **Evidence:** Guest archives are fresh and the newest active-guest archives
  pass Zstandard stream checks, but no VM, CT, HA, database, config, or
  media-metadata restore was performed. Production data and most backups share
  OMV/md0, power, ACL, and ransomware domains.
- **Affected assets:** All authoritative datasets and rebuild paths.
- **Impact:** Backup corruption, missing bind-mount content, identity conflicts,
  or total-site loss may be discovered only during an incident.
- **Root cause:** Completion is measured by archive creation rather than
  isolated restore evidence and failure-domain diversity.
- **Corrective action:** Establish RPO/RTO ownership, create an encrypted
  independent/off-site copy for critical data, and run the isolated restore
  campaign in `08-resilience-test-cards.md`.
- **Dependencies / rollback:** Requires isolated storage/compute capacity and
  temporary identities with no production NIC. Remove all restored guests and
  credentials after evidence capture.
- **Retest gate:** Representative restores meet RPO/RTO, application checks
  pass, independent-copy deletion/immutability controls are verified, and the
  runbook is repeatable by a second operator.

**Owner disposition:** Accepted residual risk. The operator does not have
resources for isolated restores or an off-site/independent copy. The retest gate
remains the condition for certification, but it is not scheduled remediation.

## F-006 — Home Assistant automatic backups exclude apps

- **Severity:** High
- **Evidence:** Live automatic backup configuration selects HA settings and SSL
  but no apps/add-ons, despite documentation claiming add-ons are included.
- **Affected assets:** Mosquitto, ESPHome, Samba, Sonarr and other HA apps,
  native HA restore procedure.
- **Impact:** A native HA restore may omit app data/config and cannot reproduce
  the documented system without relying on the larger VM archive.
- **Root cause:** UI backup selection drifted from the written backup policy.
- **Corrective action:** Inventory required apps, size and schedule a full test
  backup, select and encrypt required content, and update the policy from a
  proved restore.
- **Dependencies / rollback:** Requires storage-capacity and runtime-impact
  review. Preserve the current backup plus VM archive until the new archive is
  tested.
- **Retest gate:** Archive contents include every required app/folder; isolated
  restore brings up HA and representative apps; retention and failure alerts
  work.

## F-007 — Application-level backup and source-provenance gaps

- **Severity:** High
- **Evidence:** Household Hub PostgreSQL/Qdrant/Redis, Bambuddy, and Immich are
  excluded from the app-data job. Household Hub and GardenKeeper live source
  lacks Git provenance; Bambuddy and Household Hub lack canonical stacks.
- **Affected assets:** Docker application data, rebuild suite, credentials and
  database schemas.
- **Impact:** VM-only recovery is coarse and unproved; a single application or
  database cannot be reliably reconstructed or migrated.
- **Root cause:** New live stacks were added faster than backup/repository
  onboarding requirements.
- **Corrective action:** Canonicalize source/Compose/migrations, add consistent
  database and volume exports, hash manifests, monitoring, ownership, and
  isolated restore tests.
- **Dependencies / rollback:** Must avoid exposing `.env` values and must use
  app-supported dump semantics. Retain VM backups until new restores pass.
- **Retest gate:** Clean checkout plus secrets ledger rebuilds each service;
  isolated PostgreSQL/Qdrant/Redis/Immich recovery passes; backup age is
  monitored.

## F-008 — Transfer Portal is in a persistent restart loop

- **Severity:** High
- **Evidence:** The enabled OMV service hard-codes obsolete
  `192.168.10.147:8088`, has restarted more than 46,000 times, and fails every
  five seconds with an address-bind error.
- **Affected assets:** Transfer Portal, OMV systemd/logging/CPU, documented
  native deployment.
- **Impact:** Service unavailable, noisy logs, wasted resources, and false
  belief that file-transfer tooling is operational.
- **Root cause:** Host IP migration was not propagated to the live unit/config.
- **Corrective action:** Freeze/copy current job state, reconcile the unit with
  canonical source, validate bind and ACL scope in preview, then restart once
  in an approved window.
- **Dependencies / rollback:** Requires confirming destination/source mounts and
  no active transfer. Restore old unit and stop it if validation fails.
- **Retest gate:** Stable service with restart counter unchanged, authenticated
  browse/preview/smoke job passes, and only the intended management networks
  can reach it.

## F-009 — OMV configuration and export state are not reproducibly backed up

- **Severity:** High
- **Evidence:** No stored copy of `/etc/openmediavault/config.xml` was found;
  `backups/configs` is empty. Three bind mounts point at deleted sources and
  exports contain legacy duplicates.
- **Affected assets:** OMV rebuild, NFS/SMB exports, HA/Frigate/Docker mounts,
  Transfer Portal.
- **Impact:** A clean OMV reinstall requires error-prone manual reconstruction;
  stale exports can misdirect clients or expose unintended paths.
- **Root cause:** Export and IP migrations accumulated without a canonical
  config-export/restore process.
- **Corrective action:** Capture a sanitized inventory plus restricted config
  copy, reconcile every export/bind/client, remove stale objects only after
  dependency proof, and document clean-install reconstruction.
- **Dependencies / rollback:** NFS changes require fresh approval and client
  mount inventory. Back up `config.xml` and export state before edits.
- **Retest gate:** Clean dry-run reconstruction matches intended shares; all
  live clients mount their canonical path; deleted/duplicate exports are gone;
  config copy freshness is monitored.

## F-010 — Docker-published-port enforcement is incomplete or unproved

- **Severity:** High
- **Evidence:** Docker documentation states published traffic bypasses UFW's
  normal path. Docker host has scoped `DOCKER-USER` rules but no negative-test
  proof; monitoring host's `DOCKER-USER` chain is empty.
- **Affected assets:** All published Docker services, monitoring data/admin
  UIs, VLAN trust boundaries.
- **Impact:** Services may be reachable from sources that UFW appears to deny.
- **Root cause:** Host firewall status is used as a proxy for Docker forwarding
  enforcement; rules and intended flows are not generated from one matrix.
- **Corrective action:** Reconcile every published port to router and
  `DOCKER-USER` enforcement, add default-deny before return, and test allowed
  and denied clients in a bounded window.
- **Dependencies / rollback:** Firewall changes can lock out management and
  require console access plus atomic rollback.
- **Retest gate:** Every port has an owner and consumer; representative allow
  and deny probes pass from each VLAN/Tailscale class; rules persist after
  Docker restart/reboot.

## F-011 — NFS privilege and stale-export blast radius

- **Severity:** High
- **Evidence:** Multiple exports use client-restricted `no_root_squash` with
  `sec=sys`; duplicate/direct legacy exports and a deleted-source `CCTV` path
  remain advertised.
- **Affected assets:** OMV md0 data, backup archives, Frigate recordings,
  Docker and HA clients.
- **Impact:** Root on an allowed client can act as root on exported data;
  compromised clients can alter online backups and production media.
- **Root cause:** Functional recovery shortcuts became persistent access policy
  without per-dataset least-privilege review.
- **Corrective action:** Map UID/GID ownership, prefer root squash and narrower
  exports, separate backup identities/paths, remove legacy paths, and create an
  immutable/independent copy.
- **Dependencies / rollback:** Changes can break bind mounts and app ownership;
  test one dataset at a time with saved exportfs state.
- **Retest gate:** Client UID tests pass, unauthorized root writes fail,
  authorized apps work, exports contain no unexplained duplicates, and backup
  alteration controls are proved.

## F-012 — Switch and Tailscale control planes cannot be certified

- **Severity:** High
- **Evidence:** Switch authentication was unavailable; Tailscale admin session
  was expired. Live route advertisements are visible, but approval, grants/ACL,
  identity ownership, VLAN/PVID/PoE, and saved-startup state are not.
- **Affected assets:** Segmentation, remote access, camera power, trunking,
  management-plane recovery.
- **Impact:** A hidden allow-all policy, stale route approval, or unsaved switch
  config can bypass trust boundaries or disappear after power loss.
- **Root cause:** Critical external/device state is not exported to the audit
  evidence/rebuild ledger.
- **Corrective action:** Obtain owner-supervised read-only access, export
  sanitized control-plane state, reconcile identities/routes/policy/ports, and
  schedule persistence/deny tests.
- **Dependencies / rollback:** User authentication and potentially MFA are
  required. Configuration changes remain separately approved.
- **Retest gate:** Policy lint plus deny tests pass; route approvals equal the
  `/32` design; switch running/startup configs match; power-cycle evidence is
  captured.

## F-013 — AI/tool boundaries and private logging are not safe enough

- **Severity:** High
- **Evidence:** HA logs contain detailed household conversation/tool data.
  Observed requests were misrouted and one natural-language substitution caused
  an unconfirmed recipe-import write attempt. Adversarial/safety tests are absent.
- **Affected assets:** HA conversation agent, Household Hub/Mealie/Grocy tools,
  household privacy, automation safety boundary.
- **Impact:** Private data persists in logs; ambiguous or injected instructions
  may invoke the wrong read/write tool.
- **Root cause:** Debug logging and tool routing/confirmation contracts are more
  permissive than the user-facing safety model.
- **Corrective action:** Reduce/redact logs, classify tools by read/write/safety,
  require explicit confirmation and structured arguments for writes, enforce
  an allowlist outside the model, and run prompt-injection/cross-tool tests.
- **Dependencies / rollback:** Preserve minimal diagnostic capability; stage
  policy changes against a test agent before activating in HA.
- **Retest gate:** No private payload appears at normal log level; ambiguous and
  adversarial prompts cannot write; valid confirmed operations route
  deterministically; safety-critical entities are unreachable from AI tools.

## F-014 — Monitoring and health summaries are false-green

- **Severity:** Medium
- **Evidence:** Proxmox health says 15/15 healthy while Immich/Transfer Portal
  are failed and CT 111 is near full. Kuma checks stale HA HTTP and retired
  Ollama, and omits active llama.cpp.
- **Affected assets:** Alerting, operations decisions, incident detection.
- **Impact:** Operators may delay response because dashboard/CLI summaries do
  not represent service or capacity truth.
- **Root cause:** Monitoring inventory was not reconciled after HTTPS, Frigate,
  AI, and service changes.
- **Corrective action:** Generate monitors from the service matrix, add guest
  capacity and backup-age checks, remove retired probes, and add an independent
  notification backstop.
- **Dependencies / rollback:** Avoid alert storms; stage threshold changes and
  retain prior monitor IDs until replacements are confirmed.
- **Retest gate:** Injected test failures reach the operator; all known current
  failures display accurately; no retired endpoint remains green/down.

## F-015 — Container deployment reproducibility is weak

- **Severity:** Medium
- **Evidence:** 13 baseline images float, 21 services lack health checks, all 27
  lack limits, four mount the Docker socket, live Compose drift exists, and some
  live source is unversioned.
- **Affected assets:** Docker host, monitoring, local AI, Mermaid Viewer and all
  application rebuilds.
- **Impact:** Rebuilds can pull incompatible images, silent failures restart
  indefinitely, and Docker-socket compromise grants host-equivalent control.
- **Root cause:** Stacks were optimized for rapid deployment instead of a
  consistent provenance/health/least-privilege standard.
- **Corrective action:** Pin supported versions/digests, add health and resource
  policy, remove or proxy socket access, reconcile live/source, record licenses
  and update ownership.
- **Dependencies / rollback:** Image changes need per-service backup and
  rollback digests. Do not bulk-upgrade.
- **Retest gate:** Clean checkout recreates every stack with identical digests;
  health transitions and rollback pass; no unexplained socket mount or drift
  remains.

## F-016 — Certificate and management-plane trust is inconsistent

- **Severity:** Medium
- **Evidence:** Router/PVE/switch fail Windows trust; switch cert has generic CN
  and no SAN; OMV is HTTP-only; HA uses a roughly ten-year leaf validity;
  Frigate differs between Chrome and Schannel/revocation checks.
- **Affected assets:** Administrative sessions, automation clients, HA/Frigate
  access, certificate recovery.
- **Impact:** Users normalize warnings, clients use insecure bypasses, and
  expiry/revocation failures can be missed.
- **Root cause:** Per-service certificate setup lacks one issuance, chain,
  lifetime, revocation, distribution, and monitoring policy.
- **Corrective action:** Define management PKI policy, issue SAN-correct shorter
  certificates, serve required chains, enable OMV HTTPS, distribute trust by
  client class, and alert on expiry.
- **Dependencies / rollback:** Certificate/trust changes are access-risky and
  separately approved; preserve old endpoints until every client passes.
- **Retest gate:** Chrome, Schannel, mobile/PWA and scripted clients validate
  without bypass; expiry alerts fire; rollback certificate restores access.

## F-017 — Failed privileged HA SSH app retains unnecessary exposure

- **Severity:** Medium
- **Evidence:** Advanced SSH is boot-auto but errors on port 22 conflict. It is
  host-networked, manager-role, Docker-API-enabled, AppArmor-disabled, and has
  password authentication configured; core SSH already provides access.
- **Affected assets:** HAOS host, Supervisor/Docker API, management VLAN.
- **Impact:** Duplicate privileged remote-access surface and retained credential
  exposure without operational benefit.
- **Root cause:** Temporary/alternate administrative tooling was not retired
  after the core SSH path became authoritative.
- **Corrective action:** Confirm no unique dependency, rotate any retained
  credential, disable/remove the redundant app or harden it to a unique bounded
  purpose, and document the sole break-glass path.
- **Dependencies / rollback:** Preserve verified core SSH and local console
  recovery before removal.
- **Retest gate:** Exactly one approved SSH path is reachable; redundant
  credentials fail; HA app state has no error; break-glass recovery is tested.

## F-018 — Undocumented Sonarr app on Home Assistant

- **Severity:** Medium
- **Evidence:** Sonarr 0.5.0 is started and boot-auto on HAOS but absent from the
  canonical service, access, data, backup and ownership matrices.
- **Affected assets:** HA VM resources, media credentials/data, recovery scope.
- **Impact:** Hidden dependencies and data can be lost or exposed; HA becomes a
  mixed-purpose application host.
- **Root cause:** Live app installation bypassed estate onboarding/governance.
- **Corrective action:** Decide retire, relocate, or formally onboard; document
  auth/ports/storage/backup/update/owner and validate least privilege.
- **Dependencies / rollback:** Do not stop/remove until media consumers and
  state are identified and backed up.
- **Retest gate:** Component is absent or fully represented in every canonical
  matrix and restore test.

## F-019 — Frigate detection source/live behaviour differs

- **Severity:** Medium
- **Evidence:** Live camera config explicitly disables detection; repository
  source omits the flag. Detector process exists but detect fps is zero.
- **Affected assets:** Frigate workload, alerts, shared iGPU, privacy expectations.
- **Impact:** Redeployment may unexpectedly enable detection and resource use or
  change notification/privacy behaviour.
- **Root cause:** Live operational override was not reconciled to source.
- **Corrective action:** Record intended phase state explicitly in canonical
  source and roadmap; validate resulting config without deployment.
- **Dependencies / rollback:** Enabling detection requires camera/GPU window and
  privacy acceptance. Rollback sets explicit disabled state.
- **Retest gate:** Source/live semantic comparison is equal; intentional detect
  state is visible in UI/stats and documented.

## F-020 — Local AI has limited failure headroom

- **Severity:** Medium
- **Evidence:** CT 114 has only about 2.4 GiB available under model load, no
  swap, floating images, and shared iGPU contention is untested.
- **Affected assets:** Chat, embeddings, voice pipelines, Frigate iGPU domain.
- **Impact:** Concurrent inference can trigger OOM, latency, or cascading voice
  and CCTV degradation.
- **Root cause:** Capacity is sized from steady-state observation rather than
  bounded concurrency and failure testing.
- **Corrective action:** Pin images/models, set resource policy, monitor memory
  and GPU, define graceful shedding, and run the approved shared-load test.
- **Dependencies / rollback:** Requires camera/voice test window. Stop load
  generation at latency, temperature, or memory thresholds.
- **Retest gate:** Six-camera plus voice/chat target load meets latency and
  memory thresholds without OOM; critical logic remains independent.

## F-021 — ESPHome electrical and boot safety is unproved

- **Severity:** Medium
- **Evidence:** Production-intent YAML validates but warns about strapping pins
  GPIO4/5/9 and an unspecified framework. VentSys hardware is absent.
- **Affected assets:** VentSys controllers, booth/fan/garage sensors, relays and
  physical environment.
- **Impact:** Boot glitches, relay actuation, failed recovery, or unsafe
  ventilation behaviour may occur despite successful compilation.
- **Root cause:** Software validation precedes hardware acceptance and explicit
  boot-state/electrical hazard tests.
- **Corrective action:** Pin framework/platform versions, review schematic pull
  states and isolation, bench-test cold boot/brownout/network loss/manual
  override, and certify emergency logic outside MQTT/AI.
- **Dependencies / rollback:** Blocked until hardware and a safe test rig exist.
- **Retest gate:** Signed physical acceptance cards prove fail-safe output at
  boot, disconnect, sensor fault, and manual override; calibration is recorded.

**Owner disposition:** Deferred. VentSys is not mature enough for formal
physical acceptance and remains design-only.

## F-022 — Power and common-mode resilience are omitted

- **Severity:** High
- **Evidence:** No proved UPS inventory, runtime, shutdown ordering, alert path,
  switch/router power-cycle result, or upstream-router recovery evidence.
- **Affected assets:** Router, switch, Proxmox, OMV, cameras, monitoring and
  filesystem integrity.
- **Impact:** A single power event can remove both service and monitoring,
  corrupt online data, and defeat all same-site backups.
- **Root cause:** Logical architecture is documented more deeply than physical
  power and recovery dependencies.
- **Corrective action:** Inventory circuits/PSUs/UPS loads, set runtime and
  shutdown policy, add independent alerting, and execute separately approved
  pull-the-plug/power-cycle tests.
- **Dependencies / rollback:** Requires physical access, maintenance window and
  verified backups; switch/upstream changes need fresh approval.
- **Retest gate:** Measured runtime meets policy; orderly shutdown/restart order
  is repeatable; switch config persists; alerts survive primary-host failure.

**Owner disposition:** Accepted residual risk. No UPS exists or is planned;
manual recovery/boot-order documentation is the achievable mitigation.

## F-023 — Canonical documentation does not match current state

- **Severity:** Medium
- **Evidence:** HTTPS, Frigate storage/Tailscale/camera/MQTT, backup coverage,
  Fail2ban, paths, HomeIoT identifiers, monitoring and app placement conflict
  across README, matrices, decisions, TODOs and install docs.
- **Affected assets:** Operations, rebuild, incident response, future changes.
- **Impact:** Operators execute stale steps or treat planned/obsolete controls
  as live, increasing outage and exposure risk.
- **Root cause:** State-changing work did not update the canonical set as one
  transaction; historical and current truth are intermingled.
- **Corrective action:** After remediation decisions, update canonical docs from
  this evidence, preserve historical context, repair wiki claims, and add link/
  claim checks to verification.
- **Dependencies / rollback:** Discovery report remains immutable; corrections
  must not erase its original decision.
- **Retest gate:** Every material claim in this ledger is verified/planned/
  obsolete/blocked with owner and evidence; link and stale-path scans pass.

## F-024 — Patch and version governance is incomplete

- **Severity:** Medium
- **Evidence:** OMV, Docker hosts, local AI and HA apps have pending packages;
  multiple images float and some current vendor releases contain security fixes.
- **Affected assets:** Hosts, container runtime, HA/Frigate/ESPHome, applications.
- **Impact:** Known security/reliability fixes may be missed; unreviewed floating
  updates can introduce breaking changes.
- **Root cause:** Monitor-only intent and update-review records are not complete
  for every live component/digest.
- **Corrective action:** Create a version/SBOM inventory, subscribe to primary
  advisories, stage updates by dependency wave, pin rollback artifacts, and
  record review decisions.
- **Dependencies / rollback:** Requires backups, compatibility checks and
  per-host windows; never bulk-update the estate.
- **Retest gate:** No unexplained update remains; selected versions pass service,
  restore and rollback gates; digest/source records are current.

## F-025 — Backup jobs overlap and application consistency is unclear

- **Severity:** Medium
- **Evidence:** Docker app-data at 03:45 can overlap CT `vzdump` at 04:00; jobs
  share OMV and application disks. Database quiesce/snapshot semantics are not
  proved for every stack.
- **Affected assets:** OMV I/O, CT 111/114, Docker databases, archive quality.
- **Impact:** Latency, capacity spikes, or internally inconsistent database and
  VM copies.
- **Root cause:** Schedules evolved independently without a common I/O and
  consistency model.
- **Corrective action:** Measure durations/load, serialize high-I/O jobs, use
  app-native dumps before VM backup where required, and alert on overrun.
- **Dependencies / rollback:** Schedule edits require owner agreement and one
  observation cycle; retain prior schedule record.
- **Retest gate:** No unintended overlap, backup duration stays within window,
  database restores pass, and overrun alerts fire.

## F-026 — CCTV client UX has identifiable defects

- **Severity:** Low
- **Evidence:** The primary HA CCTV view is unnamed, takes about 11 seconds to
  render initially, and logs a DOM transition timeout; desktop/mobile video
  otherwise works.
- **Affected assets:** HA Lovelace CCTV dashboard and PWA experience.
- **Impact:** Confusing navigation and slow incident access; not a current loss
  of recording.
- **Root cause:** Storage-mode dashboard metadata/performance was not included
  in acceptance criteria.
- **Corrective action:** Name the view, profile card/stream startup, remove
  timeout cause, and test cold/warm load on target mobile clients.
- **Dependencies / rollback:** Dashboard change requires HA UI backup and can be
  rolled back from `.storage` backup.
- **Retest gate:** Named route renders within the agreed target without console
  errors on desktop and mobile, locally and through approved Tailscale path.

## F-027 — Mermaid Viewer baseline is incomplete; overlay is not yet governed

- **Severity:** Low
- **Evidence:** Baseline viewer hangs because the local Mermaid module is
  missing. A post-baseline overlay adds the vendor module, build, Nginx image,
  Compose and `dist/`, but is uncommitted and undeployed.
- **Affected assets:** Diagram browser, Docker-host proposed service,
  documentation inventory.
- **Impact:** Current baseline feature is nonfunctional; an unmanaged overlay
  could introduce generated/vendor drift.
- **Root cause:** Runtime dependency and deploy packaging were omitted from the
  original commit.
- **Corrective action:** Validate reproducible build/hash/license, decide which
  generated/vendor assets are tracked, run browser tests from the container,
  then commit/deploy through normal approval.
- **Dependencies / rollback:** No production dependency exists; rollback is
  removal of the proposed service/overlay.
- **Retest gate:** Clean clone builds without CDN, all diagrams render with no
  console error, container health and ACL pass, and tracked/generated policy is
  documented.

## F-028 — Host secret-file permissions are broader than necessary

- **Severity:** Medium
- **Evidence:** Immich environment and selected Mealie secret files are mode
  0644 on the Docker host. Values were not collected.
- **Affected assets:** Immich/Mealie accounts, local Docker-host users and
  processes, backups copying those files.
- **Impact:** Any local account/process with read access can obtain application
  credentials; backups may duplicate them into broader ACLs.
- **Root cause:** Deployment tooling created secret files with default umask/
  ownership rather than a declared secret policy.
- **Corrective action:** Inventory readers, rotate exposed credentials where
  warranted, set least-privilege ownership/mode, use a secret store or Docker
  secrets where practical, and constrain backup ACLs.
- **Dependencies / rollback:** Confirm container UID requirements before mode
  changes. Restore prior mode only if a service fails while fixing ownership.
- **Retest gate:** Unauthorized local identity cannot read secrets; containers
  remain healthy; repository/history scans are clean; backup ACL tests pass.

## F-029 — Ignored local automation secrets inherit broad Windows ACLs

- **Severity:** High
- **Evidence:** Redacted scanning found credential fields in ignored ESPHome
  secrets, VentSys runtime config, and an ignored dashboard copy. Their Windows
  ACLs grant ordinary local users read/execute and authenticated users modify
  rights. The ignored router deployment private key is correctly restricted.
- **Affected assets:** ESPHome device/API/Wi-Fi identities, VentSys dashboard
  access/configuration, local workstation users and processes.
- **Impact:** A lower-privilege local user or compromised process can read or
  replace automation credentials/config, potentially impersonating devices or
  changing control-plane targets.
- **Root cause:** Git ignore prevents repository exposure but files inherit a
  workspace ACL designed for collaborative editing rather than secrets.
- **Corrective action:** Inventory required readers, move values to an approved
  secret store or protected runtime directory, remove the ignored stale copy,
  restrict ACL inheritance, and rotate credentials if local exposure is not
  acceptable.
- **Dependencies / rollback:** Confirm ESPHome build and dashboard runtime
  identities before ACL changes. Export ACLs and retain a protected backup;
  restore only the minimum service identity if access breaks.
- **Retest gate:** A non-owner test identity cannot read or modify the files;
  authorized builds/dashboard access still work; stale copies and redacted
  candidate paths are reconciled to the secrets ledger.
