# VentSys identity monitor and temporary MQTT logging

November10 2026: identity checks and continuous MQTT capture run on Proxmox monitoring VM102 (`192.168.60.10`), migrated from the interim VM103 installation at08:31UTC after closing the required access gaps. VM103 dedicated program, service, account, credentials, SSH key, state and capture files were removed after verification; evidence was transferred to VM102.

## Server operation

Enabled `ventsys-monitor.service` runs as unprivileged `ventsys-monitor`, starts on boot and restarts on failure. Source/roster/unit: `main/tools/ventsys-monitor/`. Deployed program: `/opt/ventsys-monitor/monitor.py`; dependency: Debian `python3-paho-mqtt` (shared PyYAML on the former host was not removed).

Protected `/etc/ventsys-monitor/config.json` contains approved roster, existing MQTT credentials, HA token, CA and ntfy publisher credentials. Never commit or print it. Update its roster and tracked `roster.json` deliberately when changing hardware. The existing HA token is administrative, although this program only reads `/api/states`; no new narrowly scoped HA token was created.

Continuous TLS MQTT subscription to `esphome/discover/#` evaluates each discovery message and alerts on conflicting/unknown name-MAC-IP combinations. Every five minutes restricted SSH reads HA's ESPHome host roster, and HTTPS reads E2 uptime/maintenance. E2 unavailability outside maintenance and monitoring access failures require two checks. Other board dropout alerts remain in HA. This service never commands actuators, repairs configuration or clears latches.

Alerts/recoveries use authenticated ntfy topic `monitoring`; healthy checks produce no notifications. Deduplication persists in `/var/lib/ventsys-monitor/state.json`; internal `status.json` records check time and health. The desktop Codex heartbeat is paused; its collector/SSH child stopped after server validation.

Dedicated SSH key is restricted to source VM102 and forced `snapshot` or `logs` commands only, without forwarding. HA script `/config/ventsys-monitor-readonly.sh` is tracked as `ha-readonly.sh`. Public key marker `ventsys-monitor-vm102` is persisted in SSH app options and current authorized_keys. VM102 uses the verified existing HA host key. The prior VM103 key was revoked from both HA authorized_keys and persistent SSH app options.

TLS verifies CA, certificate chain and hostname. Python3.13 strict X509 mode is disabled for this context because the existing local CA lacks keyUsage; verification itself is enabled. Remove this compatibility setting after planned CA migration.

## Temporary diagnostics and limits

Mosquitto `core_mosquitto` temporarily uses log types error, warning, notice, information and debug; authentication-plugin debug remains off. Prior protected options backup on HA: `/share/ventsys-mqtt-temporary/options-before.json` (contains credentials). Prior `log_type` and `log_dest` were both `[]`; only log_type changed.

The restricted SSH broker stream preserves discovery packet lines and client connection/disconnection records. Correlate `Received PUBLISH from CLIENT` in `broker.jsonl` with connection address and `discovery.jsonl` payload/time. Retained replay establishes neither original publication time nor publisher. Connections preceding the log window may require a reconnect for an address correlation.

Logs in `/var/lib/ventsys-monitor/`: broker, discovery and health, each5MiB plus five backups, about90MiB total maximum. Selected earlier desktop capture is in `desktop-history/`, outside Git. Broker stdout debug also increases HA journal traffic; the collector limits do not bound HA's own journal. No automatic expiry: revert after evidence capture and cause verification, or when owner ends investigation.

Verified on server: correct HA host roster, E2 telemetry, CA-verified MQTT/HTTPS, restricted broker stream and two correct retained records. Three tests cover conflicting/unknown identity, transient conflict then correction, deduplication, retry, restart persistence and recovery. Systemd unit validated; authenticated HTTPS ntfy accepted a labelled migration test. Phone reception remains unverified. Enabled boot startup was checked; no VM reboot was performed. A VM102 outage cannot be reported by this service itself; HA external monitoring is separate. ntfy remains on VM103, so a VM103/ntfy outage also prevents delivery through this route.

## Revert temporary capture while retaining identity monitor

1. Restore Mosquitto `log_type: []`, preserving all other current options; restart app (brief reconnect expected).
2. Set `capture_broker` and `capture_payloads` false in protected server config; restart `ventsys-monitor.service`. Continuous discovery evaluation and periodic checks continue without diagnostic capture.
3. Preserve selected evidence if needed, remove unneeded captures and protected HA options backup, and close the temporary-capture task/current live state.

To stop the entire monitor: disable/stop its systemd service. Remove only its marked key from HA current authorized_keys and SSH app options, then remove its endpoint and server secrets when no longer needed. Keep the desktop heartbeat paused.

Migration acceptance: enabled/active unit on VM102, healthy MQTT and broker streams, no active identity incidents, fresh HA roster/E2 checks, three tests passed on VM102, and authenticated HTTPS ntfy migration test accepted. State/evidence were transferred over SSH without writing secrets to the vault. Old-host dedicated Paho dependency removed; shared PyYAML retained because cloud-init/netplan require it.
