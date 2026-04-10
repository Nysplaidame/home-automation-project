# HOME AUTOMATION SAFETY VAULT
## Sixth Audit — Deep-Dive Combined Analysis Report
### March 2026

> This report consolidates findings from two independent deep-dive audits conducted in March 2026.
> Findings present in only one audit are noted where relevant.

---

| Category | Findings |
|---|---|
| A — MQTT Port Inconsistencies | 9 findings |
| B — Router Phase Guide Issues | 12 findings |
| C — Cross-File Inconsistencies | 11 findings |
| D — Logic / Safety Issues | 4 findings |
| E — Outdated / Deprecated | 4 findings |
| F — Incompleteness / Missing | 7 findings |
| G — Minor Inconsistencies / Style | 6 findings |
| **TOTAL** | **53 findings** |

| Severity | Count |
|---|---|
| CRITICAL (safety or data-loss risk) | 4 |
| HIGH (incorrect behaviour on deploy) | 16 |
| MEDIUM (inconsistency / confusion) | 22 |
| LOW (style / minor inaccuracy) | 11 |

---

## Executive Summary

This report presents the findings of the sixth audit of the Home Automation Safety Vault, conducted in March 2026. The audit examined every configuration file, setup guide, ESPHome YAML, and automation package in the vault, focusing on compatibility issues, outdated software and commands, internal contradictions, incompleteness, and safety logic gaps.

53 distinct findings were identified across 7 categories. Of these, 4 are rated CRITICAL (including one finding — D1 — where the fire emergency automation activates the spray booth fan, which is unsafe during a fire event), 16 are HIGH severity (incorrect behaviour on deployment), 22 are MEDIUM, and 11 are LOW.

The most important finding categories are:

- **Category D (Safety Logic):** Two CRITICAL findings — the fire emergency mode calls purge (which runs the spray booth fan), and mode transitions are not atomic, meaning switching ventilation modes can leave multiple paths open simultaneously.
- **Category B (Router Phase Guides):** Eight HIGH-severity issues in the 8-phase router setup guides, including a shell syntax error, a WireGuard zone assignment that is completely missing, and conflicting CA setups between Phase 8 and the TLS guide.
- **Category C (Cross-File):** The Booth Valve and Booth Risk sensor entities in the HA package reference MQTT topics that no ESPHome firmware publishes to, creating false UI controls for safety-critical actuators.
- **Category F (Missing Content):** No fire-safe emergency ventilation mode script exists, the sensor board adoption procedure is entirely undocumented, and the Frigate TLS migration procedure is referenced but never written.

All findings include a suggested fix. Fixes should be prioritised in order: CRITICAL → HIGH → MEDIUM → LOW, with Category D safety issues addressed before the router is deployed.

---

## A  MQTT Port Inconsistencies (pre/post TLS)
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

### Detailed Findings

**A1  [MEDIUM]**  ha_vm_setup_guide.md Phase 4.2: mosquitto test commands hard-coded to port 1883 — no two-stage TLS migration note.
The ha_vm_setup_guide.md Phase 4.2 broker verification commands (mosquitto_sub/pub) use port 1883 unconditionally. Any operator following this guide after TLS migration will find the commands fail silently. The authoritative firewall-config.conf has a detailed two-stage note; the setup guide does not.
*Suggested fix:* Add the two-stage note used in firewall-config.conf immediately below the test commands: Stage 1 use 1883, Stage 2 switch to 8883 after TLS migration per ventsys_tls_implementation_guide.md.

**A2  [MEDIUM]**  esphome_adoption_guide.md Phase 3: mosquitto_sub test command uses port 1883 without TLS migration note (Phase 1.2 has the note but Phase 3 does not).
Phase 1.2 of esphome_adoption_guide.md correctly explains the two-stage MQTT approach, but the verification command in Phase 3 reverts to port 1883 with no cross-reference. An operator working through the guide sequentially will miss the note.
*Suggested fix:* Add an inline note after the Phase 3 test command: 'Use 1883 in Stage 1 (pre-TLS). After TLS migration, change this to 8883. See Phase 1.2 and ventsys_tls_implementation_guide.md Phase 4 for full migration steps.'

**A3  [MEDIUM]**  frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: MQTT_PORT=1883 with no two-stage note (vault version configs/frigate/docker-compose.yml has the note).
The inline docker-compose snippet in the setup guide and the authoritative vault file have diverged. The guide's snippet will be copied verbatim by anyone following the deployment steps; the important two-stage migration note is missing.
*Suggested fix:* Replace the inline docker-compose snippet in Phase 3.3 with the content from configs/frigate/docker-compose.yml, which contains the full deployment note.

**A4  [MEDIUM]**  frigate_vm_setup_guide.md Phase 3.4 inline config.yml: port: 1883 with no TLS migration note.
Same divergence as A3 but for the Frigate config.yml snippet. The guide shows port 1883 with no annotation, while the authoritative configs/frigate/config.yml has a TLS block and migration note.
*Suggested fix:* Sync the inline config.yml snippet in Phase 3.4 with the vault version, or at minimum add: 'Note: Change to 8883 and enable TLS block after running ventsys_tls_implementation_guide.md Phase 4.'

**A5  [LOW]**  bambuddy_p1s_setup_guide.md Phase 2: nc verification commands use port 1883 without TLS note.
The nc checks used to verify MQTT broker connectivity reference port 1883 only. After TLS migration these commands will fail and confuse the operator.
*Suggested fix:* Add: 'Pre-TLS: nc -zv 192.168.20.101 1883. Post-TLS: nc -zv 192.168.20.101 8883. Port 1883 will not respond after TLS migration.'

**A6  [LOW]**  bambuddy_p1s_setup_guide.md Phase 5: MQTT publishing settings show port 1883 without TLS note.
Phase 5 shows the Bambuddy MQTT_PORT=1883 setting without explaining that it should be updated to 8883 after TLS migration. The vault docker-compose.yml contains this note but the setup guide does not.
*Suggested fix:* Add a callout box: 'Stage 1 (pre-TLS): MQTT_PORT=1883. Stage 2 (after TLS migration per ventsys_tls_implementation_guide.md Phase 5.0): update to MQTT_PORT=8883 and restart Bambuddy.'

**A7  [LOW]**  bambuddy_p1s_setup_guide.md Quick Reference table: Firewall rule 2 references port 1883 — should reference 8883 with two-stage note.
The Quick Reference table at the end of the guide is consulted during debugging and re-deployment. The port 1883 entry gives a false impression that 1883 is the permanent port.
*Suggested fix:* Update the table entry to show 8883 as the permanent port and add a footnote explaining the Stage 1 / Stage 2 migration approach.

**A8  [MEDIUM]**  printairpipe-controller.yaml: port is already set to 8883 but the comment says 'switch to 1883 before TLS is set up' — backwards.
The comment reads as if 1883 is the TLS port and 8883 is the plain-text port, which is the opposite of reality. Any developer reading this file will be confused about which port to use pre-TLS.
*Suggested fix:* Replace the comment with: 'Stage 1 (pre-TLS): change port to 1883 for initial connectivity testing. Stage 2 (after TLS migration): revert to 8883. This file ships with 8883 as the post-migration default.'

**A9  [LOW]**  configuration.yaml comment references switching to 8883 after TLS but does not use the consistent two-stage language pattern established elsewhere.
Minor inconsistency in terminology. Using consistent language across all files makes the migration procedure easier to search for and follow.
*Suggested fix:* Update the comment to match the 'Stage 1 / Stage 2' wording used in firewall-config.conf and docker-compose.yml.


---

## B  Router Phase Guide Issues
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
| B9 | HIGH | phase_8_ventsys_readiness.md Step 8.1: creates CA infrastructure on the router at /etc/ventsys/ca/ — contradicts ventsys_tls_implementation_guide.md which places the CA on the HA VM at /config/ssl/ca/. Orphaned infrastructure on both systems. |
| B10 | HIGH | phase_8_ventsys_readiness.md Step 8.6: malformed bash — unclosed conditional block (missing 'fi' and closing echo), breaking shell syntax. |
| B11 | LOW | phase_2_network_infrastructure_complete.md Step 2.3: VLAN 50 note says 'no physical ports — WiFi only for security' but lan1:t (trunk to Proxmox) IS included for VLAN 50 in vlan-config.conf. |
| B12 | LOW | phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated on modern OpenWrt, may not be installed. |

### Detailed Findings

**B1  [HIGH]**  phase_3_dhcp_configuration.md Step 3.12: creates reservations for 4 ventsys devices (.81-.84) but dhcp-config.conf only has 2 (.81 ventsys-fan-controller, .82 ventsys-valve-controller). Device count and naming are both wrong.
The phase guide and the authoritative dhcp-config.conf are misaligned: the guide reserves four IPs (.81 ventsys-fan-controller, .82 ventsys-sla-valve, .83 ventsys-fdm-valve, .84 ventsys-booth-valve) while the config only reserves two. Applying the guide will create ghost reservations and confuse the DHCP server.
*Suggested fix:* Align Step 3.12 with dhcp-config.conf: remove .83 and .84 reservations and rename .82 to 'ventsys-valve-controller'. Add a note that additional valve boards will require new reservations when hardware is built.

**B2  [HIGH]**  phase_3_dhcp_configuration.md Step 3.12: missing DHCP reservations for printairpipe sensor boards at 192.168.50.31 (enc-fdm-sensors) and 192.168.50.32 (enc-sla-sensors).
The printairpipe-controller.yaml defines manual_ip for both sensor boards (.31 and .32) on VLAN 50. These IPs are not reserved in dhcp-config.conf or in the phase guide. Without reservations, a DHCP lease could be issued to another device at those addresses, causing IP conflicts with the fire safety sensor boards.
*Suggested fix:* Add DHCP reservations for both sensor boards to Step 3.12 and to configs/openwrt/dhcp-config.conf. MAC addresses will be XX:XX placeholders until hardware arrives.

**B3  [HIGH]**  phase_4_firewall_implementation.md Step 4.2: references /tmp/corrected_firewall_config.sh — this file does not exist. Should reference configs/openwrt/firewall-config.conf.
Applying Step 4.2 as written will fail immediately because the referenced file path is a throwaway temp path from an earlier editing session, not an actual vault file. The operator has no indication that they should be running the vault config file instead.
*Suggested fix:* Replace all references to /tmp/corrected_firewall_config.sh with the correct vault path: configs/openwrt/firewall-config.conf (or its deployed equivalent on the router).

**B4  [MEDIUM]**  phase_4_firewall_implementation.md Step 4.5: validation checks for a named rule 'Block IoT Internet' — but IoT internet blocking is implemented via zone forward policy (REJECT default), not a named rule. Validation would fail on a correctly deployed system.
The firewall-config.conf does include a named 'Block IoT Internet' rule as an explicit logged block (belt-and-suspenders), so the rule does technically exist. However the validation script treats its absence as a failure, which could mislead an operator into thinking the deployment is broken when it is actually correct.
*Suggested fix:* Rewrite the validation to check the zone forward policy rather than (or in addition to) the named rule, and clarify in a comment that the named rule is a supplementary logging rule.

**B5  [LOW]**  phase_5_wireless_configuration.md Success Criteria: 'Channel separation implemented: Non-overlapping 2.4GHz channels (1,6,11)' — factually incorrect. All 2.4GHz SSIDs share channel 6 on radio0 by design.
The mac80211 architecture on OpenWrt does not support per-SSID channel assignment — all SSIDs on the same radio share the same channel. The implementation is correct; the success criterion description is wrong.
*Suggested fix:* Change the success criterion to: 'All 2.4GHz SSIDs share channel 6 on radio0 (mac80211 architecture — per-SSID channel assignment is not possible on this platform).'

**B6  [HIGH]**  phase_6_vpn_setup.md Step 6.2: creates a duplicate static interface 'vpn' pointing to device 'wg0'. This is not valid OpenWrt WireGuard configuration.
In OpenWrt, WireGuard interfaces are self-contained (interface 'wg0' with proto wireguard). Adding a second static interface pointing to wg0 as a device creates an invalid layered configuration. The firewall zone should reference 'wg0' directly. Note: vlan-config.conf already has this structure; the error is specific to the phase guide instructions.
*Suggested fix:* Remove the 'config interface vpn' block from Step 6.2. Update the firewall zone instruction to reference the 'wg0' interface directly, matching the pattern already in vlan-config.conf.

**B7  [HIGH]**  phase_6_vpn_setup.md: entirely omits the step to assign the vpn_clients firewall zone to the wg0 interface, leaving VPN traffic unrouted through the firewall.
The vpn_clients zone is defined in firewall-config.conf with 'network=vpn', but Phase 6 never applies the zone assignment. Without this, WireGuard traffic bypasses all VPN firewall rules.
*Suggested fix:* Add a step after WireGuard interface creation: assign network='wg0' (or 'vpn' if using the alias) to the vpn_clients firewall zone and commit. Cross-reference firewall-config.conf zone definition.

**B8  [MEDIUM]**  phase_7_integration_testing.md Steps 7.5 and 7.7: uses 'iwlist scan' to validate SSID broadcasting — this scans for external networks, not your own configured SSIDs.
'iwlist scan' performs a scan of the radio environment and lists nearby APs. It will show your own SSIDs only if the radio is also acting as a client (which it is not in AP mode).
*Suggested fix:* Replace 'iwlist scan' with: 'iwinfo <radioN> info' (shows current channel/mode) or 'uci show wireless | grep ssid' (lists all configured SSIDs). For end-to-end SSID visibility testing, use a phone's WiFi scanner.

**B9  [HIGH]**  phase_8_ventsys_readiness.md Step 8.1: creates CA infrastructure on the router at /etc/ventsys/ca/ — contradicts ventsys_tls_implementation_guide.md which places the CA on the HA VM at /config/ssl/ca/. Orphaned infrastructure on both systems.
Two conflicting CA setups: Phase 8 runs openssl commands on the router with a different openssl.cnf structure from the one in ventsys_tls_implementation_guide.md Phase 3. If both guides are followed, two independent CAs exist and neither ESPHome device will trust the MQTT broker certificate.
*Suggested fix:* Remove the CA creation steps from Phase 8. Replace with a note: 'CA infrastructure is created on the HA VM — see ventsys_tls_implementation_guide.md Phase 3. This phase only validates network readiness for TLS.'

**B10  [HIGH]**  phase_8_ventsys_readiness.md Step 8.6: malformed bash — unclosed conditional block (missing 'fi' and closing echo), breaking shell syntax.
The script near the end of Phase 8 has an if/then block that is never closed. Executing this step will produce a 'syntax error: unexpected end of file'.
*Suggested fix:* Close the conditional block by adding the missing 'fi' statement and the closing echo line. Validate the complete script with 'bash -n' before committing.

**B11  [LOW]**  phase_2_network_infrastructure_complete.md Step 2.3: VLAN 50 note says 'no physical ports — WiFi only for security' but lan1:t (trunk to Proxmox) IS included for VLAN 50 in vlan-config.conf.
The trunk to Proxmox is necessary and correct. The note creates confusion: an operator might incorrectly remove the lan1:t trunk thinking it violates the 'WiFi only' statement.
*Suggested fix:* Change the note to: 'VLAN 50 has no direct-access physical ports (WiFi only for IoT devices). The lan1:t trunk to Proxmox is retained so the HA VM can route to VLAN 50 — this is required for ESPHome control and MQTT.'

**B12  [LOW]**  phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated and likely absent on modern OpenWrt DSA builds.
'brctl' is from the bridge-utils package which is not installed by default on modern OpenWrt (using DSA). The equivalent modern command is 'bridge vlan show'.
*Suggested fix:* Replace 'brctl show' with 'bridge vlan show' and 'bridge link show'. Add a note: 'brctl is deprecated on DSA-based OpenWrt versions.'


---

## C  Cross-File Inconsistencies
*Conflicts, naming mismatches, and divergences between the authoritative config files and their referencing guides*

| ID | Severity | Summary |
|---|---|---|
| C1 | MEDIUM | dhcp-config.conf names the valve controller 'ventsys-valve-controller' (.82) but phase_3 guide names it 'ventsys-sla-valve' (.82). Same IP, different hostname. |
| C2 | MEDIUM | frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Frigate service specifies both 'network_mode: host' AND explicit 'ports:' mappings — redundant and misleading. |
| C3 | MEDIUM | frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Bambuddy service sets MQTT_PORT=1883 without the two-stage migration note present in configs/frigate/docker-compose.yml. |
| C4 | HIGH | bambuddy_p1s_setup_guide.md Phase 6.4: references automations 'p1s_ventsys_fdm_start' and 'p1s_ventsys_fdm_stop' which do not exist in bambuddy_p1s_package.yaml or automations.yaml. |
| C5 | HIGH | ventsys_ha_package.yaml: Booth Valve entity uses command_topic 'ventsys/booth/valve/control' — no ESPHome firmware publishes to this topic. The valve controller only handles the SLA valve. |
| C6 | HIGH | ventsys_ha_package.yaml: Booth Risk sensor subscribes to 'ventsys/booth/risk/state' — no ESPHome firmware publishes to this topic. |
| C7 | MEDIUM | ventsys_ha_optional.yaml: T-inlet, T-downstream number entities and a pressure setpoint reference MQTT topics with no corresponding ESPHome firmware. Planned but unimplemented features. |
| C8 | MEDIUM | health_check.sh: only monitors fan (.81) and valve (.82) controllers — printairpipe sensor boards at .31 and .32 are not monitored. Coverage gap for fire safety sensors. |
| C9 | LOW | health_check.sh: P1S check uses port 8883 (P1S_PORT=8883) for a TCP connect test — this is the printer's own MQTT TLS port and may succeed even if the printer is malfunctioning. |
| C10 | LOW | ha_vm_setup_guide.md 'Next steps' section: lists ESPHome adoption, MQTT TLS, Frigate VM, NAS integration — omits Bambuddy/P1S setup guide reference. |
| C11 | LOW | bambuddy_p1s_package.yaml header comment: 'Bambuddy MQTT publishing configured to 192.168.20.101:1883' — should reflect two-stage port approach. |

### Detailed Findings

**C1  [MEDIUM]**  dhcp-config.conf names the valve controller 'ventsys-valve-controller' (.82) but phase_3 guide names it 'ventsys-sla-valve' (.82). Same IP, different hostname.
dhcp-config.conf is the authoritative DHCP config. The phase guide uses a different hostname for the same device, which means the DNS name assigned will depend on which file was followed.
*Suggested fix:* Standardise all references to the hostname in dhcp-config.conf: 'ventsys-valve-controller'. Update phase_3 step 3.12 to match.

**C2  [MEDIUM]**  frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Frigate service specifies both 'network_mode: host' AND explicit 'ports:' mappings — redundant and misleading.
With host networking, the container shares the host's network stack directly. The 'ports:' directive is silently ignored by Docker in host mode. The redundant ports block may confuse an operator who tries to add a firewall rule based on the ports list.
*Suggested fix:* Remove the 'ports:' block from the Frigate service definition in the inline snippet, and add a comment: 'network_mode: host — port mappings are ignored; Frigate is accessible on all host IPs directly.'

**C3  [MEDIUM]**  frigate_vm_setup_guide.md Phase 3.3 inline docker-compose: Bambuddy service sets MQTT_PORT=1883 without the two-stage migration note present in configs/frigate/docker-compose.yml.
The inline snippet and the vault file have diverged. This is listed separately from A3 because it affects the Bambuddy portion of the compose file specifically.
*Suggested fix:* Sync the Bambuddy service block in the inline snippet with the vault docker-compose.yml, including the Stage 1/Stage 2 migration comment.

**C4  [HIGH]**  bambuddy_p1s_setup_guide.md Phase 6.4: references automations 'p1s_ventsys_fdm_start' and 'p1s_ventsys_fdm_stop' which do not exist in bambuddy_p1s_package.yaml or automations.yaml.
Phase 6.4 describes VentSys FDM mode being automatically activated when a P1S print starts. The automations it references have never been created. The guide documents intended behaviour that has not been implemented.
*Suggested fix:* Either implement the two automations (p1s_ventsys_fdm_start: trigger on binary_sensor.p1s_printing ON, call script.ventsys_mode_fdm; p1s_ventsys_fdm_stop: trigger on OFF, call script.ventsys_mode_idle) or add a clear TODO note in Phase 6.4 marking this as unimplemented.

**C5  [HIGH]**  ventsys_ha_package.yaml: Booth Valve entity uses command_topic 'ventsys/booth/valve/control' — no ESPHome firmware publishes to this topic. The valve controller only handles the SLA valve.
An operator who deploys the package will see the entity in the dashboard but sending a command will have no effect. This creates a false sense of control for a safety-related valve.
*Suggested fix:* Add a comment to the Booth Valve entity: 'UNIMPLEMENTED — no ESPHome firmware currently handles this topic. Hardware and firmware for the booth valve are pending. Do not rely on this entity for safety control.'

**C6  [HIGH]**  ventsys_ha_package.yaml: Booth Risk sensor subscribes to 'ventsys/booth/risk/state' — no ESPHome firmware publishes to this topic.
The Booth Risk sensor entity will always show 'unknown' or 'unavailable' in HA. For fire safety monitoring, a persistently unavailable sensor is worse than no sensor — it may be silently assumed to be 'safe'.
*Suggested fix:* Add a comment matching C5. Additionally, consider adding an availability check automation that alerts if this sensor remains unavailable when booth printing mode is active.

**C7  [MEDIUM]**  ventsys_ha_optional.yaml: T-inlet, T-downstream number entities and a pressure setpoint reference MQTT topics with no corresponding ESPHome firmware. Planned but unimplemented features.
The optional YAML contains entities that look functional but have no hardware or firmware backing them. Unlike C5/C6, these are in the 'optional' file, so the risk is lower.
*Suggested fix:* Add a header comment to ventsys_ha_optional.yaml: 'SECTION: PLANNED FEATURES — entities below have no firmware implementation. Do not load these into HA production until ESPHome configs are created.'

**C8  [MEDIUM]**  health_check.sh: only monitors fan (.81) and valve (.82) controllers — printairpipe sensor boards at .31 and .32 are not monitored. Coverage gap for fire safety sensors.
The sensor boards are the primary smoke/VOC/temperature monitoring devices. If they go offline, the health check will show all green while the fire safety system has lost its primary input.
*Suggested fix:* Add health check entries for 192.168.50.31 and 192.168.50.32 (PING and MQTT topic checks). Consider adding a check that verifies these devices are actively publishing (last seen < 5 minutes) rather than just TCP-reachable.

**C9  [LOW]**  health_check.sh: P1S check uses port 8883 (P1S_PORT=8883) for a TCP connect test — this is the printer's own MQTT TLS port and may succeed even if the printer is malfunctioning.
A TCP connect to port 8883 only verifies that the printer's MQTT TLS listener is accepting connections. The printer could be in an error state, out of filament, or have a door open, and the health check would still show green.
*Suggested fix:* Replace the TCP port check with an ICMP ping (ping -c 1 -W 2 $P1S_IP). If MQTT status monitoring is desired, add a separate check that subscribes to the Bambuddy MQTT topic and verifies a recent heartbeat.

**C10  [LOW]**  ha_vm_setup_guide.md 'Next steps' section: lists ESPHome adoption, MQTT TLS, Frigate VM, NAS integration — omits Bambuddy/P1S setup guide reference.
The Next Steps section is used by operators to know what to tackle after HA VM deployment. The Bambuddy/P1S integration is a significant step that is not listed.
*Suggested fix:* Add 'Bambuddy P1S printer integration — follow scripts/setup/printers/bambuddy_p1s_setup_guide.md' to the Next Steps list.

**C11  [LOW]**  bambuddy_p1s_package.yaml header comment: 'Bambuddy MQTT publishing configured to 192.168.20.101:1883' — should reflect two-stage port approach.
The header comment becomes stale after TLS migration and may confuse future debugging.
*Suggested fix:* Update the comment: 'Bambuddy MQTT: Stage 1 (pre-TLS) port 1883, Stage 2 (post-TLS migration) port 8883. Current deployment port should match docker-compose.yml MQTT_PORT.'


---

## D  Logic / Safety Issues
*Automation logic errors and missing safety controls — includes CRITICAL findings*

| ID | Severity | Summary |
|---|---|---|
| D1 | CRITICAL | automations.yaml fire_detection_emergency: calls script.ventsys_mode_purge which opens ALL ventilation paths including the spray booth fan. Activating the spray booth fan during a fire event is inappropriate. |
| D2 | CRITICAL | ventsys_ha_scripts.yaml: no mode script resets other active paths before switching. Mode transitions are not atomic — switching modes can leave multiple paths open simultaneously. |
| D3 | HIGH | ventsys_ha_scripts.yaml ventsys_mode_booth_seal: only closes main-2 and spray fan — does not close main-1. If booth mode left main-1 open, booth_seal leaves it open. |
| D4 | HIGH | No boot/startup script to initialise VentSys to a known safe state when HA restarts. After restart, MQTT-controlled entities show 'unknown', leaving physical hardware in its last state. |

### Detailed Findings

**D1  [CRITICAL]**  automations.yaml fire_detection_emergency: calls script.ventsys_mode_purge which opens ALL ventilation paths including the spray booth fan. Activating the spray booth fan during a fire event is inappropriate.
The fire emergency automation triggers ventsys_mode_purge via the failsafe mechanism. Purge mode is designed to flush fumes — it opens all valve paths including the spray booth exhaust fan. In a fire scenario, running the spray booth fan can draw air across a flame, accelerate combustion, and spread combustion products. A fire-safe ventilation mode should open enclosure paths and the main inline fan to exhaust smoke, but should NOT activate the spray booth fan.
*Suggested fix:* Create a new script 'script.ventsys_mode_fire_emergency' that opens FDM valve, SLA valve, and sets main inline fan to 100%, but explicitly closes/does-not-activate the spray booth fan and booth valve. Replace the purge call in fire_detection_emergency with this new script. Add a comment explaining the safety rationale.

**D2  [CRITICAL]**  ventsys_ha_scripts.yaml: no mode script resets other active paths before switching. Mode transitions are not atomic — switching modes can leave multiple paths open simultaneously.
Example: if SLA mode is active (main-1 open) and the operator switches to FDM mode, the SLA path remains open. With multiple paths open simultaneously, fan pressure drops, effective ventilation per path is reduced, and the system is in an undefined state not covered by any mode's safety logic.
*Suggested fix:* Add a 'reset_all_paths' step at the beginning of every mode script that closes all valves and stops all fans before applying the new mode configuration. Consider creating a shared script 'script.ventsys_all_off' that all mode scripts call first, then open only the required paths.

**D3  [HIGH]**  ventsys_ha_scripts.yaml ventsys_mode_booth_seal: only closes main-2 and spray fan — does not close main-1. If booth mode left main-1 open, booth_seal leaves it open.
Booth mode opens both main-1 and main-2. The corresponding seal script only closes main-2 and the spray fan, leaving main-1 open. The system can then be in 'sealed' state (user believes ventilation is off) while main-1 continues pulling air. For a solvent spray booth, incomplete sealing is a safety hazard.
*Suggested fix:* Add 'main-1' to the ventsys_mode_booth_seal script's close sequence. As a belt-and-suspenders measure, the seal script should close ALL actuators regardless of assumed prior state (per D2 fix).

**D4  [HIGH]**  No boot/startup script to initialise VentSys to a known safe state when HA restarts. After restart, MQTT-controlled entities show 'unknown', leaving physical hardware in its last state.
If HA restarts unexpectedly (power cut, update, crash), all MQTT command topics are silent. The ESPHome devices retain their last commanded state. If a valve was open, it remains open. If the fan was running at 100%, it continues running. There is no mechanism to return to a defined safe state.
*Suggested fix:* Create an automation triggered on 'homeassistant' start event that calls 'script.ventsys_mode_idle' (or a dedicated 'script.ventsys_startup_safe_state'). This ensures all actuators are commanded to a known configuration within seconds of HA coming online. Add a 10-second delay after trigger to allow MQTT broker reconnection.

---

## E  Outdated / Deprecated Elements
*Installation methods, commands, and protocols that have been superseded*

| ID | Severity | Summary |
|---|---|---|
| E1 | MEDIUM | ha_vm_setup_guide.md Phase 5.2: HACS installation uses 'wget -O - https://get.hacs.xyz | bash -' — pipe-to-bash approach no longer recommended for HAOS. |
| E2 | MEDIUM | frigate_vm_setup_guide.md Phase 5.3: same outdated HACS installation command as E1. |
| E3 | LOW | phase_6_vpn_setup.md Step 6.5: WAN IP detection uses 'wget -qO- http://ipecho.net/plain' — unencrypted HTTP to a third-party service. |
| E4 | LOW | phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated and likely absent on modern OpenWrt DSA builds. (Duplicate of B12.) |

### Detailed Findings

**E1  [MEDIUM]**  ha_vm_setup_guide.md Phase 5.2: HACS installation uses 'wget -O - https://get.hacs.xyz | bash -' — pipe-to-bash approach no longer recommended for HAOS.
The pipe-to-bash method runs an arbitrary script from the internet with root privileges. More importantly, HACS is now available as an official add-on through the HA Supervisor store, making the manual script unnecessary.
*Suggested fix:* Update Phase 5.2 to: 'Install HACS via HA UI: Settings → Add-ons → Add-on Store → search HACS. If not available as an add-on, refer to https://hacs.xyz/docs/installation for the current method.' Remove the wget pipe command.

**E2  [MEDIUM]**  frigate_vm_setup_guide.md Phase 5.3: same outdated HACS installation command as E1.
The Frigate VM guide repeats the same problem for the Frigate/HA integration setup.
*Suggested fix:* Apply the same fix as E1 to frigate_vm_setup_guide.md Phase 5.3.

**E3  [LOW]**  phase_6_vpn_setup.md Step 6.5: WAN IP detection uses 'wget -qO- http://ipecho.net/plain' — unencrypted HTTP to a third-party service.
Using an unencrypted external service to discover the WAN IP is both a privacy concern and unreliable. For a static WAN IP, no external query is needed. For a dynamic IP, the router itself has the most reliable answer.
*Suggested fix:* Replace with: 'uci get network.wan.ipaddr' for static IPs, or 'ip route get 1.1.1.1 | grep -o "src [0-9.]*" | cut -d" " -f2' for dynamic. Note that DDNS is the correct solution for dynamic IPs.

**E4  [LOW]**  phase_2_network_infrastructure_complete.md Step 2.7: uses 'brctl show' — deprecated and likely absent on modern OpenWrt DSA builds. (Duplicate of B12.)
bridge-utils (which provides brctl) is not part of the default OpenWrt image for DSA-based hardware.
*Suggested fix:* Same fix as B12: replace with 'bridge vlan show' and 'bridge link show'.

---

## F  Incompleteness / Missing Content
*Documented intentions, referenced procedures, and required configurations that do not yet exist*

| ID | Severity | Summary |
|---|---|---|
| F1 | CRITICAL | No dedicated fire/emergency ventilation mode script exists. The failsafe currently calls purge (which includes the spray booth fan). A fire-safe mode is required. (Related to D1.) |
| F2 | LOW | ventsys_ha_scripts.yaml: no script for 'FDM + SLA simultaneous' mode (both enclosures printing at once). |
| F3 | HIGH | esphome_adoption_guide.md: covers only fan (.81) and valve (.82) controllers — no guidance for adopting the printairpipe sensor boards (.31, .32) which have a different config and require DS18B20 address scanning. |
| F4 | LOW | bambuddy_p1s_setup_guide.md Phase 5 TLS note: mentions Frigate's MQTT TLS config needs updating but provides no steps — only a note. |
| F5 | MEDIUM | ventsys_tls_implementation_guide.md Phase 5.0 (Bambuddy): does not include steps for updating Frigate's MQTT TLS configuration. |
| F6 | MEDIUM | phase_3_dhcp_configuration.md: missing DHCP reservations for printairpipe sensor boards (.31, .32) and for the 7 additional valve boards that will be needed when hardware is built. |
| F7 | LOW | backup_strategy.md recovery runbook Step 4 references 'MAC update procedure in esphome_adoption_guide.md' — that guide does not contain a VM MAC update procedure. |

### Detailed Findings

**F1  [CRITICAL]**  No dedicated fire/emergency ventilation mode script exists. The failsafe currently calls purge (which includes the spray booth fan). A fire-safe mode is required. (Related to D1.)
This is listed in both D (logic error) and F (missing content) because it involves both an incorrect automation and missing script code. The gap means there is currently no safe path for the fire emergency automation to follow.
*Suggested fix:* Create script.ventsys_mode_fire_emergency as described in D1. Add it to ventsys_ha_scripts.yaml, test it in simulation, and update the fire_detection_emergency automation to call it instead of purge.

**F2  [LOW]**  ventsys_ha_scripts.yaml: no script for 'FDM + SLA simultaneous' mode (both enclosures printing at once).
The VentSys hardware supports both enclosures being ventilated simultaneously. There is no script for this mode, so an operator must manually set each entity — error-prone for a safety system.
*Suggested fix:* Create script.ventsys_mode_fdm_and_sla: opens FDM valve, SLA valve, closes booth paths, sets fan to 80% (or calculated value for dual-path flow). Add to the dashboard as a mode button.

**F3  [HIGH]**  esphome_adoption_guide.md: covers only fan (.81) and valve (.82) controllers — no guidance for adopting the printairpipe sensor boards (.31, .32) which have a different config (printairpipe-controller.yaml) and require DS18B20 address scanning.
The sensor boards require a specific adoption workflow: flash via USB with a placeholder DS18B20 address, boot, scan for actual addresses using the ESPHome serial console, then reflash with correct addresses. This process is not documented anywhere.
*Suggested fix:* Add a Phase 4 to esphome_adoption_guide.md covering: (1) flash printairpipe-controller.yaml via USB with substitution for 'fdm' or 'sla', (2) boot and open serial monitor, (3) run ds18b20 scan to find actual addresses, (4) update the address substitution in the YAML, (5) OTA reflash with correct address, (6) verify temperature entities appear in HA.

**F4  [LOW]**  bambuddy_p1s_setup_guide.md Phase 5 TLS note: mentions Frigate's MQTT TLS config needs updating but provides no steps.
The note reads 'Frigate config.yml will also need updating for TLS' without linking to where this is documented.
*Suggested fix:* Replace the bare note with: 'Frigate MQTT TLS update: see ventsys_tls_implementation_guide.md Phase 5.0, step "Note on Frigate MQTT" — update configs/frigate/config.yml cafile/certfile/keyfile and restart Frigate.'

**F5  [MEDIUM]**  ventsys_tls_implementation_guide.md Phase 5.0 (Bambuddy): does not include steps for updating Frigate's MQTT TLS configuration. Frigate config.yml has the TLS block but the guide never walks through applying it.
Frigate also connects to MQTT and will fail to connect after TLS migration if its own config.yml TLS settings are not updated.
*Suggested fix:* Add a new sub-step to Phase 5.0: 'Update Frigate MQTT TLS: (1) Copy /config/ssl/ca/certs/ca-cert.pem to Frigate VM at /opt/frigate/certs/ca-cert.pem, (2) Update configs/frigate/config.yml mqtt section with cafile path and port 8883, (3) restart Frigate with docker compose restart.'

**F6  [MEDIUM]**  phase_3_dhcp_configuration.md: missing DHCP reservations for printairpipe sensor boards (.31, .32) and for the 7 additional valve boards that will be needed when hardware is built.
Reservations should be pre-planned even if the hardware does not yet exist, to prevent conflicts.
*Suggested fix:* Add placeholder reservations for .83-.89 with XX:XX:XX MAC placeholders and hostnames 'ventsys-valve-controller-N'. Add a note: 'MAC addresses to be filled in when hardware is built.'

**F7  [LOW]**  backup_strategy.md recovery runbook Step 4 references 'MAC update procedure in esphome_adoption_guide.md' — that guide does not contain a VM MAC update procedure.
The esphome_adoption_guide.md covers ESPHome device MACs but not Proxmox VM virtual NIC MACs. After a restore, VMs will have new MAC addresses and DHCP reservations in dhcp-config.conf will no longer match.
*Suggested fix:* Update the backup runbook Step 4 reference: 'To update VM MAC addresses after restore: (1) Check new MACs in Proxmox hardware tab for VM 100 and 101, (2) Update dhcp-config.conf VM reservations section, (3) Redeploy configs/openwrt/dhcp-config.conf to router. See vm-setup.sh NEXT STEPS for context.'

