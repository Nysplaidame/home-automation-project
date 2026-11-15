---
title: VentSys history, telemetry and activity deep dive
created: 2026-11-14
status: implemented-with-hardware-limits
---

# VentSys history, telemetry and activity

This review follows the owner's requests for sensor graphs, durable activity, array/pipe separation, pressure icons and per-board detail/maintenance controls. The live service manual remains [[../procedures/ventsys-dashboard]].

## What the investigation found

The old SVG log was a browser-session list capped at eight entries, with six diagram lines truncated after 26 characters. It never fetched HA history. Reloading therefore commonly left one Ready entry. Incident additions were recorded only while the browser was watching; cleared latches and incident recovery were not consistently represented. HA already had retained state/activity data: the inspected whole-day logbook had 18,441 rows, much of it routine automation-trigger and unitless sensor noise. A scoped request reduced that to 312 relevant activity records during acceptance. New activity uses a dedicated HA anchor and selected VentSys entities, never an unfiltered household feed.

The dashboard previously combined a new FDM array with legacy pipe-air sources and used the SLA pipe reading as its enclosure reading. These are now five independent sources: Ambient; FDM array `.31`; FDM pipe/legacy enclosure sensor `.32`; SLA array (not adopted/reporting); SLA pipe `.37`. The pipe designation follows the owner's requested dashboard grouping; physical placement remains an owner check. A missing SLA array is not filled from the pipe. FDM `.32` retains mixed legacy HA names; its CO heartbeat is matched to that board's temperature, not a different device.

## Useful graph inventory

| Graph | What it helps diagnose | Interpretation and limits |
|---|---|---|
| BME680 gas resistance, per source | Emission changes, ventilation recovery after a print, enclosure versus pipe differences | Raw resistance in ohms; not AQI, VOC concentration or proof of safe air. Temperature, humidity, heater history and sensor-to-sensor differences matter. Compare each sensor to its own baseline rather than equating absolute values between boards. |
| CO Rs/R0 plus configured ratio thresholds | Relative changes from captured clean air; proximity to the firmware alarm threshold | Falling ratio is the alarm direction. Existing thresholds are 0.5. Cross-sensitivity remains; no calibrated ppm. New `.31` baseline is still unset, so its ratio can be unknown. |
| CO voltage | Wiring saturation/disconnection, power/warm-up behaviour, baseline diagnosis | Useful alongside fault timeline and ratio, never interpreted alone as gas concentration. |
| Temperature and rise rate | Heating, extraction response, unusual rate changes | Celsius and Celsius/minute are separate plots. Current thresholds remain firmware/HA configuration, not chart-generated decisions. |
| Humidity | Process/environment changes and context for gas resistance | Useful correlation context; no new humidity safety alarm. |
| Differential pressure | Whether enclosure is above/below outside; response to doors and extraction settings | Native Pa source only. H inside/L outside must be physically confirmed. Equality uses a provisional ±0.5 Pa display tolerance, not calibrated accuracy. |
| Absolute pressure | Weather/reference offset and board comparison | Separate from differential pressure; subtracting two ordinary barometers is not a replacement for the SDP810. |
| Airflow wheel rotation | Stopped/moving wheel, response to valve/fan settings | Native raw units preserved by HA graphs; diagram converts rounds/s to RPM. Wheel RPM is not fan motor RPM and is not calibrated CFM. |
| Controller position reports | Requested routing changes and reported response | A report, not physical valve feedback. Restored commands and calibration limits still apply. |
| Fan state / operating result | Timing of ventilation requests relative to sensor changes | No fan tachometer entities currently exist. Diagram 0 RPM is explicitly an off-report indicator; running RPM is unmeasured. Unknown fan state stays unavailable. |
| Alarm/latch/fault timelines | Align pressure/gas/temperature changes with alarm activation, acknowledgment and fault recovery | Acknowledgment requested and actual latch-cleared report are different events. Physical alert/cutoff/phone delivery acceptance remains separate. |
| Wi-Fi | Correlate telemetry gaps with signal changes | Signal alone does not prove connectivity or sensor health. Uptime availability provides separate board-heartbeat context. |

Sensor trends uses HA's native history-graph cards, with 2-hour, 24-hour and 7-day selections and 60-second refresh. Individual board detail panels group recent two-hour histories by unit. This keeps different physical units out of the same scale and uses HA's own recorder/history path. No cloud chart service or new credentials were introduced.

## Recording and retention

No explicit recorder override was found in the live main configuration/packages. HA's documented default raw-state retention is ten days; no database purge or retention setting was changed. The Activity UI lets the owner select a calendar day within retained history, and shows an empty/error result honestly. It does not promise permanent records. Existing eligible temperature, humidity, gas resistance, voltage and pressure sensors already expose mean-statistics metadata. HA's native history graph can use long-term statistics for eligible sensors beyond raw retention.

CO ratio sensors lacked measurement metadata. `ventsys_dashboard_history.yaml` adds `state_class: measurement` and the display unit `ratio` to the three installed ratio sensors; threshold numbers receive the same display unit. Native wheel sensors receive measurement state class without changing their reported units. This enables future statistics; it does not reconstruct previously purged samples or change firmware alarms. New native `.31` ratio remains unknown until clean-air capture. Customizations were applied with HA core-config reload and require no firmware reflash.

References: [HA history graph](https://www.home-assistant.io/dashboards/history-graph/), [recorder](https://www.home-assistant.io/integrations/recorder/), [long-term statistics](https://www.home-assistant.io/docs/configuration/long-term-statistics/).

## Durable activity and board actions

`ventsys_dashboard_activity.yaml` records availability transitions of selected critical measurements/board heartbeats, binary alarm/fault/latch/status changes, baseline/zero/acknowledgment/shutdown requests, maintenance transitions and operating results. Ordinary numeric sample changes are deliberately excluded from the activity list; they belong in graphs. A second automation logs the four guarded dashboard script calls with a whitelist of target/zone/kind/value fields. These records say request, not successful physical action. Neither automation sends actuator commands.

Activity is stored in HA Logbook under `input_boolean.ventsys_activity_source`. The main log fetches today's scoped events every minute; clicking it opens full wrapped messages, date selection, filtering and refresh. A separate Activity tab offers the same history. The diagram shows six latest lines with all text fitted inside the wider panel, without character truncation. Very long lines can shrink; the expanded view is the readable full-text presentation. Session-only command outcomes remain distinguished from HA-recorded events, and up to 200 local session entries are retained until the page is closed. There is no fabricated reconstruction of earlier unrecorded actions.

Clicking pressure, air-sensor and airflow icons or their environment readings now selects their board in the right-hand panel. The panel lists values, current alarm/fault/latch state, guarded firmware acknowledgment where supported, recent graphs and maintenance controls. Every diagram device has a maintenance helper. Starting maintenance confirms before setting expected-offline state and sending its own reachable firmware `power_off_board` action. If no shutdown action is exposed, the UI tells the owner to unplug manually. Reactivation restores expected-online monitoring; it cannot power a disconnected or sleeping board. Restore power first and verify fresh telemetry. Maintenance does not clear alarms, calibrate sensors or suppress existing CO/failsafe warnings. The adopted `.31` and `.32` boards were added to board-dropout monitoring; future/missing devices are not silently claimed adopted. No real board shutdown was exercised in acceptance.

## Further work worth doing

1. Complete physical source placement, SDP tube polarity/zero and clean-air baselines. Log baseline captures and avoid silently resetting a baseline while investigating an event.
2. Run supervised sensor stimulus, latch acknowledgment, maintenance shutdown/reconnect, cutoff and phone-delivery tests. Browser/API tests cannot prove physical safety actions.
3. Collect several real print/extraction sessions before designing BME680 relative-change warnings. Use a fixed owner-approved clean-air reference plus duration/hysteresis, temperature/humidity context and explicit invalid-data handling. Avoid an adaptive baseline that learns a hazardous condition as normal.
4. Build a relative airflow baseline matrix for actual fan/valve configurations. Only add flow units after calibration against a known flow standard; a spinning wheel does not certify sufficient extraction.
5. Add fan tachometer hardware/firmware if real motor RPM is wanted. Current controls provide state/percent, not rotation feedback.
6. Decide whether incident records need retention beyond the recorder window. Existing InfluxDB/Grafana can support longer numeric analysis after verifying export inclusion/retention; a durable incident store/export is separate from raw-state statistics. Do not extend high-rate raw retention indiscriminately.
7. After source/measurement validation, consider overlays for print state, fan percentage and valve position; enclosure-minus-pipe temperature/gas trends; extraction recovery time after prints; and uptime/dropout duration summaries. These are analysis tools, not substitutes for certified alarms.

## Acceptance and deployment

HA configuration check passed for the added activity/history packages and extended board-health package. Scoped live Logbook API returned prior latch history and a labelled no-actuator acceptance event. Templates were exercised for ordinary sample exclusion, outage/recovery, latch clear, acknowledgment and maintenance. Frontend tests cover sensor selection/graphs, pressure states, maintenance confirmation/cancellation/exact board targeting, acknowledgment gating, history loading/full messages, graph range selection and fan RPM reporting. Existing command/arbitration regression coverage remains required. Native graph creation is tested with a helper double, and HA history/statistics APIs are verified live; physical readings/actions and all native chart interactions still need owner acceptance.
