# Solar Observatory Foundation

Local-only replacement foundation for the 7-inch VentSys screensaver. This
includes a single-renderer geometry preview and mock-tested read-only host;
it is not deployed. Existing dashboard files,
the draft HA card and live control paths are unchanged.

## Run

Requires Node 22.18 or newer. From this directory:

```powershell
npm ci
npm run typecheck
npm test
npx playwright install chromium
npm run test:browser
npm run dev
```

Open `http://127.0.0.1:4175/`. The preview uses valid local cached ephemerides
when available, otherwise clearly marked recorded reference data. For repeatable
inspection use `/?reference=1` (2026-10-04 01:00 UTC). `npm run build` produces
an ignored `dist/` preview build, not an approved HA release. `npm run stage:data`
stages public astronomy JSON only; no HA state, credentials or runtime lock
files are copied. Staged data is a snapshot; restart preview after refreshing.

Use Next focus to cycle Earth portrait/system, Jupiter portrait/system, Saturn
portrait/system. Normal focus travel takes 24 seconds; reduced motion is
immediate. Mouse movement does not wake. Click/tap or Dashboard opens an offline
placeholder, not the real dashboard. Standalone pages always report safety
status unavailable. Open `/mock-host.html` to exercise the separate candidate
card with explicitly simulated connection, failsafe and delivery-loss controls.
There is no live HA connection or command path in this harness.

The candidate `observatory-readonly-card` forwards only failsafe/fan display
states; monitoring remains unverified. Alerts interrupt astronomy and remain
latched until fresh cleared state and explicit acknowledgement. Session storage
preserves that latch across frame reloads; when storage is unavailable, latch
persistence is limited to the current document. The build includes the mock
harness for inspection, not an approved deployment package.

This is a **partial visual study, not the final treatment**: Earth and Moon
now use local 2K NASA surface maps against a muted ESO/S. Brunier Milky Way
photograph. Jupiter, Io and Saturn remain matte proof geometry, with approximate
ring bands and only Moon/Io satellite coverage. Image credits and source links
are visible in the viewport; provenance and limitations are recorded in
`public/assets/README.md`. The sky is atmospheric, not an aligned star chart.
Available trajectories are drawn as open paths, not invented closed
ellipses. Saturn orientation/radii use NASA NAIF
[pck00011](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc);
the pole uses a UTC century approximation, not a full SPICE attitude solution.
Earth/Moon surfaces now follow the approximate IAU text-PCK attitude model at
the displayed epoch, independently of their orbital translations. Jupiter's
surface orientation remains illustrative. This is not precision Earth EOP or a
binary lunar libration solution, and it adds no live cloud/weather imagery.

Orientation time coverage is deliberately limited to 2017-01-01 through
2027-06-30 UTC. NASA `naif0012.tls` supplies the UTC-to-TDB conversion constants;
[IERS Bulletin C 72](https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.72) confirms
no December 2026 leap second. Review subsequent bulletins before extending this
limit. Outside coverage, imagery is explicitly labelled an orientation fallback;
orbital display and safety state remain independent.

Tests run offline against six deliberately tracked JPL response fixtures.
`npm run capture:fixtures` explicitly regenerates those fixtures using serial
network requests. Review resulting source/version/coverage changes before
accepting them; never run capture as part of routine tests.

`npm run refresh` fetches current ephemerides into ignored
`.cache/ephemerides/`. It has no HA credentials and cannot deploy to Samba.
The one-shot worker uses an exclusive lock and publishes only after every
response validates. If it is forcibly terminated, inspect for an active worker
before manually clearing its stale `refresh.lock`. No timer or retries are
installed. Old content-addressed generations are not pruned yet; do not schedule
this prototype unattended.

## Implemented contracts

- `astronomy.ts`: kilometre/second ICRF vectors with UTC millisecond epochs;
  Hermite interpolation, parent composition, coverage rejection, shared
  right-handed display transform and path sampling. No light-time corrections.
- `horizons.ts`: pinned API response version 1.2, target/centre/frame/unit/
  correction checks, complete regular sample coverage. Unsupported metadata
  fails closed rather than silently adapting. Source API documentation version
  numbers are not necessarily the runtime response signature version.
- `safety.ts`: standalone receiver for fixed, read-only display messages. Exact
  origin/window/session checks, monotonic sequence, fifteen-second maximum
  expiry, wall plus monotonic-clock freshness, no optimistic health verdict.
  The host must generate a cryptographically random new session on each frame
  load, inject the expected session through the trusted bootstrap and send
  snapshots every five seconds. `safety-browser.ts` connects this receiver only
  inside an explicitly enabled same-origin frame. The host writes a fresh
  `data-observatory-session` bootstrap attribute on each loaded document.
- `safety-host.ts` and `observatory-card.ts`: fixed entity mapping, minimal
  envelopes, connection loss handling and five-second heartbeats. No child
  message listener, service dispatch, credentials or unrestricted entity data.
  The classic HA `hass` setter adapter is mock-tested, not HA-accepted.
- `camera.ts`: conservative sphere-based fitting to the usable viewport and
  quintic scalar motion preserving position, velocity and acceleration on
  retarget. Use log-distance for positive camera distances; full camera path
  collision/occlusion checks remain a renderer integration task.
- `cache.ts`: content-addressed bundle files, hash verification, parent-coverage
  validation and atomic local manifest replacement. A stale bundle may remain
  stored, but orbital evaluation refuses timestamps outside coverage.
- `surfaces.ts`: two shared local 2K colour maps, nonblocking loading with
  eight-second fetch timeout, matte fallback and disposed-material guards.
  No per-focus texture duplication or external runtime image requests.
- `orientation.ts`: text-PCK Earth/Moon body axes, lunar periodic terms, bounded
  UTC-to-TDB conversion and the explicit sphere-UV-to-ICRF display basis. Only
  individual meshes rotate; moon translations and path geometry do not inherit spin.

The ICRF axis remapping is not an ecliptic-plane transformation; the renderer
must choose its viewing orientation explicitly. Bodies and orbit geometry must
share that orientation, independent of each planet's axial spin.

## Evidence and limits

On 2026-10-04, typecheck, production build, 49 unit tests and 19 Chromium
browser tests passed. Browser coverage includes 800x480, 1024x600 and 390x844,
actual float32 line/mesh projection agreement, six-view cycling, keyboard/click
wake, GPU geometry disposal, gradual camera travel and offline status during
data/context failures. Screenshots were inspected and Saturn's initial overly
conservative ring framing was corrected. This is not a Pi FPS benchmark.
Safety checks cover real-timer heartbeat/expiry, malformed and foreign messages,
new sessions on reload, persistent alerts, explicit clear acknowledgement,
graphics failure, minimal payloads, rejected URLs and ignored command requests.
Asset checks cover successful local decoding, no external image requests,
stable renderer texture counts over repeated focus cycles, failed requests and
late arrival after a focus material has been disposed. Desktop/mobile imagery
screenshots were inspected; source-model accuracy limits remain explicit.
Sixteen independent SpiceyPy/CSPICE fixture samples validate Earth/Moon axes at
eight dates from 2017 through June 2027. Tests check matrix components within
1e-10 and TDB seconds within 5e-7 of those fixtures, plus actual sphere UVs,
right-handed bases, lunar near-side direction and unsupported-date fallback.
Those tolerances measure agreement with the same text-PCK model, not physical
orientation accuracy. Browser tests also verify changing rendered attitude
without disturbing moon/path projection agreement.

The optional `scripts/capture-orientations.py` generator needs Python 3.12 and
`spiceypy==8.2.0`; it is not used by builds, routine tests or the browser. It
downloads the named kernels to ignored `.cache/orientation-kernels/` and records
their hashes with generated `tests/fixtures/orientations.json`. Review fixture
changes explicitly. The local verification environment is also under `.cache/`.
A production-preview smoke check reported no browser errors or control calls.
The build retains a roughly 555 kB minified Three.js/application chunk warning;
runtime performance and asset budgets remain acceptance gates.

Recorded data spans 00:00-02:00 UTC
on that date. Keeping alternate five-minute samples and testing the withheld
midpoints gave a maximum position discrepancy of approximately 0.000418 km
(Io). This validates interpolation for those fixtures only, not general
ephemeris accuracy, source uncertainty, manoeuvres or all orbital phases.

A live one-shot refresh also succeeded: five natural bodies have 2,017 samples
each (seven days); JWST has 577 samples (two days), at five-minute intervals.
This is calculated ephemeris data, not live spacecraft telemetry.

## Next gates

1. Extend the preview with full orbital coverage, remaining body attitudes,
   real assets and label collision management. Keep the current text-PCK
   accuracy limits visible; precision EOP/lunar kernels are not implemented. Verify extended
   live-cache views, interrupted transitions and actual Pi frame time before
   expanding the catalogue. The reference fixtures remain two-hour snippets.
2. Review the candidate host against the canonical bridge contract and test
   authenticated HA frontend lifecycle, exact deployed URLs, entity mapping,
   idle/dashboard routing and physical safety acceptance. Remove the mock
   harness from the accepted release. Do not promote the old draft card unchanged.
3. Add time/trajectory freshness UI, manoeuvre-aware segments, source-specific
   refresh policies, bounded cache retention and an accepted publication path.
   For CelesTrak, stop on non-200 responses per its usage policy; do not reuse
   generic backoff blindly. SGP4/TEME conversion is not implemented.
4. Expand assets/catalogue only after browser geometry and safety gates pass;
   test actual Pi 4/5 performance and a 24-hour soak before deployment.

Canonical status: `../../docs/procedures/ventsys_solar_screensaver.md`.
