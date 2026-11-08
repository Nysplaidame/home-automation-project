# _dev — Development Prototypes

Files in this directory are development prototypes. Flash only a configuration
whose documented identity and hardware match the target board.

`ventsys_servo_pulse_calibration.yaml` records the historical feedback-servo
calibration image from before the E2/MAIN-2 board reassignment. Its embedded
MAIN-2 name with `.52` now conflicts with E2 and must not be flashed as-is.
The active MAIN-2 board uses a normal three-wire servo at `.57`; this older
image also expects a connected GPIO35 feedback network. Change the identity,
static IP, and hardware assumptions before adapting a copy for any board.
Never run two boards with the same identity. The horn must be
disconnected, the power wiring checked, and an operator ready at the board
before pressing Apply Pulse. The number state alone does not centre the servo.

For Valve 2, select 1500 µs and press Apply Pulse while watching a marked horn
or shaft. After release, record the direction, final mark, sound, Last Feedback
Mean and Last Feedback Range. Then apply 1450, 1500, 1550, 1500, 1450 µs,
one observed command at a time, and repeat that sequence twice. Stop if a
direction reversal, sticking, or persistent buzzing occurs. The provisional
acceptance target is feedback repeatability within 0.010 V at each pulse and
between-pulse separation greater than three times within-pulse variation.
Use Stop Release immediately if the motion is wrong. Do not attach the linkage
or expand the pulse window until this unloaded check passes.

`ventsys_servo_range_mapping.yaml` is the next unloaded mapping stage after
that check. The first Apply after every boot or Stop Release must be 1500 µs;
later Apply requests are rejected if they jump more than 100 µs from the last
completed pulse. Use at most 100 µs steps near the tested centre and smaller
steps toward the outer travel. Its 500–2500 µs selectable range is an
exploration envelope, **not** a claim that these endpoints are safe for this
servo. Observe every move, stop at a feedback plateau, binding, or lasting
buzz, and never use a hard stop as the calibration endpoint. Record pulse and
feedback for every accepted step. The goal is a repeatable usable unloaded
range; shaft angle cannot be inferred from voltage without an angle reference.

`ventsys_servo_sweep_1850_to_700.yaml` is a one-use unloaded experiment for
Valve 2. It boots with PWM detached. Apply 1500 µs first, then approach
1850 µs in steps of no more than 100 µs while checking each completed pulse
and its post-release feedback. The separate **Sweep 1850 To 700 Once** button
accepts one direct movement only from a completed, settled 1850 µs command.
A post-release shift over 0.020 V latches a fault and blocks further commands;
the sweep button also locks after use. The 1850 and 700 µs values are test
targets, not certified servo or valve endpoints. The servo is still powered
through the ESP32 board's 5 V pin, and earlier 650 and 1900 µs pulses showed
unexpected jumps after PWM release. Keep the linkage off and watch each move.

| File | Notes |
|---|---|
| entsys_airflow_sensor.yaml | Original airflow sensor prototype using the printAirPipe naming scheme. Reference only — production devices use entsys_fdm_airflow.yaml / entsys_sla_airflow.yaml / entsys_booth_airflow.yaml. |
| entsys_butterfly_valve.yaml | Original butterfly valve prototype (utterfly-valve-ctrlr-dev-1). Reference only — all production valves have their own dedicated YAMLs in the parent directory. |

Flashing either file to a production board will assign the wrong device_name, breaking HA adoption and DHCP reservations.
