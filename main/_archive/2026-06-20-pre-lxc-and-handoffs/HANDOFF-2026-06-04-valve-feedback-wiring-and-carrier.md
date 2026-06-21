# HANDOFF - Valve Feedback Wiring, Diagrams, and Printed Carrier

**Date:** 2026-06-04
**Scope:** Document the ESP32 D1 Mini valve-servo analog feedback wiring work, the cleaned wiring diagram, the small 3D-printable feedback carrier, and the reusable skill now available for future carrier designs.

---

## TL;DR for the next chat

The next chat is expected to:

1. Test the new portable `electronics-carrier-design` skill.
2. Use it to design a new board/carrier that incorporates the wiring and passive parts between the ESP32 board, servo, and LED.
3. Keep the ESP32 board, servo body, and LED body off the new carrier; the target is the intermediate wiring/components only.

The current tiny carrier is only for the analog feedback protection/filter network:

```text
servo feedback -> 10k resistor -> ADC output
                              |
                              +-> 20k resistor -> GND
                              |
                              +-> 100nF capacitor -> GND
```

The larger servo-power electrolytic capacitor remains a separate part across the 5V/GND rail near the servo power split.

---

## Hardware Decisions Reached

- Board is **ESP32 D1 Mini**, not ESP32-C6 Zero.
- Servo is MG90/MG90S-style with analog feedback wire.
- Servo power should use the board `VCC / 5V` rail from the powered USB hub, not the board `3.3V` pin.
- ESP32, servo, LED, and feedback network must share common GND.
- Single addressable LED can share the same 5V/GND rail; its data wiring is known and not part of the current carrier.
- Analog feedback protection/filter network:
  - Servo feedback into `10k`.
  - ADC node after `10k` goes to ESP32 `SVP / GPIO36`.
  - ADC node also goes through `20k` to GND.
  - ADC node also goes through `100nF` ceramic capacitor to GND.
- Bulk servo-power capacitor:
  - Use approximately `470uF-1000uF` electrolytic across 5V/GND.
  - Place near the servo power split.
  - This is not part of the tiny feedback carrier.

---

## Diagram Outputs

Clean wiring diagram files:

- `main/docs/diagrams/wiring-diagrams/esp32-d1-mini-servo-feedback-wiring.html`
- `main/docs/diagrams/wiring-diagrams/esp32-d1-mini-servo-feedback-wiring.png`

Diagram intent:

- Shows only the needed ESP32 D1 Mini pins.
- Avoids the original full board pinout image.
- Uses simple labeled boxes rather than schematic symbols.
- Shows servo power from `VCC / 5V`, common GND, PWM, feedback network, and the single addressable LED.

If the next session revises wiring, update both the HTML source and PNG export.

---

## Current 3D-Printable Feedback Carrier

Carrier files:

- `main/assets/3d-printing/ventsys_feedback_carrier.scad`
- `main/assets/3d-printing/ventsys_feedback_carrier.stl`
- `main/assets/3d-printing/ventsys_feedback_carrier_preview.png`
- `main/assets/3d-printing/ventsys_feedback_carrier_v2_concept.svg`
- `main/assets/3d-printing/ventsys_feedback_carrier_v2_concept.png`
- `main/assets/3d-printing/ventsys_feedback_carrier.md`

Current generated carrier geometry:

- Footprint: `11.0mm x 12.4mm`
- Height: `1.8mm`
- Recess depth: `0.75mm`
- No text in STL.
- No raised rim.
- No raised pads.
- Pockets and channels share one depth plane.
- Capacitor pocket was expanded upward by `2mm` to fit the measured nearly-`6mm` ceramic capacitor width.

OpenSCAD export command that worked:

```powershell
& 'O:\Print\CAD Software\OpenSCAD\openscad.com' -o 'K:\Documents\Obsidian\home-automation-project\main\assets\3d-printing\ventsys_feedback_carrier.stl' 'K:\Documents\Obsidian\home-automation-project\main\assets\3d-printing\ventsys_feedback_carrier.scad'
```

Preview command that worked:

```powershell
& 'O:\Print\CAD Software\OpenSCAD\openscad.com' --render --imgsize=1200,900 --camera=5.5,6.2,12,0,0,0,55 -o 'K:\Documents\Obsidian\home-automation-project\main\assets\3d-printing\ventsys_feedback_carrier_preview.png' 'K:\Documents\Obsidian\home-automation-project\main\assets\3d-printing\ventsys_feedback_carrier.scad'
```

Important caveat:

- After this carrier was generated, a new reusable skill was created with a future default of `3mm` total height, `2mm` recess depth, and `1mm` remaining base.
- The existing VentSys feedback carrier STL was **not** regenerated to those new defaults.
- Next session should decide whether to leave the current carrier as-is, regenerate it under the new default geometry, or apply the new defaults only to future larger carriers.

---

## Available Skill

A portable skill is now available:

- `C:\Users\Admin\.agents\skills\electronics-carrier-design\SKILL.md`
- `C:\Users\Admin\.claude\skills\electronics-carrier-design\SKILL.md`
- `C:\Users\Admin\.codex\skills\electronics-carrier-design\SKILL.md`

Purpose:

- Design small 3D-printable electronics carriers for hand-wired components.
- Use a circuit-first, visual-first workflow before OpenSCAD/STL generation.
- Default future geometry: `3mm` total height, `2mm` pockets/channels, `1mm` base below recesses.

The next chat should test the skill directly before using it to design the larger intermediate wiring/components carrier.

Note:

- The Codex CLI was unblocked by copying the packaged binary to `C:\Users\Admin\.local\bin\codex.exe`.
- `codex --help` and `codex doctor --summary --ascii` were verified after that change.
- A new Codex/Claude session may still be needed for skill discovery to refresh.

---

## Recommended Next Work

1. Start a new chat/session and confirm the `electronics-carrier-design` skill is discovered.
2. Ask the skill to reproduce or critique the existing tiny feedback carrier from the files above.
3. Then design the next carrier for the entire passive/wiring section between the ESP32 D1 Mini, servo, and LED.
4. Include these parts in the new carrier scope:
   - `10k` feedback resistor
   - `20k` feedback-to-GND resistor
   - `100nF` feedback capacitor
   - `470uF-1000uF` servo power electrolytic capacitor, if mechanically sensible
   - wiring junctions/solder points for 5V, GND, PWM, feedback, ADC, and LED data as needed
5. Keep these out of carrier scope:
   - ESP32 board body
   - Servo body
   - LED body
6. Preserve the same electrical assumptions unless deliberately revised:
   - Servo and LED share 5V/GND rail.
   - Feedback network protects `SVP / GPIO36`.
   - Plastic carrier is mechanical only; use solder plus heatshrink/sleeving/liquid electrical tape for exposed joints.

---

## Things Not Yet Done

- ESPHome YAML has not yet been updated to read the analog feedback ADC.
- Home Assistant entities/diagnostics for actual servo position have not yet been added.
- The wiring diagram has not yet been revised to show a single larger carrier for all intermediate wiring/components.
- The current tiny carrier has not yet been physically test-printed or dry-fitted, based on this handoff.
