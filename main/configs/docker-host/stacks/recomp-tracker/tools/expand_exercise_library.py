"""Normalize and expand Recomp Tracker's exercise library safely.

Dry-run by default. With --apply, existing exercise IDs are preserved, routines
are updated by exerciseId, completed workout history is left unchanged, and the
server's normal KV revisions provide rollback points.
"""

import argparse
import json
import re
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


RENAMES = {
    "air squats": "Squat - Air",
    "back squat": "Squat - Barbell back",
    "bicep curl": "Curl - Biceps",
    "calf raise": "Calf raise - Standing",
    "dead hang": "Hang - Dead",
    "dip back-off (bodyweight/light)": "Dip - Bodyweight back-off",
    "farmer's carry": "Carry - Farmer's",
    "full form chin-up": "Chin-up - Full form",
    "full form dips": "Dip - Full form",
    "full form pull-up": "Pull-up - Full form",
    "full form push up": "Push-up - Full form",
    "isometric hold (wall squat / dip bottom)": "Isometric hold - Wall squat or dip bottom",
    "isometrics - dip": "Dip - Isometric hold",
    "isometrics - pull up": "Pull-up - Isometric hold",
    "isometrics - push-up": "Push-up - Isometric hold",
    "jump squat": "Squat - Jump",
    "lateral bound": "Bound - Lateral",
    "lateral raise": "Raise - Dumbbell lateral",
    "mobility - arm twists": "Arm circle - Mobility",
    "overhead press": "Press - Barbell overhead",
    "pull-up back-off (bodyweight/light)": "Pull-up - Bodyweight back-off",
    "rings - dips": "Dip - Rings",
    "rings - pull-ups": "Pull-up - Rings",
    "rings - push-ups": "Push-up - Rings",
    "rings - rows": "Row - Rings",
    "romanian deadlift": "Deadlift - Romanian",
    "row": "Row - Weighted",
    "skipping": "Skipping - Freestyle",
    "skipping - boxer": "Skipping - Boxer step",
    "skipping - forward and back": "Skipping - Forward and back",
    "skipping - knees up": "Skipping - High knees",
    "skipping - normal": "Skipping - Basic",
    "static bike - hiit": "Bike - Static HIIT",
    "tricep pushdown": "Pushdown - Triceps",
    "weighted / leverage push-up": "Push-up - Weighted",
    "weighted dip": "Dip - Weighted",
    "weighted pull-up": "Pull-up - Weighted",
}


def canonical(value):
    return re.sub(r"\s+", " ", str(value).strip().lower())


def get_record(base_url, key):
    with urlopen(base_url.rstrip("/") + "/api/kv/" + key, timeout=20) as response:
        record = json.load(response)
    return record, json.loads(record["value"])


def put_record(base_url, key, record, value):
    payload = json.dumps({"value": json.dumps(value), "expectedVersion": record["version"]}).encode("utf-8")
    request = Request(base_url.rstrip("/") + "/api/kv/" + key, data=payload, method="PUT", headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=30):
            pass
    except HTTPError as error:
        raise SystemExit(f"{key} was not changed: HTTP {error.code}. Refresh and rerun the dry-run.") from error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://192.168.20.102:8420")
    parser.add_argument("--catalog", default=str(Path(__file__).resolve().parents[1] / "static" / "exercise-catalog.json"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    catalog_by_name = {canonical(item["name"]): item for item in catalog}
    library_record, library = get_record(args.url, "exercise-library")
    routines_record, routines = get_record(args.url, "workout-routines")
    items = library.setdefault("items", [])

    renames, refreshed, additions = [], [], []
    claimed_names = set()
    for item in items:
        old_name = item.get("name", "")
        desired = RENAMES.get(canonical(old_name), old_name)
        catalog_item = catalog_by_name.get(canonical(desired))
        if catalog_item:
            if old_name != catalog_item["name"]:
                renames.append({"from": old_name, "to": catalog_item["name"]})
            preserved = {key: item[key] for key in ("id", "archived") if key in item}
            item.clear(); item.update(catalog_item); item.update(preserved)
            refreshed.append(item["name"])
        elif " - " not in old_name:
            item["name"] = old_name + " - Standard"
            item.setdefault("instructions", [item.get("tip", "Use a controlled range."), "Set up in a stable position before each set.", "Stop when alignment or a pain-free range changes."])
            item.setdefault("visual", "general")
            renames.append({"from": old_name, "to": item["name"]})
        claimed_names.add(canonical(item["name"]))

    for catalog_item in catalog:
        if canonical(catalog_item["name"]) in claimed_names:
            continue
        items.append(dict(catalog_item, archived=False))
        claimed_names.add(canonical(catalog_item["name"]))
        additions.append(catalog_item["name"])

    by_id = {item["id"]: item for item in items}
    routine_updates = 0
    for routine in routines.get("items", []):
        for exercise in routine.get("exercises", []):
            source = by_id.get(exercise.get("exerciseId"))
            if not source:
                desired = RENAMES.get(canonical(exercise.get("name")))
                source = catalog_by_name.get(canonical(desired)) if desired else None
            if not source:
                continue
            before = (exercise.get("name"), exercise.get("tip"), exercise.get("instructions"), exercise.get("visual"))
            exercise.update({key: source[key] for key in ("name", "tip", "instructions", "visual", "target") if key in source})
            if before != (exercise.get("name"), exercise.get("tip"), exercise.get("instructions"), exercise.get("visual")):
                routine_updates += 1

    report = {
        "existingExercises": len(items) - len(additions), "catalogExercises": len(catalog),
        "renamed": len(renames), "refreshedWithGuidance": len(refreshed),
        "added": len(additions), "routineExercisesUpdated": routine_updates,
        "renamePreview": renames, "additionPreview": additions[:30],
    }
    print(json.dumps(report, indent=2))
    if not args.apply:
        return
    put_record(args.url, "exercise-library", library_record, library)
    if routine_updates:
        put_record(args.url, "workout-routines", routines_record, routines)
    print(f"Applied exercise expansion: {len(additions)} added, {len(renames)} renamed, {routine_updates} routine references updated.")


if __name__ == "__main__":
    main()
