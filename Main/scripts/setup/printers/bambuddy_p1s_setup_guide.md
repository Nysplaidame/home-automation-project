# Bambuddy + P1S Setup Guide

> Historical shim only, 2026-04. The current deployment is documented in
> `scripts/setup/proxmox/docker_host_setup_guide.md`.

This file is retained only so old links do not break.
It is not the source of truth and must not be used as the primary deployment
guide. Use the Docker host guide instead.

## Current Architecture

| Component | Current value |
|---|---|
| Docker host | VM 103, `docker-host`, `192.168.20.102`, VLAN 20 |
| Bambuddy stack | `/opt/stacks/bambuddy` |
| Bambuddy UI | `http://192.168.20.102:8000` |
| P1S printer | `192.168.35.200`, VLAN 35 |
| Home Assistant | VM 100, `192.168.20.101`, VLAN 20 |
| MQTT broker | Mosquitto on Home Assistant, TLS port `8883` |
| HA package | `configs/home-assistant/bambuddy_p1s_package.yaml` |
| Canonical deployment guide | `scripts/setup/proxmox/docker_host_setup_guide.md` |

## Operator Checklist

1. Follow `scripts/setup/proxmox/docker_host_setup_guide.md` to manage VM 103
   and deploy the Bambuddy workload.
2. Confirm the P1S DHCP reservation in `configs/openwrt/dhcp-config.conf`
   resolves to `192.168.35.200`.
3. Confirm the Bambuddy firewall rules in `configs/openwrt/firewall-config.conf`
   allow VM 103 to reach the printer and Home Assistant.
4. Configure Bambuddy in the web UI with the P1S serial number, LAN access
   code, and secure printer connection mode.
5. Deploy `configs/home-assistant/bambuddy_p1s_package.yaml` to
   `/config/packages/` on Home Assistant after replacing `<P1S_SERIAL>`.
6. Add the Bambuddy dashboard iframe using `http://192.168.20.102:8000`.

## Quick Verification

From VM 103:

```bash
nc -zv 192.168.35.200 8883
nc -zv 192.168.35.200 21
nc -zv 192.168.20.101 8883
nc -zv 192.168.20.101 8123
```

From Home Assistant:

```bash
mosquitto_sub -h localhost -p 8883 --cafile /ssl/ca.crt \
  -u mqtt -P '<password>' -t 'bambuddy/#' -v
```

If these checks pass, continue in the canonical Docker host guide.
