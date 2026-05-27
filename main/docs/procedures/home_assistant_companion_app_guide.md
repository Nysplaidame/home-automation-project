---
title: Home Assistant Companion App Guide
description: Operator phone onboarding, push notification test, actionable acknowledgement test, and sensor policy
tags: [home-assistant, companion-app, notifications, mobile]
created: 2026-05-27
modified: 2026-05-27
type: procedure
status: active
---

# Home Assistant Companion App Guide

Use this guide to onboard operator phones without making mobile push the only
safety path. Mobile notifications are for visibility and acknowledgement;
VentSys safety automations must continue to use HA, MQTT, ESPHome, relay logic,
and persistent notifications even if a phone is offline.

References:

- Home Assistant Companion notification basics:
  <https://companion.home-assistant.io/docs/notifications/notifications-basic>
- Home Assistant Companion actionable notifications:
  <https://companion.home-assistant.io/docs/notifications/actionable-notifications>

## Current Project State

- HA admin 2FA is recorded as complete in `TO-DO.md`.
- Companion App phone install is confirmed for device notify service
  `notify.mobile_app_mai_foenn`.
- HA is currently local HTTP at `http://192.168.20.101:8123`.
- HA HTTPS pre-flight certificates exist but HTTPS is not enabled yet.
- Tailscale remote access to HA is live through docker-host route
  `192.168.20.101/32`.

## Install Path

Run on: operator phone.

1. Install the official Home Assistant Companion App.
2. Connect the phone to the trusted home LAN or Tailscale.
3. Add server URL `http://192.168.20.101:8123`.
4. Sign in with the operator HA account and complete 2FA.
5. Allow notifications.
6. Give the phone a stable app/device name, such as `operator_pixel` or
   `operator_iphone`.

Avoid using the future public/HTTPS URL until the HA HTTPS cutover is complete.

## Find The Notify Service

Run on: Home Assistant UI.

1. Go to **Developer Tools -> Actions**.
2. Search for `notify.mobile_app`.
3. Record the exact action name, for example:

```text
notify.mobile_app_operator_pixel
```

The service name is created after the app registers. If it does not appear,
restart Home Assistant once, then check the app notification settings.

Confirmed project service:

```text
notify.mobile_app_mai_foenn
```

## Basic Push Test

Run on: Home Assistant UI -> Developer Tools -> Actions.

```yaml
action: notify.mobile_app_<device_id>
data:
  title: "HA Companion test"
  message: "Push path is working."
  data:
    tag: "ha-companion-test"
```

Expected result:

- The phone receives the notification.
- The notification does not fan out to unrelated services.
- The exact `notify.mobile_app_<device_id>` service is recorded in the handoff.

## Actionable Notification Test

Run on: Home Assistant UI -> Developer Tools -> Actions.

```yaml
action: notify.mobile_app_<device_id>
data:
  title: "HA acknowledgement test"
  message: "Tap Acknowledge to confirm action events reach HA."
  data:
    tag: "ha-ack-test"
    actions:
      - action: "ACK_TEST"
        title: "Acknowledge"
      - action: "IGNORE_TEST"
        title: "Ignore"
```

Run on: Home Assistant UI -> Developer Tools -> Events.

Listen to:

```text
mobile_app_notification_action
```

Expected result:

- Tapping **Acknowledge** emits an event with `action: ACK_TEST`.
- Tapping **Ignore** emits an event with `action: IGNORE_TEST`.

## Sensor Policy

Enable only sensors that have a clear operational use:

- Battery level and charging state.
- WiFi connection / BSSID if useful for home presence.
- Device tracker if presence automations are intentionally added.
- App notification permission/status sensors.

Keep noisy or privacy-heavy sensors disabled unless there is a documented need:

- Precise location history beyond normal device tracking.
- Activity/motion sensors.
- High-frequency network, audio, storage, or health telemetry.

## Project Integration Rule

Do not replace existing `notify.persistent_notification` safety defaults in
VentSys or Bambuddy until:

- At least one operator phone has passed both tests above.
- The exact mobile notify service is documented.
- A fallback persistent notification remains in the same automation path.
- The automation has been tested with the phone offline.

## Completion Checklist

- [x] Companion App installed on operator phone.
- [x] Phone can reach HA locally or through Tailscale.
- [x] `notify.mobile_app_mai_foenn` action appears in HA.
- [x] Basic push test succeeds.
- [x] Actionable notification event test succeeds.
- [ ] Enabled sensors reviewed and noisy sensors disabled.
- [x] Handoff updated with device notify service name.
