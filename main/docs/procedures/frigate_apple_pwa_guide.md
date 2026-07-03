---
title: Frigate Apple PWA Guide
description: End-to-end setup for Frigate as an Apple home-screen app, including local CA trust and Tailscale access
tags: [frigate, pwa, ios, ipad, certificate, mobile]
created: 2026-07-03
modified: 2026-07-03
type: procedure
status: active
---

# Frigate Apple PWA Guide

This guide installs the official Frigate web UI as a Progressive Web App on an
iPhone or iPad. Use this before evaluating third-party native clients such as
Viewu, Lumen or Kapal.

The Frigate PWA is the same authenticated Frigate UI that runs in the browser,
but launched from the Apple home screen with a cleaner app-like surface. It
keeps this project on the official Frigate path and avoids giving a third-party
mobile app Frigate credentials until there is a clear reason.

References:

- Frigate PWA install docs: <https://docs.frigate.video/configuration/pwa/>
- Frigate authentication docs:
  <https://docs.frigate.video/configuration/authentication/>

## Current Project State

- Frigate CT 111 is live at `192.168.30.20`.
- Frigate authenticated HTTPS UI is live at:

```text
https://192.168.30.20:8971
```

- Frigate internal unauthenticated API remains:

```text
http://192.168.30.20:5000
```

Only Home Assistant and trusted internal services should use the internal API.
Do not use port `5000` for Apple-device access.

- Frigate UI auth is enabled on port `8971`.
- Home Assistant CCTV views remain available through the HA Companion App.
- At-home access should use trusted WiFi direct.
- Off-WiFi access should use Tailscale.
- The full NVR VLAN is not advertised through Tailscale.

## Requirements

Apple device:

- iPhone or iPad.
- iOS/iPadOS 16.4 or newer for normal PWA installation support.
- Safari is the preferred browser for installation.
- Tailscale installed if off-WiFi access is needed.

Project services:

- Frigate reachable at `https://192.168.30.20:8971`.
- Frigate UI username and password available in the password manager.
- The local Frigate/HA certificate authority certificate is available as a
  public CA certificate file.

## Security Rules

- Copy only public certificate files to the Apple device.
- Never copy these private files to the Apple device or into git:
  - `/ssl/ca.key`
  - `/ssl/privkey.pem`
  - Frigate `.jwt_secret`
  - Frigate `/opt/frigate/.env`
  - Home Assistant long-lived tokens
  - WiFi passwords
- Use the Frigate authenticated HTTPS UI on port `8971`.
- Do not expose Frigate directly to the public internet.
- Do not enable camera vendor cloud/P2P as a shortcut for mobile viewing.
- Do not put raw camera RTSP URLs or RTSP credentials into a mobile app unless a
  later documented decision approves that.

## Access Model

Use the same Frigate URL in both local and remote cases:

```text
https://192.168.30.20:8971
```

At home:

- Connect to trusted home WiFi.
- Tailscale can stay off if the WiFi path can route to Frigate.

Away from home:

- Turn Tailscale on.
- Confirm the device can reach the home network routes needed for Frigate.
- Keep using the same Frigate HTTPS URL.

If Frigate is not reachable over Tailscale, do not broaden routes casually. The
next safe step is a deliberate route/firewall review for only the Frigate host
and required ports.

## Get The CA Certificate

Run on: Home Assistant / operator workstation.

The Apple device needs to trust the local CA that signed the Frigate HTTPS
certificate. The public CA certificate is safe to copy; the private CA key is
not.

Expected public CA file:

```text
/ssl/ca.crt
```

Ways to move only `ca.crt` to the Apple device:

- AirDrop the `ca.crt` file from a trusted Mac.
- Send it through a trusted private channel to the device.
- Copy it from Home Assistant Samba to the workstation, then transfer it to the
  Apple device.

Home Assistant Samba path from Windows:

```text
\\192.168.20.101\ssl\ca.crt
```

Do not copy anything named `ca.key`, `privkey.pem`, `.env`, or token files.

## Install And Trust The CA On iPhone Or iPad

Run on: Apple device.

1. Open the transferred `ca.crt` file.
2. Accept the prompt to install the configuration profile.
3. Open **Settings**.
4. Go to **General**.
5. Go to **VPN & Device Management**.
6. Select the downloaded certificate profile.
7. Tap **Install** and follow the prompts.
8. Go back to **Settings -> General**.
9. Open **About**.
10. Scroll to **Certificate Trust Settings**.
11. Enable full trust for the project local CA.
12. Confirm the warning only if the certificate name matches the expected
    project CA.

Expected project CA name:

```text
Home Local CA
```

If the certificate name is unexpected, stop and verify the file before trusting
it.

## Verify Certificate Trust

Run on: Apple device.

1. Connect to trusted home WiFi, or enable Tailscale if away from home.
2. Open Safari.
3. Browse to:

```text
https://192.168.30.20:8971
```

Expected result:

- Safari opens the Frigate login page.
- There is no untrusted certificate warning.
- The address bar shows HTTPS.

If Safari still warns about the certificate:

- Confirm the installed CA is enabled under **Certificate Trust Settings**.
- Confirm the URL is exactly `https://192.168.30.20:8971`.
- Confirm the certificate copied was `ca.crt`, not a server certificate with no
  CA trust role.
- Confirm the Apple device is on a network path that can reach Frigate.

## Log In To Frigate

Run on: Apple device.

1. Open Safari.
2. Go to:

```text
https://192.168.30.20:8971
```

3. Log in with the Frigate UI account.
4. If Safari asks whether to save the password, choose the operator's normal
   password-manager policy.
5. Confirm the live camera page loads.
6. Confirm events or recordings open if needed.

Use a Frigate viewer account for routine mobile viewing if one has been created.
Use `admin` only for administration and setup.

## Install The PWA

Run on: Apple device, after Safari login works.

1. Open Frigate in Safari:

```text
https://192.168.30.20:8971
```

2. Tap the **Share** button.
3. Tap **Add to Home Screen**.
4. Name it:

```text
Frigate
```

or:

```text
CCTV
```

5. Tap **Add**.
6. Return to the home screen.
7. Open the new Frigate/CCTV icon.
8. Confirm it opens Frigate without the normal Safari browser chrome.
9. Confirm live view works.

## Daily Use

At home:

1. Connect to trusted home WiFi.
2. Leave Tailscale off unless another remote-only route is needed.
3. Open the Frigate/CCTV home-screen icon.

Away from home:

1. Enable Tailscale.
2. Wait until Tailscale shows connected.
3. Open the Frigate/CCTV home-screen icon.
4. If it fails, open Safari and test the same URL directly.

For quick checks, Home Assistant Companion App CCTV views remain the preferred
operator dashboard. Use the Frigate PWA when you want the native Frigate event,
recording, live-view or admin interface.

## Optional: Create A Viewer User

Run on: Frigate UI.

After the PWA works, consider creating a non-admin account for routine mobile
viewing.

1. Open Frigate as an admin.
2. Go to **Settings -> Users**.
3. Add a user for Apple mobile viewing.
4. Give it viewer-style permissions unless admin rights are required.
5. Log out on the Apple device.
6. Log back in with the viewer account.
7. Confirm live view and recordings still meet the operator need.

Keep the admin account for configuration changes, password resets and recovery.

## Troubleshooting

### Safari Cannot Open Frigate

Check access path first:

- At home, confirm the Apple device is on trusted WiFi.
- Away from home, confirm Tailscale is connected.
- Confirm the URL uses HTTPS and port `8971`.
- Confirm Frigate is reachable from Home Assistant or a workstation.

Expected URL:

```text
https://192.168.30.20:8971
```

Wrong URLs:

```text
http://192.168.30.20:8971
http://192.168.30.20:5000
https://192.168.30.20:5000
```

### Certificate Warning Appears

The Apple device does not yet trust the project CA.

1. Reopen **Settings -> General -> About -> Certificate Trust Settings**.
2. Confirm `Home Local CA` is enabled.
3. If it is absent, reinstall `ca.crt`.
4. If the warning persists, verify Frigate is presenting the expected local
   certificate before proceeding.

### Add To Home Screen Is Missing

- Confirm the device is on iOS/iPadOS 16.4 or newer.
- Use Safari for first setup.
- Reload the Frigate page after logging in.
- Confirm the page was opened from `https://192.168.30.20:8971`.

### PWA Opens But Asks For Login Again

- Log in once from the PWA icon.
- Keep cookies/session data for Frigate.
- If the Frigate JWT secret changes or the admin password is reset again, log
  in again.

### Live View Is Slow Or Blank

- Try the Home Assistant mobile CCTV substream view to compare.
- Try Frigate's substream/live options in the web UI.
- Confirm the camera is still ingesting in Frigate.
- Avoid changing Frigate config from the mobile device during diagnosis unless
  a rollback path is clear.

### Works On WiFi But Not Away

- Confirm Tailscale is connected on the Apple device.
- Confirm the tailnet route to the Frigate host exists before changing router
  or firewall policy.
- Do not advertise all of VLAN 30 just for convenience.
- Preferred future remote route, if approved, is a narrow host route and
  firewall allowance for Frigate only.

## Validation Checklist

- [ ] Apple device is on iOS/iPadOS 16.4 or newer.
- [ ] `Home Local CA` installed.
- [ ] `Home Local CA` fully trusted in Certificate Trust Settings.
- [ ] Safari opens `https://192.168.30.20:8971` without a certificate warning.
- [ ] Frigate login succeeds.
- [ ] Live camera view works.
- [ ] PWA added to the home screen.
- [ ] PWA opens from the home-screen icon.
- [ ] PWA works on trusted home WiFi.
- [ ] PWA works off-WiFi with Tailscale, if remote access is required.
- [ ] Frigate admin password is stored in the password manager.
- [ ] Optional viewer account created for routine mobile viewing.

## What Not To Change During PWA Setup

- Do not restart Home Assistant.
- Do not restart Frigate unless validating a separate Frigate change.
- Do not change camera RTSP credentials.
- Do not change Frigate MQTT credentials.
- Do not change Tailscale advertised routes unless local testing proves the
  route is missing and a narrow route change is approved.
- Do not move recordings to OMV as part of mobile setup.
