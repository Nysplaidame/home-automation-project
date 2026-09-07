---
title: Household, Workshop and Operations Product Roadmap
description: Phased roadmap for daily household workflows, workshop operations, diagnostics, resilience, and VentSys commissioning
tags: [roadmap, household, workshop, monitoring, resilience, ventsys]
created: 2026-09-05
modified: 2026-09-06
type: product-roadmap
status: active
---

# Household, Workshop and Operations Product Roadmap

This roadmap turns the existing household services, operational tooling and
planned physical integrations into coherent daily workflows. It is a planning
document: an entry authorises discovery and design only. Each implementation
still needs a bounded change, backup, rollback and acceptance plan.

The order reflects the actual estate on 2026-09-05. Docker-host, GardenKeeper,
Grocy, Mealie, Household Hub, Recomp Tracker, monitoring and the staged
Troubleshooting Dashboard are usable foundations. The P1S is not commissioned,
the Zyxel/cameras are intentionally disconnected, and VentSys hardware remains
unbuilt. Do not make those deferred systems prerequisites for work that can be
useful now.

## Product boundaries

- **Home Assistant** coordinates and presents home state. It remains the only
  automation authority for safety paths.
- **GardenKeeper, Grocy, Mealie and Recomp Tracker** retain their existing
  records of garden work, food inventory, recipes/meal plans and nutrition/
  workouts. A new view links or reads those records; it does not duplicate them.
- **Household Hub** is the integration and research layer. Its Home Assistant
  tools stay read-only unless a separately designed, confirmation-gated action
  is accepted.
- **The Troubleshooting Dashboard and recovery views** collect and explain
  evidence. They must not run shell commands, restart services, alter firewall
  policy, delete data, restore guests or dismiss an alert.
- **VentSys safety logic** stays in reviewed HA/ESPHome/MQTT paths. No local
  model, assistant tool, simulator, portal or commissioning screen may invoke
  an emergency, power-cutoff, fan or valve command without the existing
  safety-control review and a physical acceptance test.
- New services need a named owner, source-scoped network policy, explicit
  Docker allocation, authentication design, backup/restore proof, monitoring,
  direct-navigation acceptance and a documented rollback. A Homepage card is
  added only after those gates pass.

## Delivery order

| Phase | Initiative | Readiness | First useful outcome |
|---|---|---|---|
| 0 | Home-operations evidence contract | Local POC complete | A versioned, timestamped read-only fixture that can state `unknown`, `planned offline` and `failed` honestly. |
| 1 | Today at Home | Local POC complete | One daily page for due garden work, expiring stock, planned meals, training and actionable infrastructure issues. |
| 2 | Dependency-aware troubleshooting and recovery readiness | Local POC complete; live extension gated | An incident points to plausible shared dependencies; recovery evidence distinguishes backup, integrity and restore proof. |
| 3 | Cook what we have and Recomp shortcut | Local POC complete; live data gated | Reviewed meal suggestions that use real Grocy stock without automatic stock changes or diet logging. |
| 4 | Workshop inventory and drawer map | Ready to evaluate | Find parts, tools and project allocations by location, label or QR code. |
| 5 | VentSys commissioning companion | Local POC complete; hardware-gated | Bench and installation evidence for each device, with a command-free simulation mode. |
| Later | Complementary capabilities | Individually gated | Targeted additions that extend the same operating model. |

### Local proof-of-concept update — 2026-09-06

`apps/home-operations-workbench/` now provides a static, import-only proof of
concept for phases 0, 1, 2, 3 and 5. It includes a schema 1.0 normalizer,
safe demonstration fixture, Today at Home, possible shared-dependency groups,
separate backup/integrity/restore evidence, meal availability, a VentSys
visual-only commissioning checklist, and local evidence exports. Model and
desktop/mobile browser smoke tests passed on 2026-09-06.

This is not a deployed service and does not connect to Home Assistant,
Household Hub, Grocy, Mealie, GardenKeeper, Recomp, MQTT, or a browser data
store. A live adapter, hosting decision, authenticated collection, health
monitoring, backup/restore path and acceptance evidence remain separate work.

## Phase 0 — Home-operations evidence contract

September7 continuation: offline Windows/Proxmox health imports now normalize
known statuses, require reliable timestamp evidence, mark observations older
than 36 hours stale and preserve unknown integrity/restore states. The file
picker and non-overwriting CLI converter are locally verified. Authenticated
collection, service placement and live acceptance remain separate gates.
Recovery tabletop reasoning is recorded in the existing July audit test cards;
no live outage or restore exercise was performed.

Define a small, versioned read model before adding any cross-service screen.
It should combine imports from the existing Windows and Proxmox health-check
JSON, selected app APIs and manually recorded evidence. Every item needs:

- source and observation timestamp;
- status (`healthy`, `failed`, `unknown`, `planned_offline` or `stale`);
- a link to the owning service or runbook; and
- enough dependency metadata to explain why a shared host, mount, DNS route or
  network path may be relevant.

Do not infer health from an absent value, store credentials in the browser, or
turn an observed correlation into a diagnosis. Begin with saved fixture files
and schema/contract tests. Direct authenticated collection is a later, separate
change with least-privilege service credentials.

## Phase 1 — Today at Home

Create a mobile-friendly daily view, preferably as a Household Hub surface,
that answers “what needs attention today?” rather than becoming another system
of record.

### First release

- GardenKeeper tasks due or overdue.
- Grocy items nearing expiry and the active shopping list.
- Mealie's selected/planned meal, if one exists.
- Recomp Tracker's scheduled workout or reminders.
- A compact, filtered list of actionable service issues from Phase 0.

Each card deep-links to the owner application. V1 offers no completion,
inventory, shopping-list, recipe-import or home-control button. It must show
when a source is unavailable or stale instead of omitting it silently.

### Acceptance gate

Use representative fixture data for every source, a deliberately stale source
and an empty-data state. Check keyboard navigation and 320 px mobile layout.
Verify that no browser request exposes an integration token and that each card
opens the correct owner application.

## Phase 2A — Dependency-aware troubleshooting

Extend the staged Troubleshooting Dashboard only after its outstanding real
Proxmox snapshot acceptance is complete. Add a tracked dependency graph derived
from the service and access matrices, initially covering Proxmox, VM 103,
docker-host services, OMV mounts, DNS and the monitoring VM.

An incident should say, for example, that several unavailable VM 103 services
share a host or that backup freshness and a mount warning share OMV storage. It
must call these *possible shared dependencies*, link to evidence and retain the
existing symptom-led diagnostic steps. It must never auto-remediate or conceal
unrelated failures behind a single guessed root cause.

Add a local incident history containing imported snapshot IDs, timestamps,
operator notes and resolution links. It must be explicitly separate from raw
logs, have bounded retention, exclude secrets and be exportable as a concise
incident report.

## Phase 2B — Recovery readiness board

Add a read-only recovery view alongside troubleshooting. For every critical
service, display separately:

1. newest successful backup;
2. latest integrity or archive test;
3. latest isolated restore exercise; and
4. the recovery runbook, dependency order and a clear “not yet proven” state.

Generate a small offline emergency pack for the management workstation and,
when deployed, the garage Pi. It contains runbook links, recovery order and
last-known evidence; it contains no private keys, passwords, backup payloads
or automatic restore facility. A recovery score must never imply a restore was
tested when only a backup job completed.

## Phase 3 — Cook what we have

Use Household Hub's existing read-only Grocy overview and its reviewed Mealie
workflow to suggest recipes that make use of real stock nearing expiry. Start
with a narrow pilot: a small set of recipes, one household location and
explicit unit/quantity assumptions.

- Suggestions show source ingredients, missing ingredients and uncertainty.
- Selecting a recipe opens Mealie; it does not import a recipe, create a meal
  plan, add a shopping-list line or consume Grocy stock automatically.
- A later, separate Recomp shortcut may log an explicitly selected serving of
  a saved recipe. It must show the portion and macro calculation before save,
  retain the historical nutrition snapshot and never imply that a planned meal
  was eaten.

This work is gated on representative Grocy stock data. Empty or untrusted
inventory produces an honest “no suggestions yet” state, not invented meals.

## Phase 4 — Workshop inventory and drawer map

Evaluate a dedicated household inventory base such as HomeBox against a small
project-specific application before adopting either. The choice must support:

- locations down to cabinet, drawer, bin and shelf;
- parts, tools, consumables, photos, datasheets and project allocations;
- printable QR labels that open a local authenticated record;
- quantities with a “needs count” state rather than false precision;
- source links to Gridfinity layouts, wiring diagrams and the VentSys bill of
  materials; and
- export plus isolated restore proof.

Begin with one workshop zone and a small parts set. The initial scope is
read/write inventory only; no automatic purchases, stock deductions or printer
control. Filament/AMS linkage remains a later P1S follow-up after Bambuddy,
MQTT TLS, HA and printer acceptance are complete. Avoid deploying a second
filament database until the existing Bambuddy inventory capability and its
backup/restore behaviour have been assessed.

## Phase 5 — VentSys commissioning companion

Build a separate companion for hardware rollout, not a replacement dashboard.
Each physical device gets a commissioning record with board identity, firmware
revision, wiring photographs, sensor addresses, calibration/baseline data,
MQTT/TLS test result, restart-state observation and signed-off bench/install
checks.

V1 includes a clearly labelled, command-free simulator that replays example
sensor and valve states for dashboard review. It cannot connect to an MQTT
broker or live HA APIs. Bench tests and physical installation tests remain
distinct, and the companion must not call an enclosure safe until the existing
end-to-end emergency-cutoff and fail-safe acceptance evidence is recorded.

## Complementary capabilities

These belong on the roadmap because they reuse the same data, workflows and
operational boundaries. Evaluate them one at a time after the phases above.

| Capability | Outcome | Gate |
|---|---|---|
| Network performance diary | Preserve wired and Wi-Fi baseline tests, router radio observations, ISP tests and incidents so throughput investigations have comparable evidence. | Use a wired reference plus explicit Wi-Fi signal/client metadata; scheduled internet tests alone do not diagnose Wi-Fi. |
| Configuration-drift viewer | Compare tracked intent, selected live evidence and last accepted state for DNS aliases, VM resources, Docker networks and service versions. | Show differences as evidence for review; never overwrite live configuration. |
| Garden-to-kitchen workflow | Review a GardenKeeper harvest, propose a Grocy stock addition, then surface compatible Mealie recipes. | Quantity/unit mapping and confirmation at every write boundary. |
| Garage session journal | Associate repair/build notes, part usage, photographs and manually selected MediaMTX video timestamps with a project. | Keep private clips locally scoped; no automatic video or face analysis. |
| Maintenance calendar | Track filters, printer servicing, sensor calibration, fan inspections and appliance maintenance from explicit schedules. | Runtime-based reminders wait for trusted telemetry; safety maintenance needs its own acceptance checklist. |
| Storage growth and retention preview | Forecast NAS, recordings, photo, download and backup capacity from existing metrics and measured growth. | Preview only; no automatic deletion or retention changes. |
| Household document archive | Add Paperless-ngx once its existing sensitive-data, local-HTTPS, export and isolated-restore gates are passed; link manuals/warranties to workshop inventory. | No real household documents before the harmless-document and restore proof. |
| Assistant job status and receipts | Make transcript/indexing and confirmed cross-service actions visible as queued, running, failed or completed with provenance. | Bounded logs, secret redaction, retry rules and no silent background writes. |
| Power continuity plan | Add a UPS/NUT evaluation, runtime evidence and orderly-shutdown dependency map for Proxmox, OMV and networking. | Hardware sizing, controlled low-risk test and explicit recovery order before unattended shutdown is enabled. |

## Standard implementation gate

Every roadmap item starts with a short design note that names the user outcome,
owning records, caller/callee contracts, data retention, authentication,
network path, backups, rollback and success/failure states. Implement against
fixtures first. For a live release, prove the direct user flow, negative access
path, monitoring, backup and restore method appropriate to its data. Update the
service matrix, access matrix, current live state and wiki only after that
evidence exists.

## First build candidates

1. **Complete:** define the Phase 0 evidence schema and fixtures in the local
   workbench proof of concept.
2. **Complete locally:** build Today at Home, dependency/recovery views, meal
   availability and a command-free VentSys checklist from fixture evidence.
3. Decide whether a future live view belongs in Household Hub or a separately
   placed service, then define adapter contracts and least-privilege access.
4. Complete the Proxmox snapshot acceptance before extending the staged
   Troubleshooting Dashboard with live diagnostic or recovery evidence.
5. Seed a small, accurate Grocy stock pilot before using live recipe data.
6. Run the workshop-inventory evaluation with one cabinet or Gridfinity zone.
