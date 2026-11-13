# VentSys Sensor Array - Power Splice Carrier

Glue-down wire carrier for the sensor-array 3V3 / GND splice, the decoupling
capacitors and the LDR pull-down, built to the same conventions as
`skill-test-servo-wiring-no-led-v16` (through rails, branch channels, component
pockets, concept PNG generated from the SCAD variables).

## Included Topology

- `3V3` pass-through rail: ESP32-C6-Zero 3V3 in, six feeds out (BME680, SDP810, smoke SEN0570, CO SEN0564, OLED, LDR leg 1)
- `GND` pass-through rail: ESP GND in, five grounds out (BME680, SDP810, smoke, CO, OLED)
- `LDR` pass-through rail: ESP GPIO0 in, one wire out to LDR leg 2; a `10k` from this rail to `GND` makes the divider (3V3 -> LDR -> GPIO0 -> 10k -> GND)
- `10uF` ceramic (X7R/X5R, 16V, radial) across `3V3` and `GND`
- `100nF` ceramic across `3V3` and `GND`
- Not on this carrier: I2C (SDA GPIO4 / SCL GPIO5) and the smoke (GPIO3) / CO (GPIO2) analog outputs

## Measurements Used

- `10uF` radial ceramic pocket: `8.5mm W x 6.0mm H` (body laid flat, leads out the right end) - **placeholder, measure your part**
- `100nF` ceramic pocket: `6.5mm W x 4.0mm H` (same as the v16 ceramic pocket)
- `10k` resistor pocket: `7.0mm W x 2.5mm H` (same as the v16 resistor pockets)
- Through rails: `1.5mm`, uniform along the whole board (no widened tap zones)
- Component-to-rail branches: `0.75mm`

## Geometry

- Footprint: `32.0mm x 18.5mm`
- Total height: `3mm`
- Pocket/channel recess depth: `2mm`
- Remaining base below recesses: `1mm`

## Notes

- Each capacitor's leads leave the right end of its pocket; one lead bends up the 3V3 branch, the other down the GND branch. Branches overlap the pocket end by `0.15mm` and run about `2/5` of the pocket height alongside it, as in v16.
- The 100nF sits closest to the sensor end (the high-frequency path); the 10uF is the bulk reservoir.
- The 10k sits between the GND and LDR rails: its left lead drops from GND, its right lead runs down to the LDR rail.
- The sensor wires join the rail wire along the right-hand part of each rail; heat-shrink each joint before pressing it into the recess. `layout_x` can be shortened if less joint length is needed (the last component branch ends at about `x = 19.1mm`).
- Model Y is mirrored relative to the concept PNG (same as v16): the 3V3 rail is at model `y = 1.0`, drawn at the top of the concept.

## Files

- `ventsys_i2c_power_splice.scad`
- `ventsys_i2c_power_splice.json` (Customizer preset `New set 1` = current defaults)
- `ventsys_i2c_power_splice.stl`
- `ventsys_i2c_power_splice_concept.png`
- `ventsys_i2c_power_splice_preview.png`
- `generate_concept.py`

## Tweak Workflow

1. Edit the named variables at the top of `ventsys_i2c_power_splice.scad` (or use the Customizer; all tweak values step in `0.01`).
   - `layout_x` / `layout_y` set the baseline footprint; `edge_left/right/top/bottom` grow the plate outward per edge.
   - `rail_*_y` set the rail positions.
   - `cap10_*` / `cap100_*` / `r10k_*` set pocket position/size and branch placement.
2. Regenerate the concept PNG: `python generate_concept.py`
3. Rebuild the STL / preview in OpenSCAD.

## v2 - feedback-carrier dimensions

`ventsys_i2c_power_splice_v2.scad` is the same circuit (3V3 / GND / LDR rails, 10uF + 100nF
ceramics across 3V3-GND, 10k from GND to the LDR rail) redrawn with the dimensions of
`../Feedback Carrier/ventsys_feedback_carrier.scad`:

- Plate `1.8mm`, recess `0.75mm`, plate corners `0.65mm`, pocket corners `0.35mm`
- `100nF` pocket `4.8 x 5.9mm` and `10k` pocket `6.3 x 2.15mm`, both copied from the feedback carrier
- `10uF` ceramic uses the same `4.8 x 5.9mm` pocket - **measure your part**
- Rails `1.5mm` uniform, leg channels `0.7mm`, `14mm` of extra rail (`joint_len`) for the sensor wire joints
- Footprint `27.1 x 18.55mm`; 3V3 rail on the bottom edge (dimple marks that corner), GND middle, LDR top
- Files: `ventsys_i2c_power_splice_v2.scad`, `.stl`, `_preview.png`
