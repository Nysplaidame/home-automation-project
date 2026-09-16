---
title: Local Registry Mirror Install Manual
description: TLS, quota, client-canary, and rollback-gated Docker Hub pull-through cache
tags: [install, docker-host, registry, tier3]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Local Registry Mirror Install Manual

## Purpose

Evaluate a Docker Hub pull-through cache only if measurements show repeated
pulls justify its storage and operational cost. Cache blobs are disposable; the
TLS/configuration and client rollback path are the durable parts. The default
decision is **parked**.

## Runs on

- docker-host over SSH for the mirror;
- one approved Debian Docker client for canary configuration;
- router/DNS and certificate workflow for the internal trusted endpoint.

## Mandatory gate

Record:

- measured pull-volume/latency benefit and client list;
- immutable `registry:3` image digest;
- DNS `registry-mirror.home.local`, host port `5001`, trusted local-CA TLS;
- source-scoped firewall rules; no public/Tailscale exposure by default;
- quota-enforced cache filesystem/path, warning threshold, hard ceiling, and
  owner for cleanup;
- seven-day cache TTL, deletion enabled, and no upstream Docker Hub credentials;
- each client's complete `daemon.json` backup, syntax validation, maintenance
  restart, canary pull, and direct-upstream rollback;
- config/certificate backup; cache blobs explicitly excluded from backup.

Do not add the mirror under Docker's `insecure-registries`. Do not configure a
private Docker Hub account: a credentialed pull-through cache can make private
content available to every mirror client unless separately authenticated.

## Inputs

No application secret is required for an anonymous public-image cache. The
local-CA private key remains in the existing certificate workflow and is never
copied into the container or repository.

## 1. Prepare quota/TLS and pin the image

Issue a server certificate for `registry-mirror.home.local` using the approved
local CA. Install only its certificate/key at `certs/tls.crt` and
`certs/tls.key`; clients trust the CA certificate, not the server private key.

Run on: docker-host over SSH after the gate, DNS, quota path, and certificate are approved.

```bash
install -d -m 0750 /opt/stacks/registry-mirror/{config,data,certs}
cd /opt/stacks/registry-mirror
test -s certs/tls.crt
test -s certs/tls.key
chmod 0644 certs/tls.crt
chmod 0600 certs/tls.key
openssl x509 -in certs/tls.crt -noout -subject -issuer -dates -ext subjectAltName
findmnt -T data
df -hT data
docker pull registry:3
registry_image="$(docker image inspect registry:3 --format '{{index .RepoDigests 0}}')"
test -n "$registry_image"
printf 'REGISTRY_IMAGE=%s\n' "$registry_image" >.env
chmod 0600 .env
printf '%s\n' "$registry_image"
```

Expected result: certificate SAN contains the exact mirror name and is current;
`data` resolves to the approved quota-controlled filesystem with safe capacity;
and an immutable image digest prints. Stop if quota enforcement is only an
unimplemented intention.

## 2. Create a loopback-only pull-through cache

Run on: docker-host over SSH.

```bash
cd /opt/stacks/registry-mirror
cat >config/config.yml <<'YAML'
version: 0.1
log:
  level: info
  fields:
    service: registry-mirror
storage:
  delete:
    enabled: true
  filesystem:
    rootdirectory: /var/lib/registry
proxy:
  remoteurl: https://registry-1.docker.io
  ttl: 168h
http:
  addr: :5000
  tls:
    certificate: /certs/tls.crt
    key: /certs/tls.key
YAML
cat >docker-compose.yml <<'COMPOSE'
services:
  registry:
    image: ${REGISTRY_IMAGE:?Set REGISTRY_IMAGE in .env}
    container_name: registry-mirror
    restart: unless-stopped
    ports:
      - "127.0.0.1:5001:5000"
    volumes:
      - ./data:/var/lib/registry
      - ./config/config.yml:/etc/distribution/config.yml:ro
      - ./certs:/certs:ro
COMPOSE
docker compose config --quiet
docker compose up -d
docker compose ps
curl --fail --silent --show-error \
  --cacert certs/tls.crt \
  --resolve registry-mirror.home.local:5001:127.0.0.1 \
  https://registry-mirror.home.local:5001/v2/ -o /dev/null
```

Expected result: container is `Up`, TLS verification succeeds with the explicit
certificate, and `/v2/` returns success. Logs show proxy-cache mode and no
upstream username. Keep loopback binding until client firewall/DNS/CA trust and
quota alerting are ready.

## 3. Open only the approved internal source path

After adding the exact source-scoped firewall rule, change the published address
from `127.0.0.1:5001:5000` to `192.168.20.102:5001:5000`, recreate, and test an
approved and a denied client. Do not publish on all interfaces.

Run on: docker-host over SSH after the reviewed binding change.

```bash
cd /opt/stacks/registry-mirror
docker compose config --quiet
docker compose up -d
ss -lntp | grep '192.168.20.102:5001'
docker compose logs --tail=80
```

Expected result: only the docker-host VLAN 20 address owns port `5001`, mirror
logs are healthy, approved client TLS works, and denied VLAN/source access fails.

## 4. Configure one canary Docker client reversibly

Install the project local CA in the canary's OS trust store first and prove
`curl https://registry-mirror.home.local:5001/v2/` succeeds without `-k`.

Run on: approved canary Docker client during a maintenance window.

```bash
checkpoint="$(date +%Y%m%dT%H%M%S)"
install -d -m 0755 /etc/docker
if test -f /etc/docker/daemon.json; then
  cp -a /etc/docker/daemon.json "/etc/docker/daemon.json.pre-mirror-${checkpoint}"
  jq '. + {"registry-mirrors":["https://registry-mirror.home.local:5001"]}' \
    /etc/docker/daemon.json >"/etc/docker/daemon.json.mirror-${checkpoint}"
else
  : >"/etc/docker/daemon.json.pre-mirror-${checkpoint}.absent"
  jq -n '{"registry-mirrors":["https://registry-mirror.home.local:5001"]}' \
    >"/etc/docker/daemon.json.mirror-${checkpoint}"
fi
dockerd --validate --config-file="/etc/docker/daemon.json.mirror-${checkpoint}"
install -m 0644 "/etc/docker/daemon.json.mirror-${checkpoint}" /etc/docker/daemon.json
systemctl restart docker
docker info --format '{{json .RegistryConfig.Mirrors}}'
docker pull busybox:stable
```

Expected result: validation succeeds before replacement, Docker restarts in the
window, mirror URL appears in `docker info`, and the canary pull succeeds. On
the mirror, logs must show the corresponding request; a locally cached client
image alone is not proof.

## 5. Client rollback drill

Run on: approved canary Docker client during the same window.

```bash
ls -1t /etc/docker/daemon.json.pre-mirror-* | head -n 3
```

Select the exact checkpoint made above. If it is a real JSON backup, validate
and restore it; if the `.absent` marker was created, move current
`daemon.json` aside instead of inventing an empty configuration. Restart Docker,
confirm the mirror URL is absent, and pull an approved public test image directly
from Docker Hub. Do not automate checkpoint selection in a destructive command.

Expected result: direct pulls work and all existing containers return. Reapply
the validated mirror configuration only if the evaluation continues.

## Backup, updates, and disposal

Back up `config/config.yml`, Compose, pinned digest reference, public certificate,
quota/alert definition, and client rollback records. Do not back up `data`; it is
a regenerable cache. Keep the TLS private key only in the protected certificate
backup workflow.

Before image updates, record digest, confirm client rollback, pull/pin the new
`registry:3` digest, recreate, and repeat TLS/canary/cache-log tests. No automatic
updates.

To reject the evaluation, restore every client first, verify direct pulls, stop
the mirror, remove its firewall/DNS rule, and preserve configuration evidence.
Cache deletion requires a separate exact-path approval after `findmnt` and
capacity verification.

## Failure recovery matrix

| Failure | Safe response | Proof before continuing |
|---|---|---|
| TLS trust/name failure | Do not add insecure registry; repair SAN/CA trust. | Client `/v2/` succeeds without `-k`. |
| Docker daemon rejects config | Leave original file in place; inspect generated checkpoint. | `dockerd --validate` succeeds. |
| Client pulls fail | Restore exact prior daemon file/absent state and restart Docker. | Direct pull and existing workloads pass. |
| Cache fills quota | Stop mirror; expire/garbage-collect only under approved procedure. | Usage below threshold and filesystem healthy. |
| Private upstream content appears | Stop mirror and revoke credentials; audit clients/cache. | Anonymous public-only config restored. |
| Mirror unavailable | Docker clients may fall back; restore/remove mirror config if delays persist. | Direct upstream timing/pulls return to baseline. |

## Completion checklist

- [ ] Measured benefit, client list, quota/alert, TLS, scope, TTL, and rollback gate approved.
- [ ] Immutable `registry:3` digest and public-only proxy config are recorded.
- [ ] Trusted HTTPS works; no insecure-registry client setting exists.
- [ ] One canary uses the mirror and mirror logs prove the pull.
- [ ] Canary rollback restores direct pulls and existing workloads.
- [ ] Config is backed up; cache blobs are excluded and disposable.
- [ ] No private upstream credential, public exposure, or automatic update exists.
