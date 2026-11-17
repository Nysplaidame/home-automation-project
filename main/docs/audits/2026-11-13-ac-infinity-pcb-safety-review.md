# AC Infinity interface PCB safety review — 13 November 2026

**Disposition: NOT APPROVED for unattended or safety-critical operation.** This is a source-level review, not certification or a physical acceptance test. The upstream design is `coofercat/ha-ac-infinity-fan` commit `e5279bcfa6c884b3a2ccae8edb4d0dd0cbb51b54`; the specific fan, relay batch, regulator, PCB fabrication, enclosure and installation have not been tested.

## Evidence

The Fritzing schematic connectivity was extracted and compared with the Fritzing PCB-view explicit connection graph: all 18 schematic multi-component nets appear connected in the PCB graph. This does not compare the exported Gerbers to the Fritzing graph, verify ground fills, check copper clearances, find extra shorts, or replace an electrical design-rules check. No hardware, scope measurements, isolation test, fault injection or thermal test was performed.

## Blocking findings

1. **Relay documentation contradiction.** The embedded Fritzing part's connector metadata describes connector2 as NC1 and connector3 as NO1; its schematic SVG labels connector2 NO1 and connector3 NC1. Connector2 joins controller PWM and connector3 joins the ESP32-generated fan output. The fan PWM goes to connector1 (common). The desired unpowered controller-to-fan continuity must be verified using the actual relay and board; do not assume metadata, drawing, package shape or fit proves it. Verify both energised and unpowered paths.
2. **Safety system integration unresolved.** VentSys normal modes coordinate several valves and fans through guarded HA sequencing; fire response uses independent emergency paths. This controller is not demonstrated to accept or prioritise those commands. Direct local takeover could bypass arbitration. No fire-mode mapping, independent fallback, mechanical position or airflow verification has been proven. It must not replace the existing safety function without an integrated hazard analysis and commissioning.
3. **UIS electrical interface uncharacterised.** Supply range, source current limit, short-circuit behaviour, transient limits, input and output signal levels and protective isolation of this fan/controller combination are unknown. It uses a proprietary 10 V connection with a USB-C form factor. The PCB has no established independent mains isolation barrier. Do not assume a USB-shaped port is USB or connect grounded test gear until isolation is assessed.
4. **Power and heat unverified.** The example 7805 input capacitor is 0.1 µF; compare the selected regulator's datasheet and layout to its stability and input/output capacitor requirements. A 7805 dissipates approximately (Vin−5 V)×load current; the buck option also needs its own input range, output, transient, ripple and thermal verification. Exact supply capacity, ESP32 peaks, relay current and enclosed temperature are not documented. No fuse rating can be chosen without supply characteristics and fault testing.
5. **Relay drive margin not established.** GPIO27 drives Q3 through 1 kΩ; estimated base current is only a few mA. Coil current depends on the exact relay: a 5 V 0.2 W coil draws about 40 mA. Saturation, pull-in across supply and temperature extremes, transistor dissipation and flyback diode rating must be checked for the exact parts. A product-family relay datasheet alone is insufficient.
6. **Release files not verified.** No full electrical rules check, Gerber-to-schematic equivalence, drill/fabricator stack-up review, shorts/clearance check or hardware acceptance exists in this review. Supplier and part substitutions require their own checks, especially transistor pinout, relay pinout, diode polarity and tantalum orientation.

## Firmware and behaviour

The firmware selects relay takeover using GPIO27 and generates fan PWM on GPIO26. The firmware requests takeover off on boot; verify actual relay behaviour during power loss, boot and brownout. GPIO25 is physically connected to the Q2 signal network even though current firmware does not use it. GPIO33 reads fan tach and GPIO34 reads the filtered controller signal. Signals need measurement to validate ESP32 input limits and board operation. The speed values are inferred from thresholds, not direct airflow measurement.

Boost restoration contains a possible state/order defect: turn-off sets remaining time to zero before testing whether boost is on, while its template state depends on remaining time and the running script. Verify under the actual ESPHome version before relying on timer restoration. API/Wi-Fi reboot timeout behaviour should be explicitly configured and tested: default timeouts can cause a reboot and return to pass-through, not immediate fallback. The hotspot password must be changed; the BLE boost trigger matches an address and is not shown to authenticate a sender.

## Required verification before release

- Obtain exact fan/controller models, cable and connector wiring, PCB revision and fabrication specification, exact ESP32/regulator/transistor/relay/diode/capacitor part numbers, enclosure, environmental conditions and normal/fault requirements.
- Correct the relay part documentation and verify every relay position and coil using the physical parts. Perform schematic-to-layout and Gerber-to-netlist comparison, complete design-rule/clearance/drill checks and independent review.
- Measure UIS voltage and current including startup, relay activation and ESP32 radio peaks; validate interface pin voltages/transients with suitably isolated equipment. Test back-power scenarios and isolate UIS before attaching USB, as upstream instructs.
- Bench test with a correctly configured current-limited supply; verify input and 5 V polarity, shorts, startup and output under realistic load; do not arbitrarily set a fuse value.
- Verify pass-through, takeover, boot, brownout, loss of power/Wi-Fi/HA, relay fault, cable disconnection, miswiring protection where applicable, boost cancellation/expiry, and manual recovery. Include conditions with the fan connected and controller actively commanding different speeds.
- Record thermal equilibrium at realistic maximum ambient, supply and load in the closed final enclosure, including mounting and adjacent materials; assess PCB, regulator, relay and plastic against actual rated temperatures with margin.
- Independently validate VentSys control authority, fire-response priority, valve sequencing, airflow and failure alarms through physical end-to-end tests. Use a competent professional for mains isolation and installation assessment.

## References

- Upstream electronics: https://github.com/coofercat/ha-ac-infinity-fan/tree/e5279bcfa6c884b3a2ccae8edb4d0dd0cbb51b54/electronics
- Upstream firmware: https://github.com/coofercat/ha-ac-infinity-fan/blob/e5279bcfa6c884b3a2ccae8edb4d0dd0cbb51b54/esphome/device.yaml
- VentSys operating mode and arbitration contract: `main/docs/procedures/ventsys-dashboard.md`.
- ST L78 datasheet: https://www.st.com/resource/en/datasheet/l78.pdf
- onsemi 2N3904 datasheet: https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf
