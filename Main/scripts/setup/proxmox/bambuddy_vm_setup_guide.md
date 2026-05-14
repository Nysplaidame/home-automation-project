# Bambuddy Workload Setup Guide

> Historical compatibility shim, updated 2026-05-07.
> VM 103 is now the central Docker host, not a single-purpose app VM.
> Use `scripts/setup/proxmox/docker_host_setup_guide.md` as the source of truth.

Bambuddy remains the first workload on VM 103:

| Component | Current value |
|---|---|
| Docker host | VM 103, `docker-host`, `192.168.20.102`, VLAN 20 |
| Bambuddy stack | `/opt/stacks/bambuddy` |
| Bambuddy UI | `http://192.168.20.102:8000` |
| P1S printer | `192.168.35.200`, VLAN 35 |
| Home Assistant | VM 100, `192.168.20.101`, VLAN 20 |
| HA package | `configs/home-assistant/bambuddy_p1s_package.yaml` |
| Canonical deployment guide | `scripts/setup/proxmox/docker_host_setup_guide.md` |

## Operator Checklist

1. Follow `scripts/setup/proxmox/docker_host_setup_guide.md` to manage VM 103
   and the `/opt/stacks/bambuddy` Compose workload.
2. Create `/opt/stacks/bambuddy/.env` from `.env.example` and set the real MQTT
   password from Bitwarden.
3. Start Bambuddy with `docker compose up -d` from `/opt/stacks/bambuddy`.
4. Configure Bambuddy in the web UI with the P1S serial number, LAN access code,
   and Home Assistant long-lived token.
5. Deploy `configs/home-assistant/bambuddy_p1s_package.yaml` to
   `/config/packages/` on Home Assistant after replacing `<P1S_SERIAL>`.

## Quick Verification

From VM 103:

```bash
hostname
cd /opt/stacks/bambuddy && docker compose config
nc -zv 192.168.35.200 8883
nc -zv 192.168.35.200 21
nc -zv 192.168.20.101 8883
nc -zv 192.168.20.101 8123
```

From Home Assistant:

```bash
mosquitto_sub -h 192.168.20.101 -p 8883 --cafile /ssl/ca.crt \
  -u mqtt -P '<password>' -t 'bambuddy/#' -v
```

After Mosquitto TLS is enabled, switch the MQTT checks and Bambuddy `.env` from
port `1883` to `8883` per `docs/procedures/ssl_tls_guide.md`, enable TLS in
the Bambuddy application settings, and confirm retained `bambuddy/status`
arrives.
