---
title: Temporary Router WiFi Uplink Policy
description: Operating policy for GL-MT6000 temporary wwan_uplink during pre-flight staging
tags: [router, openwrt, uplink, policy]
created: 2026-05-28
type: procedure
status: active
---

# Temporary Router WiFi Uplink Policy

This policy defines when the GL-MT6000 temporary WiFi uplink (`wwan_uplink`)
should remain enabled while the router is staged behind an existing home router.

## Current context

- GL-MT6000 management IP: `192.168.10.1`
- Temporary uplink interface: `wwan_uplink`
- Typical upstream SSID during staging: `ZyXEL_F1E9`
- Current staging upstream channel: 2.4 GHz channel `5`; the GL-MT6000
  2.4 GHz AP radio must align to this channel while `wwan_uplink` uses
  `radio0`.
- Current use: upstream internet for pre-flight services and package/image pulls

## Keep uplink enabled when

- SearXNG or Whoogle pre-flight search needs upstream internet.
- Router-side package/image pulls are needed during pre-flight operations.
- The GL-MT6000 is not yet acting as the final internet edge.

## Disable uplink only when

- Testing final-edge behavior without upstream dependency.
- An intentional alternate upstream path is already in place and verified.

## Guardrails

- Do not disable `wwan_uplink` casually; validate impact first.
- After any uplink change, confirm both:
  - management access to `192.168.10.1` still works
  - expected internet-dependent functions still work (or are intentionally offline)

## Restore command

Run from repository root on the management laptop:

```powershell
main\tools\router-deploy\uplink.ps1 -Action enable -RouterIp 192.168.10.1
```

## Validation snapshot commands

```powershell
python main\tools\router-deploy\lint.py
python main\tools\router-deploy\compile.py --profile first-flight
main\tools\router-deploy\test-connectivity.ps1 -RouterIp 192.168.10.1
```
