#!/usr/bin/env python3
"""SSH forced command: replace one bounded, validated metrics snapshot."""
import json
import os
import sys
from pathlib import Path
import event_history

body = sys.stdin.buffer.read(200001)
if not body or len(body) > 200000:
    raise SystemExit("Invalid snapshot size")
data = json.loads(body)
if not isinstance(data, dict) or not {'snapshot', 'status'} <= set(data) <= {'snapshot', 'status', 'recent_notifications'} or not isinstance(data["snapshot"], dict) or not isinstance(data["status"], dict) or not isinstance(data["snapshot"].get("timestamp"), (float, int)):
    raise SystemExit("Invalid snapshot")
directory = Path("/var/lib/troubleshooting-api")
temporary = directory / "resources.json.new"
with temporary.open("w") as stream:
    os.chmod(temporary, 0o600)
    json.dump(data, stream, allow_nan=False)
    stream.flush()
    os.fsync(stream.fileno())
temporary.replace(directory / "resources.json")
try:
    event_history.record_monitor(data)
except Exception as error:
    print('History recording failed: ' + type(error).__name__, file=sys.stderr)
