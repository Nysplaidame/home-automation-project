// Servo feedback carrier V16
// Rebuilt cleanly from saved V16 parameters after corrupt source recovery.

$fn = 32;

// ============================================================================
// GLOBAL BOARD SETTINGS
// ============================================================================

layout_x = 22.30;   // [10.00:0.01:60.00]
layout_y = 23.30;   // [10.00:0.01:60.00]
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

rail_5v_y  = 1.00;   // [0.00:0.01:40.00]
rail_gnd_y = 9.00;   // [0.00:0.01:40.00]
rail_adc_y = 16.30;  // [0.00:0.01:40.00]
rail_pwm_y = 20.80;  // [0.00:0.01:40.00]

// ============================================================================
// ELECTROLYTIC POCKET + CHANNELS
// ============================================================================

elcap_x = 2.50;    // [0.00:0.01:40.00]
elcap_y = 2.90;    // [0.00:0.01:40.00]
elcap_w = 13.00;   // [0.50:0.01:40.00]
elcap_h = 5.50;    // [0.50:0.01:40.00]
elcap_r = 0.45;    // [0.00:0.01:5.00]

elcap_branch_x = 15.35; // [0.00:0.01:40.00]

elcap_5v_branch_y = 1.75; // [0.00:0.01:40.00]
elcap_5v_branch_h = 3.35; // [0.10:0.01:20.00]

elcap_gnd_branch_y = 6.20; // [0.00:0.01:40.00]
elcap_gnd_branch_h = 3.55; // [0.10:0.01:20.00]

// ============================================================================
// 20K POCKET + LEFT GND ELBOW
// ============================================================================

r20k_x = 3.10;   // [0.00:0.01:40.00]
r20k_y = 11.90;  // [0.00:0.01:40.00]
r20k_w = 7.00;   // [0.50:0.01:40.00]
r20k_h = 2.50;   // [0.50:0.01:20.00]
r20k_r = 0.30;   // [0.00:0.01:5.00]

left_gnd_drop_x = 1.10; // [0.00:0.01:40.00]
left_gnd_drop_y = 9.75; // [0.00:0.01:40.00]
left_gnd_drop_h = 3.30; // [0.10:0.01:20.00]

left_gnd_run_x = 1.10;  // [0.00:0.01:40.00]
left_gnd_run_y = 13.05; // [0.00:0.01:40.00]
left_gnd_run_w = 2.45;  // [0.10:0.01:20.00]

r20k_fb_run_x = 10.10; // [0.00:0.01:40.00]
r20k_fb_run_y = 13.05; // [0.00:0.01:40.00]
r20k_fb_run_w = 1.50;  // [0.10:0.01:20.00]

// ============================================================================
// SHARED VERTICAL FB BRANCH
// ============================================================================

shared_fb_x = 11.50;  // [0.00:0.01:40.00]
shared_fb_y = 11.35;  // [0.00:0.01:40.00]
shared_fb_h = 5.78;   // [0.10:0.01:20.00]

// ============================================================================
// CERAMIC POCKET + CHANNELS
// ============================================================================

ceramic_x = 13.60;  // [0.00:0.01:40.00]
ceramic_y = 11.40;  // [0.00:0.01:40.00]
ceramic_w = 6.50;   // [0.50:0.01:40.00]
ceramic_h = 4.00;   // [0.50:0.01:20.00]
ceramic_r = 0.30;   // [0.00:0.01:5.00]

ceramic_fb_run_x = 11.50; // [0.00:0.01:40.00]
ceramic_fb_run_y = 11.40; // [0.00:0.01:40.00]
ceramic_fb_run_w = 2.45;  // [0.10:0.01:20.00]

right_gnd_drop_x = 20.45; // [0.00:0.01:40.00]
right_gnd_drop_y = 9.75;  // [0.00:0.01:40.00]
right_gnd_drop_h = 1.80;  // [0.10:0.01:20.00]

right_gnd_run_x = 19.75;  // [0.00:0.01:40.00]
right_gnd_run_y = 11.40;  // [0.00:0.01:40.00]
right_gnd_run_w = 1.10;   // [0.10:0.01:20.00]

// ============================================================================
// 10K POCKET
// ============================================================================

r10k_x = 13.80;   // [0.00:0.01:40.00]
r10k_y = 15.80;   // [0.00:0.01:40.00]
r10k_w = 7.00;    // [0.50:0.01:40.00]
r10k_h = 2.50;    // [0.50:0.01:20.00]
r10k_r = 0.30;    // [0.00:0.01:5.00]

// ============================================================================
// DERIVED VALUES
// ============================================================================

origin_x = edge_left;
origin_y = edge_top;
plate_x = layout_x + edge_left + edge_right;
plate_y = layout_y + edge_top + edge_bottom;

rail_5v_mid  = origin_y + rail_5v_y  + rail_w / 2;
rail_gnd_mid = origin_y + rail_gnd_y + rail_w / 2;
rail_adc_mid = origin_y + rail_adc_y + rail_w / 2;
rail_pwm_mid = origin_y + rail_pwm_y + rail_w / 2;

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
  recess_rect(0, origin_y + y_pos, plate_x, rail_w);
}

module local_recess_rect(x, y, sx, sy, r = 0) {
  recess_rect(origin_x + x, origin_y + y, sx, sy, r);
}

// ============================================================================
// MAIN SOLID
// ============================================================================

difference() {
  rounded_cut(plate_x, plate_y, plate_z, corner_r);

  rail(rail_5v_y);
  rail(rail_gnd_y);
  rail(rail_adc_y);
  rail(rail_pwm_y);

  local_recess_rect(left_gnd_drop_x, left_gnd_drop_y, branch_w, left_gnd_drop_h);
  local_recess_rect(left_gnd_run_x, left_gnd_run_y, left_gnd_run_w, branch_w);

  local_recess_rect(shared_fb_x, shared_fb_y, branch_w, shared_fb_h + join_overlap);
  local_recess_rect(r20k_fb_run_x, r20k_fb_run_y, r20k_fb_run_w + join_overlap, branch_w);
  local_recess_rect(ceramic_fb_run_x, ceramic_fb_run_y, ceramic_fb_run_w + join_overlap, branch_w);

  local_recess_rect(right_gnd_drop_x, right_gnd_drop_y, branch_w, right_gnd_drop_h + join_overlap);
  local_recess_rect(right_gnd_run_x, right_gnd_run_y, right_gnd_run_w + join_overlap, branch_w);

  local_recess_rect(elcap_branch_x, elcap_5v_branch_y, branch_w, elcap_5v_branch_h);
  local_recess_rect(elcap_branch_x, elcap_gnd_branch_y, branch_w, elcap_gnd_branch_h);

  local_recess_rect(elcap_x, elcap_y, elcap_w, elcap_h, elcap_r);
  local_recess_rect(r20k_x, r20k_y, r20k_w, r20k_h, r20k_r);
  local_recess_rect(ceramic_x, ceramic_y, ceramic_w, ceramic_h, ceramic_r);
  local_recess_rect(r10k_x, r10k_y, r10k_w, r10k_h, r10k_r);
}
