---
title: CT114 package-path repair
description: Confirmed October 2 blockers and a host-scoped maintenance change
created: 2026-10-02
modified: 2026-10-04
type: procedure
status: prepared
---

# CT114 package-path repair

## Verified diagnosis — October 2, 10:48 BST

Read-only SSH through `llm-host-lan`, `docker-host-lan` and
`home-router-lan` confirms:

- CT114 is Debian 13 on `192.168.20.104`, with no APT proxy. Its default route
  is `192.168.20.1`; `.102` is on the same directly attached `/24`.
- Debian/update/security repositories use signed HTTP metadata. Security and
  updates indexes are dated June19 and expired June26. The displayed 56
  upgrade candidates come from that old cache and are not a current update list.
- Fail2ban is **not installed**, rather than an installed inactive service.
  `dpkg --audit` is clean; no reboot-required marker exists before maintenance.
- docker-host's native apt-cacher-ng service is enabled/active on TCP3142.
  Its report page returns 200 over loopback; CT114's attempt returns no HTTP
  response. docker-host kernel logs directly record UFW blocking CT114 SYNs
  to `.102:3142`. Existing input allows name only Frigate and monitoring.
- The cache's loopback Debian InRelease request returns 503, and docker-host's
  direct Debian HTTP probe returns no response. Fixing client access alone
  therefore does not establish an upstream package path. Temporary cache-host
  maintenance egress must be verified separately; the exact upstream failure
  is not certified from the HTTP status alone.
- Direct CT114 Debian HTTP/HTTPS probes return no response, while public name
  resolution succeeds. Do not replace the update gate with broad permanent WAN.
- All seven current local-AI containers remain running, including healthy
  llama.cpp, embeddings and Open WebUI containers. No live change was applied.

## Prepared source

October4 read-only refresh: Fail2ban remains not installed and no HTTP APT proxy
is configured. The CT114 cache request still times out (HTTP000/exit28), while
apt-cacher-ng is active and its loopback Debian trixie InRelease request still
returns503. No firewall/proxy/package/service change was made. This confirms
the client/upstream blockers remain; it does not independently diagnose today's
firewall drop. Cached InRelease headers still include June19 indexes with
June26 expiry (plus the older May16 main index), so no current signed metadata
or current upgrade list is certified.

- [Host-only UFW helper](../../configs/docker-host/system/docker-host-ufw-apt-llm.sh)
  previews by default. `--apply` adds only `.104 -> .102 TCP3142` native input.
  It does not flush/reload rules, widen a subnet, edit Docker routing or restart
  any service. UFW de-duplicates an already equivalent rule.
- [CT114 proxy template](../../configs/local-ai/system/llm-host-apt-proxy.conf)
  selects the cache for HTTP and explicitly keeps HTTPS direct. Current Debian
  sources are HTTP; any future HTTPS repository needs its own maintenance path.
- [Existing Fail2ban jail](../../configs/local-ai/system/llm-host-fail2ban-sshd.local)
  retains the previously reviewed systemd backend and UFW action.

## Maintenance gate and order

This prepared change does not authorize live firewall edits, package install,
service enablement or restart. Follow the [maintenance playbook](update_maintenance_playbook.md)
and [hardening boundary](hardening-resilience-planning-runbook.md) with a named
window, verified management access, checkpoint and rollback. Package installs
can trigger systemd activation; installing Fail2ban is not merely file staging.

1. Record CT114 guest/app backup freshness, source/proxy files, existing UFW
   state and matching cache-host temporary WAN rule state. Verify a Proxmox
   console recovery route and retain current SSH sessions. Do not reuse VM104.
2. Preview the helper on docker-host with `sh docker-host-ufw-apt-llm.sh`.
   Review that it names only the two expected hosts and TCP3142. Then apply
   `sh docker-host-ufw-apt-llm.sh --apply` in the approved window.
3. Place the proxy template as root-owned mode0644
   `/etc/apt/apt.conf.d/01proxy` on CT114, retaining any prior file separately.
   Do not overwrite a subsequently created proxy without inspecting it.
4. Enable the existing host-scoped temporary **docker-host** update egress
   through the reviewed playbook. Verify a Debian InRelease request through
   cache loopback returns 200, then verify the same path from CT114. Stop on
   failure; do not disable signature/expiry validation, switch off firewalls
   or open general CT114 WAN to mask the problem.
5. On CT114 run `apt-get -o APT::Update::Error-Mode=any update`. Verify all
   configured signed repositories refreshed and dates/expiry are current.
   Re-list candidates and simulate `apt-get -s install fail2ban`. Review changed
   packages, removals and service implications before installing anything.
   Do not combine the Fail2ban baseline with a blind full upgrade.
6. Install/deploy the reviewed jail only after the simulation passes; validate
   `fail2ban-client -t`, existing SSH access and console recovery before
   enabling/restarting its service. Confirm `fail2ban-client status sshd`,
   `systemctl is-active fail2ban` and effective UFW state afterward. This does
   not authorize a deliberate ban of the current management client.
7. Remove temporary cache-host WAN access and verify it is closed. Recheck
   SSH, all seven AI containers, llama.cpp `/v1/models`, Open WebUI, and the
   existing HA voice-service listeners. Record exact executed changes and
   freshness/rollback evidence in the update review log and live inventory.

## Rollback

Restore the exact pre-change proxy file (or remove only the newly introduced
file if none existed). Remove only the new UFW rule if this window created it:

```sh
ufw delete allow in from 192.168.20.104 to 192.168.20.102 port 3142 proto tcp
```

Keep any previously existing equivalent rule. Always restore the temporary
router egress rule to its captured state. Retain the previous Fail2ban jail
and service enablement state; if enabling it breaks SSH, use the held console
to stop the new jail/service and restore that state. Package rollback requires
the reviewed simulation/checkpoint plan; do not purge or downgrade blindly.

## Verification of prepared source

The helper's isolated Linux tests substitute a fake UFW executable. They check
default dry-run, explicit application, fixed host/port scope, and rejection of
unknown/extra arguments without a UFW call. These tests do not apply firewall
rules or certify an operational package refresh.
