# VentSys Solar Observatory Screensaver

## Rebuild status - 2026-10-04

The old HTML below is a prototype, not an accepted astronomy or safety
implementation. Its arbitrary orbital phases, separate moon/path transforms,
procedural textures and token-based HA connection are being replaced. Do not
add an HA token to any public `/local/` asset.

The replacement starts in `main/apps/solar-observatory/` (see its README).
Implemented locally: typed Horizons vector ingestion, parent-relative Hermite
interpolation, common body/path transforms, camera framing and continuous
retargeting maths, a read-only expiring safety-message receiver, and validated
local cache publication. Typecheck and 25 offline tests passed. Six tracked
JPL fixtures validate withheld midpoint interpolation over two hours; worst
discrepancy was about 0.42 metres for Io, not a navigation-accuracy claim.
A live one-shot refresh fetched the six initial objects into ignored local
cache. No live HA configuration, existing card, dashboard or deployment changed.

The replacement now has a local single-Three.js geometry preview for Earth/Moon,
Jupiter/Io and Saturn, with portrait/system modes, 24-second focus travel,
click-only wake to an offline placeholder, and an always-visible safety strip.
Typecheck, production build, 49 unit tests and 19 Chromium browser tests
passed. Screenshot review at 800x480, 1024x600 and 390x844 led to tighter Saturn
framing based on ring projection rather than a whole-system bounding sphere.
The first visual asset pass adds locally served 2K NASA Earth/Moon colour maps
and a muted photographic ESO/S. Brunier Milky Way panorama with visible source
credits. Jupiter, Io and Saturn retain proof geometry. Shared texture residency,
nonblocking loading and matte fallback keep imagery separate from safety state.
Earth/Moon maps now follow the approximate IAU text-PCK body attitude, independently
of orbital translations. Sixteen independent SPICE samples verify the model and
time conversion; actual sphere UV and browser tests check map axes and unchanged
moon/path agreement. This is not precision Earth EOP or binary lunar libration.
Verified leap-second coverage is 2017-01-01 through 2027-06-30 UTC; later dates
show explicit orientation fallback until the time model is reviewed. The backdrop
is not an aligned sky chart. See the app README and `public/assets/README.md`
for source provenance, model limits and optional offline fixture regeneration.
Asset tests verify local decoding, no external runtime image requests, stable
texture counts after cycling, failed-image fallback and late-load focus changes.

Run `npm run dev` in `main/apps/solar-observatory` for localhost port 4175.
The page uses valid local cached ephemerides or explicitly marked reference
data; `?reference=1` selects the reproducible two-hour fixture span. Generated
data/build/screenshots are ignored. `/mock-host.html` now exercises a separate
read-only candidate card: fixed failsafe/fan fields, fresh per-load bootstrap,
five-second heartbeats and fifteen-second expiry. Alerts pause astronomy,
persist across reloads via session storage, and require fresh cleared state plus
explicit acknowledgement. Disabled storage limits persistence to the document.
Malformed trusted messages clear connection trust; unrelated sources are ignored.
Monitoring remains unverified, and mock data is explicitly labelled. No tokens,
services or generic child command handler are present. Production-preview smoke
testing passed with no browser errors or control calls. The old card is unchanged.
Authenticated host acceptance, full assets/catalogue, scheduled
data service, deployment and actual Pi performance/soak gates remain open.
Pi 4 is the conservative performance target; Pi 5 is preferred. Final screen
resolution is unconfirmed, so both 800x480 and 1024x600 remain acceptance sizes.

## Legacy prototype reference

The following describes existing source, not verified behaviour or deployment
approval. In particular, its claim that moons match paths is not reliable and
its public-token integration is superseded by the read-only bridge contract.

## Purpose

`ventsys_solar_screensaver.html` is the first standalone implementation of the VentSys standby display. It is designed for a 7-inch dashboard screen and follows the Quiet Observatory direction with a restrained mission/event layer.

## Architecture

- **Static deployment:** single HTML file, matching the existing `/config/www` Home Assistant deployment pattern.
- **Renderer:** one full-screen 2D `<canvas>` for the wide orrery, plus a transparent Three.js focus canvas for close-up planets, moons, rings, comets, and telescope markers.
- **Layout target:** compact `800x480`/`1024x600` class screens first, with responsive behavior for larger preview windows.
- **Astronomy model:** lightweight client-side orbital approximation from a fixed epoch. Positions are suitable for an ambient orrery, not scientific navigation.
- **Distance treatment:** orbital angles use real periods, but radial distance is compressed so Pluto and the outer planets remain visible on a 7-inch screen.
- **Focus engine:** periodic camera focus on planets, Pluto, comets, telescopes, or mission-layer placeholders. Labels only appear during focus.
- **3D focus layer:** focused planets now render in local 3D coordinates so moons sit on their own parent-body orbit paths instead of using compressed solar-system projection.
- **Comets:** always visible as unlabeled moving objects with subtle tails; labels appear only when focused.
- **Missions and telescopes:** represented as a curated local catalog for now. This leaves a clean path to replace placeholder objects with live mission/event data later.
- **VentSys safety strip:** always visible and wired for Home Assistant WebSocket status when a token is configured.

## Home Assistant Integration

The screensaver currently reads these configurable HA entities:

- `input_boolean.ventsys_failsafe`
- `fan.inline_fan`
- `sensor.fdm_airflow_rps`
- `sensor.sla_airflow_rps`
- `sensor.booth_airflow_rps`
- `binary_sensor.mqtt_broker_online`

If no token is configured, the page runs in offline/demo mode and the safety strip shows HA as offline.

## Wake Behavior

The current implementation wakes the main dashboard on click/tap only. Failsafe state also schedules a wake back to the main dashboard.

The current dashboard target is:

```text
dashboards/ventsys-dashboard.html
```

This assumes both files are deployed into the same Home Assistant `/local/` directory.

## Local Preview

The screensaver now uses a local ES module copy of Three.js, so open it through HTTP rather than directly via `file://`.

From `main/tools/playwright-smoke`:

```powershell
npm run preview:screensaver
```

Then open:

```text
http://127.0.0.1:4173/ventsys_solar_screensaver.html
```

## Next Build Steps

- Integrate this as an idle overlay or iframe route from `dashboards/ventsys-dashboard.html`.
- Replace static mission placeholders with a curated JSON feed or HA-provided event sensor.
- Add a small configuration block for focus cadence, dashboard wake target, and safety-strip entity IDs.
- Run a browser screenshot pass on the actual 7-inch display resolution before deploying permanently.
