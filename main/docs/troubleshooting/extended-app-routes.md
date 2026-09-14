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
