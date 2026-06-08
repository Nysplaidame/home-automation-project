# ESP32 D1 Mini Servo Feedback Carrier

This folder contains a provisional 3D-printable recessed wiring carrier for the
`esp32-d1-mini-servo-feedback-wiring.png` diagram.

The LED section and all LED-related wires are intentionally omitted. The carrier
covers only:

- ESP32 D1 Mini edge exits: 5V, GND, PWM, ADC / GPIO36
- Servo edge exits: 5V, GND, PWM, feedback
- 10k series resistor on the feedback path
- 20k resistor from the ADC side of the 10k to GND
- 100nF ceramic capacitor from the ADC side of the 10k to GND
- 470uF-1000uF electrolytic capacitor between 5V and GND

## Geometry

- Plate size: 22.4mm x 34.4mm x 3mm
- Recess depth: 2mm
- Remaining base below recesses: 1mm
- Channel width: 1.45mm
- Pocket clearance parameter: 0.4mm

## Component Body Measurements

These measurements came from the carrier-design request and are encoded in the
OpenSCAD source:

| Component | Body size in layout orientation |
|---|---|
| 20k resistor | 2.5mm wide x 7mm tall |
| 10k resistor | 7mm wide x 2.5mm tall |
| 100nF ceramic capacitor | 4mm wide x 7mm tall |
| Electrolytic capacitor | 11mm wide x 5mm tall |

## Files

- `esp32-d1-mini-servo-feedback-carrier-concept.png` - labeled 2D concept
- `esp32-d1-mini-servo-feedback-carrier.scad` - parametric OpenSCAD source
- `esp32-d1-mini-servo-feedback-carrier.stl` - exported STL
- `esp32-d1-mini-servo-feedback-carrier-preview.png` - OpenSCAD render preview

## Status

This is a provisional carrier because exact wire gauge, lead diameter, solder
joint size, and bend radius have not been measured yet. The layout is compact
and follows the intended no-LED topology: servo feedback passes through the 10k
resistor to the ESP ADC side, and the 20k resistor plus 100nF capacitor both
shunt from that ADC-side node to GND. Confirm physical fit with the actual parts
before relying on the STL for final installation.
