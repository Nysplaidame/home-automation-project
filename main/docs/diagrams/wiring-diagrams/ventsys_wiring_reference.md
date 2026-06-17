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

## Board 2 - Valve Controller (192.168.50.56)

Controls one or more MG90S servo motors driving butterfly valves.

| GPIO | Function | Notes |
|---|---|---|
| GPIO18 | Servo 1 PWM | 50Hz PWM, confirmed in YAML |
| GPIO19 | Servo 2 PWM (PLACEHOLDER) | Additional valve, add to YAML if used |
| GPIO20 | Servo 3 PWM (PLACEHOLDER) | Additional valve |
| GPIO21 | Servo 4 PWM (PLACEHOLDER) | Additional valve |
| GND | Common ground | Share with all servo GND wires |
| 5V / VIN | Servo power | Servos need 5V at up to 500mA each; use a dedicated 5V rail |

**Servo wiring (MG90S):** Brown = GND, Red = 5V power, Orange = PWM signal.

---

## Air Sensor and Sensor Array Boards (192.168.50.31-37)

The three air sensors and four sensor arrays share the same firmware base for now:

| Device | IP | YAML | MQTT topic prefix | Entity prefix |
|---|---:|---|---|---|
| FDM sensor array 1 | 192.168.50.31 | `ventsys_fdm_array_1.yaml` | `ventsys/fdm/array_1` | `ventsys_fdm_array_1` |
| FDM sensor array 2 | 192.168.50.32 | `ventsys_fdm_array_2.yaml` | `ventsys/fdm/array_2` | `ventsys_fdm_array_2` |
| SLA sensor array 1 | 192.168.50.33 | `ventsys_sla_array_1.yaml` | `ventsys/sla/array_1` | `ventsys_sla_array_1` |
| SLA sensor array 2 | 192.168.50.34 | `ventsys_sla_array_2.yaml` | `ventsys/sla/array_2` | `ventsys_sla_array_2` |
| Garage air sensor | 192.168.50.35 | `ventsys_garage_air_sensor.yaml` | `ventsys/garage/air` | `ventsys_garage_air` |
| FDM pipe air sensor | 192.168.50.36 | `ventsys_fdm_pipe_air_sensor.yaml` | `ventsys/fdm/pipe_air` | `ventsys_fdm_pipe_air` |
| SLA pipe air sensor | 192.168.50.37 | `ventsys_sla_pipe_air_sensor.yaml` | `ventsys/sla/pipe_air` | `ventsys_sla_pipe_air` |

### GPIO map

| GPIO | Function | Component | Notes |
|---|---|---|---|
| GPIO3 | ADC input | Smoke/MEMS VOC analog output `A` | ESP32-C6 ADC input, 3.3V max |
| GPIO4 | I2C SDA | BME680 SDA | ESP32-C6 strapping pin; avoid external pulls that fight boot state |
| GPIO5 | I2C SCL | BME680 SCL | ESP32-C6 strapping pin; avoid external pulls that fight boot state |
| GPIO2 | Status LED | Built-in LED | Active HIGH on most dev boards |
| 3.3V | Sensor VCC | BME680 and 3.3V smoke/MEMS module | Use 3.3V modules only |
| GND | Common ground | All sensors | Required for I2C and ADC reference |

### BME680 wiring (I2C, 3.3V)

```text
3.3V  -> VCC
GND   -> GND
GPIO4 -> SDA
GPIO5 -> SCL
SDO   -> 3.3V for I2C address 0x77
SDO   -> GND for I2C address 0x76
CS    -> 3.3V to keep the breakout in I2C mode
```

The current shared YAML default is `bme680_address: "0x77"`, matching SDO tied high. If SDO is tied to GND, set the wrapper substitution to `bme680_address: "0x76"`.

### Smoke/MEMS analog sensor wiring

```text
3.3V -> VCC
GND  -> GND
A    -> GPIO3
```

This is correct only for a 3.3V-output module. Do not connect a 5V analog output directly to GPIO3.

### Metric update cadence

| Signal | ESPHome update interval |
|---|---:|
| BME680 temperature, humidity, barometric pressure, gas resistance | 30s |
| Smoke/MEMS raw ADC value | 5s |
| Smoke detected binary sensor | raw ADC with delayed-on 3s and delayed-off 10s |
| High temperature binary sensor | BME680 temperature with delayed-on 10s |
| Online MQTT heartbeat | 60s |
| ESPHome status binary sensor | status-change driven by ESPHome |

---

## PrintAirPipe duct servo valve wiring

PrintAirPipe 125mm butterfly valves use MG90S micro servos mounted in printed housings.

| Valve name | MQTT topic | Servo board GPIO | Servo position logic |
|---|---|---|---|
| SLA branch valve | `ventsys/sla/branch/control` | GPIO18 | Dedicated ESP32 board |
| Main duct valve 1 | `ventsys/main/valve1/control` | GPIO18 | Dedicated ESP32 board |
| Main duct valve 2 | `ventsys/main/valve2/control` | GPIO18 | Dedicated ESP32 board |
| FDM branch valve | `ventsys/fdm/branch/control` | GPIO18 | Dedicated ESP32 board |
| FDM enclosure valve | `ventsys/fdm/valve/control` | GPIO18 | Dedicated ESP32 board |
| FDM 360 intake valve | `ventsys/fdm/360/control` | GPIO18 | Dedicated ESP32 board |
| SLA enclosure valve | `ventsys/sla/valve/control` | GPIO18 | Dedicated ESP32 board |
| SLA 360 intake valve | `ventsys/sla/360/control` | GPIO18 | Dedicated ESP32 board |

The use of GPIO18 on multiple valve rows is intentional because each valve controller is a separate ESP32.

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
- [ ] BME680 wired to GPIO4/GPIO5 and the YAML `bme680_address` matches SDO
- [ ] BME680 CS tied to 3.3V for I2C mode
- [ ] Smoke/MEMS `A` output connected to GPIO3 only if the module output is 3.3V-safe
- [ ] Servo power from 5V rail, not from ESP 3.3V
- [ ] Fan driver MOSFET or driver board fitted
- [ ] Common GND shared between ESP boards, sensors, and motor drivers
- [ ] ESPHome `secrets.yaml` filled in with WiFi, MQTT, API, OTA, and TLS CA values
