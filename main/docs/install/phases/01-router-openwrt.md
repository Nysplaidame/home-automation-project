---
title: Phase 01 - Router OpenWrt
description: Fresh OpenWrt, first-flight and full router deployment with recovery proof
tags: [install, router, openwrt]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 01 - Router OpenWrt

## Purpose

Build the GL-MT6000 network foundation: VLANs, DHCP reservations, local DNS,
firewall policy, router-local NTP, AdGuard-first DNS forwarding with public
fallback, and dormant WireGuard recovery access.

Router-deploy is router-only. It owns OpenWrt network, DHCP, local DNS,
firewall, wireless, dormant WireGuard, router-local NTP, generated artifacts,
snapshots, and validation. It never deploys Docker services, OMV, Tailscale
authentication, Home Assistant apps, monitoring state, or application data.

## Current-state callout

The physical first-flight layout was deployed and smoke-tested previously,
including recovery access on `lan5`. The 2026-08-09 source audit is currently
blocked by the missing invariant
`architecture.docker_host_tailscale_egress_rule_present`; full compilation also
contains unresolved WireGuard, MAC-address, and Wi-Fi placeholders. Do not run a
new deployment until lint and both compile profiles pass from current source.

## Runs on

- Admin laptop in an elevated PowerShell terminal from the project checkout.
- GL-MT6000 local recovery UI or console for fresh firmware installation.
- OpenWrt router over SSH, first at `192.168.1.1` through `lan5`, then at
  `192.168.10.1` through Management `lan2`.

## Stop conditions

- The downloaded image target, model, image type, or SHA-256 digest is not an
  exact match.
- `lan5` recovery and a local router configuration backup are not proved.
- Lint or compile reports an error, invariant failure, or unresolved placeholder.
- The deploy identity check names a different router.
- The watchdog cannot be armed or the pre-deploy snapshot cannot be pulled back.
- A denied inter-VLAN path starts working after deployment.

## Prerequisites

- Phase 00 is complete, including router serial/model and port labels.
- Laptop Ethernet is connected directly to `lan5`; Wi-Fi and other Ethernet
  adapters are disabled during first flight.
- Latest stable firmware for the exact `GL.iNet GL-MT6000` target and its
  published SHA-256 digest have been obtained from the official OpenWrt image
  selector.
- `<ROUTER_ROOT_PASSWORD>` is ready, and deployment SSH keys can be stored in
  the toolkit's ignored `keys/` directory.
- Full-profile Wi-Fi, WireGuard, and real device-MAC values are available before
  the full deployment; first flight deliberately strips or disables them.

## Inputs

- `<OPENWRT_IMAGE_PATH>`
- `<OPENWRT_IMAGE_SHA256>`
- `<ROUTER_ROOT_PASSWORD>`
- `<WIFI_MAIN_PASSWORD>`
- `<WIFI_IOT_PASSWORD>`
- `<WIFI_GUEST_PASSWORD>`
- `<WIREGUARD_SERVER_PRIVATE_KEY>`

All placeholders must be resolved through the
[secrets placeholder ledger](../reference/secrets-placeholder-ledger.md), never
through tracked files or terminal output.

## 1. Verify the firmware image

Use a `factory` image only for a vendor-supported stock-to-OpenWrt path. Use a
`sysupgrade` image only when the router is already running compatible OpenWrt.
Never rename one image type to impersonate the other.

Run on: Admin laptop in PowerShell.

```powershell
Get-FileHash -Algorithm SHA256 '<OPENWRT_IMAGE_PATH>'
```

Expected result: `Hash` exactly equals `<OPENWRT_IMAGE_SHA256>` and the filename
identifies `glinet_gl-mt6000`. Letter case does not matter; every hexadecimal
character does.

Recovery: delete a mismatched or ambiguous image and download it again from the
official selector. Do not flash it and do not use a digest copied from a third
party.

## 2. Install fresh OpenWrt and establish recovery access

From stock firmware, use the vendor-supported local firmware/recovery UI with
the correct factory image. From compatible OpenWrt, upload the verified
sysupgrade image in LuCI under **System > Backup / Flash Firmware**. For a true
clean rebuild, do not retain settings from a different release or vendor
layout.

After reboot, renew the laptop DHCP lease on `lan5` and set the root password in
LuCI before enabling SSH key access.

Run on: Admin laptop in PowerShell after the router reboots.

```powershell
ipconfig /release
ipconfig /renew
Test-Connection 192.168.1.1 -Count 4
ssh root@192.168.1.1 "ubus call system board; ip -brief link"
```

Expected result: the laptop receives `192.168.1.x/24`, four probes return, the
board response identifies the expected model/OpenWrt release, and physical
interfaces `wan`, `lan1` through `lan5` exist. Stop if the board identity or
port set differs.

Recovery: wait one full boot cycle, reconnect only `lan5`, renew DHCP, and use
the device's documented recovery UI. A failed flash is a firmware recovery
problem; do not attempt router-deploy until the clean LuCI/SSH baseline works.

## 3. Capture the clean baseline

Run on: OpenWrt router over SSH at `192.168.1.1`.

```sh
ubus call system board
ip -brief link
df -h /overlay
sysupgrade -b /tmp/openwrt-clean-baseline.tar.gz
ls -lh /tmp/openwrt-clean-baseline.tar.gz
```

Expected result: `/overlay` has adequate free space and the backup archive is
non-empty. Pull it to the admin laptop before package or network changes.

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
scp root@192.168.1.1:/tmp/openwrt-clean-baseline.tar.gz .\snapshots\
Get-Item .\snapshots\openwrt-clean-baseline.tar.gz |
  Format-List FullName,Length,LastWriteTime
```

Expected result: the local file has a non-zero length and current timestamp.

Recovery: if backup generation or copy fails, check overlay capacity and SSH
before proceeding. Never rely only on a `/tmp` backup because `/tmp` is lost on
reboot.

## 4. Install and verify router dependencies

Run on: OpenWrt router over SSH while temporary WAN access is available.

```sh
opkg update
opkg install wireguard-tools qrencode tcpdump iperf3 ethtool
wg --version
tcpdump --version | head -n 1
iperf3 --version | head -n 1
ethtool --version
```

Expected result: `opkg` reports packages installed or already present; all four
version commands exit `0`. Package names and verification commands are recorded
in the [package matrix](../reference/package-dependency-matrix.md).

Recovery: if package indexes or downloads fail, verify date/time, WAN, DNS, and
free overlay space. Do not leave temporary unrestricted WAN rules enabled after
installation.

## 5. Create and verify the deployment key

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
ssh-keygen -t ed25519 -f .\keys\router_deploy -N '""' -C 'router-deploy@laptop'
Get-Content .\keys\router_deploy.pub
```

Expected result: `ssh-keygen` reports the private/public file paths and a
fingerprint; the second command prints exactly one `ssh-ed25519` public-key
line. It must not print a private-key header.

Add only the public key in LuCI under **System > Administration > SSH-Keys**.
Keep the private key local and ignored by Git.

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
ssh -i .\keys\router_deploy root@192.168.1.1 "echo SSH_KEY_OK"
```

Expected result: exactly `SSH_KEY_OK`, without a password prompt.

Recovery: remove an incorrect public-key line in LuCI, add the generated `.pub`
file again, and retry. Never copy the private key to the router or repository.

## 6. Inspect and lint canonical source

Review `configs/openwrt/` against the IP plan, access matrix, and known MAC
addresses. The compiler output is disposable; canonical `.conf` files are not.

Run on: Admin laptop from `main/` in PowerShell.

```powershell
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile first-flight
```

Expected success shape:

```text
Router Config Lint
============================================================
PASSED: all checks clean.
[INFO] First-flight adjustments applied:
  - removed_placeholder_hosts: <count>
  - disabled_wifi_ifaces: <count>
[OK] Artifacts written:
  - ...\generated\summary.json
```

`first-flight` removes placeholder hosts and WireGuard peers and disables Wi-Fi
interfaces with placeholder keys. It is a wired bring-up profile, not a shortcut
to full deployment.

Recovery: fix the first canonical-source or architecture error, rerun lint, and
then compile. The current missing Docker-host Tailscale egress invariant must be
resolved in policy/source before any deployment resumes.

## 7. Deploy first flight with watchdog protection

Keep the laptop on `lan5` throughout the apply. Do not move it to `lan2` until
the deploy command finishes and recovery snapshots are confirmed.

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1 -Profile first-flight
```

Expected success shape:

```text
[OK] Router identity verified.
[OK] Router snapshots created.
[OK] Generated configs copied.
[OK] Services restarted and health checks passed.
[OK] Watchdog cancelled.
```

Recovery: if the command fails, allow its automatic restore/watchdog to finish.
Do not immediately power-cycle. If neither management nor recovery responds,
perform the physical `lan5` drill in Step 10.

## 8. Validate first-flight source and live state

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test.ps1 -Profile first-flight
powershell -NoProfile -ExecutionPolicy Bypass -File .\test-connectivity.ps1 -Profile first-flight
```

Expected result: `test.ps1` ends with `FAIL=0`; the known fully matching
first-flight connectivity shape is `Summary: PASS=83 WARN=0 FAIL=0`. A changed
PASS count is acceptable only when the test inventory intentionally changed and
every test is accounted for.

Run on: OpenWrt router over SSH at `192.168.10.1` after Management access works.

```sh
ip -brief address
bridge vlan show
ubus call service list '{"name":"dnsmasq"}'
ubus call service list '{"name":"sysntpd"}'
uci -q get system.ntp.enable_server
nft list ruleset | grep -E 'management|storage|nvr|iot|guest' | head -n 30
```

Expected result: VLAN interfaces carry their planned gateway addresses,
`dnsmasq` and `sysntpd` report running instances, NTP server mode is `1`, and
the ruleset contains the expected scoped zones/rules.

Recovery: diagnose a single failing layer—UCI intent, service state, kernel
interface, nftables rule, then client path. Do not broaden zone forwarding to
make a failing test pass.

## 9. Populate and compile the full profile

Replace every approved Wi-Fi/WireGuard/MAC placeholder through the secret and
hardware workflow. Verify no tracked diff contains a private key or Wi-Fi
password before compilation.

Run on: Admin laptop from `main/` in PowerShell.

```powershell
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile full
git diff -- configs/openwrt
```

Expected result: lint and compile exit `0`, generated artifacts are written,
and `git diff` contains only approved non-secret identifiers and policy. A
compile invoked with `--allow-placeholders` is preview-only and cannot satisfy
this gate.

Recovery: fill missing real values through their approved untracked input path,
or leave the dependent host/SSID/peer parked. Never invent MAC addresses or
commit secrets merely to clear compilation.

## 10. Rehearse physical `lan5` recovery before full deployment

Move the laptop to `lan5`, use DHCP (or temporary `192.168.1.10/24`), and prove
the recovery path while the router is healthy.

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
Test-Connection 192.168.1.1 -Count 2
ssh -i .\keys\router_deploy root@192.168.1.1 "echo RECOVERY_OK; ls -1 /tmp/router-deploy-snapshots | tail -n 3"
```

Expected result: the router responds, prints `RECOVERY_OK`, and lists at least
one snapshot directory.

If a real restore is required, select a known-good snapshot by explicit name.

Run on: OpenWrt router through physical `lan5` recovery SSH.

```sh
SNAP='/tmp/router-deploy-snapshots/<ROUTER_SNAPSHOT_TIMESTAMP>'
test -s "$SNAP/network" && test -s "$SNAP/dhcp" && test -s "$SNAP/firewall"
cp "$SNAP/network" /etc/config/network
cp "$SNAP/dhcp" /etc/config/dhcp
cp "$SNAP/wireless" /etc/config/wireless
cp "$SNAP/firewall" /etc/config/firewall
/etc/init.d/network restart
/etc/init.d/dnsmasq restart
/etc/init.d/firewall restart
```

Expected result: the `test` guard exits `0` before any copy; services restart;
recovery `192.168.1.1` and Management `192.168.10.1` return. If the guard fails,
do not copy and use the laptop-side pulled snapshot or clean-firmware recovery.

## 11. Deploy and validate the full profile

Run on: Admin laptop from `main/tools/router-deploy/` in PowerShell.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1 -Profile full
powershell -NoProfile -ExecutionPolicy Bypass -File .\test.ps1 -Profile full
powershell -NoProfile -ExecutionPolicy Bypass -File .\test-connectivity.ps1 -Profile full
```

Expected result: deployment prints all five `[OK]` milestones, both tests end
with `FAIL=0`, intended SSIDs are enabled, and only configured WireGuard peers
exist. Keep WireGuard dormant unless its governance procedure authorizes use.

Recovery: let automatic rollback finish, then use `lan5` and the snapshot drill.
After recovery, rerun lint and first-flight validation before attempting another
full deployment.

## 12. Prove user paths and policy denials

From one client in each deployed VLAN, record DHCP address, gateway, DNS,
router-local time reachability, public internet policy, and the allowed/denied
paths in the access matrix. Guest must reach the internet through router DNS but
not internal service/admin ports. NVR, Storage, Printers, and IoT must not gain
router administration merely because DHCP/DNS/NTP input is allowed.

Use [Phase 12](12-validation-troubleshooting.md) for the exact positive and
negative tests. One successful ping does not prove segmentation.

## Failure recovery matrix

| Symptom | Nearest checks | Bounded recovery | Do not do |
|---|---|---|---|
| Firmware will not boot | image type, target, digest, recovery UI | reinstall exact verified image through supported recovery | flash another model's image |
| SSH key rejected | laptop address, root login, `.pub` entry | reinstall only public key through LuCI | copy private key to router |
| Lint/compile fails | first named source/invariant error | repair canonical source and rerun in order | edit generated files |
| Lost access after apply | wait for watchdog, test `lan5` | restore explicit known-good snapshot | power-cycle during automatic rollback |
| DNS fails but routing works | `dnsmasq`, local record, AdGuard/upstream | restore last known-good DNS source; retain fallback | hand clients an undocumented resolver |
| Time/TLS fails | `sysntpd`, upstream sync, client source | restore router NTP and validate clock | disable TLS verification |
| Required path denied | source, target, port, counter | add one reviewed host/port rule | allow broad inter-VLAN forwarding |
| Denied path succeeds | matching nft/UCI rule | remove/narrow rule and repeat adjacent allowed test | accept it as temporary |

## Completion checklist

- [x] Physical first-flight and `lan5` access were previously smoke-tested.
- [ ] Current router source lint passes.
- [ ] Current first-flight compile passes without invariant failures.
- [ ] Current full compile passes without placeholders or overrides.
- [ ] Fresh-image digest and clean baseline backup are recorded for this rebuild.
- [ ] Deployment key and pulled-back snapshot are proved.
- [ ] First-flight deploy and both live test suites report zero failures.
- [ ] Physical `lan5` recovery drill is recorded before full deploy.
- [ ] Full deploy and both live test suites report zero failures.
- [ ] VLAN client positive and denial tests match the access matrix.
- [ ] Router-local NTP, AdGuard-first DNS, public fallback, and dormant WireGuard state are proved.
