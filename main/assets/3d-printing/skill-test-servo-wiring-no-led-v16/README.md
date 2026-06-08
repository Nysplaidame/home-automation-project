# Skill Test Servo Wiring Carrier - No LED V16

Fresh alternate servo no-LED layout using mixed rail and branch channel widths.

## Included Topology

- `5V` pass-through rail from ESP32 to servo
- `GND` pass-through rail shared by servo and feedback network
- `ADC / FB` pass-through rail with `10k` inline on the feedback path
- `PWM` pass-through rail
- `20k` from ADC node to `GND`
- Ceramic capacitor from ADC node to `GND`
- Electrolytic capacitor across `5V` and `GND`

## Measurements Used

- `10k` resistor pocket: `7.0mm W x 2.5mm H`
- `20k` resistor pocket: `7.0mm W x 2.5mm H`
- Electrolytic pocket: `13.0mm W x 5.5mm H`
- Ceramic capacitor pocket: `6.5mm W x 4.0mm H`
- Through rails: `1.5mm`
- Component-to-rail branches: `0.75mm`
- `10k` through channel stays `1.5mm`

## Geometry

- Footprint: `20.8mm x 23.3mm`
- Total height: `3mm`
- Pocket/channel recess depth: `2mm`
- Remaining base below recesses: `1mm`

## Notes

- Electrolytic `5V` and `GND` branches are vertically aligned on the right and slightly overlap the pocket edge.
- The upper and lower electrolytic branches each run about `2/5` of the pocket height alongside the pocket.
- The lower cluster is intentionally free to shift around for readability rather than being locked to earlier layouts.

## Files

- `servo_wiring_no_led_v16_concept.png`
- `servo_wiring_no_led_v16.scad`
- `servo_wiring_no_led_v16.stl`
- `servo_wiring_no_led_v16_preview.png`
- `generate_concept.py`

## Tweak Workflow

1. Edit the named variables at the top of `servo_wiring_no_led_v16.scad`.
   - `layout_x` / `layout_y` set the baseline solved footprint.
   - `edge_left`, `edge_right`, `edge_top`, `edge_bottom` let you grow the plate outward from each edge independently.
   - Pocket positions/sizes and channel positions/sizes are now exposed as direct numeric values wherever practical.
2. Regenerate the concept PNG:
   - `python generate_concept.py`
3. Rebuild the STL / preview in OpenSCAD.

The SCAD now exposes board size, rail positions, pocket positions/sizes, and
branch geometry as named parameters. The concept PNG reads those variables
directly so the drawing stays aligned with the model inputs.

If you use the OpenSCAD Customizer, the main tweak variables now include
clean range/step comments so they can be adjusted in `0.01` increments from the UI.
