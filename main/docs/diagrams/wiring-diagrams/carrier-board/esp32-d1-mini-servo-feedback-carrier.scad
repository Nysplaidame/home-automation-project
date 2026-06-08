$fn = 36;

// Compact recessed carrier for ESP32 D1 Mini analog-feedback servo wiring.
// LED section intentionally omitted.

plate_x = 22.4;
plate_y = 34.4;
plate_z = 3;
recess_d = 2;
corner_r = 0.8;
channel_w = 1.45;
join_overlap = 0.2;
fit_clearance = 0.4;

// User-supplied component body dimensions, in board orientation.
r20_w = 2.5;
r20_h = 7;
r10_w = 7;
r10_h = 2.5;
ceramic_w = 4;
ceramic_h = 7;
electrolytic_w = 11;
electrolytic_h = 5;

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

module channel_h(x1, x2, y) {
  recess_rect(min(x1, x2), y - channel_w / 2, abs(x2 - x1), channel_w, 0.18);
}

module channel_v(x, y1, y2) {
  recess_rect(x - channel_w / 2, min(y1, y2), channel_w, abs(y2 - y1), 0.18);
}

module pocket(cx, cy, sx, sy, r = 0.35) {
  recess_rect(
    cx - (sx + fit_clearance) / 2,
    cy - (sy + fit_clearance) / 2,
    sx + fit_clearance,
    sy + fit_clearance,
    r
  );
}

difference() {
  rounded_cut(plate_x, plate_y, plate_z, corner_r);

  // Pass-through exits: ESP side at left, servo side at right.
  channel_h(0, plate_x, 1.8);   // 5V
  channel_h(0, plate_x, 15.2);  // PWM
  channel_h(0, plate_x, 20.3);  // feedback / ADC through 10k
  channel_h(0, plate_x, 32.6);  // GND

  // Shared side channel for 5V/GND/bulk-cap access.
  channel_v(18.0, 1.8 - join_overlap, 32.6 + join_overlap);

  // ADC-side shunt branch. The 20k and 100nF both connect here, then to GND.
  channel_v(5.3, 20.3 - join_overlap, 32.6 + join_overlap);
  channel_h(5.3 - join_overlap, 13.0 + join_overlap, 25.0);
  channel_v(10.1, 25.0 - join_overlap, 32.6 + join_overlap);
  channel_v(13.0, 25.0 - join_overlap, 32.6 + join_overlap);

  // Component pockets.
  pocket(10.7, 7.5, electrolytic_w, electrolytic_h, 0.35);
  pocket(12.2, 20.3, r10_w, r10_h, 0.35);
  pocket(5.3, 29.4, r20_w, r20_h, 0.35);
  pocket(13.0, 29.4, ceramic_w, ceramic_h, 0.35);
}
