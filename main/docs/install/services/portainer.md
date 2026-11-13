---
title: Portainer Install Manual
description: Root-equivalent Docker management UI candidate with access, backup, restore, and rollback gates
tags: [install, docker-host, portainer, tier3]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Portainer Install Manual

## Purpose

Evaluate Portainer CE only if its UI provides a concrete operational benefit
over reviewed Compose files and SSH. Mounting `/var/run/docker.sock` grants
root-equivalent control of docker-host; the default decision is **parked**.

## Runs on

- docker-host over SSH at `192.168.20.102`;
- trusted Tailscale management browser through approved HTTPS only.

## Mandatory gate

Approve and record:

- accepted Docker-socket blast radius and named owner;
- immutable Portainer CE LTS image digest;
- raw Portainer HTTPS bound only to `127.0.0.1:9443`;
- unique Tailscale Serve port `8446` and ACL-approved identities;
- no Edge tunnel port `8000`, legacy HTTP `9000`, agent, webhooks, or public URL;
- named admin password and disabled anonymous statistics if that is project policy;
- encrypted Portainer configuration backup and its password custody;
- fresh, no-Docker-socket restore proof and complete route/container rollback.

Portainer backup does not back up the containers, volumes, or application data
it manages. Existing source Compose and workload backups remain authoritative.

## Inputs

- `<PORTAINER_ADMIN_PASSWORD>` entered only in the first-run UI.

Store the separate Portainer-backup encryption password in Bitwarden if backup
encryption is enabled; never put either password in Compose or shell history.

## 1. Capture baseline and pin the LTS digest

Run on: docker-host over SSH after gate approval.

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
ss -lntp | grep -E ':(8000|9000|9443|8446)\b' || true
tailscale serve status
docker pull portainer/portainer-ce:lts
portainer_image="$(docker image inspect portainer/portainer-ce:lts --format '{{index .RepoDigests 0}}')"
test -n "$portainer_image"
install -d -m 0700 /opt/stacks/portainer/data
printf 'PORTAINER_IMAGE=%s\n' "$portainer_image" >/opt/stacks/portainer/.env
chmod 0600 /opt/stacks/portainer/.env
printf '%s\n' "$portainer_image"
```

Expected result: candidate ports have no unknown owner, existing Serve handlers
are recorded, and an immutable `sha256:` image reference prints. Stop if the
port plan conflicts or the image/release is outside the approved LTS path.

## 2. Create a loopback-only evaluation stack

Run on: docker-host over SSH.

```bash
cd /opt/stacks/portainer
cat >docker-compose.yml <<'COMPOSE'
services:
  portainer:
    image: ${PORTAINER_IMAGE:?Set PORTAINER_IMAGE in .env}
    container_name: portainer
    restart: unless-stopped
    ports:
      - "127.0.0.1:9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/data
COMPOSE
docker compose config --quiet
docker compose up -d
docker compose ps
ss -lntp | grep '127.0.0.1:9443'
```

Expected result: Portainer is `Up`, only loopback `9443` is published, and no
`8000`/`9000` listener appears. Until the first admin is created, keep the
exposure window bounded and do not leave the initial setup page unattended.

## 3. Add private HTTPS access and initialize

Run on: docker-host over SSH only after confirming Serve port `8446` is free and approved.

```bash
tailscale serve status
tailscale serve --bg --https=8446 https+insecure://127.0.0.1:9443
tailscale serve status
```

Expected result: existing handlers remain and `8446` proxies only to loopback
Portainer. Open `https://docker-host.tail7012a0.ts.net:8446/` from an approved
Tailscale identity, create the named administrator with
`<PORTAINER_ADMIN_PASSWORD>`, decline unneeded telemetry, and connect only the
local Docker environment. Do not store registry/Git/cloud credentials or deploy
production stacks during evaluation.

From an unapproved identity/device, access must fail. An incorrect Portainer
password must fail from an approved client.

## 4. Validate the socket and exposure boundary

Run on: docker-host over SSH.

```bash
cd /opt/stacks/portainer
docker compose ps
docker inspect portainer --format '{{json .HostConfig.Binds}}'
docker inspect portainer --format '{{json .HostConfig.PortBindings}}'
ss -lntp | grep -E ':(8000|9000|9443)\b' || true
tailscale serve status
```

Expected result: the socket and `/data` are the only intended mounts, port
binding is loopback `9443`, `8000`/`9000` are absent, and only the approved Serve
handler exposes the UI. The socket is expected but is the reason this service
remains high risk.

## 5. Back up and restore without a Docker socket

In Portainer UI, open **Settings -> Back up Portainer**, enable password
protection, and download the configuration archive to the approved encrypted
backup location. Copy it off the client to protected OMV storage. The archive
can contain users, access control, API keys, endpoints, stack definitions, and
other credentials; do not commit it.

Restore only into a fresh instance with an empty data directory. For the proof,
create a disposable project bound to loopback `19443` with no Docker socket
mount, open it through a temporary SSH tunnel, and select **Restore Portainer
from backup** on the initialization page.

Run on: docker-host over SSH after the encrypted backup is safely stored.

```bash
install -d -m 0700 /opt/stacks/portainer-restore-test/data
docker run -d \
  --name portainer-restore-test \
  --restart=no \
  -p 127.0.0.1:19443:9443 \
  -v /opt/stacks/portainer-restore-test/data:/data \
  "$(. /opt/stacks/portainer/.env; printf '%s' "$PORTAINER_IMAGE")"
docker ps --filter name=portainer-restore-test
docker inspect portainer-restore-test --format '{{json .HostConfig.Binds}}'
```

Expected result: disposable Portainer listens only on loopback `19443`; its
bind list contains only disposable `/data` and no Docker socket. After UI
restore, verify admin login and representative Portainer settings, while the
environment remains disconnected from Docker.

Run on: docker-host over SSH after recording restore proof.

```bash
docker rm -f portainer-restore-test
```

Expected result: only the disposable container is removed. Preserve/remove the
disposable data directory according to the recorded cleanup decision.

## Updates

Export an encrypted Portainer backup, record the current digest, review the LTS
upgrade path, pull and pin the new digest, recreate, then repeat admin/exposure/
backup checks. Do not let Portainer or Watchtower update Portainer automatically.
Rollback to the prior compatible image/data checkpoint; validate upgrades on a
fresh test instance first when the database migration path is uncertain.

## Rejection/rollback

Run on: docker-host over SSH after an evaluation rejection or security failure.

```bash
tailscale serve --https=8446 off
cd /opt/stacks/portainer
docker compose down
docker ps --format '{{.Names}}' | grep -Fx portainer && exit 1 || true
ss -lntp | grep -E ':(9443|8446)\b' && exit 1 || true
```

Expected result: Serve handler and Portainer container/listeners are gone while
all unrelated workloads remain running. Preserve `/opt/stacks/portainer/data`
and the encrypted backup until the rejection decision confirms disposal.

## Completion checklist

- [ ] Root-equivalent socket gate and named owner are approved.
- [ ] LTS digest is pinned; only loopback `9443` and private Serve access exist.
- [ ] Named admin works; incorrect/unapproved access fails.
- [ ] No Edge/legacy/public listener or production deployment dependency exists.
- [ ] Encrypted UI backup restores into a fresh no-socket instance.
- [ ] Update/digest rollback and complete exposure removal are proven.
