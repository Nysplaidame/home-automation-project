# Roadmap Feasibility Disposition

This ledger classifies still-planned checklist items. External vendor-document verification was attempted but blocked by the browsing service; local installed-version validation and deployed-resource evidence were used instead.

| Source line | Roadmap item | Classification | Basis |
|---:|---|---|---|
| 48 | Configure OMV-backed Home Assistant backups once NAS storage is live, while keeping fast local Proxmox recovery on the MINISFORUM host | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 50 | Expand VentSys beyond valve 1: finish the MQTT TLS migration path, then flash/adopt the remaining ESPHome devices | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 58 | Parked: add Mullvad egress path for SearXNG/Whoogle on docker-host (privacy hardening), only after current Frigate + OMV pre-flight blockers are cleared | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 76 | Schedule controlled docker-host patch window for Docker engine/component and kernel package candidates from `docs/procedures/update_review_log.md` | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 77 | When NAS is built, add NAS telemetry using existing monitoring patterns first (prefer Telegraf -> InfluxDB -> Grafana before adding new containers) | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 83 | Add a scoped, confirmation-gated Overwatch action for saving recipes to Mealie | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 84 | Keep Hermes Agent roadmap-only until local LLM, STT, TTS, monitoring, and safety gates are stable | `redesign-required` | No bounded interface, security model, or acceptance contract exists |
| 85 | Keep future YouTube transcript/query app architecture undecided; VM 103 is only the expected target for future containerized query apps | `redesign-required` | No bounded interface, security model, or acceptance contract exists |
| 108 | Evaluate Paperless-ngx under `/opt/stacks/paperless-ngx/` | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 110 | Replace Mealie bootstrap administrator credentials and store them in Bitwarden | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 112 | Complete Grocy initial login, password change and household data model | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 113 | Roll Self-hosted LiveSync out to both Obsidian devices (Tailscale Serve is live) | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 116 | Evaluate Actual Budget under `/opt/stacks/actual-budget/` | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 117 | Evaluate Scrypted under `/opt/stacks/scrypted/` | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 123 | Evaluate Vaultwarden only after a backup/security review | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 124 | Evaluate Portainer only if its convenience beats the added admin surface | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 126 | Revisit local registry mirror after more Compose workloads exist | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 127 | Evaluate Node-RED only if HA native automations are insufficient | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 140 | Review Companion App sensors and enable only useful presence, battery, network, and notification sensors | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 144 | Prefer Studio Code Server for larger YAML/package edits; keep File Editor as fallback | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 148 | Install HACS only after a current HA backup exists | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 149 | Evaluate Frigate Card when Frigate and cameras are live | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 150 | Evaluate Mushroom Cards for general dashboards, room views, service status, printer state, and VentSys summaries | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 151 | Evaluate apexcharts-card for temperature, VOC, airflow, pressure, power, and IAQ history | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 152 | Evaluate auto-entities for dynamic maintenance views such as unavailable ESPHome devices or low batteries | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 153 | Evaluate Watchman before and after major dashboard/entity refactors | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 157 | Evaluate Bubble Card for mobile-friendly popups and compact controls | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 158 | Evaluate browser_mod for garage kiosk / wall display behavior after the display hardware exists | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 159 | Evaluate button-card for polished custom controls after core dashboard layout stabilizes | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 160 | Evaluate card-mod sparingly for styling once layout is stable | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 161 | Evaluate Scheduler Card / scheduler-component if native schedules feel awkward | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 162 | Evaluate Adaptive Lighting only if smart lighting enters project scope | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 163 | Revisit Bambu Lab / printer HACS integrations only after P1S details are confirmed and Bambuddy overlap is understood | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 167 | Keep Node-RED Tier 3/evaluate unless HA native automations become insufficient | `feasible-now` | Compatible with the present architecture; still requires normal change control |
| 168 | Evaluate AppDaemon only if Python automation apps are justified for non-critical logic | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 169 | Evaluate pyscript only for non-critical helper logic after a rollback plan exists | `feasible-with-prerequisites` | Documented dependency or decision gate must close first |
| 170 | Keep Claude/MCP or other AI automation as future advisory-only work; do not let it replace safety-critical HA/ESPHome/MQTT logic | `redesign-required` | No bounded interface, security model, or acceptance contract exists |

No item was classified `not-feasible`; several require redesign before feasibility can be responsibly asserted.
