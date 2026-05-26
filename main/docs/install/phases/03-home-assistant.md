---
title: Phase 03 - Home Assistant
description: HAOS baseline, add-ons, MQTT, VentSys package base, and backup target
tags: [install, home-assistant, mqtt]
created: 2026-05-24
modified: 2026-05-24
type: install-guide
status: active
---

# Phase 03 - Home Assistant

## Purpose

Bring HAOS VM 100 online, install required add-ons, enable MQTT, stage VentSys
packages, configure operator mobile access, and prepare later Frigate, Bambuddy,
ESPHome, and backup integrations.

## Runs on

- Home Assistant UI at `http://192.168.20.101:8123/`.
- Home Assistant Terminal add-on for shell commands.
- Home Assistant Companion App on operator phones.

## Prerequisites

- Phase 02 complete.
- HAOS VM exists.
- `<HA_ADMIN_PASSWORD>` and `<MQTT_PASSWORD>` stored.
- Router-local NTP works on the Automation VLAN gateway `192.168.20.1`.

## Inputs

- `<HA_ADMIN_PASSWORD>`
- `<MQTT_PASSWORD>`
- `<HA_LONG_LIVED_TOKEN>`

## Commands

Run on: Home Assistant Terminal add-on.

```sh
mkdir -p /config/packages /config/www
grep -n "packages:" /config/configuration.yaml || true
ha core check
```

Run on: Home Assistant Terminal add-on after copying packages.

```sh
ha core check
ha core restart
```

After preparing a Home Assistant OS `CONFIG` import containing `timesyncd.conf`,
run the import from the HA CLI.

Run on: Home Assistant Terminal add-on.

```sh
ha os import
ha host reboot
```

## Explanation

The package directory allows project YAML to be loaded cleanly. `ha core check`
must pass before restart so a bad YAML copy does not cause a restart loop.

The `ha os import` step imports OS-level configuration, including a
`timesyncd.conf` file based on `configs/home-assistant/haos-timesyncd-router.conf`.
This makes HAOS sync from router-local NTP at `192.168.20.1`. ESPHome/VentSys
devices then receive router-derived time from Home Assistant via the ESPHome
native API.

## Expected result

- HA web UI loads.
- Mosquitto, Terminal & SSH, Studio Code Server or File Editor, and ESPHome add-ons are installed.
- Home Assistant Companion App is installed on operator phones for notifications,
  presence, mobile dashboards, and acknowledgement actions.
- VentSys package files are staged.
- 2FA is enabled for the admin account.
- HACS remains optional and enhancement-only; see
  `docs/install/reference/hacs-enhancement-roadmap.md`.
- HAOS system time is sourced from router-local NTP, not arbitrary external
  internet NTP.

## Validation

Run on: Home Assistant Terminal add-on.

```sh
ha core info
ha addons list
mosquitto_pub -h localhost -p 1883 -u mqtt -P '<MQTT_PASSWORD>' -t test/install -m hello
mosquitto_sub -h localhost -p 1883 -u mqtt -P '<MQTT_PASSWORD>' -t test/install -C 1
```

Run on: Home Assistant Terminal add-on.

```sh
date
ha host info
```

## Failure recovery

- If HA fails config check, read the line number and fix YAML before restart.
- If MQTT auth fails, reset the Mosquitto user/password and update the secrets
  ledger.
- If UI is unreachable, validate VM IP and router firewall before editing HA.
- If HAOS time is wrong, validate router NTP on `192.168.20.1` before changing
  ESPHome time settings.
- If mobile notifications fail, verify the Companion App login, HA notification
  permissions, and the user's HA notification service name before changing
  automations.

## Completion checklist

- [ ] HA UI loads.
- [ ] Required add-ons installed.
- [ ] Companion App installed on operator phones and notification test passes.
- [ ] MQTT publish/subscribe test passes.
- [ ] VentSys files staged.
- [ ] HA backup target is planned, even if OMV is not live yet.
- [ ] HACS is not installed until a backup exists and enhancement choices are documented.
- [ ] HAOS router-NTP override applied or explicitly deferred.
