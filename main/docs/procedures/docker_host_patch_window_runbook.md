---
title: Docker Host Patch Window Runbook
description: Command-by-command patch window for VM 103 docker-host package and container updates
tags: [operations, updates, docker-host, maintenance, runbook]
created: 2026-05-30
modified: 2026-05-30
type: procedure
status: active
---

# Docker Host Patch Window Runbook

Use this runbook for the next controlled docker-host patch window. It assumes
docker-host is live at `192.168.20.102`, but it does not assume OMV, Frigate app
state, cameras, or VentSys hardware are live.

## Scope

Current package candidates from `docs/procedures/update_review_log.md`:

- `containerd.io`
- `docker-buildx-plugin`
- `docker-ce-cli`
- `docker-ce-rootless-extras`
- `docker-ce`
- `docker-compose-plugin`
- `linux-image-cloud-amd64`

Watchtower monitor-only also reported a newer `ghcr.io/maziggy/bambuddy:latest`
image. Treat that as a candidate, not automatic approval.

## Preconditions

Run from the management laptop unless a line says otherwise.

1. Confirm the repo is clean:

   ```powershell
   git status --short --branch
   ```

2. Confirm core services are reachable:

   ```powershell
   Test-NetConnection 192.168.20.102 -Port 22
   Test-NetConnection 192.168.20.102 -Port 8000
   Test-NetConnection 192.168.20.102 -Port 8080
   Test-NetConnection 192.168.20.102 -Port 3001
   Test-NetConnection 192.168.20.102 -Port 8081
   ```

3. Confirm router access is available for a temporary update rule:

   ```powershell
   ssh -i E:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 'uci show firewall | grep "Docker Host"'
   ```

4. Record a quick package/container baseline:

   ```powershell
   ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 'hostname; uptime; df -h /; docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"; fail2ban-client status sshd'
   ```

## Open The Temporary Update Window

Run on the router:

```powershell
ssh -i E:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 @'
uci add firewall rule
uci set firewall.@rule[-1].name='TEMP Docker Host Update Access'
uci set firewall.@rule[-1].src='automation'
uci set firewall.@rule[-1].src_ip='192.168.20.102'
uci set firewall.@rule[-1].dest='wan'
uci set firewall.@rule[-1].dest_port='80 443'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall restart
'@
```

Verify from docker-host:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 'apt-get update'
```

## Patch Host Packages

Run on docker-host:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 @'
set -eu
apt list --upgradable
apt-get upgrade -y containerd.io docker-buildx-plugin docker-ce-cli docker-ce-rootless-extras docker-ce docker-compose-plugin linux-image-cloud-amd64
docker version
docker compose version
'@
```

If `apt-get upgrade` proposes extra packages, stop and record them in
`docs/procedures/update_review_log.md` before continuing.

If a kernel package changed, reboot docker-host:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 'systemctl reboot'
```

Wait for SSH to return:

```powershell
do {
  Start-Sleep -Seconds 5
  Test-NetConnection 192.168.20.102 -Port 22
} until ($?)
```

## Optional Container Refresh

Do not refresh every image by habit. For this window, Bambuddy is the only known
candidate from Watchtower.

Run on docker-host:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 @'
set -eu
cd /opt/stacks/bambuddy
docker compose pull
docker compose up -d
docker compose ps
'@
```

If the pull fails because registry access is blocked or unreliable, defer it and
close the update window. Do not add broad permanent registry access.

## Close The Temporary Update Window

Run on the router:

```powershell
ssh -i E:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 @'
for section in $(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)=rule$/\1/p"); do
    [ "$(uci -q get ${section}.name)" = "TEMP Docker Host Update Access" ] && uci delete "${section}"
done
uci commit firewall
/etc/init.d/firewall restart
'@
```

Verify the temporary rule is gone:

```powershell
ssh -i E:\home-automation-project\main\tools\router-deploy\keys\router_deploy root@192.168.10.1 'uci show firewall | grep "TEMP Docker Host Update Access" || true'
```

## Post-Checks

Run from the management laptop:

```powershell
Test-NetConnection 192.168.20.102 -Port 22
Test-NetConnection 192.168.20.102 -Port 8000
Test-NetConnection 192.168.20.102 -Port 8080
Test-NetConnection 192.168.20.102 -Port 3001
Test-NetConnection 192.168.20.102 -Port 8081
```

Run on docker-host:

```powershell
ssh -i $env:USERPROFILE\.ssh\proxmox_admin_ed25519 root@192.168.20.102 @'
set -eu
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
systemctl is-active fail2ban
fail2ban-client status sshd
apt list --upgradable
'@
```

Run the project health check from a Linux-capable host if available:

```sh
E:/home-automation-project/main/scripts/monitoring/health_check.sh --json
```

If running from Windows only, use the endpoint checks above plus Uptime Kuma and
Grafana direct UI checks.

## Documentation Closeout

Append a new dated entry to `docs/procedures/update_review_log.md` with:

- packages upgraded,
- containers refreshed or deferred,
- whether docker-host rebooted,
- post-check results,
- remaining update candidates,
- and any follow-up maintenance window.

Update `main/HANDOFF-2026-05-28-preflight-next.md` if the live baseline changed
materially.
