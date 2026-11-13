# Extended troubleshooting routes

Generated from `main/apps/troubleshooting-dashboard/additional-routes.js`.
Regenerate with `node main/apps/troubleshooting-dashboard/scripts/export-routes.mjs`.

These read-only investigations supplement the [five original walkthroughs](diagnostic-walkthroughs.md).
Keep this file in the local vault: a docker-host outage also takes the dashboard offline.
This is a failure-scenario catalog, not a claim that these failures are happening now.

Record time with timezone, source device/network, exact error and last passing layer.
Collector imports cover only some signals. The other signals require the manual checks below;
keep findings in operator notes. A collected step does not automatically update a check status.
Keep credentials, private URLs and household data out of shared logs or incident reports.

## Coverage

| Area | Investigation |
|---|---|
| Network and access | [Homepage Preview works but Direct is blank](#portal-navigation) |
| Network and access | [An app redirects to the wrong IP or port](#proxy-redirect) |
| Network and access | [HTTPS works intermittently after service restarts](#listener-collision) |
| Network and access | [Local or remote DNS fails after a reboot](#dns-after-reboot) |
| Hosts and storage | [NAS drive disappears or says permission denied](#smb-access) |
| Hosts and storage | [NAS copies or archive extraction stop and start](#nas-speed) |
| Home and devices | [Bambuddy queue is stuck while the printer is idle](#printer-queue) |
| Applications and data | [An app shows an old version or cannot save](#frontend-cache) |
| Home and devices | [ESPHome controls the wrong device or shows stale entities](#esphome-identity) |
| Hosts and storage | [Docker app runs but builds or downloads fail](#docker-build) |
| Network and access | [Internet or Wi-Fi stops working](#internet) |
| Network and access | [Local names or web searches fail](#dns) |
| Network and access | [Certificate warning or HTTPS failure](#tls) |
| Network and access | [Works at home, fails remotely](#remote) |
| Hosts and storage | [Guests disappear after a reboot](#guests) |
| Hosts and storage | [Several apps are slow or down](#docker) |
| Hosts and storage | [Files disappear or storage fills](#storage) |
| Hosts and storage | [Application backup job fails](#app-backup) |
| Monitoring and maintenance | [Graphs or health monitors go blank](#monitoring) |
| Home and devices | [Local AI fails or becomes very slow](#local-ai) |
| Home and devices | [Voice hears nothing or gives no reply](#voice) |
| Home and devices | [HA opens but an automation does nothing](#automations) |
| Monitoring and maintenance | [Expected notifications never arrive](#notifications) |
| Monitoring and maintenance | [Updates fail or package lists are old](#updates) |
| Applications and data | [Immich uploads or thumbnails fail](#photos) |
| Applications and data | [Media library is empty or playback fails](#media) |
| Applications and data | [Downloads stall or the client disappears](#downloads) |
| Applications and data | [Notes stop syncing or conflict](#sync) |
| Applications and data | [An app opens but its data fails](#household) |
| Applications and data | [Password vault login or sync fails](#vault) |
| Home and devices | [VentSys device or dashboard is offline](#ventsys) |
| Home and devices | [Phone stream or recordings stop](#phone-relay) |

<a id="portal-navigation"></a>
## Homepage Preview works but Direct is blank

Compare the actual navigation URL with the phone’s approved HTTPS proxy path.

Required evidence: Homepage listener (`homepage`); Standalone link destination (`portal_link`); Mobile-data acceptance (`mobile_acceptance`).

### 1. Compare Preview and standalone destinations

Run on: **Affected phone / browser**.

```text
No command: record the Homepage URL, selected card and the address opened by Direct.
```

Expected: Both actions use the same HTTPS proxy; paths and queries are preserved.

If not: A raw 192.168 address or backend HTTP port bypasses the scoped phone grant. September 25 introduced this regression; September 30 repaired it.

### 2. Check the navigation release contract

Run on: **Canonical Windows checkout / repository root**.

```text
node main/configs/docker-host/stacks/homepage/tests/access-contract.cjs
```

Expected: Standalone/preview parity and listener ownership checks pass.

If not: This is an offline source check, not phone connectivity proof. Do not add VLAN routes to hide an incorrect link.

### 3. Compare the real phone paths

Run on: **Phone on mobile data / Tailscale**.

```text
No command: refresh Homepage and open the same app in Preview and Direct.
```

Expected: Both show the app or its expected login page.

If not: If only one app fails, use the redirect route; if every request fails, use the remote-access route. An already-open cached page is not a fresh acceptance test.

References: [Operating guide](../install/services/homepage.md) · [Service inventory](../reference/service-matrix.md)

<a id="proxy-redirect"></a>
## An app redirects to the wrong IP or port

Find redirects that escape a working HTTPS proxy to an unreachable backend.

Required evidence: Homepage listener (`homepage`); Redirect hostname and port (`redirect_origin`); Complete redirect chain (`redirect_chain`).

### 1. Read the Grocy first response

Run on: **VM 103 / docker-host**.

```text
curl --cacert /opt/stacks/homepage/tls/ca.crt --resolve homepage.home.local:8198:100.94.122.18 -I https://homepage.home.local:8198/
```

Expected: Location remains on homepage.home.local:8198, or is relative.

If not: Grocy previously redirected to HTTPS 192.168.20.102:9283 because the proxy sent its backend Host. That listener speaks HTTP and is outside the mobile navigation path.

### 2. Follow the complete redirect chain

Run on: **VM 103 / docker-host**.

```text
curl --max-time 15 -L --cacert /opt/stacks/homepage/tls/ca.crt --resolve homepage.home.local:8198:100.94.122.18 -sS -o /dev/null -w "%{http_code} %{url_effective}\n" https://homepage.home.local:8198/
```

Expected: The final response is the app/login page on the same HTTPS proxy origin.

If not: A 302 response alone is not acceptance. Check every hostname and port; preserve certificate verification.

### 3. Inspect the service-specific Host policy

Run on: **Canonical checkout / Homepage proxy config**.

```text
No command: inspect the Grocy 8198 server block and proxy_set_header Host.
```

Expected: Grocy preserves the external Host and port using $http_host.

If not: Do not change every upstream Host globally: other services may require their existing backend Host policy. Do not disable authentication to remove a redirect.

References: [Operating guide](../install/services/grocy.md) · [Service inventory](../reference/service-matrix.md)

<a id="listener-collision"></a>
## HTTPS works intermittently after service restarts

Separate competing proxy/Tailscale Serve listeners from DNS or certificate failure.

Required evidence: Docker host reachable (`docker_host`); Port owner by address (`listener_owner`); Serve and browser endpoints (`serve_proxy`).

### 1. Read who owns the relevant listeners

Run on: **VM 103 / docker-host**.

```text
ss -lntp | grep -E ":(443|8181|8207|8443|8444) "
```

Expected: Tailnet 8181 belongs to tailscaled; Nginx owns browser 8207 and may retain LAN-only 8181.

If not: A wildcard Nginx 8181 competes with native Bambuddy Serve. Startup order can determine which path breaks.

### 2. Inspect the persistent Serve mapping

Run on: **VM 103 / docker-host**.

```text
tailscale serve status
```

Expected: Native Bambuddy remains on the ts.net hostname at 8181; browser access uses 8207.

If not: Serve config existing does not prove a listener bound successfully. Do not reset all Serve mappings; LiveSync and ntfy also depend on them.

### 3. Read bind and handshake failures

Run on: **VM 103 / docker-host**.

```text
journalctl -u tailscaled --since "30 minutes ago" --no-pager | grep -E "address already in use|no webserver configured|failed to listen"
```

Expected: No repeated bind conflicts or name/port errors for the failing endpoint.

If not: No matches only means these errors were not recorded. Test both browser and native endpoints with their own hostnames and normal certificate verification.

References: [Operating guide](../procedures/tailscale_remote_access_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="dns-after-reboot"></a>
## Local or remote DNS fails after a reboot

Check the AdGuard startup gate and address-specific bindings before changing resolvers.

Required evidence: Docker host reachable (`docker_host`); AdGuard startup gate (`dns_startup`); LAN and tailnet DNS bindings (`dns_binding`).

### 1. Inspect the Compose startup gate

Run on: **VM 103 / docker-host**.

```text
systemctl status adguard-home-compose.service --no-pager; systemctl is-enabled adguard-home-compose.service
```

Expected: The enabled gate completed after the Tailscale address became available.

If not: July 29 recorded a reboot race. A running Docker daemon does not prove its address-bound DNS service started.

### 2. Check addresses and DNS listeners

Run on: **VM 103 / docker-host**.

```text
ip -4 address show dev tailscale0; ss -lntup | grep ":53 "
```

Expected: 100.94.122.18 is present and DNS is bound on both the intended LAN and tailnet addresses.

If not: Missing tailnet binding can break remote names while LAN DNS works. Capture the missing layer before recreating or restarting anything.

### 3. Read the gate’s first failure

Run on: **VM 103 / docker-host**.

```text
journalctl -u adguard-home-compose.service -b --no-pager -n 60
```

Expected: The address wait and Compose startup completed without a bind failure.

If not: If direct HTTPS by the approved name-resolving test works, isolate DNS. Preserve split DNS and the router’s local-name authority; do not add a public rewrite for private services.

References: [Operating guide](../procedures/tailscale_remote_access_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="smb-access"></a>
## NAS drive disappears or says permission denied

Separate persistent Windows mappings, the authenticated SMB identity, share rights and filesystem ACLs.

Required evidence: NAS listener (`nas`); Actual SMB account and mapping (`smb_identity`); Target folder permissions (`smb_acl`).

### 1. Read the actual Windows connection

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Get-SmbConnection | Select-Object ServerName,ShareName,UserName,Dialect; Get-SmbMapping | Select-Object LocalPath,RemotePath,Status
```

Expected: Y: and Z: point to the intended shares using the intended account.

If not: A saved credential does not prove the existing session uses it. Do not display credential secrets or disconnect a share while writes/transfers are active.

### 2. Read existing mapping persistence

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
net use
```

Expected: The intended mappings and reconnect state match the workstation setup.

If not: After reboot, distinguish delayed networking from a failed credential. Do not duplicate credentials under several server aliases or paste passwords into commands.

### 3. Inspect one denied directory ACL

Run on: **OMV over authorized SSH**.

```text
No command: run getfacl -p on the exact denied folder and its parent after identifying its backing filesystem.
```

Expected: Share access and filesystem traversal/write rights both include the intended account.

If not: September 28 proved nasadmin share rights were present while folder ACLs denied writes. Check both layers; do not recursively reset ownership/permissions across libraries or backup data.

References: [Operating guide](../install/phases/06-omv-nas.md) · [Service inventory](../reference/service-matrix.md)

<a id="nas-speed"></a>
## NAS copies or archive extraction stop and start

Separate many-small-file metadata latency from link speed, disk pressure and concurrent work.

Required evidence: NAS listener (`nas`); Large-file versus small-file behavior (`transfer_pattern`); Link and storage load (`nas_load`).

### 1. Record the stalled operation

Run on: **Windows workstation / transfer or archive tool**.

```text
No command: record source/destination, file count, typical size, whether pauses occur between files, and concurrent jobs.
```

Expected: The slowdown pattern is reproducible without retrying a destructive move.

If not: Long pauses between thousands of files may be SMB metadata work, not poor bulk throughput. A transfer speed gauge alone cannot identify the cause.

### 2. Read negotiated adapter speed

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Get-NetAdapter | Select-Object Name,Status,LinkSpeed; Get-SmbConnection | Select-Object ServerName,ShareName,Dialect
```

Expected: The expected wired adapter is active at its negotiated speed, with a modern SMB dialect.

If not: LinkSpeed is not measured throughput. Compare wired versus Wi-Fi history and NAS CPU/disk activity before changing SMB settings.

### 3. Read NAS load and capacity

Run on: **OMV over authorized SSH**.

```text
uptime; free -h; df -h; df -i
```

Expected: Storage has headroom and concurrent jobs are understood.

If not: A large copy, torrent, indexing run or small-file extraction can compete for disk work. A local-SSD extraction comparison is a separate optional write test; do not disable security scanning or kill transfers as a diagnostic shortcut.

References: [Operating guide](../install/phases/06-omv-nas.md) · [Service inventory](../reference/service-matrix.md)

<a id="printer-queue"></a>
## Bambuddy queue is stuck while the printer is idle

Distinguish the plate-clear safety gate, upload progress and weak printer Wi-Fi.

Required evidence: Docker host reachable (`docker_host`); Queue safety state (`queue_gate`); Upload progress and signal (`printer_upload`).

### 1. Inspect the physical printer queue

Run on: **Bambuddy / Printers / physical P1S card**.

```text
No command: read awaiting_plate_clear, printer state and queued-job status.
```

Expected: The queue’s explicit blocking reason is understood.

If not: Idle or FINISH does not mean ready for another print. The control is Clear Bed; it can immediately release a queued job. Do not press it until the plate is physically clear and a start is intended.

### 2. Compare upload and dispatch stages

Run on: **Bambuddy UI / existing Central Logs dashboard**.

```text
No command: read file size, transferred bytes, elapsed time and first upload/FTP error; omit access codes and authenticated URLs.
```

Expected: Upload progress is distinct from awaiting-plate-clear and preparing/running states.

If not: A September incident transferred about 124 MB at 135 KB/s before dispatch. Do not resend an already queued file or cancel an active job to test the path.

### 3. Inspect the established metrics

Run on: **Grafana / Bambuddy Metrics dashboard**.

```text
No command: compare printer connectivity, state, Wi-Fi signal and metric timestamps.
```

Expected: Recent samples explain the queue state and signal quality.

If not: Weak signal around -80 dBm was observed previously, not established for the current incident. A green dashboard or current upload is not permission to bypass the queue gate.

References: [Operating guide](../../scripts/setup/printers/bambuddy_p1s_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="frontend-cache"></a>
## An app shows an old version or cannot save

Separate stale frontend/service-worker assets, browser API support and rejected backend writes.

Required evidence: Docker host reachable (`docker_host`); Served and displayed release (`frontend_version`); Browser error or API outcome (`save_response`).

### 1. Identify the failure before retrying writes

Run on: **Affected browser / developer tools**.

```text
No command: record displayed version, secure-context status, exact console error and failed request status; exclude request bodies/cookies/tokens.
```

Expected: The problem is identified as a browser exception or backend response.

If not: crypto.randomUUID can be unavailable in a browser/webview; Recomp has a getRandomValues fallback. A client exception before a request is different from a server rejecting a save.

### 2. Compare served and container versions

Run on: **VM 103 / docker-host**.

```text
docker inspect recomp-tracker --format "{{.Image}} {{.State.Status}}"
```

Expected: The image matches the recorded Recomp release and browser version.

If not: The runtime tag alone may lag behind the recorded source. Compare the app handoff and served assets; do not rebuild from an incomplete source or overwrite saved data.

### 3. Inspect the existing service-worker state

Run on: **Affected browser / application storage tools**.

```text
No command: inspect active worker/cache version and whether the tab retained an older script.
```

Expected: Browser assets match the deployed release.

If not: Preserve unsaved work before refreshing. Do not clear all site storage: browser-only records or sessions may be lost. A server restart alone does not invalidate an old worker.

References: [Operating guide](../install/services/recomp-tracker.md) · [Service inventory](../reference/service-matrix.md)

<a id="esphome-identity"></a>
## ESPHome controls the wrong device or shows stale entities

Separate physical board identity, production firmware, MQTT topic and stale HA registry entries.

Required evidence: Home Assistant HTTPS (`ha_http`); Board and firmware identity (`device_identity`); HA entity and MQTT mapping (`entity_identity`).

### 1. Identify the physical board without motion

Run on: **Device owner / ESPHome and project record**.

```text
No command: compare device name, IP/MAC, flashed YAML and labelled physical board.
```

Expected: Each controller matches its dedicated production file and role.

If not: Valve 2 previously ran a Valve 1 image; an IP responding does not establish correct physical identity. Do not command a servo to identify a board.

### 2. Compare HA integration and MQTT identity

Run on: **Home Assistant / device and entity details**.

```text
No command: compare ESPHome device IDs, entity availability and recorded MQTT topic prefixes.
```

Expected: No duplicated device or topic namespace is active.

If not: Stale Valve 1 registry IDs can survive a corrected Valve 2 flash. Distinguish stale entries from the actual controller before removal or re-adoption.

### 3. Separate reset from supply-loss behavior

Run on: **Physical owner / accepted bench procedure**.

```text
No command: record whether the last outage followed USB power loss, RST/EN or firmware flashing, and whether the servo signal was connected.
```

Expected: Existing observations distinguish Wi-Fi/API availability from physical startup movement.

If not: Uncalibrated feedback is not shaft angle. Startup movement can occur with signal disconnected. Stop before rewiring, flashing or actuation; use the documented unloaded test procedure and identify the power path first.

References: [Operating guide](../diagrams/wiring-diagrams/ventsys_wiring_reference.md) · [Service inventory](../reference/service-matrix.md)

<a id="docker-build"></a>
## Docker app runs but builds or downloads fail

Separate running-stack health from default build-network, package route and release-source problems.

Required evidence: Docker host reachable (`docker_host`); Default Docker bridge (`build_network`); Release source and dependencies (`build_source`).

### 1. Inspect the default build network

Run on: **VM 103 / docker-host**.

```text
docker network inspect bridge --format "{{json .IPAM.Config}}"; ip -4 address show docker0
```

Expected: The bridge configuration and actual docker0 interface agree.

If not: A missing docker0 was recorded for VM103 while explicit Compose networks still ran. Healthy apps do not prove a default dependency build can reach the network.

### 2. Compare build and runtime failure

Run on: **Build logs / canonical release procedure**.

```text
No command: identify the first failed stage, DNS/download error, and whether the build requires new dependencies.
```

Expected: A source-only offline build is distinguished from a dependency-fetching build.

If not: Preserve the installed runtime image and rollback. Do not use host networking, broad firewall allowances or package upgrades to bypass an unexplained build-network fault.

### 3. Check source completeness

Run on: **Canonical checkout / app install manual**.

```text
No command: confirm the maintained source, release artifact and documented deployment command.
```

Expected: The chosen release can be rebuilt and validated without replacing live data.

If not: Household Hub has a documented incomplete source mirror. A running container is not evidence of a safe rebuild; use the recovery register before changing its image.

References: [Operating guide](../../scripts/setup/proxmox/docker_host_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="internet"></a>
## Internet or Wi-Fi stops working

Separate one client or SSID from a router, PPPoE or upstream outage.

Required evidence: Router reachable (`router`); Client address and gateway (`client_network`); PPPoE session (`wan_session`).

### 1. Check the affected client address

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Get-NetIPConfiguration
```

Expected: Address, gateway and DNS match the intended SSID/subnet.

If not: A self-assigned address or wrong subnet points to Wi-Fi, DHCP or VLAN placement. Compare another client first.

### 2. Read WAN state

Run on: **OpenWrt router**.

```text
ubus call network.interface.wan status
```

Expected: WAN is up with a PPPoE address and default route.

If not: Record disconnect times and check the ONT/link before changing router settings or PPPoE credentials.

### 3. Inspect wireless interfaces

Run on: **OpenWrt router**.

```text
iw dev
```

Expected: The intended SSID interfaces are present.

If not: If wired access works, isolate band, SSID and signal. Use the recorded cabling plan; do not swap VLAN ports blindly.

References: [Operating guide](troubleshooting_reference.md) · [Service inventory](../reference/service-matrix.md)

<a id="dns"></a>
## Local names or web searches fail

Distinguish local DNS, AdGuard filtering and public upstream resolution.

Required evidence: Router reachable (`router`); Local DNS answer (`dns_local`); Public DNS answer (`dns_public`).

### 1. Query the router directly

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Resolve-DnsName homepage.home.local -Server 192.168.10.1 -DnsOnly
```

Expected: HomeAdmin receives 192.168.20.102.

If not: Wrong or missing DNS is a separate failure from a server working by IP. Remote split DNS uses a different path.

### 2. Compare public resolution

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Resolve-DnsName example.com -Server 192.168.10.1 -DnsOnly
```

Expected: A public answer is returned.

If not: Local success with public failure narrows the fault to forwarding, upstream DNS or WAN.

### 3. Inspect client DNS and VPN context

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Get-DnsClientServerAddress -AddressFamily IPv4
```

Expected: Identify active adapters, DNS servers and any VPN DNS filtering.

If not: A VPN can block direct router DNS even with LAN sharing enabled. Compare router-local resolution before changing infrastructure; do not disable leak protection or change the public resolver without an explicit choice.

### 4. Compare on the router

Run on: **OpenWrt router**.

```text
nslookup homepage.home.local 127.0.0.1
```

Expected: The router itself returns 192.168.20.102.

If not: Router-local success plus workstation timeout points to the client/path, not a missing record. It does not prove every VLAN can query DNS.

### 5. Read AdGuard state

Run on: **VM 103 / docker-host**.

```text
docker ps --filter name=adguard
```

Expected: AdGuard is running; its query log explains the exact failed domain.

If not: Review filtering/upstream errors before changing client DNS. Router remains local-name authority.

References: [Operating guide](troubleshooting_reference.md) · [Service inventory](../reference/service-matrix.md)

<a id="tls"></a>
## Certificate warning or HTTPS failure

Separate certificate trust, hostname and clock errors from a dead listener.

Required evidence: Router reachable (`router`); Homepage listener (`homepage`); Trusted HTTPS response (`tls_trust`).

### 1. Read the actual TLS error

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
curl.exe -I https://homepage.home.local/
```

Expected: HTTPS responds without bypassing certificate validation.

If not: Record hostname and certificate error. Do not switch to plain HTTP or treat a bypassed check as trust proof.

### 2. Isolate DNS while preserving hostname validation

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
curl.exe --resolve homepage.home.local:443:192.168.20.102 -I https://homepage.home.local/
```

Expected: The intended hostname selects its certificate and responds.

If not: This bypasses DNS only. A wrong certificate can indicate a missing SNI route. CRYPT_E_NO_REVOCATION_CHECK means revocation evidence is unavailable; it is distinct from expiry or an untrusted CA. Do not globally disable certificate checks.

### 3. Check the client clock

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Get-Date -Format o
```

Expected: Time and timezone match a trusted clock.

If not: Clock drift can invalidate certificates and make imported evidence future-dated.

### 4. Validate the existing proxy config

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/homepage/docker-compose.yml exec -T preview-proxy nginx -t
```

Expected: The Nginx configuration is valid.

If not: Config validity is not certificate acceptance. Check expiry and client CA installation through the TLS guide.

References: [Operating guide](../procedures/ssl_tls_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="remote"></a>
## Works at home, fails remotely

Trace the approved Tailscale identity, split DNS and fixed Homepage proxy.

Required evidence: Docker host reachable (`docker_host`); Approved remote path (`tailscale_path`); Remote proxy response (`remote_proxy`).

### 1. Identify the exact remote failure

Run on: **Remote client**.

```text
No command: record URL, client identity, network and exact error.
```

Expected: The device uses its approved portal or narrow host route.

If not: LAN reachability does not prove a remote grant. Do not add broad VLAN routes.

### 2. Read Tailscale state

Run on: **VM 103 / docker-host**.

```text
tailscale status
```

Expected: The node is connected and the intended client is present.

If not: Preserve the identity/connectivity error without sharing keys. WireGuard remains a separately gated fallback.

### 3. Read fixed-proxy state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/homepage/docker-compose.yml ps
```

Expected: Homepage and preview-proxy are running.

If not: One failing card suggests its upstream or auth; all cards failing suggests the shared remote path.

References: [Operating guide](../diagrams/network/remote-access-flow.mermaid) · [Service inventory](../reference/service-matrix.md)

<a id="guests"></a>
## Guests disappear after a reboot

Separate Proxmox availability, guest startup and the shared network trunk.

Required evidence: Proxmox listener (`proxmox_api`); Guest running state (`guest_state`); Guest network placement (`guest_network`).

### 1. Test the management listener

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Test-NetConnection 192.168.10.10 -Port 8006
```

Expected: Proxmox answers from HomeAdmin.

If not: If unavailable, use the local console and recorded LAN1 trunk path. Preserve management access.

### 2. Read VM inventory

Run on: **Proxmox host**.

```text
qm list
```

Expected: Production VMs run; VM101 and VM104 stay rollback-only unless their roles changed.

If not: Record the stopped production guest and its console error before starting or restoring anything.

### 3. Read container inventory

Run on: **Proxmox host**.

```text
pct list
```

Expected: CT111 and CT114 have their intended state.

If not: Several lost guests may share host capacity or bridge failure; one failed guest needs its own console/startup evidence.

References: [Operating guide](../../configs/proxmox/guest-configs.md) · [Service inventory](../reference/service-matrix.md)

<a id="docker"></a>
## Several apps are slow or down

Check shared Docker-host resources before treating each app as a separate fault.

Required evidence: Docker host reachable (`docker_host`); Disk and memory (`docker_capacity`); Container runtime (`docker_runtime`).

### 1. Inspect container state

Run on: **VM 103 / docker-host**.

```text
docker ps -a --format "table {{.Names}}	{{.Status}}"
```

Expected: Expected services run without restart loops.

If not: Compare failure times and dependencies; preserve the first error rather than recreating every stack.

### 2. Check blocks and inodes

Run on: **VM 103 / docker-host**.

```text
df -h / /opt; df -i / /opt
```

Expected: Both disk space and inodes have headroom.

If not: A full filesystem can break databases, logs and updates together. Do not prune volumes or delete app data.

### 3. Check memory and current load

Run on: **VM 103 / docker-host**.

```text
free -h; docker stats --no-stream
```

Expected: Memory is available and no container is exhausting the host.

If not: Record sustained pressure and OOM evidence before changing guest allocations or limits.

References: [Operating guide](../../scripts/setup/proxmox/docker_host_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="storage"></a>
## Files disappear or storage fills

Check NAS mount source, capacity and permissions without writing into a fallback local directory.

Required evidence: OMV NFS listener (`nas`); Expected NFS source (`nas_mount`); Space and inodes (`nas_capacity`).

### 1. Identify the actual filesystem

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/immich; findmnt -T /mnt/omv/media
```

Expected: Each path resolves to its expected OMV NFS export.

If not: A directory existing does not prove a mount. If it resolves to VM root storage, stop writes and follow mount recovery.

### 2. Read usage without deleting files

Run on: **VM 103 / docker-host**.

```text
df -h /mnt/omv/immich /mnt/omv/media; df -i /mnt/omv/immich /mnt/omv/media
```

Expected: The expected exports have capacity.

If not: Separate full storage, inode exhaustion and missing mounts. Avoid recursive chmod/chown or deletion.

### 3. Review disk and array health

Run on: **OMV web UI / Storage**.

```text
No command: inspect Filesystems, RAID and SMART health.
```

Expected: Expected filesystems/arrays are available without new disk errors.

If not: Capture degraded-array or SMART evidence. Do not force filesystem repair, replace disks or restore before identifying affected data.

References: [Operating guide](../procedures/omv_cutover_execution_runbook.md) · [Service inventory](../reference/service-matrix.md)

<a id="app-backup"></a>
## Application backup job fails

Investigate VM103 app-data copies separately from Proxmox guest archives.

Required evidence: OMV NFS listener (`nas`); Backup mount source (`app_backup_mount`); App-data job result (`app_backup_job`).

### 1. Check the dedicated backup mount

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/docker-host-backups
```

Expected: The path is the intended OMV backup export.

If not: Do not rerun the job into an unmounted local directory.

### 2. Read timer and job state

Run on: **VM 103 / docker-host**.

```text
systemctl status docker-host-app-data-backup.timer docker-host-app-data-backup.service --no-pager
```

Expected: The timer is scheduled and the last service result is understood.

If not: A waiting timer does not prove the last backup succeeded.

### 3. Read the first job error

Run on: **VM 103 / docker-host**.

```text
journalctl -u docker-host-app-data-backup.service --since "48 hours ago" --no-pager -n 100
```

Expected: Selected dumps and copies completed.

If not: Separate dump, copy, permission, mount and heartbeat failures. Freshness alone is not restore proof.

References: [Operating guide](../../scripts/backup/backup_strategy.md) · [Service inventory](../reference/service-matrix.md)

<a id="monitoring"></a>
## Graphs or health monitors go blank

Separate a failed service from a broken monitoring pipeline or blocked observer.

Required evidence: Grafana HTTP (`grafana`); Kuma HTTP (`uptime_kuma`); Recent metric timestamps (`metrics_fresh`).

### 1. Test monitoring interfaces

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
Test-NetConnection 192.168.60.10 -Port 3000; Test-NetConnection 192.168.60.10 -Port 3001
```

Expected: Both approved management listeners respond.

If not: If both fail, check VM102 and access scope before editing dashboards.

### 2. Read monitoring container state

Run on: **VM 102 / monitoring**.

```text
docker ps -a --format "table {{.Names}}	{{.Status}}"
```

Expected: Grafana, Kuma and configured data services run.

If not: A healthy app can look down when its observer or source firewall path fails.

### 3. Compare timestamps and target

Run on: **Grafana / Uptime Kuma UI**.

```text
No command: inspect last sample time, time range, monitor target and exact error.
```

Expected: Metrics are recent and the observer uses an allowed source.

If not: Old green graphs cannot establish current health. Keep InfluxDB private.

References: [Operating guide](../../scripts/setup/proxmox/monitoring_vm_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="local-ai"></a>
## Local AI fails or becomes very slow

Separate CT114 reachability, model startup, GPU access and the chat frontend.

Required evidence: Chat endpoint (`llamacpp`); Open WebUI listener (`openwebui`); Model ready (`ai_model`); Inference resources (`ai_capacity`).

### 1. Inspect inference and frontend

Run on: **CT 114 / local AI**.

```text
docker compose -f /opt/stacks/local-ai/docker-compose.yml ps
```

Expected: The model and intended frontend are running.

If not: A working Open WebUI page does not prove inference readiness.

### 2. Read model startup errors

Run on: **CT 114 / local AI**.

```text
docker logs --tail 80 llama-cpp
```

Expected: The configured model loaded and is listening without repeated GPU/allocation errors.

If not: Preserve relevant redacted startup lines; do not change model files or GPU mappings during diagnosis.

### 3. Check resource availability

Run on: **CT 114 / local AI**.

```text
free -h; ls -l /dev/dri; docker stats --no-stream
```

Expected: Memory and expected render devices are available.

If not: Compare CT configuration and shared-GPU consumers before changing permissions or context size.

References: [Operating guide](../../scripts/setup/proxmox/llm_host_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="voice"></a>
## Voice hears nothing or gives no reply

Locate the failure between wake word, transcription, conversation and speech output.

Required evidence: Home Assistant HTTPS (`ha_http`); Assist trace (`voice_pipeline`); Wyoming services (`voice_services`).

### 1. Locate the failed voice stage

Run on: **Home Assistant / Assist pipeline debug**.

```text
No command: inspect the latest trace and its first failed stage.
```

Expected: Wake word, transcription, conversation and output complete in order.

If not: A transcript with no reply suggests conversation/output, not microphone reachability. Avoid repeated device actuation tests.

### 2. Read voice-service state

Run on: **CT 114 / local AI**.

```text
docker compose -f /opt/stacks/local-ai/docker-compose.yml ps
```

Expected: Configured Whisper, Piper and OpenWakeWord services run.

If not: Match the failed stage to its service; the HA voice migration may still be pending.

### 3. Inspect transcription errors

Run on: **CT 114 / local AI**.

```text
docker logs --tail 60 wyoming-whisper
```

Expected: No repeated connection or model-loading errors for transcription.

If not: For output/wake-word failures inspect the corresponding Piper/OpenWakeWord log. Redact household speech before sharing.

References: [Operating guide](../../scripts/setup/proxmox/llm_host_setup_guide.md) · [Service inventory](../reference/service-matrix.md)

<a id="automations"></a>
## HA opens but an automation does nothing

Distinguish trigger and condition failures from unavailable entities or integrations.

Required evidence: Home Assistant HTTPS (`ha_http`); MQTT TLS listener (`mqtt`); Trace and entities (`automation_trace`).

### 1. Inspect the latest automation trace

Run on: **Home Assistant / Settings / Automations**.

```text
No command: note the last completed trigger, condition or action.
```

Expected: The trigger fired, conditions passed and entity IDs resolved.

If not: No trace suggests a trigger or disabled automation; a stopped trace identifies the condition/action to inspect.

### 2. Read entity state without changing it

Run on: **Home Assistant / Developer tools / States**.

```text
No command: inspect availability and last-updated time.
```

Expected: The affected entity has recent data.

If not: An open MQTT port does not prove client authentication or topic delivery. Do not use Set state as a repair.

### 3. Validate HA configuration

Run on: **Home Assistant Terminal & SSH add-on**.

```text
ha core check
```

Expected: Configuration validation passes.

If not: Preserve named YAML/package errors. Do not manually trigger heaters, fans, plugs or safety automations as a shortcut.

References: [Operating guide](troubleshooting_reference.md) · [Service inventory](../reference/service-matrix.md)

<a id="notifications"></a>
## Expected notifications never arrive

Separate the producing job, ntfy delivery and phone subscription without sending test messages.

Required evidence: Docker host reachable (`docker_host`); Producer job outcome (`notification_producer`); Delivery response (`notification_delivery`).

### 1. Read the producer result

Run on: **VM 103 / docker-host**.

```text
docker logs --tail 80 watchtower
```

Expected: The monitor-only scan outcome and delivery response are visible.

If not: A scan can succeed while delivery fails. September7 recorded error40014; establish whether it still applies.

### 2. Read notification-service state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/ntfy/docker-compose.yml ps
```

Expected: ntfy is running.

If not: Topic names, URLs and auth values may be private; share only redacted error evidence.

### 3. Inspect the receiving subscription

Run on: **Phone / ntfy app**.

```text
No command: inspect server, subscription, notification permission and battery restrictions.
```

Expected: The intended subscription and permissions are present.

If not: Do not loosen authentication or attachment policy. An actual test notification is a separate acceptance action.

References: [Operating guide](../install/services/ntfy.md) · [Service inventory](../reference/service-matrix.md)

<a id="updates"></a>
## Updates fail or package lists are old

Check the approved package path and metadata age without installing or upgrading anything.

Required evidence: Approved package path (`package_route`); Metadata timestamp (`package_metadata`); Cache listener from workstation (`package_cache`).

### 1. Read the configured APT proxy

Run on: **Affected Debian guest**.

```text
apt-config dump | grep -i proxy
```

Expected: Proxy configuration matches the approved cache design.

If not: No output means no configured proxy. CT114 previously lacked a proxy and could not reach3142; verify current evidence.

### 2. Read cached metadata age

Run on: **Affected Debian guest**.

```text
find /var/lib/apt/lists -maxdepth 1 -name "*InRelease" -printf "%TY-%Tm-%Td %TH:%TM %f\n"
```

Expected: Metadata is recent enough to assess candidates.

If not: Old candidate lists are not a current security assessment. Do not upgrade to diagnose connectivity.

### 3. Read cache service state

Run on: **VM 103 / docker-host**.

```text
systemctl status apt-cacher-ng --no-pager
```

Expected: The intended cache service is active.

If not: Separate service failure from guest-to-cache access. Repair the approved path during maintenance before refreshing metadata.

References: [Operating guide](../procedures/apt_cacher_ng_design.md) · [Service inventory](../reference/service-matrix.md)

<a id="photos"></a>
## Immich uploads or thumbnails fail

Separate the photo API, database, background jobs and NAS upload/library mount.

Required evidence: Docker host reachable (`docker_host`); OMV NFS listener (`nas`); Immich API listener (`immich`); Upload and job outcome (`immich_jobs`).

### 1. Read Immich service state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/immich/docker-compose.yml ps
```

Expected: Required server and data services run.

If not: Separate UI/API errors from database and machine-learning failures.

### 2. Verify the media filesystem

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/immich; df -h /mnt/omv/immich
```

Expected: The intended export is mounted with capacity.

If not: Stop upload attempts if it falls back to root storage; do not move or delete originals.

### 3. Inspect one failed upload or job

Run on: **Immich administration UI**.

```text
No command: read job failures and the exact error for one affected item.
```

Expected: Uploads and relevant background jobs complete.

If not: A failed thumbnail is not proof of a lost original. Preserve originals, database and matching versions before recovery.

References: [Operating guide](../install/services/immich.md) · [Service inventory](../reference/service-matrix.md)

<a id="media"></a>
## Media library is empty or playback fails

Separate Jellyfin, Calibre-Web or Atsumeru from missing mounts and client playback issues.

Required evidence: OMV NFS listener (`nas`); Library mount source (`media_mount`); Library service (`media_application`).

### 1. Check the shared media mount

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/media; df -h /mnt/omv/media
```

Expected: The intended export is mounted and readable.

If not: Do not rescan an empty fallback directory or move files between library roots.

### 2. Inspect application state

Run on: **VM 103 / docker-host**.

```text
docker ps -a --format "table {{.Names}}	{{.Status}}"
```

Expected: The selected media application runs.

If not: Use its stack guide to distinguish database/config problems from missing media.

### 3. Compare one known item and another client

Run on: **Affected media UI**.

```text
No command: test a known item and record the playback or scan error.
```

Expected: A known item is indexed and accessible to the intended account.

If not: One failing client suggests codec/session trouble; an empty library for everyone suggests mount/path/permissions. Jellyfin media is intentionally read-only.

References: [Operating guide](../../configs/docker-host/stacks/jellyfin/README.md) · [Service inventory](../reference/service-matrix.md)

<a id="downloads"></a>
## Downloads stall or the client disappears

Check VPN containment, client state and staging storage without bypassing the tunnel.

Required evidence: VPN container health (`download_vpn`); Download client (`download_client`); Staging mount (`download_storage`).

### 1. Read VPN and client state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/download-gateway/docker-compose.yml ps
```

Expected: VPN health is established before using the client.

If not: The client may be deliberately contained when the tunnel fails. Do not move it to host networking.

### 2. Read the recent tunnel error

Run on: **VM 103 / docker-host**.

```text
docker logs --tail 60 download-vpn
```

Expected: The intended provider tunnel is established.

If not: Redact provider/account information. Do not bypass the kill switch.

### 3. Inspect staging storage

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/media; df -h /mnt/omv/media
```

Expected: The staging export is mounted with capacity.

If not: Do not mount final libraries into the download client. Full staging requires reviewed cleanup, not broad deletion.

References: [Operating guide](../../configs/docker-host/stacks/download-gateway/README.md) · [Service inventory](../reference/service-matrix.md)

<a id="sync"></a>
## Notes stop syncing or conflict

Separate the local vault, sync transport and CouchDB without replacing canonical data.

Required evidence: Docker host reachable (`docker_host`); Sync connection (`sync_transport`); Vault conflict review (`sync_conflicts`).

### 1. Preserve the local state first

Run on: **Canonical Windows vault / Obsidian**.

```text
No command: record affected files and last sync; preserve local edits before resolving conflicts.
```

Expected: The canonical K: vault and unsynced edits are identified.

If not: Do not reset a database or overwrite a device to remove a warning.

### 2. Read sync backend state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/obsidian-livesync/docker-compose.yml ps
```

Expected: The intended CouchDB backend runs.

If not: This does not prove credentials, CORS, remote HTTPS or plugin settings.

### 3. Inspect the plugin error

Run on: **Obsidian / LiveSync status**.

```text
No command: capture error category and affected documents without tokens or passwords.
```

Expected: The intended vault/database is selected and replication completes.

If not: Git history and replication solve different problems. Reconcile conflicts deliberately; never bulk accept deletions.

References: [Operating guide](../install/services/obsidian-livesync.md) · [Service inventory](../reference/service-matrix.md)

<a id="household"></a>
## An app opens but its data fails

Investigate Mealie, Grocy, GardenKeeper, Household Hub and Recomp API/database boundaries.

Required evidence: Docker host reachable (`docker_host`); Affected API response (`household_api`); Database and saved data (`household_data`).

### 1. Identify one failing operation

Run on: **Affected app / browser developer tools**.

```text
No command: record app, time, action, request path and HTTP status; exclude bodies, cookies and tokens.
```

Expected: The intended API responds for the signed-in account.

If not: Static HTML does not prove API/auth/database health. Avoid repeatedly submitting writes.

### 2. Read stack state

Run on: **VM 103 / docker-host**.

```text
docker ps -a --format "table {{.Names}}	{{.Status}}"
```

Expected: The affected frontend and data services run.

If not: Compare the service inventory. Do not rebuild Household Hub from its incomplete source mirror.

### 3. Check shared data capacity

Run on: **VM 103 / docker-host**.

```text
df -h /opt; df -i /opt
```

Expected: The app data filesystem has capacity.

If not: Before database repair or version change, identify its matching backup. Preserve data and avoid reseeding a live app.

References: [Operating guide](../reference/service-matrix.md) · [Service inventory](../reference/service-matrix.md)

<a id="vault"></a>
## Password vault login or sync fails

Separate trusted HTTPS, client/account state and Vaultwarden without weakening access controls.

Required evidence: Docker host reachable (`docker_host`); Trusted vault HTTPS (`vault_tls`); Vaultwarden state (`vault_service`).

### 1. Check trusted HTTPS

Run on: **Windows HomeAdmin workstation / PowerShell**.

```text
curl.exe -I https://vault.home.local/
```

Expected: The canonical endpoint responds without a certificate bypass.

If not: Do not enter credentials on an unexpected hostname or expose the raw backend.

### 2. Read Vaultwarden state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/vaultwarden/docker-compose.yml ps
```

Expected: The service runs.

If not: Preserve the account error separately from availability. Do not enable open signup or change admin tokens.

### 3. Separate one client from a server-wide failure

Run on: **Approved vault clients**.

```text
No command: compare error categories with another already-authorized client.
```

Expected: The intended server and account are selected.

If not: Do not sign out the last working client, delete its local vault or restore over the live database as a test.

References: [Operating guide](../install/services/vaultwarden.md) · [Service inventory](../reference/service-matrix.md)

<a id="ventsys"></a>
## VentSys device or dashboard is offline

Establish commissioning state before investigating telemetry; no actuation or safety acceptance.

Required evidence: Home Assistant HTTPS (`ha_http`); MQTT TLS listener (`mqtt`); Commissioned device telemetry (`ventsys_telemetry`).

### 1. Establish commissioning state

Run on: **Project record / device owner**.

```text
No command: confirm this sensor/controller is installed and accepted.
```

Expected: Identity, power, network and role are known.

If not: Hardware acceptance was pending in September. A planned device is not an unexpected live outage.

### 2. Read device availability

Run on: **Home Assistant / ESPHome integration**.

```text
No command: inspect last update, availability and integration error.
```

Expected: A commissioned device has recent telemetry.

If not: Separate Wi-Fi, authentication and entity names. Never put credentials into dashboard HTML.

### 3. Stop before physical testing

Run on: **Physical installation / acceptance procedure**.

```text
No command: record missing evidence before any fan, valve, heater or plug action.
```

Expected: Safety and failsafe tests have a separate accepted procedure.

If not: Green network checks cannot prove airflow, smoke response, power isolation or safe operation.

References: [Operating guide](../diagrams/ventsys/ventsys-control-and-safety-flow.mermaid) · [Service inventory](../reference/service-matrix.md)

<a id="phone-relay"></a>
## Phone stream or recordings stop

Separate phone publisher, MediaMTX relay, viewer and OMV recording storage.

Required evidence: Docker host reachable (`docker_host`); Authenticated phone stream (`phone_stream`); Recording mount and files (`phone_recording`).

### 1. Read relay state

Run on: **VM 103 / docker-host**.

```text
docker compose -f /opt/stacks/mediamtx/docker-compose.yml ps
```

Expected: MediaMTX runs.

If not: An idle relay may simply have no publisher. Real phone-session acceptance and retention remain separate gates.

### 2. Inspect recent relay errors

Run on: **VM 103 / docker-host**.

```text
docker logs --tail 60 mediamtx
```

Expected: Expected publisher/reader connect without repeated auth/codec errors.

If not: Redact authenticated URLs. Verify the HomeAdmin source and RTSP-over-TCP path; do not open new ports.

### 3. Verify recording storage

Run on: **VM 103 / docker-host**.

```text
findmnt -T /mnt/omv/media; df -h /mnt/omv/media
```

Expected: OMV is mounted with capacity.

If not: No automatic deletion was approved in the baseline. Do not delete recordings to diagnose a stream failure.

References: [Operating guide](../install/services/mediamtx.md) · [Service inventory](../reference/service-matrix.md)
