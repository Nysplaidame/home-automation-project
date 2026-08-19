---
title: Phase 00 - Operator Basics
description: Safety, inventory, assumptions, and beginner operating rules before installation
tags: [install, phase, basics]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 00 - Operator Basics

## Purpose

Prepare the operator, admin laptop, hardware inventory, address plan, and secret
records before changing a live device. This phase prevents otherwise-correct
commands from being run on the wrong host or with missing recovery information.

## Runs on

Admin laptop on a trusted local network. Commands in this phase use PowerShell.

## Stop conditions

Do not continue to Phase 01 if any of these are true:

- the repository root cannot be identified;
- unexpected local changes have not been reviewed;
- Git or SSH is unavailable;
- a device that will be changed has no recorded model, management path, or
  rollback method;
- a required secret has nowhere outside Git to be stored;
- the planned management IP conflicts with another device.

## Prerequisites

- Repository available locally.
- Admin laptop has Git, SSH, a browser, and a text editor.
- Password manager available for secret values.
- Hardware list reviewed in `README.md` and `bill-of-materials/`.
- The operator has read
  [command-location-legend.md](../reference/command-location-legend.md),
  [secrets-placeholder-ledger.md](../reference/secrets-placeholder-ledger.md),
  and [rebuild-state-matrix.md](../reference/rebuild-state-matrix.md).

## Inputs

- `<ADMIN_SSH_PUBLIC_KEY>`
- Password-manager vault location
- Hardware models, serial numbers, MAC addresses, and physical port labels
- Planned VLAN and IP assignments

Real secret values never belong in this repository. Angle-bracket values are
documentation placeholders; resolve them from the password manager only when a
later step explicitly requires the real value.

## 1. Confirm the repository and tools

Run on: Admin laptop.

```powershell
$repoRoot = git rev-parse --show-toplevel
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'main/docs/install/START-HERE.md'))) {
    throw 'This is not the home-automation-project repository root.'
}
Set-Location -LiteralPath $repoRoot

git status --short
git --version
ssh -V
```

Expected output resembles:

```text
git version 2.x.x.windows.x
OpenSSH_for_Windows_9.xp1, LibreSSL 3.x.x
```

`git status --short` may print nothing in a clean worktree. If it lists files,
identify who owns those changes before editing or staging anything. Obsidian
workspace/plugin changes are user-owned unless explicitly stated otherwise.

Run on: Admin laptop.

```powershell
$uppercaseActivePaths = @(
    git ls-files | Select-String -CaseSensitive -Pattern '^[A-Z]ain/'
)
$activePaths = @(
    git ls-files | Select-String -CaseSensitive -Pattern '^main/'
)

[pscustomobject]@{
    UppercaseActivePaths = $uppercaseActivePaths.Count
    CanonicalMainPaths   = $activePaths.Count
}
```

Expected output:

```text
UppercaseActivePaths CanonicalMainPaths
-------------------- ------------------
                   0       greater than 0
```

The `-CaseSensitive` switches are required. Without them, PowerShell treats
`Main/` and `main/` as the same pattern and produces a false failure.

## 2. Build the hardware inventory

Record one row per physical host, network appliance, camera, sensor controller,
and operator device. Do not wait for every future device to arrive: use
`not purchased` or `unknown` rather than inventing a value.

Example inventory (illustrative values only):

| Role | Make/model | Serial/asset record | Physical connection | Management path | MAC state | Rollback or recovery path |
|---|---|---|---|---|---|---|
| Router | GL.iNet GL-MT6000 | Password manager or asset record | WAN plus labelled LAN ports | Recovery IP/LuCI and physical lan5 | recorded | physical lan5 recovery; saved config backup |
| Proxmox host | MINISFORUM M1 Pro-125H | asset record | managed-switch trunk | `192.168.10.10` web/SSH | recorded | console access plus known-good backup |
| NAS | OMV storage host | asset record | VLAN 40 access port | `192.168.40.50` web/SSH | recorded | local console; preserve data disks |
| Future camera | exact model pending | not purchased | planned PoE VLAN 30 port | planned DHCP reservation | unknown | factory reset and isolated bench port |

For each row, also photograph or record port labels and note whether local
keyboard/display access exists. A management IP by itself is not a recovery
path if the network configuration is the component being changed.

## 3. Capture MAC addresses without guessing

First record the admin laptop interface used for the work. Filter out virtual
adapters and disconnected interfaces.

Run on: Admin laptop.

```powershell
Get-NetAdapter -Physical |
    Where-Object Status -eq 'Up' |
    Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed |
    Format-Table -AutoSize
```

Expected output resembles:

```text
Name     InterfaceDescription              MacAddress        LinkSpeed
----     --------------------              ----------        ---------
Ethernet Intel(R) Ethernet Controller ...  AA-BB-CC-DD-EE-FF 1 Gbps
```

The shown address is an example. Copy the value reported on the actual device,
normalize it to `AA:BB:CC:DD:EE:FF` when a router reservation requires colons,
and confirm it against the device label or management UI. Wi-Fi and Ethernet
interfaces on the same device have different MAC addresses.

For headless Linux hosts, collect the address only after confirming the prompt
belongs to the intended host.

Run on: Proxmox host shell, docker-host over SSH, Frigate CT over SSH, llm-host over SSH, or OMV shell, as applicable.

```bash
ip -brief link
```

Expected output resembles:

```text
lo               UNKNOWN        00:00:00:00:00:00
enp1s0           UP             aa:bb:cc:dd:ee:ff
```

Ignore `lo`, bridges, container interfaces, and other virtual interfaces unless
the later phase explicitly requests one. Record the physical interface that is
connected to the planned switch port.

## 4. Confirm the IP plan

Use the canonical project plan below. A device may use DHCP during isolated
bench setup, but its intended VLAN and final reservation must be recorded before
it becomes live.

| VLAN | Purpose | Subnet | Example infrastructure assignment |
|---:|---|---|---|
| 1 | user LAN | `192.168.1.0/24` | client DHCP |
| 10 | management | `192.168.10.0/24` | router `.1`, Proxmox `.10`, switch `.12` |
| 20 | automation | `192.168.20.0/24` | HA `.101`, docker-host `.102`, llm-host `.104` |
| 30 | NVR/cameras | `192.168.30.0/24` | Frigate `.20`, cameras `.21` onward |
| 35 | printers | `192.168.35.0/24` | printer reservations |
| 40 | storage | `192.168.40.0/24` | OMV `.50` |
| 50 | IoT sensors | `192.168.50.0/24` | ESPHome/MQTT clients |
| 60 | monitoring | `192.168.60.0/24` | monitoring VM `.10` |
| 70 | DMZ | `192.168.70.0/24` | explicitly approved services only |
| 99 | guest | `192.168.99.0/24` | guest DHCP |

Before assigning an address, check the canonical DHCP source and probe the live
network. A failed ping does not prove an address is free, so also inspect the
router lease/neighbor tables in Phase 01.

Run on: Admin laptop.

```powershell
Select-String -Path 'main/configs/openwrt/dhcp-config.conf' -Pattern '192\.168\.'
Test-Connection -ComputerName 192.168.10.1 -Count 2
```

Expected result:

- the source file displays the planned reservations and local records;
- the router responds if the management network is already live;
- if this is a blank rebuild, the ping may fail and Phase 01 establishes the
  initial recovery/management path instead.

## 5. Prepare secret placeholders

Create password-manager records before creating the real values. Record the
placeholder name in the record notes so a later operator can map documentation
to the secret without exposing it.

Example:

| Documentation value | Password-manager record | Repository value |
|---|---|---|
| `<ADMIN_SSH_PUBLIC_KEY>` | `Home Automation / Admin SSH key` | public key only where requested |
| `<ROUTER_ROOT_PASSWORD>` | `Home Automation / OpenWrt root` | placeholder only |
| `<HA_ADMIN_PASSWORD>` | `Home Automation / Home Assistant owner` | placeholder only |

Confirm that the public half of the admin key exists. Never print or copy a
private-key file into project notes.

Run on: Admin laptop.

```powershell
$publicKeyPath = Join-Path $env:USERPROFILE '.ssh/id_ed25519.pub'
if (-not (Test-Path -LiteralPath $publicKeyPath)) {
    throw 'Admin SSH public key is missing. Create or recover the approved key before continuing.'
}
$publicKey = (Get-Content -LiteralPath $publicKeyPath -Raw).Trim()
if ($publicKey -notmatch '^ssh-(ed25519|rsa)\s+') {
    throw 'The selected file does not look like an OpenSSH public key.'
}
'Validated an OpenSSH public key; private key was not read.'
```

Expected output:

```text
Validated an OpenSSH public key; private key was not read.
```

If the approved key uses another filename, change only `$publicKeyPath`. Do not
generate a replacement merely to make this check pass: replacement affects
every system that trusts the old key and requires a deliberate rotation plan.

## Expected result

- The operator can identify the exact target and shell/UI for every later step.
- Git reports zero tracked uppercase `Main/` paths and one or more canonical
  `main/` paths.
- Git and SSH version commands succeed.
- Every present device has an inventory row, management path, and recovery path.
- Known physical MAC addresses are recorded; unavailable addresses are marked
  `unknown` rather than fabricated.
- Planned addresses agree with the canonical VLAN table and DHCP source.
- Every currently required secret placeholder has a password-manager record;
  no real secret was written to Git.

## Validation and recovery rehearsal

This phase uses read-only checks. Rehearse both stop paths before continuing:

1. Run the repository guard from a directory outside this repository. It must
   stop with either Git's `not a git repository` error or the explicit
   `not the home-automation-project repository root` error.
2. Set `$publicKeyPath` temporarily to a nonexistent filename and run only the
   public-key validation block. It must stop with `Admin SSH public key is
   missing`. Restore the correct path; do not create or delete keys for the
   rehearsal.
3. Confirm that `Get-NetAdapter -Physical` excludes Hyper-V, VirtualBox, and
   other virtual adapters. If no physical interface is `Up`, record the adapter
   from the device label or its trusted management UI after connectivity is
   restored.

These recovery paths are safe because they do not change Git, keys, adapters,
or live devices. The repository/tool/MAC checks and their expected output shape
were re-run on the admin laptop on 2026-08-09.

## Failure recovery

| Failure | Safe response | Proof before continuing |
|---|---|---|
| `git rev-parse` fails | Open the correct checkout and rerun the repository guard. | `$repoRoot` contains `main/docs/install/START-HERE.md`. |
| `git status` shows unfamiliar work | Stop; identify and preserve the owner changes. Do not reset or stage them. | Every listed change is understood and scoped. |
| Git or SSH is missing | Install Git or enable Windows OpenSSH Client, then reopen PowerShell. | Both version commands succeed. |
| Uppercase active paths are reported | Inspect exact matches and repair repository casing deliberately. | `UppercaseActivePaths` is `0`. |
| MAC address is ambiguous | Match physical port, device label, switch table, and management UI; do not create a reservation yet. | Two independent sources agree. |
| Planned IP responds unexpectedly | Treat it as occupied; inspect DHCP leases and neighbor tables in Phase 01. | Existing owner is identified or a different address is approved. |
| Placeholder has no password-manager record | Create the record before generating or entering the secret. | Placeholder name and system owner are recorded outside Git. |
| Approved SSH public key is missing | Recover the approved key or plan a controlled replacement. | Public-key validation succeeds and dependent hosts are accounted for. |

## Completion checklist

- [ ] Admin laptop can run Git and SSH.
- [ ] Repository guard and case-sensitive path checks pass.
- [ ] Password manager contains records for the placeholders needed by the next phase.
- [ ] Hardware inventory includes management and recovery paths.
- [ ] Known MAC addresses and planned VLAN/IP assignments are recorded.
- [ ] Both read-only stop-path rehearsals behave as documented.
- [ ] You can explain the command-location and rebuild-state rules.

Continue to [Phase 01 - Router/OpenWrt](01-router-openwrt.md) only after every
applicable checkbox above is satisfied.
