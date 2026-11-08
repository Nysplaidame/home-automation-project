# VentSys Wiring Reference
# Physical wiring guide for ESP32 sensor and control boards
# Confirmed GPIO assignments are taken from the deployed ESPHome YAML configs.
# Assignments marked PLACEHOLDER need to be confirmed during physical build.

> **Safety note:** ESP32 ADC pins are 3.3V maximum. Do NOT connect 5V sensor outputs directly. Use a voltage divider or a level-shifter module.

---

## Board inventory

| Board | ESPHome name | IP | YAML |
|---|---|---|---|
| Main fan controller | `ventsys-main-fan` | 192.168.50.21 | `ventsys_fan_controller.yaml` |
| Booth fan controller | `ventsys-booth-fan` | 192.168.50.22 | `ventsys_booth_fan.yaml` |
| FDM sensor array 1 | `ventsys-fdm-array-1` | 192.168.50.31 | `ventsys_fdm_array_1.yaml` |
| FDM sensor array 2 | `ventsys-fdm-array-2` | 192.168.50.32 | `ventsys_fdm_array_2.yaml` |
| SLA sensor array 1 | `ventsys-sla-array-1` | 192.168.50.33 | `ventsys_sla_array_1.yaml` |
| SLA sensor array 2 | `ventsys-sla-array-2` | 192.168.50.34 | `ventsys_sla_array_2.yaml` |
| Garage air sensor | `ventsys-garage-air-sensor` | 192.168.50.35 | `ventsys_garage_air_sensor.yaml` |
| FDM pipe air sensor | `ventsys-fdm-pipe-air-sensor` | 192.168.50.36 | `ventsys_fdm_pipe_air_sensor.yaml` |
| SLA pipe air sensor | `ventsys-sla-pipe-air-sensor` | 192.168.50.37 | `ventsys_sla_pipe_air_sensor.yaml` |
| FDM airflow sensor | `ventsys-fdm-airflow` | 192.168.50.41 | `ventsys_fdm_airflow.yaml` |
| SLA airflow sensor | `ventsys-sla-airflow` | 192.168.50.42 | `ventsys_sla_airflow.yaml` |
| Booth airflow sensor | `ventsys-booth-airflow` | 192.168.50.43 | `ventsys_booth_airflow.yaml` |
| SLA print valve controller | `ventsys-sla-print-valve` | 192.168.50.56 | `configs/esphome/ventsys_sla_print_valve.yaml` |

Sensor arrays and air sensors use ESP32-C6 boards with ESP-IDF firmware. Exposed Home Assistant entity names use `ventsys_` prefixes, for example `sensor.ventsys_fdm_pipe_air_temperature`, while ESPHome hostnames remain DNS-safe with hyphens.

---

## Board 1 - Fan Controller (192.168.50.21)

Controls the inline duct fan via PWM. Fan must accept 0-10V or PWM control signal. Confirm fan model supports this before wiring.

| GPIO | Function | Wire colour (suggestion) | Notes |
|---|---|---|---|
| GPIO23 | Fan PWM output | Yellow | 25kHz PWM via MOSFET or fan driver board |
| GND | Common ground | Black | Share with fan driver GND |
| 3.3V | ESP logic power | Red | From on-board 3.3V regulator |
| 5V / VIN | ESP board power | Red | 5V USB or external PSU |

**Fan driver circuit:** ESP32 GPIO23 (3.3V) to MOSFET gate or fan PWM input. Do not connect fan power directly to GPIO.

---

## Valve controllers (192.168.50.51-62)

Each butterfly valve has its own ESP32. Do not wire multiple valve servos to a
single controller unless its ESPHome configuration is deliberately redesigned.

| Controller family | Devices | Servo PWM | Feedback ADC | Touch toggle | Status LED |
|---|---|---|---|---|---|
| Standard ESP32 valve controller | Main 1 `.51`, E2/SLA branch `.52`, FDM branch `.53`, FDM print `.55`, SLA print `.56`, Main 2 `.57` | GPIO16 | GPIO35 (ADC1_CH7) only on feedback variants | GPIO33 | GPIO21 (WS2812) |
| Legacy 360° intake valve controller | SLA 360 `.61`, FDM 360 `.62` | GPIO4 | Not part of the legacy design | GPIO33 | GPIO21 (WS2812) |

The unconfirmed `*_360_valve_v2_nerdiy.yaml` variants are not wiring sources;
they use provisional GPIO0/GPIO1 substitutions and must not be flashed or wired
until the installed board is physically identified.

| Connection | Standard valve boards | Legacy 360° valve boards | Notes |
|---|---|---|---|
| Servo signal | GPIO16 | GPIO4 | 50Hz PWM |
| Servo feedback | GPIO35 / ADC1_CH7 through the feedback network | Not part of the legacy design | Raw voltage, calibrated position, disconnected-wire and position-mismatch diagnostics |
| Touch input | GPIO33 | GPIO33 | Optional local toggle |
| WS2812 DIN | GPIO21 | GPIO21 | On-board status LED |
| Servo ground | Common GND | Common GND | Share with ESP32 and 5V supply |
| Servo power | Dedicated 5V rail | Dedicated 5V rail | Do not use ESP32 3.3V rail |
| ESP32 power | 5V/VIN or USB | 5V/VIN or USB | Size supply for board and servo load |

For bench calibration with ESP32 on PC USB and servo on a separate 5 V supply,
connect the servo red wire directly to the separate supply's +5 V and its
brown wire to that supply's GND. Join that GND to ESP32 GND; retain GPIO16
signal and the protected GPIO35 feedback connection. Do **not** connect the
separate supply's +5 V to the board's 5 V pin or parallel it with PC USB +5 V.
Use a suitable supply breakout/splitter to access the servo rail. A supply's
4 A rating does not remove current/voltage-drop concerns if the servo is fed
through the controller board's USB and 5 V pin path.

**E2 branch valve as built:**
The board with MAC `ec:e3:34:b4:79:7c` was previously called Main Duct Valve 2
during bench testing. On 2026-10-06 it was reassigned to the E2/SLA branch
position in the garage diagram. It has a normal three-wire servo on GPIO16,
with no connected feedback lead or GPIO35 conditioning network. The earlier
`esp32-d1-mini-servo-feedback-wiring.html` records the superseded feedback-servo
build, not the present E2 installation. The separate-supply paragraph above
describes a possible test setup.

**MAIN-2 board as built for range testing:**
MAC `ec:e3:34:67:a0:18` now runs `ventsys_main_valve2.yaml` at
`192.168.50.57`, with a normal three-wire servo on GPIO16, GPIO21 status LED,
and GPIO33 touch toggle enabled in firmware. No feedback lead or GPIO35 network
is used. The 940–2000 µs command range is copied from E2 for initial testing;
neither physical stop has been accepted for MAIN-2. HA's 0–100 position is a
restored command, not measured horn position.

**MAIN-1 board as built for range testing:**
MAC `EC:E3:34:67:8C:9C` runs `ventsys_main_valve1.yaml` at
`192.168.50.51`. Its normal three-wire servo uses GPIO16 PWM and board
5 V/GND; GPIO21 drives the status LED and GPIO33 is enabled for touch toggle.
No feedback lead or GPIO35 network is fitted. The 940–2000 µs command window
is provisional until MAIN-1's physical stops are calibrated. HA's position
is a saved command, not a measured horn angle.

**Servo wiring (feedback-capable standard controller):** Brown = GND, Red = 5V
power, Orange = PWM signal, plus the servo's feedback lead (colour varies by
supplier). The legacy 360° design remains a three-wire servo controller.

### Standard-valve feedback network

The standard controller uses the feedback-capable servo's fourth lead. Do not
connect it directly to the ESP32 ADC. The intended carrier topology is:

```text
servo feedback ── 10k series resistor ── ADC node ── GPIO35 / ADC1_CH7
                                         ├── 20k ── GND
                                         └── 100nF ── GND
```

The feedback node and ESP32 share the servo's common ground. The production
ESPHome files expose the protected raw voltage, a calibrated 0-100% feedback
position, a disconnected-wire problem entity, and a delayed commanded-versus-
measured position-mismatch entity. Calibration values are substitutions at the
top of each valve YAML and must be replaced with that valve's measured endpoints.

The 2026-09-23 main-valve-2 bench test established the initial baseline used in
the files: closed after PWM detach `0.464V`, open `1.123V`, disconnected
`0.075V`, disconnected threshold `0.200V`, and mismatch tolerance `10%` after
three seconds. Ten open/closed cycles produced only `9mV` open spread and
`11mV` closed spread, with no reset or brownout. These values are provisional
for every other valve until it is bench-calibrated. Before connecting any
board, confirm the carrier output never exceeds the ESP32's 3.3V ADC limit.

---

## Air Sensor and Sensor Array Boards (192.168.50.31-37)

The three air sensors and four sensor arrays share `ventsys_air_sensor_base.yaml`.
The four enclosure arrays use the printed sensor carrier (Waveshare ESP32-C6-Zero,
Pimoroni BME680, DFRobot SEN0570 MEMS smoke, DFRobot SEN0564 MEMS CO) and also
include `ventsys_air_sensor_co.yaml` for the CO channel. Two optional packages
cover the array add-ons (enable them per wrapper where the hardware is fitted):
`ventsys_air_sensor_dp.yaml` (Sensirion SDP810-125Pa differential pressure) and
`ventsys_air_sensor_display.yaml` (0.96" SSD1306 OLED + GL5528 LDR auto-brightness):

| Device | IP | YAML | MQTT topic prefix | Entity prefix |
|---|---:|---|---|---|
| FDM sensor array 1 | 192.168.50.31 | `ventsys_fdm_array_1.yaml` | `ventsys/fdm/array_1` | `ventsys_fdm_array_1` |
| FDM sensor array 2 | 192.168.50.32 | `ventsys_fdm_array_2.yaml` | `ventsys/fdm/array_2` | `ventsys_fdm_array_2` |
| SLA sensor array 1 | 192.168.50.33 | `ventsys_sla_array_1.yaml` | `ventsys/sla/array_1` | `ventsys_sla_array_1` |
| SLA sensor array 2 | 192.168.50.34 | `ventsys_sla_array_2.yaml` | `ventsys/sla/array_2` | `ventsys_sla_array_2` |
| Garage air sensor | 192.168.50.35 | `ventsys_garage_air_sensor.yaml` | `ventsys/garage/air` | `ventsys_garage_air` |
| FDM pipe air sensor | 192.168.50.36 | `ventsys_fdm_pipe_air_sensor.yaml` | `ventsys/fdm/pipe_air` | `ventsys_fdm_pipe_air` |
| SLA pipe air sensor | 192.168.50.37 | `ventsys_sla_pipe_air_sensor.yaml` | `ventsys/sla/pipe_air` | `ventsys_sla_pipe_air` |

The installed SLA pipe board uses CO `A` on GPIO3 and BME680 SDA/SCL on
GPIO4/5 at I2C address `0x77`. It has no configured smoke channel. The CO
output is presently near the ADC rail and faulted; check wiring before use.

### GPIO map

| GPIO | Function | Component | Notes |
|---|---|---|---|
| GPIO3 | ADC1_CH3 input | SEN0570 MEMS smoke `A` | 3.3V max; module powered from 3V3 |
| GPIO2 | ADC1_CH2 input | SEN0564 MEMS CO `A` (arrays only) | 3.3V max; module powered from 3V3 |
| GPIO0 | ADC1_CH0 input | GL5528 LDR divider (display package) | 3V3 -> LDR -> GPIO0 -> 10k -> GND; brighter = higher voltage |
| GPIO4 | I2C SDA | BME680 (0x76), SDP810 (0x25), OLED (0x3C) | MTMS strapping pin; only selects the JTAG source when an eFuse enables it, so the breakout pull-ups are safe. Bus runs at 400 kHz |
| GPIO5 | I2C SCL | BME680, SDP810, OLED | MTDI strapping pin; same note as GPIO4 |
| GPIO8 | Status LED | On-board WS2812 (C6-Zero) | Bright red = alarm active; dim red = alarm latched; orange = temperature rising fast; yellow = sensor fault; blue = gas-sensor heaters settling; purple = API/MQTT down; dim green = OK |
| 3.3V | Sensor VCC | BME680, SEN0570, SEN0564, SDP810, OLED, LDR | Both MEMS modules are rated 3.3-5V; 3V3 supply keeps `A` inside the ADC range. Worst case about 80-100 mA with everything fitted. 10 uF + 100 nF ceramic across 3V3/GND at the splice |
| GND | Common ground | All sensors | Required for I2C and ADC reference |

All of these sit on the C6-Zero's left header (5V, GND, 3V3, GP0-GP5), so the
right header can stay unwired.

### BME680 wiring (Pimoroni breakout, I2C, 3.3V)

```text
3.3V  -> 3-6V / VCC
GND   -> GND
GPIO4 -> SDA
GPIO5 -> SCL
```

The Pimoroni breakout answers on `0x76` by default and on `0x77` after its
ADDR trace is cut (older revisions: bridge the ADDR pads). The shared YAML
default is `bme680_address: "0x76"`; set `bme680_address: "0x77"` in a wrapper
only for a board whose trace has been cut. `i2c: scan: true` logs the address
found at boot.

### Power / I2C splice carrier

The 3V3 and GND joints, the two decoupling capacitors and the LDR pull-down
resistor sit on a printed glue-down carrier:
`main/assets/3d-printing/Splice Carrier/` (README, SCAD, concept PNG).
SDA and SCL are not on the carrier; join them off-board (GPIO4 / GPIO5 to the
BME680, SDP810 and OLED).

```text
ESP 3V3   -> 3V3 rail -> BME680, SDP810, smoke, CO, OLED VCC, LDR leg 1
ESP GND   -> GND rail -> BME680, SDP810, smoke, CO, OLED GND
ESP GPIO0 -> LDR rail -> LDR leg 2      (10k from LDR rail to GND rail)
10 uF X7R/X5R 16 V + 100 nF ceramic across 3V3 rail / GND rail
```

### SDP810-125Pa wiring (differential pressure, optional package)

```text
SDP810 pin 1 SCL -> GPIO5 (I2C) pin 2 VDD -> 3V3 rail
SDP810 pin 3 GND -> GND rail     pin 4 SDA -> GPIO4 (I2C)
```

2.0 mm pitch pins, I2C `0x25` (SDP8x1 variants use `0x26`; set `sdp_address`).
Port H stays open to the enclosure air, port L is tubed to the garage, so the
reading is enclosure minus garage: negative = enclosure held below garage
pressure. Zero it once with the extraction fan off using `dp_capture_zero`.

### OLED display and LDR wiring (optional display package)

```text
OLED (0.96" SSD1306, 4-pin)      GL5528 LDR
VCC -> 3V3 rail                  leg 1 -> 3V3 rail
GND -> GND rail                  leg 2 -> LDR rail (GPIO0, 10k to GND)
SCL -> GPIO5 (I2C bus)
SDA -> GPIO4 (I2C bus)
```

Check the pin labels on the module itself: 52Pi S-0018 is GND, VCC, SCL, SDA,
but many clones swap GND and VCC. Default address `0x3C` (`display_address`
substitution for `0x3D` units). The display sits on top of the case lid; only
its header passes through the lid into the space behind the SDP810. The LDR
sits in a pocket under the lid and looks out through a 3.5 mm hole.

Screen layout (yellow band = header, 3 x 2 readings below, alarm takeover and a
5 s diagnostics page each minute): `ventsys_array_oled_layout.png` in this folder.

### MEMS smoke and CO sensor wiring

```text
SEN0570 smoke            SEN0564 CO (arrays only)
3.3V -> VCC              3.3V -> VCC
GND  -> GND              GND  -> GND
A    -> GPIO3            A    -> GPIO2
```

Power both modules from 3V3, not 5V: their `A` output can then never exceed the
ADC limit. DFRobot rates both as qualitative only (no ppm calibration). The
firmware converts each reading to the sensing resistance ratio Rs/R0 using the
4.7k load resistor, and alarms when the ratio falls below 0.50 against a
clean-air baseline. Capture the baseline once per board with the
`*_capture_clean_air_baseline` button after the sensor has run in clean air;
until then a 1.50 V fallback threshold applies. Alarms are suppressed for the
first 180 s after power-up while the heaters settle.

### Metric update cadence

| Signal | ESPHome update interval |
|---|---:|
| BME680 temperature, humidity, barometric pressure (hPa and Pa), gas resistance | 10s (IIR 3x) |
| Temperature rise rate | 30s, averaged over ~2 minutes |
| Smoke and CO voltage, Rs/R0 ratio | 5s |
| Smoke detected binary sensor | delayed-on 3s, delayed-off 10s; MQTT state republished every 30s |
| CO detected binary sensor (arrays) | delayed-on 5s, delayed-off 15s; MQTT state republished every 30s |
| High temperature binary sensor | BME680 temperature with delayed-on 10s |
| Temperature rising fast (early warning, not latched) | rise rate above threshold, delayed-off 120s |
| Sensor fault | BME680 silent >45s, or MEMS output <0.02V / within 0.05V of 3V3 for 15s |
| SDP810 differential pressure (dp package) | 1s samples, published as a 5s average |
| Ambient light from the LDR (display package) | 1s, median of 5 |
| OLED refresh (display package) | 500ms (also the alarm flash rate) |
| Online MQTT heartbeat | 30s |
| ESPHome status binary sensor | status-change driven by ESPHome |

### Alarms, thresholds and calibration (Home Assistant entities)

- Thresholds are config `number` entities on each board, so they can be
  changed from the garage dashboard without reflashing: temperature alarm,
  temperature-rise alarm, smoke and CO Rs/R0 ratio, smoke and CO fallback
  voltage. Wrapper substitutions only set their first-boot values.
- `pressure_offset` (Pa) is added to the BME680 pressure before publishing.
  Set it from Home Assistant with the fans off so each enclosure board matches
  the garage reference before differential pressure is calculated.
- Smoke, CO and high-temperature alarms set `alarm_latched`, which survives a
  reboot and clears only when `acknowledge_alarms` is pressed with no alarm
  active. The rate-of-rise warning is not latched.
- Display package: `display_enabled`, `display_off_when_dark` and
  `display_diagnostics_page` switches; `display_dark_level` /
  `display_bright_level` (% ambient) and `display_min_brightness` /
  `display_max_brightness` set the auto-brightness curve. Any smoke, CO or
  high-temperature alarm wakes the screen at full brightness.
- dp package: `dp_zero_offset` (Pa) and the `dp_capture_zero` button.
- `sensor_fault` combines BME680, smoke, CO and SDP810 faults. A faulted gas sensor
  cannot raise or clear its alarm; it reports `fault` on `<prefix>/fault`.

---

## PrintAirPipe duct servo valve wiring

PrintAirPipe 125mm butterfly valves use MG90S micro servos mounted in printed housings.

| Valve name | MQTT topic | Controller GPIO | Controller IP |
|---|---|---|---|
| E2 / SLA branch valve (installed board) | `ventsys/sla/branch/control` | GPIO16 PWM; no feedback ADC | `.52` |
| Main duct valve 1 (bench board) | `ventsys/main/valve1/control` | GPIO16 PWM; no feedback ADC | `.51` |
| Main duct valve 2 (bench board) | `ventsys/main/valve2/control` | GPIO16 PWM; no feedback ADC | `.57` |
| E1 / FDM branch valve (bench board) | `ventsys/fdm/branch/control` | GPIO16 PWM; no feedback ADC | `.53` |
| FDM enclosure / print valve | `ventsys/fdm/valve/control` | GPIO16 PWM + GPIO35 feedback ADC | `.55` |
| FDM 360 intake valve | `ventsys/fdm/360/control` | GPIO4 PWM only | `.62` |
| SLA enclosure / print valve | `ventsys/sla/valve/control` | GPIO16 PWM + GPIO35 feedback ADC | `.56` |
| SLA 360 intake valve | `ventsys/sla/360/control` | GPIO4 PWM only | `.61` |

Repeated GPIO assignments are intentional because each valve controller is a
separate ESP32. The installed standard-valve bench boards use GPIO16 PWM
without feedback; GPIO35 applies only to future feedback-capable variants.
GPIO4 is the active legacy 360°-valve assignment.

## Airflow sensor boards (192.168.50.41-43)

| Device | Pulse input | WS2812 LED output | Notes |
|---|---|---|---|
| FDM airflow `.41` | GPIO0, inverted `INPUT_PULLUP` | GPIO1 | Active FDM configuration |
| SLA airflow `.42` | GPIO0, inverted `INPUT_PULLUP` | GPIO1 | Corrected to installed SLA wiring, 2026-10-19 |
| Booth airflow `.43` | GPIO10, inverted `INPUT_PULLUP` | GPIO9 | Active booth configuration |

Keep the pulse-sensor output at ESP32-C6-safe logic voltage. If the selected
sensor output is higher than 3.3V, use a level shifter before its GPIO input.

## Fan controller boards (192.168.50.21-22)

| Device | PWM output | Frequency | Interface |
|---|---|---:|---|
| Main inline fan `.21` | GPIO23 | 25kHz | Fan PWM input or suitable MOSFET/driver |
| Spray booth fan `.22` | GPIO23 | 25kHz | Fan PWM input or suitable MOSFET/driver |

GPIO23 is a 3.3V logic control signal only. Power the fan from an appropriately
rated supply and do not connect mains or fan power to an ESP32 GPIO.

---

## Power distribution summary

| Rail | Source | Consumers |
|---|---|---|
| 5V 3A | USB power bank or wall adapter | ESP32 boards via USB/VIN, servo power where needed |
| 3.3V | ESP32 on-board regulator | BME680, 3.3V smoke/MEMS modules, ADC inputs |
| 12V or 240V | Separate PSU / mains | Inline duct fan, check fan voltage spec |

Keep ESP 3.3V logic and servo/fan power separate. A noisy motor rail can cause ESP32 brownouts.

---

## Checklist before first power-on

- [ ] All ADC inputs checked for 3.3V compliance
- [ ] BME680 wired to GPIO4/GPIO5 and the YAML `bme680_address` matches the
  Pimoroni ADDR trace (uncut = 0x76)
- [ ] SEN0570 smoke `A` on GPIO3 and SEN0564 CO `A` on GPIO2, both modules powered from 3V3
- [ ] Servo power from 5V rail, not from ESP 3.3V
- [ ] Standard-valve feedback lead passes through the 10k/20k/100nF network to
  GPIO35, shares GND, and measures no more than 3.3V at the ADC node
- [ ] Fan driver MOSFET or driver board fitted
- [ ] Common GND shared between ESP boards, sensors, and motor drivers
- [ ] ESPHome `secrets.yaml` filled in with WiFi, MQTT, API, OTA, and TLS CA values
