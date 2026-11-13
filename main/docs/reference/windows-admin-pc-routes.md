---
title: Windows admin PC project routes
created: 2026-10-20
modified: 2026-10-20
type: reference
status: active
---

# Windows admin PC project routes

Diagram: [[../diagrams/network/windows-admin-pc-routes.mermaid|Admin PC routes and Orca recovery path]].

Published in the Mermaid Viewer on October20 via its standard verified release.
All17 canonical diagrams rendered in the browser gate; post-deploy desktop LAN
and mobile-width Homepage HTTPS checks rendered the new printer route.
Viewer: `https://homepage.home.local:8195/?diagram=windows-admin-pc-routes`.
Rollback checkpoint: `/opt/backups/mermaid-viewer-release-20261020T184031Z`.

The saved printer route survives reboot and removes the dependency on
HomePrinters Wi-Fi while management Ethernet can reach `192.168.10.1`.
If Ethernet is disconnected, the PC moves to another subnet, or its adapter
configuration changes, verify the selected route again. This is local home
access, not a remote-access or automatic network-failover guarantee.

Verified on the Admin desktop, canonical K: checkout, on 2026-10-20.
Ethernet is on management VLAN 10 at `192.168.10.132`, gateway
`192.168.10.1`. Mullvad remains connected with LAN sharing enabled.

## Persistent project routes

All five entries use gateway `192.168.10.1` and route metric `1`.
The four older destinations were recorded in current-live-state on September 27;
that is evidence they existed then, not necessarily their original creation date.

| Destination | Purpose | Persistence/interface evidence |
| --- | --- | --- |
| `192.168.20.0/24` | Automation: HA, VM103 apps, Bambuddy virtual printer `.103`, CT114 | Saved Ethernet route; active on Ethernet |
| `192.168.30.0/24` | NVR/Frigate and cameras | Saved legacy route displays `iftype0_0`; active copies on Ethernet and Wi-Fi at inventory time |
| `192.168.40.50/32` | OMV NAS only | Saved Ethernet route; active on Ethernet |
| `192.168.60.0/24` | Monitoring VM/services | Saved legacy route displays `iftype0_0`; active copies on Ethernet and Wi-Fi at inventory time |
| `192.168.35.200/32` | Physical Bambu P1S only | Added by owner October 20; saved entry displays `iftype0_0`, selected active route is Ethernet |

`iftype0_0` is the display returned for these persistent records; use the active
table and `Find-NetRoute` to verify the actual selected interface. Wi-Fi was
disconnected by the final check; active-table copies alone do not prove link use.

The connected management `192.168.10.0/24` routes are automatic interface routes.
`192.168.56.0/24` belongs to Ethernet 2 and is outside this project. VPN/default,
loopback, broadcast and multicast routes are not manually added project routes.
No full printer-subnet or full storage-subnet exception is installed.

## Inspect, restore and remove

### Epson XP-8700 route prepared — owner application pending

October20 Windows inventory identifies `EPSON XP-8700 Series` on Standard
TCP/IP port `IP_192.168.35.124`, RAW TCP9100, SNMP disabled. Router DHCP/ARP
identifies `EPSOND6023C`, MAC `dc:cd:2f:d6:02:3c`, at that address. No matching
static reservation was found in the inspected live DHCP configuration; review
address stability before treating this DHCP address as permanent.

The desktop currently selects Mullvad for this destination. Adding the route
was rejected because the agent shell is not elevated. Apply from Administrator
PowerShell, then verify TCP9100 and print from Windows:

```powershell
route -p add 192.168.35.124 mask 255.255.255.255 192.168.10.1 metric 1
Test-NetConnection 192.168.35.124 -Port 9100
```

Rollback: `route delete 192.168.35.124 mask 255.255.255.255 192.168.10.1`.
This pending sixth entry is not included in the five verified routes above.
Routing and real print acceptance remain pending; no test page was submitted.

Read-only inventory:

```powershell
Get-NetRoute -PolicyStore PersistentStore -AddressFamily IPv4
Get-NetRoute -AddressFamily IPv4
Find-NetRoute -RemoteIPAddress 192.168.35.200
Test-NetConnection 192.168.35.200 -Port 8883
```

To restore a missing entry, use Administrator PowerShell. Confirm the current
Ethernet interface index first; do not reuse an old numeric index such as 13.
Run only the missing route commands, with Ethernet connected to VLAN 10:

```powershell
$projectEthernetIndex = (Get-NetAdapter -Name 'Ethernet').ifIndex
route -p add 192.168.20.0 mask 255.255.255.0 192.168.10.1 metric 1 if $projectEthernetIndex
route -p add 192.168.30.0 mask 255.255.255.0 192.168.10.1 metric 1 if $projectEthernetIndex
route -p add 192.168.40.50 mask 255.255.255.255 192.168.10.1 metric 1 if $projectEthernetIndex
route -p add 192.168.60.0 mask 255.255.255.0 192.168.10.1 metric 1 if $projectEthernetIndex
route -p add 192.168.35.200 mask 255.255.255.255 192.168.10.1 metric 1 if $projectEthernetIndex
```

The owner's October 20 command omitted `if`; Windows selected Ethernet.
Rollback of that printer exception only, from Administrator PowerShell:

```powershell
route delete 192.168.35.200 mask 255.255.255.255 192.168.10.1
```

Verify active and persistent tables after changes. Routes select a network path;
router ACLs and service authentication still apply. Exact hosts-file aliases are
a separate DNS mechanism; see [[../decisions/04-dns-resolver-and-adblocking]].
These routes apply to this desktop, not other devices or remote Tailscale access.

## October 20 Orca connection error investigation

### October21 follow-up: Orca sends bypassing Bambuddy

Owner identified Orca destination as `Da Printore`. Saved Orca connection fields
identify this as the physical P1S at `.35.200` with physical serial, not the
Bambuddy VP. No `.20.103` connection was found in inspected Orca user/printer
JSON/config files. Orca recorded two "send ok" messages, but Bambuddy had no new
upload or queue entry. The virtual printer is enabled as `Da Printor VP`, queue
mode with auto-dispatch, bind IP `.20.103`; desktop TCP8883/990/3000/3002 opened.
Use the VP's own serial/access code from Bambuddy when adding its manual-IP
connection to Orca. Merely renaming the physical printer or changing only its
IP would leave mismatched connection credentials. Rebinding and a successful
owner print remain pending; no diagnostic print was submitted.

Evidence from Windows WLAN-AutoConfig Operational events (8001/8003, local
Europe/London time), Mullvad daemon logs, route tables and PowerShell history:

- October 19, 17:05:23: Windows connected to `HomePrinters`.
- October 20, 08:34:59: Windows automatically connected to `HomePrinters` after
  boot. Mullvad recorded underlying IPv4 `192.168.35.116`, then `.10.132`.
- October 20, 08:37:09: Windows disconnected HomePrinters with reason
  "a policy disabling auto connect on this interface". The event does not
  identify which actor changed that policy.
- HomeAdmin was connected at 16:41:39 and disconnected at 16:45:35. Neither
  HomeAdmin nor management Ethernet supplies a directly connected VLAN35 route.
- Before repair, `Find-NetRoute` chose Mullvad/default gateway `10.64.0.1`
  for `.35.200`; desktop TCP 8883/990/6000 timed out. The persistent table
  contained the four older project routes, with no printer destination.
- VM103 successfully opened printer TCP 8883/990. Its ICMP probes received
  router-origin Destination Port Unreachable; failed ping did not mean the
  printer's services were unreachable.
- Owner added the persistent `.35.200/32` route. The selected route became
  Ethernet via `.10.1`; desktop TCP 8883, 990 and 6000 all opened with Mullvad
  still connected. Orca application reconnection/upload remains owner acceptance.

Strongest explanation: the direct HomePrinters Wi-Fi connection previously
provided local printer reachability without a saved route; losing that link
exposed the missing management-to-printer route. Logs do not establish the exact
last successful Orca connection. No earlier printer-route command was found in
the inspected PowerShell history, and no evidence proves deletion of a saved
route. A reboot clearing an unrecorded temporary route cannot be excluded.
Mullvad's generic missing-route warnings do not identify a printer destination
and must not be treated as proof it deleted this route. Plain Orca logs do not
establish the network failure's onset; its network log is encrypted.

Local evidence inspected, not copied into Git: `C:\ProgramData\Mullvad VPN\daemon.log`,
`daemon.old.log`, Windows WLAN event log, and Admin's PSReadLine history.
No VPN settings, router policies or printer settings changed during this repair.
