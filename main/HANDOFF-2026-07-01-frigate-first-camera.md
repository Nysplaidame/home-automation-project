# HANDOFF — First Frigate Camera Live (2026-07-01)

Project root: `E:\home-automation-project`

## What was accomplished

- Bench camera: ANNKE C500, model `I51HJ`, firmware `v5.8.10 build 250917`
- Camera MAC confirmed: `D0:3B:F4:07:71:45`
- Camera IP is now the reserved address `192.168.30.21`
- Verified RTSP paths:
  - main: `/Streaming/Channels/101`
  - sub: `/Streaming/Channels/102`
- Camera hardening during bench work:
  - `Annke Vision` disabled
  - router-local NTP set
  - ONVIF enabled
  - RTSP auth changed from `Digest` to `Digest/Basic`
- Live Frigate on CT 111 is ingesting the first camera successfully at roughly
  `10 fps`
- Frigate MQTT is enabled over TLS to HA Mosquitto on `192.168.20.101:8883`,
  with CA trust at `/opt/frigate/certs/ca-cert.pem`. This is required for the
  HA Frigate integration's sensors, switches, and occupancy entities to stay
  available.
- Frigate go2rtc is enabled for the first camera:
  - `cam_01_annke_c500` restreams the main `101` stream
  - `cam_01_annke_c500_sub` restreams the sub `102` stream
  - WebRTC candidates include `192.168.30.20:8555`
  - the browser verified a WebRTC consumer with video and PCMU audio

## Important live state

- The repository `main/configs/frigate/config.yml` is still the migration-safe
  baseline. Do not assume repo source matches live CT 111 camera config yet.
- Live CT 111 files that were changed:
  - `/opt/frigate/config/config.yml`
  - `/opt/frigate/.env`
  - `/opt/frigate/docker-compose.yml`
- Live camera test config on CT 111 uses:
  - detect from substream `102`
  - record from mainstream `101`
- Live `/opt/frigate/.env` now contains the current RTSP and MQTT passwords.
  Do not write those secrets into tracked repository files.

## HA / browser state from 2026-07-01 before TLS cutover

- Home Assistant UI was reachable directly at `http://192.168.20.101:8123/`
  from the in-app browser before the 2026-07-02 native HTTPS cutover. Current
  HA UI is `https://192.168.20.101:8123/`.
- Direct SSH from this Codex/Windows host to the HA Terminal & SSH add-on is
  working after adding local SSH config entries for `ha`, `home-assistant`,
  `haos`, and `192.168.20.101`, all using
  `~/.ssh/id_ed25519_codex_ha`. Verified commands:
  `ssh ha` and `ssh root@192.168.20.101`.
- A fresh long-lived access token was created during this session and shared in
  chat. Do not record that token in git or in project docs.
- HA login/browser session is usable.
- The Frigate HA custom integration was staged manually from official release
  `v5.15.4` to `/config/custom_components/frigate` over Samba.
- HACS custom integration `2.0.5` was staged manually from the official
  `hacs/integration` release asset to `/config/custom_components/hacs` over
  Samba. A follow-up mirror pass verified source/destination parity:
  `2260` files and `48,047,695` bytes on both sides.
- HA was restarted after staging the Frigate and HACS integrations.
- After restart, both custom integrations load far enough for direct add-flows
  to open:
  - HACS: `.../add?domain=hacs` opens "Do you want to set up HACS?"
  - Frigate: `.../add?domain=frigate` opens "Do you want to set up Frigate?"
- Frigate HA integration setup is complete. HA now has a `frigate` config entry
  titled `192.168.30.20:5000`, created from the UI on 2026-07-01. Use the
  Frigate API URL `http://192.168.30.20:5000` for this integration, not the
  Frigate web UI URL on port `8971`.
- HACS setup is complete. HA now has a `hacs` config entry created from the UI
  on 2026-07-01 after GitHub device authentication.
- Advanced Camera Card, formerly Frigate Card, was installed from release
  `v7.27.4` in a HACS-style frontend asset layout under
  `/config/www/community/advanced-camera-card`. HACS did not register the repo
  through its catalog during this session, so the active Lovelace resource uses
  `/local/community/advanced-camera-card/advanced-camera-card.js` rather than a
  HACS-managed `/hacsfiles/...` URL.
- The CCTV dashboard now uses Advanced Camera Card as the primary card for the
  first Frigate camera. It is configured for `camera.cam_01_annke_c500`, with
  `frigate.camera_name: cam_01_annke_c500` and `live_provider: go2rtc`.
- The dashboard also includes a compact entity/status panel for the camera's
  Frigate motion, person occupancy, object count, review status, and Frigate
  control switches: detect, motion, recordings, snapshots, review alerts, and
  review detections.
- Advanced Camera Card loaded successfully after a Home Assistant Core restart
  and now uses the Frigate go2rtc live provider. The image provider remains
  available as a fallback button.
- After MQTT was enabled, the Frigate entity card no longer shows the first
  camera entities as unavailable; the browser snapshot showed live toggle rows
  for detect, motion, recordings, snapshots, review alerts, and review
  detections.
- Verification stats showed the camera healthy at about `10 fps`, with
  `detection_enabled: false` at that moment. Turn on the HA `Detect` switch
  when object/person detection data should actively populate.
- The camera exposes Hikvision/ANNKE ISAPI endpoints. HA package
  `/config/packages/cam_01_annke_c500_package.yaml` adds:
  - `sensor.cam_01_annke_c500_ir_cut_mode`
  - `input_select.cam_01_annke_c500_ircut_mode`
  - `sensor.cam_01_annke_c500_supplemental_light_mode`
  - `input_select.cam_01_annke_c500_supplemental_light_mode`
  - `input_number.cam_01_annke_c500_white_light_brightness`
  - `input_number.cam_01_annke_c500_ir_light_brightness`
  - `sensor.cam_01_annke_c500_two_way_audio_enabled`
  - `input_boolean.cam_01_annke_c500_two_way_audio`
  - `input_number.cam_01_annke_c500_speaker_volume`
  - `input_number.cam_01_annke_c500_microphone_volume`
  - `script.cam_01_annke_c500_set_ircut_mode`
  - `script.cam_01_annke_c500_set_supplemental_light`
  - `script.cam_01_annke_c500_set_two_way_audio`
  - digest-auth `rest_command.cam_01_annke_c500_set_ircut`
  - digest-auth `rest_command.cam_01_annke_c500_set_supplemental_light`
  - digest-auth `rest_command.cam_01_annke_c500_set_two_way_audio`
- Live HA `/config/secrets.yaml` contains
  `cam_01_annke_c500_password`; do not copy the value into git.
- The CCTV dashboard entity panel now exposes IR-cut, supplemental light,
  guarded two-way audio settings, and Frigate status/control rows.
- User verified the IR-cut selector works. `Detect` is now on in Frigate.
- Camera capability probes found:
  - two-way audio endpoint exists but was left disabled after deployment
  - two-way audio supports `G.711ulaw` and `AAC`, with speaker/mic volume
  - supplemental light supports `eventIntelligence`, `colorVuWhiteLight`,
    `irLight`, and `close`, with white/IR brightness
  - `/ISAPI/System/IO/outputs` returns an empty output list, so no generic
    relay/siren output is exposed there
- The direct Frigate add-flow was tested before staging and returned the
  expected "does not support configuration via the UI" error because the custom
  integration had not yet been loaded by a restart.
- The stale ONVIF integration entry for `Camera 1 - d0:3b:f4:07:71:45` was
  removed from HA through the UI. Follow-up verification found zero ONVIF
  config entries, zero ONVIF entities, and no ONVIF device registry match for
  the camera MAC.

## 2026-07-02 live CCTV mobile views and HA HTTP/HTTPS audit

### CCTV dashboard changes

- Live HA storage dashboard changed:
  `/config/.storage/lovelace.cctv_feed`
- Backup made before the write:
  `/config/.storage/lovelace.cctv_feed.backup-mobile-views-20260702-*`
- Added `Mobile Balanced` view:
  - path: `cctv-mobile-balanced`
  - icon: `mdi:cellphone-play`
  - uses Advanced Camera Card with `live_provider: go2rtc`
  - explicitly uses Frigate/go2rtc stream `cam_01_annke_c500_sub`
  - keeps lightweight camera status, detect/record/snapshot toggles, IR-cut,
    supplemental-light mode, and IR brightness controls
- Added `Mobile Full Control` view:
  - path: `cctv-mobile-full-control`
  - icon: `mdi:cctv`
  - uses Advanced Camera Card with `live_provider: go2rtc`
  - explicitly uses Frigate/go2rtc stream `cam_01_annke_c500`
  - exposes Frigate controls plus IR-cut, supplemental light, and guarded
    two-way-audio settings
- The original primary CCTV view was left in place. The new views are additive
  so rollback can simply restore the timestamped backup or delete the two
  mobile views from HA dashboard storage.
- `ha core check` passed after the dashboard storage update. No HA restart was
  performed for this Lovelace-only change.

### HA HTTP/HTTPS dependency audit before TLS cutover

Pre-cutover state captured before the 2026-07-02 HTTPS migration:

- HA Core reported `ssl: false`; the active UI was still plain HTTP at
  `http://192.168.20.101:8123/`.
- Live protocol check:
  - `http://192.168.20.101:8123/` works.
  - `https://192.168.20.101:8123/` fails with the expected TLS/wrong-version
    behavior because HA TLS is not enabled yet.
- `/config/.storage/core.config` has `internal_url: null` and
  `external_url: null`; these need to be set deliberately during the TLS
  migration.
- `/config/.storage/http` has server port `8123`, `ssl_profile: modern`,
  `ip_ban_enabled: true`, `use_x_frame_options: true`, and only the default
  cast CORS origin. No active `ssl_certificate` / `ssl_key` configuration is
  present in `configuration.yaml`.
- `/ssl` contains existing MQTT/local certificate material plus HA HTTPS
  pre-flight files:
  - `/ssl/ca.crt`
  - `/ssl/ca.key`
  - `/ssl/fullchain.pem`
  - `/ssl/privkey.pem`
  - `/ssl/server.crt`
  - `/ssl/ha_https_preflight_fullchain.pem`
  - `/ssl/ha_https_preflight_privkey.pem`
- Mosquitto add-on publishes both plaintext and TLS listeners:
  `1883`, `1884`, `8883`, and `8884`. The HA MQTT integration itself is still
  configured to broker `192.168.20.101` on port `1883`; Frigate MQTT remains
  documented/live over TLS to Mosquitto on `8883`.
- The Frigate HA integration uses
  `http://192.168.30.20:5000`; this is Frigate's internal unauthenticated API
  path for HA and should not need to change when HA's own UI moves to HTTPS.
- The HA Companion App has an Android registration (`LE2123`). Because HA
  global URLs are unset, the phone's configured server URL and local CA trust
  must be handled explicitly during the HTTPS cutover.
- Lovelace dashboards:
  - `CCTV Feed` is storage mode at `/lovelace/cctv-feed`.
  - `Garage Dashboards` embeds `/local/ventsys-card-wrapper.html`, a same-origin
    relative URL that should survive an HTTP-to-HTTPS HA origin change.
  - `Monitoring` uses direct links to Grafana/Kuma HTTP URLs, not embedded
    iframes, so it is not directly blocked by HA HTTPS. Browser mixed-content
    rules matter only if these become embedded later.
- VentSys dashboard assets:
  - `ventsys-dashboard.html` derives the HA API/WebSocket scheme from
    `window.location.protocol`, so it should switch from `ws://` to `wss://`
    automatically when served from HTTPS.
  - `ventsys-config.js` contains only commented example `http://` and `ws://`
    values; do not enable those stale examples during migration.
- HA local LLM and service integrations use internal HTTP service URLs:
  - SearXNG: `http://192.168.20.102:8087`
  - Mealie: `http://192.168.20.102:9925`
  - llama.cpp: `http://192.168.20.104:8081/v1`
  These are HA server-side calls and do not block the HA UI HTTPS migration.
- Camera ISAPI package uses direct camera HTTP URLs at
  `http://192.168.30.21/...`. These are HA server-side REST calls and do not
  block the HA UI HTTPS migration.
- Monitoring HA package uses server-side `curl` checks to Grafana, InfluxDB and
  Uptime Kuma over HTTP. These are not browser mixed-content dependencies.
- Repo references that must be updated or consciously left as legacy during the
  migration:
  - `main/docs/procedures/ssl_tls_guide.md`
  - `main/docs/procedures/home_assistant_companion_app_guide.md`
  - `main/scripts/setup/proxmox/ha_vm_setup_guide.md`
  - `main/scripts/setup/proxmox/docker_host_setup_guide.md`
  - `main/scripts/monitoring/health_check.sh`
  - `main/scripts/monitoring/health_check.ps1`
  - `main/dashboards/ventsys-config.js.example`
  - `main/dashboards/ventsys_solar_screensaver.html`
  - this handoff

Security cleanup during audit:

- Removed stale live file `/config/www/codex_ssh_addons_probe.txt` because it
  contained add-on diagnostic output under the HA web-served `/local/` tree.
  Keep future diagnostics out of `/config/www/`.

## 2026-07-02 HA native HTTPS cutover with local CA

HA native HTTPS is now live. Do not redo the cutover in the next chat unless
validation proves drift.

Pre-change snapshots/backups:

- Restricted local snapshot:
  `C:\Users\Administrator\ha-live-snapshots\pre-ha-native-tls-20260702-102124`
- Snapshot includes:
  `/config/configuration.yaml`, `/config/.storage/core.config`,
  `/config/.storage/http`, `/config/.storage/lovelace.cctv_feed`,
  `/ssl/ca.crt`, `/ssl/fullchain.pem`, `/ssl/privkey.pem`,
  `/ssl/ha_https_preflight_fullchain.pem`, and
  `/ssl/ha_https_preflight_privkey.pem`.
- HA backup created before cutover:
  `pre-ha-native-tls-20260702-db-excluded`, slug `04da1c7d`, local location,
  database excluded.
- `ha mounts info` reported no active Supervisor mounts, so the prior
  `nas_backups` HA mount needs revalidation/restoration before relying on it.
- Live config backup before cutover:
  `/config/configuration.yaml.pre-native-tls-20260702-104713`.

Certificate findings:

- `/ssl/ha_https_preflight_fullchain.pem` and
  `/ssl/ha_https_preflight_privkey.pem` match each other and include expected
  SANs, but the cert is self-signed and does not chain to `/ssl/ca.crt`.
- `/ssl/fullchain.pem` and `/ssl/privkey.pem` match, chain to `/ssl/ca.crt`
  (`Home Local CA`), and include SANs for `192.168.20.101`,
  `homeassistant.home.local`, `homeassistant`, and
  `core-mosquitto.local.hass.io`.
- The cutover deliberately used `/ssl/fullchain.pem` and `/ssl/privkey.pem`.

Live HA config now includes:

```yaml
homeassistant:
  internal_url: https://192.168.20.101:8123
  packages: !include_dir_named packages

http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
  server_host: 0.0.0.0
  server_port: 8123
```

Post-restart state:

- User approved the HA restart before the access-risky cutover step.
- `ha core check` passed before restart.
- HA Core restarted successfully and reports `ssl: true` on port `8123`.
- Browser access to `https://192.168.20.101:8123/` returned HTTP 200 and the
  certificate chain is trusted by the Windows operator profile.
- HTTP `http://192.168.20.101:8123/` no longer serves HA, as expected.
- `external_url` remains unset deliberately.
- Windows CurrentUser Root trusts the local CA thumbprint
  `CC0542F01870C4EC9466658223570F47AAC80EE6`.
- User installed/trusted the local CA on the Android operator phone.

Validation completed:

- Android Companion App works against `https://192.168.20.101:8123`.
- CCTV `Mobile Balanced` view works on mobile with the substream
  `cam_01_annke_c500_sub`.
- CCTV `Mobile Full Control` view works on mobile with the main stream
  `cam_01_annke_c500`.
- Frigate API remained reachable from HA:
  `/api/version` returned `0.17.1-416a9b7`; `/api/stats` showed camera
  `cam_01_annke_c500` at about `10 fps` with detection enabled.
- Frigate/HACS/mobile_app config entries and Frigate camera/status entities
  remained present.
- VentSys static assets served over HTTPS:
  `/local/ventsys-dashboard.html` and `/local/ventsys-card-wrapper.html`.
- `ventsys-dashboard.html` still derives API/WebSocket scheme from
  `window.location.protocol`, so it should use HTTPS/WSS under the HA origin.
- Grafana `http://192.168.60.10:3000/api/health` returned healthy.
- Uptime Kuma `http://192.168.60.10:3001` returned the expected web response.
- Monitoring links remain direct HTTP links, not embedded iframes.

Rollback path:

1. Restore `/config/configuration.yaml.pre-native-tls-20260702-104713` over
   `/config/configuration.yaml`.
2. Run `ha core check`.
3. Restart HA Core.
4. Change Companion App server URL back to `http://192.168.20.101:8123` only if
   the rollback is actually performed.
5. Use the local snapshot and HA backup slug `04da1c7d` only if file-level
   restore is insufficient.

Optional cleanup if rolling back fully: remove the trusted Windows local CA
from CurrentUser Root by thumbprint. Do not remove phone CA trust unless the
phone no longer needs to trust this project CA for MQTT/HA/local services.

## 2026-07-02 mobile/Tailscale findings

- Initial Companion App failure was not a TLS certificate failure alone; the
  phone was trying to reach `https://192.168.20.101:8123` while Tailscale was
  off and it was not on a trusted routed home WiFi path.
- With Tailscale on, the app worked, but HA later logged intermittent mobile
  websocket drops from the docker-host route address `192.168.20.102`:
  `No PONG received after 27.5 seconds`.
- docker-host Tailscale prefs contained stale broad route
  `192.168.20.0/24`; user approved cleanup.
- docker-host Tailscale is now configured with only:
  `192.168.20.101/32,192.168.40.50/32,192.168.60.10/32`.
- The operator phone still used DERP relay rather than direct Tailscale UDP.
  DERP path latency was high enough to plausibly explain Companion App
  websocket drops.
- Five-minute mobile-data watch after route cleanup was clean; later normal
  WiFi with Tailscale still on produced another websocket drop.
- User switched to HomeAdmin WiFi with Tailscale off; HA app worked and a
  direct-watch window stayed clean.
- HomeMain also has an OpenWrt firewall allowance from LAN to
  `192.168.20.101:8123`, so at-home direct HA access should work there too.
- Tailscale is still the recommended off-WiFi remote access path. It is secure
  and appropriate; exposing HA directly to the public internet is not
  recommended.
- Optional DERP/direct-connect improvement for a future network-change window:
  forward UDP `41641` from the upstream internet router to the GL-MT6000 uplink
  address, then forward UDP `41641` on the GL-MT6000 to docker-host
  `192.168.20.102`.

## 2026-07-02 post-cutover stabilization follow-up

- Revalidated HA native HTTPS from the operator workstation:
  `https://192.168.20.101:8123/` returned HTTP `200`, plain
  `http://192.168.20.101:8123/` no longer served HA, and `ha core info`
  reported `ssl: true`, port `8123`, HAOS `2026.7.0`.
- `ha mounts info` still returned `mounts: []` and
  `default_backup_mount: null`.
- Attempted to recreate the HA Supervisor backup mount with the documented NFS
  target `192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/home-assistant`.
  The operation timed out; Supervisor logged `Mounting nas_backups did not
  succeed`, and host logs showed the systemd mount unit timing out.
- Follow-up reachability checks found the wider OMV path unhealthy: Proxmox
  `pvesm status` reported `omv-backups` inactive, `showmount -e
  192.168.40.50` returned `RPC: Unable to receive`, and Proxmox traffic to
  `192.168.40.50` failed via `192.168.10.1`.
- Router-side read-only checks found VLAN 40 (`br-lan.40`) up at
  `192.168.40.1/24`, but physical `lan4` was `NO-CARRIER` with `Link detected:
  no`; `lan3` and `lan1` had carrier. ARP for `192.168.40.50` stayed
  incomplete and no VLAN 40 DHCP lease was visible.
- User clarified OMV was no longer on router `lan4`; it needed to move to the
  managed switch on port 8. With approval, the GS1900 was configured for the
  intended architecture:
  - switch VLANs `10`, `30`, and `40` added
  - port 1 router uplink tagged for VLANs `10`, `30`, and `40`
  - port 2 camera access set to PVID 30 and untagged VLAN 30
  - port 8 OMV access set to PVID 40 and untagged VLAN 40
  - switch management moved to VLAN 10 via DHCP reservation
    `gs1900-switch` / `70:49:A2:0D:70:72` / `192.168.10.12`
  - router `lan3` changed from temporary untagged VLAN 30 to tagged trunk for
    VLANs 1/10/30/40
- Validation after the trunk cutover:
  - router pinged `192.168.10.12`, `192.168.30.108`, and `192.168.40.50`
  - router ARP showed switch on VLAN 10, camera on VLAN 30, OMV on VLAN 40
  - HA reached Frigate API `0.17.1-416a9b7`; camera stats showed
    `cam_01_annke_c500` at about `10 fps` with detection enabled
  - Proxmox `omv-backups` returned active
  - HA `nas_backups` was recreated, set as default, and manual backup
    `post-switch-trunk-nas-backups-20260703-db-excluded` wrote to
    `nas_backups` with slug `3e3b1ecb`
- User later confirmed CCTV feeds work both on home WiFi and on mobile data
  with Tailscale enabled.
- The GS1900 top-level Save action was invoked after the VLAN/trunk changes.
  The switch remained reachable afterward at `http://192.168.10.12/` with HTTP
  `200`; no reboot was performed.
- HA automatic backups were configured after the `nas_backups` mount was
  restored. Because HA's custom backup-settings controls could not be driven
  reliably through browser automation and the Supervisor token was not accepted
  by HA Core, user approved a direct `/config/.storage/backup` edit plus HA
  Core restart. Safety copy:
  `/config/.storage/backup.pre-auto-schedule-20260703-145639`. Final stored
  config: `automatic_backups_configured: true`, `agent_ids:
  ["hassio.nas_backups"]`, retention `copies: 14`, recurrence `daily`, time
  `03:00:00`. HA HTTPS returned `200` after restart and `ha mounts info`
  still showed `nas_backups` active/default.
- Frigate UI HTTPS was revalidated: `https://192.168.30.20:8971/api/version`
  returns `401` with auth enabled, and plain HTTP to port `8971` is rejected.
  HA still uses Frigate's internal `http://192.168.30.20:5000` API.
- Current recordings are local on CT 111: Frigate reports
  `/media/frigate/recordings` on ext4, backed by the Compose bind mount
  `/opt/frigate/storage:/media/frigate`. OMV recording storage remains a
  future cutover.
- First-camera IP cutover completed on 2026-07-03. The live router DHCP
  reservation for `D0:3B:F4:07:71:45` is `192.168.30.21`; the camera was
  rebooted through ISAPI, Frigate config was saved/restarted through the
  internal API, and the HA camera-control package was updated/reloaded via HA
  Core restart. Validation showed camera HTTP `200`, HA HTTPS `200`, Frigate
  `0.17.1-416a9b7`, Frigate config IPs `192.168.30.20 192.168.30.21`, and
  `cam_01_annke_c500` back at about `10 fps`.
- Fresh HA backup mount proof completed on 2026-07-03 after the first-camera IP
  cutover. `ha mounts info` showed `nas_backups` active, writable, and default.
  Backup `post-cutover-nas-backups-proof2-20260703-db-excluded`, slug
  `db7946c4`, wrote to `nas_backups` with
  `homeassistant_exclude_database: true` and size `81.51 MiB`. A previous
  proof attempt, slug `f9fb0ea6`, also wrote to `nas_backups` but did not
  exclude the database because the HA CLI boolean flag needed the explicit
  `--homeassistant-exclude-database=true` form.

## Likely follow-up docs/source work

- `main/configs/frigate/config.yml` now mirrors the accepted first-camera live
  layout using environment placeholders for RTSP and MQTT secrets; keep
  `main/configs/frigate/config-baseline.yml` as the no-camera fallback.
- Decide whether to keep the manual Advanced Camera Card asset install or
  replace it with a HACS-managed install once HACS catalog/repository lookup is
  behaving normally
- Consider a later pass on deterrence features (light/sound alarm) and any
  feasible talkback path, but only after HA + Frigate viewing is settled
