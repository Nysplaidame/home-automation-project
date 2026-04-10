# HOME AUTOMATION SAFETY VAULT
# Combined Audit Report — All Findings, All Severities
# Merged from Sixth Audit (53 findings) + Prior Audit Unique Findings (23 additional)
# March 2026

---

## Summary

| Category | Findings |
|---|---|
| A — MQTT Port Inconsistencies | 10 findings |
| B — Router Phase Guide Issues | 17 findings |
| C — Cross-File Inconsistencies | 15 findings |
| D — Logic / Safety Issues | 7 findings |
| E — Outdated / Deprecated | 4 findings |
| F — Incompleteness / Missing | 12 findings |
| G — Minor Inconsistencies / Style | 8 findings |
| H — Security Gaps | 3 findings |
| **TOTAL** | **76 findings** |

| Severity | Count |
|---|---|
| CRITICAL (safety or data-loss risk) | 7 |
| HIGH (incorrect behaviour on deploy) | 22 |
| MEDIUM (inconsistency / confusion) | 29 |
| LOW (style / minor inaccuracy) | 18 |

---

## Executive Summary

This report consolidates findings from two independent deep-dive audits of the Home Automation Safety Vault conducted in March 2026. The first audit examined configuration files, setup guides, ESPHome YAMLs, and automation packages across 53 findings (categories A–G). The second audit reviewed the same scope and identified 40 findings, of which 23 were unique and not covered by the first audit. This document merges both into a single canonical reference of 76 findings.

Of the 76 findings, 7 are CRITICAL (including a fire emergency automation that activates the spray booth fan, a FIRE_RISK topic with no publisher, and a P1S serial placeholder that breaks all printer automations), 22 are HIGH (incorrect behaviour on deployment), 29 are MEDIUM, and 18 are LOW.

Fixes should be prioritised: CRITICAL → HIGH → MEDIUM → LOW, with Category D and H safety/security issues addressed before the router is deployed or any live ventilation control is activated.

---

## A — MQTT Port Inconsistencies
*Setup guides and inline configs that hard-code port 1883 without the two-stage migration note*

| ID | Severity | Summary |
|---|---|---|
| A1 | MEDIUM | ha_vm_setup_guide.md Phase 4.2: mosquitto test commands hard-coded to port 1883 — no two-stage TLS migration note. |
| A2 | MEDIUM | esphome_adoption_guide.md Phase 3: mosquitto_sub test command uses port 1883 without TLS migration note (Phase 1.2 has the note but Phase 3 does not). |
| A3 | MEDIUM | frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: MQTT_PORT=1883 with no two-stage note (vault version configs/frigate/docker-compose.yml has the note). |
| A4 | MEDIUM | frigate_vm_setup_guide.md Phase 3.4 inline config.yml: port: 1883 with no TLS migration note. |
| A5 | LOW | bambuddy_p1s_setup_guide.md Phase 2: nc verification commands use port 1883 without TLS note. |
| A6 | LOW | bambuddy_p1s_setup_guide.md Phase 5: MQTT publishing settings show port 1883 without TLS note. |
| A7 | LOW | bambuddy_p1s_setup_guide.md Quick Reference table: Firewall rule 2 references port 1883 — should reference 8883 with two-stage note. |
| A8 | MEDIUM | printairpipe-controller.yaml: port is already set to 8883 but the comment says 'switch to 1883 before TLS is set up' — backwards. |
| A9 | LOW | configuration.yaml comment references switching to 8883 after TLS but does not use the consistent two-stage language pattern established elsewhere. |
| A10 | HIGH | All ESPHome firmware YAMLs require mqtt_ca_cert secret and port 8883 TLS to connect at all. TLS is a Phase 6 activity; first hardware test is Phase 3–4. Every board will fail to connect on first boot. Pre-TLS variants (port 1883, no ca_certificate) are needed for initial bring-up and are not documented or provided. |

### Detailed Findings

**A1 [MEDIUM]** The ha_vm_setup_guide.md Phase 4.2 broker verification commands (mosquitto_sub/pub) use port 1883 unconditionally. Any operator following this guide after TLS migration will find the commands fail silently. The authoritative firewall-config.conf has a detailed two-stage note; the setup guide does not.
*Suggested fix:* Add the two-stage note used in firewall-config.conf immediately below the test commands: Stage 1 use 1883, Stage 2 switch to 8883 after TLS migration per ventsys_tls_implementation_guide.md.

**A2 [MEDIUM]** Phase 1.2 of esphome_adoption_guide.md correctly explains the two-stage MQTT approach, but the verification command in Phase 3 reverts to port 1883 with no cross-reference.
*Suggested fix:* Add an inline note after the Phase 3 test command: 'Use 1883 in Stage 1 (pre-TLS). After TLS migration, change this to 8883. See Phase 1.2 and ventsys_tls_implementation_guide.md Phase 4.'

**A3 [MEDIUM]** The inline docker-compose snippet in the setup guide and the authoritative vault file have diverged. The guide's snippet will be copied verbatim by anyone following the deployment steps; the important two-stage migration note is missing.
*Suggested fix:* Replace the inline docker-compose snippet in Phase 3.3 with the content from configs/frigate/docker-compose.yml.

**A4 [MEDIUM]** Same divergence as A3 but for the Frigate config.yml snippet. The guide shows port 1883 with no annotation, while the authoritative configs/frigate/config.yml has a TLS block and migration note.
*Suggested fix:* Sync the inline config.yml snippet in Phase 3.4 with the vault version, or add: 'Note: Change to 8883 and enable TLS block after running ventsys_tls_implementation_guide.md Phase 4.'

**A5 [LOW]** The nc checks used to verify MQTT broker connectivity reference port 1883 only. After TLS migration these commands will fail.
*Suggested fix:* Add: 'Pre-TLS: nc -zv 192.168.20.101 1883. Post-TLS: nc -zv 192.168.20.101 8883.'

**A6 [LOW]** Phase 5 shows the Bambuddy MQTT_PORT=1883 setting without explaining that it should be updated to 8883 after TLS migration.
*Suggested fix:* Add a callout: 'Stage 1 (pre-TLS): MQTT_PORT=1883. Stage 2 (after TLS migration): update to MQTT_PORT=8883 and restart Bambuddy.'

**A7 [LOW]** The Quick Reference table at the end of the guide is consulted during debugging. The port 1883 entry gives a false impression that 1883 is the permanent port.
*Suggested fix:* Update the table entry to show 8883 as the permanent port with a Stage 1/Stage 2 footnote.

**A8 [MEDIUM]** The comment reads as if 1883 is the TLS port and 8883 is the plain-text port, which is the opposite of reality.
*Suggested fix:* Replace the comment with: 'Stage 1 (pre-TLS): change port to 1883 for initial connectivity testing. Stage 2 (after TLS migration): revert to 8883. This file ships with 8883 as the post-migration default.'

**A9 [LOW]** Minor inconsistency in terminology. Using consistent language across all files makes the migration procedure easier to follow.
*Suggested fix:* Update the comment to match the 'Stage 1 / Stage 2' wording used in firewall-config.conf and docker-compose.yml.

**A10 [HIGH]** All current ESPHome YAML files (ventsys_fan_controller.yaml, ventsys_valve_controller.yaml, printairpipe-controller.yaml) use port: 8883 and ca_certificate: !secret mqtt_ca_cert. TLS infrastructure (CA, broker cert, device certs) is not created until Phase 6 of the setup guides. Hardware bring-up typically happens in Phase 3–4. A developer flashing and booting any ESP32 board before Phase 6 completion will see the device connect to WiFi then immediately fail MQTT with a TLS handshake error and no further indication of the cause. No pre-TLS firmware variants exist.
*Suggested fix:* Create pre-TLS variants of each firmware YAML (or add a substitution flag) that use port 1883 and omit ca_certificate. Document the two-phase firmware migration process in esphome_adoption_guide.md: flash pre-TLS on first boot, migrate to TLS variant after Phase 6.


---

## B — Router Phase Guide Issues
*Errors, broken references, and incorrect validation steps in the 8-phase router setup guides*

| ID | Severity | Summary |
|---|---|---|
| B1 | HIGH | phase_3_dhcp_configuration.md Step 3.12: creates reservations for 4 ventsys devices (.81-.84) but dhcp-config.conf only has 2 (.81 ventsys-fan-controller, .82 ventsys-valve-controller). Device count and naming are both wrong. |
| B2 | HIGH | phase_3_dhcp_configuration.md Step 3.12: missing DHCP reservations for printairpipe sensor boards at 192.168.50.31 (enc-fdm-sensors) and 192.168.50.32 (enc-sla-sensors). |
| B3 | HIGH | phase_4_firewall_implementation.md Step 4.2: references /tmp/corrected_firewall_config.sh — this file does not exist. Should reference configs/openwrt/firewall-config.conf. |
| B4 | MEDIUM | phase_4_firewall_implementation.md Step 4.5: validation checks for a named rule 'Block IoT Internet' — but IoT internet blocking is implemented via zone forward policy (REJECT default), not a named rule. Validation would fail on a correctly deployed system. |
| B5 | LOW | phase_5_wireless_configuration.md Success Criteria: 'Channel separation implemented: Non-overlapping 2.4GHz channels (1,6,11)' — factually incorrect. All 2.4GHz SSIDs share channel 6 on radio0 by design. |
| B6 | HIGH | phase_6_vpn_setup.md Step 6.2: creates a duplicate static interface 'vpn' pointing to device 'wg0'. This is not valid OpenWrt WireGuard configuration. |
| B7 | HIGH | phase_6_vpn_setup.md: entirely omits the step to assign the vpn_clients firewall zone to the wg0 interface, leaving VPN traffic unrouted through the firewall. |
| B8 | MEDIUM | phase_7_integration_testing.md Steps 7.5 and 7.7: uses 'iwlist scan' to validate SSID broadcasting — this scans for external networks, not your own configured SSIDs. |
| B9 | HIGH | phase_8_ventsys_readiness.md Step 8.1: creates CA infrastructure on the router at /etc/ventsys/ca/ — contradicts ventsys_tls_implementation_guide.md which places the CA on the HA VM at /config/ssl/ca/. Two independent CAs, neither trusted by any device. |
| B10 | HIGH | phase_8_ventsys_readiness.md Step 8.6: malformed bash — unclosed conditional block (missing 'fi' and closing echo), breaking shell syntax. |
| B11 | LOW | phase_2_network_infrastructure_complete.md Step 2.3: VLAN 50 note says 'no physical ports — WiFi only for security' but lan1:t (trunk to Proxmox) IS included for VLAN 50 in vlan-config.conf. |
| B12 | LOW | phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated on modern OpenWrt, may not be installed. |
| B13 | MEDIUM | proxmox_setup_guide.md: HAOS VM image version is hardcoded as 14.2. The guide should instruct the operator to fetch the current release from the HA GitHub releases API rather than pinning to a version that will be outdated. |
| B14 | LOW | proxmox_setup_guide.md: covers creating VM 100 (HAOS) in detail, but vm-setup.sh creates both VM 100 and VM 101 (Frigate/Bambuddy). A deployer following the guide sequentially may not realise VM 101 is handled by the script. |
| B15 | LOW | proxmox_setup_guide.md: backup storage target is the local pool with no note about available space requirements. HAOS + Frigate recordings can fill this quickly; space planning should be called out. |
| B16 | LOW | Proxmox subscription nag removal patch (if applied manually) is overwritten on every proxmox-widget-toolkit package upgrade. The setup guide applies the patch but does not note this — operators may be confused when the nag returns after an update. |
| B17 | LOW | VLAN 60 (Monitoring) has full DHCP scope and firewall rules configured in the OpenWrt configs but no VM, no setup guide, and no deployment timeline. Should either have a plan or be explicitly marked 'reserved — no deployment planned until intentional activation' to prevent accidental use. |

### Detailed Findings

**B1 [HIGH]** The phase guide and the authoritative dhcp-config.conf are misaligned: the guide reserves four IPs (.81 ventsys-fan-controller, .82 ventsys-sla-valve, .83 ventsys-fdm-valve, .84 ventsys-booth-valve) while the config only reserves two. Applying the guide will create ghost reservations.
*Suggested fix:* Align Step 3.12 with dhcp-config.conf: remove .83 and .84 reservations and rename .82 to 'ventsys-valve-controller'. Add a note that additional valve boards will require new reservations when hardware is built.

**B2 [HIGH]** The printairpipe-controller.yaml defines manual_ip for both sensor boards (.31 and .32) on VLAN 50. Without DHCP reservations, a lease could be issued to another device at those addresses, causing IP conflicts with fire safety sensor boards.
*Suggested fix:* Add DHCP reservations for both sensor boards to Step 3.12 and to configs/openwrt/dhcp-config.conf. MAC addresses will be XX:XX placeholders until hardware arrives.

**B3 [HIGH]** Applying Step 4.2 as written will fail immediately because the referenced file path is a throwaway temp path from an earlier editing session, not an actual vault file.
*Suggested fix:* Replace all references to /tmp/corrected_firewall_config.sh with the correct vault path: configs/openwrt/firewall-config.conf.

**B4 [MEDIUM]** The firewall-config.conf does include a named 'Block IoT Internet' rule as an explicit logged block. However the validation script treats its absence as a failure. The primary protection is the zone default REJECT.
*Suggested fix:* Rewrite the validation to check the zone forward policy rather than (or in addition to) the named rule, and clarify that the named rule is a supplementary logging rule.

**B5 [LOW]** The mac80211 architecture on OpenWrt does not support per-SSID channel assignment. The implementation is correct; the success criterion description is wrong.
*Suggested fix:* Change to: 'All 2.4GHz SSIDs share channel 6 on radio0 (mac80211 architecture — per-SSID channel assignment is not possible on this platform).'

**B6 [HIGH]** In OpenWrt, WireGuard interfaces are self-contained (interface 'wg0' with proto wireguard). Adding a second static interface pointing to wg0 as a device creates an invalid layered configuration. Note: vlan-config.conf already has this structure; the error is specific to the phase guide instructions.
*Suggested fix:* Remove the 'config interface vpn' block from Step 6.2. Update the firewall zone instruction to reference the 'wg0' interface directly.

**B7 [HIGH]** The vpn_clients zone is defined in firewall-config.conf with 'network=vpn', but Phase 6 never applies the zone assignment. Without this, WireGuard traffic bypasses all VPN firewall rules — the 'VPN to LAN Access', 'Block VPN to Management' rules are all dead.
*Suggested fix:* Add a step after WireGuard interface creation: assign network='wg0' to the vpn_clients firewall zone and commit.

**B8 [MEDIUM]** 'iwlist scan' performs a scan of the radio environment and lists nearby APs. It will show your own SSIDs only if the radio is also acting as a client.
*Suggested fix:* Replace with 'iwinfo <radioN> info' or 'uci show wireless | grep ssid'. For end-to-end SSID visibility testing, use a phone's WiFi scanner.

**B9 [HIGH]** Two conflicting CA setups: Phase 8 runs openssl commands on the router with a different openssl.cnf structure from ventsys_tls_implementation_guide.md Phase 3. If both guides are followed, two independent CAs exist and neither ESPHome device will trust the MQTT broker certificate. The HA VM location is the correct one.
*Suggested fix:* Remove the CA creation steps from Phase 8. Replace with a note: 'CA infrastructure is created on the HA VM — see ventsys_tls_implementation_guide.md Phase 3. This phase only validates network readiness for TLS.'

**B10 [HIGH]** The script near the end of Phase 8 has an if/then block that is never closed. Executing this step will produce 'syntax error: unexpected end of file'.
*Suggested fix:* Close the conditional block by adding the missing 'fi' statement and the closing echo line. Validate the complete script with 'bash -n' before committing.

**B11 [LOW]** The trunk to Proxmox is necessary and correct — it allows the HA VM to communicate with IoT devices on VLAN 50. The note creates confusion and may cause an operator to incorrectly remove the trunk.
*Suggested fix:* Change the note to: 'VLAN 50 has no direct-access physical ports (WiFi only for IoT devices). The lan1:t trunk to Proxmox is retained so the HA VM can route to VLAN 50.'

**B12 [LOW]** 'brctl' is from the bridge-utils package which is not installed by default on modern OpenWrt (using DSA).
*Suggested fix:* Replace 'brctl show' with 'bridge vlan show' and 'bridge link show'.

**B13 [MEDIUM]** Hardcoding a version number in a setup guide means every deployment after the next HA release uses an outdated image. HA releases minor versions frequently.
*Suggested fix:* Replace the hardcoded version with: 'curl -s https://api.github.com/repos/home-assistant/operating-system/releases/latest | grep tag_name' and instruct operators to use the result.

**B14 [LOW]** The vm-setup.sh script creates both VM 100 and VM 101. The guide's omission of VM 101 creation may cause confusion during the Frigate deployment phase when the VM is expected to already exist.
*Suggested fix:* Add a note to the proxmox_setup_guide.md: 'vm-setup.sh creates both VM 100 (HAOS) and VM 101 (Frigate/Bambuddy). Review vm-setup.sh before running to confirm VM 101 settings match your hardware.'

**B15 [LOW]** HAOS disk image is typically 32GB, Frigate recordings can accumulate rapidly at 4 cameras × 1080p. No guidance is given on local pool capacity requirements.
*Suggested fix:* Add a storage planning note: 'Recommended: 500GB+ free on local pool before deployment. Frigate recording retention should be configured immediately after Frigate VM creation.'

**B16 [LOW]** The subscription nag will return after every update to the proxmox-widget-toolkit package. Operators who applied the patch will be confused when it reappears.
*Suggested fix:* Add a note: 'This patch is overwritten on proxmox-widget-toolkit upgrades. Consider using the official Proxmox community scripts or an apt hook to reapply after updates.'

**B17 [LOW]** VLAN 60 exists in configs and has firewall rules but no deployment plan. Any device accidentally placed on VLAN 60 would have unintended network access based on those rules.
*Suggested fix:* Add a comment to vlan-config.conf and firewall-config.conf VLAN 60 sections: 'RESERVED — No devices deployed. Do not use until monitoring VM and tooling are planned and documented.'


---

## C — Cross-File Inconsistencies
*Conflicts, naming mismatches, and divergences between authoritative config files and their referencing guides*

| ID | Severity | Summary |
|---|---|---|
| C1 | MEDIUM | dhcp-config.conf names the valve controller 'ventsys-valve-controller' (.82) but phase_3 guide names it 'ventsys-sla-valve' (.82). Same IP, different hostname. |
| C2 | MEDIUM | frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Frigate service specifies both 'network_mode: host' AND explicit 'ports:' mappings — redundant and misleading. |
| C3 | MEDIUM | frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Bambuddy service sets MQTT_PORT=1883 without the two-stage migration note present in configs/frigate/docker-compose.yml. |
| C4 | HIGH | bambuddy_p1s_setup_guide.md Phase 6.4: references automations 'p1s_ventsys_fdm_start' and 'p1s_ventsys_fdm_stop' which do not exist in bambuddy_p1s_package.yaml or automations.yaml. |
| C5 | HIGH | ventsys_ha_package.yaml: Booth Valve entity uses command_topic 'ventsys/booth/valve/control' — no ESPHome firmware publishes to this topic. Creates a false sense of control for a safety-related valve. |
| C6 | HIGH | ventsys_ha_package.yaml: Booth Risk sensor subscribes to 'ventsys/booth/risk/state' — no ESPHome firmware publishes to this topic. A persistently unavailable sensor may be silently assumed safe. |
| C7 | MEDIUM | ventsys_ha_optional.yaml: T-inlet, T-downstream number entities and a pressure setpoint reference MQTT topics with no corresponding ESPHome firmware. Planned but unimplemented. |
| C8 | MEDIUM | health_check.sh: only monitors fan (.81) and valve (.82) controllers — printairpipe sensor boards at .31 and .32 are not monitored. Coverage gap for fire safety sensors. |
| C9 | LOW | health_check.sh: P1S check uses port 8883 (P1S_PORT=8883) for a TCP connect test — this is the printer's own MQTT TLS port and may succeed even if the printer is malfunctioning. |
| C10 | LOW | ha_vm_setup_guide.md 'Next steps' section: lists ESPHome adoption, MQTT TLS, Frigate VM, NAS integration — omits Bambuddy/P1S setup guide reference. |
| C11 | LOW | bambuddy_p1s_package.yaml header comment: 'Bambuddy MQTT publishing configured to 192.168.20.101:1883' — should reflect two-stage port approach. |
| C12 | MEDIUM | configs/frigate/docker-compose.yml and configs/frigate/config.yml use unpinned image tags (Frigate: 'stable', Bambuddy: 'latest'). A container restart after a background image pull can silently update to a breaking version. |
| C13 | LOW | printairpipe-controller.yaml publishes humidity data to ventsys/{enc}/humidity on every sensor update cycle. No HA sensor entity subscribes to this topic in ventsys_ha_package.yaml. The data is published and immediately discarded. |
| C14 | LOW | configuration.yaml comment references Frigate API port 5000. Frigate 0.12+ changed the default API port to 5000 but older versions used 8080 and some deployments run both. The comment should reference the actual value in configs/frigate/config.yml rather than hardcoding 5000. |
| C15 | LOW | ventsys_phase1_foundation.md references sensor boards at 192.168.50.31, .32, and .33. Only .31 (FDM) and .32 (SLA) are defined anywhere else. .33 appears to be a copy-paste artefact with no corresponding hardware, YAML, or DHCP entry. |

### Detailed Findings

**C1 [MEDIUM]** dhcp-config.conf is the authoritative DHCP config. The phase guide uses a different hostname for the same device, which means the DNS name assigned will depend on which file was followed.
*Suggested fix:* Standardise all references to the hostname in dhcp-config.conf: 'ventsys-valve-controller'. Update phase_3 step 3.12 to match.

**C2 [MEDIUM]** With host networking, the container shares the host's network stack directly. The 'ports:' directive is silently ignored by Docker in host mode. The redundant ports block may confuse an operator who tries to add a firewall rule based on the ports list.
*Suggested fix:* Remove the 'ports:' block from the Frigate service definition in the inline snippet, and add a comment: 'network_mode: host — port mappings are ignored; Frigate is accessible on all host IPs directly.'

**C3 [MEDIUM]** The inline snippet and the vault file have diverged. This is listed separately from A3 because it affects the Bambuddy portion of the compose file specifically.
*Suggested fix:* Sync the Bambuddy service block in the inline snippet with the vault docker-compose.yml, including the Stage 1/Stage 2 migration comment.

**C4 [HIGH]** Phase 6.4 describes VentSys FDM mode being automatically activated when a P1S print starts. The automations it references have never been created. The package only has p1s_print_started/completed/failed triggered by MQTT topics.
*Suggested fix:* Either implement the two automations or add a clear TODO note in Phase 6.4 marking this as unimplemented.

**C5 [HIGH]** The HA package configures a Booth Valve control entity. Sending a command will have no effect — the message will publish to MQTT but no device is subscribed. This creates a false sense of control for a safety-related valve.
*Suggested fix:* Add a comment to the Booth Valve entity: 'UNIMPLEMENTED — no ESPHome firmware currently handles this topic. Do not rely on this entity for safety control.' Add to TO-DO.md Phase 3.

**C6 [HIGH]** The Booth Risk sensor entity will always show 'unknown' or 'unavailable'. For fire safety monitoring, a persistently unavailable sensor is worse than no sensor — it may be silently assumed safe.
*Suggested fix:* Add a comment matching C5. Additionally, consider adding an availability check automation that alerts if this sensor remains unavailable when booth printing mode is active.

**C7 [MEDIUM]** The optional YAML contains entities that look functional but have no hardware or firmware backing them. Unlike C5/C6, these are in the 'optional' file, but the file should clearly mark these as future/unimplemented.
*Suggested fix:* Add a header comment to ventsys_ha_optional.yaml: 'SECTION: PLANNED FEATURES — entities below have no firmware implementation. Do not load into HA production until ESPHome configs are created.'

**C8 [MEDIUM]** The sensor boards (enc-fdm-sensors and enc-sla-sensors) are the primary smoke/VOC/temperature monitoring devices. If they go offline, the health check will show all green while the fire safety system has lost its primary input.
*Suggested fix:* Add health check entries for 192.168.50.31 and 192.168.50.32. Consider adding a check that verifies these devices are actively publishing (last seen < 5 minutes) rather than just TCP-reachable.

**C9 [LOW]** A TCP connect to port 8883 only verifies that the printer's MQTT TLS listener is accepting connections. The printer could be in an error state and the health check would still show green.
*Suggested fix:* Replace the TCP port check with an ICMP ping. If MQTT status monitoring is desired, add a separate check that subscribes to the Bambuddy MQTT topic and verifies a recent heartbeat.

**C10 [LOW]** The Next Steps section is used by operators to know what to tackle after HA VM deployment. Bambuddy/P1S integration is a significant step not listed.
*Suggested fix:* Add 'Bambuddy P1S printer integration — follow scripts/setup/printers/bambuddy_p1s_setup_guide.md' to the Next Steps list.

**C11 [LOW]** The header comment becomes stale after TLS migration and may confuse future debugging.
*Suggested fix:* Update: 'Bambuddy MQTT: Stage 1 (pre-TLS) port 1883, Stage 2 (post-TLS migration) port 8883. Current deployment port should match docker-compose.yml MQTT_PORT.'

**C12 [MEDIUM]** Using unpinned image tags means a container restart after a background image pull can break the running system with no warning. 'stable' for Frigate and 'latest' for Bambuddy are both risky for a 24/7 safety system.
*Suggested fix:* Pin both images to specific version tags (e.g. frigate:0.14.1, bambuddy:1.2.0). Create a documented procedure for intentional upgrades with a test step before restarting.

**C13 [LOW]** Humidity is published by the ESP32 sensor boards but never consumed anywhere. This is potentially useful data (SLA resin curing is humidity-sensitive) that is currently silently discarded.
*Suggested fix:* Add HA sensor entities for FDM and SLA humidity to ventsys_ha_package.yaml, subscribing to ventsys/fdm/humidity and ventsys/sla/humidity.

**C14 [LOW]** Port references in comments should match the actual deployed configuration, not a different file.
*Suggested fix:* Update the comment to reference the value in configs/frigate/config.yml, or remove the port reference from the comment and note 'see configs/frigate/config.yml for port.'

**C15 [LOW]** A phantom sensor board reference creates confusion during hardware planning — is there a third enclosure? Is this a typo?
*Suggested fix:* Remove the .33 reference from ventsys_phase1_foundation.md and add a note: 'Two sensor boards planned: .31 (FDM) and .32 (SLA). No third enclosure currently planned.'


---

## D — Logic / Safety Issues
*Automation logic errors and missing safety controls — includes CRITICAL findings*

| ID | Severity | Summary |
|---|---|---|
| D1 | CRITICAL | automations.yaml fire_detection_emergency: calls script.ventsys_mode_purge which opens ALL ventilation paths including the spray booth fan. Activating the spray booth fan during a fire event is unsafe — it draws air across the flame and accelerates combustion. |
| D2 | CRITICAL | ventsys_ha_scripts.yaml: no mode script resets other active paths before switching. Mode transitions are not atomic — switching modes can leave multiple paths open simultaneously. |
| D3 | HIGH | ventsys_ha_scripts.yaml ventsys_mode_booth_seal: only closes main-2 and spray fan — does not close main-1. If booth mode left main-1 open, booth_seal leaves it open, creating an incomplete seal in a solvent spray booth. |
| D4 | HIGH | No boot/startup script to initialise VentSys to a known safe state when HA restarts. After restart, MQTT-controlled entities show 'unknown', leaving physical hardware in its last commanded state. |
| D5 | CRITICAL | ventsys_ha_package.yaml: sensor.sla_risk, sensor.fdm_risk, and sensor.booth_risk subscribe to ventsys/{enc}/risk/state. No ESPHome YAML, Node-RED flow, or HA script publishes to these topics. The ventsys_fire_risk_cutoff automation can never trigger via this path. The primary fire-risk detection chain is a dead end. |
| D6 | HIGH | automations.yaml: the mqtt_reconnect_alert automation targets binary_sensor.mqtt_broker_online but the sensor in ventsys_ha_package.yaml has friendly name 'MQTT Broker', generating entity ID binary_sensor.mqtt_broker. The watchdog trigger will never fire. |
| D7 | HIGH | automations.yaml: fire_detection_emergency, fire_risk_cutoff, and high-temperature automations use switch.fdm_printer_plug and switch.sla_printer_plug to cut power to printers. These entity IDs depend on the smart plug integration and actual device naming at deployment time. HA logs a warning if they are wrong but the automation still completes — the power cutoff silently fails. For a fire safety action, silent failure is unacceptable. |

### Detailed Findings

**D1 [CRITICAL]** The fire emergency automation triggers ventsys_mode_purge via the failsafe mechanism. Purge mode opens all valve paths including the spray booth exhaust fan. In a fire scenario, running the spray booth fan can draw air across a flame, accelerate combustion, and spread combustion products. A fire-safe ventilation mode should exhaust enclosure smoke via the main inline fan only — not activate the spray booth fan.
*Suggested fix:* Create a new script 'script.ventsys_mode_fire_emergency' that opens FDM valve, SLA valve, and sets main inline fan to 100%, but explicitly does NOT activate the spray booth fan or booth valves. Replace the purge call in fire_detection_emergency with this new script. Add a comment explaining the safety rationale.

**D2 [CRITICAL]** Example: if SLA mode is active (main-1 open) and the operator switches to FDM mode, the SLA path remains open. With multiple paths open, fan pressure drops, effective ventilation per path is reduced, and the system is in an undefined state not covered by any mode's safety logic.
*Suggested fix:* Add a 'reset_all_paths' step at the beginning of every mode script that closes all valves and stops all fans before applying the new mode configuration. Consider creating a shared script 'script.ventsys_all_off' that all mode scripts call first.

**D3 [HIGH]** Booth mode opens both main-1 and main-2. The corresponding seal script only closes main-2 and the spray fan, leaving main-1 open. The system can then be in a user-perceived 'sealed' state while main-1 continues pulling air. For a solvent spray booth, incomplete sealing is a safety hazard.
*Suggested fix:* Add main-1 closure to the ventsys_mode_booth_seal script. As a belt-and-suspenders measure, the seal script should close ALL actuators regardless of assumed prior state (per D2 fix).

**D4 [HIGH]** If HA restarts unexpectedly (power cut, update, crash), all MQTT command topics are silent. The ESPHome devices retain their last commanded state. If a valve was open and the fan was running, they continue running with no mechanism to return to a defined safe state.
*Suggested fix:* Create an automation triggered on 'homeassistant' start event that calls script.ventsys_startup_safe_state. Include a 10-second delay after trigger to allow MQTT broker reconnection before publishing commands.

**D5 [CRITICAL]** The HA package defines three risk-state sensor entities. The ventsys_fire_risk_cutoff automation triggers when any of them reaches the value "FIRE_RISK". However, no code anywhere publishes to ventsys/sla/risk/state, ventsys/fdm/risk/state, or ventsys/booth/risk/state. The ESPHome firmware only publishes temperature, smoke, and IAQ values — it does not compute or publish a risk state string. The fire risk cutoff automation is structurally complete but functionally dead.
*Suggested fix:* Either (a) create an HA automation or template sensor that derives FIRE_RISK state from the raw sensor values (temperature > threshold AND smoke > threshold), or (b) add a lambda in the ESPHome firmware that publishes a risk state string based on local sensor conditions. Option (b) is preferred for fail-safe behaviour (acts even if HA is down). Document which approach is chosen and update the package accordingly.

**D6 [HIGH]** The entity ID is derived from the friendly name by HA, lowercased with spaces replaced by underscores: 'MQTT Broker' → binary_sensor.mqtt_broker. The automation targets binary_sensor.mqtt_broker_online, which does not exist. The MQTT broker watchdog will never trigger an alert regardless of broker state.
*Suggested fix:* Update the automation trigger entity_id to binary_sensor.mqtt_broker, matching the entity generated by the ventsys_ha_package.yaml binary_sensor definition.

**D7 [HIGH]** Entity IDs for smart plugs depend on the integration used (TP-Link Tapo, Shelly, ZHA, etc.) and the device names configured in the integration at deployment time. The automations assume switch.fdm_printer_plug and switch.sla_printer_plug will exist, but HA generates entity IDs from the device names set during integration setup. If the IDs are wrong, HA logs a single warning per automation run but the action is skipped silently.
*Suggested fix:* Add a deployment checklist item: 'Verify smart plug entity IDs after integration setup. Update automations.yaml switch entity IDs to match actual HA entities before enabling fire safety automations. Do not activate fire detection without confirming power cutoff works.'

---

## E — Outdated / Deprecated Elements
*Installation methods, commands, and protocols that have been superseded*

| ID | Severity | Summary |
|---|---|---|
| E1 | MEDIUM | ha_vm_setup_guide.md Phase 5.2: HACS installation uses 'wget -O - https://get.hacs.xyz \| bash -' — pipe-to-bash approach no longer recommended for HAOS. |
| E2 | MEDIUM | frigate_vm_setup_guide.md Phase 5.3: same outdated HACS installation command as E1. |
| E3 | LOW | phase_6_vpn_setup.md Step 6.5: WAN IP detection uses 'wget -qO- http://ipecho.net/plain' — unencrypted HTTP to a third-party service. |
| E4 | LOW | phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated and likely absent on modern OpenWrt DSA builds. (Duplicate of B12.) |

### Detailed Findings

**E1 [MEDIUM]** The pipe-to-bash method runs an arbitrary script from the internet with root privileges. HACS is now available as an official add-on through the HA Supervisor store, making the manual script unnecessary.
*Suggested fix:* Update Phase 5.2 to: 'Install HACS via HA UI: Settings → Add-ons → Add-on Store → search HACS. If not available as an add-on, refer to https://hacs.xyz/docs/installation for the current method.'

**E2 [MEDIUM]** The Frigate VM guide repeats the same problem for the Frigate/HA integration setup.
*Suggested fix:* Apply the same fix as E1 to frigate_vm_setup_guide.md Phase 5.3.

**E3 [LOW]** Using an unencrypted external service to discover the WAN IP is a privacy concern and unreliable.
*Suggested fix:* Replace with: 'uci get network.wan.ipaddr' for static IPs, or 'ip route get 1.1.1.1 | grep -o "src [0-9.]*" | cut -d" " -f2' for dynamic.

**E4 [LOW]** bridge-utils (which provides brctl) is not part of the default OpenWrt image for DSA-based hardware. (Same fix as B12.)
*Suggested fix:* Replace with 'bridge vlan show' and 'bridge link show'.


---

## F — Incompleteness / Missing Content
*Documented intentions, referenced procedures, and required configurations that do not yet exist*

| ID | Severity | Summary |
|---|---|---|
| F1 | CRITICAL | No dedicated fire/emergency ventilation mode script exists. The failsafe currently calls purge (which includes the spray booth fan). A fire-safe mode is required. (Related to D1.) |
| F2 | LOW | ventsys_ha_scripts.yaml: no script for 'FDM + SLA simultaneous' mode (both enclosures printing at once). |
| F3 | HIGH | esphome_adoption_guide.md: covers only fan (.81) and valve (.82) controllers — no guidance for adopting the printairpipe sensor boards (.31, .32) which require DS18B20 address scanning. |
| F4 | LOW | bambuddy_p1s_setup_guide.md Phase 5 TLS note: mentions Frigate's MQTT TLS config needs updating but provides no steps — only a note. Should cross-reference TLS guide Phase 5.0. |
| F5 | MEDIUM | ventsys_tls_implementation_guide.md Phase 5.0 (Bambuddy): does not include steps for updating Frigate's MQTT TLS configuration. Frigate config.yml has the TLS block but the guide never walks through applying it. |
| F6 | MEDIUM | phase_3_dhcp_configuration.md: missing DHCP reservations for printairpipe sensor boards (.31, .32) and for the additional valve boards that will be needed when hardware is built. |
| F7 | LOW | backup_strategy.md recovery runbook Step 4 references 'MAC update procedure in esphome_adoption_guide.md' — that guide does not contain a VM MAC update procedure. |
| F8 | CRITICAL | bambuddy_p1s_package.yaml: the literal string '<P1S_SERIAL>' appears in all 12 MQTT topic references (e.g. 'bambu/device/<P1S_SERIAL>/report'). No substitution is performed at load time. Every P1S sensor entity will show unavailable, every print start/complete/failed automation will never fire. This is a pre-deployment blocker that silently breaks the entire Bambuddy integration. |
| F9 | HIGH | VentSys architecture systemic gap: the software layer (HA package, scripts, dashboard) is designed for a 10-endpoint system (2 fans, 8 valve positions). Only 2 complete ESPHome firmware files exist (fan controller, one valve controller). The wiring reference documents 8 valve controller YAMLs as needed but not yet created. On deployment, 8 of 10 MQTT command topics will have no subscriber — every mode script will silently partially execute. |
| F10 | MEDIUM | No unified MQTT TLS migration checklist exists. The migration touches 6 files/services simultaneously: Frigate config.yml, Bambuddy docker-compose.yml MQTT_PORT, ESPHome secrets (ca_certificate), HA MQTT integration port, temp-1883 firewall rule removal, firewall-config.conf TEMP rule cleanup. Without a single-document checklist an operator is likely to miss one step and be left with a partially-migrated system. |
| F11 | LOW | No master secrets reference document exists. HA, ESPHome, Bambuddy, and Frigate each document their secrets requirements in inline comments scattered across multiple files. An operator populating secrets.yaml for the first time must read every file to find all required keys. |
| F12 | LOW | Router setup folder contains stale/duplicate files: 'router_setup_complete - Copy.md', 'openwrt_complete_config_phase_2.md', and 'openwrt_script_analysis.md'. These are working artefacts from earlier editing sessions that should be removed or archived. |

### Detailed Findings

**F1 [CRITICAL]** This is listed in both D (logic error) and F (missing content) because it involves both an incorrect automation and missing script code. The gap means there is currently no safe path for the fire emergency automation to follow.
*Suggested fix:* Create script.ventsys_mode_fire_emergency as described in D1. Add it to ventsys_ha_scripts.yaml, test it in simulation, and update the fire_detection_emergency automation to call it instead of purge.

**F2 [LOW]** The VentSys hardware supports both enclosures being ventilated simultaneously. There is no script for this mode, so an operator must manually set each entity — which is error-prone for a safety system.
*Suggested fix:* Create script.ventsys_mode_fdm_and_sla: opens FDM valve, SLA valve, closes booth paths, sets fan to 80%. Add to the dashboard as a mode button.

**F3 [HIGH]** The sensor boards require a specific adoption workflow: flash via USB with a placeholder DS18B20 address, boot, scan for actual addresses using the ESPHome serial console, then reflash with correct addresses. This process is not documented anywhere. An operator would not know to do this and would end up with incorrect or no temperature readings — the primary fire thermal detection would be non-functional.
*Suggested fix:* Add a Phase 4 to esphome_adoption_guide.md covering: (1) flash printairpipe-controller.yaml via USB, (2) boot and open serial monitor, (3) run DS18B20 scan to find actual addresses, (4) update the address substitution in the YAML, (5) OTA reflash, (6) verify temperature entities appear in HA.

**F4 [LOW]** The note reads 'Frigate config.yml will also need updating for TLS' without linking to where this is documented.
*Suggested fix:* Replace with: 'Frigate MQTT TLS update: see ventsys_tls_implementation_guide.md Phase 5.0, step "Note on Frigate MQTT".'

**F5 [MEDIUM]** The TLS guide focuses on ESPHome and Bambuddy. Frigate also connects to MQTT and will fail to connect after TLS migration if its own config.yml TLS settings are not updated. The TLS block exists in the vault file but there is no procedure for deploying it.
*Suggested fix:* Add a new sub-step to Phase 5.0: 'Update Frigate MQTT TLS: (1) Copy ca-cert.pem to Frigate VM, (2) Update configs/frigate/config.yml mqtt section with cafile path and port 8883, (3) restart Frigate with docker compose restart.'

**F6 [MEDIUM]** Covers the sensor board gap (also B2) and the additional valve boards. Reservations should be pre-planned even if hardware does not yet exist, to prevent address conflicts.
*Suggested fix:* Add placeholder reservations for sensor boards (.31, .32) and future valve boards (.83+) with XX:XX MAC placeholders and descriptive hostnames. Add a note cross-referencing TO-DO.md Phase 3.

**F7 [LOW]** The esphome_adoption_guide.md covers ESPHome device MACs but not Proxmox VM virtual NIC MACs. After a restore, VMs will have new MACs and DHCP reservations will no longer match.
*Suggested fix:* Update the backup runbook Step 4 reference: 'To update VM MAC addresses after restore: (1) Check new MACs in Proxmox hardware tab for VM 100 and 101, (2) Update dhcp-config.conf VM reservations, (3) Redeploy dhcp-config.conf to router.'

**F8 [CRITICAL]** The bambuddy_p1s_package.yaml file was written with '<P1S_SERIAL>' as a placeholder string. YAML does not perform any substitution on load — this literal string is used as part of the MQTT topic path. Mosquitto will subscribe to topics like 'bambu/device/<P1S_SERIAL>/report' which the printer never publishes to. Every sensor will show unavailable in HA and every print detection automation will be permanently inactive. This must be resolved before any P1S integration testing.
*Suggested fix:* Replace '<P1S_SERIAL>' with the actual printer serial number (visible on the printer label and in the Bambu Handy app). A deployment checklist item should require this substitution before activating the Bambuddy integration.

**F9 [HIGH]** The software layer is already topology-aware — the HA package, scripts, and dashboard are all written for the 10-endpoint system. The gap is 8 missing ESPHome firmware files. Each is a copy-paste-and-adjust job from ventsys_valve_controller.yaml (change 4 fields: name, IP, MQTT subscription topic, state feedback topic). Files needed: ventsys_fdm_valve_controller.yaml, ventsys_fdm_branch_controller.yaml, ventsys_fdm_360_controller.yaml, ventsys_sla_branch_controller.yaml, ventsys_sla_360_controller.yaml, ventsys_main_valve1_controller.yaml, ventsys_main_valve2_controller.yaml, ventsys_spray_fan_controller.yaml.
*Suggested fix:* Create all 8 firmware files from the valve controller template. Assign IPs (.83–.90 or similar), add DHCP reservations, and document GPIO assignments in ventsys_wiring_reference.md.

**F10 [MEDIUM]** A partially-migrated TLS state (some services on 8883, some still on 1883, temp firewall rules still open) is difficult to debug. The individual migration steps are spread across the TLS guide, firewall config notes, and ESPHome secrets — with no master checklist tying them together.
*Suggested fix:* Create ventsys_tls_migration_checklist.md with a sequential step-by-step checklist: CA creation → broker cert → device certs → Mosquitto TLS config → ESPHome firmware update → HA integration update → Bambuddy update → Frigate update → firewall temp rule removal → verification tests.

**F11 [LOW]** The secrets required span: wifi_ssid, wifi_pass, mqtt_user, mqtt_pass, mqtt_ca_cert, api_key, ota_password (ESPHome); MQTT credentials (Bambuddy env); HA long-lived token (dashboard); and various HA secrets. No single document lists them all.
*Suggested fix:* Create docs/secrets_reference.md listing every secret key, which file(s) require it, and where to find or generate it. Clearly mark which secrets are shared across multiple files.

**F12 [LOW]** Working artefacts left in the setup folder create ambiguity about which is the canonical file.
*Suggested fix:* Delete or archive 'router_setup_complete - Copy.md', 'openwrt_complete_config_phase_2.md', and 'openwrt_script_analysis.md'. Keep only the canonical phase-N files.


---

## G — Minor Inconsistencies / Style
*Small inaccuracies, outdated TODO comments, and terminology gaps*

| ID | Severity | Summary |
|---|---|---|
| G1 | LOW | ventsys_ha_package.yaml temperature sensors: unit_of_measurement is 'C' — should be '°C' for consistency with HA standards. |
| G2 | LOW | dhcp-config.conf: VLAN table at the top of the file omits VLAN 60 (Monitoring) and VLAN 70 (DMZ). |
| G3 | LOW | dhcp-config.conf: DNS domain entries only map 'router.home.local' to 192.168.1.1. Devices on other VLANs querying this name will get the wrong IP. |
| G4 | LOW | ventsys_ha_package.yaml contains comment: 'IMPORTANT: confirm topic names match printairpipe-controller.yaml when finalised' — this has been verified; the TODO should be marked resolved. |
| G5 | LOW | phase_5_wireless_configuration.md success criteria bullet about channel separation is factually wrong. (Duplicate of B5 in style category.) |
| G6 | LOW | backup_strategy.md Layer 5 GitHub section: contains the specific personal GitHub repo URL with no warning about sensitive config history in git. |
| G7 | LOW | vlan-config.conf and dhcp-config.conf contain Obsidian [[wikilink]] syntax inside UCI config comment blocks. These will render correctly in Obsidian but are non-standard in UCI files and could confuse scripts that parse comments. |
| G8 | LOW | ESPHome device names don't match DHCP hostnames for the same boards: the fan controller YAML uses 'ventsys-fan-ctrl' but DHCP reserves 'ventsys-fan-controller'; the valve controller uses 'ventsys-valve-ctrl' vs 'ventsys-valve-controller'. mDNS will broadcast the ESPHome name; DHCP assigns the reservation name — these will diverge. |

### Detailed Findings

**G1 [LOW]** Home Assistant uses '°C' as the standard unit string for Celsius. Using bare 'C' still works but will display differently on graphs and statistics tables.
*Suggested fix:* Replace all unit_of_measurement: "C" with unit_of_measurement: "°C" in ventsys_ha_package.yaml.

**G2 [LOW]** The documentation table lists VLANs 1, 10, 20, 30, 40, 50, and 99 but skips 60 and 70. Both are fully configured in vlan-config.conf and firewall-config.conf.
*Suggested fix:* Add VLAN 60 (Monitoring, 192.168.60.0/24) and VLAN 70 (DMZ, 192.168.70.0/24) to the table.

**G3 [LOW]** The router has a different IP on each VLAN (.1 on each subnet). A device on VLAN 50 querying 'router.home.local' will receive 192.168.1.1, which is not routable from VLAN 50.
*Suggested fix:* Either add per-VLAN router A records or add a comment explaining that 'router.home.local' resolves to the VLAN 1 address only and devices should use their gateway IP directly.

**G4 [LOW]** The topics have been cross-verified across audits and they match. The IMPORTANT comment creates unnecessary alarm.
*Suggested fix:* Replace with: '(Verified March 2026) Topic names confirmed consistent with printairpipe-controller.yaml.'

**G5 [LOW]** The mac80211 architecture does not support per-SSID channel assignment. The implementation is correct; the success criterion is wrong. (Same fix as B5.)
*Suggested fix:* Correct the success criterion wording to reflect the actual single-channel-per-radio architecture.

**G6 [LOW]** The repository may contain historical configs with placeholder secrets, commented-out credentials, or infrastructure details. A note about reviewing git history before making the repo public is prudent.
*Suggested fix:* Add a note: 'Warning: review git history before changing repo visibility. Ensure no plaintext secrets, real credentials, or sensitive network topology details are present in any commit. Use git-secrets or similar tooling.'

**G7 [LOW]** [[wikilink]] syntax inside UCI config comments is specific to Obsidian and has no meaning in the config file context. If the file is ever processed by a script that reads comments (e.g. for documentation generation or diff tooling), the brackets will be unexpected.
*Suggested fix:* Replace [[wikilink]] references with plain text descriptions or markdown-style links in a dedicated comments file rather than inline in UCI config.

**G8 [LOW]** mDNS will broadcast the ESPHome name (.local hostname). DHCP will assign the reservation hostname. These will diverge: the device responds to ventsys-fan-ctrl.local but DHCP DNS maps ventsys-fan-controller. Tools that rely on DNS name (health_check.sh, ESPHome dashboard) may use either, leading to inconsistency.
*Suggested fix:* Standardise on one name. Either shorten the DHCP reservations to match ESPHome names, or add -controller suffix to all ESPHome device names. Apply consistently across all boards.

---

## H — Security Gaps
*Firewall exposure and hardening issues not covered in other categories*

| ID | Severity | Summary |
|---|---|---|
| H1 | HIGH | firewall-config.conf: 'Allow DHCP Requests' and 'Allow Local DNS' rules use src='*' which includes the WAN zone. Port 53 accepting queries from WAN is a DNS amplification attack surface. |
| H2 | HIGH | firewall-config.conf: the 'SSH Rate Limit' rule allows SSH (port 22) from the WAN zone. WireGuard VPN is already configured for remote access — WAN-exposed SSH is unnecessary attack surface. |
| H3 | HIGH | configuration.yaml: ip_ban_enabled and login_attempts_threshold are commented out. HA's built-in brute-force protection is disabled. Any device that can reach port 8123 can attempt unlimited login attempts. |

### Detailed Findings

**H1 [HIGH]** The 'Allow Local DNS' rule permits UDP/TCP port 53 from any source zone including WAN. A DNS server open to the internet can be abused for DNS amplification DDoS attacks — small forged-source queries return large responses to a third-party victim. The rule should be scoped to internal zones only.
*Suggested fix:* Change src='*' to src='lan' (or list internal zones explicitly: lan, management, automation, iot_sensors, etc.) on both the DHCP and DNS rules. DHCP requests from WAN are also invalid — DHCP is link-local only.

**H2 [HIGH]** SSH over WAN with a rate-limit rule is not a robust security posture. Rate limiting reduces brute-force speed but does not eliminate it. If the SSH daemon has any vulnerability or a weak credential exists, WAN exposure is an attack vector. The vpn_clients zone already provides authenticated remote access via WireGuard.
*Suggested fix:* Remove the 'SSH Rate Limit' WAN rule from firewall-config.conf. Add an SSH allow rule from the management or vpn_clients zone only. If emergency WAN access is needed, use a WireGuard connection first.

**H3 [HIGH]** HA's ip_ban mechanism blocks an IP after a configurable number of failed login attempts. With this disabled, any device that can reach port 8123 (including devices on VLANs with HA access, or VPN clients) can attempt unlimited credential guesses. The feature is disabled by default in some HA versions but the configuration exists and should be explicitly enabled for a security-conscious deployment.
*Suggested fix:* Uncomment and set: ip_ban_enabled: true and login_attempts_threshold: 5 in configuration.yaml. Consider also enabling HA's multi-factor authentication and restricting port 8123 access in the firewall to trusted VLANs only.


---

## Fix Priority Matrix
*Recommended fix order. Address CRITICAL and HIGH items before router deployment or live use.*

| ID | Severity | Action Required | Affects Deployment? |
|---|---|---|---|
| D1 | CRITICAL | Create script.ventsys_mode_fire_emergency (no spray fan); update fire_detection_emergency automation | YES — safety |
| D5 | CRITICAL | Implement FIRE_RISK publisher (ESPHome firmware or HA template) — current chain is a dead end | YES — safety |
| F1 | CRITICAL | Implement fire-safe ventilation script (related to D1) | YES — safety |
| D2 | CRITICAL | Add 'reset all paths' to every mode script for atomic transitions | YES — safety |
| F8 | CRITICAL | Replace '<P1S_SERIAL>' placeholder in bambuddy_p1s_package.yaml before Bambuddy deployment | YES — integration |
| A10 | HIGH | Create pre-TLS ESPHome firmware variants for initial hardware bring-up | YES — hardware ops |
| B9 | HIGH | Remove conflicting CA creation from Phase 8; CA belongs on HA VM only | YES — breaks TLS |
| B10 | HIGH | Fix malformed bash in phase_8 Step 8.6 (missing fi) | YES — script fails |
| B3 | HIGH | Fix /tmp path reference in phase_4 Step 4.2 | YES — script fails |
| B6 | HIGH | Fix invalid WireGuard interface layering in phase_6 | YES — VPN broken |
| B7 | HIGH | Add missing vpn_clients zone assignment in phase_6 | YES — VPN rules dead |
| B1 | HIGH | Align phase_3 DHCP reservations with dhcp-config.conf (count + naming) | YES — DHCP conflicts |
| B2 | HIGH | Add sensor board DHCP reservations (.31, .32) to phase_3 and dhcp-config.conf | YES — IP conflicts |
| H1 | HIGH | Restrict Allow Local DNS and Allow DHCP Requests to internal zones only | YES — DNS amplification risk |
| H2 | HIGH | Remove SSH WAN exposure; restrict to management/VPN zone only | YES — security |
| H3 | HIGH | Enable ip_ban_enabled and login_attempts_threshold in configuration.yaml | YES — pre-go-live |
| C4 | HIGH | Implement or clearly mark as TODO the p1s_ventsys_fdm_start/stop automations | PARTIAL |
| C5 | HIGH | Mark Booth Valve entity as UNIMPLEMENTED in HA package | YES — false control |
| C6 | HIGH | Mark Booth Risk sensor as UNIMPLEMENTED in HA package | YES — false safety UI |
| D3 | HIGH | Fix ventsys_mode_booth_seal to also close main-1 | YES — safety |
| D4 | HIGH | Create HA startup automation to initialise VentSys to a known safe state | YES — safety |
| D6 | HIGH | Fix mqtt_reconnect_alert automation entity ID (binary_sensor.mqtt_broker) | YES — watchdog dead |
| D7 | HIGH | Verify and hardcode smart plug entity IDs; add deployment checklist item | YES — silent failure |
| F3 | HIGH | Write sensor board adoption procedure in esphome_adoption_guide.md | YES — hardware ops |
| F9 | HIGH | Create 8 missing ESPHome firmware YAMLs for valve/fan controllers | YES — hardware ops |
| A1 | MEDIUM | Add two-stage MQTT note to ha_vm_setup_guide Phase 4.2 test commands | MEDIUM |
| A2 | MEDIUM | Add two-stage note to esphome_adoption_guide Phase 3 | MEDIUM |
| A3 | MEDIUM | Sync frigate_vm_setup_guide Phase 3.3 inline docker-compose with vault version | MEDIUM |
| A4 | MEDIUM | Sync frigate_vm_setup_guide Phase 3.4 inline config.yml with vault version | MEDIUM |
| A8 | MEDIUM | Fix backwards comment in printairpipe-controller.yaml re: port 1883/8883 | MEDIUM |
| B4 | MEDIUM | Fix phase_4 validation to check zone policy, not named rule only | LOW |
| B8 | MEDIUM | Replace iwlist scan in phase_7 with iwinfo / uci show wireless | LOW |
| B13 | MEDIUM | Remove hardcoded HAOS version 14.2; use GitHub API to fetch latest | MEDIUM |
| C2 | MEDIUM | Remove redundant 'ports:' from host-networked Frigate in setup guide | LOW |
| C3 | MEDIUM | Sync Bambuddy service block in frigate_vm_setup_guide with vault version | MEDIUM |
| C7 | MEDIUM | Add 'PLANNED FEATURES' header to ventsys_ha_optional.yaml | LOW |
| C8 | MEDIUM | Add sensor boards .31 and .32 to health_check.sh | MEDIUM |
| C12 | MEDIUM | Pin Frigate and Bambuddy Docker image versions | MEDIUM |
| E1 | MEDIUM | Update HACS install method in ha_vm_setup_guide | LOW |
| E2 | MEDIUM | Update HACS install method in frigate_vm_setup_guide | LOW |
| F5 | MEDIUM | Write Frigate MQTT TLS update steps in ventsys_tls_implementation_guide | MEDIUM |
| F10 | MEDIUM | Create unified MQTT TLS migration checklist document | MEDIUM |
| A5 | LOW | Add TLS migration note to bambuddy_p1s_setup_guide Phase 2 nc commands | LOW |
| A6 | LOW | Add Stage 1/Stage 2 callout to bambuddy_p1s_setup_guide Phase 5 | LOW |
| A7 | LOW | Update Quick Reference table port 1883 entry to 8883 with footnote | LOW |
| A9 | LOW | Align configuration.yaml comment with Stage 1/Stage 2 terminology | LOW |
| B5 | LOW | Fix phase_5 success criterion: single-channel architecture description | LOW |
| B11 | LOW | Clarify VLAN 50 physical port note re: lan1:t trunk to Proxmox | LOW |
| B12 | LOW | Replace brctl show with bridge vlan show in phase_2 | LOW |
| B14 | LOW | Add note to proxmox_setup_guide re: VM 101 created by vm-setup.sh | LOW |
| B15 | LOW | Add storage space planning note to proxmox_setup_guide | LOW |
| B16 | LOW | Add note about Proxmox subscription nag patch being overwritten on upgrade | LOW |
| B17 | LOW | Mark VLAN 60 as reserved/no-deployment in config comments | LOW |
| C1 | MEDIUM | Standardise valve controller hostname to 'ventsys-valve-controller' everywhere | LOW |
| C9 | LOW | Replace P1S TCP port check in health_check.sh with ping | LOW |
| C10 | LOW | Add Bambuddy/P1S guide to ha_vm_setup_guide Next Steps section | LOW |
| C11 | LOW | Update bambuddy_p1s_package.yaml header comment with two-stage port | LOW |
| C13 | LOW | Add FDM/SLA humidity sensor entities to ventsys_ha_package.yaml | LOW |
| C14 | LOW | Verify Frigate API port reference in configuration.yaml comment | LOW |
| C15 | LOW | Remove phantom sensor board .33 reference from ventsys_phase1_foundation.md | LOW |
| E3 | LOW | Replace WAN IP wget command with local router query | LOW |
| E4 | LOW | Replace brctl show (same as B12) | LOW |
| F2 | LOW | Create ventsys_mode_fdm_and_sla simultaneous-mode script | LOW |
| F4 | LOW | Add TLS guide cross-reference to bambuddy_p1s_setup_guide Phase 5 note | LOW |
| F6 | MEDIUM | Add placeholder DHCP reservations for all future valve boards | MEDIUM |
| F7 | LOW | Update backup runbook Step 4 cross-reference to correct procedure | LOW |
| F11 | LOW | Create docs/secrets_reference.md with all secret keys listed | LOW |
| F12 | LOW | Delete stale duplicate files from router setup folder | LOW |
| G1 | LOW | Fix unit_of_measurement: "C" → "°C" in ventsys_ha_package.yaml | LOW |
| G2 | LOW | Add VLAN 60 and 70 to dhcp-config.conf architecture table | LOW |
| G3 | LOW | Clarify router.home.local DNS entry scope or add per-VLAN records | LOW |
| G4 | LOW | Mark verified TODO comment as resolved in ventsys_ha_package.yaml | LOW |
| G5 | LOW | Correct channel separation success criterion in phase_5 (same as B5) | LOW |
| G6 | LOW | Add git history warning to backup_strategy.md GitHub section | LOW |
| G7 | LOW | Replace Obsidian wikilinks in UCI config comment blocks with plain text | LOW |
| G8 | LOW | Standardise ESPHome device names to match DHCP reservation hostnames | LOW |

