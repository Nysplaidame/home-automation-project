# Frigate LXC Setup Guide

Compatibility filename retained for existing links. Production Frigate runs in
unprivileged **CT 111**, not VM 101.

## Production specification

| Field | Value |
|---|---|
| Hostname | `frigate-nvr` |
| Address | `192.168.30.20/24`, gateway `192.168.30.1`, VLAN 30 |
| Resources | 2 cores, 4096 MiB RAM, 32 GiB root, no swap |
| Features | `nesting=1,keyctl=1` |
| Startup | `onboot=1`, order 2 |
| Workload | Docker Compose at `/opt/frigate` |

Use a current Debian LXC template. Install Docker Engine, Compose, UFW,
Fail2ban, `intel-gpu-tools` and `vainfo`. Apply shared GPU mapping from
`igpu_passthrough_guide.md`.

Deploy:

- `configs/frigate/docker-compose.yml` to
  `/opt/frigate/docker-compose.yml`
- a deliberate production config to `/opt/frigate/config/config.yml`
- `configs/frigate/system/frigate-nvr-fail2ban-sshd.local`

The current live baseline intentionally has `mqtt.enabled: false` and
`cameras: {}`. Do not deploy placeholder cameras from the repository until
camera models, RTSP URLs and credentials are real.

## Required validation

```bash
cd /opt/frigate
docker compose config -q
docker compose up -d
docker ps --filter name=frigate
docker exec frigate ps aux | grep '[d]etector:ov'
curl -kfsS https://127.0.0.1:8971/ >/dev/null
curl -fsS http://127.0.0.1:5000/api/version
```

VM 101 is a stopped rollback artifact only. Never start it while CT 111 owns
`192.168.30.20`.
