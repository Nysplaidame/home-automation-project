---
title: Roadmap, code and file audit — 2026-10-02
description: Current feature disposition, reproducible checks and independent next work
created: 2026-10-02
modified: 2026-10-04
type: audit
status: complete
---

# Roadmap, code and file audit — 2026-10-02

## Conclusion

The roadmap is not fully implemented. The service foundation and diagnostic
tools are ahead of integrated household workflows. The current source checks
pass after two local code repairs, but fixtures, documentation, reachable
services and tested recovery components are separate kinds of evidence.

The canonical K: checkout had substantial pre-existing changes, deletions and
untracked work. This audit preserves that working set; it does not stage, commit,
publish, remove caches, deploy code, restart services or command physical devices.

## Feature disposition

| Scope | Implemented evidence | Remaining work |
|---|---|---|
| Phase 0 evidence contract | Workbench schema, bounded imports, freshness/unknown handling; 10 tests and desktop/mobile browser checks pass | Authenticated production adapters and deployed collection |
| Phase 1 Today at Home | Local fixture/import prototype; combined saved Grocy, GardenKeeper, Mealie and Recomp routine selections verified | Authenticated production adapters, live placement and daily household acceptance |
| Phase 2A troubleshooting | Deployed 37-route catalog; local 20 tests and desktop/mobile smoke pass; September 15 Proxmox import recorded | Cross-service dependency extension and retained bounded incident history; existing report export is not retained history |
| Phase 2B recovery board | Local prototype separates backup, integrity and restore; component recovery records exist | Curated real evidence, deployed board/offline pack, recurring coordinated Hub backup and full application/integration restores |
| Phase 3 cooking/Recomp | Fixture meal availability; Hub read-only Grocy client; Recomp persistence/reliability checks pass | Representative stock/recipe/unit pilot and separately confirmed write workflows |
| Phase 4 workshop inventory | Evaluation contract | Record-owner choice, real zone inventory, QR labels, exports and restore proof |
| Phase 5 VentSys | Configuration, dashboard sources, command-free companion prototype and some bench work | Authenticated card/page bridge, remaining hardware/calibration, startup-motion diagnosis, physical installation and end-to-end safety acceptance |
| Household Hub knowledge features | Transcript persistence/chunking, lexical/vector/assistant adapters, search, recipe confirmation, export, integration contracts; 62 API tests and frontend production build pass | Worker remains a placeholder; background import/index jobs and MCP server are absent; external/voice workflows need their own acceptance |
| Printer | P1S/Bambuddy MQTT, HA dashboard and notification baseline recorded as commissioned | Camera/physical interlock acceptance and host-network exception remain separate |
| Monitoring | Grafana/Kuma/Influx/Telegraf/Loki/Alloy source and manuals; core endpoints reachable | Additional host-local collectors, CT114 update/Fail2ban path, phone notification receipt and independent outage proof |
| Immich curated export | Allow-list/no-delete implementation, state contract and tests staged | Owner-selected album/API credential, bounded live test, Jellyfin/review/backup proof before timer |
| Cameras | Three historically accepted ANNKE streams configured | Physical reconnection and fresh detection/notification/recording acceptance; fourth camera remains future scope |
| HACS and later services | HA baseline and selected integrations recorded; candidate list documented | Optional HACS items and six parked service candidates are not mandatory missing features |

The installation checklist's 42 entries / 36 Written / 6 Candidate is a dated
documentation inventory, not feature completion or a current rebuild certificate.
Obico ML API is a later addition outside that original count. Historical roadmap
dates and test records remain historical; current labels were reconciled below.

## Checks actually run

| Check | Result |
|---|---|
| Router `lint.py` and compiler recovery unittest | Clean lint; 4 tests pass |
| Troubleshooting `npm run check` | Syntax and 20 tests pass |
| Workbench `npm run check` | Syntax and 10 tests pass |
| Both static-app browser smoke suites | Desktop/mobile pass using temporary localhost servers |
| Mermaid `npm run verify` | 16 diagrams match maintained source and render; selected mobile views pass |
| Homepage `tests/access-contract.cjs` | Standalone/preview routes, origins and listener ownership pass |
| Recomp `tools/test_frontend.cjs` / `test_reliability.py` | Frontend contract suite and 7 temporary-DB backend tests pass |
| Transfer Portal pytest | 55 pass, 2 platform-specific skips, including 7 session-secret regression cases |
| Hub `build:web`, API pytest, Ruff | Production build, 62 API tests and lint pass |
| Monitoring snapshot + exporter pytest | 10 tests pass |
| Offline health-check PowerShell tests | 11 HTTP/DNS and 6 transport-classification scenarios pass |
| WSL GardenKeeper and MediaMTX backup tests | 7 + 2 isolated failure-path tests pass |
| Repository-audit regression test | Nested Git source, ignored cache and fenced-example resolution pass |
| Metadata/source scan | 890 existing candidate files at baseline, including nested Hub source; 99 Python AST, 68 JSON and 105 YAML syntax checks pass |
| Additional script syntax | 41 own JavaScript files, 15 PowerShell files and 23 shell scripts pass |
| `main/_verify.ps1` | Prerequisite checks pass; new optional `-RepositoryAudit` runs the read-only inventory |
| npm registry audits | Hub and Mermaid lockfiles report zero advisories on October 2 |

Python dependencies used for unavailable backend tests were installed in isolated
directories outside the vault. Hub npm dependencies came from `npm ci` with
install scripts disabled; its generated build remains ignored. These tests use
the declared requirements, not the exact deployed Python environment. Initial
Windows backup failures were missing `/bin/sh`; their WSL reruns pass. Initial
browser sandbox launch failures were resolved by approved local execution.
Deprecation warnings remain in Recomp UTC timestamps and the isolated Hub
Starlette/httpx test adapter. No Python advisory scan, full ESPHome compilation,
fresh HA configuration validation, full Linux semantic/security lint, penetration
test or end-to-end test of every deployed service was performed.

## Code and file findings

1. **Fixed in source: predictable Transfer Portal session secret.** Missing
   configured secrets previously fell back to a known development string. A
   forged signed session could bypass login in that configuration. Startup now
   fails for missing, empty or shorter-than-32-character secrets. Tests isolate
   import-time app initialization from real service state. Native installation
   already generates a secret file. This fix is not deployed; current live
   secret configuration was not inspected and no credential was rotated.
2. **Fixed: Hub lint.** Five long-line errors in its Grocy client were repaired
   without behaviour changes; Ruff and all 62 API tests pass afterward.
3. **Fixed: current Obico manual link.** Its stack reference was one parent
   directory short. No unresolved current inline Markdown links remain in the
   scan. Four historical audit links remain separately reported.
4. **Repository hygiene:** 20 tracked paths are already deleted in the owner's
   working set. Most concern the documented Mermaid consolidation; no deleted
   source was silently restored. Ten non-empty exact-hash duplicate groups are
   review candidates, including deliberate release/source copies and templates.
   No private-key PEM headers were found by the narrow source scan; this is not
   a comprehensive secret-leak certificate.
5. **Wiki navigation:** eleven unresolved/ambiguous wikilinks were reported at
   baseline, mainly undeveloped methodology pages and append-only historical
   log entries. This does not justify creating unrelated product integrations.
6. **Reproducibility:** `tools/repository-audit/audit.py` inventories candidate
   files using each Git repository's ignore policy, checks Python/JSON/YAML
   syntax, local Markdown links and config/script wikilinks, and reports duplicate
   hashes/deleted paths. It ignores fenced examples and never prints secrets.
   Link/duplicate/deletion findings are advisory; syntax/unreadable files fail.
   YAML syntax checks require PyYAML. Dependency trees are excluded, and the
   scanner does not estimate total physical cache size or validate every config's
   runtime schema. JSON evidence is kept outside the vault.

## Fresh read-only live evidence

At **10:37 BST on October 2**, the Windows health collector returned 11 pass /
1 fail / 0 unknown. Router, HA, Frigate host SSH, Docker host, Homepage,
Bambuddy, MQTT TLS listener, Grafana, Kuma, llama.cpp and OMV NFS respond.
Camera 1 RTSP fails consistently with deliberate physical disconnection.
HTTP checks are reachability observations; they do not establish certificate
trust, login/user workflows, data consistency or a new restore acceptance.

OMV `omv-lan` BatchMode key login succeeds. Read-only `smartctl -H -A` reports
all five disks passed, temperatures 30–47 C and no reported pending or offline
uncorrectable sectors. RAID1 md0 has both members `[UU]`; an existing consistency
**check** is 46.7% complete. It was not started, stopped or tuned by this audit.
One current member reports lifetime UDMA CRC count 1. Device-name attribution
differs from the September 30 sample, so do not infer a counter increase or a
new cable fault without matching stable disk identity. SMART passed is not
a self-test, media integrity proof or backup restore proof.

## Next work without owner input

1. Diagnose CT114's package path, metadata age and Fail2ban state read-only.
   Distinguish today's state from the September 7 failure before preparing a
   bounded update/routing repair. Do not enable services or reboot from a probe.
2. Prepare recurring coordinated Household Hub backup logic and failure-path
   tests against isolated store/manifest fixtures. The existing checkpoint is
   one-off; enabling a live timer/cold stop still needs a maintenance decision.
3. Import curated, dated recovery records into the local Workbench and prepare
   its offline emergency export. Keep backup success, integrity and isolated
   restore separate; add no credentials or new service.

This audit itself closes the repeatable file/code-audit work and fresh OMV SMART
evidence task. Phone receipt, real stock/workshop data, album selection,
account/recovery choices, hardware actions and disruptive maintenance still need
the owner. None of those gates should be marked complete from automated checks.

## Same-day independent follow-up

CT114 diagnosis/source preparation is complete: no proxy, absent Fail2ban,
expired June metadata, logged native-cache UFW rejection and upstream503 are
confirmed. A dry-run-default host-only permission helper/proxy template and
[bounded repair procedure](../procedures/ct114-package-path-repair.md) are staged;
five isolated helper/backup tests pass. No live repair occurred.

Seven curated historical recovery records now load in the Workbench and produce
a scope-preserving offline index. Its unit suite is now12 passing tests;
dedicated desktop/320px import checks pass. Partial boot/component exercises
do not establish full recovery, and no new backup freshness was invented.
Recurring coordinated Hub backup preparation is also complete: ten isolated
tests cover failures and a real archive round trip; service/timer syntax is
verified with temporary Docker/executable stand-ins. Live read-only preflight
passes for the exact NFS mount, five running containers and three owned volumes,
with no other running container using those volumes. Source remains undeployed;
manual checkpoint/restore and recurring outage acceptance remain open. See the
[activation and rollback procedure](../procedures/household-hub-coordinated-backup.md).

Saved Grocy overview preparation is also complete in the local Workbench:
sixteen unit tests and desktop/320px fresh/stale/unavailable imports pass. The
converter targets the existing recovered Hub overview response, bounds inputs,
excludes notes/unknown fields, preserves best-before semantics and refuses output
overwrite. Synthetic acceptance is separate from a real export pilot, live
adapter and deployment; see the [release contract](../procedures/read-only-product-release-plan.md).

The seven-system selected-runbook bundle now includes13 canonical documents,
clickable index, link manifest and17 checksummed files. Twenty unit tests and
independent standard checksum verification pass;54 omitted references are
disabled/labelled rather than silently implying a full rebuild kit. Generated
output is outside the vault. This advances offline documentation portability,
not live backup freshness or full-estate application recovery.

Dashboard8094 IPv6 preflight/source preparation is also complete: live bind is
IPv4-only, bridge IPv6 disabled, and rule32 Tailscale RETURN/rule33 DROP counters
remain zero at inspection. Windows and monitoring IPv6 probes fail without
establishing complete audience-path denial. A local dedicated8094 DROP replaces
its source allow-loop entry and passes isolated rule-emission/order checks;
all16 system-helper tests pass. Live policy/persistence remain unchanged and
maintenance-gated. The full tracked ruleset must not be reloaded as a shortcut
because it flushes both chains and lacks the complete live IPv4 dashboard policy.

OMV host-local collector preparation now passes six isolated tests and a live
one-off `omv-health/1.0` observation. It reads load/memory, five disks, md0,
exact UUID mounts and four daemon states, preserving standby/missing-data
unknowns and SMART warnings. Five health results pass,30–42 C; lifetime CRC1
and a separate historical threshold flag remain explicit. RAID is currently
nondegraded with idle sync. Source omits raw serials/WWNs and uses explicit ATA
power-check guards. No collector schedule, credential, firewall, metric shipping
or NAS panel was deployed; see the
[collector contract](../procedures/omv-health-collector-preparation.md).

## October 4 saved-task implementation

The local Workbench now imports saved GardenKeeper selections from a verified
API task shape: pending-only display, bounded rows, explicit observation
freshness and UTC due times, with notes/identifiers/recurrence omitted. Shared
URL validation also rejects credential-like fragments, and list spacing is
corrected at mobile width. Twenty-five unit tests and three desktop/320px
browser suites pass, including Grocy and recovery regressions. Schema inspection
did not fetch household task records. Real-data pilot and live deployment remain
open; see the [release plan](../procedures/read-only-product-release-plan.md).
The final Git-aware recheck covers985 files (78 JSON,121 Python,105 YAML and349
Markdown), with no syntax or navigation findings and no generated candidates.
The previously reviewed20 missing tracked paths and10 duplicate groups persist.

## Canonical sources (audit inputs)

October4 navigation/file-disposition recheck repairs the four copied historical
Markdown targets and all11 unresolved wiki links. Seven missing methodology
stubs are source-backed and explicitly separate optional ideas from deployed
tools; raw sources and historical wiki log entries remain untouched. The wiki
also qualifies its overly broad RAG accumulation claim against the original
paper and canonical Household Hub state.

The audit still reports20 deleted tracked paths and10 duplicate groups. These
are preserved, not hidden or staged:17 deleted paths belong to the old Mermaid
layout, whose README defines `apps/mermaid-viewer/src/`, `dist/` and root stack
files as the consolidated source/release. The retained release independently
passes all five SHA256SUMS checks and the browser suite for16 canonical diagrams,
including its mobile zoom/fit checks. The deleted servo SCAD copy has the same
Git blob hash as the retained `.scad` (`909972740bed745800b54a1c4ebcb8d68b8ebede`).
Recomp's README identifies standalone `docker-compose.yml` as canonical rather
than the deleted snippet. The remaining root camera snapshot deletion is left
as a pre-existing working-tree change; no intent or replacement is inferred.
Duplicate groups include release/source pairs, stack release material and small
placeholder/config files; no automatic deletion or claim of a clean Git tree.

The full canonical TransferPortal suite is also reproduced October4 with its
existing external dependencies:62 passed,2 Windows symlink skips. The earlier
missing-`itsdangerous` collection limitation is resolved locally. Production
hardening remains undeployed; local suite success does not refresh its live
acceptance. The navigation recheck covers957 files, including71 JSON,121 Python,
105 YAML and348 Markdown files, with no syntax/current/historical Markdown-link
or unresolved-wiki findings. Existing deleted paths/duplicate groups remain.

October4 local OMV preparation advances this item without changing delivery
status: atomic publication, stdout conversion and consumer input fragments are
prepared;18 Linux tests and five exact Telegraf parser cases pass. Three guarded
current-state/unit Flux queries pass19 synthetic cases (32 actual executions)
without reading or writing buckets. Newer invalid/stale evidence, elapsed age,
missing readings and failed producer state cannot become retained healthy data.
Dedicated consumer permissions, authenticated shipping, schedule and Grafana
UI/alerts remain unaccepted. The existing collector procedure holds the complete
manual acceptance/rollback sequence, with query artifacts outside provisioning.

- [Task list](../../TO-DO.md)
- [Product roadmap](../procedures/household-workshop-operations-roadmap.md)
- [Monitoring roadmap](../procedures/monitoring_roadmap.md)
- [HA enhancement candidates](../install/reference/hacs-enhancement-roadmap.md)
- [VentSys TLS roadmap](../../ventsys/integration-process/ventsys_implementation_roadmap.md)
- [Hub source roadmap](../../apps/household-hub-recovery/docs/plans/roadmap.md)
- [Read-only release contract](../procedures/read-only-product-release-plan.md)
- [Current live inventory](../reference/current-live-state.md)
- [Installation coverage](../install/INSTALL-TO-DO.md)

## October 4 import-state audit follow-up

An older asynchronous file read can no longer replace evidence after Clear,
Load demonstration or a newer import. Those actions invalidate pending reads;
obsolete failures also leave the current message unchanged. A newer malformed
or oversized selection still preserves the last accepted evidence and its error
message instead of allowing an older read to appear later.

The summary counters are explicitly labelled as dependency counts; zero does
not mean there are no garden tasks or household observations. All25 unit tests
and the three desktop/320px browser suites pass. Controlled delayed-read checks
cover Clear, demonstration, newer success, newer malformed input, newer
oversized input and an obsolete read failure. Mobile layout was reviewed.
This remains local source verification, with no runtime deployment or data writes.

The timestamp follow-up uses one strict `evidence-time.js` validator across
health, Grocy and GardenKeeper imports. Hours/minutes/seconds, real calendar
dates and offsets up to14:00 are validated before JavaScript conversion;
24:00 rollover, invalid leap days and any future observation cannot certify
current health or backup freshness. Source fractional seconds (up to six digits)
are accepted and displayed at JavaScript millisecond precision. Legacy health
snapshots still require the actual explicit collection-time offset. All28 unit
tests and three desktop/320px browser suites pass, including direct picker and
recovery-view assertions for invalid and slightly future health observations.
No collector, live service or backup schedule was changed.

October4 saved Mealie verification advances local Today at Home only: explicit
calendar selection from the verified paginated schema, bounded display and
private payload omission, with stale/unknown states and no ingredient inference.
All33 unit tests and three desktop/320px browser suites pass. The public schema
read fetched no household records; real-data pilot and integrated hosting remain
open. See the [release plan](../procedures/read-only-product-release-plan.md).

October4 combined saved-source verification now passes38 unit tests and three
browser suites at1440/320px. A single explicit household bundle preserves each
source observation, isolates unavailable cached rows and rejects malformed
bundles atomically. Three reserved source summaries survive operation caps.
This advances local composition only; genuine pilot, Recomp, diagnostic/recovery
composition and live release remain open. No API requests or source writes.

October4 saved Recomp and four-source composition passes45 unit tests and three
browser suites, preserving weekday/move semantics and unknown completion or
readiness. No personal records were fetched and no source writes occurred.
Older three-source bundles remain supported; diagnostic/recovery composition,
full programme coverage, household pilot and live release are still open.
