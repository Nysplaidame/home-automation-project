// =====================================================================
//  VentSys sensor carrier case  -  fully parametric (OpenSCAD)   v11
//
//  Holds: ESP32-C6-Zero, Pimoroni BME680 breakout, DFRobot SEN0570 smoke/VOC sensor,
//  and a CO sensor (same size and layout as the smoke sensor).
//  Boards face UP, header pins point UP (connectors plug in from above).
//
//  HOW THE BOARDS ARE HELD (copied from your VentSys example files)
//   * Sensor boards: each sits in a pocket with its SENSOR END facing a case
//     wall opening.  Heat-set insert holes (3.2 mm, 4.2 mm chamfer) sit at
//     the board's notches; a bolt head overlaps the board edge and clamps it.
//   * Pimoroni BME680: its two screw holes sit inside the board at the sensor
//     end; a bolt goes through each hole into a heat-set insert beneath.
//   * Pin headers: a channel under/next to each board's pin edge leaves room
//     for the solder joints and pins.
//   * ESP32: a boss with an insert hole sits just past the end of the board;
//     a small flat RETAINER CLIP bolts onto it and overlaps the board end.
//   * Case lid: bolted to heat-set inserts in the four corner ears.
//   * SDP810 differential pressure sensor (optional): stands against a wall
//     with its necks in two slots, flanges outside, in a floor pocket (end lips
//     plus a low back lip clear of its snap hooks), raised on a seat so the
//     lid underside holds it down. The lid lip is cut away above it.
//   * Mounting tabs (optional): one at the middle of each outside wall, at
//     floor level, with a countersunk screw hole to fix the case to a surface.
//   * 0.96" OLED (optional): sits ON TOP of the lid inside a low surround, on
//     four standoffs (M2 self-tapping screws); only its 4-pin header goes
//     through a slot into the cavity. GL5528 LDR (optional): pocket under the
//     lid, looking out through a small hole beside the display.
//
//  HOW TO USE
//   * Window > Customizer.  Settings are numbered groups.  Values marked
//     [MEASURE] are assumptions - check against your real boards.
//   * "part_to_generate": assembly (preview), base, lid, retainer_clip, or
//     all_parts_flat (everything laid out for printing).
//   * Board frame (used by the sensor settings): X runs from the board's
//     BACK / PIN edge (x = 0) to its SENSOR END; Y runs across the width.
//   * Case frame: X = case length, Y = width, Z = up.  The ESP's USB end is
//     the -X end.  Origin = inside corner of the cavity, at floor level.
// =====================================================================

/* [1. Part to generate and preview] */
// What to output
part_to_generate = "all_parts_flat"; // [assembly, base, lid, retainer_clip, oled_bezel, all_parts_flat]
// Slice the model in half to look inside (preview only)
show_cutaway_view = false;
// Show coloured stand-ins for the boards (assembly preview only)
show_board_ghosts = false;
// Gap between parts when part_to_generate = all_parts_flat
spacing_between_parts_when_flat = 12;
// Curve smoothness (higher = smoother, slower)
curve_smoothness = 48;
$fn = curve_smoothness;

/* [2. Case shell] */
// Thickness of the four outer walls
wall_thickness = 2;
// Thickness of the floor
floor_thickness = 2;
// Radius of the vertical outside corners (0 = square)
outer_corner_radius = 2;
// Cavity height (floor top to lid underside). 0 = work it out automatically from the tallest part
cavity_height_override = 0;
// Extra space above the tallest part when the height is automatic
headroom_above_tallest_part = 3;
// Force cavity length along X. 0 = automatic
cavity_length_override = 0;
// Force cavity width along Y. 0 = automatic
cavity_width_override = 0;
// Spare space left at each X end of the cavity (automatic sizing)
spare_space_each_x_end = 0.1;
// Spare space left at each Y side of the cavity (automatic sizing)
spare_space_each_y_side = 1.1;

/* [3. Layout of the boards] */
// "single_row": ESP then sensors in one line along X.  "two_rows": ESP along the front, sensors along the back
layout_style = "two_rows"; // [single_row, two_rows]
// Space between the ESP block and the first sensor (single_row) or between the two rows (two_rows). More = less ESP heat reaching the BME680
gap_between_esp_and_sensors = 3;
// Space between neighbouring sensor blocks
gap_between_sensor_blocks = 2;
// Sensor in the position nearest the ESP
sensor_position_1 = "smoke"; // [bme, smoke, co, none]
// Sensor in the middle position
sensor_position_2 = "bme"; // [bme, smoke, co, none]
// Sensor in the position farthest from the ESP (best for the BME680: least ESP heat)
sensor_position_3 = "co"; // [bme, smoke, co, none]
// two_rows only: X position where the sensor row starts
two_rows_sensor_row_start_x = 2;

/* [3b. Move individual boards (fine adjustment, mm)] */
// Line the sensor blocks up inside their row: centre (as before), or push them all against the +Y or -Y side of the row (two_rows: +Y = the wall the sensors face)
sensor_row_alignment = "centre"; // [centre, toward_plus_y, toward_minus_y]
// Move the ESP block along X (+ = away from the USB wall). The USB opening follows
esp_offset_x = 1.1;
// Move the ESP block along Y. The USB opening follows"xkcd:aqua marine"
esp_offset_y = 1.1;
// Move the BME680 block along X
bme_offset_x = -1.1;
// Move the BME680 block along Y
bme_offset_y = 0.1;
// Move the smoke sensor block along X
smoke_offset_x = -1.1;
// Move the smoke sensor block along Y
smoke_offset_y = 3.1;
// Move the CO sensor block along X
co_offset_x = -1.1;
// Move the CO sensor block along Y
co_offset_y = 3.1;
// Grow the cavity automatically when a moved block would hit a wall (off = cavity size stays as calculated before the moves)
cavity_grows_to_fit_moved_blocks = true;

/* [4. Lid] */
// Lid plate thickness
lid_thickness = 1.5;
// Add a lip under the lid that fits inside the walls
lid_lip_enable = true;
// How far the lip hangs down
lid_lip_height = 2;
// Wall thickness of the lip
lid_lip_wall_thickness = 1.5;
// Gap between the lip and the inside of the case walls
lid_lip_gap_to_walls = 0.1;

/* [5. Corner ears: heat-set inserts that hold the lid bolts] */
// Add the four corner ears
corner_ears_enable = true;
// Outside diameter of each ear
corner_ear_diameter = 6;
// How far each ear centre sits outside the case corner (0 = centred on the corner)
corner_ear_offset_outward = -1;
// Heat-set insert hole diameter in the base ears (3.2 = your housing file)
corner_insert_hole_diameter = 3.2;
// Chamfered mouth diameter at the hole entrance (4.2 = your housing file)
corner_insert_mouth_diameter = 3.2;
// Insert hole depth (insert length + about 1.5 mm)
corner_insert_hole_depth = 4;
// Bolt clearance hole through the lid ears (M2.5 = 2.9)
lid_bolt_hole_diameter = 2.2;
// Recess in the lid top for the bolt head (0 = none)
lid_bolt_head_recess_diameter = 4;
// Depth of that recess
lid_bolt_head_recess_depth = 0.6;

/* [5b. Mounting tabs: screw the whole case to a surface] */
// Add a mounting tab with a screw hole at the middle of each outside wall (floor level)
mounting_tabs_enable = true;
// Tab on the -X wall (USB end)
mounting_tab_minus_x = true;
// Tab on the +X wall
mounting_tab_plus_x = true;
// Tab on the -Y wall
mounting_tab_minus_y = true;
// Tab on the +Y wall
mounting_tab_plus_y = true;
// Tab thickness (height above the bed)
mounting_tab_thickness = 3;
// Tab width, and the diameter of its rounded end
mounting_tab_width = 11;
// Distance from the outside of the wall to the screw hole centre
mounting_hole_distance_from_wall = 6;
// Screw clearance hole diameter (3.5 suits M3 or No.6 wood screws)
mounting_hole_diameter = 3.5;
// Countersink diameter at the top of the hole for a countersunk screw head (0 = plain hole)
mounting_countersink_diameter = 7;
// Slide the X-wall tabs along Y from the middle of the wall
mounting_tab_shift_along_x_walls = 0;
// Slide the Y-wall tabs along X from the middle of the wall
mounting_tab_shift_along_y_walls = 0;

/* [6. Heat-set inserts for the sensor boards and ESP clip] */
// Insert hole diameter (3.2 = your insert file)
board_insert_hole_diameter = 3.2;
// Chamfered mouth diameter (4.2 = your housing file)
board_insert_mouth_diameter = 4.2;
// Maximum insert hole depth (5.5 = your insert file). Automatically limited so the hole never breaks through the underside
board_insert_hole_depth = 8;
// Diameter of the raised round boss around each insert hole
board_insert_boss_diameter = 6.4;
// How far BELOW the PCB underside the top of each heat-set insert sits (0 = flush with the underside; raise it for more clearance)
board_insert_top_below_pcb_underside = 0;
// Corner radius of every sensor board slot (0 = square corners)
slot_corner_radius = 1;

/* [7. ESP32-C6-Zero board] */
// Board length along X (23.5 nominal, 23.37 measured)
esp_board_length_x = 23.5;
// Board width along Y (18 nominal, 17.78 measured)
esp_board_width_y = 18;
// PCB thickness  [MEASURE]
esp_pcb_thickness = 1;
// Fit clearance added around the board on every side
esp_fit_clearance = 0.3;
// Height from the underside of the PCB to the tallest component (9.9 per spec)
esp_total_height = 9.9;
// Height of the platform the board sits on. Must be taller than the solder tails under the board (typically 1.5 to 3 mm)
esp_platform_height = 2;
// Rim around the board: wall thickness
esp_rim_wall_thickness = 1.5;
// Rim around the board: how far it stands up above the PCB top face
esp_rim_height_above_pcb = 0.8;

/* [8. ESP32 pin headers (soldered pins-up)] */
// Are pin headers fitted? (affects grooves, lid windows, cavity height)
esp_has_pin_headers = true;
// Pins per header row  [MEASURE]
esp_header_pins_per_row = 9;
// Distance between pins
esp_header_pin_pitch = 2.54;
// Distance between the two header rows, centre to centre  [MEASURE]
esp_header_row_spacing = 15.24;
// Distance from the USB end of the board to the first header pin  [MEASURE]
esp_header_start_from_usb_end = 0.32;
// Height of the black plastic header body (sits on TOP of the PCB)
esp_header_plastic_height = 2.54;
// How far the pins stick up above the plastic body
esp_header_pin_height_above_plastic = 6;
// Cut grooves in the platform so the solder tails under the board do not hold it up
esp_cut_grooves_for_solder_tails = true;
// Width of each groove (one under each header row)
esp_solder_tail_groove_width = 3.2;
// Cut grooves deeper than the platform, into the floor
esp_solder_tail_groove_extra_depth = 0;
// Clear a window under the board between the header rows (for parts on the underside)
esp_clear_window_under_board = false;

/* [9. ESP32 retainer clip (bolts onto a boss to hold the board)] */
// Add the boss, insert hole and clip
esp_retainer_enable = true;
// Distance from the END of the board (away from USB) to the centre of the insert hole  (housing file: about 4)
esp_retainer_hole_distance_from_board_end = 4;
// How far the clip reaches over the board end
esp_retainer_clip_overlap_on_board = 6;
// Clip width
esp_retainer_clip_width = 5;
// Clip thickness
esp_retainer_clip_thickness = 1.5;
// Bolt hole diameter in the clip (M2.5 = 2.9)
esp_retainer_clip_bolt_hole_diameter = 2.9;
// Retainer boss top height relative to the top of the surrounding rim (0 = flat with the rim, so the whole area is one flat surface for the clip to sit on)
esp_retainer_boss_top_relative_to_pcb_top = 1;
// Open the rim at the antenna end (turn off if the clip sits there)
esp_open_rim_at_antenna_end = false;
// Length of rim removed at the antenna end
esp_open_rim_length = 5;

/* [10. USB cable opening in the -X wall (same size as your housing)] */
// Opening width (9.4 measured from housing file)
usb_opening_width = 9;
// Opening height (3.9 measured from housing file)
usb_opening_height = 3;
// Height of the opening centre above the PCB top face (USB-C socket centre is about 1.6)
usb_opening_centre_above_pcb = 0;
// Shift the opening sideways from the board centre (+ = toward +Y)
usb_opening_shift_sideways = 0;
// Corner radius of the opening
usb_opening_corner_radius = 1;

/* [11. Pimoroni BME680 breakout] */
// Which case wall the SENSOR END (the end away from the pins, with the two screw holes) faces. Its air opening is cut in that wall
bme_sensor_end_faces = "+Y"; // [+Y, -Y, +X, -X]
// Board length from the pin edge to the sensor end (19 mm)
bme_board_length = 19;
// Board width, measured between the edges at the two ends of the pin row (19 mm)
bme_board_width = 19;
// PCB thickness (19 x 19 x 2.75 mm overall height per Pimoroni; the PCB itself is probably 1.6)  [MEASURE]
bme_pcb_thickness = 1.6;
// Fit clearance added around the board
bme_fit_clearance = 0.3;
// Height of the platform the board sits on
bme_platform_height = 3;
// Rim around the pocket: wall thickness
bme_rim_wall_thickness = 1.5;
// Rim height above the PCB top face
bme_rim_height_above_pcb = 0;
// Pin section recess: length of the narrower section, measured from the pin edge (6 mm)
bme_pin_section_length = 6;
// Pin section recess: how much narrower on EACH side (2 mm)
bme_pin_section_inset_each_side = 2;
// Screw holes through the board (at the two sensor-end corners): hole diameter  [MEASURE]
bme_screw_hole_diameter = 2;
// Screw holes: gap from the edge of the hole to the sensor-end edge and to the side edges (1.8 mm)
bme_screw_hole_edge_to_board_edge = 1.2;
// Heat-set insert holes: move BOTH holes together along the board length (+ = towards the sensor end)
bme_insert_offset_x = 0;
// Heat-set insert holes: move BOTH holes together across the board width
bme_insert_offset_y = 0;
// Heat-set insert holes: change the distance between the two holes (+ = further apart, - = closer)
bme_insert_spacing_adjust = 0.1;
// Pin header: number of pins (the Pimoroni kit has a 1x5 header)
bme_pin_count = 5;
// Pin header: distance from the pin edge to the pin centre line  [MEASURE]
bme_pin_row_distance_from_back_edge = 1.5;
// Pin channel under the board: how far it reaches in from the pin edge
bme_pin_channel_inboard_length = 5;
// Pin channel: how far it reaches out past the pin edge (0 = none)
bme_pin_channel_outward_length = 0;
// Pin channel depth BELOW the underside of the PCB (about 2 mm for the solder joints)
bme_pin_channel_depth = 2;
// Pin channel width = pins x pitch plus this extra (keep it inside the narrower pin section)
bme_pin_channel_extra_width = 2;
// Cut a window under the middle of the board (lets air reach the gas sensor)
bme_cut_window_under_board = true;
// Support ledge left around that window (keep it big enough to leave material around the two screw-hole inserts)
bme_window_ledge_width = 4;
// Window goes right through the floor
bme_window_goes_through_floor = true;

/* [12. Smoke sensor (DFRobot SEN0570) and CO sensor (same size and layout)] */
// Which case wall the SENSOR END (side opposite the pin edge) faces. Notch holes then run parallel to that wall
smoke_sensor_end_faces = "+Y"; // [+Y, -Y, +X, -X]
// Board length from the PIN edge to the sensor end (13 x 13 x 2.5 per DFRobot)
smoke_board_length = 13;
// Board width across
smoke_board_width = 13;
// PCB thickness  [MEASURE - DFRobot only lists 2.5 mm overall height]
smoke_pcb_thickness = 1.6;
// Fit clearance added around the board
smoke_fit_clearance = 0.3;
// Height of the platform the board sits on
smoke_platform_height = 3;
// Rim around the pocket: wall thickness
smoke_rim_wall_thickness = 1.5;
// Rim height above the PCB top face (0 = flush)
smoke_rim_height_above_pcb = 0;
// Where the half-round notches / insert holes are (your insert file: middle of the two side edges)
smoke_notch_positions = "one_on_each_side_edge"; // [two_on_back_edge, two_on_sensor_end_edge, one_on_each_side_edge, one_on_back_and_sensor_end_edges, none]
// Distance between notches when two are on the same edge
smoke_notch_spacing = 11.4;
// Insert hole centre distance in from the board edge (0.15 in your insert file)
smoke_notch_hole_distance_in_from_edge = 0.15;
// Heat-set insert holes: move BOTH holes together along the board length (+ = towards the sensor end). Smoke and CO
smoke_insert_offset_x = 0;
// Heat-set insert holes: move BOTH holes together across the board width. Smoke and CO
smoke_insert_offset_y = 0;
// Heat-set insert holes: change the distance between the two holes (+ = further apart, - = closer). Smoke and CO
smoke_insert_spacing_adjust = 0;
// Diameter of the clear area left around each hole for the board notch
smoke_notch_clearance_diameter = 3.6;
// Pin header: number of castellated pins (A, VCC, GND)
smoke_pin_count = 3;
// Pin header: distance from the pin edge to the pin centre line  [MEASURE]
smoke_pin_row_distance_from_back_edge = 0.8;
// Pin channel width across (10 in your insert file, centred)
smoke_pin_channel_width = 10;
// Pin channel: how far it reaches in under the board from the pin edge
smoke_pin_channel_inboard_length = 2.5;
// Pin channel: how far it reaches out past the pin edge (5.8 in your insert file)
smoke_pin_channel_outward_length = 0;
// Pin channel depth below the underside of the PCB
smoke_pin_channel_depth = 2;
// Cut a window under the middle of the board
smoke_cut_window_under_board = true;
// Support ledge left around that window
smoke_window_ledge_width = 2.5;
// Window goes right through the floor
smoke_window_goes_through_floor = true;

/* [13. Air openings in the wall each sensor faces] */
// Opening in the wall in front of the BME680 sensor end
bme_air_opening_enable = true;
// Opening width
bme_air_opening_width = 10;
// Opening in the wall in front of the smoke sensor
smoke_air_opening_enable = true;
// Opening width
smoke_air_opening_width = 10;
// Opening in the wall in front of the CO sensor
co_air_opening_enable = true;
// Opening width
co_air_opening_width = 10;
// Opening height, measured up from the top of the sensor PCB
air_opening_height = 12;
// Corner radius of these openings
air_opening_corner_radius = 1.5;

/* [14. Wall vent slots] */
// Width of each vent slot
vent_slot_width = 1.5;
// Distance between slot centres
vent_slot_spacing = 3;
// Height of each slot
vent_slot_height = 13;
// Slot bottom edge, measured up from the floor top
vent_slot_bottom_above_floor = 4;
// Solid wall kept at each end of a vented wall region
vent_solid_margin_at_ends = 3;
// Vents in the +X end wall beside the sensors
vents_in_plus_x_wall = true;
// Vents in the -X end wall beside the sensors (usually off: this is the USB end)
vents_in_minus_x_wall = true;
// Vents in the +Y wall beside the sensors (skips the sensor air openings)
vents_in_plus_y_wall = true;
// Vents in the -Y wall along the whole row
vents_in_minus_y_wall = true;

/* [15. Lid openings] */
// Slotted grille over the sensors
lid_grille_over_sensors_enable = true;
// Grille slot width
lid_grille_slot_width = 1.8;
// Distance between grille slot centres
lid_grille_slot_spacing = 4;
// Solid margin between the grille and the sensor blocks' outline
lid_grille_margin = 2;
// Windows over the ESP header rows so connectors can pass through the lid
lid_windows_over_esp_headers = false;
// Window width
lid_header_window_width = 5;
// Window extends this far past each end of the header
lid_header_window_extra_length = 2;
// Windows over each sensor's pin header so connectors can pass through the lid (off = the lid grille is one uniform pattern; the cavity is then made tall enough for the connectors, see below)
lid_windows_over_sensor_pins = false;
// Sensor connector height above the PCB (header + plug). Used to size the cavity if the sensor windows are off
sensor_connector_height_above_pcb = 12;

/* [16. SDP810 differential pressure sensor (tube version, SDP81x)] */
// Fit an SDP810 / SDP811: body inside the case against a wall, both ports out through that wall
sdp_enable = true;
// Which wall the ports come out of
sdp_wall = "-Y"; // [-Y, +Y, -X, +X]
// Move the sensor along its wall from its automatic position (on -Y: + = toward +X). Automatic = just past the ESP block
sdp_offset_along_wall = 0;
// Ports sit near the top of the body (short wall slots, sensor drops in from above) or near the bottom
sdp_ports_near = "top"; // [top, bottom]
// Raise the sensor on a seat so the lid underside sits sdp_lid_gap above the body (holds it in place with no pad)
sdp_auto_lift_to_lid = true;
// Manual lift of the body off the floor (used only when the automatic lift is off)
sdp_lift_above_floor = 0;
// Body length (datasheet 29 +/-0.4)
sdp_body_length = 29.0;
// Body height when standing in the case (datasheet 18 +/-0.4)
sdp_body_height = 18.0;
// Body depth from the port face to the pin face (datasheet 10.25 +/-0.25)
sdp_body_depth = 10.25;
// Distance between the two ports (datasheet 12.6)
sdp_port_spacing = 12.6;
// Port centre distance from the nearer long edge of the body (datasheet 4.5)
sdp_port_from_edge = 4.5;
// Port neck diameter between body and flange (datasheet 4)
sdp_neck_diameter = 4.0;
// Free neck length between body face and flange: the wall sits in this gap (datasheet 2.6)
sdp_neck_length = 2.6;
// Flange diameter (datasheet 8)
sdp_flange_diameter = 8.0;
// Side clearance around the neck in the wall slot
sdp_slot_clearance = 0.4;
// Body height tolerance from the datasheet (18 +/-0.4): the seat is set for the tallest body
sdp_height_tolerance = 0.4;
// Gap between the tallest body's top and the lid underside (a nominal body gets this plus the tolerance)
sdp_lid_gap = 0.1;
// Cut the lid lip away above the sensor (the lip would otherwise hit the body and the port slots)
sdp_lid_lip_cutout = true;
// Extra length of that lip cutout beyond each end of the body
sdp_lid_lip_cutout_extra = 1.5;
// --- Floor pocket (lip around the body's base) ---
// Body size tolerance from the datasheet (+/-0.4 on 29 and 18, +/-0.25 on 10.25): the pocket fits the largest body
sdp_length_tolerance = 0.4;
sdp_depth_tolerance = 0.25;
// Fit clearance inside the pocket on each side
sdp_pocket_clearance = 0.2;
// Pocket lip wall thickness
sdp_lip_thickness = 1.6;
// End lip height (the two short ends; nothing protrudes there)
sdp_end_lip_height = 4;
// Back lip height (behind the pin face). Keep it under ~2.5 mm: the snap hooks reach down to about 1.4 mm above the floor near each end
sdp_back_lip_height = 2;
// The back lip stops this far from each end of the body, clear of the snap hooks and pegs (datasheet: hooks 1.8-3.6 mm from each end)
sdp_back_lip_end_gap = 5.5;
// Shallow reliefs in the floor under the two mounting-hole lugs, in case their rings stand proud of the face (0 = none)
sdp_lug_relief_depth = 0.6;
// Lug relief diameter
sdp_lug_relief_diameter = 6;
// Lug hole centre: distance in from each end of the body (datasheet 29 - 24 = 2.5 per end)
sdp_lug_from_end = 2.5;
// Lug hole centre: distance from the pin face (datasheet 6.3)
sdp_lug_from_pin_face = 6.3;
// Free space kept behind the pin face for the 2.0 mm pitch connector and wires
sdp_rear_clearance = 12;
// Gap between the sensor and the ESP block when placed automatically
sdp_gap_to_esp = 3;
// Engrave H (high, leave open to the enclosure) and L (low, tube to the garage) beside the ports
sdp_engrave_port_labels = true;
// Label text size
sdp_label_size = 3.5;
// Label engraving depth
sdp_label_depth = 0.5;

/* [17. OLED display on the lid (0.96 inch SSD1306, 4-pin I2C)] */
// Fit the display on top of the lid
oled_enable = true;
// Board width: the side with the pin header (measured 27)
oled_board_width = 27.0;
// Board height: the other side (measured 27.9)
oled_board_height = 27.9;
// PCB thickness [MEASURE]
oled_pcb_thickness = 1.6;
// Glass panel + tape above the PCB front [MEASURE]
oled_glass_thickness = 1.5;
// Mounting hole diameter (measured 2.1)
oled_hole_diameter = 2.1;
// Hole centre distance from both edges (measured 1.6)
oled_hole_inset = 1.6;
// Board centre on the lid, X (case frame, same origin as the cavity)
oled_centre_x = 41;
// Board centre on the lid, Y
oled_centre_y = 28;
// Which way the pin-header edge points. -Y = toward the top wall when the case hangs vertically (S-0018: yellow band at the top)
oled_header_edge = "-Y"; // [-Y, +Y, -X, +X]
// Number of header pins
oled_header_pins = 4;
// Header pin row distance from the header edge of the board [MEASURE]
oled_header_row_from_edge = 2.0;
// Header plastic height behind the board (= standoff height, the board rests on both) [MEASURE]
oled_header_plastic_height = 2.5;
// Slot in the lid the header pins pass through: width
oled_pin_slot_width = 2.2;
// Slot extra length past the outer pins at each end
oled_pin_slot_extra = 0.6;
// Standoff outside diameter
oled_standoff_diameter = 4.6;
// Pilot hole for M2 self-tapping screws (M2 x 5 reaches 5.6 mm: board + standoff + lid)
oled_screw_pilot_diameter = 1.7;
// Raised surround that protects the board edges (top sits level with the glass)
oled_surround_enable = true;
// Surround wall thickness
oled_surround_wall = 1.6;
// Gap between the board edge and the surround
oled_surround_clearance = 0.4;
// Lid grille slots stop this far from the surround and the LDR collar
oled_grille_keepout = 1.5;

/* [18. Light sensor (GL5528 LDR) under the lid] */
// Fit the LDR pocket and light hole
ldr_enable = true;
// LDR centre X (case frame)
ldr_x = 64;
// LDR centre Y
ldr_y = 18;
// Head size across its round sides (measured 5)
ldr_head_diameter = 5.0;
// Head size across its flats (measured 4)
ldr_head_flats = 4.0;
// Head thickness (measured 2)
ldr_head_thickness = 2.0;
// Fit clearance around the head
ldr_fit_clearance = 0.2;
// Flats run along X or along Y
ldr_flats_along = "Y"; // [X, Y]
// Light hole through the lid
ldr_light_hole_diameter = 3.5;
// Lid material left above the head around the light hole
ldr_skin_above_head = 0.8;
// Collar wall around the pocket (hangs under the lid)
ldr_collar_wall = 1.0;

/* [19. OLED bezel plate: printed cover that screws over the display] */
// Make the bezel plate (screws through the display's 4 corner holes into the lid standoffs)
oled_bezel_enable = true;
// Plate material left above the deepest recess (the top skin)
oled_bezel_face = 1.3;
// Gap between the plate and the inside wall of the surround (per side)
oled_bezel_side_gap = 0.1;
// Plate outer corner radius
oled_bezel_corner_radius = 0.5;
// Clearance added around every recess (glass, header pins, cable) and above them
oled_bezel_fit = 0.25;

// --- Window (the lit screen area; everything outside it is covered) ---
// Window top edge: distance from the board edge at the HEADER end (measured 4.1)
oled_window_top_from_header_edge = 4.1;
// Window bottom edge: distance from the board edge at the CABLE end (measured 8.5)
oled_window_bottom_from_far_edge = 8.5;
// Window width [MEASURE]
oled_window_width = 24;
// Move the window sideways (+ = right when the header is at the bottom)
oled_window_shift_x = 0;
// Window corner radius
oled_window_corner_radius = 1;

// --- Glass recess under the plate (also covers the slightly lower black bezel strip) ---
// Glass width [MEASURE]
oled_glass_width = 26.6;
// Glass top edge: distance from the board edge at the header end [MEASURE]
oled_glass_top_from_header_edge = 3.5;
// Glass bottom edge: distance from the board edge at the cable end [MEASURE]
oled_glass_bottom_from_far_edge = 5.4;
// Glass corner radius of the recess
oled_glass_recess_corner_radius = 0.6;

// --- Header pin recess (solder tips standing up on the screen side) ---
// Pin tip height above the PCB top (measured about 2.5)
oled_bezel_pin_height = 2.5;
// Recess starts this far from the board edge at the header end
oled_bezel_pin_recess_from_edge = 0.4;
// Recess length along the board (towards the screen)
oled_bezel_pin_recess_length = 3.0;
// Recess width = pins x 2.54 plus this extra
oled_bezel_pin_recess_extra_width = 1.0;
// Move the pin recess sideways
oled_bezel_pin_recess_shift_x = 0;

// --- Screen cable recess (flex cable standing proud at the far end) ---
// Cable width (measured about 11.5)
oled_bezel_cable_width = 11.5;
// Cable height above the PCB top [MEASURE]
oled_bezel_cable_height = 1.5;
// Move the cable recess sideways
oled_bezel_cable_shift_x = 0;
// Recess reaches this far in over the glass (so it joins the glass recess)
oled_bezel_cable_overlap_into_glass = 0.5;
// Run the recess out through the plate edge at the cable end
oled_bezel_cable_open_to_edge = true;

// --- Screws ---
// Clear hole for the screw (M2 = 2.4)
oled_bezel_screw_hole = 2.4;
// Counterbore diameter for the screw head
oled_bezel_head_dia = 4.2;
// Counterbore depth
oled_bezel_head_depth = 1.2;
// Move all four screw holes together on X / Y (display frame, +Y = towards the cable end)
oled_bezel_hole_shift_x = 0;
oled_bezel_hole_shift_y = 0;

// ---------------------------------------------------------------------
//  Nothing below this line is a setting.
// ---------------------------------------------------------------------

wall_t = wall_thickness; floor_t = floor_thickness;
is_row = (layout_style == "single_row");
boss_r = board_insert_boss_diameter / 2;
sensor_header_pitch = 2.54;

// ---- helper functions --------------------------------------------------
function pick(k, b, s) = k == "bme" ? b : s;           // BME680 value or smoke/CO value
// Insert-hole centres in board coordinates (origin = board's back/-Y corner of the BODY)
function hole_points(pattern, L, W, spacing, inset) =
    pattern == "two_on_back_edge"        ? [[inset, W/2 - spacing/2], [inset, W/2 + spacing/2]] :
    pattern == "two_on_sensor_end_edge"  ? [[L - inset, W/2 - spacing/2], [L - inset, W/2 + spacing/2]] :
    pattern == "one_on_each_side_edge"   ? [[L/2, inset], [L/2, W - inset]] :
    pattern == "one_on_back_and_sensor_end_edges" ? [[inset, W/2], [L - inset, W/2]] : [];
// Shift a pair of insert holes together by (dx, dy) and change the distance between them by dsp
function adjust_pair(p, dx, dy, dsp) =
    len(p) != 2 ? [for (q = p) [q[0] + dx, q[1] + dy]] :
    let (c = (p[0] + p[1]) / 2, d = p[1] - p[0], n = norm(d), u = n > 0 ? d / n : [0, 1],
         h = max(0.1, n + dsp) / 2)
    [[c[0] + dx - u[0]*h, c[1] + dy - u[1]*h], [c[0] + dx + u[0]*h, c[1] + dy + u[1]*h]];
function face_rot(f) = f == "+X" ? 0 : f == "+Y" ? 90 : f == "-X" ? 180 : 270;
// board outline with the narrower pin section (x = 0 is the pin edge)
function board_outline(L, W, recL, recD) = [[0, recD], [recL, recD], [recL, 0], [L, 0], [L, W], [recL, W], [recL, W - recD], [0, W - recD]];
// board-frame point -> case frame (block placed with its min corner at the origin)
function rotpt(rot, bx, by, p) = rot == 0 ? p : rot == 90 ? [by - p[1], p[0]] : rot == 180 ? [bx - p[0], by - p[1]] : [p[1], bx - p[0]];
// how far bosses poke out past the rim on each side: [back, front, -Y, +Y]
function boss_extras(pts, tol, rim, br, L, W) =
    len(pts) == 0 ? [0,0,0,0] : [
        max(0, max([for (q = pts) br - (tol + q[0]) - rim])),
        max(0, max([for (q = pts) (tol + q[0]) + br - (L + 2*tol) - rim])),
        max(0, max([for (q = pts) br - (tol + q[1]) - rim])),
        max(0, max([for (q = pts) (tol + q[1]) + br - (W + 2*tol) - rim]))];
// grow the extras for a lip at the front and a pin channel reaching out of the back
function grow_extras(e, lip, tol, rim, ch_out) =
    [max(e[0], ch_out > 0 ? ch_out + 1.2 - rim : 0), max(e[1], lip > 0 ? lip + tol - rim : 0), e[2], e[3]];

// ---- ESP derived -------------------------------------------------------
esp_px = esp_board_length_x + 2*esp_fit_clearance;
esp_py = esp_board_width_y  + 2*esp_fit_clearance;
esp_rim = esp_rim_wall_thickness;
esp_tol = esp_fit_clearance;
esp_pcb_top_z = floor_t + esp_platform_height + esp_pcb_thickness;
esp_ret_cx = esp_tol + esp_board_length_x + esp_retainer_hole_distance_from_board_end;
esp_ret_cy = esp_py / 2;
esp_extra_plus_x = esp_retainer_enable ? max(0, esp_ret_cx + boss_r - esp_px - esp_rim) : 0;
esp_blk_x = esp_px + 2*esp_rim + esp_extra_plus_x;
esp_blk_y = esp_py + 2*esp_rim;
esp_boss_top_z = esp_pcb_top_z + esp_rim_height_above_pcb + esp_retainer_boss_top_relative_to_pcb_top;

// ---- BME680 derived (board frame) --------------------------------------
bme_tol = bme_fit_clearance; bme_rim = bme_rim_wall_thickness;
bme_px = bme_board_length + 2*bme_tol; bme_py = bme_board_width + 2*bme_tol;
bme_pts = [];       // no edge notches on this board: it uses screw holes inside the board instead
bme_hr = bme_screw_hole_edge_to_board_edge + bme_screw_hole_diameter/2;     // hole centre distance from the edges
bme_thru_pts = adjust_pair([[bme_board_length - bme_hr, bme_hr], [bme_board_length - bme_hr, bme_board_width - bme_hr]],
                           bme_insert_offset_x, bme_insert_offset_y, bme_insert_spacing_adjust);
bme_e = grow_extras(boss_extras(bme_thru_pts, bme_tol, bme_rim, boss_r, bme_board_length, bme_board_width), 0, bme_tol, bme_rim, bme_pin_channel_outward_length);
bme_blk_x = bme_px + 2*bme_rim + bme_e[0] + bme_e[1];
bme_blk_y = bme_py + 2*bme_rim + bme_e[2] + bme_e[3];
bme_ox = bme_e[0] + bme_rim;  bme_oy = bme_e[2] + bme_rim;
bme_top_z = floor_t + bme_platform_height + bme_pcb_thickness;
bme_rot = face_rot(bme_sensor_end_faces);
bme_gx = (bme_rot % 180 == 0) ? bme_blk_x : bme_blk_y;
bme_gy = (bme_rot % 180 == 0) ? bme_blk_y : bme_blk_x;

// ---- smoke / CO derived (board frame) ----------------------------------
sm_tol = smoke_fit_clearance; sm_rim = smoke_rim_wall_thickness;
sm_px = smoke_board_length + 2*sm_tol; sm_py = smoke_board_width + 2*sm_tol;
sm_pts = adjust_pair(hole_points(smoke_notch_positions, smoke_board_length, smoke_board_width, smoke_notch_spacing, smoke_notch_hole_distance_in_from_edge),
                     smoke_insert_offset_x, smoke_insert_offset_y, smoke_insert_spacing_adjust);
sm_e = grow_extras(boss_extras(sm_pts, sm_tol, sm_rim, boss_r, smoke_board_length, smoke_board_width),
                   0, sm_tol, sm_rim, smoke_pin_channel_outward_length);
sm_blk_x = sm_px + 2*sm_rim + sm_e[0] + sm_e[1];
sm_blk_y = sm_py + 2*sm_rim + sm_e[2] + sm_e[3];
sm_ox = sm_e[0] + sm_rim;  sm_oy = sm_e[2] + sm_rim;
sm_top_z = floor_t + smoke_platform_height + smoke_pcb_thickness;
sm_rot = face_rot(smoke_sensor_end_faces);
sm_gx = (sm_rot % 180 == 0) ? sm_blk_x : sm_blk_y;
sm_gy = (sm_rot % 180 == 0) ? sm_blk_y : sm_blk_x;

// ---- per-kind accessors ("bme", "smoke", "co") -------------------------
function k_gx(k)  = pick(k, bme_gx, sm_gx);
function k_gy(k)  = pick(k, bme_gy, sm_gy);
function k_bx(k)  = pick(k, bme_blk_x, sm_blk_x);
function k_by(k)  = pick(k, bme_blk_y, sm_blk_y);
function k_rot(k) = pick(k, bme_rot, sm_rot);
function k_ox(k)  = pick(k, bme_ox, sm_ox);
function k_oy(k)  = pick(k, bme_oy, sm_oy);
function k_px(k)  = pick(k, bme_px, sm_px);
function k_py(k)  = pick(k, bme_py, sm_py);
function k_tol(k) = pick(k, bme_tol, sm_tol);
function k_L(k)   = pick(k, bme_board_length, smoke_board_length);
function k_W(k)   = pick(k, bme_board_width, smoke_board_width);
function k_recL(k) = pick(k, bme_pin_section_length, 0);
function k_recD(k) = pick(k, bme_pin_section_inset_each_side, 0);
function k_t(k)   = pick(k, bme_pcb_thickness, smoke_pcb_thickness);
function k_plat(k)= pick(k, bme_platform_height, smoke_platform_height);
function k_top(k) = pick(k, bme_top_z, sm_top_z);
function k_face(k)= pick(k, bme_sensor_end_faces, smoke_sensor_end_faces);
function k_open_on(k) = k == "bme" ? bme_air_opening_enable : k == "smoke" ? smoke_air_opening_enable : co_air_opening_enable;
function k_open_w(k)  = k == "bme" ? bme_air_opening_width  : k == "smoke" ? smoke_air_opening_width  : co_air_opening_width;

// ---- layout ------------------------------------------------------------
kinds = [for (k = [sensor_position_1, sensor_position_2, sensor_position_3]) if (k != "none") k];
nk = len(kinds);
maxsens_y = max([for (k = kinds) k_gy(k)]);
esp_x0_base = spare_space_each_x_end;
esp_x0 = esp_x0_base + esp_offset_x;
rowB_y0 = esp_blk_y + gap_between_esp_and_sensors;               // two_rows only
first_x0 = is_row ? esp_x0 + esp_blk_x + gap_between_esp_and_sensors : two_rows_sensor_row_start_x;
function sx(i) = i == 0 ? first_x0 : sx(i-1) + k_gx(kinds[i-1]) + gap_between_sensor_blocks;
sensors_end_x = nk > 0 ? sx(nk-1) + k_gx(kinds[nk-1]) : first_x0;
function k_align(k) = sensor_row_alignment == "toward_plus_y" ? maxsens_y - k_gy(k)
                    : sensor_row_alignment == "toward_minus_y" ? 0 : (maxsens_y - k_gy(k))/2;
function k_off(k) = k == "bme" ? [bme_offset_x, bme_offset_y] : k == "smoke" ? [smoke_offset_x, smoke_offset_y] : [co_offset_x, co_offset_y];
function ky0(k) = sens_y_base + k_align(k) + k_off(k)[1];
function kx0(i) = sx(i) + k_off(kinds[i])[0];
function kpocket_c(i) = [kx0(i), ky0(kinds[i])] + rotpt(k_rot(kinds[i]), k_bx(kinds[i]), k_by(kinds[i]),
                         [k_ox(kinds[i]) + k_px(kinds[i])/2, k_oy(kinds[i]) + k_py(kinds[i])/2]);

function sdp_need_along_early() = (sdp_wall == "-Y" ? esp_x0 + esp_blk_x + sdp_gap_to_esp + sdp_body_length/2 + sdp_length_tolerance + sdp_pocket_clearance + sdp_lip_thickness
                                  : sdp_body_length/2 + 2) + sdp_offset_along_wall
                                  + sdp_body_length/2 + sdp_length_tolerance + sdp_pocket_clearance + sdp_lip_thickness + 0.5;
sens_max_x = nk > 0 ? max([for (i = [0:nk-1]) kx0(i) + k_gx(kinds[i])]) : 0;
sdp_x_need = (sdp_enable && (sdp_wall == "-Y" || sdp_wall == "+Y")) ? sdp_need_along_early() : 0;
auto_inner_x = cavity_grows_to_fit_moved_blocks
             ? max(esp_x0 + esp_blk_x, sensors_end_x, sens_max_x, sdp_x_need) + spare_space_each_x_end
             : max(esp_x0_base + esp_blk_x, sensors_end_x, sdp_x_need) + spare_space_each_x_end;
inner_x = cavity_length_override > 0 ? cavity_length_override : auto_inner_x;
auto_inner_y = is_row ? max(esp_blk_y, maxsens_y) + 2*spare_space_each_y_side
                      : rowB_y0 + maxsens_y + spare_space_each_y_side;
inner_y_base = cavity_width_override > 0 ? cavity_width_override : auto_inner_y;
esp_y0 = (is_row ? (inner_y_base - esp_blk_y)/2 : 0) + esp_offset_y;
sens_y_base = is_row ? (inner_y_base - maxsens_y)/2 : rowB_y0;
// extra width only when a moved block would poke past the +Y side
sens_max_y = nk > 0 ? max([for (k = kinds) ky0(k) + k_gy(k)]) : 0;
esp_max_y  = esp_y0 + esp_blk_y;
inner_y = (cavity_width_override > 0 || !cavity_grows_to_fit_moved_blocks) ? inner_y_base
        : max(inner_y_base, sens_max_y + spare_space_each_y_side, esp_max_y + spare_space_each_y_side);

// ---- SDP810 placement (local frame: u along the wall, v into the cavity from the inner wall face) ----
sdp_on = sdp_enable;
sdp_ywall = (sdp_wall == "-Y" || sdp_wall == "+Y");
// automatic centre along the wall: just past the ESP block (-Y) or centred on the wall otherwise
sdp_auto_pos = sdp_wall == "-Y" ? esp_x0 + esp_blk_x + sdp_gap_to_esp + sdp_body_length/2 + sdp_length_tolerance + sdp_pocket_clearance + sdp_lip_thickness
             : sdp_ywall ? sdp_body_length/2 + 2 : sdp_body_length/2 + 2;
sdp_pos = sdp_auto_pos + sdp_offset_along_wall;

sdp_need_along = sdp_on ? sdp_pos + sdp_body_length/2 + 1 : 0;    // how far along the wall it reaches
sdp_need_h = sdp_on ? (sdp_auto_lift_to_lid ? 0 : sdp_lift_above_floor) + sdp_body_height + sdp_height_tolerance + sdp_lid_gap
                      + ((lid_lip_enable && !sdp_lid_lip_cutout) ? lid_lip_height : 0) : 0;
// pocket inner size (largest body + clearance)
sdp_pk_len = sdp_body_length + 2*sdp_length_tolerance + 2*sdp_pocket_clearance;
sdp_pk_dep = sdp_body_depth + sdp_depth_tolerance + sdp_pocket_clearance;

// cavity height
tall_esp = esp_platform_height + max(esp_total_height,
           esp_pcb_thickness + (esp_has_pin_headers ? esp_header_plastic_height + esp_header_pin_height_above_plastic : 0));
tall_ret = esp_retainer_enable ? esp_boss_top_z - floor_t + esp_retainer_clip_thickness + 2.5 : 0;
sens_conn = lid_windows_over_sensor_pins ? 6 : sensor_connector_height_above_pcb;
tall_bme = bme_platform_height + bme_pcb_thickness + sens_conn;
tall_sm  = smoke_platform_height + smoke_pcb_thickness + sens_conn;
auto_inner_h = max(tall_esp, tall_ret, tall_bme, tall_sm) + headroom_above_tallest_part;
inner_h = cavity_height_override > 0 ? cavity_height_override : max(auto_inner_h, sdp_need_h);
wall_h = floor_t + inner_h;
// SDP810 seat height: automatic = whatever puts the body top sdp_lid_gap under the lid
sdp_lift = !sdp_on ? 0 : sdp_auto_lift_to_lid
         ? max(0, inner_h - sdp_body_height - sdp_height_tolerance - sdp_lid_gap - ((lid_lip_enable && !sdp_lid_lip_cutout) ? lid_lip_height : 0))
         : sdp_lift_above_floor;
sdp_seat_z = floor_t + sdp_lift;
sdp_port_z = sdp_seat_z + (sdp_ports_near == "top" ? sdp_body_height - sdp_port_from_edge : sdp_port_from_edge);
total_x = inner_x + 2*wall_t;
total_y = inner_y + 2*wall_t;

// ---------------------------------------------------------------------
//  HELPER MODULES
// ---------------------------------------------------------------------
module rrect(x, y, h, r) {
    if (r <= 0) cube([x, y, h]);
    else hull() for (i=[r, x-r], j=[r, y-r]) translate([i,j,0]) cylinder(r=r, h=h);
}
module rslot(w, h, d, r) {   // rounded opening, w across, h up, d deep (centred on its mid-plane)
    rr = min(r, min(w,h)/2 - 0.01);
    hull() for (i=[-w/2+rr, w/2-rr], j=[rr, h-rr])
        translate([i, 0, j]) rotate([90,0,0]) cylinder(r=rr, h=d, center=true);
}
module on_wall(side, pos, zb) {
    if (side == "+Y") translate([pos, inner_y + wall_t/2, zb]) children();
    if (side == "-Y") translate([pos, -wall_t/2, zb]) children();
    if (side == "+X") translate([inner_x + wall_t/2, pos, zb]) rotate([0,0,90]) children();
    if (side == "-X") translate([-wall_t/2, pos, zb]) rotate([0,0,90]) children();
}
// put children in a sensor block's own (board) frame, block min corner at origin
module in_frame(rot, bx, by) {
    if (rot == 0) children();
    if (rot == 90)  translate([by, 0, 0]) rotate([0,0,90]) children();
    if (rot == 180) translate([bx, by, 0]) rotate([0,0,180]) children();
    if (rot == 270) translate([0, bx, 0]) rotate([0,0,270]) children();
}
// 2D board-slot outline: square corners by default, optionally rounded
module pocket_2d(L, W, recL, recD, tol) {
    if (slot_corner_radius > 0)
        offset(r = slot_corner_radius) offset(delta = -slot_corner_radius) offset(delta = tol) polygon(board_outline(L, W, recL, recD));
    else offset(delta = tol) polygon(board_outline(L, W, recL, recD));
}
module insert_hole(d, mouth, depth) {   // top face at local z=0, drilled downward
    translate([0,0,-depth]) cylinder(d=d, h=depth + 0.01);
    translate([0,0,-(mouth-d)/2]) cylinder(d1=d, d2=mouth, h=(mouth-d)/2 + 0.01);
    cylinder(d=mouth, h=1);
}
// place one sensor's frame in the case: i = position index
module at_sensor(i) {
    k = kinds[i];
    translate([kx0(i), ky0(k), 0]) in_frame(k_rot(k), k_bx(k), k_by(k)) children();
}

// ---------------------------------------------------------------------
//  SENSOR BLOCK (solid part) and its CUTS
// ---------------------------------------------------------------------
module sensor_solid(k) {
    L = k_L(k); W = k_W(k); t = k_t(k); tol = k_tol(k);
    rim = pick(k, bme_rim, sm_rim); plat = k_plat(k);
    hold = pick(k, bme_rim_height_above_pcb, smoke_rim_height_above_pcb);
    pts = pick(k, bme_pts, sm_pts);
    notch_d = smoke_notch_clearance_diameter;   // only used for edge-notch boards (smoke, CO)
    ox = k_ox(k); oy = k_oy(k); top = floor_t + plat + t;
    union() {
        difference() {
            cube([k_bx(k), k_by(k), top + hold]);
            translate([ox + tol, oy + tol, floor_t + plat])
                linear_extrude(t + hold + 1) pocket_2d(L, W, k_recL(k), k_recD(k), tol);
        }
        for (q = pts)
            translate([ox + tol + q[0], oy + tol + q[1], 0])
                difference() {
                    cylinder(d=board_insert_boss_diameter, h=top);
                    translate([-q[0], -q[1], -1])
                        linear_extrude(top + 2) pocket_2d(L, W, k_recL(k), k_recD(k), tol);
                }
    }
}

// cuts for one sensor, in its board frame
module sensor_cuts(k) {
    L = k_L(k); W = k_W(k); t = k_t(k); tol = k_tol(k); plat = k_plat(k);
    ox = k_ox(k); oy = k_oy(k); top = floor_t + plat + t;
    pts = pick(k, bme_pts, sm_pts);
    seat = floor_t + plat;                       // underside of the PCB
    // heat-set insert holes beneath screw holes that go THROUGH the board (insert top = underside of PCB)
    if (k == "bme")
        for (q = bme_thru_pts)
            translate([ox + tol + q[0], oy + tol + q[1], floor_t + plat - board_insert_top_below_pcb_underside])
                insert_hole(board_insert_hole_diameter, board_insert_mouth_diameter, min(board_insert_hole_depth, floor_t + plat - board_insert_top_below_pcb_underside - 0.8));
    // heat-set insert holes at edge notches (bolt head overlaps the board edge)
    // (insert top sits at the PCB underside minus the recess setting; the recess above it clears the bolt)
    for (q = pts)
        translate([ox + tol + q[0], oy + tol + q[1], seat - board_insert_top_below_pcb_underside]) {
            insert_hole(board_insert_hole_diameter, board_insert_mouth_diameter, min(board_insert_hole_depth, seat - board_insert_top_below_pcb_underside - 0.8));
            cylinder(d = smoke_notch_clearance_diameter, h = t + board_insert_top_below_pcb_underside + 6);
        }
    // window under the middle of the board
    win_on = pick(k, bme_cut_window_under_board, smoke_cut_window_under_board);
    ledge  = pick(k, bme_window_ledge_width, smoke_window_ledge_width);
    thru   = pick(k, bme_window_goes_through_floor, smoke_window_goes_through_floor);
    // keep the window clear of the pin channel: start it after the channel
    ch_in  = pick(k, bme_pin_channel_inboard_length, smoke_pin_channel_inboard_length);
    if (win_on)
        translate([ox + tol + max(ledge, ch_in + 1), oy + tol + ledge, thru ? -1 : floor_t + 0.6])
            cube([L - max(ledge, ch_in + 1) - ledge, W - 2*ledge, seat + 2 - (thru ? -1 : floor_t + 0.6) + 0.01]);
    // pin channel: under the board at the pin edge, extending out past it
    ch_out = pick(k, bme_pin_channel_outward_length, smoke_pin_channel_outward_length);
    ch_dep = pick(k, bme_pin_channel_depth, smoke_pin_channel_depth);
    ch_w   = k == "bme" ? bme_pin_count*sensor_header_pitch + bme_pin_channel_extra_width : smoke_pin_channel_width;
    ch_z0  = max(0.8, seat - ch_dep);
    translate([ox + tol - ch_out, oy + tol + W/2 - ch_w/2, ch_z0])
        cube([ch_out + ch_in, ch_w, seat - ch_z0 + 0.01]);
    if (ch_out > 0)    // outward part is open to the top so a plug/wires can leave the edge
        translate([ox + tol - ch_out, oy + tol + W/2 - ch_w/2, seat - 0.01])
            cube([ch_out, ch_w, t + 6]);
}

// ---------------------------------------------------------------------
//  ESP BLOCK
// ---------------------------------------------------------------------
module esp_block() {
    px = esp_px; py = esp_py; rim = esp_rim; tol = esp_tol;
    top = esp_pcb_top_z;
    h = esp_platform_height + esp_pcb_thickness + esp_rim_height_above_pcb;
    cy = esp_blk_y / 2;
    hx0 = rim + tol + esp_header_start_from_usb_end;
    hlen = esp_header_pins_per_row * esp_header_pin_pitch;
    difference() {
        union() {
            difference() {
                cube([esp_blk_x, esp_blk_y, floor_t + h]);
                translate([rim, rim, floor_t + esp_platform_height]) cube([px, py, h + 1]);
            }
            if (esp_retainer_enable)
                translate([rim + esp_ret_cx, rim + esp_ret_cy, 0])
                    difference() {
                        cylinder(d=board_insert_boss_diameter, h=esp_boss_top_z);
                        translate([-esp_ret_cx + tol, -esp_ret_cy + tol, -1])
                            cube([esp_board_length_x, esp_board_width_y, esp_boss_top_z + 2]);
                    }
        }
        if (esp_retainer_enable)
            translate([rim + esp_ret_cx, rim + esp_ret_cy, esp_boss_top_z])
                insert_hole(board_insert_hole_diameter, board_insert_mouth_diameter,
                            min(board_insert_hole_depth, esp_boss_top_z - 0.8));
        if (esp_clear_window_under_board)
            translate([rim + 2, cy - esp_header_row_spacing/2 + esp_solder_tail_groove_width/2, floor_t + 0.6])
                cube([px - 4, esp_header_row_spacing - esp_solder_tail_groove_width, esp_platform_height + 0.5]);
        if (esp_cut_grooves_for_solder_tails && esp_has_pin_headers)
            for (s = [-1, 1])
                translate([hx0 - 1, cy + s*esp_header_row_spacing/2 - esp_solder_tail_groove_width/2,
                           floor_t - esp_solder_tail_groove_extra_depth])
                    cube([hlen + 2, esp_solder_tail_groove_width,
                          esp_platform_height + esp_solder_tail_groove_extra_depth + 0.01]);
        if (esp_open_rim_at_antenna_end)
            translate([rim + px - esp_open_rim_length, rim, top])
                cube([esp_open_rim_length + rim + 1, py, h + 1]);
    }
}

// ---------------------------------------------------------------------
//  RETAINER CLIP  (origin = bolt-hole centre; reaches toward -X over the board end)
// ---------------------------------------------------------------------
module retainer_clip() {
    reach = esp_retainer_hole_distance_from_board_end + esp_retainer_clip_overlap_on_board;
    w = esp_retainer_clip_width;
    difference() {
        hull() {
            cylinder(d=w, h=esp_retainer_clip_thickness);
            translate([-reach, -w/2, 0]) cube([0.01, w, esp_retainer_clip_thickness]);
        }
        translate([0, 0, -1]) cylinder(d=esp_retainer_clip_bolt_hole_diameter, h=esp_retainer_clip_thickness + 2);
    }
}

// ---------------------------------------------------------------------
//  BASE
// ---------------------------------------------------------------------
function ear_centers() = [
    [-wall_t - corner_ear_offset_outward, -wall_t - corner_ear_offset_outward, -wall_t + outer_corner_radius, -wall_t + outer_corner_radius],
    [inner_x + wall_t + corner_ear_offset_outward, -wall_t - corner_ear_offset_outward, inner_x + wall_t - outer_corner_radius, -wall_t + outer_corner_radius],
    [-wall_t - corner_ear_offset_outward, inner_y + wall_t + corner_ear_offset_outward, -wall_t + outer_corner_radius, inner_y + wall_t - outer_corner_radius],
    [inner_x + wall_t + corner_ear_offset_outward, inner_y + wall_t + corner_ear_offset_outward, inner_x + wall_t - outer_corner_radius, inner_y + wall_t - outer_corner_radius]
];

// mounting tabs: [hole x, hole y, direction the tab points]
function mount_tabs() = [
    if (mounting_tab_minus_x) [-wall_t - mounting_hole_distance_from_wall, inner_y/2 + mounting_tab_shift_along_x_walls, 180],
    if (mounting_tab_plus_x)  [inner_x + wall_t + mounting_hole_distance_from_wall, inner_y/2 + mounting_tab_shift_along_x_walls, 0],
    if (mounting_tab_minus_y) [inner_x/2 + mounting_tab_shift_along_y_walls, -wall_t - mounting_hole_distance_from_wall, 270],
    if (mounting_tab_plus_y)  [inner_x/2 + mounting_tab_shift_along_y_walls, inner_y + wall_t + mounting_hole_distance_from_wall, 90]
];
mount_reach = mounting_tabs_enable ? mounting_hole_distance_from_wall + mounting_tab_width/2 : 0;
module mounting_tab_solid(t) {
    // rounded tab from the wall face out past the hole
    translate([t[0], t[1], 0]) rotate([0, 0, t[2]])
        hull() {
            cylinder(d = mounting_tab_width, h = mounting_tab_thickness);
            translate([-mounting_hole_distance_from_wall - 1, -mounting_tab_width/2, 0])
                cube([0.01, mounting_tab_width, mounting_tab_thickness]);
        }
}
module mounting_tab_hole(t) {
    translate([t[0], t[1], -1]) cylinder(d = mounting_hole_diameter, h = mounting_tab_thickness + 2);
    if (mounting_countersink_diameter > mounting_hole_diameter)
        translate([t[0], t[1], mounting_tab_thickness - (mounting_countersink_diameter - mounting_hole_diameter)/2])
            cylinder(d1 = mounting_hole_diameter, d2 = mounting_countersink_diameter,
                     h = (mounting_countersink_diameter - mounting_hole_diameter)/2 + 0.01);
}

// SDP810 local frame -> case frame. Local x = along the wall, local y = into the cavity
// (y = 0 at the inner wall face, y = -wall_t at the outer face), local z = up.
module sdp_frame() {
    if (sdp_wall == "-Y") translate([sdp_pos, 0, 0]) children();
    if (sdp_wall == "+Y") translate([inner_x - sdp_pos, inner_y, 0]) rotate([0, 0, 180]) children();
    if (sdp_wall == "-X") translate([0, inner_y - sdp_pos, 0]) rotate([0, 0, -90]) children();
    if (sdp_wall == "+X") translate([inner_x, sdp_pos, 0]) rotate([0, 0, 90]) children();
}
// is a vent slot at position `pos` along wall `side` inside the SDP span?
function sdp_blocks_vent(side, pos) = sdp_on && side == sdp_wall &&
    abs((side == "-Y" ? pos : side == "+Y" ? inner_x - pos : side == "-X" ? inner_y - pos : pos) - sdp_pos)
        < sdp_body_length/2 + 2;
// wall cuts: a U-slot from each port up through the top of the wall, plus an outer pocket
// when the wall is thicker than the neck gap, and optional H / L labels
module sdp_wall_cuts() {
    w = sdp_neck_diameter + sdp_slot_clearance;
    thin_to = sdp_neck_length - 0.3;                     // wall thickness the neck gap can take
    for (s = [-1, 1]) {
        translate([s*sdp_port_spacing/2, 0, 0]) {
            // slot (round bottom at the port axis, open to the top of the wall)
            translate([0, -wall_t/2, sdp_port_z]) rotate([90, 0, 0]) cylinder(d = w, h = wall_t + 2, center = true);
            translate([-w/2, -wall_t - 1, sdp_port_z]) cube([w, wall_t + 2, wall_h - sdp_port_z + 1]);
            if (wall_t > thin_to)
                hull() for (z = [sdp_port_z, wall_h + sdp_flange_diameter])
                    translate([0, -wall_t - 1, z]) rotate([-90, 0, 0]) cylinder(d = sdp_flange_diameter + 1, h = wall_t - thin_to + 1);
        }
    }
    if (sdp_engrave_port_labels)
        for (lab = [[-1, "H"], [1, "L"]])
            translate([lab[0]*sdp_port_spacing/2, -wall_t + sdp_label_depth - 0.01,
                       sdp_port_z + (sdp_ports_near == "top" ? -1 : 1) * (sdp_flange_diameter/2 + 1.5 + sdp_label_size/2)])
                rotate([90, 0, 0]) linear_extrude(sdp_label_depth + 1)
                    text(lab[1], size = sdp_label_size, halign = "center", valign = "center");
}
// floor pocket: end lips + a short low back lip (in the SDP local frame)
module sdp_pocket_solid() {
    z0 = floor_t - 0.01;
    rise = sdp_seat_z - z0;                       // seat height above the floor
    // seat the body stands on
    if (sdp_lift > 0.01) translate([-sdp_pk_len/2, 0, z0]) cube([sdp_pk_len, sdp_pk_dep, rise]);
    for (s = [-1, 1])
        translate([s > 0 ? sdp_pk_len/2 : -sdp_pk_len/2 - sdp_lip_thickness, 0, z0])
            cube([sdp_lip_thickness, sdp_pk_dep + sdp_lip_thickness, rise + sdp_end_lip_height]);
    back_len = sdp_body_length - 2*sdp_back_lip_end_gap;
    if (back_len > 2 && sdp_back_lip_height > 0)
        translate([-back_len/2, sdp_pk_dep, z0]) cube([back_len, sdp_lip_thickness, rise + sdp_back_lip_height]);
}
module sdp_floor_reliefs() {
    if (sdp_lug_relief_depth > 0)
        for (s = [-1, 1])
            translate([s*(sdp_body_length/2 - sdp_lug_from_end), sdp_body_depth - sdp_lug_from_pin_face, sdp_seat_z - sdp_lug_relief_depth])
                cylinder(d = sdp_lug_relief_diameter, h = sdp_lug_relief_depth + 0.5);
}
module sdp_ghost() {
    z0 = sdp_seat_z;
    color("dimgray", 0.8) translate([-sdp_body_length/2, 0, z0]) cube([sdp_body_length, sdp_body_depth, sdp_body_height]);
    color("dimgray", 0.8) for (s = [-1, 1]) translate([s*sdp_port_spacing/2, 0, sdp_port_z]) rotate([90, 0, 0]) {
        cylinder(d = sdp_neck_diameter, h = sdp_neck_length);
        translate([0, 0, sdp_neck_length]) cylinder(d = sdp_flange_diameter, h = 1.25);
        translate([0, 0, sdp_neck_length + 1.25]) cylinder(d1 = 5.2, d2 = 3.5, h = 13.5 - sdp_neck_length - 1.25);
    }
    color("gold", 0.8) for (i = [0:3]) translate([-3 + 2*i - 0.25, sdp_body_depth, z0 + sdp_body_height/2 - 0.25]) cube([0.5, 3.3, 0.5]);
}

module vent_slots_wall(side, from_v, to_v) {
    span = to_v - from_v - 2*vent_solid_margin_at_ends;
    if (span > vent_slot_width) {
        n = floor((span - vent_slot_width) / vent_slot_spacing) + 1;
        used = (n-1)*vent_slot_spacing + vent_slot_width;
        start = from_v + vent_solid_margin_at_ends + (span - used)/2 + vent_slot_width/2;
        for (i=[0:n-1]) if (!sdp_blocks_vent(side, start + i*vent_slot_spacing))
            on_wall(side, start + i*vent_slot_spacing, floor_t + vent_slot_bottom_above_floor)
                rslot(vent_slot_width, vent_slot_height, wall_t + 2, 0.5);
    }
}
// is global x inside the air opening of some sensor facing +Y?
function x_in_plus_y_opening(x) = len([for (i = [0:nk-1])
    if (k_open_on(kinds[i]) && k_face(kinds[i]) == "+Y" && abs(x - kpocket_c(i)[0]) < k_open_w(kinds[i])/2 + 1.5) 1]) > 0;
module vent_slots_plus_y() {
    span = inner_x - 2*vent_solid_margin_at_ends;
    n = floor((span - vent_slot_width) / vent_slot_spacing) + 1;
    used = (n-1)*vent_slot_spacing + vent_slot_width;
    start = vent_solid_margin_at_ends + (span - used)/2 + vent_slot_width/2;
    for (i=[0:n-1]) {
        x = start + i*vent_slot_spacing;
        if (x > first_x0 - 1 && x < sensors_end_x + 1 && !x_in_plus_y_opening(x) && !sdp_blocks_vent("+Y", x))
            on_wall("+Y", x, floor_t + vent_slot_bottom_above_floor)
                rslot(vent_slot_width, vent_slot_height, wall_t + 2, 0.5);
    }
}
module sensor_air_opening(face, gc, w, zb) {
    if (face == "+Y") on_wall("+Y", gc[0], zb) rslot(w, air_opening_height, wall_t + 2, air_opening_corner_radius);
    if (face == "-Y") on_wall("-Y", gc[0], zb) rslot(w, air_opening_height, wall_t + 2, air_opening_corner_radius);
    if (face == "+X") on_wall("+X", gc[1], zb) rslot(w, air_opening_height, wall_t + 2, air_opening_corner_radius);
    if (face == "-X") on_wall("-X", gc[1], zb) rslot(w, air_opening_height, wall_t + 2, air_opening_corner_radius);
}

module base() {
    difference() {
        union() {
            difference() {
                translate([-wall_t, -wall_t, 0]) rrect(total_x, total_y, wall_h, outer_corner_radius);
                translate([0, 0, floor_t]) cube([inner_x, inner_y, wall_h]);
            }
            if (corner_ears_enable) for (c = ear_centers())
                hull() {
                    translate([c[0], c[1], 0]) cylinder(d=corner_ear_diameter, h=wall_h);
                    translate([c[2], c[3], 0]) cylinder(d=corner_ear_diameter*0.4, h=wall_h);
                }
            translate([esp_x0, esp_y0, 0]) esp_block();
            for (i = [0:nk-1]) at_sensor(i) sensor_solid(kinds[i]);
            if (mounting_tabs_enable) for (t = mount_tabs()) mounting_tab_solid(t);
            if (sdp_on) sdp_frame() sdp_pocket_solid();
        }

        // ---- cuts ----
        // USB opening in the -X wall (also through the ESP rim)
        // (runs from outside the wall to the same point near the ESP rim as before, and follows the ESP when it moves)
        usb_x_end   = -wall_t - 1 + (wall_t + esp_rim + esp_x0_base + 6)/2 + esp_offset_x;
        usb_x_start = -wall_t - 2 - (wall_t + esp_rim + esp_x0_base + 6)/2;
        translate([(usb_x_start + usb_x_end)/2, esp_y0 + esp_blk_y/2 + usb_opening_shift_sideways,
                   esp_pcb_top_z + usb_opening_centre_above_pcb - usb_opening_height/2])
            rotate([0,0,90]) rslot(usb_opening_width, usb_opening_height, usb_x_end - usb_x_start, usb_opening_corner_radius);

        // sensor holes, windows, pin channels, lip slot
        for (i = [0:nk-1]) at_sensor(i) sensor_cuts(kinds[i]);

        // air openings in the wall each sensor faces
        for (i = [0:nk-1]) if (k_open_on(kinds[i]))
            sensor_air_opening(k_face(kinds[i]), kpocket_c(i), k_open_w(kinds[i]), k_top(kinds[i]));

        // wall vents
        if (vents_in_plus_y_wall)  vent_slots_plus_y();
        if (vents_in_plus_x_wall)  vent_slots_wall("+X", sens_y_base, sens_y_base + maxsens_y);
        if (vents_in_minus_x_wall) vent_slots_wall("-X", sens_y_base, sens_y_base + maxsens_y);
        if (vents_in_minus_y_wall) vent_slots_wall("-Y", esp_x0, sensors_end_x);

        // SDP810 port slots and labels
        if (sdp_on) sdp_frame() { sdp_wall_cuts(); sdp_floor_reliefs(); }

        // mounting tab screw holes
        if (mounting_tabs_enable) for (t = mount_tabs()) mounting_tab_hole(t);

        // corner insert holes (lid bolts)
        if (corner_ears_enable) for (c = ear_centers())
            translate([c[0], c[1], wall_h])
                insert_hole(corner_insert_hole_diameter, corner_insert_mouth_diameter, corner_insert_hole_depth);
    }
}

// ---------------------------------------------------------------------
//  OLED + LDR (lid frame: z = 0 is the lid underside, lid top at lid_thickness)
// ---------------------------------------------------------------------
oled_on = oled_enable;
ldr_on  = ldr_enable;
oled_rot = oled_header_edge == "-Y" ? 0 : oled_header_edge == "+Y" ? 180 : oled_header_edge == "+X" ? 90 : -90;
oled_w = oled_board_width;  oled_h = oled_board_height;
oled_back_z = lid_thickness + oled_header_plastic_height;              // board back face
oled_top_z  = oled_back_z + oled_pcb_thickness + oled_glass_thickness; // glass top
oled_in_w = oled_w + 2*oled_surround_clearance;
oled_in_h = oled_h + 2*oled_surround_clearance;
oled_out_w = oled_in_w + 2*oled_surround_wall;
oled_out_h = oled_in_h + 2*oled_surround_wall;
// footprint extents in the case frame (axis-aligned)
oled_span_x = (oled_rot % 180 == 0) ? oled_out_w : oled_out_h;
oled_span_y = (oled_rot % 180 == 0) ? oled_out_h : oled_out_w;
ldr_pk_d = ldr_head_diameter + 2*ldr_fit_clearance;
ldr_pk_f = ldr_head_flats + 2*ldr_fit_clearance;
ldr_pk_depth = ldr_head_thickness + 0.2;
ldr_collar_drop = max(0, ldr_pk_depth + ldr_skin_above_head - lid_thickness);   // how far the collar hangs below the lid
ldr_out_d = ldr_pk_d + 2*ldr_collar_wall;
function rotpt2(a, p) = [p[0]*cos(a) - p[1]*sin(a), p[0]*sin(a) + p[1]*cos(a)];
function oled_local(p) = [oled_centre_x, oled_centre_y] + rotpt2(oled_rot, p);
// header pin row centre in the case frame
oled_pin_row = oled_local([0, -oled_h/2 + oled_header_row_from_edge]);
// grille keep-out boxes [x0, x1, y0, y1]
grille_keepouts = concat(
    oled_on ? [[oled_centre_x - oled_span_x/2 - oled_grille_keepout, oled_centre_x + oled_span_x/2 + oled_grille_keepout,
                oled_centre_y - oled_span_y/2 - oled_grille_keepout, oled_centre_y + oled_span_y/2 + oled_grille_keepout]] : [],
    ldr_on ? [[ldr_x - ldr_out_d/2 - oled_grille_keepout, ldr_x + ldr_out_d/2 + oled_grille_keepout,
               ldr_y - ldr_out_d/2 - oled_grille_keepout, ldr_y + ldr_out_d/2 + oled_grille_keepout]] : []);
// split a slot [y0, y1] around the keep-outs that overlap its x-range; drop stubs shorter than min_len
function seg_sub(segs, b, min_len) = [for (sg = segs) each
    (b[1] <= sg[0] || b[0] >= sg[1]) ? [sg]
    : [ if (b[0] - sg[0] >= min_len) [sg[0], b[0]], if (sg[1] - b[1] >= min_len) [b[1], sg[1]] ]];
function seg_all(segs, blocks, min_len, i = 0) = i >= len(blocks) ? segs
    : seg_all(seg_sub(segs, blocks[i], min_len), blocks, min_len, i + 1);
function slot_segments(x0, x1, y0, y1) =
    seg_all([[y0, y1]], [for (k = grille_keepouts) if (x1 > k[0] && x0 < k[1]) [k[2], k[3]]], 2*lid_grille_slot_width);

// rounded rectangle centred on the origin
module rrect_c(w, h, z, r) { translate([-w/2, -h/2, 0]) rrect(w, h, z, r); }
// LDR head outline: a disc with two flats
module ldr_shape_2d(d, f) {
    intersection() { circle(d = d); if (ldr_flats_along == "Y") square([f, d + 2], center = true); else square([d + 2, f], center = true); }
}
module oled_frame() { translate([oled_centre_x, oled_centre_y, 0]) rotate([0, 0, oled_rot]) children(); }
module oled_hole_points() {
    for (sx = [-1, 1], sy = [-1, 1]) translate([sx*(oled_w/2 - oled_hole_inset), sy*(oled_h/2 - oled_hole_inset), 0]) children();
}
module oled_lid_solids() {
    if (oled_on) oled_frame() {
        oled_hole_points() translate([0, 0, lid_thickness - 0.01]) cylinder(d = oled_standoff_diameter, h = oled_header_plastic_height + 0.01);
        if (oled_surround_enable)
            translate([0, 0, lid_thickness - 0.01]) difference() {
                rrect_c(oled_out_w, oled_out_h, oled_top_z - lid_thickness + 0.01, 1.2);
                translate([0, 0, -1]) rrect_c(oled_in_w, oled_in_h, oled_top_z + 2, 0.6);
            }
    }
    if (ldr_on && ldr_collar_drop > 0)
        translate([ldr_x, ldr_y, -ldr_collar_drop]) linear_extrude(ldr_collar_drop + 0.01) ldr_shape_2d(ldr_out_d, ldr_pk_f + 2*ldr_collar_wall);
}
module oled_lid_cuts() {
    if (oled_on) oled_frame() {
        oled_hole_points() translate([0, 0, -lid_lip_height - 1]) cylinder(d = oled_screw_pilot_diameter, h = oled_back_z + lid_lip_height + 2);
        slot_len = (oled_header_pins - 1)*2.54 + 0.64 + 2*oled_pin_slot_extra;
        translate([-slot_len/2, -oled_h/2 + oled_header_row_from_edge - oled_pin_slot_width/2, -lid_lip_height - 1])
            cube([slot_len, oled_pin_slot_width, lid_thickness + lid_lip_height + 2]);
    }
    if (ldr_on) translate([ldr_x, ldr_y, 0]) {
        translate([0, 0, -ldr_collar_drop - 0.01]) linear_extrude(ldr_pk_depth + 0.01) ldr_shape_2d(ldr_pk_d, ldr_pk_f);
        translate([0, 0, -ldr_collar_drop - 1]) cylinder(d = ldr_light_hole_diameter, h = ldr_collar_drop + lid_thickness + 2);
    }
}
module oled_ghost() {
    if (oled_on) oled_frame() {
        color("darkblue", 0.7) translate([-oled_w/2, -oled_h/2, oled_back_z]) cube([oled_w, oled_h, oled_pcb_thickness]);
        color("black", 0.8) translate([-oled_glass_width/2, -oled_h/2 + oled_glass_top_from_header_edge, oled_back_z + oled_pcb_thickness]) cube([oled_glass_width, oled_h - oled_glass_top_from_header_edge - oled_glass_bottom_from_far_edge, oled_glass_thickness]);
        color("gold") for (i = [0:oled_header_pins-1])
            translate([(i - (oled_header_pins-1)/2)*2.54 - 0.32, -oled_h/2 + oled_header_row_from_edge - 0.32, oled_back_z - 10])
                cube([0.64, 0.64, 10 + oled_pcb_thickness]);
        color("dimgray") translate([-(oled_header_pins*2.54)/2, -oled_h/2 + oled_header_row_from_edge - 1.25, lid_thickness])
            cube([oled_header_pins*2.54, 2.5, oled_header_plastic_height]);
    }
    if (ldr_on) color("orange") translate([ldr_x, ldr_y, -ldr_collar_drop]) linear_extrude(ldr_head_thickness) ldr_shape_2d(ldr_head_diameter, ldr_head_flats);
}

// ---------------------------------------------------------------------
//  LID
// ---------------------------------------------------------------------
// Bezel plate, installed orientation, centred on the board: z = 0 is the PCB top face,
// y = -oled_h/2 is the header end. Total thickness = deepest recess + the top skin.
oled_bz_glass_d = oled_glass_thickness + oled_bezel_fit;
oled_bz_pin_d   = oled_bezel_pin_height + oled_bezel_fit;
oled_bz_cable_d = oled_bezel_cable_height + oled_bezel_fit;
oled_bz_t = max(oled_bz_glass_d, oled_bz_pin_d, oled_bz_cable_d) + oled_bezel_face;
module oled_bezel_body() {
    gy0 = -oled_h/2 + oled_glass_top_from_header_edge;
    gy1 =  oled_h/2 - oled_glass_bottom_from_far_edge;
    wy0 = -oled_h/2 + oled_window_top_from_header_edge;
    wy1 =  oled_h/2 - oled_window_bottom_from_far_edge;
    pin_w = oled_header_pins*2.54 + oled_bezel_pin_recess_extra_width;
    cy0 = gy1 - oled_bezel_cable_overlap_into_glass;
    cy1 = oled_h/2 + (oled_bezel_cable_open_to_edge ? 2 : 0);
    difference() {
        rrect_c(oled_in_w - 2*oled_bezel_side_gap, oled_in_h - 2*oled_bezel_side_gap, oled_bz_t, oled_bezel_corner_radius);
        // glass recess (covers the glass and the lower black bezel strip)
        translate([0, (gy0 + gy1)/2, -0.01])
            rrect_c(oled_glass_width + 2*oled_bezel_fit, gy1 - gy0 + 2*oled_bezel_fit, oled_bz_glass_d + 0.01, oled_glass_recess_corner_radius);
        // header pin recess
        translate([oled_bezel_pin_recess_shift_x, -oled_h/2 + oled_bezel_pin_recess_from_edge + oled_bezel_pin_recess_length/2, -0.01])
            rrect_c(pin_w, oled_bezel_pin_recess_length, oled_bz_pin_d + 0.01, 0.4);
        // screen cable recess
        translate([oled_bezel_cable_shift_x, (cy0 + cy1)/2, -0.01])
            rrect_c(oled_bezel_cable_width + 2*oled_bezel_fit, cy1 - cy0, oled_bz_cable_d + 0.01, 0.3);
        // visible window
        translate([oled_window_shift_x, (wy0 + wy1)/2, -1])
            rrect_c(oled_window_width, wy1 - wy0, oled_bz_t + 2, oled_window_corner_radius);
        // screw holes + counterbores
        translate([oled_bezel_hole_shift_x, oled_bezel_hole_shift_y, 0]) oled_hole_points() {
            translate([0, 0, -1]) cylinder(d = oled_bezel_screw_hole, h = oled_bz_t + 2);
            translate([0, 0, oled_bz_t - oled_bezel_head_depth]) cylinder(d = oled_bezel_head_dia, h = oled_bezel_head_depth + 1);
        }
    }
}
module oled_bezel_in_place() {
    if (oled_on && oled_bezel_enable)
        translate([0, 0, wall_h]) oled_frame() translate([0, 0, oled_back_z + oled_pcb_thickness]) oled_bezel_body();
}
module oled_bezel_for_printing() {
    if (oled_on && oled_bezel_enable) translate([0, 0, oled_bz_t]) rotate([180, 0, 0]) oled_bezel_body();
}

module lid() {
    hx0 = esp_x0 + esp_rim + esp_tol + esp_header_start_from_usb_end;
    hlen = esp_header_pins_per_row * esp_header_pin_pitch;
    cy  = esp_y0 + esp_blk_y/2;
    difference() {
        union() {
            translate([-wall_t, -wall_t, 0]) rrect(total_x, total_y, lid_thickness, outer_corner_radius);
            if (corner_ears_enable) for (c = ear_centers())
                hull() {
                    translate([c[0], c[1], 0]) cylinder(d=corner_ear_diameter, h=lid_thickness);
                    translate([c[2], c[3], 0]) cylinder(d=corner_ear_diameter*0.4, h=lid_thickness);
                }
            oled_lid_solids();
            if (lid_lip_enable)
                translate([lid_lip_gap_to_walls, lid_lip_gap_to_walls, -lid_lip_height])
                    difference() {
                        cube([inner_x - 2*lid_lip_gap_to_walls, inner_y - 2*lid_lip_gap_to_walls, lid_lip_height + 0.01]);
                        translate([lid_lip_wall_thickness, lid_lip_wall_thickness, -1])
                            cube([inner_x - 2*lid_lip_gap_to_walls - 2*lid_lip_wall_thickness,
                                  inner_y - 2*lid_lip_gap_to_walls - 2*lid_lip_wall_thickness, lid_lip_height + 2]);
                    }
        }
        // lip cut away above the SDP810
        if (sdp_on && lid_lip_enable && sdp_lid_lip_cutout)
            sdp_frame() translate([-sdp_pk_len/2 - sdp_lip_thickness - sdp_lid_lip_cutout_extra, -1, -lid_lip_height - 1])
                cube([sdp_pk_len + 2*sdp_lip_thickness + 2*sdp_lid_lip_cutout_extra, lid_lip_gap_to_walls + lid_lip_wall_thickness + 1.5, lid_lip_height + 1.01]);
        if (corner_ears_enable) for (c = ear_centers()) {
            translate([c[0], c[1], -1]) cylinder(d=lid_bolt_hole_diameter, h=lid_thickness + 2);
            if (lid_bolt_head_recess_diameter > 0)
                translate([c[0], c[1], lid_thickness - lid_bolt_head_recess_depth]) cylinder(d=lid_bolt_head_recess_diameter, h=lid_bolt_head_recess_depth + 1);
        }
        if (lid_windows_over_esp_headers && esp_has_pin_headers)
            for (s=[-1,1])
                translate([hx0 - lid_header_window_extra_length, cy + s*esp_header_row_spacing/2 - lid_header_window_width/2, -lid_lip_height - 1])
                    cube([hlen + 2*lid_header_window_extra_length, lid_header_window_width, lid_thickness + lid_lip_height + 2]);
        // windows over each sensor's pin header (drawn in the sensor's board frame)
        if (lid_windows_over_sensor_pins)
            for (i = [0:nk-1]) {
                k = kinds[i];
                n = pick(k, bme_pin_count, smoke_pin_count);
                rowd = pick(k, bme_pin_row_distance_from_back_edge, smoke_pin_row_distance_from_back_edge);
                len_along = n*sensor_header_pitch + 2*lid_header_window_extra_length;
                translate([kx0(i), ky0(k), 0]) in_frame(k_rot(k), k_bx(k), k_by(k))
                    translate([k_ox(k) + k_tol(k) + rowd - lid_header_window_width/2,
                               k_oy(k) + k_tol(k) + k_W(k)/2 - len_along/2, -lid_lip_height - 1])
                        cube([lid_header_window_width, len_along, lid_thickness + lid_lip_height + 2]);
            }
        if (lid_grille_over_sensors_enable) {
            gx0 = first_x0 + lid_grille_margin;
            gx1 = sensors_end_x - lid_grille_margin;
            // slots run the full width of the lid, ending the same distance from each wall as the closer side would
            m_near = min(sens_y_base + lid_grille_margin, inner_y - (sens_y_base + maxsens_y - lid_grille_margin));
            gy0 = m_near;
            gy1 = inner_y - m_near;
            span = gx1 - gx0;
            if (span > lid_grille_slot_width) {
                n = floor((span - lid_grille_slot_width)/lid_grille_slot_spacing) + 1;
                used = (n-1)*lid_grille_slot_spacing + lid_grille_slot_width;
                st = gx0 + (span - used)/2;
                for (i=[0:n-1]) {
                    x0 = st + i*lid_grille_slot_spacing;
                    for (sg = slot_segments(x0, x0 + lid_grille_slot_width, gy0, gy1))
                        translate([x0, sg[0], -lid_lip_height - 1])
                            cube([lid_grille_slot_width, sg[1] - sg[0], lid_thickness + lid_lip_height + 2]);
                }
            }
        }
        oled_lid_cuts();
    }
}

// ---------------------------------------------------------------------
//  PREVIEW STAND-INS
// ---------------------------------------------------------------------
module ghosts() {
    color("green", 0.6) translate([esp_x0 + esp_rim + esp_tol, esp_y0 + esp_rim + esp_tol, floor_t + esp_platform_height])
        cube([esp_board_length_x, esp_board_width_y, esp_pcb_thickness]);
    if (sdp_on) sdp_frame() sdp_ghost();
    translate([0, 0, wall_h]) oled_ghost();
    for (i = [0:nk-1]) {
        k = kinds[i];
        color(k == "bme" ? "blue" : k == "smoke" ? "orange" : "red", 0.6) at_sensor(i) {
            translate([k_ox(k) + k_tol(k), k_oy(k) + k_tol(k), floor_t + k_plat(k)])
                linear_extrude(k_t(k)) polygon(board_outline(k_L(k), k_W(k), k_recL(k), k_recD(k)));
        }
    }
}

// ---------------------------------------------------------------------
//  OUTPUT
// ---------------------------------------------------------------------
module lid_for_printing() {
    translate([0, total_y - 2*wall_t, lid_thickness]) rotate([180, 0, 0]) lid();
}
module retainer_in_place() {
    translate([esp_x0 + esp_rim + esp_ret_cx, esp_y0 + esp_rim + esp_ret_cy, esp_boss_top_z]) retainer_clip();
}

module scene() {
    if (part_to_generate == "base") base();
    else if (part_to_generate == "lid") lid_for_printing();
    else if (part_to_generate == "retainer_clip") retainer_clip();
    else if (part_to_generate == "oled_bezel") oled_bezel_for_printing();
    else if (part_to_generate == "all_parts_flat") {
        base();
        translate([total_x + spacing_between_parts_when_flat + max(2*corner_ear_offset_outward + corner_ear_diameter, 2*mount_reach), 0, 0]) lid_for_printing();
        translate([0, -spacing_between_parts_when_flat - 12 - mount_reach, 0]) retainer_clip();
        translate([0, total_y + spacing_between_parts_when_flat + oled_out_h/2 + mount_reach, 0]) oled_bezel_for_printing();
    } else {
        base();
        translate([0, 0, wall_h]) lid();
        if (esp_retainer_enable) retainer_in_place();
        oled_bezel_in_place();
        if (show_board_ghosts) ghosts();
    }
}

if (show_cutaway_view) {
    difference() { scene(); translate([-50, inner_y/2, -50]) cube([total_x + 100, total_y, 200]); }
} else scene();

echo(str("Cavity: ", inner_x, " x ", inner_y, " x ", inner_h, " mm"));
echo(str("Outside (no ears): ", total_x, " x ", total_y, " x ", wall_h + lid_thickness, " mm"));
if (sdp_on) {
    echo(str("SDP810 on wall ", sdp_wall, ", centre ", sdp_pos, " mm along it, port axis ", sdp_port_z, " mm above the base underside"));
    if (sdp_wall == "-Y" && sdp_pos - sdp_body_length/2 < esp_x0 + esp_blk_x && esp_y0 < sdp_body_depth + sdp_rear_clearance)
        echo("WARNING: the SDP810 overlaps the ESP block - increase sdp_offset_along_wall");
    if (sdp_wall == "-Y" && sdp_body_depth + sdp_rear_clearance > sens_y_base && sdp_pos + sdp_body_length/2 > first_x0 && is_row == false)
        echo("WARNING: less than sdp_rear_clearance behind the SDP810 before the sensor row");
    echo(str("SDP810 pocket ", sdp_pk_len, " x ", sdp_pk_dep, " mm on a ", sdp_lift, " mm seat; body top ",
             inner_h - sdp_lift - sdp_body_height, " mm under the lid (nominal body), ",
             inner_h - sdp_lift - sdp_body_height - sdp_height_tolerance, " mm (tallest body)"));
    if (wall_t > sdp_neck_length - 0.3) echo("NOTE: wall is thicker than the SDP neck gap - outer pockets are cut around the ports");
}
if (mounting_tabs_enable) echo(str("Footprint with mounting tabs: ", total_x + 2*mount_reach, " x ", total_y + 2*mount_reach, " mm"));
if (oled_on) {
    echo(str("OLED: surround ", oled_span_x, " x ", oled_span_y, " mm, top ", oled_top_z - lid_thickness, " mm above the lid; header pins at x ",
             oled_pin_row[0], ", y ", oled_pin_row[1], " (about ", 10 - oled_header_plastic_height - lid_thickness, " mm of pin below the lid)"));
    if (oled_centre_x - oled_span_x/2 < -wall_t || oled_centre_x + oled_span_x/2 > inner_x + wall_t ||
        oled_centre_y - oled_span_y/2 < -wall_t || oled_centre_y + oled_span_y/2 > inner_y + wall_t)
        echo("WARNING: the OLED surround overhangs the lid edge");
    if (sdp_on && sdp_wall == "-Y" && oled_pin_row[1] < sdp_pk_dep + sdp_lip_thickness + 1
        && abs(oled_pin_row[0] - sdp_pos) < sdp_pk_len/2 + sdp_lip_thickness + 7)
        echo("WARNING: the OLED header pins come down onto the SDP810 - move the display");
}
if (ldr_on) {
    echo(str("LDR: pocket at x ", ldr_x, ", y ", ldr_y, "; collar hangs ", ldr_collar_drop, " mm under the lid"));
    if (oled_on && abs(ldr_x - oled_centre_x) < (oled_span_x + ldr_out_d)/2 && abs(ldr_y - oled_centre_y) < (oled_span_y + ldr_out_d)/2)
        echo("WARNING: the LDR sits under the OLED surround - move one of them");
    if (lid_lip_enable && (ldr_x + ldr_out_d/2 > inner_x - lid_lip_gap_to_walls - lid_lip_wall_thickness || ldr_x - ldr_out_d/2 < lid_lip_gap_to_walls + lid_lip_wall_thickness
        || ldr_y + ldr_out_d/2 > inner_y - lid_lip_gap_to_walls - lid_lip_wall_thickness || ldr_y - ldr_out_d/2 < lid_lip_gap_to_walls + lid_lip_wall_thickness))
        echo("WARNING: the LDR collar hits the lid lip - move it inward");
    if (sdp_on && sdp_wall == "-Y" && ldr_y - ldr_out_d/2 < sdp_pk_dep + sdp_lip_thickness && abs(ldr_x - sdp_pos) < sdp_pk_len/2 + sdp_lip_thickness + ldr_out_d/2)
        echo("WARNING: the LDR collar sits over the SDP810 body - move it");
}
// warn when a moved block ends up outside the cavity
for (i = [0:nk-1]) if (kx0(i) < 0 || ky0(kinds[i]) < 0 || kx0(i) + k_gx(kinds[i]) > inner_x || ky0(kinds[i]) + k_gy(kinds[i]) > inner_y)
    echo(str("WARNING: the ", kinds[i], " block pokes into a wall - reduce its offset"));
if (esp_x0 < 0 || esp_y0 < 0) echo("WARNING: the ESP block pokes into a wall - reduce its offset");
