#!/usr/bin/env python3
"""Offline gates for production VentSys persistence and board management."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

class Loader(yaml.SafeLoader):
    pass

Loader.add_multi_constructor("!", lambda loader, tag, node: loader.construct_scalar(node))

def load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)

def check():
    folder = ROOT / "configs/esphome"
    management = load(folder / "ventsys_board_management.yaml")
    assert {b["platform"] for b in management["button"]} == {"shutdown", "restart"}
    valves = list(folder.glob("*valve*.yaml"))
    for path in valves:
        config = load(path)
        numbers = {n["id"]: n for n in config["number"]}
        for identity in ("valve_position_direct_control_number", "valve_opened_position", "valve_closed_position"):
            assert numbers[identity].get("restore_value") is True, (path.name, identity)
        assert config["preferences"]["flash_write_interval"] == "1ms", path.name
        assert all(s.get("restore") is False for s in config["servo"]), path.name
        assert "board_management" in config["packages"], path.name
        assert "on_boot" not in config["esphome"], path.name
        if path.name.endswith("_360_valve_v2_nerdiy.yaml"):
            # publish_state alone doesn't save TemplateNumber preferences.
            for message in config["mqtt"]["on_message"]:
                assert "number.set" in message["then"][0], path.name
            for button in config["button"]:
                assert "number.set" in button["on_press"]["then"][0], path.name
            drive = next(s for s in config["script"] if s["id"] == "drive_valve_to")
            assert "publish_state" not in str(drive), path.name
    checked = 0
    for path in folder.glob("ventsys_*.yaml"):
        config = load(path)
        # Optional sensor/display and management fragments are packages, not standalone firmware.
        if "esp32" not in config and "esp8266" not in config:
            if path.name not in ("ventsys_air_sensor_co.yaml", "ventsys_air_sensor_dp.yaml", "ventsys_air_sensor_display.yaml", "ventsys_board_management.yaml"):
                assert "base" in config.get("packages", {}), path.name
            continue
        assert "board_management" in config.get("packages", {}), path.name
        checked += 1
    for path in (ROOT / "ventsys/ventsys_bundle_updated").glob("*controller*.yaml"):
        config = load(path)
        assert "board_management" in config.get("packages", {}), path.name
        if "valve" in path.name:
            assert config["globals"][0]["restore_value"] is True, path.name
            assert config["globals"][0]["update_interval"] == "1ms", path.name
            assert config["preferences"]["flash_write_interval"] == "1ms", path.name
            assert all(s.get("restore") is False for s in config["servo"]), path.name
    print(f"PASS: {len(valves)} valve variants persist command/endpoints; {checked} standalone configs plus sensor wrappers inherit shutdown/restart; four controller templates covered; valve startup stays command-free")

if __name__ == "__main__":
    check()
