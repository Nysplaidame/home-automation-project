# _dev — Development Prototypes

Files in this directory are **development prototypes** and must **not** be flashed to any production board.

| File | Notes |
|---|---|
| entsys_airflow_sensor.yaml | Original airflow sensor prototype using the printAirPipe naming scheme. Reference only — production devices use entsys_fdm_airflow.yaml / entsys_sla_airflow.yaml / entsys_booth_airflow.yaml. |
| entsys_butterfly_valve.yaml | Original butterfly valve prototype (utterfly-valve-ctrlr-dev-1). Reference only — all production valves have their own dedicated YAMLs in the parent directory. |

Flashing either file to a production board will assign the wrong device_name, breaking HA adoption and DHCP reservations.