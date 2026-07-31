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
| Proxmox host | `192.168.10.10` | `configs/proxmox/system/proxmox-fail2ban.local` | Live (`sshd` only, 2026-07-31); web-UI jail deferred |
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

## Lessons from the Proxmox host (2026-07-31)

Three findings that will repeat on the other hosts:

1. **Debian trixie ships no stock `proxmox` filter.** Do not assume a filter
   exists because upstream fail2ban has one. Check
   `ls /etc/fail2ban/filter.d/` during pre-flight and ship the filter with the
   jail when it is missing.
2. **Anchor failregex with `__prefix_line`, not the daemon name.** Under the
   systemd backend fail2ban sees `<hostname> <daemon>[<pid>]: <message>`. A
   regex anchored as `^daemon\[` silently matches zero lines and looks like
   "no attacks" rather than a broken filter. Always prove a new filter with
   `fail2ban-regex` against real failures before enabling the jail.
3. **`fail2ban-regex` "ignored" is not "dropped".** The sshd filter classified
   1252 benign disconnect lines as ignored with 0 matched. That is correct
   behaviour on a host with no real attacks, not a defect.

### Proxmox web UI — why its jail is deferred

The Proxmox UI is normally reached through the docker-host
`homepage-preview-proxy` (nginx). Consequences, both confirmed live:

- `pvedaemon` records every proxied login failure as
  `rhost=::ffff:192.168.20.102`, the proxy — never the real client. A jail on
  that signal bans the proxy and removes UI access for everyone, while an
  actual attacker stays invisible.
- The proxy's own access log does see real client IPs, but Proxmox returns
  HTTP `200` for both failed and successful `POST /api2/extjs/access/ticket`
  requests. Only the response body size differs (77 bytes failed, ~782 bytes
  succeeded). A jail keyed on body size is a brittle heuristic, not a control.

Adding `192.168.20.102` to `ignoreip` is explicitly rejected — it makes the jail
blind to every proxied login while appearing to be protection.

### Resolution (2026-07-31)

This was initially framed as a trade-off against Homepage convenience. It was
not one. Homepage's Proxmox tile `href` in `services.yaml` already points
directly at `https://192.168.10.10:8006/`, and its `siteMonitor` health check on
proxy port `8299` performs unauthenticated GETs that never generate
`authentication failure` lines. Only the browser TLS listener on `8183` masked
client addresses.

The `8183` server block was therefore removed from the docker-host
`homepage-preview-proxy` and the container restarted. Verified after the change:
`8183` refuses connections, while `8180`, `8184`, `8186`, `8187`, `8188` and the
`8299` health check all still respond. Live rollback copy:
`/opt/stacks/homepage/preview-proxy/nginx.conf.pre-8183-removal-20260731T192248Z`.

Known consequence: Homepage's embedded iframe *preview* of Proxmox is gone,
because the `8183` block carried its `frame-ancestors` CSP. The tile link still
opens Proxmox directly. There is no configuration that keeps the embedded
preview and still exposes real client IPs — an iframe on `:8183` is a separate
origin and would require its own login through the proxy.

Remaining gate before enabling the `[proxmox]` jail: confirm a direct login at
`https://192.168.10.10:8006` works, then confirm a deliberate failure logs
`rhost=` as the real client rather than `192.168.20.102`. Only then enable the
jail. Note that direct access presents Proxmox's own certificate; signing it
with the local `Home Local CA` would remove the browser warning.

The proxy configuration was previously untracked. It is now mirrored at
`configs/docker-host/stacks/homepage/preview-proxy/`.

## Exit criteria

- Every host in the scope table is either deployed and verified, or has a
  written reason for exclusion.
- Ban windows are identical across hosts, or the difference is documented.
- Counters from each host are visible in Grafana without tag collisions.
- `docs/procedures/ids_ips_progression_plan.md` current state and
  `docs/reference/current-live-state.md` are updated with the live result.
