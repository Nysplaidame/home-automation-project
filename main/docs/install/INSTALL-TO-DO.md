---
title: Installation Manual Suite To-Do
description: Companion checklist for completing and validating the fresh rebuild documentation suite
tags: [install, tasks, rebuild, documentation]
created: 2026-05-24
modified: 2026-09-14
type: task-list
status: active
---

# Installation Manual Suite To-Do

Use this checklist with [START-HERE.md](START-HERE.md). It tracks what remains
before the documentation suite is good enough to rebuild the system from zero
without live assistance.

## Consolidated coverage audit — September 11

This is the current planning view; the dated continuation notes below are history.
Scope: all 34 named operational entries in the service matrix plus eight named
roadmap additions, with ntfy counted once. Internal databases/workers are assessed
under their parent service; unnamed future AI apps have no defined auditable scope.
The troubleshooting app's September11 additions are included in its source record.

**42 entries: 36 Written, 0 Review, 0 Missing source/configuration, 6 Candidate.**
These counts describe documentation disposition, not a completeness percentage.

- **Written:** lifecycle instructions exist in the linked manual and shared
  phases. This does not certify every command, current runtime or successful restore.
- **Review:** a runbook exists, but a specific lifecycle/freshness check remains;
  heading presence alone was not treated as comprehensive coverage. The nine
  initial review rows have now been processed; none remains in this disposition.
- **Missing source/configuration:** instructions cannot close the recovery
  contract without the named source, settings or backup-policy artifact.
- **Candidate:** an evaluation path exists; intentionally parked deployment and
  acceptance are not defects to solve by starting the service.

Every operational entry still requires dated evidence for its intended scope.
Historical successes remain valid historical records, not fresh acceptance.
No row means a complete credentialed blank-hardware rebuild has been proven.

| Service | Documentation disposition | Remaining work / proof |
|---|---|---|
| [OpenWrt router](phases/01-router-openwrt.md) | Written | Real deployment inputs and full credentialed rebuild proof. |
| [Proxmox](phases/02-proxmox-host.md) | Written | Blank host/guest rebuild and current archive/restore evidence. |
| [Home Assistant](phases/03-home-assistant.md) | Written | Isolated native restore; physical integrations remain deferred. |
| [Frigate](phases/04-frigate.md) | Written | Camera reconnection and recording/restore acceptance. |
| [Monitoring stack](phases/10-backups-monitoring-maintenance.md) | Written | VM102 rebuild, independent observer and alert acceptance. |
| [Docker host](phases/05-docker-host.md) | Written | Partial-build backup inventory and guest rebuild rehearsal. |
| [Local AI inference](phases/05a-local-ai.md) | Written | Mounted model/voice/WebUI recovery and floating-image limits documented; actual image artifacts and inference restore proof remain. |
| [OMV NAS](phases/06-omv-nas.md) | Written | OS/reference reconstruction separated from independent data copies; disk-specific recovery and fresh SMART/restore proof remain. |
| [OMV Transfer Portal](services/transferportal.md) | Written | Stopped DB/config/helper checkpoint and disposable portal restore documented; September hardening deployment remains separate. |
| [Tailscale](phases/05-docker-host.md) | Written | Identity/route recovery and intended-denial tests on rebuilt host. |
| [AdGuard Home](services/adguard-home.md) | Written | Use Phase07/12 for fallback/update/recovery proof; validate effective configuration. |
| [Immich](services/immich.md) | Written | Matched database/media isolated restore and household import acceptance. |
| [Homepage](services/homepage.md) | Written | Protected TLS recovery and proxy denial/rollback proof via Phase07/12. |
| [Dozzle](services/dozzle.md) | Written | Phase07/12 socket/exposure checks; no authoritative application data. |
| [Bambuddy](../../configs/docker-host/stacks/bambuddy/README.md) | Written | Full stopped-state recovery added; host-network exception and P1S commissioning remain open. |
| [ntfy](services/ntfy.md) | Written | Phone delivery and current isolated account/ACL restore acceptance. |
| [Mealie](services/mealie.md) | Written | Owner/export and representative isolated restore acceptance. |
| [Grocy](services/grocy.md) | Written | Owner/pilot workflow and consistent isolated restore acceptance. |
| [Obsidian LiveSync](services/obsidian-livesync.md) | Written | Client wizard/two-device rollout; preserve canonical vault recovery boundary. |
| [GardenKeeper](services/gardenkeeper.md) | Written | Backup defect repaired/deployed; seven tests, source builds, isolated DB/API recovery passed. Git provenance, uploads and worker workflows remain separate. |
| [Household Hub](../../configs/docker-host/stacks/household-hub/README.md) | Written | Source builds, isolated PostgreSQL/API and two Qdrant collection restores passed; coordinated cross-store and external workflow recovery remain open. |
| [Mermaid Viewer](services/mermaid-viewer.md) | Written | Complete static artifact checkpoint, isolated render and full/diagram-only rollback paths linked. |
| [Gridfinity Layout Tool](services/gridfinity-layout-tool.md) | Written | Static build, scheduler, previous-release and separate browser-state recovery documented; runtime version/task state unverified. |
| [Recomp Tracker](services/recomp-tracker.md) | Written | Current SQLite restore and notification acceptance; preserve copied-data isolation. |
| [MediaMTX](services/mediamtx.md) | Written | Daily protected config checkpoint deployed and restored; September14 schedule success. Owner chose no recording deletion/manual review; recording backups separate. |
| [Jellyfin](services/media-libraries.md) | Written | Consistent application checkpoint plus independent library recovery proof. |
| [Calibre-Web](services/media-libraries.md) | Written | Consistent application/library checkpoint and isolated restore proof. |
| [Atsumeru](services/media-libraries.md) | Written | Consistent config/database checkpoint plus library recovery proof. |
| [Vaultwarden](services/vaultwarden.md) | Written | Preserve historical restore evidence; verify current recovery credentials and matched checkpoint. |
| [Mullvad gateway + qBittorrent](services/download-gateway.md) | Written | Current tunnel containment and isolated config recovery; payloads are separate. |
| [SearXNG](services/searxng.md) | Written | Sanitized settings parsed/loaded; effective environment overrides verified. Source Compose rejects empty secret; engine-wide search acceptance remains separate. |
| [Whoogle](services/whoogle.md) | Written | Rebuild pinned service and bounded upstream query acceptance; browser preferences separate. |
| [Watchtower monitor-only](services/watchtower-monitor-only.md) | Written | Resolve error40014; preserve separate Compose/env backup and prove unchanged scan targets. |
| [apt-cacher-ng](../procedures/apt_cacher_ng_design.md) | Written | Native package/config/client recovery documented; CT114 package-path acceptance remains open. |
| [Immich curated exporter](services/immich-curated-exporter.md) | Written | Matched state/allow-list/media recovery and rollback documented; timer remains gated on bounded no-delete acceptance. |
| [Paperless-ngx](services/paperless-ngx.md) | Candidate | Written evaluation/export/restore path; no real document import before acceptance. |
| [Actual Budget](services/actual-budget.md) | Candidate | Written evaluation and recovery path; HTTPS/financial-data promotion gated. |
| [Scrypted](services/scrypted.md) | Candidate | Placement/camera overlap decision precedes isolated evaluation. |
| [Portainer](services/portainer.md) | Candidate | Socket/admin boundary and isolated no-production-socket restore required. |
| [Local registry mirror](services/local-registry-mirror.md) | Candidate | TLS/capacity/client rollback decision remains required. |
| [Node-RED](services/node-red.md) | Candidate | Safe-mode restore and explicit flow promotion remain required. |
| [Troubleshooting Dashboard](../../apps/troubleshooting-dashboard/README.md) | Written | September11 routes/Windows collector documented; Proxmox collector/access and real backup evidence still open. |

### Live source discovery follow-up

Both live application trees and migration implementations were located through
working VM103 SSH. Read-only schema queries returned GardenKeeper0001–0029 and
Household Hub20260809_0002. GardenKeeper reset migrations0006/0009 and Hub's
unconditional Alembic startup command are now documented in their runbooks.
Missing-source disposition now means missing provenance/complete off-host
recovery artifact, not that the source is absent from the running host.
No migrations, domain-data reads or service changes were executed.

### Protected checkpoint follow-up

GardenKeeper and Hub source snapshots plus SearXNG's secret-bearing settings
were copied off VM103 to a restricted workstation directory; hashes verified.
Exact paths/hashes and exclusions are in the service runbooks. These are scoped
recovery artifacts, not full deployment backups, Git provenance or restore proof.
SearXNG semantic/runtime review remains open because a YAML parser was not
available in the inspected interpreter. No live service configuration changed.

### September 12–14 execution and acceptance

- [x] Repair/deploy GardenKeeper backup; seven failure/success regression cases
  passed, first manual run succeeded and September14 unit status remains success.
- [x] Parse and sanitize SearXNG settings with its installed interpreter; verify
  effective secret/base URL and unchanged limiter/engine enablement. Add guarded
  Compose interpolation and a blank env example. No production settings changed.
- [x] Build all six recovered API/worker/web images through existing egress;
  offline dependency caches were insufficient. No live images were replaced.
- [x] Restore both PostgreSQL dumps with schema comparison; run rebuilt APIs on
  restored data with no production network and test health, authenticated reads
  and anonymous denial. Restore both Qdrant collections (five total points).
- [x] Deploy/check MediaMTX daily protected configuration backup, verify hash,
  extraction and exact restored-file matches. September14 scheduled run passed.
  Owner selected deletion disabled/manual review; no recordings were deleted.
- [x] Complete the cross-phase entry/exit dependency review: Phase02 owns host
  foundation; guests are created in their phases, storage arrives at06, recurring
  backup/monitoring at10, and disconnected hardware remains deferred at11/12.
- [ ] Complete a credentialed blank-system rehearsal and the remaining physical,
  worker/integration and coordinated multi-store acceptance. Documentation counts
  do not certify those unperformed tests.

Final validation: 133 local paths/anchors, 13 embedded shell blocks, both
changed shell scripts and whitespace checks passed. MediaMTX also passed two
offline mount-boundary tests (missing mount and wrong export), in addition to
the live checkpoint/restore and successful scheduled run.

The four missing-artifact dispositions are closed by tested source checkpoints,
reviewed settings and the new config-backup contract. Unknown upstream Git
provenance and incomplete workflow coverage remain explicit in the runbooks.

### Historical next-work list (superseded by execution above)

1. Recover GardenKeeper's application/migration source and repair its backup
   script's masked pipeline failure; the checked manual checkpoint is a temporary
   documented method, not a deployed script fix.
2. Recover Hub source and SearXNG effective settings through an existing authorized
   management route; establish MediaMTX protected off-host capture/retention.
3. Finish the sequential dry-read, checking every phase's inputs and return
   dependencies. Syntax/link checks and bounded phase reviews are already recorded,
   but they do not substitute for this walkthrough.
4. Perform selected isolated restore/notification acceptance, then the complete
   rebuild rehearsal when credentials, storage and hardware scope permit it.

Architecture navigation: [diagram library](../diagrams/README.md),
[service placement](../diagrams/infrastructure/docker-host-service-placement.mermaid),
[backup flow](../diagrams/storage/storage-and-backup-flow.mermaid) and
[offline troubleshooting](../troubleshooting/diagnostic-walkthroughs.md).

### Nine-row review completion

All nine initial review entries were processed against their existing manuals
and relevant source. Eight now have written recovery/update boundaries;
GardenKeeper moved to Missing source because its application/migrations are
outside the vault. Its dump script also masks upstream pipeline failure; this
was documented and queued, not silently treated as a successful backup.
Bambuddy's historical password-in-command shim was replaced with canonical
runbook navigation, and Mermaid app deployment now names the actual stack files.
No live service, image, timer, hardware or source repository was changed.
The initial raw-IP SSH attempt did not select the configured workstation key.
The subsequent access correction verified `docker-host-lan` and configured the
IP to use the same identity; both now work with strict host-key checking.
No server authentication changed. GardenKeeper/Hub source provenance remains
open, but VM103 workstation access is no longer blocked.
Validation passed: 115 local paths/anchors across 14 files and 56 shell blocks;
whitespace checks passed. Phase06/08 exit wording was also reconciled with
future-app and Phase10 return checkpoints.

## September 11 service lifecycle continuation

Expanded ntfy, Watchtower, SearXNG and Whoogle installation, update, backup,
isolated recovery and rollback guidance against tracked Compose and backup
source. Added Mermaid links and replaced unpinned setup examples. Corrected
obsolete WiFi WAN/no-proxy claims and the nonexistent SearXNG `.env.example`.
Watchtower notification error40014, phone receipt and live restore acceptance
remain open. The central app-data job covers ntfy's SQLite snapshots/config,
not the other three stacks' configuration; separate checkpoints are explicit.

Validation: 38 local Markdown paths/anchors across eight canonical files,
14 shell blocks and two PowerShell blocks in the four manuals passed. Whitespace
validation passed after removing trailing blank lines. This checks navigation
and command syntax only; no infrastructure commands or restores were executed.


### September 11 rebuild dependency pass

- [x] Review Phase07/08 boundaries: remove the all-stack stop example, separate
  blank credential generation from restore, and defer VM102 monitoring and the
  recurring app-data timer to Phase10 on a blank build. Manual checkpoints and
  later promotion evidence remain required.
- [x] Add a root-only MediaMTX configuration checkpoint/extraction procedure and
  recording-capacity estimate; encrypted off-VM destination, recurring capture,
  actual restore proof and owner-selected retention remain open.
- [x] Preserve Household Hub's historical Alembic revision and protected dump
  location as recovery leads; current source/schema recovery is still unproven.

Validation passed: 76 local paths/anchors across eight canonical files,
22 shell blocks and four PowerShell blocks in the changed phase/service scope,
and `git diff --check`. These are syntax/navigation checks only.

This is a bounded dependency review, not completion of the full sequential
rebuild dry-read. No live backups, credential changes or deletion were performed.

### September 11 backup-phase continuation

- [x] Add Phase10's missing app-data script/unit/timer installation path and
  Kuma heartbeat helper/secret prerequisites. First manual backup and heartbeat
  acceptance precede timer enablement; partial rebuilds retain manual checkpoints.
- [x] Document the mandatory source inventory, GardenKeeper dump prerequisite
  and non-atomic `latest` mirror. Restore from a successfully completed dated run.
- [x] Make VM/CT restore checks stop on failure, reject both VM and CT ID
  collisions, and remove all restored CT network entries before isolation review.
- Validation: 17 shell blocks, two PowerShell blocks, 15 local paths and
  `git diff --check` passed. No backup jobs, heartbeats or restores were executed.
- [ ] Complete the remaining sequential dry-read and a separate live rehearsal;
  this focused repair does not certify the entire rebuild suite.

### September 11 final-phase dependency review

- [x] Correct Phase09's false Watchtower backup-coverage claim and return its
  recurring-job checks to Phase10 installation/heartbeat prerequisites.
- [x] Reconcile Phase11 with deliberately disconnected cameras and uncommissioned
  P1S/VentSys; distinguish deferred hardware tests from failures and permit
  independent Phase12 software checks without certifying physical acceptance.
- [x] Stop ESPHome flashing and router source-validation sequences when a prior
  native command fails; preserve PowerShell location cleanup.
- Validation: 32 shell blocks, 10 PowerShell blocks and 66 local paths across
  the three phases/START-HERE passed; `git diff --check` passed. No firmware,
  router deployment, hardware commissioning or live acceptance was performed.

## September 10 continuation

- [x] Reconcile install entrypoint, router/operator/Proxmox/OMV phases and final
  validation with the September network baseline: PPPoE, VLAN55, HomeAdmin/LAN5
  recovery, direct LAN1 Proxmox trunk and direct LAN4 OMV.
- [x] Retain written troubleshooting beside the app: add
  [five diagnostic walkthroughs](../troubleshooting/diagnostic-walkthroughs.md)
  with source hosts, expected results, evidence freshness and Mermaid links.
- [x] Correct disconnected-camera/P1S claims, old LAN2 recovery advice, the
  NAS switch-port claim, and the superseded August compiler blocker.
- [x] Add a shared [media operating manual](services/media-libraries.md) for
  Jellyfin, Calibre-Web and Atsumeru, including explicit backup/restore limits.
- [ ] Finish service-by-service lifecycle coverage against the current matrix,
  including services whose runbooks live beside Compose rather than in this suite.
- [x] Review the cross-system troubleshooting reference's shell contexts,
  authentication advice and immediate recovery actions. Correct public-token
  guidance, MQTT localhost/password examples, ping/refusal assumptions and
  automatic restart/ownership advice. Runtime acceptance remains separate.
- [x] Add download-gateway and Recomp lifecycle manuals from Compose,
  application and backup source; include restore isolation and Mermaid links.
- [x] Repair the VM103 circular entry dependency and EFI/import disk assumption;
  defer early OMV archive steps explicitly until Phase06, and reconcile CT114
  resource guidance against the guest inventory.
- [x] Expand VM102's cloud-image creation steps, verified-image prerequisite,
  current resources, imported-disk discovery and cloud-init retention; link
  this prerequisite from Phase10. Live blank-build acceptance is still open.
- [x] Review MediaMTX lifecycle instructions and Household Hub's actual source
  boundary. Add MediaMTX installation/backup/update/restore guidance and a Hub
  deployment-boundary README instead of implying the mirror can build the app.
- [ ] Recover the canonical Household Hub application repository/revision and
  link its build/migration/isolated database restore procedure; the Compose
  mirror and backed-up exports alone cannot meet this requirement.
- [ ] Establish MediaMTX protected configuration backup and recording retention;
  its source is reproducible but the central app-data job does not capture it.
- [x] Complete the source-backed update/restore coverage review for SearXNG,
  Whoogle, Watchtower and ntfy (September11); live acceptance remains separate.
- [ ] Recover and review effective SearXNG settings and preserve a sanitized
  source template; the current Compose alone cannot reproduce engine/limiter
  policy or prove effective secret use. Add protected off-VM configuration backup.
- [ ] Perform a complete sequential dry-read after this reconciliation, then
  record a separate credentialed rebuild/restore rehearsal when feasible.

The app's September 10 freshness improvements are now deployed and live-tested
in a separate task. The Windows collector uses canonical source; the installed
Proxmox collector update and fresh mount/backup acceptance remain blocked by
SSH access. DNS/Homepage promotion remains open. The historical audit counts below apply
to their dated August scope, not to every subsequently added document.

### September 10 second continuation

- Added source-backed operating manuals for the download gateway and Recomp,
  expanded MediaMTX, and documented the missing Household Hub application
  source/database recovery contract.
- Corrected the troubleshooting reference's authentication/transport assumptions
  and named each executable shell context. Removed public dashboard-token
  advice, command-line MQTT password examples and automatic repair shortcuts.
- Fixed the VM103 entry dependency, explicit VM102 cloud-image creation,
  discovered imported disk IDs instead of assuming EFI/OS disk numbering,
  current VM103/CT114 resources and post-NAS return checkpoints.
- The first validation of this second batch passed 318 local links across
  76 documents, 393 shell blocks and 72 PowerShell blocks. These are syntax and
  local navigation checks, not executed infrastructure/recovery procedures.
  Final navigation check passed 329 local links across 77 documents; all four
  shell blocks in the expanded MediaMTX/Hub scope also passed. `git diff --check`
  passed. Other active app changes in the shared checkout were not part of
  this documentation validation.

### September 10 source verification

- Local Markdown paths/anchors: 279 links across 70 documents passed. Scope
  includes the install suite, troubleshooting directory and changed Markdown
  references; this is not a full Obsidian WikiLink or external-URL audit.
- Embedded commands: 83 PowerShell blocks parsed; 351 shell blocks were
  syntax-checked. Two older unquoted placeholder examples were repaired and
  all 26 shell blocks in those two affected documents passed the recheck.
- Router source lint and all four compiler recovery regression tests passed.
- Commands were parsed, not executed against live hosts. These results do not
  close sequential usability, credentialed deployment or isolated restore proof.

## Completion standard

- [ ] A true beginner can identify the next document, target machine, user/shell context, command, expected result, and recovery path at every step.
- [x] Every command block has a `Run on:` label immediately before it
  (2026-08-09 automated audit: zero missing labels across active install docs).
- [x] Every placeholder used in an install command appears in
  [secrets-placeholder-ledger.md](reference/secrets-placeholder-ledger.md)
  (2026-08-09 audit: 52 unique active-install placeholders, zero missing).
- [x] Every package or dependency appears in [package-dependency-matrix.md](reference/package-dependency-matrix.md)
  (2026-08-24 install-command audit added the missing OpenWrt `ethtool`,
  workstation Node/npm, and Garage Pi virtual-environment dependencies).
- [x] Every risky service has a decision gate before deployment (2026-08-24:
  global public-exposure, credential-store, camera-bridge, low-code/agent and
  automatic-update gates plus the service promotion-boundary matrix).
- [ ] Every Tier 1-3 service has install, validation, backup, update, rollback, and troubleshooting coverage.
- [ ] The suite passes a dry-read from [START-HERE.md](START-HERE.md) through final validation.

## Phase Manual Expansion

- [x] Phase 00 operator basics: add examples for hardware inventory, IP plan, MAC addresses, and secret placeholders.
- [x] Phase 01 router/OpenWrt: add full fresh-flash path, first-flight deploy path, full deploy path, router-local NTP validation, and lan5 recovery drill.
- [x] Phase 02 Proxmox: add ISO verification, install checkpoints, storage layout choices, bridge/VLAN validation, and rollback notes.
- [x] Phase 03 Home Assistant: add HAOS install, onboarding, add-on installs, MQTT setup, Companion App setup, router-derived time config, HACS decision gate, and backup validation.
- [x] Phase 04 Frigate: expand CT 111 base/Docker/shared-iGPU guide with tested blank-to-live recovery examples.
- [x] Phase 05 docker-host: add VM baseline, Docker official repository install, Compose policy, `/opt/stacks/<service>/` layout, Tailscale host-route setup, UFW rules, and rollback.
- [x] Phase 05A local AI inference: align CT 114 Compose, shared-iGPU mapping, HA Assist integration and performance gates.
- [x] Phase 06 OMV NAS: add OMV install, disk wipe warning, filesystems, users, NFS/SMB shares, SMART monitoring, and HA/Frigate/Immich storage mounts.
- [x] Phase 07 Tier 1 apps: add full command-by-command deploy order for AdGuard Home, Immich, Homepage, and Dozzle.
- [x] Phase 08 Tier 2 apps: make every draft installable while keeping deployment approval gates explicit.
- [x] Phase 09 Tier 3/evaluate apps: ensure Vaultwarden, Portainer, Watchtower, registry mirror, and Node-RED cannot be made live without security/backup approval.
- [x] Phase 10 backups/monitoring/maintenance: add restore drills, maintenance windows, update policy, and alerting checks.
- [x] Phase 11 physical integrations: add camera, printer, ESPHome, VentSys wiring, first-flash, adoption, and safety-test sequences.
- [x] Phase 12 validation/troubleshooting: add an end-to-end acceptance test and one troubleshooting path per Tier 1 service.

## Router-Deploy Documentation Tasks

- [x] Document that router-deploy is router-only: network, DHCP, DNS, firewall, local hostnames, WireGuard fallback, router-local NTP, and validation artifacts.
- [x] Document that router-deploy does not deploy Docker services, OMV, Tailscale auth, or app stacks.
- [x] Add beginner notes for `first-flight` versus `full` profiles.
- [x] Add expected output examples for `lint.py`, `compile.py`, `deploy.ps1`, `test.ps1`, and `test-connectivity.ps1`.
- [x] Add a recovery drill for failed deploy, watchdog rollback, and physical lan5 recovery.

## Service Manual Coverage

- [x] AdGuard Home: install, first-run setup, router DNS fallback, blocklist policy, backup/export, monitoring, rollback.
- [x] Immich: install, `.env`, database volumes, OMV library path, backup, update, mobile app onboarding, rollback.
- [x] Homepage: install, service widgets, secrets handling, backup, rollback.
- [x] Dozzle: install, read-only Docker socket decision, auth/exposure decision, backup, rollback.
- [x] Paperless-ngx: install, scanner/import path, OCR dependencies, backup, retention, rollback.
- [x] Mealie: manual now covers named users, full application backup, portable
  recipe export, loopback-only isolated restore, updates and matching-data
  rollback. Live admin/export acceptance remains an operator action.
- [x] Grocy: manual now covers the disposable purchase/consume/correction/
  expiry workflow, pre-pilot checkpoint, isolated restore and version/data
  rollback. The live pilot remains an operator action.
- [x] Obsidian LiveSync: manual now covers backend rebuild, `K:` canonical-vault
  selection, Bitwarden/setup-URI separation, stop-before-initialise gate,
  two-device round trip, isolated CouchDB restore and wrong-source rollback.
  Client rollout remains parked while the canonical tree is dirty.
- [x] ntfy: install, topic policy, public/private exposure decision, backup, rollback.
- [x] Actual Budget: install, auth, backup/export, rollback.
- [x] Scrypted: hardware/camera decision gate, install, storage, HA/Frigate overlap, rollback.
- [x] SearXNG: install, instance secret, egress policy, rate-limit/abuse controls, backup, rollback.
- [x] Whoogle: install, egress policy, rate-limit/abuse controls, backup, rollback.
- [x] Vaultwarden: explicit security gate, HTTPS-only exposure, SQLite-consistent
  backup and two isolated restore proofs documented; owner onboarding/2FA/
  recovery remains an operational follow-up rather than a manual-coverage gap.
- [x] Portainer: explicit admin-surface gate, auth, backup, rollback.
- [x] Watchtower monitor-only: install, notifications, no automatic updates, rollback.
- [x] Local registry mirror: storage sizing, cache policy, backup/exclusion policy, rollback.
- [x] Node-RED: decision gate, credential secret handling, HA overlap, backup, rollback.

## Reference Completeness

- [x] Diagram library: replace stale exported/static diagrams with canonical Mermaid sources for architecture, install sequence, DNS/NTP, access, service placement, storage, and VentSys safety flow.
- [x] Rebuild state matrix: verify every phase maps
  blank/prepared/installed/configured/validated/live.
- [ ] Secrets ledger: add every router, HA, MQTT, Tailscale, Docker, OMV, app, camera, and printer placeholder.
- [x] Package matrix: every active `apt`/`opkg` install dependency plus the
  Garage Pi Python and Mermaid Viewer Node/npm build dependencies has install
  and verification coverage (2026-08-24 audit).
- [x] Command location legend: add UI-only contexts where no shell is used.
- [x] Version policy: volatile infrastructure, app, AI and client manuals now
  require official release lookup, immutable version recording and compatible
  data rollback before deployment (2026-08-24).
- [x] Decision gates: public exposure, password managers, camera bridges,
  low-code/agent automation, and automatic updates have explicit approvals and
  rollback requirements (2026-08-24).
- [ ] Service matrix: verify every planned app has host, port, URL, VLAN, Tailscale exposure, backup, monitoring, and runbook.
- [ ] ACL/access matrix: verify no undocumented path reaches Management, NVR, IoT, Printers, or Storage.
- [x] Local AI references: align CT 114 packages, firewall paths, monitoring checks and performance evidence.

## Current-State Annotations

- [x] Add current-state callouts for router first-flight deployed state.
- [x] Add current-state callouts for Proxmox, HAOS, Frigate base, docker-host, and Bambuddy live state.
- [x] Add current-state callout for OMV.
- [x] Add current-state callouts for cameras, Tier 1 apps, and VentSys hardware.
- [x] Add current-state callout for core HA tools: Mosquitto, ESPHome, Terminal & SSH, Studio Code Server/File Editor, and Companion App status.
- [x] Add canonical current-state callout for CT 114 after deployment.
- [x] Ensure current-state callouts never replace the fresh rebuild path
  (2026-08-09 phase-manual dry-read: callouts are separated from ordered fresh
  install/recovery steps).

## Sanity Checks

- [x] Run local Markdown link validation (2026-08-24: all 50 active install
  documents checked; zero broken local Markdown links).
- [x] Search for stale `Main/` paths (active docs clean; legacy `Main/` paths remain in `_archive/` historical files).
- [x] Search for stale Pi OS Lite NAS claims.
- [x] Search for Pi-hole-preferred claims.
- [x] Search for Google DNS fallback references.
- [x] Search for broad Tailscale/WireGuard storage subnet claims.
- [x] Search for unresolved placeholders outside approved examples (2026-08-24:
  52 active angle-bracket placeholders, all present in the secrets ledger;
  zero undocumented placeholders).
- [x] Confirm every command block has a `Run on:` label (2026-08-24: two newer
  omissions repaired; zero missing across active install docs, 66 PowerShell
  blocks parsed without errors and 311 shell blocks passed `bash -n`).
- [ ] Complete credentialed router compilation and rebuild acceptance after changes.
  - 2026-08-09 source audit: `validate-home-local-dns.ps1 -SkipLive` passed for
    48 aliases.
  - Historical 2026-08-24 Tailscale-invariant failure is superseded by September
    recovery lint/compiler regression passes. Both profiles require real PPPoE
    credentials; full deployment still needs real WireGuard, device-MAC and
    Wi-Fi inputs. Preview output is not deployment acceptance.

## Final Dry-Run

- [x] Start at [START-HERE.md](START-HERE.md).
- [x] Follow every phase link in order (2026-08-09: all 13 phase links and
  phase-local Markdown links resolve; sequence reviewed against the ownership
  and rebuild-state maps).
- [x] For each command, confirm the target machine and shell/user are obvious
  (2026-08-09 install-suite label and shell-language audit).
- [x] For each phase, confirm expected result and failure recovery are actionable
  (2026-08-09: all 13 phase manuals have a nearby expected-result contract for
  every shell/PowerShell block plus a bounded recovery/rehearsal path).
- [x] For each service, confirm deployment can be stopped before it becomes
  live (2026-08-24: `services/README.md` records the last safe stop and
  promotion evidence for all 23 service manuals).
- [x] Update this checklist with any missing steps found during the dry-run
  (router source blockers and live-only acceptance gates remain explicit).

2026-08-24 historical result: structure, navigation, placeholders and parsed
command syntax passed; the then-failing router invariant blocked progression.
September source recovery supersedes that blocker. A sequential dry-read and
credentialed blank-hardware rebuild remain open; structural checks and live
operator acceptance are separate requirements.
