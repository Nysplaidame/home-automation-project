"""Read-only exact-source guard for the prepared Docker-host NFS mounts."""
import argparse
import json
import subprocess


def check(expected):
    issues = []
    for target, source in expected.items():
        result = subprocess.run(["findmnt", "-J", "--mountpoint", target, "-o", "SOURCE,FSTYPE"],
                                capture_output=True, text=True)
        if result.returncode:
            issues.append({"target": target, "reason": "missing exact mount"}); continue
        mounts = json.loads(result.stdout).get("filesystems", [])
        if len(mounts) != 1 or mounts[0].get("source") != source or mounts[0].get("fstype") not in {"nfs", "nfs4"}:
            issues.append({"target": target, "reason": "wrong remote source or filesystem"})
    return issues


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract")
    args = parser.parse_args()
    with open(args.contract, encoding="utf-8") as stream:
        expected = json.load(stream)
    issues = check(expected)
    print(json.dumps({"issues": issues}, indent=2))
    raise SystemExit(2 if issues else 0)
