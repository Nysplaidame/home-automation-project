---
title: Home Assistant Apps and Enhancement Roadmap
description: Home Assistant companion apps, add-ons, HACS ideas, dashboards, maintenance, and quality of life
tags: [hacs, home-assistant, roadmap, dashboards, companion-app]
created: 2026-05-24
modified: 2026-05-27
type: reference
status: active
---

# Home Assistant Apps and Enhancement Roadmap

Home Assistant has three layers in this project:

1. Core required tools: official HA apps/add-ons that the system depends on.
2. High-value enhancements: dashboards, maintenance helpers, and mobile access.
3. Optional/risk-gated tools: custom integrations, visual automation engines, or
   styling-heavy cards that must not become safety-critical dependencies.

HACS is an enhancement layer, not core infrastructure. Safety paths, backups,
MQTT, firewall policy, VentSys emergency behavior, and monitoring must keep
working if every HACS card or custom integration is removed.

## Core required tools

These are part of the baseline Home Assistant install path, not optional HACS
work.

| Tool | Type | Value | Deployment note |
|---|---|---|---|
| Home Assistant Companion App | Official mobile app | Push alerts, actionable notifications, mobile dashboards, presence, device battery/network sensors, emergency VentSys/NVR notifications | Install on operator phones after HA accounts and 2FA exist |
| ESPHome add-on | Official add-on | Build, flash, adopt, update, and log VentSys ESP32 devices | Already required by Phase 03 and physical integration docs |
| Mosquitto broker add-on | Official add-on | MQTT backbone for VentSys, Bambuddy, Frigate, printer telemetry, and alerts | Already required by Phase 03 and TLS docs |
| Terminal & SSH add-on | Official/community add-on | HA-side diagnostics, logs, package copies, MQTT checks, emergency troubleshooting | Required for command-based validation steps |
| Studio Code Server or File Editor | Official/community add-on | Safer editing of YAML packages, dashboards, and secrets references | Prefer Studio Code Server as docs grow; File Editor is acceptable fallback |

## Core deployment rule

- Install the Companion App only after HA users and 2FA are configured.
- Use `docs/procedures/home_assistant_companion_app_guide.md` for the operator
  phone install, push test, actionable notification test, and sensor review.
- Do not route life-safety behavior through mobile-only actions.
- Use mobile notifications for alerting and acknowledgement, not as the only
  emergency control path.
- Keep ESPHome and Mosquitto documented as baseline tools, not optional
  enhancements.

## Deployment rule

- Install HACS only after Home Assistant core is stable and backed up.
- Record each HACS item, version, purpose, and rollback note.
- Prefer frontend/dashboard additions before custom integrations that affect
  automation behavior.
- Do not make safety-critical controls depend on HACS-only UI elements.

## High-value candidates

| Candidate | Type | Value | Deployment note |
|---|---|---|---|
| Frigate Card | Frontend card | Better NVR/camera dashboard inside HA | Install when cameras and Frigate are live |
| Mushroom Cards | Frontend cards | Clean general dashboards for rooms, services, printer state, and VentSys summaries | Good first dashboard enhancement |
| apexcharts-card | Frontend card | Better time-series charts for temperature, VOC, pressure, airflow, power, and IAQ | Useful after sensors publish stable history |
| auto-entities | Frontend card | Dynamic maintenance views, such as unavailable ESPHome devices or low batteries | Useful as entity count grows |
| Watchman | Integration | Finds broken entity/service references in dashboards and automations | Useful before and after refactors |

## Quality-of-life candidates

| Candidate | Type | Value | Deployment note |
|---|---|---|---|
| Bubble Card | Frontend cards | Mobile-friendly controls, popups, and compact panels | Consider for phone-first dashboards |
| browser_mod | Integration/frontend | Wall tablet, kiosk, popup, navigation, and display behavior | Consider for garage VentSys display |
| button-card | Frontend card | Highly flexible custom controls | Use for polished dashboards after core controls are stable |
| card-mod | Frontend styling | Fine-grained Lovelace styling | Use sparingly; easy to create maintenance burden |
| Scheduler Card / scheduler-component | Frontend/integration | Friendlier schedule UI for household automations | Evaluate if native schedules feel awkward |
| Adaptive Lighting | Integration | Lighting quality of life if smart lighting is added later | Not relevant until lighting scope exists |
| Bambu Lab / printer-related integrations | Integration | Potential extra printer telemetry alongside Bambuddy | Avoid duplication until P1S details are confirmed |

## Risk-gated automation candidates

| Candidate | Type | Value | Deployment note |
|---|---|---|---|
| Node-RED | Add-on or docker-host service | Visual automation flows if native HA automations become difficult to maintain | Tier 3/evaluate; do not duplicate safety-critical VentSys logic without a rollback plan |
| AppDaemon | Add-on/Python app framework | Python automation apps when YAML/templates become too awkward | Evaluate only after native HA options are exhausted |
| pyscript | Custom integration | Lightweight Python-like scripting inside HA | Evaluate only for non-critical helper logic |

## Suggested install order

1. Companion App on operator phones after HA accounts and 2FA exist.
2. Confirm ESPHome, Mosquitto, Terminal & SSH, and Studio Code Server/File Editor are installed.
3. HACS only after a current HA backup exists.
4. Frigate Card, when Frigate and cameras are live.
5. Mushroom Cards for general HA dashboard cleanup.
6. apexcharts-card for VentSys/environment history.
7. auto-entities for maintenance views.
8. Watchman before broad dashboard/entity refactors.
9. browser_mod only when the garage kiosk/wall display is real.
10. Bubble Card, button-card, and card-mod after the dashboard layout is stable.
11. Node-RED, AppDaemon, or pyscript only after a decision gate confirms native HA automations are insufficient.

## Completion checklist

- [ ] Companion App installed on operator phones.
- [ ] Companion App notifications and actionable notification categories tested.
- [ ] Companion App device sensors reviewed; enable only useful sensors.
- [ ] ESPHome, Mosquitto, Terminal & SSH, and Studio Code Server/File Editor are installed or explicitly deferred with reason.
- [ ] HA backup exists before HACS install.
- [ ] Each selected HACS item has a purpose and rollback note.
- [ ] No safety-critical workflow depends solely on HACS.
- [ ] HACS items are reviewed after HA core upgrades.
- [ ] Risk-gated automation tools are not deployed until native HA automations prove insufficient.
