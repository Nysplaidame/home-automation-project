---
title: Node-RED Install Manual
description: Safe-mode, authenticated Node-RED evaluation with secret-coupled backup, restore, and rollback
tags: [install, docker-host, node-red, tier3]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: draft-installable
---

# Node-RED Install Manual

## Purpose

Evaluate Node-RED only for a named workflow that Home Assistant cannot implement
clearly and safely. Node-RED can become a second automation authority; it must
start in safe mode with no production credentials or active outputs. The default
decision is **parked**.

## Runs on

- docker-host over SSH at `192.168.20.102`;
- trusted Tailscale management browser through approved HTTPS.

## Mandatory gate

Record:

- exact workflow and why HA/firmware is insufficient;
- proof the workflow is not fire, smoke, thermal shutdown, ventilation safety,
  access control, or another safety-critical interlock;
- immutable Node-RED image digest and reviewed node/module allowlist;
- loopback-only raw editor port `1880` plus private HTTPS endpoint;
- `adminAuth`, named admin password, and stored credential encryption secret;
- safe-mode first boot and a harmless inject/debug pilot with no external output;
- backup of flows, credentials, settings, modules, and credential secret as one
  recovery set; isolated safe-mode restore;
- explicit promotion step, HA/MQTT least-privilege credentials, monitoring, and
  rollback ownership.

No production HA token, MQTT command credential, Docker socket, host path, USB
device, or broad VLAN route is allowed during the initial evaluation.

## Inputs

- `<NODE_RED_ADMIN_PASSWORD>`
- `<NODE_RED_CREDENTIAL_SECRET>`

Create/store both in Bitwarden first. They must be distinct and never appear in
tracked files or command-line arguments.

## 1. Pin the image and generate the bcrypt admin hash

Run on: docker-host over SSH after gate approval and during a maintenance window.

```bash
docker pull nodered/node-red:latest
node_red_image="$(docker image inspect nodered/node-red:latest --format '{{index .RepoDigests 0}}')"
test -n "$node_red_image"
install -d -m 0700 /opt/stacks/node-red/data
printf 'NODE_RED_IMAGE=%s\n' "$node_red_image" >/opt/stacks/node-red/.image.env
chmod 0600 /opt/stacks/node-red/.image.env
printf '%s\n' "$node_red_image"
docker run --rm -it "$node_red_image" node-red admin hash-pw
```

Expected result: immutable digest prints, then Node-RED prompts twice for
`<NODE_RED_ADMIN_PASSWORD>` and prints a bcrypt hash. Copy only the resulting
hash for the next interactive step; do not pass the clear password as an
argument.

## 2. Create root-only runtime secrets and settings

Run on: docker-host over SSH.

```bash
cd /opt/stacks/node-red
read -r -p 'Paste Node-RED bcrypt admin hash: ' node_red_admin_hash
read -r -s -p 'Enter NODE_RED_CREDENTIAL_SECRET from Bitwarden: ' node_red_credential_secret
printf '\n'
test -n "$node_red_admin_hash"
test -n "$node_red_credential_secret"
umask 077
{
  cat .image.env
  printf 'NODE_RED_ADMIN_PASSWORD_HASH=%s\n' "$node_red_admin_hash"
  printf 'NODE_RED_CREDENTIAL_SECRET=%s\n' "$node_red_credential_secret"
} >.env
unset node_red_admin_hash node_red_credential_secret
chmod 0600 .env
cat >data/settings.js <<'JAVASCRIPT'
module.exports = {
  credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET,
  adminAuth: {
    type: "credentials",
    sessionExpiryTime: 86400,
    users: [{
      username: "admin",
      password: process.env.NODE_RED_ADMIN_PASSWORD_HASH,
      permissions: "*"
    }]
  },
  editorTheme: {
    projects: { enabled: false }
  }
};
JAVASCRIPT
chmod 0640 data/settings.js
```

Expected result: `.env` is mode `0600`, contains the pinned image/hash/credential
secret, and `settings.js` references environment variables rather than clear
secrets. `.env` must be ignored by Git and included only in the protected secret
recovery process.

## 3. Start loopback-only in safe mode

Run on: docker-host over SSH.

```bash
cd /opt/stacks/node-red
cat >docker-compose.yml <<'COMPOSE'
services:
  node-red:
    image: ${NODE_RED_IMAGE:?Set NODE_RED_IMAGE in .env}
    container_name: node-red
    restart: unless-stopped
    ports:
      - "127.0.0.1:1880:1880"
    environment:
      TZ: Europe/London
      NODE_RED_ENABLE_SAFE_MODE: "true"
      NODE_RED_ADMIN_PASSWORD_HASH: ${NODE_RED_ADMIN_PASSWORD_HASH:?Set admin hash}
      NODE_RED_CREDENTIAL_SECRET: ${NODE_RED_CREDENTIAL_SECRET:?Set credential secret}
    volumes:
      - ./data:/data
COMPOSE
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=100
ss -lntp | grep '127.0.0.1:1880'
```

Expected result: container is `Up`, logs identify safe mode/no running flows,
and only loopback owns `1880`. Stop if logs warn about a system-generated
credential key, settings parse failure, or active flows.

## 4. Add private HTTPS and test authentication

Run on: docker-host over SSH only after confirming Serve port `8447` is free and approved.

```bash
tailscale serve status
tailscale serve --bg --https=8447 http://127.0.0.1:1880
tailscale serve status
```

Expected result: existing handlers remain and `8447` proxies only to loopback
Node-RED. Open `https://docker-host.tail7012a0.ts.net:8447/` from the approved
identity. Incorrect credentials must fail; `<NODE_RED_ADMIN_PASSWORD>` must open
the editor. An unapproved Tailscale identity/source must fail before Node-RED.

Do not disable safe mode. Create only a disconnected Inject -> Debug pilot,
export its JSON, and verify no HA/MQTT/network/device node exists.

## 5. Back up the coupled recovery set

The encrypted `flows_cred.json` is unusable without the exact credential secret.
Back up `/opt/stacks/node-red/data` consistently and store
`<NODE_RED_CREDENTIAL_SECRET>` in Bitwarden/offline recovery. The `.env` file is
not a normal plaintext app-data artifact; protect it as a secret.

Run on: docker-host over SSH while Node-RED remains in safe mode.

```bash
cd /opt/stacks/node-red
docker compose stop node-red
find data -maxdepth 2 -type f -printf '%s %p\n' | sort
findmnt -T /mnt/omv/docker-host-backups
systemctl start docker-host-app-data-backup.service
systemctl --no-pager --full status docker-host-app-data-backup.service
docker compose up -d
docker compose logs --tail=60
```

Expected result: data/settings/flow/module files are inventoried, the OMV job
succeeds, and Node-RED returns in safe mode. Confirm backup coverage explicitly;
do not infer it from a successful generic job.

## 6. Isolated safe-mode restore

Restore the selected data backup to `/opt/stacks/node-red-restore-test/data`,
create a disposable Compose project on loopback port `11880`, and inject the
same credential secret/hash from Bitwarden without copying production `.env` to
an unprotected location. Keep `NODE_RED_ENABLE_SAFE_MODE=true`.

Run on: docker-host over SSH after the disposable project is configured.

```bash
cd /opt/stacks/node-red-restore-test
docker compose config --quiet
docker compose up -d
docker compose ps
docker compose logs --tail=100
```

Expected result: restored editor authenticates, starts in safe mode, shows the
harmless pilot flow, and can decrypt any disposable credential without running
the flow. A missing/wrong credential secret must be treated as a failed restore.

Run on: docker-host over SSH after recording restore proof.

```bash
cd /opt/stacks/node-red-restore-test
docker compose down --remove-orphans
```

Expected result: only disposable resources stop. Never use `down -v` without
listing and approving the exact disposable volumes.

## Promotion, updates, and rollback

Promotion out of safe mode requires a second approval covering exact HA/MQTT
service accounts, flow outputs, rate limits, timeout/error behavior, and an
independent HA/firmware safety path. Change safe mode only in a checkpointed
Compose file during a watched test window.

Before updates, export flows, stop for a consistent backup, record digest, review
runtime/node compatibility, pin the new digest, and repeat auth/safe-mode/restore
checks. No automatic module or container updates.

Run on: docker-host over SSH to reject/roll back the evaluation.

```bash
tailscale serve --https=8447 off
cd /opt/stacks/node-red
docker compose down
docker ps --format '{{.Names}}' | grep -Fx node-red && exit 1 || true
ss -lntp | grep -E ':(1880|8447)\b' && exit 1 || true
```

Expected result: Node-RED and its private route are absent while HA/firmware
automations continue unchanged. Preserve the encrypted flow recovery set until
the rejection decision confirms disposal.

## Completion checklist

- [ ] Concrete non-safety workflow and HA-overlap gate approved.
- [ ] Immutable digest, reviewed node allowlist, and no auto-update policy recorded.
- [ ] Editor is loopback-only behind private HTTPS with `adminAuth`.
- [ ] Credential secret is stored and runtime does not use a generated key.
- [ ] First boot/pilot and isolated restore remain in safe mode.
- [ ] Flow/data backup and credential secret restore as one recovery set.
- [ ] No production token, command output, Docker socket, device, or safety flow exists before promotion approval.
