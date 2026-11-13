---
title: Phase 03 - Home Assistant
description: HAOS image import, onboarding, core apps, MQTT TLS, packages, mobile access, time, HTTPS, and backup validation
tags: [install, home-assistant, mqtt]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 03 - Home Assistant

## Purpose

Create HAOS VM 100 from the official KVM/Proxmox image, complete onboarding,
install the required Home Assistant apps, validate MQTT over TLS, stage only
safe configuration packages, establish mobile access, apply router-derived
time, enable native HTTPS, and prove that a usable backup exists.

Frigate, Bambuddy, VentSys hardware, and local AI are integrated in later
phases. This phase prepares their Home Assistant foundations without pretending
that their hardware-dependent entities are live.

## Current-state callout

This manual is the blank-to-live rebuild path. As recorded in
[current-live-state.md](../../reference/current-live-state.md), the production
VM currently uses native HTTPS at `https://192.168.20.101:8123`; Mosquitto,
File Editor, Terminal & SSH, ESPHome Device Builder, the Companion App, and the
router-derived time path are live. Rebuild operators must still follow and
record every checkpoint below rather than treating that statement as proof for
a new VM.

## Runs on

- Admin laptop for image verification, transfer, browser checks, and phone work.
- Proxmox host shell for VM creation and disk import.
- Proxmox web UI/VM console for boot diagnosis.
- Home Assistant UI, initially at `http://192.168.20.101:8123/` and later at
  `https://192.168.20.101:8123/`.
- Home Assistant Terminal & SSH app for `/config` and HA CLI checks.
- Operator phone for Companion App and notification validation.

Home Assistant now calls add-ons **apps** in current UI text. Older screenshots
and project documents may still say **add-ons**; both terms refer to the same
Supervisor-managed components in this guide.

## Decision gates and stop conditions

Do not continue if:

- Phase 02 networking, storage, and local-console recovery are not validated;
- VM ID `100` already exists and its ownership is unknown;
- the HAOS image is not the official KVM/Proxmox `.qcow2.xz` asset or its
  SHA-256 does not match the value published with that exact release asset;
- VLAN 20 cannot provide DHCP, gateway, DNS, and NTP reachability;
- `<HA_ADMIN_PASSWORD>` and `<MQTT_PASSWORD>` have no approved password-manager
  records;
- a configuration change is about to be restarted without `ha core check`;
- HACS, a custom integration, or public exposure is proposed before the core
  installation has a downloaded or external backup.

Native HTTPS is an approved project design, but its cutover remains a recovery
gate: retain VM console access and a known-good `configuration.yaml` copy until
the HTTPS browser and Companion App checks pass.

## Prerequisites

- Phase 02 complete.
- Proxmox `local-lvm` active with at least 32 GiB available for VM 100.
- Router reservation and firewall plan for VM 100 on VLAN 20.
- Official HAOS KVM/Proxmox release asset and published SHA-256 available.
- Password manager contains records for the inputs below.
- Local `Home Local CA` certificate workflow available from
  [ssl_tls_guide.md](../../procedures/ssl_tls_guide.md).

## Inputs

- `<HA_ADMIN_PASSWORD>`
- `<MQTT_PASSWORD>`
- `<HA_LONG_LIVED_TOKEN>` only for an integration that cannot use a narrower
  supported credential; do not create it during basic onboarding.
- `<ADMIN_SSH_PUBLIC_KEY>` for the Terminal & SSH app if remote shell access is
  deliberately enabled.

## 1. Download and verify the HAOS image

Use the official Home Assistant **KVM/Proxmox** asset. The filename normally
ends in `.qcow2.xz`. Record the release, filename, download URL, published hash,
and verification date in the rebuild log. Do not hard-code a release number in
this manual because HAOS changes independently from the project repository.

Run on: Admin laptop.

```powershell
$haosArchive = 'C:\Users\Admin\Downloads\haos_ova-VERSION.qcow2.xz'
if (-not (Test-Path -LiteralPath $haosArchive)) {
    throw "HAOS archive not found: $haosArchive"
}
$haosHash = (Get-FileHash -LiteralPath $haosArchive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($haosHash -notmatch '^[0-9a-f]{64}$') {
    throw 'Calculated HAOS SHA-256 is malformed.'
}
$haosHash
```

`VERSION` is a filename cue, not a secret placeholder. Replace the whole path
with the actual downloaded filename. Expected output is one 64-character
lowercase hexadecimal value. It must match the SHA-256 shown for that exact
asset on the official Home Assistant OS release page.

If the hashes differ, delete the archive, redownload it from the official
release, and repeat the calculation. Do not decompress or import a mismatched
image.

## 2. Transfer and decompress the image

Run on: Admin laptop.

```powershell
scp -p -- $haosArchive root@192.168.10.10:/var/lib/vz/template/iso/
```

Expected result: `scp` reaches `100%` and exits without an error.

Run on: Proxmox host shell.

```bash
apt-get update
apt-get install -y xz-utils
xz --version
```

Expected result: package metadata refreshes without repository errors and `xz`
prints its version.

Run on: Proxmox host shell.

```bash
mapfile -t haos_archives < <(
  find /var/lib/vz/template/iso -maxdepth 1 -type f -name 'haos_ova-*.qcow2.xz' -print
)
if [ "${#haos_archives[@]}" -ne 1 ]; then
  printf 'Expected exactly one HAOS archive; found %s.\n' "${#haos_archives[@]}" >&2
  exit 1
fi
haos_archive="${haos_archives[0]}"
test -s "$haos_archive"
xz -dk "$haos_archive"
haos_image="${haos_archive%.xz}"
qemu-img info "$haos_image"
```

Expected output characteristics:

- `test -s` returns exit code `0`;
- `xz` returns without a corruption error;
- `qemu-img info` reports `file format: qcow2` and a non-zero virtual size.

If more than one `haos_ova-*.qcow2.xz` file exists, the command substitution is
ambiguous. Stop, list the directory, and set `haos_archive` to one exact file.
Do not delete older images until the selected release has booted and the rebuild
record contains its hash.

## 3. Create VM 100 and import the HAOS disk

First prove that VM ID 100 is free.

Run on: Proxmox host shell.

```bash
if qm status 100 >/dev/null 2>&1; then
    echo 'STOP: VM ID 100 already exists.' >&2
    exit 1
fi
pvesm status | grep -E '^(Name|local-lvm[[:space:]])'
```

Expected result: the guard does not print `STOP`, and `local-lvm` reports
`active` with adequate free space.

Run on: Proxmox host shell.

```bash
qm create 100 \
  --name home-assistant \
  --ostype l26 \
  --machine q35 \
  --bios ovmf \
  --cores 2 \
  --memory 6144 \
  --scsihw virtio-scsi-pci \
  --net0 virtio,bridge=vmbr0,tag=20 \
  --onboot 1

qm set 100 --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0
qm importdisk 100 "$haos_image" local-lvm
qm config 100 | grep -E '^(bios|cores|efidisk0|machine|memory|name|net0|onboot|scsihw|unused[0-9]+):'
```

Expected import output ends with a line resembling:

```text
Successfully imported disk as 'unused0:local-lvm:vm-100-disk-1'
```

The unused slot and volume suffix can differ. Read the actual `unusedN` line;
do not assume `unused0` or `disk-1`.

Run on: Proxmox host shell.

```bash
unused_line="$(qm config 100 | awk -F': ' '/^unused[0-9]+:/{print; exit}')"
test -n "$unused_line" || { echo 'Imported HAOS disk was not found.' >&2; exit 1; }
unused_key="${unused_line%%:*}"
imported_volume="${unused_line#*: }"
imported_volume="${imported_volume%%,*}"

qm set 100 --scsi0 "${imported_volume},discard=on,ssd=1"
qm set 100 --boot order=scsi0
qm config 100
```

Expected configuration characteristics:

- `bios: ovmf`, `machine: q35`, and an EFI disk are present;
- `scsi0` references the imported HAOS volume and is 32 GiB by default;
- `boot: order=scsi0` is present;
- `net0` uses `virtio`, `bridge=vmbr0`, and `tag=20`;
- memory is `6144` MiB and cores are `2`;
- the imported disk no longer remains only as an `unusedN` entry.

If the imported image reports a smaller disk, expand `scsi0` to 32 GiB from the
Proxmox **Hardware -> Disk Action -> Resize** UI and verify the resulting size.
Never shrink an imported disk. If attaching or resizing fails, keep the VM
stopped. Inspect `qm config 100` and `pvesm list local-lvm --vmid 100`; never
import repeatedly until unexplained unused disks accumulate.

## 4. First boot and network checkpoint

Run on: Proxmox host shell.

```bash
qm start 100
qm status 100
```

Expected result: `qm status 100` reports `status: running`. Use
**VM 100 -> Console** in the Proxmox UI to observe HAOS boot and the address
banner.

Run on: Admin laptop.

```powershell
$deadline = (Get-Date).AddMinutes(20)
do {
    $probe = Test-NetConnection 192.168.20.101 -Port 8123 -WarningAction SilentlyContinue
    if ($probe.TcpTestSucceeded) { break }
    Start-Sleep -Seconds 15
} while ((Get-Date) -lt $deadline)

if (-not $probe.TcpTestSucceeded) {
    throw 'Home Assistant onboarding did not reach TCP 8123 within 20 minutes.'
}
'Home Assistant onboarding port is reachable.'
```

Expected output:

```text
Home Assistant onboarding port is reachable.
```

If the port never opens, inspect the VM console first. Confirm that `net0` is
VLAN 20, the router reservation matches the VM MAC from `qm config 100`, DHCP
is active on VLAN 20, and the VM clock is sane. Do not change HA configuration
before HAOS itself has a valid address.

## 5. Complete onboarding and establish recovery identities

Run on: Home Assistant UI.

1. Open `http://192.168.20.101:8123/` during initial onboarding.
2. Create the named owner account using `<HA_ADMIN_PASSWORD>` from the password
   manager. Avoid a generic shared account name when attribution matters.
3. Set the correct home location, elevation, metric units, and
   `Europe/London` time zone.
4. Review discovered devices; do not accept an integration merely because it
   appears.
5. Enable TOTP multi-factor authentication for the owner and store its recovery
   material outside Home Assistant.
6. Create a separate emergency admin identity with a distinct password and
   TOTP method. Do not use it for daily operation.
7. Sign out and prove both identities can sign in before depending on either.

Expected result:

- the Overview dashboard loads;
- **Settings -> System -> Repairs -> System information** reports HAOS,
  Supervisor, and Core versions;
- the owner and emergency account each pass an independent sign-in;
- no recovery code or password is stored in Git or screenshots.

## 6. Make the VLAN 20 address explicit

The router reservation is the canonical address assignment. HAOS may also use
a matching manual address, but the two records must agree.

Run on: Home Assistant UI.

1. Open **Settings -> System -> Network**.
2. Select the wired adapter and choose IPv4 manual configuration.
3. Set `192.168.20.101/24`, gateway `192.168.20.1`, and DNS
   `192.168.20.1`.
4. Save and wait for the UI to reconnect at the same address.

Run on: Admin laptop.

```powershell
Resolve-DnsName homeassistant.home.local -Server 192.168.10.1
Test-NetConnection 192.168.20.101 -Port 8123
```

Expected result: DNS returns `192.168.20.101` and TCP 8123 succeeds. If the UI
does not return, use the Proxmox VM console and HA CLI network commands to
restore DHCP or correct the manual gateway; do not clone/start another VM 100
with the same address.

## 7. Install the required Home Assistant apps

Run on: Home Assistant UI.

Open **Settings -> Apps** (called **Add-ons** in older UI versions), then install
and start these in order:

| App | Required configuration | Start/boot policy | Acceptance evidence |
|---|---|---|---|
| Mosquitto broker | HA `mqtt` service user; TLS certificate/key later in this phase | start now; watchdog and start-on-boot | log shows broker running; MQTT integration connects |
| File Editor or Studio Code Server | management users only | start on boot | can read `/config/configuration.yaml` |
| Terminal & SSH | approved public key; password login disabled if network SSH is enabled | start on boot | HA CLI works; `/config` is visible |
| ESPHome Device Builder | no device adoption yet | start on boot | dashboard opens without adopting hardware |

Samba is optional. If installed, use a separate Samba credential from the HA
login and restrict it to trusted management clients. The Samba credential must
be added to the secrets ledger before use; do not reuse `<HA_ADMIN_PASSWORD>`.

Run on: Home Assistant Terminal & SSH app.

```bash
ha core info
ha addons list
test -d /config && echo '/config is available'
```

Expected output characteristics:

- `ha core info` reports `state: running`;
- the app list includes Mosquitto, an editor, Terminal & SSH, and ESPHome;
- the final line is `/config is available`.

If the UI names or slugs differ in a later release, record what was installed
and validate by purpose and publisher rather than copying a stale slug.

## 8. Configure Mosquitto and the MQTT integration

Create a dedicated non-admin HA user named `mqtt` with `<MQTT_PASSWORD>`. Do
not use the owner account from devices. Configure the Mosquitto app to use the
project local certificate files:

Run on: Home Assistant UI.

1. Confirm `/ssl/fullchain.pem`, `/ssl/privkey.pem`, and `/ssl/ca.crt` are the
   intended local-CA files before enabling TLS.
2. Configure Mosquitto with `certfile: fullchain.pem`,
   `keyfile: privkey.pem`, `require_certificate: false`, and no plaintext
   credential copied into app YAML.
3. Start/restart Mosquitto and inspect its log for TLS listener errors.
4. Add the MQTT integration using broker `192.168.20.101`, port `8883`, user
   `mqtt`, `<MQTT_PASSWORD>`, and CA validation.
5. Confirm the integration reports connected.

Do not expose or reintroduce a router firewall exception for plaintext port
`1883`. A temporary localhost-only bootstrap is acceptable only when recorded
and removed before completion.

### MQTT success and failure test

Use Home Assistant's MQTT integration UI so the password is not exposed in
shell history or a process list.

Run on: Home Assistant UI -> Settings -> Devices & services -> MQTT -> Configure.

1. Start listening on `test/install`.
2. Publish payload `TLS_OK` to `test/install`.
3. Confirm the listener displays the same topic and payload.
4. In a separate, temporary client profile, deliberately use an incorrect
   password once and confirm connection is rejected.
5. Delete the temporary invalid profile and confirm the valid integration
   remains connected.

Expected success evidence:

```text
topic: test/install
payload: TLS_OK
```

Expected failure evidence is an authentication/connection rejection, not a
successful anonymous connection. Never paste either real password into the
rebuild log.

## 9. Enable package directories safely

Do not replace a fresh `configuration.yaml` with the repository reference file.
Preserve `default_config:` and existing includes. Add the package include to
the existing top-level `homeassistant:` block, or create that block only if it
does not exist.

Run on: Home Assistant Terminal & SSH app.

```bash
checkpoint="$(date +%Y%m%dT%H%M%S)"
cp -a /config/configuration.yaml "/config/configuration.yaml.pre-packages-${checkpoint}"
mkdir -p /config/packages /config/themes /config/www
touch /config/automations.yaml /config/scripts.yaml /config/scenes.yaml
ls -l "/config/configuration.yaml.pre-packages-${checkpoint}"
```

Expected result: the timestamped backup exists and is non-zero.

Ensure this key exists exactly once:

Run on: Home Assistant UI -> File Editor or Studio Code Server.

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Keep these normal fresh-install lines if present:

Run on: Home Assistant UI -> File Editor or Studio Code Server.

```yaml
default_config:
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml
```

Run on: Home Assistant Terminal & SSH app.

```bash
ha core check
```

Expected output includes:

```text
Configuration check finished successfully.
```

If the check names a duplicate key, missing include, or YAML line, restore the
timestamped file or correct only the named error. Do not restart until the check
passes.

## 10. Stage project files without activating missing hardware

Copy only files whose prerequisites are satisfied:

| Source | HA destination | Rebuild gate |
|---|---|---|
| `ventsys/ventsys_bundle_updated/ventsys_ha_package.yaml` | `/config/packages/ventsys_ha_package.yaml` | core package may be staged; hardware entities remain unavailable |
| `ventsys/ventsys_bundle_updated/ventsys_ha_scripts.yaml` | `/config/packages/ventsys_ha_scripts.yaml` | stage only after reviewing entity references |
| `dashboards/ventsys-dashboard.html` | `/config/www/ventsys-dashboard.html` | never copy a real token back to the repository |
| `configs/home-assistant/bambuddy_p1s_package.yaml` | deferred | requires real `<P1S_SERIAL>` and Phase 05 workload |
| `ventsys_ha_optional.yaml` | deferred | requires confirmed pressure/PID entities |
| `configs/home-assistant/automations.yaml` | deferred | safety devices and test plan must exist first |

The preferred copy route is the trusted Samba share if the optional Samba app
has been deliberately configured. File Editor is the fallback. Do not paste
secrets through chat or commit live copies.

Run on: Home Assistant Terminal & SSH app after each copy batch.

```bash
find /config/packages /config/www -maxdepth 1 -type f -printf '%p %s bytes\n' | sort
ha core check
```

Expected result: copied files are non-zero and the configuration check succeeds.
Unavailable hardware entities may be expected; YAML/parser errors are not.

Run on: Home Assistant Terminal & SSH app.

```bash
ha core restart
ha core info
```

Expected result: Core returns to `state: running`. Review **Settings -> System
-> Logs** and record any package warning that is accepted as hardware-pending.

## 11. Apply router-derived HAOS time

The source template is
`configs/home-assistant/haos-timesyncd-router.conf`. Prepare supported HAOS
`CONFIG` import media containing `timesyncd.conf`, then import it. This is an OS
setting, not `/config/configuration.yaml`.

Run on: Home Assistant Terminal & SSH app.

```bash
ha os import
ha host reboot
```

Expected result: the import command reports success and the VM reboots. Reopen
the UI before validation.

Run on: Home Assistant Terminal & SSH app after reboot.

```bash
date --iso-8601=seconds
ha host info
```

Expected result: the timestamp, time zone/offset, and actual wall clock agree;
the host reports healthy. If time is wrong, validate UDP 123 and router NTP at
`192.168.20.1` before changing ESPHome or certificate settings. Reimport the
known-good template or temporarily return to the HAOS default time source as the
rollback, then record the deviation.

## 12. Create the pre-hardening backup

Create a local backup before native HTTPS, HACS, or custom integrations. The UI
is preferred because backup encryption and emergency-kit handling evolve.

Run on: Home Assistant UI.

1. Open **Settings -> System -> Backups**.
2. Create a backup named `pre-ha-hardening-YYYYMMDD`.
3. Include configuration, SSL material, and required app data.
4. Enable encryption and store the emergency-kit/recovery material outside HA.
5. Download or copy the backup to a different system before continuing.

Run on: Home Assistant Terminal & SSH app.

```bash
ha backups list
```

Expected result: the named backup has a slug, creation timestamp, and non-error
state. A row in this list proves catalog presence only; the external copy and
later isolated restore prove recoverability.

When Phase 06 storage is live, add network storage of type **Backup** for OMV,
select it as an automatic-backup location, create a fresh backup, and prove the
file exists on OMV. The current project target is named `nas_backups`; exact NFS
paths belong to Phase 06 and the backup strategy rather than being guessed here.

## 13. Enable native HTTPS with the local CA

Follow the approved local-CA option in
[ssl_tls_guide.md](../../procedures/ssl_tls_guide.md). The active certificate
must cover `192.168.20.101` and `homeassistant.home.local`; private keys remain
under `/ssl` and never enter Git.

Run on: Home Assistant Terminal & SSH app.

```bash
test -s /ssl/fullchain.pem
test -s /ssl/privkey.pem
test -s /ssl/ca.crt
openssl x509 -in /ssl/fullchain.pem -noout -subject -issuer -dates -ext subjectAltName
cp -a /config/configuration.yaml "/config/configuration.yaml.pre-https-$(date +%Y%m%dT%H%M%S)"
```

Expected output shows the intended issuer, valid date range, and SANs containing
the HA IP/hostname. The private key is checked for existence only and is never
printed.

Add or reconcile these settings without creating duplicate top-level keys:

Run on: Home Assistant UI -> File Editor or Studio Code Server.

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

Run on: Home Assistant Terminal & SSH app.

```bash
ha core check
ha core restart
```

Expected result: configuration validation succeeds before Core restarts.

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.101 -Port 8123
$response = Invoke-WebRequest -Uri 'https://192.168.20.101:8123/' -MaximumRedirection 0
[pscustomobject]@{ StatusCode = $response.StatusCode; ContentType = $response.Headers.'Content-Type' }
```

Expected result: TCP succeeds and the request returns an HTML response without
using `-SkipCertificateCheck`. That proves the admin laptop trusts the local CA.

### HTTPS rollback rehearsal

Before closing the VM console, rehearse the recovery decision:

1. Confirm the exact `configuration.yaml.pre-https-*` filename exists.
2. Confirm VM 100 console access reaches the HA CLI even if the browser does not.
3. If HTTPS fails, use the File Editor/Samba path if available or the supported
   HAOS console access path to restore the backup file, then restart Core.
4. Reopen the former HTTP URL only long enough to correct certificate trust or
   configuration; do not leave an undocumented plaintext rollback live.

Expected recovery evidence is a successful `ha core check`, Core returning to
`state: running`, and the chosen UI URL loading. Merely retaining a backup file
does not count as a tested recovery path.

## 14. Onboard the Companion App

Use
[home_assistant_companion_app_guide.md](../../procedures/home_assistant_companion_app_guide.md).

Run on: Operator phone.

1. Install and trust only `/ssl/ca.crt`, never a private key.
2. Confirm the phone browser trusts `https://192.168.20.101:8123`.
3. Install the official Home Assistant Companion App and sign in using an
   operator identity with 2FA.
4. Allow notifications and give the device a stable, non-secret name.
5. Test direct trusted Wi-Fi first; add the approved Tailscale path only after
   Phase 05 establishes it.

Run on: Home Assistant UI -> Developer Tools -> Actions.

Send a basic notification and the acknowledgement test defined in the Companion
App guide. Expected result: the phone receives the notification and tapping the
action emits `mobile_app_notification_action` with the expected action ID.
Keep persistent HA notifications as the safety fallback.

## 15. HACS decision gate

HACS is optional and enhancement-only. Do not install it during core recovery.
Install only when:

- Core, MQTT, required apps, HTTPS, Companion App, and backup checks pass;
- a current backup is stored outside VM 100;
- every selected custom item has an owner, purpose, source, version record,
  update plan, and removal/rollback note;
- no safety-critical VentSys behavior depends solely on a HACS card or custom
  integration.

Use [hacs-enhancement-roadmap.md](../reference/hacs-enhancement-roadmap.md) for
the approval record. Do not pipe an unaudited remote installer directly into a
shell from this phase manual.

Expected deferral result: Home Assistant remains fully usable without HACS.
If an approved HACS item breaks after an update, remove/disable that item and
restore its pre-change backup without rolling back unrelated HA core state.

## 16. Backup restore proof

A backup is not proven by creation alone. Perform the native-backup restore test
in a disposable, isolated HAOS VM during the rebuild acceptance window:

1. Create a fresh disposable HAOS VM with a temporary ID and no production NIC,
   or attach it only to a deliberately isolated test network.
2. Start onboarding and choose restore from backup.
3. Upload the external copy of `pre-ha-hardening-YYYYMMDD` and provide its
   recovery key.
4. Allow restoration to complete; do not attach the production VLAN while VM
   100 is running.
5. From the isolated console, verify the restored configuration and required
   app data are present and Core reaches a running state.
6. Shut down and remove the disposable VM only after recording the test ID,
   backup slug, date, and result.

Never boot two restored HA instances on VLAN 20 with the same identity/IP. This
drill is approval-gated because it creates and removes a temporary VM. Until it
passes, record the backup as **created and externally copied, restore unproven**.

Expected recovery evidence:

- restore operation reports completion;
- restored Core reaches a running state on the isolated console;
- expected `/config`, `/ssl`, and required app data are present;
- production VM 100 remains unchanged and singular on VLAN 20.

## End-of-phase validation

Run on: Home Assistant Terminal & SSH app.

```bash
ha core check
ha core info
ha host info
ha addons list
ha backups list
date --iso-8601=seconds
```

Expected result: configuration check succeeds, Core/host/add-ons are healthy,
at least one current backup is listed, and the timestamp agrees with the
router-derived local time.

Run on: Admin laptop.

```powershell
Resolve-DnsName homeassistant.home.local -Server 192.168.10.1
Test-NetConnection 192.168.20.101 -Port 8123
Invoke-WebRequest -Uri 'https://192.168.20.101:8123/' -MaximumRedirection 0 | Select-Object StatusCode
```

Expected result:

- configuration check succeeds and Core is running;
- HAOS/Supervisor health has no unexplained error;
- required apps are installed and running;
- MQTT listen/publish succeeds over TLS and invalid authentication is rejected;
- DNS and trusted HTTPS succeed from an approved client;
- owner, emergency admin, and Companion App sign-ins are proven;
- a current backup exists outside VM 100;
- the isolated restore proof is recorded, or explicitly marked as the remaining
  recovery acceptance gate;
- HACS is either deliberately deferred or every custom item has a rollback note.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| HAOS hash mismatch | Delete and redownload the exact official asset. | Calculated and published hashes match. |
| VM 100 already exists | Stop; identify ownership and current backup state. | No production VM is overwritten or duplicated. |
| Imported disk remains unused | Keep VM stopped; inspect `qm config` and `pvesm list`; attach the one imported volume. | `scsi0` owns the HAOS volume and boot order points to it. |
| HAOS does not boot | Use Proxmox console; verify OVMF/q35, imported disk, and boot order. | Console reaches HAOS banner. |
| TCP 8123 never opens | Verify VM VLAN tag/MAC, router lease, gateway, DNS, and HAOS console. | Onboarding port becomes reachable without weakening firewall scope. |
| Manual IP loses access | Use HAOS console to return to DHCP or correct gateway/DNS. | DNS and TCP tests pass at `.101`. |
| Required app will not start | Inspect its log and configuration; do not install an unofficial substitute silently. | App reports running and its purpose-specific check passes. |
| MQTT valid login fails | Check broker cert/SAN/time, dedicated user, port 8883, and CA trust. | TLS publish/listen succeeds. |
| MQTT invalid login succeeds | Stop; anonymous access or auth is misconfigured. | Wrong credentials are rejected and valid integration still connects. |
| `ha core check` fails | Fix the named YAML/include/certificate path or restore the timestamped file. | Check succeeds before restart. |
| Core fails after package restart | Restore the pre-packages file and remove only the new batch. | Core runs; add files back one at a time. |
| HAOS time is wrong | Validate router NTP and UDP 123; reimport known-good config or revert to default time source. | Wall clock and certificate validation agree. |
| HTTPS UI fails | Use VM console plus the pre-HTTPS config; distinguish certificate trust from server failure. | Selected URL loads and Core is running. |
| Companion push fails | Check phone CA trust, app login, notification permission, and exact notify action. | Basic and actionable tests both pass. |
| Backup restore fails in isolated VM | Preserve production; inspect archive/recovery key and retry with a fresh disposable VM. | A complete isolated restore is recorded. |
| HACS item breaks HA | Disable/remove only the custom item or restore its pre-change backup. | Core works without the optional item. |

## Completion checklist

- [ ] Official HAOS KVM/Proxmox image hash matches its release asset.
- [ ] VM 100 matches the canonical CPU, RAM, disk, OVMF/q35, VLAN, and startup settings.
- [ ] HAOS boot and initial HTTP onboarding checkpoints pass.
- [ ] Owner and emergency admin identities with 2FA are independently proven.
- [ ] Router reservation, HAOS address, gateway, DNS, and NTP agree.
- [ ] Mosquitto, editor, Terminal & SSH, and ESPHome apps pass their acceptance checks.
- [ ] MQTT succeeds over TLS and rejects invalid authentication.
- [ ] Package include and each staged file batch pass `ha core check`.
- [ ] Hardware-dependent packages and integrations remain correctly deferred.
- [ ] HAOS router-time import is validated or explicitly deferred with reason.
- [ ] Local backup is encrypted, externally copied, and listed by HA.
- [ ] Native HTTPS passes trusted-client validation and its rollback path is rehearsed.
- [ ] Companion App basic/actionable notification tests pass; persistent fallback remains.
- [ ] HACS is deferred or its decision gate and per-item rollback records are complete.
- [ ] Native backup passes an isolated restore proof, or is explicitly recorded as restore-unproven.

Continue to [Phase 04 - Frigate](04-frigate.md) after the stable HA core,
MQTT, HTTPS, mobile, and backup foundations are accepted. Phase 06 completes
the OMV-backed automatic backup target; Phase 05A adds optional local AI voice.
