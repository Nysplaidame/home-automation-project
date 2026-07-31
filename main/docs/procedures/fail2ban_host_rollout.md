---
title: Fail2ban Host Rollout
description: Standard jail policy and per-host deployment procedure for extending Fail2ban beyond docker-host and the Frigate CT
tags: [security, fail2ban, hardening, ids]
created: 2026-07-31
modified: 2026-07-31
type: procedure
status: active
---

# Fail2ban Host Rollout

This is the execution procedure for Phase A step 1 of
`docs/procedures/ids_ips_progression_plan.md`: extend the deployed docker-host
and Frigate CT baselines to the remaining Linux hosts with real authentication
surfaces.

## Standard policy

Every host uses the same window so bans are comparable across the estate:

| Setting | Value |
|---|---|
| `bantime` | `1h` |
| `findtime` | `10m` |
| `maxretry` | `5` |
| `backend` | `systemd` |
| `ignoreip` | loopback + Management VLAN 10, plus host-specific service peers |

Deviations must be written into the host's jail file as a comment explaining
why, not applied silently on the live host.

## Scope

| Host | Address | Jail source | State |
|---|---|---|---|
| docker-host (VM 103) | `192.168.20.102` | `configs/docker-host/system/docker-host-fail2ban-sshd.local` | Live |
| frigate-nvr (CT 111) | `192.168.30.20` | `configs/frigate/system/frigate-nvr-fail2ban-sshd.local` | Live |
| Proxmox host | `192.168.10.10` | `configs/proxmox/system/proxmox-fail2ban.local` | Source ready, not deployed |
| monitoring (VM 102) | `192.168.60.10` | `configs/grafana/system/monitoring-fail2ban-sshd.local` | Source ready, not deployed |
| llm-host (CT 114) | `192.168.20.104` | `configs/local-ai/system/llm-host-fail2ban-sshd.local` | Source ready, not deployed |
| OMV NAS | `192.168.40.50` | `configs/omv/system/omv-fail2ban-sshd.local` | Source ready, not deployed |

Deliberately out of scope:

- **Home Assistant OS (`192.168.20.101`)** — appliance OS. HA has its own
  `ip_ban_enabled` / login-attempt threshold in `http:`; do not install
  Fail2ban into HAOS.
- **OpenWrt router (`192.168.10.1`)** — no Fail2ban. Router-side blocking stays
  with its own firewall rules and selective deny logging.
- **Zyxel GS1900-8HP, cameras, ESP32 devices** — no general-purpose OS.

## Pre-flight per host

Run these read-only checks before writing anything. They decide two values that
differ per host and will break the jail if guessed:

```bash
command -v fail2ban-client || echo "fail2ban not installed"
command -v ufw && ufw status | head -1
nft list tables 2>/dev/null | head -3
journalctl -u ssh -n 3 --no-pager || journalctl -u sshd -n 3 --no-pager
```

- If `ufw` is installed and active, set `banaction = ufw` (docker-host and the
  Frigate CT baseline).
- If nftables is active without ufw, keep `banaction = nftables-multiport`.
- If neither, use `iptables-multiport`.
- If the sshd journal is empty or unavailable, switch that host to
  `backend = auto` with an explicit `logpath`.

Record the answers in the host's jail file comment block before deploying.

## Deployment

Do one host at a time, and keep a second authenticated session open on that
host until verification passes — a wrong `banaction` or `ignoreip` can lock the
admin path out.

```bash
apt-get update && apt-get install -y fail2ban
cp /etc/fail2ban/jail.d/<name>.local /root/<name>.local.pre-rollout-$(date -u +%Y%m%dT%H%M%SZ) 2>/dev/null || true
install -o root -g root -m 0644 <name>.local /etc/fail2ban/jail.d/<name>.local
fail2ban-client -t
systemctl enable --now fail2ban
```

`fail2ban-client -t` must pass before the service is started or reloaded. A
failed test means the jail file is wrong; fix the source file in the repository
rather than editing the live host.

## Verification

```bash
systemctl is-enabled fail2ban && systemctl is-active fail2ban
fail2ban-client status
fail2ban-client status sshd
```

Expected: the service is enabled and active, the jail list contains `sshd` (plus
`proxmox` on the Proxmox host), and the jail reports counters rather than an
error.

Then confirm the host's own service path still works — Proxmox backups to OMV,
HA backup writes, Frigate recording writes, or the monitoring scrape, depending
on the host. A jail that bans a service peer is worse than no jail.

## Rollback

```bash
rm -f /etc/fail2ban/jail.d/<name>.local
fail2ban-client unban --all
systemctl restart fail2ban   # or: systemctl disable --now fail2ban
```

`fail2ban-client unban --all` clears bans applied during the window. If the
admin path is already banned, use the Proxmox console for guests, or the
physical/IPMI console for the Proxmox host itself.

## Monitoring

`scripts/monitoring/export_fail2ban_to_influx.sh` already exports jail counters
to InfluxDB. It is per-host: deploy it alongside the jail, set `INFLUX_BUCKET`
to the bucket that owns that host's metrics, and set `JAILS` to the jail names
on that host (`JAILS="sshd proxmox"` on the Proxmox host).

The exporter tags only `jail`, so counters from several hosts writing the same
jail name into the same bucket would collide. Either give each host its own
bucket or extend the exporter with a `host` tag before the second host starts
exporting.

After deployment, add the host's Fail2ban service to Uptime Kuma or the health
check so a stopped Fail2ban is visible, and confirm the `Security Posture`
Grafana dashboard shows the new series.

## Exit criteria

- Every host in the scope table is either deployed and verified, or has a
  written reason for exclusion.
- Ban windows are identical across hosts, or the difference is documented.
- Counters from each host are visible in Grafana without tag collisions.
- `docs/procedures/ids_ips_progression_plan.md` current state and
  `docs/reference/current-live-state.md` are updated with the live result.
