// Read-only investigations grounded in the service matrix and operating guides.
const vm = 'VM 103 / docker-host';
const pc = 'Windows HomeAdmin workstation / PowerShell';
const ai = 'CT 114 / local AI';
const reference = 'docs/troubleshooting/troubleshooting_reference.md';
const inventory = 'docs/reference/service-matrix.md';
const check = (key, label, stage) => ({ key, label, stage });
const command = (title, runOn, command, expected, failure) => ({ title, runOn, command, expected, failure });
function route(id, category, title, short, checks, steps, guide = reference) {
  return { id, category, title, short, description: short,
    checks: checks.map(([key, label, stage = 'Evidence']) => check(key, label, stage)),
    path: checks.map(([key, label]) => ({ label, keys: [key] })),
    steps: steps.map((step, i) => ({ ...step, id: `${id}-${i}`, stage: 'Evidence' })),
    docs: [['Operating guide', guide], ['Service inventory', inventory]],
  };
}
export const additionalRoutes = [
  route('internet', 'Network and access', 'Internet or Wi-Fi stops working',
    'Separate one client or SSID from a router, PPPoE or upstream outage.',
    [['router', 'Router reachable'], ['client_network', 'Client address and gateway'], ['wan_session', 'PPPoE session']], [
      command('Check the affected client address', pc, 'Get-NetIPConfiguration', 'Address, gateway and DNS match the intended SSID/subnet.', 'A self-assigned address or wrong subnet points to Wi-Fi, DHCP or VLAN placement. Compare another client first.'),
      command('Read WAN state', 'OpenWrt router', 'ubus call network.interface.wan status', 'WAN is up with a PPPoE address and default route.', 'Record disconnect times and check the ONT/link before changing router settings or PPPoE credentials.'),
      command('Inspect wireless interfaces', 'OpenWrt router', 'iw dev', 'The intended SSID interfaces are present.', 'If wired access works, isolate band, SSID and signal. Use the recorded cabling plan; do not swap VLAN ports blindly.'),
    ]),
  route('dns', 'Network and access', 'Local names or web searches fail',
    'Distinguish local DNS, AdGuard filtering and public upstream resolution.',
    [['router', 'Router reachable'], ['dns_local', 'Local DNS answer'], ['dns_public', 'Public DNS answer']], [
      command('Query the router directly', pc, 'Resolve-DnsName homepage.home.local -Server 192.168.10.1 -DnsOnly', 'HomeAdmin receives 192.168.20.102.', 'Wrong or missing DNS is a separate failure from a server working by IP. Remote split DNS uses a different path.'),
      command('Compare public resolution', pc, 'Resolve-DnsName example.com -Server 192.168.10.1 -DnsOnly', 'A public answer is returned.', 'Local success with public failure narrows the fault to forwarding, upstream DNS or WAN.'),
      command('Read AdGuard state', vm, 'docker ps --filter name=adguard', 'AdGuard is running; its query log explains the exact failed domain.', 'Review filtering/upstream errors before changing client DNS. Router remains local-name authority.'),
    ]),
  route('tls', 'Network and access', 'Certificate warning or HTTPS failure',
    'Separate certificate trust, hostname and clock errors from a dead listener.',
    [['router', 'Router reachable'], ['homepage', 'Homepage listener'], ['tls_trust', 'Trusted HTTPS response']], [
      command('Read the actual TLS error', pc, 'curl.exe -I https://homepage.home.local/', 'HTTPS responds without bypassing certificate validation.', 'Record hostname and certificate error. Do not switch to plain HTTP or treat a bypassed check as trust proof.'),
      command('Check the client clock', pc, 'Get-Date -Format o', 'Time and timezone match a trusted clock.', 'Clock drift can invalidate certificates and make imported evidence future-dated.'),
      command('Validate the existing proxy config', vm, 'docker compose -f /opt/stacks/homepage/docker-compose.yml exec -T preview-proxy nginx -t', 'The Nginx configuration is valid.', 'Config validity is not certificate acceptance. Check expiry and client CA installation through the TLS guide.'),
    ], 'docs/procedures/ssl_tls_guide.md'),
  route('remote', 'Network and access', 'Works at home, fails remotely',
    'Trace the approved Tailscale identity, split DNS and fixed Homepage proxy.',
    [['docker_host', 'Docker host reachable'], ['tailscale_path', 'Approved remote path'], ['remote_proxy', 'Remote proxy response']], [
      command('Identify the exact remote failure', 'Remote client', 'No command: record URL, client identity, network and exact error.', 'The device uses its approved portal or narrow host route.', 'LAN reachability does not prove a remote grant. Do not add broad VLAN routes.'),
      command('Read Tailscale state', vm, 'tailscale status', 'The node is connected and the intended client is present.', 'Preserve the identity/connectivity error without sharing keys. WireGuard remains a separately gated fallback.'),
      command('Read fixed-proxy state', vm, 'docker compose -f /opt/stacks/homepage/docker-compose.yml ps', 'Homepage and preview-proxy are running.', 'One failing card suggests its upstream or auth; all cards failing suggests the shared remote path.'),
    ], 'docs/diagrams/network/remote-access-flow.mermaid'),
  route('guests', 'Hosts and storage', 'Guests disappear after a reboot',
    'Separate Proxmox availability, guest startup and the shared network trunk.',
    [['proxmox_api', 'Proxmox listener'], ['guest_state', 'Guest running state'], ['guest_network', 'Guest network placement']], [
      command('Test the management listener', pc, 'Test-NetConnection 192.168.10.10 -Port 8006', 'Proxmox answers from HomeAdmin.', 'If unavailable, use the local console and recorded LAN1 trunk path. Preserve management access.'),
      command('Read VM inventory', 'Proxmox host', 'qm list', 'Production VMs run; VM101 and VM104 stay rollback-only unless their roles changed.', 'Record the stopped production guest and its console error before starting or restoring anything.'),
      command('Read container inventory', 'Proxmox host', 'pct list', 'CT111 and CT114 have their intended state.', 'Several lost guests may share host capacity or bridge failure; one failed guest needs its own console/startup evidence.'),
    ], 'configs/proxmox/guest-configs.md'),
  route('docker', 'Hosts and storage', 'Several apps are slow or down',
    'Check shared Docker-host resources before treating each app as a separate fault.',
    [['docker_host', 'Docker host reachable'], ['docker_capacity', 'Disk and memory'], ['docker_runtime', 'Container runtime']], [
      command('Inspect container state', vm, 'docker ps -a --format "table {{.Names}}\t{{.Status}}"', 'Expected services run without restart loops.', 'Compare failure times and dependencies; preserve the first error rather than recreating every stack.'),
      command('Check blocks and inodes', vm, 'df -h / /opt; df -i / /opt', 'Both disk space and inodes have headroom.', 'A full filesystem can break databases, logs and updates together. Do not prune volumes or delete app data.'),
      command('Check memory and current load', vm, 'free -h; docker stats --no-stream', 'Memory is available and no container is exhausting the host.', 'Record sustained pressure and OOM evidence before changing guest allocations or limits.'),
    ], 'scripts/setup/proxmox/docker_host_setup_guide.md'),
  route('storage', 'Hosts and storage', 'Files disappear or storage fills',
    'Check NAS mount source, capacity and permissions without writing into a fallback local directory.',
    [['nas', 'OMV NFS listener'], ['nas_mount', 'Expected NFS source'], ['nas_capacity', 'Space and inodes']], [
      command('Identify the actual filesystem', vm, 'findmnt -T /mnt/omv/immich; findmnt -T /mnt/omv/media', 'Each path resolves to its expected OMV NFS export.', 'A directory existing does not prove a mount. If it resolves to VM root storage, stop writes and follow mount recovery.'),
      command('Read usage without deleting files', vm, 'df -h /mnt/omv/immich /mnt/omv/media; df -i /mnt/omv/immich /mnt/omv/media', 'The expected exports have capacity.', 'Separate full storage, inode exhaustion and missing mounts. Avoid recursive chmod/chown or deletion.'),
      command('Review disk and array health', 'OMV web UI / Storage', 'No command: inspect Filesystems, RAID and SMART health.', 'Expected filesystems/arrays are available without new disk errors.', 'Capture degraded-array or SMART evidence. Do not force filesystem repair, replace disks or restore before identifying affected data.'),
    ], 'docs/procedures/omv_cutover_execution_runbook.md'),
  route('app-backup', 'Hosts and storage', 'Application backup job fails',
    'Investigate VM103 app-data copies separately from Proxmox guest archives.',
    [['nas', 'OMV NFS listener'], ['app_backup_mount', 'Backup mount source'], ['app_backup_job', 'App-data job result']], [
      command('Check the dedicated backup mount', vm, 'findmnt -T /mnt/omv/docker-host-backups', 'The path is the intended OMV backup export.', 'Do not rerun the job into an unmounted local directory.'),
      command('Read timer and job state', vm, 'systemctl status docker-host-app-data-backup.timer docker-host-app-data-backup.service --no-pager', 'The timer is scheduled and the last service result is understood.', 'A waiting timer does not prove the last backup succeeded.'),
      command('Read the first job error', vm, 'journalctl -u docker-host-app-data-backup.service --since "48 hours ago" --no-pager -n 100', 'Selected dumps and copies completed.', 'Separate dump, copy, permission, mount and heartbeat failures. Freshness alone is not restore proof.'),
    ], 'scripts/backup/backup_strategy.md'),
  route('monitoring', 'Monitoring and maintenance', 'Graphs or health monitors go blank',
    'Separate a failed service from a broken monitoring pipeline or blocked observer.',
    [['grafana', 'Grafana HTTP'], ['uptime_kuma', 'Kuma HTTP'], ['metrics_fresh', 'Recent metric timestamps']], [
      command('Test monitoring interfaces', pc, 'Test-NetConnection 192.168.60.10 -Port 3000; Test-NetConnection 192.168.60.10 -Port 3001', 'Both approved management listeners respond.', 'If both fail, check VM102 and access scope before editing dashboards.'),
      command('Read monitoring container state', 'VM 102 / monitoring', 'docker ps -a --format "table {{.Names}}\t{{.Status}}"', 'Grafana, Kuma and configured data services run.', 'A healthy app can look down when its observer or source firewall path fails.'),
      command('Compare timestamps and target', 'Grafana / Uptime Kuma UI', 'No command: inspect last sample time, time range, monitor target and exact error.', 'Metrics are recent and the observer uses an allowed source.', 'Old green graphs cannot establish current health. Keep InfluxDB private.'),
    ], 'scripts/setup/proxmox/monitoring_vm_setup_guide.md'),
  route('local-ai', 'Home and devices', 'Local AI fails or becomes very slow',
    'Separate CT114 reachability, model startup, GPU access and the chat frontend.',
    [['llamacpp', 'Chat endpoint'], ['ai_model', 'Model ready'], ['ai_capacity', 'Inference resources']], [
      command('Inspect inference and frontend', ai, 'docker compose -f /opt/stacks/local-ai/docker-compose.yml ps', 'The model and intended frontend are running.', 'A working Open WebUI page does not prove inference readiness.'),
      command('Read model startup errors', ai, 'docker logs --tail 80 llama-cpp', 'The configured model loaded and is listening without repeated GPU/allocation errors.', 'Preserve relevant redacted startup lines; do not change model files or GPU mappings during diagnosis.'),
      command('Check resource availability', ai, 'free -h; ls -l /dev/dri; docker stats --no-stream', 'Memory and expected render devices are available.', 'Compare CT configuration and shared-GPU consumers before changing permissions or context size.'),
    ], 'scripts/setup/proxmox/llm_host_setup_guide.md'),
  route('voice', 'Home and devices', 'Voice hears nothing or gives no reply',
    'Locate the failure between wake word, transcription, conversation and speech output.',
    [['ha_http', 'Home Assistant HTTPS'], ['voice_pipeline', 'Assist trace'], ['voice_services', 'Wyoming services']], [
      command('Locate the failed voice stage', 'Home Assistant / Assist pipeline debug', 'No command: inspect the latest trace and its first failed stage.', 'Wake word, transcription, conversation and output complete in order.', 'A transcript with no reply suggests conversation/output, not microphone reachability. Avoid repeated device actuation tests.'),
      command('Read voice-service state', ai, 'docker compose -f /opt/stacks/local-ai/docker-compose.yml ps', 'Configured Whisper, Piper and OpenWakeWord services run.', 'Match the failed stage to its service; the HA voice migration may still be pending.'),
      command('Inspect transcription errors', ai, 'docker logs --tail 60 wyoming-whisper', 'No repeated connection or model-loading errors for transcription.', 'For output/wake-word failures inspect the corresponding Piper/OpenWakeWord log. Redact household speech before sharing.'),
    ], 'scripts/setup/proxmox/llm_host_setup_guide.md'),
  route('automations', 'Home and devices', 'HA opens but an automation does nothing',
    'Distinguish trigger and condition failures from unavailable entities or integrations.',
    [['ha_http', 'Home Assistant HTTPS'], ['mqtt', 'MQTT TLS listener'], ['automation_trace', 'Trace and entities']], [
      command('Inspect the latest automation trace', 'Home Assistant / Settings / Automations', 'No command: note the last completed trigger, condition or action.', 'The trigger fired, conditions passed and entity IDs resolved.', 'No trace suggests a trigger or disabled automation; a stopped trace identifies the condition/action to inspect.'),
      command('Read entity state without changing it', 'Home Assistant / Developer tools / States', 'No command: inspect availability and last-updated time.', 'The affected entity has recent data.', 'An open MQTT port does not prove client authentication or topic delivery. Do not use Set state as a repair.'),
      command('Validate HA configuration', 'Home Assistant Terminal & SSH add-on', 'ha core check', 'Configuration validation passes.', 'Preserve named YAML/package errors. Do not manually trigger heaters, fans, plugs or safety automations as a shortcut.'),
    ]),
  route('notifications', 'Monitoring and maintenance', 'Expected notifications never arrive',
    'Separate the producing job, ntfy delivery and phone subscription without sending test messages.',
    [['docker_host', 'Docker host reachable'], ['notification_producer', 'Producer job outcome'], ['notification_delivery', 'Delivery response']], [
      command('Read the producer result', vm, 'docker logs --tail 80 watchtower', 'The monitor-only scan outcome and delivery response are visible.', 'A scan can succeed while delivery fails. September7 recorded error40014; establish whether it still applies.'),
      command('Read notification-service state', vm, 'docker compose -f /opt/stacks/ntfy/docker-compose.yml ps', 'ntfy is running.', 'Topic names, URLs and auth values may be private; share only redacted error evidence.'),
      command('Inspect the receiving subscription', 'Phone / ntfy app', 'No command: inspect server, subscription, notification permission and battery restrictions.', 'The intended subscription and permissions are present.', 'Do not loosen authentication or attachment policy. An actual test notification is a separate acceptance action.'),
    ], 'docs/install/services/ntfy.md'),
  route('updates', 'Monitoring and maintenance', 'Updates fail or package lists are old',
    'Check the approved package path and metadata age without installing or upgrading anything.',
    [['package_route', 'Approved package path'], ['package_metadata', 'Metadata timestamp'], ['package_cache', 'Cache listener']], [
      command('Read the configured APT proxy', 'Affected Debian guest', 'apt-config dump | grep -i proxy', 'Proxy configuration matches the approved cache design.', 'No output means no configured proxy. CT114 previously lacked a proxy and could not reach3142; verify current evidence.'),
      command('Read cached metadata age', 'Affected Debian guest', 'find /var/lib/apt/lists -maxdepth 1 -name "*InRelease" -printf "%TY-%Tm-%Td %TH:%TM %f\\n"', 'Metadata is recent enough to assess candidates.', 'Old candidate lists are not a current security assessment. Do not upgrade to diagnose connectivity.'),
      command('Read cache service state', vm, 'systemctl status apt-cacher-ng --no-pager', 'The intended cache service is active.', 'Separate service failure from guest-to-cache access. Repair the approved path during maintenance before refreshing metadata.'),
    ], 'docs/procedures/apt_cacher_ng_design.md'),
  route('photos', 'Applications and data', 'Immich uploads or thumbnails fail',
    'Separate the photo API, database, background jobs and NAS upload/library mount.',
    [['docker_host', 'Docker host reachable'], ['nas', 'OMV NFS listener'], ['immich_jobs', 'Upload and job outcome']], [
      command('Read Immich service state', vm, 'docker compose -f /opt/stacks/immich/docker-compose.yml ps', 'Required server and data services run.', 'Separate UI/API errors from database and machine-learning failures.'),
      command('Verify the media filesystem', vm, 'findmnt -T /mnt/omv/immich; df -h /mnt/omv/immich', 'The intended export is mounted with capacity.', 'Stop upload attempts if it falls back to root storage; do not move or delete originals.'),
      command('Inspect one failed upload or job', 'Immich administration UI', 'No command: read job failures and the exact error for one affected item.', 'Uploads and relevant background jobs complete.', 'A failed thumbnail is not proof of a lost original. Preserve originals, database and matching versions before recovery.'),
    ], 'docs/install/services/immich.md'),
  route('media', 'Applications and data', 'Media library is empty or playback fails',
    'Separate Jellyfin, Calibre-Web or Atsumeru from missing mounts and client playback issues.',
    [['nas', 'OMV NFS listener'], ['media_mount', 'Library mount source'], ['media_application', 'Library service']], [
      command('Check the shared media mount', vm, 'findmnt -T /mnt/omv/media; df -h /mnt/omv/media', 'The intended export is mounted and readable.', 'Do not rescan an empty fallback directory or move files between library roots.'),
      command('Inspect application state', vm, 'docker ps -a --format "table {{.Names}}\t{{.Status}}"', 'The selected media application runs.', 'Use its stack guide to distinguish database/config problems from missing media.'),
      command('Compare one known item and another client', 'Affected media UI', 'No command: test a known item and record the playback or scan error.', 'A known item is indexed and accessible to the intended account.', 'One failing client suggests codec/session trouble; an empty library for everyone suggests mount/path/permissions. Jellyfin media is intentionally read-only.'),
    ], 'configs/docker-host/stacks/jellyfin/README.md'),
  route('downloads', 'Applications and data', 'Downloads stall or the client disappears',
    'Check VPN containment, client state and staging storage without bypassing the tunnel.',
    [['download_vpn', 'VPN container health'], ['download_client', 'Download client'], ['download_storage', 'Staging mount']], [
      command('Read VPN and client state', vm, 'docker compose -f /opt/stacks/download-gateway/docker-compose.yml ps', 'VPN health is established before using the client.', 'The client may be deliberately contained when the tunnel fails. Do not move it to host networking.'),
      command('Read the recent tunnel error', vm, 'docker logs --tail 60 download-vpn', 'The intended provider tunnel is established.', 'Redact provider/account information. Do not bypass the kill switch.'),
      command('Inspect staging storage', vm, 'findmnt -T /mnt/omv/media; df -h /mnt/omv/media', 'The staging export is mounted with capacity.', 'Do not mount final libraries into the download client. Full staging requires reviewed cleanup, not broad deletion.'),
    ], 'configs/docker-host/stacks/download-gateway/README.md'),
  route('sync', 'Applications and data', 'Notes stop syncing or conflict',
    'Separate the local vault, sync transport and CouchDB without replacing canonical data.',
    [['docker_host', 'Docker host reachable'], ['sync_transport', 'Sync connection'], ['sync_conflicts', 'Vault conflict review']], [
      command('Preserve the local state first', 'Canonical Windows vault / Obsidian', 'No command: record affected files and last sync; preserve local edits before resolving conflicts.', 'The canonical K: vault and unsynced edits are identified.', 'Do not reset a database or overwrite a device to remove a warning.'),
      command('Read sync backend state', vm, 'docker compose -f /opt/stacks/obsidian-livesync/docker-compose.yml ps', 'The intended CouchDB backend runs.', 'This does not prove credentials, CORS, remote HTTPS or plugin settings.'),
      command('Inspect the plugin error', 'Obsidian / LiveSync status', 'No command: capture error category and affected documents without tokens or passwords.', 'The intended vault/database is selected and replication completes.', 'Git history and replication solve different problems. Reconcile conflicts deliberately; never bulk accept deletions.'),
    ], 'docs/install/services/obsidian-livesync.md'),
  route('household', 'Applications and data', 'An app opens but its data fails',
    'Investigate Mealie, Grocy, GardenKeeper, Household Hub and Recomp API/database boundaries.',
    [['docker_host', 'Docker host reachable'], ['household_api', 'Affected API response'], ['household_data', 'Database and saved data']], [
      command('Identify one failing operation', 'Affected app / browser developer tools', 'No command: record app, time, action, request path and HTTP status; exclude bodies, cookies and tokens.', 'The intended API responds for the signed-in account.', 'Static HTML does not prove API/auth/database health. Avoid repeatedly submitting writes.'),
      command('Read stack state', vm, 'docker ps -a --format "table {{.Names}}\t{{.Status}}"', 'The affected frontend and data services run.', 'Compare the service inventory. Do not rebuild Household Hub from its incomplete source mirror.'),
      command('Check shared data capacity', vm, 'df -h /opt; df -i /opt', 'The app data filesystem has capacity.', 'Before database repair or version change, identify its matching backup. Preserve data and avoid reseeding a live app.'),
    ], inventory),
  route('vault', 'Applications and data', 'Password vault login or sync fails',
    'Separate trusted HTTPS, client/account state and Vaultwarden without weakening access controls.',
    [['docker_host', 'Docker host reachable'], ['vault_tls', 'Trusted vault HTTPS'], ['vault_service', 'Vaultwarden state']], [
      command('Check trusted HTTPS', pc, 'curl.exe -I https://vault.home.local/', 'The canonical endpoint responds without a certificate bypass.', 'Do not enter credentials on an unexpected hostname or expose the raw backend.'),
      command('Read Vaultwarden state', vm, 'docker compose -f /opt/stacks/vaultwarden/docker-compose.yml ps', 'The service runs.', 'Preserve the account error separately from availability. Do not enable open signup or change admin tokens.'),
      command('Separate one client from a server-wide failure', 'Approved vault clients', 'No command: compare error categories with another already-authorized client.', 'The intended server and account are selected.', 'Do not sign out the last working client, delete its local vault or restore over the live database as a test.'),
    ], 'docs/install/services/vaultwarden.md'),
  route('ventsys', 'Home and devices', 'VentSys device or dashboard is offline',
    'Establish commissioning state before investigating telemetry; no actuation or safety acceptance.',
    [['ha_http', 'Home Assistant HTTPS'], ['mqtt', 'MQTT TLS listener'], ['ventsys_telemetry', 'Commissioned device telemetry']], [
      command('Establish commissioning state', 'Project record / device owner', 'No command: confirm this sensor/controller is installed and accepted.', 'Identity, power, network and role are known.', 'Hardware acceptance was pending in September. A planned device is not an unexpected live outage.'),
      command('Read device availability', 'Home Assistant / ESPHome integration', 'No command: inspect last update, availability and integration error.', 'A commissioned device has recent telemetry.', 'Separate Wi-Fi, authentication and entity names. Never put credentials into dashboard HTML.'),
      command('Stop before physical testing', 'Physical installation / acceptance procedure', 'No command: record missing evidence before any fan, valve, heater or plug action.', 'Safety and failsafe tests have a separate accepted procedure.', 'Green network checks cannot prove airflow, smoke response, power isolation or safe operation.'),
    ], 'docs/diagrams/ventsys/ventsys-control-and-safety-flow.mermaid'),
  route('phone-relay', 'Home and devices', 'Phone stream or recordings stop',
    'Separate phone publisher, MediaMTX relay, viewer and OMV recording storage.',
    [['docker_host', 'Docker host reachable'], ['phone_stream', 'Authenticated phone stream'], ['phone_recording', 'Recording mount and files']], [
      command('Read relay state', vm, 'docker compose -f /opt/stacks/mediamtx/docker-compose.yml ps', 'MediaMTX runs.', 'An idle relay may simply have no publisher. Real phone-session acceptance and retention remain separate gates.'),
      command('Inspect recent relay errors', vm, 'docker logs --tail 60 mediamtx', 'Expected publisher/reader connect without repeated auth/codec errors.', 'Redact authenticated URLs. Verify the HomeAdmin source and RTSP-over-TCP path; do not open new ports.'),
      command('Verify recording storage', vm, 'findmnt -T /mnt/omv/media; df -h /mnt/omv/media', 'OMV is mounted with capacity.', 'No automatic deletion was approved in the baseline. Do not delete recordings to diagnose a stream failure.'),
    ], 'docs/install/services/mediamtx.md'),
];
