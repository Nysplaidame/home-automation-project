import os
import re
import sqlite3
import threading
import time
import json
import math
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
import requests

DB_PATH = os.environ.get("DB_PATH", "/data/recomp.db")
NTFY_URL = os.environ.get("NTFY_URL", "http://ntfy")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
NTFY_TOKEN = os.environ.get("NTFY_TOKEN", "")
NTFY_USER = os.environ.get("NTFY_USER", "")
NTFY_PASSWORD = os.environ.get("NTFY_PASSWORD", "")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", str(8 * 1024 * 1024)))

KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    # Single generic key-value table. Mirrors the artifact's window.storage
    # semantics exactly (key -> JSON string value), so the same index.html
    # works unmodified whether it's a Claude artifact or served here.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kv_revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            value TEXT,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_kv_revisions_key_id
        ON kv_revisions (key, id DESC)
    """)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.commit()
    conn.close()


def local_now():
    return datetime.now().astimezone()


def kv_get(key):
    conn = get_db()
    row = conn.execute(
        "SELECT value, updated_at FROM kv_store WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def kv_set(key, value, expected_version=None, strict_version=False):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        current = conn.execute(
            "SELECT value, updated_at FROM kv_store WHERE key = ?", (key,)
        ).fetchone()
        if strict_version or expected_version is not None:
            current_version = current["updated_at"] if current else None
            if expected_version != current_version:
                return None, "conflict"
        if current:
            conn.execute(
                "INSERT INTO kv_revisions (key, value, updated_at) VALUES (?, ?, ?)",
                (key, current["value"], current["updated_at"]),
            )
        now = datetime.utcnow().isoformat(timespec="microseconds")
        conn.execute("""
            INSERT INTO kv_store (key, value, updated_at) VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """, (key, value, now))
        conn.commit()
        return now, None
    finally:
        conn.close()


def kv_revisions(key, limit=20):
    conn = get_db()
    rows = conn.execute(
        "SELECT id, updated_at FROM kv_revisions WHERE key = ? ORDER BY id DESC LIMIT ?",
        (key, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def kv_restore_revision(key, revision_id, expected_version=None):
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        current = conn.execute(
            "SELECT updated_at FROM kv_store WHERE key = ?", (key,)
        ).fetchone()
        current_version = current["updated_at"] if current else None
        if expected_version is not None and expected_version != current_version:
            return None, "conflict"
        revision = conn.execute(
            "SELECT value FROM kv_revisions WHERE key = ? AND id = ?", (key, revision_id)
        ).fetchone()
        if not revision:
            return None, "not_found"
        if current:
            current_value = conn.execute(
                "SELECT value FROM kv_store WHERE key = ?", (key,)
            ).fetchone()["value"]
            conn.execute(
                "INSERT INTO kv_revisions (key, value, updated_at) VALUES (?, ?, ?)",
                (key, current_value, current_version),
            )
        now = datetime.utcnow().isoformat(timespec="microseconds")
        conn.execute(
            "INSERT INTO kv_store (key, value, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, revision["value"], now),
        )
        conn.commit()
        return now, None
    finally:
        conn.close()


def send_ntfy(message, title=None, priority="default", tags=None):
    if not NTFY_TOPIC:
        return False
    url = f"{NTFY_URL.rstrip('/')}/{NTFY_TOPIC}"
    headers = {}
    if title:
        headers["Title"] = title
    if priority:
        headers["Priority"] = priority
    if tags:
        headers["Tags"] = ",".join(tags)
    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"
    auth = (NTFY_USER, NTFY_PASSWORD) if NTFY_USER and NTFY_PASSWORD else None
    try:
        response = requests.post(
            url, data=message.encode("utf-8"), headers=headers, auth=auth, timeout=10
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


# ---------- Generic KV API (backs the frontend's Storage shim) ----------

@app.route("/healthz")
def healthz():
    try:
        conn = get_db()
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except sqlite3.Error:
        return jsonify({"status": "unhealthy"}), 503
    return jsonify({"status": "ok"})


@app.route("/api/kv/<key>", methods=["GET"])
def api_kv_get(key):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "invalid key"}), 400
    record = kv_get(key)
    if record is None:
        return jsonify(None), 404
    return jsonify({"key": key, "value": record["value"], "version": record["updated_at"]})


@app.route("/api/kv/<key>", methods=["PUT"])
def api_kv_put(key):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "invalid key"}), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "value" not in data:
        return jsonify({"error": "JSON object with string 'value' required"}), 400
    value = data["value"]
    if not isinstance(value, str):
        return jsonify({"error": "'value' must be a string"}), 400
    try:
        part = next((p for p, k in PART_KEYS.items() if k == key), None)
        if part:
            validate_part(part, json.loads(value))
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400
    expected_version = data.get("expectedVersion")
    if expected_version is not None and not isinstance(expected_version, str):
        return jsonify({"error": "'expectedVersion' must be a string or null"}), 400
    version, error = kv_set(key, value, expected_version, strict_version="expectedVersion" in data)
    if error == "conflict":
        return jsonify({"error": "conflict", "message": "This data changed on another device. Refresh before saving."}), 409
    return jsonify({"key": key, "value": value, "version": version})


@app.route("/api/kv/<key>/revisions", methods=["GET"])
def api_kv_revisions(key):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "invalid key"}), 400
    return jsonify({"key": key, "revisions": kv_revisions(key)})


@app.route("/api/kv/<key>/revisions/<int:revision_id>/restore", methods=["POST"])
def api_kv_restore_revision(key, revision_id):
    if not KEY_RE.fullmatch(key):
        return jsonify({"error": "invalid key"}), 400
    data = request.get_json(silent=True) or {}
    expected_version = data.get("expectedVersion")
    if expected_version is not None and not isinstance(expected_version, str):
        return jsonify({"error": "'expectedVersion' must be a string or null"}), 400
    version, error = kv_restore_revision(key, revision_id, expected_version)
    if error == "conflict":
        return jsonify({"error": "conflict"}), 409
    if error == "not_found":
        return jsonify({"error": "revision not found"}), 404
    return jsonify({"key": key, "version": version})


@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/service-worker.js")
def service_worker():
    response = send_from_directory("static", "service-worker.js")
    response.headers["Cache-Control"] = "no-cache"
    return response


PART_KEYS = {
    "health": "health-log", "workouts": "workout-log", "routines": "workout-routines",
    "library": "exercise-library", "settings": "tracker-settings", "reviews": "monthly-reviews",
    "reminders": "reminder-settings", "active": "active-workout", "diet": "daily-diet-log",
    "foods": "food-library", "dietSettings": "diet-settings", "mealTemplates": "meal-templates",
    "programme": "calisthenics-programme",
}


def validate_part(part, value):
    """Reject malformed backups before changing any live record."""
    def require(condition, detail):
        if not condition:
            raise ValueError(f"{part}: {detail}")

    def objects(items, detail, ids=False):
        require(isinstance(items, list) and all(isinstance(x, dict) for x in items), detail)
        if ids:
            identifiers = [x.get("id") for x in items]
            require(all(isinstance(x, str) and x for x in identifiers) and
                    len(set(identifiers)) == len(identifiers), "missing or duplicate IDs")
        return items

    def exercises(items, require_sets=False):
        for exercise in objects(items, "invalid exercises"):
            require(isinstance(exercise.get("name"), str), "exercise name required")
            if require_sets or "sets" in exercise:
                objects(exercise.get("sets"), "invalid sets")

    def finite_tree(item):
        if isinstance(item, float):
            require(math.isfinite(item), "non-finite number")
        elif isinstance(item, dict):
            for child in item.values():
                finite_tree(child)
        elif isinstance(item, list):
            for child in item:
                finite_tree(child)

    finite_tree(value)

    if part == "active" and value is None:
        return
    require(isinstance(value, dict), "expected an object")
    if part == "workouts":
        for session in objects(value.get("sessions"), "sessions must be an array", True):
            require(isinstance(session.get("date"), str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", session["date"])), "invalid workout date")
            try:
                datetime.strptime(session["date"], "%Y-%m-%d")
            except ValueError:
                raise ValueError("workouts: invalid workout date")
            exercises(session.get("exercises"), require_sets=True)
        for deleted in objects(value.get("trash", []), "invalid recently deleted list", True):
            require(isinstance(deleted.get("session"), dict), "invalid deleted workout")
            validate_part("workouts", {"sessions": [deleted["session"]]})
    elif part == "active":
        exercises(value.get("exercises"), require_sets=True)
    elif part in ("library", "foods", "routines", "mealTemplates"):
        for item in objects(value.get("items"), "items must be an array", True):
            require(isinstance(item.get("name"), str), "name required")
            if part == "routines":
                exercises(item.get("exercises"))
            if part == "mealTemplates":
                objects(item.get("entries"), "invalid meal entries")
    elif part in ("health", "diet", "reviews"):
        field = {"health": "entries", "diet": "days", "reviews": "items"}[part]
        require(isinstance(value.get(field), dict), f"{field} must be an object")
        require(all(isinstance(x, dict) for x in value[field].values()), f"invalid {field}")
        if part == "diet":
            for day in value[field].values():
                require(isinstance(day.get("meals", {}), dict), "invalid meals")
                for rows in day.get("meals", {}).values():
                    objects(rows, "invalid meal rows")
                if "oneTimeMeals" in day:
                    estimates = objects(day["oneTimeMeals"], "invalid one-time meals")
                    require(len(estimates) <= 100, "too many one-time meals")
                    for estimate in estimates:
                        if "id" in estimate:
                            require(isinstance(estimate["id"], str) and 0 < len(estimate["id"]) <= 160, "invalid one-time meal ID")
                        if "name" in estimate:
                            require(isinstance(estimate["name"], str) and len(estimate["name"]) <= 140, "invalid one-time meal description")
                        if "checked" in estimate:
                            require(isinstance(estimate["checked"], bool), "invalid one-time meal inclusion")
                        for nutrient in ("calories", "protein", "carbs", "fat"):
                            if nutrient in estimate:
                                nutrient_value = estimate[nutrient]
                                require(isinstance(nutrient_value, (int, float)) and not isinstance(nutrient_value, bool) and 0 <= nutrient_value <= 100000, f"invalid one-time meal {nutrient}")
    elif part == "dietSettings":
        for constant in objects(value.get("constants"), "invalid constants", True):
            require(isinstance(constant.get("name"), str), "constant name required")
            if "quantity" in constant:
                require(isinstance(constant["quantity"], (int, float)) and not isinstance(constant["quantity"], bool) and 0 < constant["quantity"] <= 100000, "invalid constant quantity")
            if "foodId" in constant:
                require(constant["foodId"] is None or isinstance(constant["foodId"], str), "invalid constant food reference")
            if "sourceMode" in constant:
                require(constant["sourceMode"] in ("per100", "legacy-portion"), "invalid constant source mode")
        require(isinstance(value.get("targets"), dict), "targets required")
        if "sections" in value:
            objects(value["sections"], "invalid sections", True)
    elif part == "settings":
        if "exerciseGoals" in value:
            objects(value["exerciseGoals"], "invalid goals", True)
        for field in ("equipment", "hiit"):
            if field in value:
                require(isinstance(value[field], dict), f"invalid {field}")
    elif part == "programme":
        require(isinstance(value.get("skillStages"), dict), "skill stages required")
        objects(value.get("tests", []), "invalid tests", True)
        objects(value.get("stageHistory", []), "invalid stage history")
        for field in ("weeklyChecks", "prerequisites"):
            require(isinstance(value.get(field, {}), dict), f"invalid {field}")
    elif part == "reminders":
        for field in ("enabled", "times"):
            require(isinstance(value.get(field, {}), dict), f"invalid {field}")


@app.route("/api/backup/validate", methods=["POST"])
def validate_backup():
    try:
        bundle = request.get_json(silent=True)
        if not isinstance(bundle, dict) or not isinstance(bundle.get("data"), dict):
            raise ValueError("Expected a Recomp Tracker backup")
        if not isinstance(bundle.get("schemaVersion"), int) or not 1 <= bundle["schemaVersion"] <= 13:
            raise ValueError("Unsupported backup version")
        parts = bundle["data"]
        if not parts or any(p not in PART_KEYS for p in parts):
            raise ValueError("Backup has missing or unknown sections")
        for part, value in parts.items():
            if value is not None or part == "active":
                validate_part(part, value)
        return jsonify({"valid": True})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/kv-batch", methods=["POST"])
def api_kv_batch():
    body = request.get_json(silent=True)
    try:
        if not isinstance(body, dict) or not isinstance(body.get("data"), dict) or not body["data"]:
            raise ValueError("Expected non-empty data")
        parts = body["data"]
        versions = body.get("versions")
        if not isinstance(versions, dict) or any(p not in PART_KEYS for p in parts):
            raise ValueError("Invalid sections or missing versions")
        for part, value in parts.items():
            if part not in versions or (versions[part] is not None and not isinstance(versions[part], str)):
                raise ValueError("Every section requires its expected version")
            validate_part(part, value)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    conn = get_db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        for part in parts:
            current = conn.execute("SELECT updated_at FROM kv_store WHERE key=?", (PART_KEYS[part],)).fetchone()
            if (current["updated_at"] if current else None) != versions[part]:
                return jsonify({"error": "Data changed on another device. Reload before retrying."}), 409
        now = datetime.utcnow().isoformat(timespec="microseconds")
        if body.get("snapshot"):
            snapshot = {}
            for part, key in PART_KEYS.items():
                row = conn.execute("SELECT value FROM kv_store WHERE key=?", (key,)).fetchone()
                snapshot[part] = json.loads(row["value"]) if row else None
            previous = conn.execute("SELECT value,updated_at FROM kv_store WHERE key='pre-import-snapshot'").fetchone()
            if previous:
                conn.execute("INSERT INTO kv_revisions(key,value,updated_at) VALUES(?,?,?)", ("pre-import-snapshot", previous["value"], previous["updated_at"]))
            conn.execute("INSERT OR REPLACE INTO kv_store VALUES(?,?,?)", ("pre-import-snapshot", json.dumps({"schemaVersion": 13, "data": snapshot}), now))
        result = {}
        for part, value in parts.items():
            key = PART_KEYS[part]
            current = conn.execute("SELECT value,updated_at FROM kv_store WHERE key=?", (key,)).fetchone()
            if current:
                conn.execute("INSERT INTO kv_revisions(key,value,updated_at) VALUES(?,?,?)", (key, current["value"], current["updated_at"]))
            conn.execute("INSERT OR REPLACE INTO kv_store VALUES(?,?,?)", (key, json.dumps(value), now))
            result[part] = now
        conn.commit()
        return jsonify({"versions": result})
    finally:
        conn.close()


# ---------- Reminder config — edit this list to change what/when you get nudged ----------
# Meal anchors: breakfast 07:45, lunch 12:45, dinner 18:00.
# Weekday numbering: Monday=0 ... Sunday=6.
# "field" (optional) is a key inside today's health-log entry (camelCase, matching
# the frontend's HABITS: training, proteinBreakfast, postMealWalk, dimLight,
# morningLight) — if already true, the nudge is skipped.
REMINDERS = [
    {"id": "morning_light", "time": "07:15", "field": "morningLight",
     "label": "Good window for morning light right now — get outside if you can", "days": None},
    {"id": "water_breakfast", "time": "07:20",
     "label": "Water — breakfast in 25 min", "days": None},
    {"id": "fish_oil", "time": "07:45",
     "label": "Fish oil with breakfast (1-2g EPA/DHA)", "days": None},
    {"id": "post_breakfast_move", "time": "08:10",
     "label": "Short walk or a few bodyweight squats/calf raises", "days": None},
    {"id": "resistant_starch", "time": "09:30",
     "label": "Resistant starch in a smoothie sometime today", "days": None},
    {"id": "water_lunch", "time": "12:20",
     "label": "Water — lunch in 25 min", "days": None},
    {"id": "lunch_supplements", "time": "12:45",
     "label": "Creatine (3-5g) + make sure lunch hits your protein target", "days": None},
    {"id": "post_lunch_move", "time": "13:10",
     "label": "Short walk or a few bodyweight squats/calf raises", "days": None},
    {"id": "water_dinner", "time": "17:35",
     "label": "Water — dinner in 25 min", "days": None},
    {"id": "post_dinner_move", "time": "18:25",
     "label": "Walk or bodyweight squats/calf raises after your biggest carb meal", "days": None},
    {"id": "workout_calisthenics", "time": "18:30", "field": "training",
     "label": "Today: Calisthenics \u2014 Pair A (weighted pull-up \u2194 dip), Pair B (push-up \u2194 row), then isometric hold",
     "days": [0, 2]},
    {"id": "workout_cardio", "time": "18:30",
     "label": "Today: Cardio (run/skip) \u2014 optional jump squats/lateral bounds first", "days": [1, 3]},
    {"id": "workout_weights", "time": "18:30", "field": "training",
     "label": "Today: Weights \u2014 squat, RDL, overhead press + isolation work", "days": [5]},
    {"id": "workout_rest", "time": "18:30",
     "label": "Rest day \u2014 light walk if you feel like it, otherwise let it be a real rest", "days": [4, 6]},
    {"id": "dim_light_warning", "time": "21:15", "field": "dimLight",
     "label": "Dim the lights and put screens down soon \u2014 reading time coming up", "days": None},
    {"id": "bedtime_nudge", "time": "23:00",
     "label": "Wind down \u2014 aiming for asleep by 23:30", "days": None},
]
_reminders_sent_today = set()
_reminders_last_reset = None


def get_today_habit_entry(today_str):
    """Reads today's entry straight out of the health-log JSON blob
    (same shape as the frontend's DATA.entries[date])."""
    record = kv_get("health-log")
    if not record:
        return {}
    try:
        parsed = json.loads(record["value"])
        return parsed.get("entries", {}).get(today_str, {})
    except (json.JSONDecodeError, AttributeError):
        return {}


def check_configured_reminders(now, today_str):
    global _reminders_sent_today, _reminders_last_reset
    if _reminders_last_reset != today_str:
        _reminders_sent_today = set()
        _reminders_last_reset = today_str

    settings_record = kv_get("reminder-settings")
    try:
        settings = json.loads(settings_record["value"]) if settings_record else {}
    except (json.JSONDecodeError, TypeError):
        settings = {}
    weekday = now.weekday()
    for r in REMINDERS:
        if r["id"] in _reminders_sent_today:
            continue
        if settings.get("enabled", {}).get(r["id"]) is False:
            continue
        if r.get("days") is not None and weekday not in r["days"]:
            continue
        reminder_time = settings.get("times", {}).get(r["id"], r["time"])
        try:
            rh, rm = map(int, reminder_time.split(":"))
        except (ValueError, AttributeError):
            rh, rm = map(int, r["time"].split(":"))
        if not (rh == now.hour and rm <= now.minute < rm + 5):
            continue

        if r.get("field"):
            entry = get_today_habit_entry(today_str)
            if bool(entry.get(r["field"])):
                _reminders_sent_today.add(r["id"])
                continue

        if send_ntfy(r["label"], title="Reminder", tags=["bell"]):
            _reminders_sent_today.add(r["id"])


def check_monthly_photo_reminder(now, today_str, last_photo_date):
    if last_photo_date == today_str or now.hour != 9:
        return last_photo_date
    record = kv_get("health-log")
    if not record:
        return last_photo_date
    try:
        entries = json.loads(record["value"]).get("entries", {})
    except (json.JSONDecodeError, AttributeError):
        return last_photo_date
    if not entries:
        return last_photo_date
    first_date = datetime.strptime(min(entries.keys()), "%Y-%m-%d")
    days_since = (now.replace(tzinfo=None) - first_date).days
    if days_since > 0 and days_since % 30 == 0:
        if send_ntfy("New tracking month \u2014 take progress photos, waist measurement, and weigh-in.",
                     title="Monthly check-in", tags=["camera", "straight_ruler"]):
            return today_str
    return last_photo_date


@app.route("/api/reminders", methods=["GET"])
def api_reminders():
    """Expose the safe, user-configurable reminder catalogue to the UI."""
    return jsonify({
        "items": [
            {key: reminder[key] for key in ("id", "label", "time", "days")}
            for reminder in REMINDERS
        ]
    })


@app.route("/api/reminders/test", methods=["POST"])
def api_reminders_test():
    if not NTFY_TOPIC:
        return jsonify({"error": "ntfy topic is not configured"}), 503
    if not send_ntfy("Recomp Tracker notifications are working.", title="Test notification", tags=["white_check_mark"]):
        return jsonify({"error": "notification could not be delivered"}), 502
    return jsonify({"status": "sent"})


def scheduler_loop():
    last_photo_date = None
    while True:
        now = local_now()
        today_str = now.strftime("%Y-%m-%d")
        check_configured_reminders(now, today_str)
        last_photo_date = check_monthly_photo_reminder(now, today_str, last_photo_date)
        time.sleep(300)


if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    from waitress import serve
    serve(app, host="0.0.0.0", port=8420, threads=4)
