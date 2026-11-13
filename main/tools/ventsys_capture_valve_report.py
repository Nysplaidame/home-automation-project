#!/usr/bin/env python3
"""Capture a MAC-verified ESPHome valve report without issuing device commands."""
import argparse
import asyncio
import json
import math
import os
from pathlib import Path
from aioesphomeapi import APIClient
from ventsys_firmware_check import validate

async def capture(host, port, expected_mac, api_key, accepted_image, wait=4):
    client = APIClient(host, port, "", noise_psk=api_key)
    values = {}
    try:
        await client.connect(login=True)
        info = await client.device_info()
        if info.mac_address.casefold() != expected_mac.casefold():
            raise ValueError("Connected board MAC does not match expected identity")
        entities, _ = await client.list_entities_services()
        names = {item.key: item.name for item in entities}
        def on_state(state): values[names.get(state.key, "")] = getattr(state, "state", None)
        client.subscribe_states(on_state)
        await asyncio.sleep(wait)
        report = {"mac": info.mac_address, "build": info.compilation_time,
                  "position": values.get("Valve Position"), "open": values.get("Valve Open Position"),
                  "closed": values.get("Valve Closed Position"),
                  "pwm_active": values.get("PWM Commanded Active"),
                  "uptime_seconds": values.get("Uptime"), "accepted_image": accepted_image}
        validate(report)
        if not isinstance(report["uptime_seconds"], (int, float)) or not math.isfinite(report["uptime_seconds"]):
            raise ValueError("Uptime is unavailable; image acceptance cannot be assessed")
        if report["uptime_seconds"] < 90:
            raise ValueError("Board uptime under 90 seconds; wait for image acceptance")
        return report
    finally:
        await client.disconnect()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host",required=True);parser.add_argument("--port",type=int,default=6053)
    parser.add_argument("--mac",required=True);parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--image-acceptance-confirmed",action="store_true",help="Confirm image acceptance independently; uptime alone is not proof")
    args=parser.parse_args()
    key=os.environ.get("VENTSYS_ESPHOME_API_KEY")
    if not key: parser.error("Set VENTSYS_ESPHOME_API_KEY privately in the process environment")
    try:
        report=asyncio.run(capture(args.host,args.port,args.mac,key,args.image_acceptance_confirmed))
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    except Exception as exc:
        print(f"INDETERMINATE: {type(exc).__name__}: {exc}");return 2
    print(f"Captured {report['mac']} at {args.output}; no commands sent.");return 0

if __name__ == "__main__": raise SystemExit(main())
