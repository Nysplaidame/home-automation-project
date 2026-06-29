---
title: Frigate Camera Pre-Flight Checklist
description: Pre-arrival, bench, and first-deployment checklist for PoE cameras and the managed PoE switch
tags: [frigate, cameras, poe, preflight, nvr]
created: 2026-06-28
modified: 2026-06-28
type: procedure
status: active
---

# Frigate Camera Pre-Flight Checklist

## Purpose

Prepare the Frigate camera rollout before the PoE cameras and managed PoE
switch arrive, without enabling production recording or camera MQTT before the
real RTSP paths, credentials, MAC addresses and switch behavior are known.

Current baseline:

- Frigate CT 111 is live at `192.168.30.20`.
- The live Frigate config is the migration-safe baseline with MQTT and cameras
  disabled.
- `configs/frigate/config.yml` is the future production template for four
  cameras at `192.168.30.21` through `192.168.30.24`.
- Router `lan3` is reserved for the managed switch as a tagged trunk carrying
  VLANs 1, 10, 30 and 40 after the switch is present and configured.
- The managed PoE switch is a Zyxel GS1900-8HP. Use stock firmware for initial
  camera rollout; treat OpenWrt-on-switch as a later evaluation only if stock
  firmware blocks the desired VLAN, PoE, monitoring or management posture.
- The switch is no longer camera-only: it will also carry OMV NAS access on
  VLAN 40 and the TL-WA801N extender on VLAN 1.
- Do not route or advertise VLAN 30 through Tailscale.

## Pre-Arrival Actions

- Record exact camera model, firmware line, default login behavior, RTSP
  paths, substream paths, audio support, ONVIF support and reset procedure.
- Record exact switch model, management method, default IP/login behavior,
  VLAN capability, PoE budget, PoE per-port controls and firmware update path.
- For the Zyxel GS1900-8HP, record hardware revision, current firmware version,
  PoE budget, admin access method, backup/export procedure and recovery/reset
  procedure before changing VLAN settings.
- Decide the camera naming/location map before adoption:

| Frigate name | Planned IP | Physical label | Initial role |
|---|---:|---|---|
| `cam_01` | `192.168.30.21` | `<label>` | detect + record |
| `cam_02` | `192.168.30.22` | `<label>` | detect + record |
| `cam_03` | `192.168.30.23` | `<label>` | detect + record |
| `cam_04` | `192.168.30.24` | `<label>` | detect + record |

- Prepare one unique camera admin password and one RTSP/viewer credential in
  Bitwarden. Prefer a non-admin RTSP user if the camera firmware supports it.
- Prepare a Frigate MQTT password entry in Bitwarden if the existing Mosquitto
  `mqtt` credential is not already recorded for this use.
- Confirm `/opt/frigate/certs/ca-cert.pem` still exists on CT 111 before MQTT
  is enabled.
- Keep `/opt/frigate/.env` absent or incomplete until final RTSP and MQTT
  credentials are ready.
- Put the PoE switch management interface on VLAN 10. Use planned reservation
  `192.168.10.12` after recording the switch management MAC address.
- Plan a bench-test patch lead layout: router `lan3` to PoE switch uplink,
  one camera at a time, labelled patch leads, no permanent mounting. Do not
  recable OMV or the extender to the switch until the trunk and access-port
  VLAN tests pass.
- Do not update `configs/frigate/config.yml` RTSP paths until the real camera
  stream URLs have been verified with `ffprobe`.

## Network And Switch Pre-Flight

Planned router source assigns `lan3` as a tagged trunk after the switch arrives:

```text
router lan3 -> Zyxel GS1900-8HP uplink
Tagged VLANs:   1, 10, 30, 40
Switch mgmt:    VLAN 10, 192.168.10.12
Camera ports:   untagged VLAN 30, PVID 30
OMV NAS port:   untagged VLAN 40, PVID 40
Extender port:  untagged VLAN 1, PVID 1
```

Expected switch posture:

- Camera access ports are untagged VLAN 30.
- Uplink to router `lan3` is tagged for VLANs 1, 10, 30 and 40.
- Switch management interface is VLAN 10 at `192.168.10.12`.
- OMV NAS access port is untagged VLAN 40.
- TL-WA801N extender access port is untagged VLAN 1.
- If the switch requires a PVID/native VLAN on the uplink, use an unused
  isolated VLAN for untagged ingress containment; do not make VLAN 30 native.
- Disable unused switch ports.
- Disable cloud/P2P features on cameras if the firmware exposes them.
- Disable camera internet access; VLAN 30 has no WAN path by design.
- Keep camera NTP/DNS pointed at the router unless the firmware requires a
  different local-only setting.

## Hardware Arrival Bench Sequence

1. Photograph labels, serial numbers, MAC addresses and default sticker info.
2. Power the PoE switch alone and confirm management access/reset behavior.
3. Update switch firmware only if the update path is local and does not require
   weakening VLAN 30 isolation.
4. Set switch admin password and disable unused management services.
5. Connect one camera to the bench switch.
6. Set camera admin password, disable cloud/P2P, set time zone, and configure
   local NTP/DNS.
7. Create a non-admin RTSP/viewer user if supported.
8. Record camera MAC address and chosen static IP.
9. Add the router DHCP reservation for that camera.
10. Reboot camera and confirm it receives the intended IP.
11. Verify RTSP from CT 111 with `ffprobe`.
12. Repeat for each camera before mounting anything.

## Frigate Activation Gate

Only enable the production Frigate config after all of these pass:

- All camera MAC addresses are recorded in `configs/openwrt/dhcp-config.conf`.
- Each camera responds on its intended `192.168.30.21-24` address.
- Each main stream works from CT 111 with `ffprobe`.
- If substreams are available, each substream path is recorded for lower-cost
  detection or mobile viewing.
- `/opt/frigate/.env` exists with secure permissions and contains final
  `FRIGATE_RTSP_PASSWORD` and `FRIGATE_MQTT_PASSWORD`.
- MQTT TLS to HA has been re-tested from CT 111.
- Frigate UI HTTPS/SSL plan is chosen before regular daily use.
- Initial recording retention is accepted for local CT storage before any NAS
  recording cutover.

## Apple And Remote Viewing Plan

Default Apple-device access is Home Assistant first, then Frigate's official
web UI/PWA. Lumen is not the planned path because its app-store quality signal
is weak. Treat Lumen, Viewu, Kapal or other native clients as optional later
evaluations only after Frigate camera ingest is stable.

Preferred order:

1. Home Assistant Companion App with Frigate integration, camera entities,
   alerts and dashboards.
2. Frigate web UI/PWA in Safari for direct Frigate viewing when needed.
3. Frigate Card after Frigate and camera ingest are stable.
4. Third-party native iOS clients only if they add clear value and can use the
   same secure Frigate endpoint without direct camera RTSP credentials.

Remote viewing security gates:

- Do not expose vendor camera cloud features.
- Do not route the full NVR VLAN through Tailscale.
- Do not put raw camera RTSP credentials on mobile devices.
- Prefer HA over the existing HA/Tailscale path for daily mobile viewing.
- If direct Frigate remote viewing is approved later, expose only
  `192.168.30.20/32` and only the minimum required Frigate ports through a
  tailnet-only route or HTTPS reverse proxy.

## Validation Commands

Run on Frigate CT 111.

```sh
ls -l /opt/frigate/certs/ca-cert.pem
openssl s_client -connect 192.168.20.101:8883 -CAfile /opt/frigate/certs/ca-cert.pem </dev/null
ffprobe -rtsp_transport tcp rtsp://<rtsp-user>:<rtsp-password>@192.168.30.21:554/<path>
docker compose -f /opt/frigate/docker-compose.yml config
docker compose -f /opt/frigate/docker-compose.yml logs --tail=120 frigate
```

Run on Home Assistant Terminal after MQTT is enabled.

```sh
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt -u mqtt -P '<MQTT_PASSWORD>' -t 'frigate/#' -C 1
```

Run on router after adding reservations.

```sh
uci show dhcp | grep -E 'camera|cam-|frigate'
logread | grep -E 'DHCPACK.*192\.168\.30\.2[1-4]'
```

## Do Not Do Yet

- Do not mount cameras permanently before RTSP paths, field of view and PoE
  stability are proven on the bench.
- Do not enable NAS recording cutover at the same time as first camera bring-up.
- Do not expose the Frigate UI broadly or route VLAN 30 through Tailscale.
- Do not introduce camera vendor cloud access as a troubleshooting shortcut.
- Do not install Scrypted or Frigate Card until basic Frigate camera ingest is
  stable.
- Do not adopt Lumen, Viewu, Kapal or another third-party Apple app until HA
  Companion and Frigate PWA have been tested against the live Frigate instance.

## Documentation Updates After Bench Test

- Update `configs/openwrt/dhcp-config.conf` with camera MAC reservations.
- Update `configs/frigate/config.yml` with verified stream paths, resolution,
  FPS, audio and substream choices.
- Update `TO-DO.md` Phase 5 with completed purchase, MAC reservation, bench
  RTSP and Frigate ingest steps.
- Update `docs/reference/current-live-state.md` only after production Frigate
  camera/MQTT config is actually enabled.
