---
title: Phase 05 - docker-host
description: Docker app host baseline, Compose policy, UFW, and Tailscale host routes
tags: [install, docker-host, tailscale]
created: 2026-05-24
modified: 2026-05-27
type: install-guide
status: active
---

# Phase 05 - docker-host

## Purpose

Build VM 103 as the trusted Docker Compose host for internal services and the
Tailscale host-route subnet router.

## Runs on

docker-host over SSH at `192.168.20.102`.

## Prerequisites

- Phase 02 complete.
- Router allows documented docker-host Tailscale and AdGuard upstream egress.
- `<TAILSCALE_AUTH_KEY>` ready.

## Inputs

- `<TAILSCALE_AUTH_KEY>`

## Commands

Run on: docker-host over SSH.

```sh
apt-get update
apt-get install -y ca-certificates curl gnupg ufw qemu-guest-agent
systemctl enable --now qemu-guest-agent
```

Run on: docker-host over SSH after adding the official Docker apt repo.

```sh
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
docker --version
docker compose version
mkdir -p /opt/stacks
```

Run on: docker-host over SSH after installing Tailscale.

```sh
echo 'net.ipv4.ip_forward = 1' >/etc/sysctl.d/99-tailscale-subnet-router.conf
sysctl -p /etc/sysctl.d/99-tailscale-subnet-router.conf
tailscale up --auth-key='<TAILSCALE_AUTH_KEY>' --advertise-routes=192.168.20.101/32,192.168.40.50/32
tailscale status
```

## Explanation

Docker hosts the internal Compose stacks under `/opt/stacks/<service>/`.
Tailscale advertises only host routes for HA and OMV; broad VLAN subnet routes
are intentionally not used.

VM 103 is the expected target for future containerized AI-adjacent query apps
after their own app-specific design is approved. It is not the host for local
LLM, STT, or TTS inference; those workloads belong on VM 104 `llm-host` in
Phase 05A.

Current non-secret rebuild templates for the live docker-host stacks and host
firewall are stored under `configs/docker-host/`. They are source templates,
not backups of live secrets, app databases, ntfy auth DBs, or AdGuard password
hashes.

## Expected result

- Docker Compose works.
- `/opt/stacks/` exists.
- Tailscale shows docker-host online.
- Tailscale admin console shows only `192.168.20.101/32` and `192.168.40.50/32`
  pending or approved.

## Validation

Run on: docker-host over SSH.

```sh
docker run --rm hello-world
tailscale status
ip route | grep tailscale || true
ufw status verbose
```

## Failure recovery

- If Docker install fails, re-check the official Docker Debian repo setup.
- If routes do not appear, approve them in the Tailscale admin console.
- If LAN access breaks after UFW, disable UFW from console and reapply narrower
  rules from the docker-host guide.

## Completion checklist

- [x] Docker Compose installed.
- [x] `/opt/stacks/` created.
- [x] Tailscale installed and authenticated.
- [x] Only HA and OMV host routes are advertised.
- [x] No containers are deployed outside `/opt/stacks/<service>/`.
