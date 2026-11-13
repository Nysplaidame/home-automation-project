#!/usr/bin/env python3
"""Forced SSH command on Proxmox: export metrics, never monitor credentials."""
import json
import subprocess
from pathlib import Path

status = json.loads(subprocess.check_output(["/usr/bin/python3", "/usr/local/sbin/resource-pressure-monitor.py", "--status"], timeout=5))
snapshot = json.loads(Path("/var/lib/resource-pressure-monitor/latest.json").read_text())
fields = ("timestamp", "samples", "expected", "errors", "inventory_valid", "load", "cpus", "blocked", "thin_pct", "thin_metadata_pct", "boot_id")
selected = {key: snapshot.get(key) for key in fields}
selected["inventory"] = [{key: row.get(key) for key in ("vmid", "name", "type", "status", "cpu", "maxcpu", "maxmem")} for row in snapshot.get("inventory", [])]
state = json.loads(Path('/var/lib/resource-pressure-monitor/state.json').read_text())
accepted = {key: value['last_sent'] for key, value in state.get('checks', {}).items() if value.get('last_sent')}
if status.get('collector_health', {}).get('last_sent'):
    accepted['collector-health'] = status['collector_health']['last_sent']
print(json.dumps({"snapshot": selected, "status": status, 'recent_notifications': accepted}))
