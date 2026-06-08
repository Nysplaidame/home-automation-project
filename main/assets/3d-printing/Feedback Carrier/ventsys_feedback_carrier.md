# VentSys Feedback Carrier

Tiny 11mm x 12.4mm printable carrier for the analog-feedback servo
divider/filter network.

## File

- `ventsys_feedback_carrier.scad`
- `ventsys_feedback_carrier.stl`
- `ventsys_feedback_carrier_preview.png`
- `ventsys_feedback_carrier_v2_concept.svg`
- `ventsys_feedback_carrier_v2_concept.png`

The STL was exported with the local OpenSCAD install at
`O:\Print\CAD Software\OpenSCAD`.

## Parts

- 1x 10k resistor
- 1x 20k resistor
- 1x 100nF ceramic capacitor
- Thin hook-up wire or clipped component leads
- Heatshrink or liquid electrical tape for exposed joints

## Layout

Visual concept labels:

- `FB` = servo feedback wire enters this side.
- `ADC` = protected analog signal exits to ESP32 `SVP / GPIO36`.
- `GND` = shared ground return.

The generated STL has no lettering, perimeter rim, or raised pads. It uses
recessed component pockets and wire channels on one shared depth plane.

Electrical path:

```text
servo feedback -> 10k resistor -> ADC output
                              |
                              +-> 20k resistor -> GND
                              |
                              +-> 100nF capacitor -> GND
```

## Assembly Notes

- The plastic part is only a mechanical carrier, not an electrical connector.
- Glue the component bodies into the recessed pockets after dry-fitting the
  leads.
- Bare leads may touch only where they are meant to be the same electrical node.
- Use heatshrink, sleeving, or liquid electrical tape over finished joints.
- Keep the carrier close to the ESP32 ADC pin if convenient, but this feedback
  network is not especially placement-sensitive.
- The large 470uF-1000uF electrolytic capacitor for servo power is separate and
  should stay across the 5V/GND rail near the servo power split.

## Print Guidance

- Print flat side down.
- PLA or PETG is fine.
- Use 0.2mm layer height or finer.
- No supports should be required.
- If wire channels are too tight, adjust the channel dimensions in the SCAD
  file.
