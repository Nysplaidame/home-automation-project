// VentSys servo feedback network carrier, V2
// Compact 11mm x 12.4mm glue-down carrier for:
//   servo feedback -> 10k -> ADC
//                         |
//                       node
//                      /    \
//                 20k to GND  100nF to GND
//
// The STL intentionally has no text, no raised pads, and no perimeter rim.
// Channels and component pockets are recessed so wires can stay on one plane.

$fn = 32;

plate_x = 11.0;
plate_y = 12.4;
plate_z = 1.8;
corner_r = 0.65;

recess_d = 0.75;

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

module recess_rect(x, y, sx, sy, depth, r = 0) {
  translate([x, y, plate_z - depth])
    if (r > 0) {
      rounded_cut(sx, sy, depth + 0.04, r);
    } else {
      cube([sx, sy, depth + 0.04]);
    }
}

difference() {
  rounded_cut(plate_x, plate_y, plate_z, corner_r);

  // Recessed wire channels, all open to edges where external wires enter/exit.
  recess_rect(0, 1.8, 11.0, 0.85, recess_d);     // ADC <-> 10k <-> FB
  recess_rect(2.05, 1.8, 0.7, 9.98, recess_d);   // 20k leg down to GND
  recess_rect(4.9, 3.7, 0.7, 8.08, recess_d);    // 100nF leg down to GND
  recess_rect(2.05, 3.7, 3.2, 0.7, recess_d);    // capacitor branch to node
  recess_rect(0, 10.83, 11.0, 0.95, recess_d);   // GND bus

  // Recessed component body pockets.
  recess_rect(3.45, 0.95, 6.3, 2.15, recess_d, 0.35);  // 10k resistor
  recess_rect(1.15, 5.0, 2.5, 4.75, recess_d, 0.35);   // 20k resistor
  recess_rect(5.25, 4.3, 4.8, 5.9, recess_d, 0.35);    // 100nF capacitor
}
