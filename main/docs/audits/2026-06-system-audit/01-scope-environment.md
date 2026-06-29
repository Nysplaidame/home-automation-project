---
title: Audit Scope and Environment
created: 2026-06-21
modified: 2026-06-21
type: audit-evidence
status: complete
---

# Audit Scope and Environment

## Evidence rules

Truth precedence is live observed behaviour, canonical active records, durable decisions/procedures, wiki, then historical material. A running endpoint proves reachability, not functional correctness. A parse pass proves syntax, not safe behaviour. A checked TODO proves only that the project record asserts completion unless independently corroborated.

Secrets were never copied into this evidence pack. Discovery was read-only except for ignored router compiler output and these audit artefacts. No production configuration, firewall, service, hardware output, or canonical document was changed.

## Repository snapshot

| Item | Value |
|---|---|
| Active checkout | `E:\home-automation-project` |
| Stale context | `G:\home-automation-project` is not mounted |
| Branch / commit | `main` / `f808556282cd8888791029df2e5a0a40fb1126ac` |
| Initial worktree | Clean |
| Tracked artefacts | 448 |
| Active project root | `main/` |
| Machine inventory | `artifact-inventory.csv` |
| Host | Windows, management Wi-Fi `192.168.10.105/24` |
| Gateway / DNS | `192.168.10.1` |
| Available tooling | Python 3.13.13, PyYAML, PowerShell 7, Git/OpenSSH, ESPHome 2026.5.3 |
| Missing local tooling | Node/npm, Docker CLI, standalone Bash on PATH |

## Live environment snapshot

| Layer | Observed state |
|---|---|
| Router | `192.168.10.1`, SSH/HTTP reachable; full validation 87/87; connectivity validation 85/85 |
| Proxmox | `192.168.10.10`, PVE 9.1.9; root filesystem 79% used; 30 GiB RAM with 11 GiB available and 3.5 GiB swap used |
| QEMU | 100/102/103 running; retired 101/104 stopped |
| LXC | 111/114 running; CT 114 carries `snapshot-delete` lock |
| Home Assistant | HAOS 2026.6.3, HTTP reachable, Samba readable |
| Docker host | Debian 13; 15 listed containers; UFW active default-deny incoming/routed; Tailscale online |
| Frigate | CT 111 container healthy; one failed `run-rpc_pipefs.mount` unit |
| Local AI | CT 114 services reachable; legacy local LLM runtime reports model loaded 100% on GPU |
| Monitoring | Grafana, InfluxDB, Uptime Kuma, Telegraf live; no failed host units |
| OMV/cameras | Not built, consistent with planned status |

## Coverage and limitations

- All tracked artefacts received an inventory result; parseable JSON, YAML, Python, and PowerShell were syntax-checked.
- All 364 checklist rows received a disposition. Completion assertions were sampled against live evidence; they are not automatically certification.
- Live checks were management-origin only. Representative source-VLAN negative tests require test clients or network namespaces in scheduled windows.
- Browser rendering was blocked because both the in-app browser runtime and local Node/Playwright runtime were unavailable.
- Current official vendor-document lookups were attempted twice and blocked by the browsing service with HTTP 403. Roadmap classifications therefore rely on installed-version validation and local/deployed evidence and must be vendor-rechecked during remediation.
- No physical VentSys, camera, power-loss, restore, or outage test was performed.
