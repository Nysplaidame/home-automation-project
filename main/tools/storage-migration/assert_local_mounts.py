"""Read-only UUID/whole-filesystem guard for OMV and its Filebrowser views."""
import argparse
import json
import subprocess


def check(expected):
    issues = []
    for target, uuid in expected.items():
        result = subprocess.run(["findmnt", "-J", "--mountpoint", target, "-o", "UUID,FSTYPE,SOURCE"],
                                capture_output=True, text=True)
        rows = json.loads(result.stdout).get("filesystems", []) if result.returncode == 0 else []
        if (len(rows) != 1 or rows[0].get("uuid") != uuid or rows[0].get("fstype") != "ext4" or
                "[" in rows[0].get("source", "")):
            issues.append(target)
    return issues


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    args = parser.parse_args()
    with open(args.contract, encoding="utf-8") as stream:
        expected = json.load(stream)
    issues = check(expected)
    print(json.dumps({"wrong_or_missing_mounts": issues}))
    raise SystemExit(2 if issues else 0)
