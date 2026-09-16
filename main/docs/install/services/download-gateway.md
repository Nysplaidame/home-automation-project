---
title: Download Gateway Operations
description: Source-backed installation, diagnosis, backup and recovery for Gluetun and qBittorrent
tags: [install, downloads, vpn, recovery]
created: 2026-09-10
modified: 2026-09-10
type: install-guide
status: active
---

# Download Gateway Operations

The [tracked Compose](../../../configs/docker-host/stacks/download-gateway/docker-compose.yml)
runs Gluetun as container `download-vpn` and qBittorrent in Gluetun's network
namespace on VM 103. The [stack record](../../../configs/docker-host/stacks/download-gateway/README.md)
contains the August acceptance evidence. This manual describes that contract;
it does not establish a fresh tunnel, restore or failure-test result.

Diagrams: [access](../../diagrams/network/security-access-flow.mermaid),
[service placement](../../diagrams/infrastructure/docker-host-service-placement.mermaid),
[storage](../../diagrams/storage/storage-and-backup-flow.mermaid).

## Prerequisites and inputs

- Complete docker-host and OMV installation. Verify `/mnt/omv/media` is the
  intended OMV NFS export before creating or starting a writer.
- Retain only the explicit `10.240.20.0/24` bridge and source-scoped UI port
  `8084`. qBittorrent has no independently published port or Docker network.
- Copy the tracked directory to `/opt/stacks/download-gateway/`. Prepare a
  mode-`0600` `.env` from its `.env.example` outside Git.
- Set `MEDIA_UID`/`MEDIA_GID` to the actual OMV media-service identity. Set
  `WIREGUARD_PRIVATE_KEY` and `WIREGUARD_ADDRESSES` from the owner's approved
  Mullvad WireGuard configuration, and `SERVER_CITIES` to the approved filter.
  The account's public device key is not the private key. Do not print `.env`
  or expanded Compose output into reports.
- Preserve `/opt/stacks/download-gateway/qbittorrent-config` and `gluetun`
  when recovering. The WebUI credential is recorded in Windows Credential
  Manager as `home-automation/qbittorrent`; do not reset it as a first step.

The only payload mount is `/mnt/omv/media/incoming/qbittorrent:/downloads`.
Incomplete and complete paths are `/downloads/incomplete` and
`/downloads/complete`. The container must not see quarantine, final libraries,
Immich originals or backups. Promotion is a separate reviewed host-side action.

## Prepare, validate and start

Run on: docker-host shell in the prepared stack directory.

```sh
cd /opt/stacks/download-gateway || exit 1
findmnt -T /mnt/omv/media
test -f .env && stat -c '%a %n' .env
docker compose config --quiet
docker compose config --images
```

Expected: the mount source is the documented OMV export (not a local root
filesystem), `.env` reports `600`, and Compose validation succeeds with the
reviewed image digests. Review `/dev/net/tun`, declared mount directories,
host firewall and the [version policy](../reference/version-policy.md).

Last safe stop: leave both services down before household clients, real jobs or
schedules depend on the candidate. Use the approved image-pull maintenance
window; do not leave broad host egress enabled for updates.

Run on: docker-host shell after those prerequisites are satisfied.

```sh
cd /opt/stacks/download-gateway || exit 1
docker compose up -d gluetun
docker compose ps
docker compose logs --tail=60 gluetun
```

Expected: Gluetun reaches healthy. Inspect logs locally and redact identifiers
or sensitive connection details before sharing. A healthy container alone is
not proof of the downloader's egress path.

Run on: docker-host shell after Gluetun is healthy.

```sh
docker compose up -d qbittorrent
docker compose ps
curl -I http://127.0.0.1:8084/
docker inspect qbittorrent --format '{{.HostConfig.NetworkMode}}'
docker inspect download-vpn --format '{{.Id}}'
```

Expected: both services run, the UI responds, and qBittorrent's
`container:<id>` network mode names the current `download-vpn` container ID.
Complete a trusted WebUI login and inspect both configured download paths.
Homepage uses its existing `/portal-preview/qbittorrent/` route. UI success
does not establish VPN identity or failure containment.

## Tunnel acceptance and diagnosis

Before enabling jobs, repeat the established provider-identity check from the
downloader namespace and record the method/time without logging account
secrets. A provider lookup from VM 103 itself tests host egress instead.
Use the [household plan](../../procedures/household-services-implementation-plan.md)
for the separately controlled tunnel-loss test. Keep actual payload jobs paused
during a test and distinguish tunnel loss from a stopped UI.

| Symptom | Diagnose | Recovery |
|---|---|---|
| Gluetun never becomes healthy | Service logs, actual WireGuard inputs, time, approved relay filter and host route | Correct the identified input; do not disable Gluetun's firewall |
| UI works but downloads cannot connect | Current provider identity, tracker/job errors and namespace identity | Establish which layer failed before changing ports or paths |
| Failure after Gluetun replacement | Compare qBittorrent NetworkMode ID with current VPN container | Recreate qBittorrent after the provider is healthy |
| Permission denied or unexpected free space | OMV mount source, selected download subtree and media UID/GID | Stop downloader writes; repair the exact mount/ownership issue |
| Direct UI works, Homepage fails | Fixed proxy path, forwarding configuration and access scope | Diagnose the existing proxy; do not publish a new listener |

Run on: docker-host shell after Gluetun replacement and healthy validation.

```sh
cd /opt/stacks/download-gateway || exit 1
docker compose up -d --force-recreate qbittorrent
docker compose ps
```

Expected: qBittorrent attaches to the new provider namespace. Repeat the
namespace-ID, login and tunnel checks. Do not switch it to host networking.

## Backup and isolated restore

The application backup job copies `qbittorrent-config` into its `qbittorrent`
generation. It does not capture the live VPN `.env`, all Gluetun state or
the payload tree. Keep recoverable VPN configuration in the approved protected
credential store, and explicitly decide how payloads are preserved or resumed.

For a consistent pre-update checkpoint, pause jobs, stop qBittorrent, and copy
its complete config directory to a new protected off-host generation. Save the
matching Compose/image references and protected provider configuration through
their separate backup paths. A raw directory copy while the client is writing
is not the same checkpoint.

Run on: docker-host shell during the selected maintenance window.

```sh
cd /opt/stacks/download-gateway || exit 1
docker compose stop qbittorrent
docker compose ps --all
```

Expected: the client is stopped before copying its state. After the checkpoint,
resume only when the mount and Gluetun health are still valid.

An isolated restore must use unique names/network, an unused loopback UI port,
copied configuration and a disposable payload directory. Strip real jobs from
the test copy or keep its network denied; do not allow a restore rehearsal to
resume production downloads. Check saved authentication and configured paths
without mounting writable production payloads. The production Compose's fixed
container names require deliberate edits; a different project name alone is
insufficient isolation. Record configuration-restore proof separately from
tunnel-identity/failure-containment proof.

## Updates and rollback

Record both old image digests and the consistent data checkpoint first. Review
upstream migration notes through the version policy. Change one candidate
stack, validate, then recreate Gluetun and qBittorrent in that order when the
provider is replaced. Recheck namespace identity, login, paths, provider
identity and the controlled failure test before restoring job reliance.

If the candidate fails, stop the downloader and restore the matching old images
and config checkpoint. Do not combine old binaries with migrated client state
without compatibility evidence. Reattach the client to the restored provider
namespace and repeat the original checks. The August successful restore and
failure tests are historical evidence, not acceptance of a newly rebuilt stack.
