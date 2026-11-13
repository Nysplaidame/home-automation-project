"""Synthetic GardenKeeper recovery acceptance; never reads production config.

Run seed, take a cold database/media checkpoint, restore to another database and
directory, then run verify in a fresh process. DATABASE_URL must name a disposable
loopback PostgreSQL database whose name begins garden_rehearsal.
"""

import argparse
import asyncio
import hashlib
import json
import os
import socket
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["seed", "verify"])
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    from sqlalchemy.engine import make_url

    url = make_url(os.environ["DATABASE_URL"])
    if url.host not in {"127.0.0.1", "localhost"} or not (
        url.database or ""
    ).startswith("garden_rehearsal"):
        raise ValueError("Use a disposable loopback garden_rehearsal database.")
    source = args.source_repo.resolve()
    state = args.state_dir.resolve()
    if args.phase == "seed":
        state.mkdir(parents=True, exist_ok=False)
        if args.manifest.exists():
            raise FileExistsError(args.manifest)
    else:
        if not state.is_dir():
            raise FileNotFoundError(state)
    # Explicit environment and an empty working directory avoid vault .env files.
    os.chdir(state)
    os.environ.update(
        {
            "GARDENKEEPER_ENV": "development",
            "GARDENKEEPER_MEDIA_DIR": str(state / "media"),
            "GARDENKEEPER_LOG_DIR": str(state / "logs"),
            "GARDENKEEPER_APP_TOKEN": "",
            "GARDENKEEPER_NOTIFICATION_BROKER_TOKEN": "",
            "HOME_ASSISTANT_WEBHOOK_SECRET": "",
        }
    )
    sys.path[:0] = [str(source / "apps/api"), str(source / "apps/worker")]
    import httpx
    import uvicorn
    from fastapi.testclient import TestClient
    from gardenkeeper.core.config import get_settings
    from gardenkeeper.main import create_app

    get_settings.cache_clear()
    if args.phase == "seed":
        now = datetime.now(UTC)
        # A valid PNG, plus padding to exercise ordinary phone-photo payload size.
        import base64

        photo = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRz0AAAAASUVORK5CYII="
        ) + b"\0" * (2 * 1024 * 1024)
        with TestClient(create_app()) as client:
            uploaded = client.post(
                "/api/journal/media",
                content=photo,
                headers={"Content-Type": "image/png"},
            )
            assert uploaded.status_code == 201, uploaded.text
            photo_url = uploaded.json()["url"]
            entry = client.post(
                "/api/journal/entries",
                json={
                    "title": "Recovery rehearsal photo",
                    "entry_type": "photo_note",
                    "observed_at": now.isoformat(),
                    "body": "Synthetic recovery fixture",
                    "photo_url": photo_url,
                    "photo_alt_text": "One pixel test image",
                },
            )
            assert entry.status_code == 201, entry.text
            task = client.post(
                "/api/tasks",
                json={
                    "title": "Recovery watering",
                    "category": "watering",
                    "due_at": (now + timedelta(hours=1)).isoformat(),
                },
            )
            event = client.post(
                "/api/events",
                json={
                    "title": "Recovery event",
                    "event_type": "custom",
                    "starts_at": (now + timedelta(hours=1)).isoformat(),
                },
            )
            assert task.status_code == event.status_code == 201
            recipient = client.post(
                "/api/notifications/recipients",
                json={"name": "Recovery recipient", "ntfy_topic": "recovery-test"},
            )
            assert recipient.status_code == 201
            queued = client.post(
                "/api/notifications/publish",
                json={
                    "event_type": "garden.task.due",
                    "title": "Recovery digest",
                    "message": "Restored pending message",
                },
            )
            assert queued.status_code == 200
        # Make the synthetic queued delivery due before taking the stopped checkpoint.
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        async def make_due():
            engine = create_async_engine(url)
            try:
                async with engine.begin() as connection:
                    await connection.execute(
                        text(
                            "UPDATE notification_deliveries SET deliver_after = CURRENT_TIMESTAMP - INTERVAL '1 minute'"
                        )
                    )
            finally:
                await engine.dispose()

        asyncio.run(make_due())
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(
                {
                    "photo_url": photo_url,
                    "photo_sha256": hashlib.sha256(photo).hexdigest(),
                    "photo_size": len(photo),
                    "journal_id": entry.json()["id"],
                    "task_id": task.json()["id"],
                    "event_id": event.json()["id"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print("Seed complete; API stopped, ready for cold database/media checkpoint.")
        return

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    remote = {
        f"gardenkeeper-event-{uuid4()}.ics": b"stale",
        "personal.ics": b"preserve",
    }
    notifications = []

    class IsolatedServices(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def finish_response(self, status, body=b""):
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_PROPFIND(self):
            entries = "".join(
                f"<d:response><d:href>/calendar/{escape(name)}</d:href><d:propstat><d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response>"
                for name in remote
            )
            self.finish_response(
                207, f'<d:multistatus xmlns:d="DAV:">{entries}</d:multistatus>'.encode()
            )

        def do_PUT(self):
            remote[self.path.rsplit("/", 1)[-1]] = self.rfile.read(
                int(self.headers["Content-Length"])
            )
            self.finish_response(201)

        def do_DELETE(self):
            assert self.path.rsplit("/", 1)[-1] != "personal.ics"
            remote.pop(self.path.rsplit("/", 1)[-1], None)
            self.finish_response(204)

        def do_POST(self):
            notifications.append(
                self.rfile.read(int(self.headers["Content-Length"])).decode()
            )
            self.finish_response(200, b"{}")

    services = ThreadingHTTPServer(("127.0.0.1", 0), IsolatedServices)
    threading.Thread(target=services.serve_forever, daemon=True).start()
    integration_url = f"http://127.0.0.1:{services.server_port}"
    os.environ["NTFY_BASE_URL"] = integration_url
    get_settings.cache_clear()
    api_socket = socket.socket()
    api_socket.bind(("127.0.0.1", 0))
    api_port = api_socket.getsockname()[1]
    api_url = f"http://127.0.0.1:{api_port}"
    server = uvicorn.Server(uvicorn.Config(create_app(), log_level="error"))
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [api_socket]}, daemon=True
    )
    thread.start()
    try:
        deadline = time.monotonic() + 20
        while not server.started:
            if time.monotonic() >= deadline or not thread.is_alive():
                raise RuntimeError("Isolated API startup failed.")
            time.sleep(0.05)
        with httpx.Client(base_url=api_url) as client:
            assert client.get("/ready").status_code == 200
            entry = client.get(f"/api/journal/entries/{manifest['journal_id']}")
            assert (
                entry.status_code == 200
                and entry.json()["photo_url"] == manifest["photo_url"]
            )
            photo = client.get(manifest["photo_url"])
            assert photo.status_code == 200
            assert len(photo.content) == manifest["photo_size"]
            assert hashlib.sha256(photo.content).hexdigest() == manifest["photo_sha256"]
            assert (
                client.post("/api/notifications/dispatch-due").json()[
                    "delivered_recipients"
                ]
                == 1
            )
            assert notifications == ["• Recovery digest: Restored pending message"]
            assert (
                client.post("/api/notifications/dispatch-due").json()[
                    "delivered_recipients"
                ]
                == 0
            )
            from dataclasses import replace

            import gardenkeeper_worker as worker

            settings = replace(
                worker.load_settings(),
                api_url=api_url,
                api_token=None,
                nextcloud_caldav_url=integration_url + "/calendar/",
                nextcloud_user="synthetic",
                nextcloud_app_password="synthetic",
            )
            first = asyncio.run(worker.run_nextcloud_projection(settings, {}, {}))
            assert first == 3  # Two restored objects and one stale owned removal.
            assert (
                b"BEGIN:VTODO" in remote[f"gardenkeeper-task-{manifest['task_id']}.ics"]
            )
            assert (
                b"BEGIN:VEVENT"
                in remote[f"gardenkeeper-event-{manifest['event_id']}.ics"]
            )
            assert (
                client.patch(
                    f"/api/events/{manifest['event_id']}", json={"status": "cancelled"}
                ).status_code
                == 200
            )
            asyncio.run(worker.run_nextcloud_projection(settings, {}, {}))
            assert f"gardenkeeper-event-{manifest['event_id']}.ics" not in remote
            assert remote["personal.ics"] == b"preserve"
        result = {
            "status": "passed",
            "database": "restored PostgreSQL",
            "photo_bytes": manifest["photo_size"],
            "photo_hash": "matched",
            "journal_link": "matched",
            "queued_notification": "delivered once",
            "calendar_restart": "owned stale entries removed; unrelated entry preserved",
            "limits": "Synthetic data and isolated service doubles; no production checkpoint or real Nextcloud/ntfy acceptance.",
        }
        (state / "acceptance.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        print(json.dumps(result))
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        services.shutdown()
        services.server_close()


if __name__ == "__main__":
    main()
