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

## Operator path

This historical shim does not override the September host-network exception or
uncommissioned P1S state. Use the [stack lifecycle runbook](../../../configs/docker-host/stacks/bambuddy/README.md)
for backup, update and isolated restore, and the linked docker-host guide for
VM creation. Do not replace existing credentials during recovery.

For MQTT acceptance, use Home Assistant's authenticated MQTT integration topic
listener with `bambuddy/#`; do not put the MQTT password in a shell command.
Use idle printer status only after commissioning is authorized. MQTT TLS8883
remains required outside a documented temporary recovery exception.
