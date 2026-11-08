# Home Operations Workbench

This is a local, read-only proof of concept for the selected Household and
Workshop Operations roadmap work:

- Today at Home
- dependency-aware troubleshooting
- recovery readiness
- Cook What We Have
- VentSys commissioning companion

It deliberately has no live Home Assistant, Mealie, Grocy, GardenKeeper, Recomp,
MQTT, shell, or browser-storage integration. Importing data puts a normalized
copy into the current browser tab only. Closing or clearing the tab removes it.

## Evidence contract

The app accepts a JSON object with `schemaVersion: "1.0"`. The normalizer
supports these top-level areas:

- `today` with garden tasks, food, meals, workouts, and operations
- `dependencies` and `incidents`
- `recovery.systems` with separate backup, integrity, and restore evidence
- `cooking.candidates` with per-ingredient availability
- `commissioning.devices` and visual-only `commissioning.scenarios`

`fixtures/demo-operations.js` is the complete safe example. It is marked as a
demonstration and reflects no live service state.

The normalizer rejects unknown schema versions, caps collections, removes
non-HTTP(S) links, and omits imported detail that appears to contain a secret.
This is a presentation boundary, not a substitute for keeping credentials out
of source exports.

## Local verification

### Saved Recomp routine plans and four-source bundles

`recomp-plan/1.0` imports only the selected `data.routines` section from a
Recomp export, wrapped with an explicit observation time and calendar selection.
The tracked `static/app-v2.js` defines Monday=0 through Sunday=6 and one-off
`scheduleOverrides` keys as `source-date|routine-id`. No live personal records
were fetched. This is routine scheduling, not the entire calisthenics programme.

```json
{
  "schemaVersion": "recomp-plan/1.0",
  "status": "available",
  "observedAt": "2026-10-04T12:00:00Z",
  "planDate": "2026-10-04",
  "ownerUrl": "https://recomp.example.invalid/",
  "routines": {
    "items": [
      { "id": "routine-a", "name": "Sunday routine", "scheduleDays": [6] }
    ],
    "scheduleOverrides": {}
  }
}
```

Use an actual source observation time; copying an older export does not refresh
its evidence. Prefer a trimmed routines selection, excluding exercise and
version payloads, rather than placing a full personal backup in this envelope.
The existing picker limit is512KB. Missing schedule days mean unscheduled,
matching the source convention. Invalid/duplicate IDs, weekdays, calendar dates
or moves reject the selection. Routine items and move maps are each bounded
at5000. Moves suppress the original occurrence and add it on the target date;
orphan moves referring to removed routines are omitted and counted. Up to50
matching occurrences display after projection. Plan dates retain calendar meaning.

Names, selected dates and move origins are the only routine display fields;
identifiers, exercises, discomfort, loads, RPE, body measurements, diet, session
history and programme data are omitted. Completion and readiness remain unknown,
even for an old planned occurrence; it is not labelled missed or pending from
absence of session history. Fresh routine plans are Needs review, stale plans
stay stale, future observations stay unknown and unavailable sources omit cached
rows. No routine start, reschedule, completion or source write is possible.

For all four Today areas, use `household-sources/1.1`: the same three source
envelopes described below plus exactly one `recomp-plan/1.0` envelope. Version1.0
still requires exactly its original three sources. Four-source bundles reserve
four source observations, leaving up to46 shopping rows; omissions are explicit.
Independent freshness and atomic rejection remain unchanged. Each bundle
replaces the current workbook; diagnostic/recovery composition remains open.

All45 unit tests and three desktop/320px browser suites pass, including moves,
source isolation, stale training beside current meals, atomic rejection and
compatibility with the three-source bundle. Narrow screenshots were reviewed.
Genuine household acceptance, live adapters and integrated hosting remain open.

### Combined saved household sources

The existing picker accepts `household-sources/1.0` with exactly one envelope
for each verified household source. Use `status: "unavailable"` explicitly for
an unavailable source rather than omitting it. This synthetic example shows
calendar selection and source observations separately:

```json
{
  "schemaVersion": "household-sources/1.0",
  "sources": [
    {
      "schemaVersion": "garden-tasks/1.0",
      "status": "available",
      "observedAt": "2026-10-04T12:00:00Z",
      "tasks": [{ "title": "Water herbs", "status": "pending" }]
    },
    {
      "schemaVersion": "grocy-overview/1.0",
      "status": "available",
      "observedAt": "2026-10-04T11:00:00Z",
      "overview": {
        "stock": [{ "name": "Beans", "amount": 2 }],
        "shopping_list": []
      }
    },
    {
      "schemaVersion": "mealie-plan/1.0",
      "status": "available",
      "observedAt": "2026-10-04T10:00:00Z",
      "planDate": "2026-10-04",
      "plan": {
        "items": [{ "date": "2026-10-04", "entryType": "dinner", "title": "Bean stew" }]
      }
    }
  ]
}
```

`household-adapter.js` invokes the existing three source adapters with one
import clock, retaining each source's own observation, status, selection and
privacy rules. Bundle creation time never refreshes stale data. Input source
order does not change allocation. Unsupported, duplicate, missing or malformed
sources reject the whole import; the previous accepted evidence remains visible.
An unavailable source shows its observation without cached household rows.

Garden, food and meals retain their independent50-row bounds. Operations has
three reserved source summaries followed by up to47 selected shopping rows;
additional shopping display omissions are declared on the Grocy summary. The
512KB picker bound still applies to the entire file. Raw notes, credentials,
recipe payloads and pagination links never become combined output.

This explicitly replaces the current workbook, without incrementally merging
old browser state, persistence or live API calls. It includes no Recomp,
diagnostic dependencies, recovery evidence or ingredient matching. Unavailable
training/recovery stays absent; fresh stock cannot certify a meal's ingredients.
Real-data pilot and integrated Hub release remain open.

All38 unit tests and three browser suites pass. The existing
`node tests/browser-garden.mjs --regression` runner exercises mixed freshness,
coexisting household cards, unavailable source isolation, atomic rejection,
operation caps, overlapping reads and the older Grocy/recovery flows at1440/320px.
Desktop and narrow-screen screenshots were reviewed.

### Saved Mealie meal plans

The existing picker accepts `mealie-plan/1.0`. `mealie-adapter.js` uses the
Mealie v3.19.2 `GET /api/households/mealplans` paginated response shape verified
through public `/openapi.json` on October4. Only schema metadata was fetched;
no tokens or household meal records were used. Wrap a deliberately saved page:

```json
{
  "schemaVersion": "mealie-plan/1.0",
  "status": "available",
  "observedAt": "2026-10-04T12:00:00Z",
  "planDate": "2026-10-04",
  "ownerUrl": "https://mealie.example.invalid/",
  "plan": {
    "items": [
      { "date": "2026-10-04", "entryType": "dinner", "title": "Bean stew" }
    ]
  }
}
```

`planDate` is an explicit source calendar selection; it is never inferred from
UTC or browser time. Only matching entries are shown, capped at50 after date
filtering. The source page is limited to5000 object entries with valid dates and
explicit types: breakfast, lunch, dinner, side, snack, drink or dessert. Invalid
structure is rejected while retaining the last accepted evidence. The source
calendar date remains unchanged; it does not claim today's household schedule.

Titles use the entry title, then recipe name, then a safe unnamed fallback.
Notes/text, identifiers, recipe payloads, images, external recipe URLs and
pagination links are omitted. The optional owner link uses the shared URL
filters. A fresh plan is **Needs review**, not ingredient availability, food
safety, recipe suitability or completion. Empty and partial pages cannot imply
complete meal coverage. Source freshness alone can be healthy.

Observation time uses the shared strict offset/calendar validator. Future or
ambiguous observations are unknown; records older than36 hours are stale.
`status: "unavailable"` omits cached meals. Each import replaces the current
workbook; it does not merge sources or persist them. No API calls, recipe
imports, calendar writes or credentials are introduced.

`npm run check` passes33 unit tests. The existing `node tests/browser-garden.mjs
--regression` runner now covers Mealie and GardenKeeper imports, general flows,
Grocy/recovery regressions and overlapping reads at1440/320px. Screenshots,
if `SCREENSHOT_DIR` is set, should remain outside the vault. The example is
synthetic; a real-data pilot, application-link acceptance and live release are open.

### Saved GardenKeeper tasks

The existing file picker accepts `garden-tasks/1.0` envelopes directly and
recalculates observation freshness at import. `garden-adapter.js` targets the
read-only GardenKeeper `/api/tasks` response shape verified through its
`/openapi.json` schema on October4. Only the schema was fetched; no personal
task data, integration credentials or live writes were used.

Synthetic envelope example:

```json
{
  "schemaVersion": "garden-tasks/1.0",
  "status": "available",
  "observedAt": "2026-10-04T00:00:00Z",
  "ownerUrl": "https://garden.example.invalid/tasks",
  "tasks": [
    { "title": "Water herbs", "status": "pending", "due_at": null }
  ]
}
```

`status` must be `available` or `unavailable`. Available envelopes require an
array of at most5000 object records with source task states `pending`,
`completed` or `cancelled`; malformed records fail the whole import. The adapter
shows at most50 pending tasks after filtering, states saved-selection counts
explicitly and omits completed/cancelled task titles. It does not claim complete
garden coverage or calculate overdue status. Pending tasks use **Needs review**
when evidence is fresh; the source's **Healthy** badge describes the saved
observation, not garden condition or task completion.

Observation time requires a valid calendar date and explicit offset, including
API microsecond timestamps. Future/ambiguous/missing time stays unknown; data
older than36 hours stays stale. Due time is independently validated and
normalized to UTC, or left absent. `unavailable` ignores cached rows. An empty
saved selection does not mean there are no tasks in GardenKeeper.

Only task titles, recorded state, validated due time and a safe owner link are
displayed. Notes, UUIDs, plant/zone associations, recurrence rules, completion
timestamps and unknown fields are omitted. URL userinfo and credential-like
query/fragment parameters are blocked across all Workbench imports; this
heuristic does not replace a reviewed, credential-free export.

Imports remain in the current tab, replacing the prior workbook. Failed or
oversized imports retain the previous evidence; Clear removes it. No merging,
background fetch, persistence, completion or rescheduling is added. A real-data
export pilot and verified application deep links remain separate acceptance.

Run `npm run check` and `npm run test:browser:garden`. The latter starts its own
loopback-only test server and covers BOM files, fresh/stale/future evidence,
empty/unavailable states, errors, oversize, prior-evidence retention, Clear,
no external requests and overflow at1440/320px. Screenshots default outside the
vault; `SCREENSHOT_DIR` may select another external destination. All25 unit tests
and both viewport checks pass as of October4.
Use `node tests/browser-garden.mjs --regression` to also run the existing general
and recovery/Grocy browser suites against the same temporary loopback server.
Those suites also pass after the shared URL-fragment and list-indentation fixes.

### Curated historical recovery evidence

`evidence/recovery-2026-10-02.json` can be loaded through the existing file
picker. It contains seven scoped, dated recovery records drawn from canonical
docs, with stale backup observations and unknown complete-system restores.
VM102 boot proof and Hub/GardenKeeper component exercises remain visible as
partial evidence. It invents no household inventory or current backup success.
This is a manual historical snapshot, not an authenticated adapter or live board.

Generate a small offline index outside the vault:

```powershell
node recovery-pack.mjs evidence/recovery-2026-10-02.json C:/path/to/recovery-index.md
node tests/browser-recovery.mjs
```

The exporter preserves scope notes and vault-relative source/runbook paths;
those paths are manually navigated from the vault root and are not browser
links. It rejects escaping/non-Markdown references and refuses to overwrite
output. Keep the vault/runbooks available offline: this index does not embed
their contents or restore data. Scope is the seven named records, not complete
estate recovery. The scheduled Hub backup implementation remains separate.

### Portable offline runbook bundle

`recovery-bundle.mjs` adds the seven curated systems' runbooks, their four source
references and selected Proxmox/OMV/shared backup/current-state/Hub checkpoint
guidance to the existing recovery index (13 unique Markdown documents). Generate
into a new directory outside the vault:

```powershell
node recovery-bundle.mjs evidence/recovery-2026-10-02.json C:/private/recovery-runbooks
node recovery-bundle.mjs --verify C:/private/recovery-runbooks
```

The root README and clickable index work without the vault. Local links to
included documents are converted to Markdown; references to omitted files are
disabled and visibly marked. The JSON manifest lists every detected bundled,
external and omitted inline Markdown/Obsidian link, plus source and copied-file
hashes. Code blocks and inline command examples remain unchanged. Heading
anchors, HTML and reference-style links are not validated; external web links
still require a network. There is no automatic recursive repository crawl.

The October2 pack has 54 omitted references, including configuration/image/
other-manual dependencies. It is self-contained for reading the selected
runbooks, **not** a complete executable or full-estate rebuild kit. Backup data,
container images, scripts/configs and private credentials remain separate.
Historical backup/restore statuses and existing maintenance gates are preserved.

Require COMPLETE and verify SHA256SUMS before use. The included README provides
the standard Linux checksum command; the Node verifier also rejects extra files
and symlinks. Checksums detect modification, not authenticity. Generation
refuses existing output, symlinked sources, escaping/non-Markdown references,
files over 512 KB and total source data over 2 MB. Credential-candidate heuristics
reject private-key headers, selected literal assignments and credential URLs
without printing values; this is not comprehensive secret detection. Keep the
pack in a protected directory; Windows permissions depend on its destination ACL.
Failed output without COMPLETE must not be used. No deletion/retention is run.

Twenty unit tests pass, including portability without the original test vault,
tampered/extra files, overwrite/path guards, credential candidates and Windows
junction rejection. All 17 checksummed files also pass independent `sha256sum`.

### Saved Grocy overview imports

The file picker directly accepts a manually saved **Household Hub** Grocy
overview envelope. `import-grocy.mjs` optionally converts the same envelope to
schema 1.0 for offline sharing. Neither path accepts raw Grocy endpoints or
contacts either service. Wrap a saved response with this
envelope (the values below are synthetic, not household observations):

```json
{
  "schemaVersion": "grocy-overview/1.0",
  "status": "available",
  "observedAt": "2026-10-02T12:00:00+01:00",
  "ownerUrl": "https://grocy.example.test/",
  "overview": {
    "stock": [{"name": "Synthetic oats", "amount": 2, "location": "Demo pantry", "best_before_date": "2026-10-05"}],
    "shopping_list": [{"name": "Synthetic apples", "amount": 1}]
  }
}
```

Use the actual collection time with offset; file-save time does not establish
observation time. For a failed collection, use `"status": "unavailable"` and
omit `overview`; cached rows are ignored. Do not put credentials in the envelope.
Choose the reviewed owning-app link manually; it is never inferred from a token
or source payload. Missing/unsafe links are omitted.

```powershell
node main/apps/home-operations-workbench/import-grocy.mjs C:/private/saved-overview.json C:/private/today-evidence.json
```

Output refuses overwrite and input is bounded to 512 KB. On Linux output is
created with 0600; on Windows protect the destination with its filesystem ACL.
Stock appears under Food to use, shopping rows under Operations, with a separate
source observation. Names, quantities and location are limited display fields;
shopping notes, product identifiers, extra fields and credentials are not copied.
Best-before dates are preserved as **best before**, never converted to use-by
dates. Numeric amounts retain source units; recipe availability is not inferred.

Freshness is calculated on direct envelope import (or CLI conversion) using a
36-hour window. Invalid, missing, timezone-ambiguous or future observations are
unknown. Reimport the original envelope as evidence ages, or regenerate converter
output; an already loaded tab has no background freshness polling. A Healthy
badge describes the saved observation, not food safety or complete inventory.
Only up to 50 rows per collection are selected, and the Hub response itself may
be filtered/limited: empty rows cannot establish absence of household stock.
Each import replaces tab evidence; it does not merge with the recovery snapshot.

Sixteen unit tests and desktop/320px fresh/stale/unavailable import checks pass.
Both converted and direct BOM-prefixed envelopes are verified. Invalid JSON,
unsupported schemas, malformed arrays and oversized files show errors while
retaining the previous labelled evidence; Clear removes it from the tab.
Real export acceptance, authenticated adapters and product deployment stay open.

### Offline health snapshot format

The file picker accepts saved `Windows management workstation` and `Proxmox
host` health-check JSON in addition to schema 1.0 workbooks. Only known check
statuses are copied; raw detail, filenames, command output and unknown fields
are discarded. These imports never contact a service or execute commands.

Evidence older than 36 hours is stale. Missing, malformed, timezone-ambiguous
or future timestamps produce unknown states. Older collectors emit local time
without an offset: explicitly convert those snapshots on the workstation using
the collector's offset at collection time (for example `+01:00` for London BST):

```powershell
node main/apps/home-operations-workbench/import-health.mjs .\windows-health.json .\operations-evidence.json +01:00
```

The converter refuses to overwrite existing output. Import its output in the
Workbench. Do not assume the Proxmox host uses the workstation's timezone.
Backup freshness never supplies integrity or restore proof. A failed camera
probe stays failed; intentional disconnection requires separate human evidence
and is not inferred from an IP address. The two collector formats can be
imported independently; each import replaces the current tab's evidence.

### Checks

```powershell
Set-Location K:\Documents\Obsidian\home-automation-project\main\apps\home-operations-workbench
npm run check

$server = Start-Process -FilePath python -ArgumentList '-m', 'http.server', '8129', '--bind', '127.0.0.1' -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
try {
  npm run test:browser
} finally {
  Stop-Process -Id $server.Id
}
```

Open `http://127.0.0.1:8129` while the local server runs to inspect the
workbench manually. Do not deploy this proof of concept or add it to the
Docker host until a live adapter contract and service placement decision exist.

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
