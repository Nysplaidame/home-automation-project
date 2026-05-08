# VentSys Solar Observatory Screensaver

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
ventsys-dashboard.html
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

- Integrate this as an idle overlay or iframe route from `ventsys-dashboard.html`.
- Replace static mission placeholders with a curated JSON feed or HA-provided event sensor.
- Add a small configuration block for focus cadence, dashboard wake target, and safety-strip entity IDs.
- Run a browser screenshot pass on the actual 7-inch display resolution before deploying permanently.
