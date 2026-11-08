// VentSys sensor-array power splice carrier
// Glue-down wire carrier in the style of skill-test-servo-wiring-no-led-v16.
//
// ESP32-C6-Zero (left) -> three through rails (uniform width) -> sensor wires (right)
//   3V3 : ESP 3V3 in  -> 10uF + 100nF to GND -> BME680, SDP810, smoke, CO, OLED, LDR
//   GND : ESP GND in  -> both capacitors      -> BME680, SDP810, smoke, CO, OLED
//   LDR : ESP GPIO0   -> 10k to GND           -> LDR (other LDR leg on the 3V3 rail)
// I2C (SDA GPIO4 / SCL GPIO5) and the smoke (GPIO3) / CO (GPIO2) analog lines
// do not pass through this carrier.

$fn = 32;

// ============================================================================
// GLOBAL BOARD SETTINGS
// ============================================================================

layout_x = 32.00;   // [10.00:0.01:80.00]
layout_y = 18.50;   // [10.00:0.01:60.00]
edge_left = 0.00;   // [0.00:0.01:20.00]
edge_right = 0.00;  // [0.00:0.01:20.00]
edge_top = 0.00;    // [0.00:0.01:20.00]
edge_bottom = 0.00; // [0.00:0.01:20.00]

plate_z = 3.00;     // [1.00:0.01:10.00]
recess_d = 2.00;    // [0.50:0.01:5.00]
corner_r = 0.80;    // [0.00:0.01:5.00]

rail_w = 1.50;       // [0.50:0.01:5.00]
branch_w = 0.75;     // [0.25:0.01:3.00]
join_overlap = 0.05; // [0.00:0.01:1.00]

// ============================================================================
// RAIL POSITIONS
// ============================================================================

rail_3v3_y = 1.00;   // [0.00:0.01:50.00]
rail_gnd_y = 10.10;  // [0.00:0.01:50.00]
rail_ldr_y = 16.00;  // [0.00:0.01:50.00]

// ============================================================================
// 10uF CERAMIC POCKET + CHANNELS (radial X7R/X5R 16V, laid flat)
// ============================================================================

cap10_x = 1.00;    // [0.00:0.01:80.00]
cap10_y = 3.30;    // [0.00:0.01:50.00]
cap10_w = 8.50;    // [0.50:0.01:40.00]
cap10_h = 6.00;    // [0.50:0.01:40.00]
cap10_r = 0.40;    // [0.00:0.01:5.00]

cap10_branch_x = 9.35;     // [0.00:0.01:80.00]

cap10_3v3_branch_y = 1.75; // [0.00:0.01:50.00]
cap10_3v3_branch_h = 3.95; // [0.10:0.01:30.00]

cap10_gnd_branch_y = 6.90; // [0.00:0.01:50.00]
cap10_gnd_branch_h = 3.95; // [0.10:0.01:30.00]

// ============================================================================
// 100nF CERAMIC POCKET + CHANNELS
// ============================================================================

cap100_x = 12.00;  // [0.00:0.01:80.00]
cap100_y = 4.30;   // [0.00:0.01:50.00]
cap100_w = 6.50;   // [0.50:0.01:40.00]
cap100_h = 4.00;   // [0.50:0.01:40.00]
cap100_r = 0.30;   // [0.00:0.01:5.00]

cap100_branch_x = 18.35;    // [0.00:0.01:80.00]

cap100_3v3_branch_y = 1.75; // [0.00:0.01:50.00]
cap100_3v3_branch_h = 4.15; // [0.10:0.01:30.00]

cap100_gnd_branch_y = 6.70; // [0.00:0.01:50.00]
cap100_gnd_branch_h = 4.15; // [0.10:0.01:30.00]

// ============================================================================
// 10k LDR PULL-DOWN POCKET + CHANNELS (GND rail -> resistor -> LDR rail)
// ============================================================================

r10k_x = 3.00;   // [0.00:0.01:80.00]
r10k_y = 12.60;  // [0.00:0.01:50.00]
r10k_w = 7.00;   // [0.50:0.01:40.00]
r10k_h = 2.50;   // [0.50:0.01:20.00]
r10k_r = 0.30;   // [0.00:0.01:5.00]

r10k_gnd_drop_x = 1.50;  // [0.00:0.01:80.00]
r10k_gnd_drop_y = 10.85; // [0.00:0.01:50.00]
r10k_gnd_drop_h = 3.38;  // [0.10:0.01:30.00]
r10k_gnd_run_w = 1.55;   // [0.10:0.01:30.00]

r10k_ldr_run_x = 9.95;   // [0.00:0.01:80.00]
r10k_ldr_run_w = 1.50;   // [0.10:0.01:30.00]
r10k_ldr_rise_y = 13.475; // [0.00:0.01:50.00]
r10k_ldr_rise_h = 3.275; // [0.10:0.01:30.00]

// ============================================================================
// DERIVED VALUES
// ============================================================================

origin_x = edge_left;
origin_y = edge_top;
plate_x = layout_x + edge_left + edge_right;
plate_y = layout_y + edge_top + edge_bottom;

rail_3v3_mid = origin_y + rail_3v3_y + rail_w / 2;
rail_gnd_mid = origin_y + rail_gnd_y + rail_w / 2;
rail_ldr_mid = origin_y + rail_ldr_y + rail_w / 2;
r10k_mid_y = r10k_y + r10k_h / 2;

// ============================================================================
// GEOMETRY HELPERS
// ============================================================================

module rounded_rect_2d(x, y, r) {
  hull() {
    translate([r, r]) circle(r = r);
    translate([x - r, r]) circle(r = r);
    translate([r, y - r]) circle(r = r);
    translate([x - r, y - r]) circle(r = r);
  }
}

module rounded_cut(x, y, z, r) {
  linear_extrude(height = z)
    rounded_rect_2d(x, y, min(r, x / 2, y / 2));
}

module recess_rect(x, y, sx, sy, r = 0) {
  translate([x, y, plate_z - recess_d])
    if (r > 0) {
      rounded_cut(sx, sy, recess_d + 0.04, r);
    } else {
      cube([sx, sy, recess_d + 0.04]);
    }
}

module rail(y_pos) {
  recess_rect(-0.02, origin_y + y_pos, plate_x + 0.04, rail_w);
}

module local_recess_rect(x, y, sx, sy, r = 0) {
  recess_rect(origin_x + x, origin_y + y, sx, sy, r);
}

// ============================================================================
// MAIN SOLID
// ============================================================================

difference() {
  rounded_cut(plate_x, plate_y, plate_z, corner_r);

  rail(rail_3v3_y);
  rail(rail_gnd_y);
  rail(rail_ldr_y);

  local_recess_rect(cap10_branch_x, cap10_3v3_branch_y, branch_w, cap10_3v3_branch_h);
  local_recess_rect(cap10_branch_x, cap10_gnd_branch_y, branch_w, cap10_gnd_branch_h);
  local_recess_rect(cap100_branch_x, cap100_3v3_branch_y, branch_w, cap100_3v3_branch_h);
  local_recess_rect(cap100_branch_x, cap100_gnd_branch_y, branch_w, cap100_gnd_branch_h);

  local_recess_rect(cap10_x, cap10_y, cap10_w, cap10_h, cap10_r);
  local_recess_rect(cap100_x, cap100_y, cap100_w, cap100_h, cap100_r);

  // 10k: left lead drops from the GND rail, right lead runs to the LDR rail
  local_recess_rect(r10k_gnd_drop_x, r10k_gnd_drop_y, branch_w, r10k_gnd_drop_h);
  local_recess_rect(r10k_gnd_drop_x, r10k_mid_y - branch_w / 2, r10k_gnd_run_w + join_overlap, branch_w);
  local_recess_rect(r10k_ldr_run_x, r10k_mid_y - branch_w / 2, r10k_ldr_run_w, branch_w);
  local_recess_rect(r10k_ldr_run_x + r10k_ldr_run_w - branch_w, r10k_ldr_rise_y, branch_w, r10k_ldr_rise_h);
  local_recess_rect(r10k_x, r10k_y, r10k_w, r10k_h, r10k_r);
}
