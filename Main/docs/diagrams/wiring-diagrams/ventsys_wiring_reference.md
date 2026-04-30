# VentSys Wiring Reference
# Physical wiring guide for ESP32 sensor and control boards
# Confirmed GPIO assignments are taken from the deployed ESPHome YAML configs.
# Assignments marked PLACEHOLDER need to be confirmed during physical build.

> **Safety note:** ESP32 ADC pins are 3.3V maximum. Do NOT connect 5V sensor outputs directly. Use a voltage divider (10kΩ / 20kΩ) or a level-shifter module.

---

## Board inventory

| Board | ESPHome name | IP | YAML |
|---|---|---|---|
| Main fan controller | `ventsys-main-fan` | 192.168.50.21 | `ventsys_fan_controller.yaml` |
| SLA print valve controller | `ventsys-sla-print-valve` | 192.168.50.56 | `configs/esphome/ventsys_sla_print_valve.yaml` (canonical deployable) |
| FDM sensor board | `ventsys-fdm-sensor` | 192.168.50.31 | `ventsys_fdm_sensor.yaml`  # A6-4 fix: per-device YAML (A4-4) |
| SLA sensor board | `ventsys-sla-sensor` | 192.168.50.32 | `ventsys_sla_sensor.yaml`  # A6-4 fix: per-device YAML (A4-4) |
| Garage ambient sensor | `ventsys-garage-sensor` | 192.168.50.34 | `ventsys_garage_sensor.yaml` |

All boards: ESP32-DevKitC (38-pin) or equivalent. Powered 5V via USB or VIN pin from 5V rail.

---

## Board 1 — Fan Controller (192.168.50.21)

Controls the inline duct fan via PWM. Fan must accept 0–10V or PWM control signal — confirm fan model supports this before wiring.

| GPIO | Function | Wire colour (suggestion) | Notes |
|---|---|---|---|
| GPIO23 | Fan PWM output | Yellow | 25kHz PWM via MOSFET or fan driver board |
| GND | Common ground | Black | Share with fan driver GND |
| 3.3V | ESP logic power | Red | From on-board 3.3V reg |
| 5V / VIN | ESP board power | Red | 5V USB or external PSU |

**Fan driver circuit:** ESP32 GPIO23 (3.3V) → MOSFET gate (e.g. IRLZ44N) → fan PWM wire. Do not connect fan directly to GPIO — fan draws more current than the pin can source.

**Fan speed sense (optional):** Fan tachometer → GPIO input with 10kΩ pull-up to 3.3V. Add to ESPHome config if needed.

---

## Board 2 — Valve Controller (192.168.50.56)

Controls one or more MG90S servo motors driving butterfly valves.

| GPIO | Function | Notes |
|---|---|---|
| GPIO18 | Servo 1 PWM (SLA main valve) | 50Hz PWM — confirmed in YAML |
| GPIO19 | Servo 2 PWM (PLACEHOLDER) | Additional valve — add to YAML if used |
| GPIO20 | Servo 3 PWM (PLACEHOLDER) | Additional valve |
| GPIO21 | Servo 4 PWM (PLACEHOLDER) | Additional valve |
| GND | Common ground | Share with all servo GND wires |
| 5V / VIN | Servo power | Servos need 5V at up to 500mA each — use dedicated 5V rail, NOT ESP 3.3V |

**Power:** Drive servos from a separate 5V 2A (or higher) supply. Connect servo GND to ESP GND. Only the PWM signal wire connects to the ESP GPIO.

**Servo wiring (MG90S):** Brown = GND, Red = 5V power, Orange = PWM signal.

---

## Board 3 — FDM Enclosure Sensor Board (192.168.50.31)

| GPIO | Function | Component | Notes |
|---|---|---|---|
| GPIO4 | 1-Wire data | DS18B20 temperature | 4.7kΩ pull-up resistor between GPIO4 and 3.3V |
| GPIO21 | I2C SDA | BME680 | Shared bus — pull-up 4.7kΩ to 3.3V |
| GPIO22 | I2C SCL | BME680 | Shared bus — pull-up 4.7kΩ to 3.3V |
| GPIO34 | ADC input | MQ-2 or MQ-135 (smoke/VOC) | ADC1 only, 3.3V max — use voltage divider if sensor outputs 5V |
| GPIO35 | ADC input | Differential pressure sensor | ADC1 only, 3.3V max |
| GPIO2 | Status LED | Built-in LED | Active HIGH on most dev boards |
| 3.3V | Sensor VCC | BME680, DS18B20 | 3.3V sensors |
| 5V / VIN | MQ sensor heater | MQ-2/MQ-135 heater coil | MQ sensors require 5V for heater — logic output is still 3.3V-safe |
| GND | Common ground | All sensors | |

### DS18B20 wiring

```
3.3V ──┬──── DS18B20 VCC (red)
       │
      4.7kΩ
       │
GPIO4 ─┴──── DS18B20 DATA (yellow/white)
GND ──────── DS18B20 GND (black)
```

After first flash, run with `logger: level: DEBUG` and check serial output for:
`Found Dallas device 0x<address>` — copy that address into the ESPHome YAML.

### BME680 wiring (I2C, 3.3V)

```
3.3V ─── VCC
GND  ─── GND
GPIO21 ─ SDA
GPIO22 ─ SCL
SDO  ─── GND (sets I2C address to 0x76)
       or
SDO  ─── 3.3V (sets I2C address to 0x77)
```

Default in YAML is `address: 0x76` (SDO to GND).
The BME680 also exposes a gas resistance reading on the same I2C bus —
no additional wiring needed beyond the four standard I2C pins.

### MQ sensor wiring (5V heater, 3.3V-safe output)

```
5V   ─── VCC (heater)
GND  ─── GND
AOUT ─┬─ [10kΩ] ─── GND     ← voltage divider — bring 0-5V output down to 0-3.3V
      └─ GPIO34              ← connect divider midpoint to ESP ADC pin
```

Allow 24–48h burn-in before calibrating thresholds. Take clean-air ADC readings and set smoke alarm threshold in YAML accordingly.

---

## Board 4 — SLA Enclosure Sensor Board (192.168.50.32)

Identical wiring to Board 3 (FDM sensor board). Use `ventsys_sla_sensor.yaml`  # A6-4 fix: per-device YAML exists (A4-4). The substitutions below are pre-set in that file:
```yaml
substitutions:
  device_name: ventsys-sla-sensor
  friendly_name: "SLA Enclosure Sensors"
  device_ip: "192.168.50.32"
  mqtt_topic_prefix: "ventsys/sla"
```

Adjust temperature alarm threshold to 40°C in the binary_sensor block (SLA resin is more temperature sensitive than FDM).

---

## PrintAirPipe duct servo valve wiring

PrintAirPipe 125mm butterfly valves use MG90S micro servos mounted in printed housings.

| Valve name | MQTT topic | Servo board GPIO | Servo position logic |
|---|---|---|---|
| SLA branch valve | `ventsys/sla/branch/control` | GPIO18 (board 2, ventsys-valve-ctrl) | Already in YAML — confirmed |
| Main duct valve 1 | `ventsys/main/valve1/control` | GPIO18 (board TBD — **own dedicated ESP32**) | FIX #24: was listed as "GPIO18 (board 2)" same as SLA branch — that is a labelling error. Each valve is on its own ESP32 per project decision. GPIO18 on a separate board is fine; the board designation and YAML are TBD. |
| Main duct valve 2 | `ventsys/main/valve2/control` | GPIO18 (board TBD — **own dedicated ESP32**) | See above |
| FDM branch valve | `ventsys/fdm/branch/control` | GPIO18 (board TBD — **own dedicated ESP32**) | |
| FDM enclosure valve | `ventsys/fdm/valve/control` | GPIO18 (board TBD — **own dedicated ESP32**) | |
| FDM 360° valve | `ventsys/fdm/360/control` | GPIO18 (board TBD — **own dedicated ESP32**) | |
| SLA enclosure valve | `ventsys/sla/valve/control` | GPIO18 (board TBD — **own dedicated ESP32**) | |
| SLA 360° valve | `ventsys/sla/360/control` | GPIO18 (board TBD — **own dedicated ESP32**) | |

> **Note:** The use of GPIO18 on multiple boards is intentional — each valve controller is a dedicated ESP32.
> GPIO18 is the natural default for the first servo on each board. If a board drives more than one valve,
> use GPIO19, GPIO20, GPIO21 for additional servos (see Board 2 pinout above).
> ESPHome YAMLs for the seven additional valve controllers are documented as needed in fix #12 of
> `configs/esphome/ventsys_sla_print_valve.yaml` is the canonical deployable SLA print-valve file.
> `ventsys_bundle_updated/ventsys_valve_controller.yaml` remains a reference template for additional board variants.

---

## Power distribution summary

| Rail | Source | Consumers |
|---|---|---|
| 5V 3A | USB power bank or wall adapter | All 4 ESP32 boards (via USB or VIN), MQ sensor heaters, servo power |
| 3.3V | ESP32 on-board regulator | DS18B20, BME280, ADC inputs |
| 12V or 240V | Separate PSU / mains | Inline duct fan (check fan voltage spec) |

> Keep ESP 3.3V logic and 5V servo/heater power separate. A noisy 5V rail from servo current spikes can cause ESP32 brownouts.

---

## Checklist before first power-on

- [ ] All ADC inputs checked for 3.3V compliance (voltage dividers fitted where needed)
- [ ] DS18B20 pull-up resistor (4.7kΩ) fitted on GPIO4
- [ ] I2C pull-ups (4.7kΩ each) on GPIO21 and GPIO22
- [ ] Servo power from 5V rail, NOT from ESP 3.3V
- [ ] Fan driver MOSFET or driver board fitted (not direct GPIO to fan)
- [ ] Common GND shared between ESP boards, sensors, and motor drivers
- [ ] BME680 SDO pin tied to GND or 3.3V to set I2C address
- [ ] ESPHome secrets.yaml filled in (wifi_ssid, mqtt credentials, api_key, ota_password)
- [ ] DS18B20 addresses noted after first flash, added to YAML
