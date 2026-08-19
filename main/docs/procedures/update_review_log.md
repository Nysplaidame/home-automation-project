---
title: Weekly Update Review Log
description: Execution log for weekly update-candidate review and post-check outcomes
tags: [operations, updates, maintenance, watchtower, docker-host]
created: 2026-05-28
modified: 2026-08-01
type: procedure
status: active
---

# Weekly Update Review Log

Use this log for recurring update-candidate review runs.

Current planning baseline:

- Treat OMV as live on VLAN 40 with Proxmox/HA/Immich storage paths active;
  the old md0 high-water warning is cleared by the 2026-07-05 Proxmox check
  showing `omv-backups` active at 54.21% used.
- Treat Frigate as live on CT 111 with one bench camera and HA integration;
  broader camera rollout, OMV recording cutover, and new-camera validation remain
  near-term follow-up when hardware arrives.
- Treat VentSys entities as unbuilt.

Do not log tasks here that assume full camera rollout, OMV recording cutover, or
VentSys hardware acceptance is complete unless baseline is explicitly updated
first.

## Entry template

```text
Date:
Operator:
Scope:
Maintenance window:

Host package candidates:
- ...

Container image candidates (Watchtower monitor-only):
- ...

Security-relevant items:
- ...

Actions taken:
- ...

Actions deferred:
- ...

Post-check:
- health_check result:
- key endpoint checks:

Follow-up window:
- ...
```

## 2026-05-28 — Initial weekly review baseline

Date:

- 2026-05-28

Operator:

- Codex session

Scope:

- docker-host only (`192.168.20.102`)

Maintenance window:

- review-only window; no package/container updates applied

Host package candidates:

- `containerd.io` upgradable (`2.2.3` -> `2.2.4`)
- `docker-buildx-plugin` upgradable (`0.33.0` -> `0.34.1`)
- `docker-ce-cli` upgradable (`29.4.3` -> `29.5.2`)
- `docker-ce-rootless-extras` upgradable (`29.4.3` -> `29.5.2`)
- `docker-ce` upgradable (`29.4.3` -> `29.5.2`)
- `docker-compose-plugin` upgradable (`5.1.3` -> `5.1.4`)
- `linux-image-cloud-amd64` upgradable (`6.12.90-1` -> `6.12.90-2`)

Container image candidates (Watchtower monitor-only):

- watchtower reported `Found new ghcr.io/maziggy/bambuddy:latest image`
- session summary: `Failed=0 Scanned=11 Updated=1 notify=no`

Security-relevant items:

- Docker engine/component upgrades available; schedule controlled patch window
- kernel metapackage upgrade available; requires reboot planning

Actions taken:

- collected `apt list --upgradable` snapshot
- reviewed watchtower logs and container health status

Actions deferred:

- all package upgrades deferred to planned patch window
- all container image refresh deferred to planned patch window

Post-check:

- health_check result: not run from this Windows session (shell compatibility)
- key endpoint checks: docker-host containers currently `Up`; watchtower `healthy`

Follow-up window:

- next scheduled patch window should include docker-host package upgrades and
  explicit restart/reboot validation plan

## 2026-05-29 — Docker-host metrics preflight and patch-window planning

Date:

- 2026-05-29

Operator:

- Codex session

Scope:

- docker-host metrics deployment
- monitoring VM Grafana/Influx integration
- router source/live drift check for docker-host-to-InfluxDB access

Maintenance window:

- metrics-only preflight; no host package upgrades or application image updates applied

Host package candidates:

- carry forward 2026-05-28 docker-host package candidates
- schedule a controlled docker-host patch window for Docker engine/component updates and kernel metapackage update

Container image candidates:

- no routine application image updates applied
- Telegraf image was transferred from monitoring VM via `docker save/load`, avoiding a new broad registry egress window

Security-relevant items:

- added narrow router allowance from docker-host `192.168.20.102` to monitoring VM `192.168.60.10:8086`
- created scoped InfluxDB bucket/token path for docker-host metrics
- kept Watchtower monitor-only posture unchanged

Actions taken:

- deployed docker-host Telegraf collector under `/opt/stacks/telegraf`
- created InfluxDB bucket `dockerhost`
- created Grafana datasource `InfluxDB - Docker Host`
- added Docker-host/container panels to `Proxmox Resource Overview`
- fixed `health_check.sh` Proxmox storage column parsing

Actions deferred:

- docker-host package upgrades deferred to planned patch window
- routine container updates deferred to planned patch window
- registry mirror remains parked until recurring image-pull friction justifies it

Post-check:

- router connectivity validation: `PASS=85 WARN=0 FAIL=0`
- `health_check.sh`: `11/11` checks passed after storage parsing fix
- docker-host `fail2ban` sshd jail: `0` failed, `0` banned
- docker-host Telegraf: running and writing `dockerhost` measurements

Follow-up window:

- perform docker-host package patching with
  `docs/procedures/docker_host_patch_window_runbook.md`, including explicit
  pre-checks, temporary update window, package upgrade, reboot if kernel
  changes, post-check validation, and closeout logging

## 2026-05-30 — Frigate Fail2ban hardening and patch runbook prep

Date:

- 2026-05-30

Operator:

- Codex session

Scope:

- docker-host patch-window runbook
- Frigate VM SSH hardening baseline

Maintenance window:

- Frigate package-install window; temporary router update rules opened and then removed

Host package candidates:

- docker-host package candidates remain deferred to the dedicated patch window
- Frigate installed `fail2ban` and dependencies

Container image candidates:

- no container images updated

Security-relevant items:

- added repo-side Frigate Fail2ban SSH jail template at
  `configs/frigate/system/frigate-nvr-fail2ban-sshd.local`
- installed and enabled Fail2ban on VM 101
- `sshd` jail active with `0` currently failed and `0` currently banned

Actions taken:

- added `docs/procedures/docker_host_patch_window_runbook.md`
- attempted Frigate install through `apt-cacher-ng`; the first package fetch failed while docker-host/cache had no useful upstream HTTP path
- opened temporary Frigate and docker-host update rules during troubleshooting
- copied cached Fail2ban package set from docker-host to Frigate as a fallback; install then completed successfully
- deployed `/etc/fail2ban/jail.d/frigate-nvr-sshd.local`
- removed temporary router update rules after install

Actions deferred:

- docker-host package upgrades remain deferred to the controlled patch window
- Frigate app/container start remains blocked by camera RTSP, HTTPS/SSL, and audio prerequisites

Post-check:

- Frigate `fail2ban` service: active
- Frigate `sshd` jail: active, `0` failed, `0` banned
- router temporary update rules: removed

Follow-up window:

- run docker-host patch window from `docs/procedures/docker_host_patch_window_runbook.md`
- investigate the staged-uplink/cache behavior before relying on `apt-cacher-ng` for future restricted-host installs

## 2026-07-06 — OMV backup proof and household app review

Date:

- 2026-07-06

Operator:

- Codex session

Scope:

- Proxmox `omv-backups`
- CT 111/114 LXC backup behavior
- docker-host household app health
- Frigate/OMV planning-baseline cleanup

Maintenance window:

- read-only checks plus one manual CT 114 backup proof; no package or container
  updates applied

Host package candidates:

- not checked in this review

Container image candidates:

- not checked in this review

Security-relevant items:

- no credentials were read, changed, or written to repo files
- Mealie/Grocy credential rotation remains an operator action in Bitwarden
- Obsidian LiveSync credentials and E2EE/setup passphrases remain Bitwarden-only

Actions taken:

- updated canonical docs so Frigate is first-camera baseline live with near-term
  camera rollout pending, not fully parked
- updated OMV/storage docs after Proxmox reported `omv-backups` active at
  54.21% used
- fixed Proxmox LXC backup job
  `a8c84d38-2a73-4d9d-bf34-111114000001` with `tmpdir=/var/tmp`
- proved CT 111 backup manually on 2026-07-05:
  `vzdump-lxc-111-2026_07_05-23_11_08.tar.zst` (`23G`)
- proved CT 114 backup manually on 2026-07-06:
  `vzdump-lxc-114-2026_07_06-00_13_59.tar.zst`, `15.30GB`,
  `00:23:30`, snapshot removed successfully
- documented Proxmox thin-pool warnings from the CT 114 proof as a monitoring
  note
- confirmed docker-host app health through Proxmox guest agent:
  Mealie `200`, Grocy `302`, Obsidian LiveSync/CouchDB `401`, root disk `62%`,
  Immich OMV mount present
- confirmed docker-host household app data source paths exist:
  Mealie `/opt/stacks/mealie/data` (`15M`), Grocy
  `/opt/stacks/grocy/config` (`4.2M`), and Obsidian LiveSync
  `/opt/stacks/obsidian-livesync/data` (`152K`); GardenKeeper local dumps also
  exist at `/opt/stacks/gardenkeeper/backups` (`36K`) with daily dumps through
  2026-07-06; no mounted `backups/docker-host` target was proven
- confirmed from Proxmox that OMV exports
  `/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host`
  to `192.168.20.102`
- added repo-side docker-host app-data backup script/service/timer templates

Actions deferred:

- Mealie admin credential replacement and Bitwarden storage
- Grocy admin credential replacement and household model setup
- Obsidian LiveSync client rollout to both devices
- docker-host `backups/docker-host` mount/job live installation and restore
  smoke for Mealie, Grocy, Obsidian LiveSync, and GardenKeeper dump copies
- docker-host package patch window from the existing runbook
- full NAS SMART/resource dashboard panels
- Frigate multi-camera rollout and OMV recording cutover until the new cameras
  arrive and are stable

Post-check:

- `git diff --check`: passed
- stale baseline search found no remaining active-doc claims that OMV/Frigate
  are unbuilt or that CT 114 backup still needs proof

Follow-up window:

- run the next docker-host patch window from
  `docs/procedures/docker_host_patch_window_runbook.md`
- after the next scheduled 04:00 LXC job, confirm the automatic CT 111/114 run
  also succeeds with `tmpdir=/var/tmp`

## 2026-07-07 — docker-host app-data backup install

Date:

- 2026-07-07

Operator:

- Codex session

Scope:

- OpenWrt docker-host-to-OMV NFS rule
- docker-host OMV backup mount
- docker-host app-data backup systemd timer
- Mealie, Grocy, Obsidian LiveSync, and GardenKeeper backup/restore smoke

Maintenance window:

- narrow storage-backup enablement; no package, container image, or app
  credential changes applied

Actions taken:

- added the live OpenWrt `Docker Host to OMV NFS` rule matching source intent:
  docker-host `192.168.20.102` to OMV `192.168.40.50` on NFS/RPC ports
  `111`, `2049`, `20048`, and `32765-32767`
- verified docker-host could reach OMV NFS after the rule was applied
- added docker-host fstab mount for
  `/mnt/omv/docker-host-backups` using NFSv3 with `_netdev`, `nofail`,
  `timeo=50`, and `retrans=2`
- mounted the OMV `backups/docker-host` export and wrote a test file
- installed `/usr/local/sbin/docker-host-app-data-backup.sh` plus
  `docker-host-app-data-backup.service` and `.timer`
- ran a dry-run and first real backup; real run `20260706T231304Z` wrote `20M`
  under `runs/` and updated `latest/`
- restore-smoked `latest/` into `/tmp`, verifying Mealie `mealie.db`, Grocy
  `grocy.db`, LiveSync shards, and a GardenKeeper compressed SQL dump
- enabled `docker-host-app-data-backup.timer`; next run scheduled daily at
  `03:45` local time

Post-check:

- `findmnt /mnt/omv/docker-host-backups`: mounted from OMV over NFSv3
- `systemctl is-enabled docker-host-app-data-backup.timer`: `enabled`
- `systemctl is-active docker-host-app-data-backup.timer`: `active`
- backup sizes: `latest` `20M`, run `20260706T231304Z` `20M`

Actions deferred:

- Mealie credential rotation is carried by the broader hardening roadmap, not a
  near-term app setup task
- Grocy pilot product workflow
- Obsidian LiveSync rollout to both client devices

## 2026-07-07 — Grocy seed and LiveSync client prep

Date:

- 2026-07-07

Operator:

- Codex session

Scope:

- Grocy household model seed
- Obsidian LiveSync backend/client-readiness checks
- Local Obsidian vault plugin install

Maintenance window:

- low-risk app setup; no package updates, container image updates, or service
  credential changes applied

Actions taken:

- removed Mealie credential rotation from the near-term docker-host app roadmap;
  it remains covered by the broader hardening roadmap
- created Grocy database checkpoint
  `/opt/stacks/grocy/config/data/grocy.db.pre-household-seed-20260707T125250Z`
- seeded Grocy locations: `Pantry`, `Fridge`, `Freezer`, `Cleaning`, and
  `Garage/Workshop`
- seeded Grocy quantity units: existing `Piece`/`Pack`, plus `each`, `box`,
  `bottle`, `jar`, `g`, `kg`, `ml`, and `L`
- seeded Grocy product groups: `Dry goods`, `Chilled`, `Frozen`, `Cleaning`,
  `Household consumables`, and `Printer/workshop consumables`
- verified Grocy still returns `HTTP/1.1 302 Found`
- verified LiveSync CouchDB `3.5.0`, database `home-automation-project`, and
  CORS preflight from `app://obsidian.md`
- installed and enabled Self-hosted LiveSync plugin `0.25.80` in the local root
  Obsidian vault without writing CouchDB credentials or plugin sync settings
- ran docker-host app-data backup again; run `20260707T125454Z` captured the
  seeded Grocy database

Post-check:

- Grocy model rows present in live SQLite database
- LiveSync database exists and is empty before first authoritative upload
- `OPTIONS` preflight to CouchDB returned `204 No Content`
- local admin laptop did not resolve `docker-host.tail7012a0.ts.net`; validate
  the Tailscale Serve HTTPS endpoint from a Tailscale-connected client

Actions deferred:

- Grocy pilot product purchase/consume/correction and expiry workflow
- LiveSync plugin wizard on the authoritative device
- LiveSync setup URI generation and second-device connection

## 2026-07-07 — Grocy voice shopping-list integration

Date:

- 2026-07-07

Operator:

- Codex session

Scope:

- Grocy API key for Home Assistant
- HA custom LLM tools for Grocy shopping-list add/list actions
- docker-host firewall persistence for HA-to-Grocy access

Maintenance window:

- low-risk app integration; HA config check and restart completed, no package or
  container image updates applied

Actions taken:

- created a dedicated Grocy API key named `home-assistant-voice`
- stored the live key in HA `/config/secrets.yaml` as `grocy_api_key` and on
  docker-host at `/root/grocy-home-assistant-voice-api-key.txt`
- deployed the repo `grocy_llm` Home Assistant custom integration and added
  `grocy_household` to the local LLM exposed API list
- limited voice tools to add/list Grocy shopping-list items only; purchase,
  consume, stock correction, completion, deletion, and inventory actions remain
  blocked pending a confirmation-gated design
- updated and installed `/usr/local/sbin/docker-host-firewall.sh` so HA
  `192.168.20.101` and HA Supervisor `172.30.32.0/23` can reach Grocy on
  `9283/tcp` before the docker-host `DOCKER-USER` drop
- verified HA could call the Grocy API, create a temporary product, add it to
  the shopping list, delete the product, and return the shopping list to empty
- ran docker-host app-data backup `20260707T132647Z`; latest backup size was
  `22M`

Post-check:

- `ha core check`: passed before and after restart
- HA logs showed no Grocy custom component errors
- docker-host `DOCKER-USER` rule order includes HA and HA Supervisor returns
  for `9283/tcp` before the Grocy drop

Actions deferred:

- manual spoken Assist validation from the user's normal voice device
- Grocy pilot product purchase/consume/correction and expiry workflow

## 2026-07-29 — Docker-host patch-window candidate refresh

Date:

- 2026-07-29

Operator:

- Codex session

Scope:

- read-only package/reboot review before choosing a maintenance window

Findings:

- Docker engine candidates: `containerd.io` `2.2.6`, Docker CE/CLI/rootless
  extras `29.6.2`, Buildx `0.35.0`, and Compose plugin `5.3.1`
- Debian candidates: Python 3.13 runtime/minimal packages at
  `3.13.5-2+deb13u4`
- Tailscale candidate: `1.98.10`
- running kernel: `6.12.96+deb13-cloud-amd64`
- `/var/run/reboot-required` is absent before the window

Actions taken:

- refreshed `docker_host_patch_window_runbook.md` with the current candidate
  set, working `docker-host-lan` SSH alias, OMV mount checks and the new
  Homepage/media endpoints
- no package or container update was applied

Actions deferred:

- choose an explicit date/time for the controlled window
- re-run `apt list --upgradable` immediately before execution
- execute package updates, reboot only if required, then run the expanded
  service, mount, firewall, Grafana and Kuma post-checks

## 2026-08-01 — Docker-host controlled package window

Date:

- 2026-08-01

Operator:

- Codex session

Scope:

- docker-host VM 103 package maintenance
- post-window Mullvad/Gluetun/qBittorrent activation and containment proof

Actions taken:

- created and verified pre-window NAS backup run `20260801T143119Z` (`41M`)
- upgraded 11 packages: Docker CE/CLI/rootless `29.7.1`, containerd `2.2.6`,
  Buildx `0.36.0`, Compose `5.3.1`, Python 3.13 packages
  `3.13.5-2+deb13u4`, and Tailscale `1.98.10`
- confirmed no reboot was required and no package remained upgradable
- installed the Mullvad WireGuard secret only in the mode-`0600` live file
- expanded the existing host-specific OpenWrt VPN egress rule with UDP `51820`
- started and configured qBittorrent, proved Mullvad identity and both
  interface-drop/full-provider-stop fail-closed behaviour
- created post-configuration backup run `20260801T144643Z` (`49M`) and passed
  an isolated qBittorrent config restore

Post-check:

- `dpkg --audit`: clean; simulated fix-broken operation: no changes
- Docker/containerd/Tailscale/Fail2ban/AdGuard coordinator and backup timer:
  active
- all 33 pre-existing containers remained running after package maintenance
- both OMV mounts present
- Homepage, AdGuard, Dozzle, Mealie, Grocy, Immich, Jellyfin, Calibre-Web,
  Atsumeru, Vaultwarden, Grafana and Uptime Kuma endpoint checks passed
- UFW and `DOCKER-USER` policies remained present; Fail2ban had no bans

Actions deferred:

- optional allow-listed Autobrr evaluation
- Vaultwarden owner onboarding after live DNS
- no package autoremove was performed

## 2026-08-01 - Gridfinity Layout Tool recovery

Actions taken:

- corrected the static Nginx redirect so `/designer` and `/baseplate` retain
  the public service port rather than redirecting to Docker-host's AdGuard
  listener on `:8080`
- updated the pinned static release from `gridfinity-layout-tool-v4.253.0` to
  `gridfinity-layout-tool-v4.342.0`; this includes upstream's geometry-worker
  timeout/error handling for the Bin and Baseplate infinite-spinner defect
- hardened the release updater's health probe to tolerate Nginx's short
  listener handover during an otherwise healthy container recreation

Post-check:

- `/healthz` returned `ok`
- direct and HTTPS-preview `/designer` and `/baseplate` redirects now stay on
  their original host and port
- browser checks rendered both the Baseplate and Bin Designer canvases with no
  visible loading state after the update
