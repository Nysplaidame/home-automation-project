---
title: VentSys authenticated card/page bridge contract
description: Security and safety contract for the draft Lovelace-card to dashboard bridge
tags: [ventsys, home-assistant, authentication, safety]
created: 2026-09-18
type: interface-contract
status: historical-dashboard-bridge
---

# VentSys authenticated card/page bridge contract

## Status and purpose

**Superseded for the VentSys dashboard on 2026-10-18.** The deployed
`ventsys-dashboard-card` is now a direct HA custom card; it receives the
frontend's authenticated `hass` context and uses no iframe messages. The old
public-config credential was revoked. See [[ventsys-dashboard]] for the current
implementation and acceptance. The bridge requirements below are historical
constraints for any future framed integration, not the live dashboard protocol.

The separate Solar Observatory read-only candidate discussed below remains
local and retains its own bridge acceptance gates. Dashboard deployment does
not promote that independent screensaver integration.

## Trust boundary

The Lovelace card is the only authenticated caller. The embedded same-origin
page is an untrusted presentation consumer until it proves the expected origin,
source window, protocol version, and a current card-issued session identifier.
The page may receive a minimal display-state snapshot only. It may not receive
an HA token, websocket object, service object, raw secrets, or unrestricted
entity state.

## Message contract

Use an explicit protocol version and message type. Every message includes a
random per-frame session ID, issued time, expiry under one minute, and a
monotonic request ID. The receiver rejects a wrong origin, wrong source window,
wrong session, expired/replayed request, malformed payload, or unknown type.
On reload, disconnect, timeout, or validation failure, clear display state and
render an offline status; never retain the last trusted state as live.

The initial protocol contains only `state_snapshot` and `offline`. A state
snapshot permits a documented allowlist of display fields. Do not use wildcard
origins, `postMessage('*')`, executable payloads, or generic entity/service
proxies.

## Command boundary

There is no command message in the first accepted bridge. If a future review
allows a control, it must name one HA script/entity action, validate its schema
in the authenticated card, require a visible user confirmation, rate-limit it,
record an audit event without secrets, and fail closed. Emergency cutoff, fan,
valve, and power controls remain governed by their existing HA/ESPHome/MQTT
safety review and physical acceptance; this bridge cannot bypass them.

## Review and promotion gates

1. Review exact frame URLs, allowed origins, state allowlist, and no-command
   initial protocol.
2. Implement origin/source/schema/expiry/replay validation and offline clearing.
3. Add focused browser/mock checks for valid state, malformed/wrong-origin,
   wrong-source, expired/replayed, reload/disconnect, and command-free startup.
4. Independently inspect deployed assets for tokens and confirm an unopened page
   cannot initiate an MQTT or HA service call.
5. Use the existing physical safety acceptance procedure before any live control
   claim. Retain the current live asset and its rollback copy until all gates pass.

## Local candidate implementation (2026-10-04)

`main/apps/solar-observatory/` now includes a separate
`observatory-readonly-card`, receiver wiring and a simulated host. This remains
local, draft-review-required work, not accepted authenticated HA integration.
The old dashboard card is unchanged and must not be promoted unchanged.

The candidate uses version 1, `sessionId`, monotonic `sequence`, `issuedAtMs`
and `expiresAtMs` envelopes, with five-second heartbeats and fifteen-second
maximum validity. The host injects a fresh `data-observatory-session` attribute
on the same-origin iframe document at each load before sending state. Only the
expected parent, origin and bootstrapped session can establish trust. This is
not an isolation boundary against malicious same-origin scripts.

Only `input_boolean.ventsys_failsafe` and `fan.inline_fan` are mapped to fixed
display fields; unavailable values stay unknown and monitoring stays unverified.
There is no child message listener or command API. Failsafe interruption remains
latched after disconnect and, when session storage is available, frame reload;
fresh cleared state plus explicit acknowledgement is required to resume.

The application suite passes 29 unit and 14 browser tests, including real-timer
expiry, reload/replay, malformed/foreign messages, WebGL failure and command-free
operation. Real HA lifecycle, exact deployed URL/entity review, release asset
inspection, dashboard routing and physical acceptance remain promotion gates.

## Related work

- [Draft status](../../dashboards/ventsys-card-status.md)
- [VentSys roadmap](household-workshop-operations-roadmap.md)
- [VentSys HA packages](../../configs/home-assistant/)
