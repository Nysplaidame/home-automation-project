# Roadmap Feasibility Disposition

Initial mechanical classification; final feasibility is controlled by current vendor and live-state evidence.

| Source line | Section | Roadmap item | Initial classification |
|---:|---|---|---|
| 46 | Hardening and resilience roadmap | Plan the whole-system hardening run before changing credentials or access paths: inventory all admin surfaces, service accounts, API tokens, SSH keys, certificates, Tailscale/WireGuard paths, OpenWrt rules, host firewalls, and password-manager records. | `requires-evidence-review` |
| 47 | Hardening and resilience roadmap | Plan the whole-system resilience run before live drills: define recovery goals, access routes, trusted backups, restore order, and stop/ask gates for Mini PC, OMV, router, Home Assistant, docker-host, Frigate, llm-host, monitoring, Tailscale, local CA, and credential-loss scenarios. | `requires-evidence-review` |
| 48 | Hardening and resilience roadmap | Prove backup and restore readiness before broad credential rotation: Proxmox VM/LXC restore evidence, HA backup restore path, OMV export/config recovery path, and repo/config backup coverage. Docker-host app-data backup/restore smoke passed on 2026-07-07. | `requires-evidence-review` |
| 49 | Hardening and resilience roadmap | Execute hardening run in a controlled window: rotate infrastructure passwords, API tokens, long-lived HA tokens, app bootstrap credentials, SSH keys, and service secrets; validate each dependent service before revoking old credentials. | `requires-evidence-review` |
| 50 | Hardening and resilience roadmap | Execute resilience tabletop scenarios before disruptive tests: document what still works, what fails, first diagnostic commands, recovery route, rollback path, and "do not touch" boundaries for each major failure scenario. | `requires-evidence-review` |
| 51 | Hardening and resilience roadmap | Execute only low-risk live resilience drills first: stop non-critical services or simulate dependency loss where rollback is immediate; defer Mini PC, router, OMV, and broad network failure drills until a dedicated maintenance window. | `requires-evidence-review` |
| 52 | Hardening and resilience roadmap | Update canonical docs after each pass: `docs/reference/current-live-state.md`, `docs/reference/access-matrix.md`, `docs/reference/service-matrix.md`, `scripts/backup/backup_strategy.md`, and relevant procedures/handoffs. | `requires-evidence-review` |
| 53 | Hardening and resilience roadmap | Define log retention and analysis policy for the whole assistant stack: set 48-hour retention defaults for structured assistant state, compact conversation traces, tool summaries, and performance timings; explicitly exclude raw audio, full prompt/tool dumps, secrets, and unbounded verbose logs unless temporarily enabled for debugging with rotation and review gates. | `requires-evidence-review` |
| 68 | Operational next steps | Expand VentSys beyond valve 1: finish the MQTT TLS migration path, then flash/adopt the remaining ESPHome devices | `requires-evidence-review` |
| 76 | Operational next steps | Parked: add Mullvad egress path for SearXNG/Whoogle on docker-host (privacy hardening), only after current Frigate + OMV pre-flight blockers are cleared | `requires-evidence-review` |
| 94 | Operational next steps | Schedule controlled docker-host patch window for Docker engine/component and kernel package candidates from `docs/procedures/update_review_log.md` | `requires-evidence-review` |
| 101 | Operational next steps | Add a scoped, confirmation-gated Overwatch action for saving recipes to Mealie | `requires-evidence-review` |
| 102 | Operational next steps | Keep Hermes Agent roadmap-only until local LLM, STT, TTS, monitoring, and safety gates are stable | `requires-evidence-review` |
| 103 | Operational next steps | Keep future YouTube transcript/query app architecture undecided; VM 103 is only the expected target for future containerized query apps | `requires-evidence-review` |
| 107 | Operational next steps | Optional only if mobile access becomes flaky: improve Tailscale direct connectivity for off-WiFi mobile access by adding explicit UDP `41641` forwarding through the upstream router and GL-MT6000 to docker-host; current user validation on 2026-07-03 found CCTV feeds working on both home WiFi and mobile data with Tailscale | `requires-evidence-review` |
| 109 | Operational next steps | Approve and validate the new Tailscale `192.168.30.20/32` Frigate host route for off-WiFi Frigate PWA access; docker-host route advertisement, docker-host UFW routed allow, and OpenWrt docker-host-to-Frigate HTTPS rule were staged on 2026-07-05 | `requires-evidence-review` |
| 110 | Operational next steps | Add an internal web-based Mermaid diagram viewer for `docs/diagrams/` so the canonical `.mermaid` sources can be browsed without opening the Obsidian desktop vault; keep it read-only and internal-only | `requires-evidence-review` |
| 133 | Docker-host app roadmap | Evaluate Paperless-ngx under `/opt/stacks/paperless-ngx/` | `requires-evidence-review` |
| 138 | Docker-host app roadmap | Parked: Self-hosted LiveSync client rollout; backend/client prep exists, but Obsidian is no longer part of the near-term path | `requires-evidence-review` |
| 142 | Docker-host app roadmap | Evaluate Actual Budget under `/opt/stacks/actual-budget/` | `requires-evidence-review` |
| 143 | Docker-host app roadmap | Evaluate Scrypted under `/opt/stacks/scrypted/` | `requires-evidence-review` |
| 149 | Docker-host app roadmap | Evaluate Vaultwarden only after a backup/security review | `requires-evidence-review` |
| 150 | Docker-host app roadmap | Evaluate Portainer only if its convenience beats the added admin surface | `requires-evidence-review` |
| 152 | Docker-host app roadmap | Revisit local registry mirror after more Compose workloads exist | `requires-evidence-review` |
| 153 | Docker-host app roadmap | Evaluate Node-RED only if HA native automations are insufficient | `requires-evidence-review` |
| 167 | Home Assistant apps and enhancement roadmap | Review Companion App sensors and enable only useful presence, battery, network, and notification sensors | `requires-evidence-review` |
| 171 | Home Assistant apps and enhancement roadmap | Prefer Studio Code Server for larger YAML/package edits; keep File Editor as fallback | `requires-evidence-review` |
| 181 | Home Assistant apps and enhancement roadmap | Evaluate Mushroom Cards for general dashboards, room views, service status, printer state, and VentSys summaries | `requires-evidence-review` |
| 182 | Home Assistant apps and enhancement roadmap | Evaluate apexcharts-card for temperature, VOC, airflow, pressure, power, and IAQ history | `requires-evidence-review` |
| 183 | Home Assistant apps and enhancement roadmap | Evaluate auto-entities for dynamic maintenance views such as unavailable ESPHome devices or low batteries | `requires-evidence-review` |
| 184 | Home Assistant apps and enhancement roadmap | Evaluate Watchman before and after major dashboard/entity refactors | `requires-evidence-review` |
| 188 | Home Assistant apps and enhancement roadmap | Evaluate Bubble Card for mobile-friendly popups and compact controls | `requires-evidence-review` |
| 189 | Home Assistant apps and enhancement roadmap | Evaluate browser_mod for garage kiosk / wall display behavior after the display hardware exists | `requires-evidence-review` |
| 190 | Home Assistant apps and enhancement roadmap | Evaluate button-card for polished custom controls after core dashboard layout stabilizes | `requires-evidence-review` |
| 191 | Home Assistant apps and enhancement roadmap | Evaluate card-mod sparingly for styling once layout is stable | `requires-evidence-review` |
| 192 | Home Assistant apps and enhancement roadmap | Evaluate Scheduler Card / scheduler-component if native schedules feel awkward | `requires-evidence-review` |
| 193 | Home Assistant apps and enhancement roadmap | Evaluate Adaptive Lighting only if smart lighting enters project scope | `requires-evidence-review` |
| 194 | Home Assistant apps and enhancement roadmap | Revisit Bambu Lab / printer HACS integrations only after P1S details are confirmed and Bambuddy overlap is understood | `requires-evidence-review` |
| 198 | Home Assistant apps and enhancement roadmap | Keep Node-RED Tier 3/evaluate unless HA native automations become insufficient | `requires-evidence-review` |
| 199 | Home Assistant apps and enhancement roadmap | Evaluate AppDaemon only if Python automation apps are justified for non-critical logic | `requires-evidence-review` |
| 200 | Home Assistant apps and enhancement roadmap | Evaluate pyscript only for non-critical helper logic after a rollback plan exists | `requires-evidence-review` |
| 201 | Home Assistant apps and enhancement roadmap | Keep Claude/MCP or other AI automation as future advisory-only work; do not let it replace safety-critical HA/ESPHome/MQTT logic | `requires-evidence-review` |
