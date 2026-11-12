# Monitoring VM network access audit — November10 2026

Read-only endpoint probes from VM102 (`192.168.60.10`), compared with VM103, router UCI/nft rules, destination listeners/firewalls, service matrix and Kuma database. TCP reachability is not application acceptance. Initial audit was read-only; owner-authorized remediation is recorded below.

## Confirmed missing router permissions

| Endpoint | Assessment |
|---|---|
| HA MQTT TLS `192.168.20.101:8883` | Appropriate for broker/device health and discovery capture; blocked at router, reachable from VM103. Use a source/host/port scoped allowance and restricted MQTT identity. |
| ntfy HTTPS `192.168.20.102:8193` | Current approved HTTPS path blocked; existing Kuma uses raw8085 and remains reachable. Host HTTPS policy must also permit VM102. |
| Homepage HTTPS `192.168.20.102:443` | Current monitoring only checks HTTP3001, so it cannot certify HTTPS proxy/TLS health. Router and host UFW lack this path. A scoped HTTPS health check is appropriate. |
| Household Hub `192.168.20.102:8100` | Host policy already permits VM102, router does not. Appropriate application health check; no Kuma monitor currently configured. |
| Jellyfin8096, Calibre-Web8083, Atsumeru31337, qBittorrent8084 on VM103 | Host policy/service matrix already includes monitoring; router omitted all four. Reachable on VM103, refused from VM102. No Kuma monitors currently configured. |

The router's older general monitoring-to-automation allowlist has not kept up with these service additions. Destination host allowances alone do not grant routed reachability. Add narrowly scoped rules rather than expanding all monitoring-VLAN access to whole zones.

## Require deliberate monitoring design

- Mermaid8092, Gridfinity8093, Recomp8420 and troubleshooting8094 are blocked at router and intentionally restricted by destination host policy. Prefer dedicated health endpoints or host-published health, rather than exposing app contents to monitoring implicitly.
- Router web80 and Frigate HTTPS8971 are blocked; existing router DNS/Proxmox/Frigate API checks pass. UI checks would be additional coverage, not a current required path.
- AI embeddings8082 is deliberately source-scoped to VM103. Monitoring can reach llama8081, Open WebUI3002 and all three voice ports. Add a scoped embeddings health check only with an intended monitoring role.
- E2 native6053 and printer MQTT8883 are not allowed from monitoring. Device health can already be observed through HA/Bambuddy; direct API probes would need explicit scoped rules/credentials. Whole IoT/printer access is unnecessary.
- Transfer Portal8088 on OMV failed from both VM102 and VM103, and no listener was present. Do not classify this as merely a missing monitoring firewall rule or enable a parked service just to satisfy a check.

## Existing paths verified

VM102 can reach router DNS53, Proxmox8006, HA8123/SSH22, HomepageHTTP3001, OMVweb80/NFS2049, FrigateAPI5000, AIchat8081/WebUI3002/voice10200-10400. Existing active Kuma latest statuses were healthy except the three intentionally disconnected cameras and the SMART heartbeat below. Newer application endpoints above are absent from Kuma's configured checks, so old green monitors do not cover them.

## Repaired OMV SMART heartbeat regression

Kuma34 was down with missing heartbeats; OMV's sender timed out. Router OMV-to-Kuma3001 rule was present. VM102 DOCKER-USER lacked OMV's allowance because `monitoring-docker-firewall.sh` flushes/rebuilds the chain and could erase the separate augmentation script's rule.

Added the existing intended OMV `192.168.40.50` to VM1023001 allowance to the full rebuild source (`configs/grafana/system/monitoring-docker-firewall.sh`) and ordered the augmentation service after that rebuild service. Deployed both, restored the rule, and verified it survived restarting both firewall units. OMV sender exited0, Kuma34 recovered at08:22:55UTC with all five physical disks healthy. Backups on VM102: `/root/monitoring-docker-firewall.before-20261110` and `/root/monitoring-firewall.before-20261110.service`.

This does not claim every other OMV unit is healthy: unrelated failed fan-control, quota and historical storage-job units were observed and not changed in this network audit.

## Remediation — November10, 08:31UTC

Owner authorized closing the confirmed network gaps and relocating both monitors.
Router rules now allow only VM102 to HA TCP8883 and VM103 TCP443/8193/8100/
8096/8083/31337/8084. Canonical source updated; router lint and `fw4 check`
passed. Applied narrow named UCI rules without deploying unrelated network
settings; committed and reloaded firewall. Router rollback checkpoint:
`/root/firewall-before-monitoring-20261110`.

VM103 host UFW now allows VM102 to its exact IP on TCP443/8193. Persistent
source: `configs/docker-host/system/docker-host-monitoring-access.sh`. Other
confirmed endpoints already had destination-host allowances. All eight newly
allowed paths passed VM102 TCP checks; MQTT TLS, HA API and ntfy HTTPS passed
application checks. Optional policy-restricted endpoints above were left scoped
as documented. To roll back only this access change, delete the two named UCI
rules `monitor_mqtt_tls`/`monitor_current_services`, commit/reload firewall,
and delete the two matching source/destination UFW rules; preserve later changes.

Identity checks and temporary MQTT capture now run on VM102; tests, enabled
service, both streams and no active incidents verified. State/history transferred
over SSH. Removed dedicated VM103 service, account, program, credentials/key,
state/logs and its solely introduced Paho dependency; revoked old HA SSH key.
Shared PyYAML remains because cloud-init/netplan require it. Desktop copies
remain stopped/paused. Details and temporary capture rollback are in the monitor
procedure.

Kuma checks for newer services are a remaining coverage task; network access
alone does not create those checks. Owner separately requested adding Kuma
metrics/status to Homepage's home page to the task list.

