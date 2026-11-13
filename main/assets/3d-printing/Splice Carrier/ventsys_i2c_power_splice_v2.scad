// VentSys sensor-array power splice carrier, v2 - fully editable
// Glue-down wire carrier: 3V3 / GND / LDR rails, 10uF + 100nF ceramics across 3V3-GND,
// 10k from GND to the LDR rail. Dimensions follow ventsys_feedback_carrier.scad
// (rounded to 0.1 mm). Every feature below has its own labelled group; all values are in mm.
//
// Frame: origin = plate bottom-left corner, X to the right, Y up. Positions are the
// bottom-left corner of a feature. Channels overlap their pocket/rail by 0.1 mm so
// they join cleanly - keep that overlap when you move things.
//   Y up:  LDR rail (top) / 10k / GND rail (middle) / capacitors / 3V3 rail (bottom)
// No text, no raised pads, no rim. Print flat side down, 0.2 mm layers, no supports.

$fn = 32;

/* [1. Plate] */
plate_x  = 27.1;  // [5:0.1:80]
plate_y  = 18.6;  // [5:0.1:60]
plate_z  = 1.8;   // [0.6:0.1:6]
corner_r = 0.7;   // [0:0.1:5]
// Depth of every pocket and channel (leaves plate_z - recess_d underneath)
recess_d = 0.8;   // [0.2:0.1:5]

/* [2. 3V3 rail (bottom)] */
rail_3v3_enable = true;
rail_3v3_x = 0.0;   // [0:0.1:80]
rail_3v3_y = 1.0;   // [0:0.1:60]
rail_3v3_len = 27.1; // [1:0.1:80]
rail_3v3_w = 1.5;   // [0.4:0.1:5]

/* [3. GND rail (middle)] */
rail_gnd_enable = true;
rail_gnd_x = 0.0;   // [0:0.1:80]
rail_gnd_y = 10.4;  // [0:0.1:60]
rail_gnd_len = 27.1; // [1:0.1:80]
rail_gnd_w = 1.5;   // [0.4:0.1:5]

/* [4. LDR rail (top)] */
rail_ldr_enable = true;
rail_ldr_x = 0.0;   // [0:0.1:80]
rail_ldr_y = 16.1;  // [0:0.1:60]
rail_ldr_len = 27.1; // [1:0.1:80]
rail_ldr_w = 1.5;   // [0.4:0.1:5]

/* [5. 10uF ceramic - pocket] */
cap10_enable = true;
cap10_x = 1.0;  // [0:0.1:80]
cap10_y = 3.5;  // [0:0.1:60]
cap10_w = 4.8;  // [1:0.1:30]
cap10_l = 5.9;  // [1:0.1:30]
cap10_r = 0.4;  // [0:0.1:3]

/* [6. 10uF ceramic - leg channel to 3V3 rail] */
cap10_3v3_x  = 3.1;  // [0:0.1:80]
cap10_3v3_y  = 2.4;  // [0:0.1:60]
cap10_3v3_sx = 0.7;  // [0.2:0.1:5]
cap10_3v3_sy = 1.2;  // [0.2:0.1:30]

/* [7. 10uF ceramic - leg channel to GND rail] */
cap10_gnd_x  = 3.1;  // [0:0.1:80]
cap10_gnd_y  = 9.3;  // [0:0.1:60]
cap10_gnd_sx = 0.7;  // [0.2:0.1:5]
cap10_gnd_sy = 1.2;  // [0.2:0.1:30]

/* [8. 100nF ceramic - pocket] */
cap100_enable = true;
cap100_x = 7.3;  // [0:0.1:80]
cap100_y = 3.5;  // [0:0.1:60]
cap100_w = 4.8;  // [1:0.1:30]
cap100_l = 5.9;  // [1:0.1:30]
cap100_r = 0.4;  // [0:0.1:3]

/* [9. 100nF ceramic - leg channel to 3V3 rail] */
cap100_3v3_x  = 9.4;  // [0:0.1:80]
cap100_3v3_y  = 2.4;  // [0:0.1:60]
cap100_3v3_sx = 0.7;  // [0.2:0.1:5]
cap100_3v3_sy = 1.2;  // [0.2:0.1:30]

/* [10. 100nF ceramic - leg channel to GND rail] */
cap100_gnd_x  = 9.4;  // [0:0.1:80]
cap100_gnd_y  = 9.3;  // [0:0.1:60]
cap100_gnd_sx = 0.7;  // [0.2:0.1:5]
cap100_gnd_sy = 1.2;  // [0.2:0.1:30]

/* [11. 10k resistor - pocket] */
res_enable = true;
res_x = 1.7;   // [0:0.1:80]
res_y = 12.9;  // [0:0.1:60]
res_w = 6.3;   // [1:0.1:30]
res_h = 2.2;   // [0.5:0.1:15]
res_r = 0.4;   // [0:0.1:3]

/* [12. 10k resistor - left lead: vertical channel up from the GND rail] */
res_left_up_x  = 1.0;  // [0:0.1:80]
res_left_up_y  = 11.8; // [0:0.1:60]
res_left_up_sx = 0.7;  // [0.2:0.1:5]
res_left_up_sy = 2.6;  // [0.2:0.1:30]

/* [13. 10k resistor - left lead: join into the pocket] */
res_left_join_x  = 1.0;  // [0:0.1:80]
res_left_join_y  = 13.7; // [0:0.1:60]
res_left_join_sx = 0.8;  // [0.2:0.1:10]
res_left_join_sy = 0.7;  // [0.2:0.1:5]

/* [14. 10k resistor - right lead: join out of the pocket] */
res_right_join_x  = 7.9;  // [0:0.1:80]
res_right_join_y  = 13.7; // [0:0.1:60]
res_right_join_sx = 0.9;  // [0.2:0.1:10]
res_right_join_sy = 0.7;  // [0.2:0.1:5]

/* [15. 10k resistor - right lead: vertical channel up to the LDR rail] */
res_right_up_x  = 8.0;  // [0:0.1:80]
res_right_up_y  = 13.7; // [0:0.1:60]
res_right_up_sx = 0.7;  // [0.2:0.1:5]
res_right_up_sy = 2.5;  // [0.2:0.1:30]

/* [16. Orientation dimple (3V3 side)] */
dimple_enable = true;
dimple_x = 0.5;   // [0:0.1:80]
dimple_y = 0.5;   // [0:0.1:60]
dimple_d = 0.6;   // [0.2:0.1:3]
dimple_depth = 0.4; // [0.1:0.1:2]

// ---------------------------------------------------------------------------
module rrect2d(x, y, r) {
  hull() for (i = [r, x - r], j = [r, y - r]) translate([i, j]) circle(r = r);
}
module recess(x, y, sx, sy, r = 0) {
  translate([x, y, plate_z - recess_d])
    linear_extrude(height = recess_d + 0.1)
      if (r > 0) rrect2d(sx, sy, min(r, sx / 2, sy / 2)); else square([sx, sy]);
}
// rail: runs off the plate edge where it reaches it, so the ends stay open
module rail(en, x, y, len, w) {
  if (en) {
    x0 = x <= 0 ? -0.1 : x;
    x1 = (x + len) >= plate_x ? plate_x + 0.1 : x + len;
    recess(x0, y, x1 - x0, w);
  }
}

difference() {
  linear_extrude(height = plate_z) rrect2d(plate_x, plate_y, min(corner_r, plate_x / 2, plate_y / 2));

  rail(rail_3v3_enable, rail_3v3_x, rail_3v3_y, rail_3v3_len, rail_3v3_w);
  rail(rail_gnd_enable, rail_gnd_x, rail_gnd_y, rail_gnd_len, rail_gnd_w);
  rail(rail_ldr_enable, rail_ldr_x, rail_ldr_y, rail_ldr_len, rail_ldr_w);

  if (cap10_enable) {
    recess(cap10_x, cap10_y, cap10_w, cap10_l, cap10_r);
    recess(cap10_3v3_x, cap10_3v3_y, cap10_3v3_sx, cap10_3v3_sy);
    recess(cap10_gnd_x, cap10_gnd_y, cap10_gnd_sx, cap10_gnd_sy);
  }
  if (cap100_enable) {
    recess(cap100_x, cap100_y, cap100_w, cap100_l, cap100_r);
    recess(cap100_3v3_x, cap100_3v3_y, cap100_3v3_sx, cap100_3v3_sy);
    recess(cap100_gnd_x, cap100_gnd_y, cap100_gnd_sx, cap100_gnd_sy);
  }
  if (res_enable) {
    recess(res_x, res_y, res_w, res_h, res_r);
    recess(res_left_up_x, res_left_up_y, res_left_up_sx, res_left_up_sy);
    recess(res_left_join_x, res_left_join_y, res_left_join_sx, res_left_join_sy);
    recess(res_right_join_x, res_right_join_y, res_right_join_sx, res_right_join_sy);
    recess(res_right_up_x, res_right_up_y, res_right_up_sx, res_right_up_sy);
  }
  if (dimple_enable)
    translate([dimple_x, dimple_y, plate_z - dimple_depth]) cylinder(d = dimple_d, h = dimple_depth + 0.1);
}
echo(str("Plate ", plate_x, " x ", plate_y, " x ", plate_z, " mm"));
