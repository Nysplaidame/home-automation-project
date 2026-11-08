---
title: Read-only household operations release plan
description: Bounded delivery contract for Today at Home and recovery readiness
tags: [household, product, recovery, read-only]
created: 2026-09-18
type: release-plan
status: proposed
---

# Read-only household operations release plan

## Outcome and scope

Deliver one useful, mobile-friendly, read-only Household Hub surface before
adding another service. The first release combines **Today at Home** with a
small recovery-readiness summary. It links to the owning applications; it does
not become a system of record, invoke Home Assistant, write to Grocy/Mealie/
GardenKeeper/Recomp, or conceal a missing source.

The existing [Home Operations Workbench](../../apps/home-operations-workbench/README.md)
is the local fixture/saved-import reference implementation. The live
[Troubleshooting Dashboard](../../apps/troubleshooting-dashboard/README.md) remains
a separate diagnostic surface and is not a source of authority for household data.

## Placement and ownership decision

Use the owner-authorized local Household Hub recovery repository as the source
baseline for future bounded changes. Its original repository/history remains
unknown, its recovery provenance must stay visible, and it has no remote. Keep
the release in the Workbench as an import-only proof until the deployment owner,
migration/restore contract, adapter boundary, and release approval are explicit;
do not deploy a second web service merely to host it. This avoids inventing a
parallel authentication, backup, monitoring, and network surface.

| Card | Authoritative source | V1 action | Missing/stale behaviour |
|---|---|---|---|
| Garden tasks | GardenKeeper | Deep link only | Show source unavailable or timestamp |
| Expiry/shopping | Grocy | Deep link only | Do not infer stock from absence |
| Planned meal | Mealie | Deep link only | Show no planned meal honestly |
| Training | Recomp Tracker | Deep link only | Show source unavailable or timestamp |
| Operations | Versioned evidence import | Link to diagnostic/runbook | Preserve `unknown`, `stale`, or `planned_offline` |
| Recovery readiness | Curated recovery evidence | Link to runbook | Keep backup, integrity, and restore proof separate |

## Adapter contract

Each future server-side adapter produces a bounded, versioned record compatible
with the Workbench schema. It must include source name, observation time with
offset, source status, a safe owner-application link, and only the display
fields required by its card. Credentials remain server-side; the browser never
receives an integration token, raw command output, or private record payload.

Adapters may fail closed into an explicit unavailable state. They must not
substitute fixture data, cached success, or guessed health for a failed source.
Collection is read-only, source-scoped, rate-limited, and logged without
secrets or personal content.

## Delivery sequence

1. Recover the Hub repository/revision and document its deployment, migration,
   backup, rollback, and owner boundary.
2. Choose the minimum fields and least-privilege credentials for one source at
   a time; start with a saved GardenKeeper or Grocy export rather than a live
   browser call.
3. Implement the normalizer/adapter against representative, stale, empty, and
   unavailable fixtures. Preserve the current Workbench accessibility and
   narrow-screen behaviour.
4. Add the recovery summary from curated evidence only. It must show the newest
   successful backup, latest integrity check, latest isolated restore, and a
   runbook link as four independent facts.
5. Prepare a bounded deployment change with source-scoped firewall policy,
   server-side secrets, monitoring, backup/restore, rollback, and direct-link
   acceptance. Owner approval is required before live credentials or hosting.

## Non-goals and release gates

V1 has no completion buttons, stock adjustments, shopping-list writes, recipe
imports, workout logging, home-control actions, background notifications, or
automatic remediation. A later write capability needs its own confirmation,
audit, and rollback design.

Before a live release, verify keyboard operation, 320 px layout, stale and
empty states, direct links, absence of browser credentials, least-privilege
denial behaviour, monitoring, and a data-appropriate backup/restore path.
These are release gates, not claims that they have already passed.

## October 2 local recovery slice

The existing Workbench now accepts a curated seven-system snapshot at
`apps/home-operations-workbench/evidence/recovery-2026-10-02.json` through its
file picker. Twelve unit tests and desktop/320px browser import checks pass.
Its `recovery-pack.mjs` exporter adds scope notes and validated vault-relative
source/runbook paths to an offline index, without overwriting an existing file.
Historical backups are explicitly stale, and VM102 boot plus Hub/GardenKeeper
component exercises retain unknown full-system restore status.

This completes one local import/export proof. It does not establish fresh
backup evidence, full estate/runbook-pack coverage, a live adapter, Today data,
recurring coordinated Hub backups or deployed product acceptance. The existing
hosting/credential/maintenance gates still apply.

## October 2 portable runbook pack

`recovery-bundle.mjs` now produces an offline-readable pack for the seven curated
systems: 13 selected canonical Markdown documents, clickable recovery index,
manifest, checksums and completion marker. Proxmox, OMV, backup strategy, current
state and Hub checkpoint preparation are included as selected dependencies.
Commands/code blocks remain unchanged. Fifty-four omitted inline references are
disabled/labelled and listed alongside bundled and external links; heading/HTML/
reference-style links remain outside validation. This is selected runbook
coverage, not complete estate, data, image or configuration recovery.

Twenty unit tests pass, including copied/moved-pack use without the original
test vault, tamper/extra-file detection, protected path/overwrite bounds and
Windows junction rejection. The real pack's17 checksummed files also pass standard
`sha256sum -c SHA256SUMS`. Generated output stays outside the vault; current
historical evidence and maintenance gates are not advanced by this packaging.

## October 2 saved Grocy slice

`apps/home-operations-workbench/import-grocy.mjs` now converts a versioned manual
envelope around the existing Hub `stock`/`shopping_list` response to Today food
and shopping observations. It copies only bounded display fields, excludes
shopping notes/unknown payload, filters unsafe links and preserves best-before
semantics without inferring use-by dates or recipe suitability. A failed source
produces no stock; missing/ambiguous/future observation time is unknown and
records over 36 hours are stale at conversion. Limited or empty rows never
establish complete inventory. The existing file picker imports either converter
output or the original `grocy-overview/1.0` envelope directly, recalculating
freshness for direct source imports. BOM exports and malformed/oversized input
error handling are verified; failed imports retain the previously labelled
evidence and Clear removes it. No extra page or service was added.

Sixteen unit tests, CLI overwrite/size/error checks and desktop/320px imports
for fresh/stale/unavailable synthetic snapshots pass; the narrow layout was
visually inspected. This completes saved-response contract preparation, not a
real-data pilot or live adapter. There was no service call, credential use or
deployment. Regenerate/reimport dated evidence as it ages. Hosting and genuine
source acceptance remain open. Format and command are in the
[Workbench manual](../../apps/home-operations-workbench/README.md).

## October 4 saved GardenKeeper slice

The local Workbench now accepts a `garden-tasks/1.0` envelope in its existing
picker. The GardenKeeper read-only task response schema was verified through
`/openapi.json`; only schema metadata was fetched, not personal task records or
credentials. Up to50 pending tasks from a bounded saved selection are displayed
with independent freshness and UTC due-time validation. Completed/cancelled
titles, notes, plant/zone identifiers, recurrence rules and unknown fields are
omitted. Pending is **Needs review**, never a claim of completion or garden
health; empty selections do not establish complete task coverage.

All25 unit tests and dedicated browser checks at1440/320px pass, including BOM,
stale/future, empty/unavailable, failed/oversized import retention and Clear.
The shared URL boundary now also rejects credential-like fragments. No live
fetch, task actions, source writes, persistence, hosting or credentials were
introduced. A real-data pilot, application-link acceptance and integrated Hub
release remain open. Contract/example and repeatable browser test:
[[../../apps/home-operations-workbench/README]].


## October 4 saved Mealie slice

The local Workbench now accepts `mealie-plan/1.0` around a saved paginated
Mealie v3.19.2 `GET /api/households/mealplans` response. Public schema inspection
fetched no household records or credentials. The required explicit calendar
selection filters entries before the50-row cap; dates retain source calendar
meaning, independently of observation freshness. Notes, identifiers, recipe
payloads and pagination links are excluded. Planned meals remain Needs review,
with ingredient availability and food safety unknown; empty or partial pages
do not certify complete coverage. Unavailable sources omit cached meals.

All33 unit tests and the three desktop/320px browser suites pass, including
fresh/stale/future, empty/unavailable, BOM and failed-import preservation.
Narrow-screen screenshots were inspected. The existing picker replaces its
current workbook; multi-source combination, real-data pilot, live adapters and
hosting remain open. No source writes or service changes occurred. The format
and example are in the [Workbench manual](../../apps/home-operations-workbench/README.md).


## October 4 combined saved-source slice

The Workbench now accepts `household-sources/1.0`, containing exactly one
GardenKeeper, Grocy and Mealie envelope. Explicit unavailable sources hide
cached rows; independent source times/statuses survive the common import clock.
Unknown, duplicate, missing or malformed sources reject the entire bundle while
preserving the previous evidence. Input order cannot change allocation. All
three source summaries are reserved before the operation display cap; selected
shopping omissions are visible. No existing browser state is implicitly merged.

All38 unit tests and three desktop/320px browser suites pass, including mixed
freshness, source isolation, atomic failure and capped operations. Screenshots
were reviewed. This completes local three-source composition; real-data pilot,
Recomp, diagnostic/recovery composition, authenticated adapters and live hosting
remain open. No API calls, credentials or source writes were added. Example and
bounds are in the [Workbench manual](../../apps/home-operations-workbench/README.md).


## October 4 Recomp and four-source composition

Saved `recomp-plan/1.0` projects the tracked Recomp routine schedule convention,
including one-off moves, for an explicit calendar date. It imports names and
move origins only; health/exercise/session payloads do not enter the Workbench.
Completion/readiness remain unknown and empty routines do not imply rest or
complete training coverage. The separate calisthenics programme is outside this
selection. No live personal records were fetched or modified.

`household-sources/1.1` adds exactly one Recomp envelope to the existing three
source bundle. Version1.0 retains its original contract. Four reserved source
observations survive operation caps; each source keeps its own freshness and
unavailable state. All45 unit tests and three desktop/320px browser suites pass,
including source moves, atomic rejection and mixed freshness. Narrow screenshot
review passes. This completes saved four-source Today composition; genuine
household pilot, diagnostic/recovery composition, live adapters and hosting
remain open. The [Workbench manual](../../apps/home-operations-workbench/README.md)
contains format, selection, privacy and scheduling limits.

## Related work (canonical references)

- [Product roadmap](household-workshop-operations-roadmap.md)
- [Roadmap assessment](../audits/2026-09-16-roadmap-assessment.md)
- [Service matrix](../reference/service-matrix.md)
- [Household Hub source recovery register](household-hub-source-recovery-register.md)
- [Access matrix](../reference/access-matrix.md)

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
