from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware

from .helper_client import HelperClient, HelperError
from .models import JobMode, JobStatus, Portal, RsyncOptions
from .portals import PortalConfigError, find_portal, load_portals, remove_portal, upsert_portal
from .rsync import RsyncOptionError, build_rsync_command
from .settings import AppConfig, load_config
from .store import JobStore


CONFIG_PATH = Path(os.environ.get("TRANSFERPORTAL_CONFIG", "/etc/transferportal/config.yaml"))


def create_app() -> FastAPI:
    config = load_config(CONFIG_PATH)
    app = FastAPI(title="Transfer Portal")
    app.state.config = config
    app.state.store = JobStore(config.database_path)
    app.state.helper = HelperClient(config.helper_path)
    app.add_middleware(SessionMiddleware, secret_key=_session_secret(config))

    @app.exception_handler(HTTPException)
    async def html_http_error(request: Request, exc: HTTPException) -> Response:
        location = exc.headers.get("Location") if exc.headers else None
        if location and exc.status_code in {302, 303, 307, 308}:
            return RedirectResponse(location, status_code=exc.status_code)
        detail = str(exc.detail or "The request could not be completed.")
        if _wants_html(request):
            return page("Request Error", nav("portals") + error_panel(detail), status_code=exc.status_code)
        return JSONResponse({"detail": detail}, status_code=exc.status_code)

    @app.exception_handler(PortalConfigError)
    async def html_portal_error(request: Request, exc: PortalConfigError) -> HTMLResponse:
        return page("Request Error", nav("portals") + error_panel(str(exc)), status_code=404)

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        require_auth(request)
        refresh_jobs(app, "system")
        portals = load_portals(CONFIG_PATH)
        jobs = app.state.store.list_jobs()
        return page(
            "Portals",
            nav("portals")
            + f"""
            <section class="toolbar"><a class="button primary" href="/portals/new">New portal</a></section>
            <section class="grid">{''.join(portal_card(portal) for portal in portals) or empty('No portals configured yet.')}</section>
            <h2>Recent Jobs</h2>
            {jobs_table(jobs)}
            """,
        )

    @app.get("/login", response_class=HTMLResponse)
    def login_form() -> HTMLResponse:
        return login_page()

    @app.post("/login")
    def login(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]) -> Response:
        if not verify_login(username, password):
            return login_page("Username or password was not recognised.", username=username, status_code=401)
        request.session["user"] = username
        return RedirectResponse("/", status_code=303)

    @app.post("/logout")
    def logout(request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    @app.get("/portals", response_class=HTMLResponse)
    def portals(request: Request) -> HTMLResponse:
        require_auth(request)
        return RedirectResponse("/", status_code=303)

    @app.get("/portals/new", response_class=HTMLResponse)
    def new_portal(request: Request) -> HTMLResponse:
        require_auth(request)
        return page("New Portal", nav("portals") + portal_form())

    @app.get("/api/browse")
    def browse(request: Request, path: str | None = None) -> JSONResponse:
        require_auth(request)
        try:
            response = app.state.helper.request(
                "browse-path",
                {"path": path or "", "config_path": str(CONFIG_PATH)},
            )
        except HelperError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return JSONResponse(response["response"])

    @app.post("/portals")
    def create_portal(
        request: Request,
        slug: Annotated[str, Form()],
        display_name: Annotated[str, Form()],
        source_path: Annotated[str, Form()],
        destination_path: Annotated[str, Form()],
        allow_source_delete: Annotated[bool, Form()] = False,
        allow_destination_delete: Annotated[bool, Form()] = False,
    ) -> RedirectResponse:
        actor = require_auth(request)
        portal = Portal(
            slug=slug,
            display_name=display_name,
            source_path=Path(source_path),
            destination_path=Path(destination_path),
            allow_source_delete=allow_source_delete,
            allow_destination_delete=allow_destination_delete,
        )
        try:
            app.state.helper.request(
                "create-portal",
                {
                    "slug": portal.slug,
                    "source_path": str(portal.source_path),
                    "destination_path": str(portal.destination_path),
                    "config_path": str(CONFIG_PATH),
                },
            )
            upsert_portal(portal, CONFIG_PATH)
            app.state.store.record_audit(actor, "portal.create", portal.slug, detail={"portal": portal.slug})
        except (HelperError, PortalConfigError, OSError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return RedirectResponse(f"/portals/{portal.slug}", status_code=303)

    @app.get("/portals/{slug}", response_class=HTMLResponse)
    def portal_detail(request: Request, slug: str) -> HTMLResponse:
        require_auth(request)
        portal = find_portal(load_portals(CONFIG_PATH), slug)
        return page(
            portal.display_name,
            nav("portals")
            + f"""
            <section class="panel">
              <h1>{esc(portal.display_name)}</h1>
              <dl>
                <dt>Real source folder</dt><dd>{esc(display_path(portal.source_path))}</dd>
                <dt>Portal source mount</dt><dd>{esc(str(portal.source_mount))}</dd>
                <dt>Real destination folder</dt><dd>{esc(display_path(portal.destination_path))}</dd>
                <dt>Portal destination mount</dt><dd>{esc(str(portal.destination_mount))}</dd>
                <dt>Source delete</dt><dd>{yes_no(portal.allow_source_delete)}</dd>
                <dt>Destination delete</dt><dd>{yes_no(portal.allow_destination_delete)}</dd>
              </dl>
              <div class="actions">
                <a class="button primary" href="/transfer-builder?portal={esc(portal.slug)}">Build transfer</a>
              </div>
              <form class="danger-zone" method="post" action="/portals/{esc(portal.slug)}/delete">
                <h2>Delete Portal</h2>
                <p class="help">Deletes this portal's bind-mount units and removes it from the app. It does not delete source or destination files.</p>
                <label>Type the portal slug to confirm
                  <input name="confirm_slug" placeholder="{esc(portal.slug)}" required>
                </label>
                <button class="danger" type="submit">Delete portal</button>
              </form>
            </section>
            """,
        )

    @app.post("/portals/{slug}/delete")
    def delete_portal(request: Request, slug: str, confirm_slug: Annotated[str, Form()]) -> RedirectResponse:
        actor = require_auth(request)
        refresh_jobs(app, actor)
        portal = find_portal(load_portals(CONFIG_PATH), slug)
        if confirm_slug != portal.slug:
            raise HTTPException(status_code=400, detail="confirmation did not match the portal slug")
        if app.state.store.active_count_for_portal(portal.slug):
            raise HTTPException(status_code=409, detail="portal has an active transfer job")
        try:
            response = app.state.helper.request(
                "remove-portal",
                {"slug": portal.slug, "config_path": str(CONFIG_PATH)},
            )
            remove_portal(portal.slug, CONFIG_PATH)
            app.state.store.record_audit(
                actor,
                "portal.delete",
                portal.slug,
                detail={"portal": portal.slug, "cleanup": response.get("response", {})},
            )
        except (HelperError, PortalConfigError, OSError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return RedirectResponse("/", status_code=303)

    @app.get("/transfer-builder", response_class=HTMLResponse)
    def transfer_builder(request: Request, portal: str | None = None) -> HTMLResponse:
        require_auth(request)
        portals = load_portals(CONFIG_PATH)
        selected = portal or (portals[0].slug if portals else "")
        return page("Transfer Builder", nav("builder") + transfer_form(portals, selected))

    @app.post("/jobs/dry-run")
    def dry_run(request: Request, payload: Annotated[dict[str, Any], Depends(job_form)]) -> RedirectResponse:
        return submit_job(app, request, JobMode.DRY_RUN, payload)

    @app.post("/jobs/copy")
    def copy(request: Request, payload: Annotated[dict[str, Any], Depends(job_form)]) -> RedirectResponse:
        return submit_job(app, request, JobMode.COPY, payload)

    @app.post("/jobs/move")
    def move(request: Request, payload: Annotated[dict[str, Any], Depends(job_form)]) -> RedirectResponse:
        if payload.get("confirm_move") != "confirm":
            raise HTTPException(status_code=400, detail="move mode requires confirmation")
        return submit_job(app, request, JobMode.MOVE_AFTER_VERIFIED_COPY, payload)

    @app.get("/jobs", response_class=HTMLResponse)
    def jobs(request: Request) -> HTMLResponse:
        actor = require_auth(request)
        refresh_jobs(app, actor)
        return page("Jobs", nav("jobs") + jobs_table(app.state.store.list_jobs()))

    @app.get("/jobs/{job_id}", response_class=HTMLResponse)
    def job_detail(request: Request, job_id: int) -> HTMLResponse:
        actor = require_auth(request)
        refresh_jobs(app, actor)
        job = app.state.store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404)
        command = json_list(job["command_json"])
        return page(
            f"Job {job_id}",
            nav("jobs")
            + f"""
            <section class="panel">
              <h1>Job {job_id}</h1>
              {job_portal_mapping(job)}
              <dl>
                <dt>Portal</dt><dd>{esc(job['portal_slug'])}</dd>
                <dt>Mode</dt><dd>{esc(job['mode'])}</dd>
                <dt>Status</dt><dd>{esc(job['status'])}</dd>
                <dt>Phase</dt><dd>{esc(job['current_phase'])}</dd>
                <dt>Exit code</dt><dd>{esc(str(job['exit_code'] if job['exit_code'] is not None else ''))}</dd>
                <dt>Log</dt><dd>{esc(str(job['log_path'] or ''))}</dd>
                <dt>Status file</dt><dd>{esc(str(job['status_path'] or ''))}</dd>
                <dt>Runner PID</dt><dd>{esc(str(job['pid'] or ''))}</dd>
              </dl>
              <h2>Command</h2>
              <pre>{esc(repr(command))}</pre>
              <form method="post" action="/jobs/{job_id}/stop"><button class="danger" type="submit">Stop</button></form>
              <form method="post" action="/jobs/{job_id}/retry"><button type="submit">Retry</button></form>
            </section>
            """,
        )

    @app.post("/jobs/refresh")
    def refresh(request: Request) -> RedirectResponse:
        actor = require_auth(request)
        refresh_jobs(app, actor)
        return RedirectResponse("/jobs", status_code=303)

    @app.post("/jobs/{job_id}/stop")
    def stop_job(request: Request, job_id: int) -> RedirectResponse:
        actor = require_auth(request)
        job = app.state.store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404)
        if not job["pid"]:
            raise HTTPException(status_code=409, detail="job has no tracked process id")
        try:
            app.state.helper.request("stop-job", {"pid": int(job["pid"])})
            app.state.store.mark_interrupted(job_id)
            app.state.store.record_audit(actor, "job.stop", job["portal_slug"], job_id, {"pid": int(job["pid"])})
        except HelperError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return RedirectResponse(f"/jobs/{job_id}", status_code=303)

    @app.post("/jobs/{job_id}/retry")
    def retry_job(request: Request, job_id: int) -> RedirectResponse:
        actor = require_auth(request)
        config: AppConfig = app.state.config
        job = app.state.store.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404)
        if app.state.store.active_count() >= config.max_active_jobs:
            raise HTTPException(status_code=409, detail="another transfer job is active")
        command = tuple(json_list(job["command_json"]))
        status_path = config.log_dir / f"job-{job_id}-retry-{uuid.uuid4().hex}.status.json"
        new_id = app.state.store.create_job(
            job["portal_slug"],
            job["mode"],
            JobStatus.QUEUED.value,
            {},
            command,
            "queued",
            Path(job["log_path"]) if job["log_path"] else None,
            status_path,
        )
        app.state.store.record_audit(actor, "job.retry", job["portal_slug"], new_id, {"source_job_id": job_id})
        launch_job(
            app,
            actor,
            new_id,
            job["portal_slug"],
            command,
            Path(job["log_path"]) if job["log_path"] else config.log_dir / f"job-{new_id}.log",
            status_path,
        )
        return RedirectResponse(f"/jobs/{new_id}", status_code=303)

    @app.get("/settings", response_class=HTMLResponse)
    def settings(request: Request) -> HTMLResponse:
        require_auth(request)
        config = app.state.config
        portals = load_portals(CONFIG_PATH)
        jobs = app.state.store.list_jobs()
        active_jobs = app.state.store.active_count()
        return page("Settings", nav("settings") + settings_view(config, portals, len(jobs), active_jobs))

    return app


def submit_job(app: FastAPI, request: Request, mode: JobMode, payload: dict[str, Any]) -> RedirectResponse:
    actor = require_auth(request)
    config: AppConfig = app.state.config
    preview_only = payload.get("preview_only") == "on"
    if not preview_only and app.state.store.active_count() >= config.max_active_jobs:
        raise HTTPException(status_code=409, detail="another transfer job is active")
    portal = find_portal(load_portals(CONFIG_PATH), str(payload["portal_slug"]))
    if not portal.enabled:
        raise HTTPException(status_code=400, detail="portal is disabled")
    options = options_from_payload(payload)
    try:
        command = build_rsync_command(portal, options, mode)
    except RsyncOptionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    log_path = config.log_dir / f"job-{portal.slug}-{mode.value}.log"
    status_path = config.log_dir / f"job-{portal.slug}-{mode.value}.status.json"
    job_id = app.state.store.create_job(
        portal.slug,
        mode.value,
        JobStatus.COMPLETED.value if preview_only else JobStatus.QUEUED.value,
        asdict(options),
        command,
        "preview" if preview_only else "queued",
        log_path,
        status_path,
    )
    app.state.store.record_audit(
        actor,
        "job.create",
        portal.slug,
        job_id,
        {"mode": mode.value, "command": list(command)},
    )
    if preview_only:
        return RedirectResponse(f"/jobs/{job_id}", status_code=303)
    launch_job(app, actor, job_id, portal.slug, command, log_path, status_path)
    return RedirectResponse(f"/jobs/{job_id}", status_code=303)


def launch_job(
    app: FastAPI,
    actor: str,
    job_id: int,
    portal_slug: str,
    command: tuple[str, ...],
    log_path: Path,
    status_path: Path,
) -> None:
    try:
        response = app.state.helper.request(
            "run-rsync",
            {
                "command": list(command),
                "log_path": str(log_path),
                "status_path": str(status_path),
                "config_path": str(CONFIG_PATH),
            },
        )
        pid = int(response["response"]["pid"])
        app.state.store.mark_launched(job_id, pid)
        app.state.store.record_audit(actor, "job.launch", portal_slug, job_id, {"pid": pid})
    except HelperError as exc:
        app.state.store.mark_failed(job_id, str(exc))
        app.state.store.record_audit(actor, "job.launch_failed", portal_slug, job_id, {"error": str(exc)})
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def refresh_jobs(app: FastAPI, actor: str) -> None:
    for job in app.state.store.list_active_jobs():
        if not job["pid"] or not job["status_path"]:
            continue
        try:
            response = app.state.helper.request(
                "job-status",
                {"pid": int(job["pid"]), "status_path": str(job["status_path"])},
            )["response"]
        except HelperError as exc:
            app.state.store.record_audit(actor, "job.status_failed", job["portal_slug"], int(job["id"]), {"error": str(exc)})
            continue
        if response.get("running"):
            continue
        state = str(response.get("state") or "failed")
        exit_code = int(response.get("exit_code", 1))
        if state == "completed" and exit_code == 0:
            app.state.store.mark_completed(int(job["id"]), exit_code)
            app.state.store.record_audit(actor, "job.completed", job["portal_slug"], int(job["id"]), {"exit_code": exit_code})
        elif state == "interrupted" or exit_code < 0:
            app.state.store.mark_interrupted(int(job["id"]), exit_code)
            app.state.store.record_audit(actor, "job.interrupted", job["portal_slug"], int(job["id"]), {"exit_code": exit_code})
        else:
            app.state.store.mark_failed(int(job["id"]), f"rsync exited {exit_code}", exit_code)
            app.state.store.record_audit(actor, "job.failed", job["portal_slug"], int(job["id"]), {"exit_code": exit_code})


async def job_form(request: Request) -> dict[str, Any]:
    form = await request.form()
    return dict(form)


def options_from_payload(payload: dict[str, Any]) -> RsyncOptions:
    advanced_flags = tuple(str(payload[key]) for key in sorted(payload) if key.startswith("advanced_flag_") and payload[key])
    return RsyncOptions(
        skip_existing=payload.get("skip_existing") == "on",
        update_newer_only=payload.get("update_newer_only") == "on",
        checksum_compare=payload.get("checksum_compare") == "on",
        size_only_compare=payload.get("size_only_compare") == "on",
        delete_destination_extras=payload.get("delete_destination_extras") == "on",
        preserve_acls=payload.get("preserve_acls") == "on",
        preserve_xattrs=payload.get("preserve_xattrs") == "on",
        preserve_owner_group=payload.get("preserve_owner_group") == "on",
        preserve_permissions=payload.get("preserve_permissions") == "on",
        preserve_hard_links=payload.get("preserve_hard_links") == "on",
        advanced_flags=advanced_flags,
    )


def verify_login(username: str, password: str) -> bool:
    expected_user = os.environ.get("TRANSFERPORTAL_ADMIN_USER", "admin")
    expected_hash = os.environ.get("TRANSFERPORTAL_ADMIN_PASSWORD_SHA256")
    expected_password = os.environ.get("TRANSFERPORTAL_ADMIN_PASSWORD")
    if username != expected_user:
        return False
    if expected_hash:
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(digest, expected_hash)
    if expected_password:
        return hmac.compare_digest(password, expected_password)
    return False


def require_auth(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return str(user)


def _session_secret(config: AppConfig) -> str:
    if config.session_secret_file.exists():
        return config.session_secret_file.read_text(encoding="utf-8").strip()
    return os.environ.get("TRANSFERPORTAL_SESSION_SECRET", "dev-only-change-me")


def nav(active: str) -> str:
    items = [
        ("portals", "/", "Portals"),
        ("builder", "/transfer-builder", "Builder"),
        ("jobs", "/jobs", "Jobs"),
        ("settings", "/settings", "Settings"),
    ]
    links = "".join(f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>' for key, href, label in items)
    return f'<header><div class="brand"><pre aria-hidden="true">{LOGO}</pre><strong>Transfer Portal</strong></div><nav>{links}</nav><form method="post" action="/logout"><button>Sign out</button></form></header>'


def portal_card(portal: Portal) -> str:
    return f"""
    <article class="card">
      <h2>{esc(portal.display_name)}</h2>
      <p><strong>Source</strong><br>{esc(display_path(portal.source_path))}</p>
      <p><strong>Destination</strong><br>{esc(display_path(portal.destination_path))}</p>
      <a class="button" href="/portals/{esc(portal.slug)}">Open</a>
    </article>
    """


def job_portal_mapping(job: Any) -> str:
    try:
        portal = find_portal(load_portals(CONFIG_PATH), str(job["portal_slug"]))
    except PortalConfigError:
        return ""
    return f"""
    <section class="mapping">
      <h2>Portal Mapping</h2>
      <dl>
        <dt>Real source folder</dt><dd>{esc(display_path(portal.source_path))}</dd>
        <dt>Portal source mount</dt><dd>{esc(str(portal.source_mount))}</dd>
        <dt>Real destination folder</dt><dd>{esc(display_path(portal.destination_path))}</dd>
        <dt>Portal destination mount</dt><dd>{esc(str(portal.destination_mount))}</dd>
      </dl>
    </section>
    """


def portal_form() -> str:
    return """
    <form class="panel" method="post" action="/portals">
      <div class="form-head">
        <div>
          <h1>New Portal</h1>
          <p class="lede">Create stable source and destination mount points for one local OMV disk-to-disk transfer workflow.</p>
        </div>
        <a class="button" href="/">Back</a>
      </div>
      <label>Slug
        <span class="help">Short machine name used in URLs and mount paths, for example <code>photos-move</code>.</span>
        <input name="slug" pattern="[a-z0-9][a-z0-9-]{0,62}" required>
      </label>
      <label>Display name
        <span class="help">Human-friendly label shown in the portal list and transfer builder.</span>
        <input name="display_name" required>
      </label>
      <label>Source path
        <span class="help">Existing directory on the source data filesystem. System paths, unmounted paths, and overlapping paths are refused.</span>
        <span class="path-row"><input id="source_path" name="source_path" placeholder="/srv/dev-disk-by-uuid-xxxxxxx/source_folder" required><button type="button" data-browse-field="source_path">Browse</button></span>
      </label>
      <label>Destination path
        <span class="help">Existing directory on the destination data filesystem. This is where copy jobs write files.</span>
        <span class="path-row"><input id="destination_path" name="destination_path" placeholder="/srv/dev-disk-by-uuid-xxxxxxx/destination_folder" required><button type="button" data-browse-field="destination_path">Browse</button></span>
      </label>
      <section class="picker" id="path-picker" hidden>
        <div class="picker-head">
          <div>
            <strong id="picker-title">Choose folder</strong>
            <p class="help" id="picker-current">Mounted data roots</p>
          </div>
          <button type="button" id="picker-close">Close</button>
        </div>
        <div class="actions">
          <button type="button" id="picker-up" hidden>Up</button>
          <button type="button" class="primary" id="picker-use" hidden>Use this folder</button>
        </div>
        <div class="picker-list" id="picker-list"></div>
      </section>
      <fieldset>
        <legend>Destructive permissions</legend>
        <p class="help">Leave these off unless this portal is specifically meant to permit delete operations.</p>
        <label class="check"><input type="checkbox" name="allow_source_delete"> Allow source deletion for move mode</label>
        <label class="check"><input type="checkbox" name="allow_destination_delete"> Allow destination delete extras</label>
      </fieldset>
      <div class="actions">
        <button class="primary" type="submit">Create portal</button>
        <a class="button" href="/">Cancel</a>
      </div>
    </form>
    <script>
      (() => {
        const picker = document.getElementById('path-picker');
        const list = document.getElementById('picker-list');
        const current = document.getElementById('picker-current');
        const up = document.getElementById('picker-up');
        const use = document.getElementById('picker-use');
        const close = document.getElementById('picker-close');
        let activeField = null;
        let activePath = '';
        let parentPath = null;

        async function load(path) {
          list.textContent = 'Loading...';
          const response = await fetch('/api/browse?path=' + encodeURIComponent(path || ''), {headers: {'Accept': 'application/json'}});
          if (!response.ok) {
            list.textContent = 'Unable to list that folder.';
            return;
          }
          const data = await response.json();
          activePath = data.path || '';
          parentPath = data.parent || null;
          current.textContent = activePath || 'Mounted data roots';
          up.hidden = !parentPath;
          use.hidden = !activePath;
          list.textContent = '';
          if (!data.entries.length) {
            const empty = document.createElement('p');
            empty.className = 'empty';
            empty.textContent = 'No child folders.';
            list.appendChild(empty);
          }
          for (const entry of data.entries) {
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = entry.name;
            button.addEventListener('click', () => load(entry.path));
            list.appendChild(button);
          }
        }

        document.querySelectorAll('[data-browse-field]').forEach((button) => {
          button.addEventListener('click', () => {
            activeField = document.getElementById(button.dataset.browseField);
            picker.hidden = false;
            load(activeField.value);
          });
        });
        up.addEventListener('click', () => parentPath && load(parentPath));
        use.addEventListener('click', () => {
          if (activeField && activePath) activeField.value = activePath;
          picker.hidden = true;
        });
        close.addEventListener('click', () => { picker.hidden = true; });
      })();
    </script>
    """


def transfer_form(portals: list[Portal], selected: str) -> str:
    options = "".join(f'<option value="{esc(p.slug)}" {"selected" if p.slug == selected else ""}>{esc(p.display_name)}</option>' for p in portals)
    if not portals:
        return empty("Create a portal before building a transfer.")
    return f"""
    <form class="panel" method="post">
      <h1>Transfer Builder</h1>
      <label>Portal <select name="portal_slug">{options}</select></label>
      <fieldset><legend>Normal Options</legend>
        {checkbox('skip_existing', 'Skip existing')}
        {checkbox('update_newer_only', 'Update newer only')}
        {checkbox('checksum_compare', 'Checksum compare')}
        {checkbox('size_only_compare', 'Size-only compare')}
        {checkbox('delete_destination_extras', 'Delete destination extras')}
        {checkbox('preserve_acls', 'Preserve ACLs', True)}
        {checkbox('preserve_xattrs', 'Preserve xattrs', True)}
        {checkbox('preserve_owner_group', 'Preserve owner/group', True)}
        {checkbox('preserve_permissions', 'Preserve permissions', True)}
        {checkbox('preserve_hard_links', 'Preserve hard links', True)}
      </fieldset>
      <details><summary>Advanced</summary>
        <p class="warning">Advanced flags can change overwrite behavior. They are allowlisted and shown in the generated command preview.</p>
        <label>Advanced flag <select name="advanced_flag_1"><option value=""></option><option>--one-file-system</option><option>--whole-file</option><option>--ignore-times</option><option>--inplace</option></select></label>
      </details>
      <label class="check"><input type="checkbox" name="preview_only"> Preview command only, do not run rsync</label>
      <label>Move confirmation <input name="confirm_move" placeholder="type confirm for move"></label>
      <div class="actions">
        <button formaction="/jobs/dry-run" type="submit">Dry run</button>
        <button formaction="/jobs/copy" type="submit">Copy</button>
        <button class="danger" formaction="/jobs/move" type="submit">Move after verified copy</button>
      </div>
    </form>
    """


def settings_view(config: AppConfig, portals: list[Portal], job_count: int, active_jobs: int) -> str:
    allowed_prefixes = ", ".join(esc(str(path)) for path in config.allowed_mount_prefixes)
    blocked_paths = ", ".join(esc(str(path)) for path in config.blocked_paths)
    enabled_portals = sum(1 for portal in portals if portal.enabled)
    return f"""
    <section class="panel">
      <h1>Settings</h1>
      <p class="lede">Current Transfer Portal runtime settings and safety boundaries.</p>
      <div class="settings-grid">
        <section>
          <h2>Runtime</h2>
          <dl>
            <dt>Bind address</dt><dd>{esc(config.bind_host)}:{esc(str(config.bind_port))}</dd>
            <dt>Database</dt><dd>{esc(str(config.database_path))}</dd>
            <dt>Logs</dt><dd>{esc(str(config.log_dir))}</dd>
            <dt>Root helper</dt><dd>{esc(str(config.helper_path))}</dd>
            <dt>Portal base</dt><dd>{esc(str(config.portal_base))}</dd>
          </dl>
        </section>
        <section>
          <h2>Safety</h2>
          <dl>
            <dt>Allowed mount prefixes</dt><dd>{allowed_prefixes}</dd>
            <dt>Blocked paths</dt><dd>{blocked_paths}</dd>
            <dt>Max active jobs</dt><dd>{esc(str(config.max_active_jobs))}</dd>
          </dl>
        </section>
        <section>
          <h2>Activity</h2>
          <dl>
            <dt>Portals</dt><dd>{esc(str(len(portals)))} total, {esc(str(enabled_portals))} enabled</dd>
            <dt>Recent jobs</dt><dd>{esc(str(job_count))}</dd>
            <dt>Active jobs</dt><dd>{esc(str(active_jobs))}</dd>
          </dl>
        </section>
      </div>
      <section class="note-block">
        <h2>Portal paths</h2>
        <p>The source and destination fields should point to real folders on mounted data drives, such as <code>/srv/dev-disk-by-uuid-xxxxxxx/source_folder</code> and <code>/srv/dev-disk-by-uuid-xxxxxxx/destination_folder</code>.</p>
        <p>The app creates stable bind-mount paths under <code>{esc(str(config.portal_base))}/portal-slug/source</code> and <code>{esc(str(config.portal_base))}/portal-slug/destination</code>. Those portal paths are mount points, not copies of the data on the OS drive.</p>
        <p>The folders do not need to be OMV shared folders. They only need to exist on mounted data filesystems that pass the safety checks. Linux ownership and permissions still apply to the resulting rsync operation.</p>
      </section>
    </section>
    """


def checkbox(name: str, label: str, checked: bool = False) -> str:
    return f'<label class="check"><input type="checkbox" name="{name}" {"checked" if checked else ""}> {label}</label>'


def jobs_table(jobs: list[Any]) -> str:
    if not jobs:
        return empty("No jobs recorded yet.")
    rows = "".join(
        f"<tr><td><a href=\"/jobs/{job['id']}\">{job['id']}</a></td><td>{esc(job['portal_slug'])}</td><td>{esc(job['mode'])}</td><td>{esc(job['status'])}</td><td>{esc(job['created_at'])}</td></tr>"
        for job in jobs
    )
    return f"<table><thead><tr><th>ID</th><th>Portal</th><th>Mode</th><th>Status</th><th>Created</th></tr></thead><tbody>{rows}</tbody></table>"


def empty(text: str) -> str:
    return f'<p class="empty">{esc(text)}</p>'


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def json_list(value: str) -> list[str]:
    parsed = json.loads(value)
    return parsed if isinstance(parsed, list) else []


def display_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def esc(value: str) -> str:
    import html

    return html.escape(value, quote=True)


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "*/*" in accept or not accept


def error_panel(message: str) -> str:
    return f"""
    <section class="panel">
      <h1>Request Error</h1>
      <div class="alert" role="alert">{esc(message)}</div>
      <div class="actions"><a class="button" href="/">Back to portals</a></div>
    </section>
    """


LOGO = r""" .-==-. 
/  ()  \
\  /\  /
 `-==-'"""


def login_page(message: str | None = None, username: str = "", status_code: int = 200) -> HTMLResponse:
    alert = f'<div class="alert" role="alert">{esc(message)}</div>' if message else ""
    return page(
        "Sign In",
        f"""
        <section class="login">
          <form method="post" action="/login" class="panel" novalidate>
            <pre class="login-mark" aria-hidden="true">{LOGO}</pre>
            <h1>Transfer Portal</h1>
            {alert}
            <label>Username <input name="username" autocomplete="username" value="{esc(username)}" required></label>
            <label>Password <input name="password" type="password" autocomplete="current-password" required></label>
            <button class="primary" type="submit">Sign in</button>
          </form>
        </section>
        """,
        authenticated=False,
        status_code=status_code,
    )


def page(title: str, body: str, authenticated: bool = True, status_code: int = 200) -> HTMLResponse:
    del authenticated
    return HTMLResponse(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} - Transfer Portal</title>
  <style>
    :root {{ color-scheme: light; --ink:#172026; --muted:#5f6b74; --line:#d8dee4; --panel:#ffffff; --bg:#f5f7f9; --accent:#176b87; --danger:#b42318; --danger-soft:#fff1f0; }}
    body {{ margin:0; background:radial-gradient(circle at 14% 8%,rgba(23,107,135,.12),transparent 25rem),radial-gradient(circle at 86% 92%,rgba(34,151,102,.09),transparent 27rem),repeating-linear-gradient(90deg,transparent 0 95px,rgba(23,107,135,.035) 96px),repeating-linear-gradient(0deg,transparent 0 95px,rgba(23,107,135,.025) 96px),var(--bg); color:var(--ink); font-family:Segoe UI,Roboto,Arial,sans-serif; }}
    header {{ display:flex; align-items:center; gap:20px; padding:12px 20px; border-bottom:1px solid var(--line); background:rgba(255,255,255,.72); box-shadow:inset 0 1px 0 rgba(255,255,255,.78),0 10px 28px rgba(23,32,38,.1); backdrop-filter:blur(16px) saturate(125%); }}
    .brand {{ display:flex; align-items:center; gap:10px; min-width:190px; }}
    .brand pre {{ margin:0; color:var(--accent); background:transparent; padding:0; font:700 9px/0.9 Consolas,monospace; letter-spacing:0; }}
    nav {{ display:flex; gap:8px; flex:1; }}
    nav a, .button, button {{ border:1px solid var(--line); background:linear-gradient(145deg,rgba(255,255,255,.9),rgba(245,248,250,.72)); box-shadow:inset 0 1px 0 rgba(255,255,255,.9),0 5px 12px rgba(23,32,38,.12); color:var(--ink); padding:8px 10px; border-radius:6px; text-decoration:none; font:inherit; cursor:pointer; transition:transform 150ms ease,box-shadow 150ms ease,border-color 150ms ease; }}
    nav a.active, .primary, button:hover, .button:hover {{ border-color:var(--accent); color:var(--accent); box-shadow:inset 0 1px 0 rgba(255,255,255,.95),0 9px 18px rgba(23,32,38,.18); transform:translateY(-1px); }}
    main {{ max-width:1120px; margin:24px auto; padding:0 20px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; }}
    .settings-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:20px; }}
    .note-block {{ margin-top:20px; border-top:1px solid var(--line); padding-top:16px; }}
    .card, .panel {{ background:linear-gradient(135deg,rgba(255,255,255,.72),rgba(255,255,255,.52)); border:1px solid rgba(216,222,228,.88); border-radius:8px; box-shadow:inset 0 1px 0 rgba(255,255,255,.82),inset 0 -1px 0 rgba(23,32,38,.04),0 16px 32px rgba(23,32,38,.12); padding:16px; backdrop-filter:blur(14px) saturate(120%); }}
    .toolbar, .actions {{ display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }}
    .form-head {{ display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:8px; }}
    .lede {{ max-width:720px; color:var(--muted); margin:4px 0 0; }}
    label {{ display:block; margin:12px 0; }}
    .help {{ display:block; color:var(--muted); font-size:0.92rem; line-height:1.35; margin:4px 0 6px; max-width:780px; }}
    code {{ background:#eef2f4; padding:1px 4px; border-radius:4px; }}
    .path-row {{ display:flex; gap:8px; align-items:center; max-width:760px; }}
    .path-row input {{ flex:1; max-width:none; }}
    .picker {{ border:1px solid var(--line); border-radius:8px; padding:12px; margin:12px 0 16px; background:#fbfcfd; }}
    .picker-head {{ display:flex; align-items:flex-start; justify-content:space-between; gap:12px; }}
    .picker-list {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:8px; margin-top:8px; }}
    .picker-list button {{ text-align:left; overflow-wrap:anywhere; }}
    .mapping {{ border:1px solid var(--line); border-radius:8px; padding:12px; margin:0 0 16px; background:#fbfcfd; }}
    .mapping h2 {{ margin-top:0; }}
    fieldset {{ border:1px solid var(--line); border-radius:8px; padding:10px 12px; margin:16px 0; }}
    legend {{ padding:0 6px; font-weight:600; }}
    input, select {{ width:100%; max-width:620px; box-sizing:border-box; padding:8px; border:1px solid var(--line); border-radius:6px; font:inherit; }}
    .check {{ display:flex; gap:8px; align-items:center; }}
    .check input {{ width:auto; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); }}
    th, td {{ padding:10px; border-bottom:1px solid var(--line); text-align:left; }}
    dt {{ font-weight:600; margin-top:10px; }}
    dd {{ margin-left:0; color:var(--muted); }}
    pre {{ white-space:pre-wrap; background:#eef2f4; padding:12px; border-radius:6px; }}
    .danger {{ border-color:var(--danger); color:var(--danger); }}
    .danger-zone {{ margin-top:24px; border-top:1px solid var(--line); padding-top:16px; }}
    .alert {{ border:1px solid var(--danger); background:var(--danger-soft); color:var(--danger); border-radius:6px; padding:10px 12px; margin:0 0 12px; }}
    .warning {{ color:var(--danger); }}
    .empty {{ color:var(--muted); }}
    .login {{ min-height:100vh; display:grid; place-items:center; }}
    .login .panel {{ width:min(420px, calc(100vw - 32px)); }}
    .login-mark {{ display:inline-block; margin:0 0 8px; color:var(--accent); background:transparent; padding:0; font:700 13px/0.95 Consolas,monospace; letter-spacing:0; }}
    @media (max-width: 720px) {{
      header {{ align-items:flex-start; flex-direction:column; gap:10px; }}
      nav {{ flex-wrap:wrap; }}
      .form-head {{ flex-direction:column; }}
      .path-row {{ align-items:stretch; flex-direction:column; }}
    }}
  </style>
</head>
<body><main>{body}</main></body>
	</html>""",
        status_code=status_code,
    )


app = create_app()
