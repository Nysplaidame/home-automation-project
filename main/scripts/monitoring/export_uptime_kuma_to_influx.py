#!/usr/bin/env python3
"""Export latest Uptime Kuma monitor state to InfluxDB line protocol.

This intentionally exports a small current-state snapshot once per run instead
of trying to replace Uptime Kuma's own history. Grafana can then show status,
latency, and short-term trends without requiring a SQLite datasource plugin.
"""

from __future__ import annotations

import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request


DB_PATH = os.environ.get("KUMA_DB_PATH", "/opt/monitoring/uptime-kuma/kuma.db")
INFLUX_URL = os.environ.get("INFLUX_URL", "http://127.0.0.1:8086")
INFLUX_ORG = os.environ.get("INFLUX_ORG", "homelab")
INFLUX_BUCKET = os.environ.get("INFLUX_BUCKET", "uptimekuma")
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]


def lp_escape_tag(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")


def lp_escape_string(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def main() -> int:
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        select
            m.id,
            m.name,
            m.type,
            m.active,
            coalesce(m.hostname, '') as hostname,
            coalesce(m.port, '') as port,
            coalesce(m.url, '') as url,
            h.status,
            h.time as heartbeat_time,
            coalesce(h.msg, '') as msg,
            coalesce(h.ping, 0) as ping
        from monitor m
        left join heartbeat h on h.id = (
            select id
            from heartbeat
            where monitor_id = m.id
            order by time desc
            limit 1
        )
        where m.active = 1
        order by m.name
        """
    ).fetchall()

    now = int(time.time())
    lines: list[str] = []
    for row in rows:
        status = int(row["status"] or 0)
        ping = int(row["ping"] or 0)
        is_up = 1 if status == 1 else 0
        target = row["url"] or f"{row['hostname']}:{row['port']}"
        tags = ",".join(
            [
                f"monitor={lp_escape_tag(row['name'])}",
                f"type={lp_escape_tag(row['type'])}",
                f"target={lp_escape_tag(target)}",
            ]
        )
        fields = ",".join(
            [
                f"status={status}i",
                f"up={is_up}i",
                f"ping_ms={ping}i",
                f"message=\"{lp_escape_string(row['msg'])}\"",
                f"heartbeat_time=\"{lp_escape_string(row['heartbeat_time'] or '')}\"",
            ]
        )
        lines.append(f"uptime_kuma_monitor,{tags} {fields} {now}")

    if not lines:
        return 0

    query = urllib.parse.urlencode(
        {"org": INFLUX_ORG, "bucket": INFLUX_BUCKET, "precision": "s"}
    )
    request = urllib.request.Request(
        f"{INFLUX_URL.rstrip('/')}/api/v2/write?{query}",
        data=("\n".join(lines) + "\n").encode("utf-8"),
        headers={"Authorization": f"Token {INFLUX_TOKEN}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status not in (200, 204):
                raise RuntimeError(f"unexpected InfluxDB HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"InfluxDB write failed: HTTP {exc.code}: {body}") from exc

    print(f"exported {len(lines)} active Uptime Kuma monitors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
