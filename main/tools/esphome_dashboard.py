#!/usr/bin/env python3
"""Run ESPHome Device Builder actions on the Home Assistant add-on from this desktop (needs `websockets`).

The add-on's dashboard is only reachable through Home Assistant's ingress, so this opens an ingress session
with an admin token (supervisor websocket) and then speaks the dashboard's own websocket protocol (`/ws`,
JSON commands such as `devices/validate`, `firmware/compile`, `firmware/install`), which is what the buttons
in its web UI do. Written against Device Builder 2026.10.2; re-check the protocol if the add-on is upgraded.

  python esphome_dashboard.py --token-file F validate home-assistant-voice-0ae52a.yaml
  python esphome_dashboard.py --token-file F compile  home-assistant-voice-0ae52a.yaml
  python esphome_dashboard.py --token-file F upload   home-assistant-voice-0ae52a.yaml --device 192.168.50.108

`upload` flashes the firmware from the last successful `compile` over the air, then the device reboots (in
this Device Builder version `install` only builds). `--device` is the address to flash (the dashboard finds
devices by mDNS, which does not cross VLANs). The token is read from the file and never printed. Output
streams as it arrives; the exit status is 0 only when the job reports success.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import ssl
import sys

import websockets

HA = "192.168.20.101:8123"
ADDON = "5c53de3b_esphome"
ANSI = re.compile(r"(?:\x1b|\\033)\[[0-9;]*m")  # the dashboard sends the escape as literal text


def ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


async def ingress(token: str) -> tuple[str, str]:
    """Return (ingress entry path, ingress session cookie value)."""
    async with websockets.connect(f"wss://{HA}/api/websocket", ssl=ssl_ctx(), max_size=2**24) as ws:
        await ws.recv()
        await ws.send(json.dumps({"type": "auth", "access_token": token}))
        if json.loads(await ws.recv())["type"] != "auth_ok":
            raise SystemExit("auth failed")

        async def api(msg_id: int, endpoint: str, method: str) -> dict:
            await ws.send(json.dumps({"id": msg_id, "type": "supervisor/api", "endpoint": endpoint, "method": method}))
            while True:
                reply = json.loads(await ws.recv())
                if reply.get("id") == msg_id:
                    if not reply.get("success"):
                        raise SystemExit(f"supervisor api {endpoint} failed: {reply.get('error')}")
                    return reply["result"]

        info = await api(1, f"/addons/{ADDON}/info", "get")
        if info.get("state") != "started":
            raise SystemExit(f"ESPHome add-on is {info.get('state')}, start it first")
        session = await api(2, "/ingress/session", "post")
        return info["ingress_entry"], session["session"]


class Dashboard:
    """Minimal client for the Device Builder websocket protocol."""

    def __init__(self, ws: websockets.ClientConnection) -> None:
        self.ws = ws
        self.next_id = 0

    def _send(self, command: str, args: dict | None) -> str:
        self.next_id += 1
        message_id = str(self.next_id)  # the server only matches string ids
        asyncio.get_running_loop().create_task(
            self.ws.send(json.dumps({"command": command, "message_id": message_id, "args": args or {}}))
        )
        return message_id

    async def command(self, command: str, args: dict | None = None):
        """One request, one result."""
        mid = self._send(command, args)
        async for raw in self.ws:
            msg = json.loads(raw)
            if msg.get("message_id") != mid:
                continue
            if "error_code" in msg:
                raise SystemExit(f"{command} failed: {msg['error_code']} {msg.get('details')}")
            return msg.get("result")
        raise SystemExit(f"{command}: connection closed")

    async def stream(self, command: str, args: dict | None = None):
        """A streaming request: prints output events; returns the final result payload."""
        mid = self._send(command, args)
        async for raw in self.ws:
            msg = json.loads(raw)
            if msg.get("message_id") != mid:
                continue
            if "error_code" in msg:
                raise SystemExit(f"{command} failed: {msg['error_code']} {msg.get('details')}")
            if msg.get("event") == "output":
                data = msg.get("data")
                print(ANSI.sub("", data if isinstance(data, str) else json.dumps(data)).rstrip(), flush=True)
            elif msg.get("event") == "result":
                return msg.get("data")
        raise SystemExit(f"{command}: connection closed before a result")


def job_id_of(result) -> str:
    if isinstance(result, dict):
        for key in ("job_id", "id"):
            if result.get(key):
                return str(result[key])
        if isinstance(result.get("job"), dict):
            return job_id_of(result["job"])
    raise SystemExit(f"could not find a job id in {result!r}")


async def run(token: str, action: str, configuration: str, device: str | None) -> int:
    entry, session = await ingress(token)
    async with websockets.connect(f"wss://{HA}{entry}/ws", ssl=ssl_ctx(), max_size=None,
                                  additional_headers={"Cookie": f"ingress_session={session}"}) as ws:
        hello = json.loads(await ws.recv())
        if "server_version" not in hello:
            raise SystemExit(f"unexpected first message: {str(hello)[:200]}")
        print(f"[dashboard {hello.get('server_version')}, requires_auth={hello.get('requires_auth')}]", flush=True)
        if hello.get("requires_auth"):
            raise SystemExit("the dashboard asks for its own login; ingress was expected to bypass it")
        dash = Dashboard(ws)
        if action == "validate":
            result = await dash.stream("devices/validate", {"configuration": configuration})
            print(f"[result] {json.dumps(result)[:400]}")
            return 0 if (result or {}).get("success", (result or {}).get("valid", True)) else 1
        if action == "compile":
            started = await dash.command("firmware/compile", {"configuration": configuration})
        elif action == "upload":
            # Flash the firmware built by the last compile, over the air; the device reboots.
            started = await dash.command(
                "firmware/upload", {"configuration": configuration, "port": device or "OTA"}
            )
        else:
            started = await dash.command(
                "firmware/install",
                {"configuration": configuration, "port": device or "OTA", "force_local": False, "bootloader": False},
            )
        print(f"[started] {json.dumps(started)[:300]}", flush=True)
        final = await dash.stream("firmware/follow_job", {"job_id": job_id_of(started)})
        print(f"[job result] {json.dumps(final)[:600]}")
        ok = isinstance(final, dict) and (
            final.get("success") is True or final.get("exit_code") == 0 or final.get("state") in ("completed", "success"))
        return 0 if ok else 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token-file", required=True)
    ap.add_argument("action", choices=["validate", "compile", "install", "upload"])
    ap.add_argument("configuration", help="YAML file name inside /config/esphome")
    ap.add_argument("--device", help="address to flash (install only), e.g. 192.168.50.108")
    a = ap.parse_args()
    # Build output contains non-ASCII characters; a Windows console encoding must not kill the stream.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    token = open(a.token_file, encoding="utf-8").read().strip()
    sys.exit(asyncio.run(run(token, a.action, a.configuration, a.device)))


if __name__ == "__main__":
    main()
