"""Server-side staged migration controller. Does not format disks or change services.

Preview is the default for copying; all namespace mutation requires quiesced
writers. CLI UUID checks cannot be disabled. Internal UUID=None supports fixtures.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import uuid as uuid_module

import migration_ops as ops
import verify_copy
import verify_layout
import snapshot_live
import quarantine

Y_UUID = "fdb92af7-371c-4793-8d98-ff47e961498d"
Z_UUID = "a216b8bb-708e-4342-a5be-a415cdc465fa"
MERGES = {"backups", "_codex_diagnostics",
          "_codex_diagnostics/actual-necrons-20261001-215428",
          "_codex_diagnostics/focused-20261001-213336",
          "_codex_diagnostics/sevenzip-20261001-213911"}
PHASES = ["flatten-z", "publish-z", "publish-y", "retain-y", "flatten-print"]


def check_array(root, healthy=False):
    if root.uuid is None:  # tests only; CLI never supplies None
        return
    md = Path(f"/sys/dev/block/{os.major(root.device)}:{os.minor(root.device)}")
    if (md / "md/level").read_text().strip() != "raid1":
        raise ValueError("Destination is not an MD RAID1 filesystem")
    if healthy and (int((md / "md/degraded").read_text()) != 0 or
                    (md / "md/sync_action").read_text().strip() != "idle"):
        raise ValueError("Y data requires a fully synchronised healthy destination mirror")
    serials = set()
    for member in (md / "slaves").iterdir():
        result = subprocess.run(["lsblk", "-sn", "-o", "SERIAL", "/dev/" + member.name],
                                capture_output=True, text=True, check=True)
        serials.update(result.stdout.split())
    if "3HG402GN" not in serials or not serials <= {"3HG402GN", "3GHV81YE"}:
        raise ValueError("Unexpected mirror member identity")


def create_session(state, y, z, target, session, uuids):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{5,47}", session):
        raise ValueError("Invalid session name")
    state = Path(state).resolve()
    roots = [ops.Root(path, value) for path, value in zip((y, z, target), uuids)]
    try:
        paths = [r.path for r in roots]
        if roots[0].info("Print") is None or roots[0].info("Print")["kind"] != stat.S_IFDIR:
            raise ValueError("Expected Print source directory")
        if any(name.casefold() in {".household-migration", ".household-retained"}
               for root in roots[:2] for name in root.names(".")):
            raise ValueError("Reserved migration namespace already exists in a source")
        if any(a == b or a in b.parents or b in a.parents
               for i, a in enumerate(paths) for b in paths[i+1:]):
            raise ValueError("Data roots must be distinct and non-nested")
        if state.exists() or any(state == p or p in state.parents for p in paths):
            raise ValueError("State must be new and outside all data roots")
        check_array(roots[2])
        if roots[2].names(".") not in ([], ["lost+found"]):
            raise ValueError("New destination must contain only optional empty lost+found")
        if roots[2].names(".") and roots[2].names("lost+found"):
            raise ValueError("lost+found is not empty")
        state.mkdir(mode=0o700)
        base = ".household-migration"
        os.mkdir(base, mode=0o700, dir_fd=roots[2].fd)
        with roots[2].directory(base) as fd:
            os.mkdir(session, mode=0o700, dir_fd=fd); os.fsync(fd)
        prefix = base + "/" + session
        with roots[2].directory(prefix) as fd:
            for name in ("stage-z", "stage-y"):
                os.mkdir(name, mode=0o700, dir_fd=fd)
            os.fsync(fd)
        os.fsync(roots[2].fd)
        config = {"session": session, "roots": {role: str(root.path) for role, root in zip(("y", "z", "target"), roots)},
                  "uuids": dict(zip(("y", "z", "target"), uuids)), "prefix": prefix,
                  "stage_ids": {role: roots[2].info(prefix + "/stage-" + role) for role in ("z", "y")}}
        ops.synced_json(state / "session.json", config)
        return config
    finally:
        for root in roots:
            root.close()


class Session:
    def __init__(self, state, fixture=False):
        self.state = Path(state).resolve()
        self.config = json.loads((self.state / "session.json").read_text())
        if not fixture and (self.config["uuids"]["y"] != Y_UUID or self.config["uuids"]["z"] != Z_UUID or
                            not self.config["uuids"]["target"] or self.config["uuids"]["target"] in {Y_UUID, Z_UUID}):
            raise ValueError("Production session requires pinned source UUIDs and a new target UUID")

    @contextmanager
    def locked(self):
        fd = os.open(self.state / "session.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            ops.fcntl.flock(fd, ops.fcntl.LOCK_EX | ops.fcntl.LOCK_NB)
            yield
        finally:
            os.close(fd)

    def event(self, name, **values):
        ops.append_event(self.state / "session.jsonl", {"event": name, **values})

    def history(self):
        return ops.events(self.state / "session.jsonl")

    def open_root(self, role):
        return ops.Root(self.config["roots"][role], self.config["uuids"][role])

    def stage(self, role):
        if role not in {"z", "y"}:
            raise ValueError("Invalid source role")
        return self.config["prefix"] + "/stage-" + role

    def check_stage(self, target, role):
        if target.info(self.stage(role)) != self.config["stage_ids"][role]:
            raise ValueError("Staging directory identity changed")

    def copy(self, role, execute=False, final=False, checksum_repair=False):
        with self.locked():
            source, target = self.open_root(role), self.open_root("target")
            try:
                check_array(target, healthy=role == "y")
                self.check_stage(target, role)
                if (self.state / ("flatten-z" if role == "z" else "publish-y")).exists():
                    raise ValueError("Transformation plan already sealed; copy cannot resume into changed layout")
                if checksum_repair and not final:
                    raise ValueError("Checksum repair requires a cold final copy")
                command = ops.copy_command(source.path, target.path / self.stage(role), role == "y", execute, checksum_repair)
                if not execute:
                    return {"preview": command}
                if shutil.disk_usage(target.path).free < 1024**3:
                    raise ValueError("Destination free space below 1 GiB safety floor")
                self.event("copy-start", role=role, command=command)
                result = subprocess.run(command, capture_output=True, text=True)
                self.event("copy-finish", role=role, code=result.returncode, final=final)
                (self.state / ("copy-" + role + "-" + uuid_module.uuid4().hex + ".log")).write_text(
                    result.stdout + "\n" + result.stderr, encoding="utf-8")
                if result.returncode:
                    raise RuntimeError("Rsync incomplete; sources retained, inspect private copy log")
                return {"copied": role}
            finally:
                source.close(); target.close()

    def verify_stage(self, role):
        with self.locked():
            relevant = [r for r in self.history() if r.get("role") == role and r["event"] in {"copy-start", "copy-finish"}]
            if (not relevant or relevant[-1]["event"] != "copy-finish" or relevant[-1]["code"] != 0 or
                    not relevant[-1].get("final")):
                raise ValueError("A successful cold final copy is required")
            if (self.state / ("flatten-z" if role == "z" else "publish-y")).exists():
                raise ValueError("Original staging layout is sealed for transformation")
            source, target = self.open_root(role), self.open_root("target")
            try:
                self.check_stage(target, role)
                report = self.state / ("verify-" + role + "-" + uuid_module.uuid4().hex + ".jsonl")
                result = verify_copy.verify(source.path, target.path / self.stage(role), report,
                                            {"Print"} if role == "y" else set())
                seal = ops.receipt(report, target.path / self.stage(role)) if result["issues"] == 0 else None
                self.event("verify-finish", role=role, report=str(report), receipt=seal, **result)
                return {"report": str(report), **result}
            finally:
                source.close(); target.close()

    def verified(self, role, target):
        history = [r for r in self.history() if r.get("role") == role and
                   r["event"] in {"copy-start", "copy-finish", "verify-finish"}]
        if not history or history[-1]["event"] != "verify-finish" or history[-1]["issues"]:
            raise ValueError("Fresh zero-issue verification required")
        report = Path(history[-1]["report"])
        self.validate_report(history[-1], role)
        # Detect changes since verification without rehashing terabytes. Mount
        # UUID is pinned separately; device numbers may change across reboot.
        with report.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["status"] != "checked":
                    continue
                name = row["path"].removeprefix("./")
                path = self.stage(role) if name == "." else self.stage(role) + "/" + ops.relative(name)
                with target.parent(path) as (fd, leaf):
                    value = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                actual = [str(v) for v in (value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)]
                if actual != row["target_generation"][1:]:
                    raise ValueError("Staging entry changed since verification: " + path)
        return report

    def validate_report(self, record, role):
        checked = ops.receipt(record["report"], Path(self.config["roots"]["target"]) / self.stage(role))
        if checked != record.get("receipt"):
            raise ValueError("Verification receipt changed after it was sealed")
        return record["report"]

    def prepare_phase(self, phase):
        with self.locked():
            role = "y" if phase in {"retain-y", "flatten-print"} else "target"
            root = self.open_root(role)
            try:
                moves, metadata, report, evidence_target = [], {}, None, None
                z = self.stage("z")
                y = self.stage("y")
                if phase == "flatten-z":
                    report = self.verified("z", root); evidence_target = root.path / z
                    metadata[z + "/books"] = root.meta(z + "/Media/books")
                    metadata[z] = root.meta(z)
                    moves.append((z + "/Media/books/calibre-library", z + "/calibre-library"))
                    moves += [(z + "/Media/" + name, z + "/" + name) for name in root.names(z + "/Media")]
                    self.event("z-root-metadata", value=root.meta(z))
                elif phase == "publish-z":
                    self.require_complete("flatten-z")
                    if root.names(z + "/Media"):
                        raise ValueError("Media staging wrapper still contains entries")
                    names = [n for n in root.names(z) if n != "Media"]
                    moves = [(z + "/" + name, name) for name in names]
                    metadata["."] = [r["value"] for r in self.history() if r["event"] == "z-root-metadata"][-1]
                elif phase == "publish-y":
                    self.require_complete("publish-z")
                    check_array(root, healthy=True)
                    report = self.verified("y", root); evidence_target = root.path / y
                    live = [r for r in self.history() if r["event"] == "live-baseline"]
                    activated = any(r["event"] == "activated" and r.get("phase") == "publish-z" for r in self.history())
                    if activated and (not live or live[-1]["issues"]):
                        raise ValueError("Quiesced current Media baseline required after live Z activation")
                    if live and ops.hash_file(live[-1]["report"]) != live[-1]["sha256"]:
                        raise ValueError("Live baseline changed after it was sealed")
                    def merge(source, dest):
                        existing = root.info(dest)
                        if existing is None:
                            moves.append((source, dest)); return
                        if dest not in MERGES or existing["kind"] != stat.S_IFDIR or root.info(source)["kind"] != stat.S_IFDIR:
                            raise ValueError("Unapproved merge or leaf collision: " + dest)
                        metadata[dest] = root.meta(source)
                        for name in root.names(source):
                            merge(source + "/" + name, dest + "/" + name)
                    for name in root.names(y):
                        if name == "Print":
                            raise ValueError("Print was incorrectly copied into the Y stage")
                        merge(y + "/" + name, name)
                    metadata["."] = live[-1]["root_metadata"] if live else [
                        r["value"] for r in self.history() if r["event"] == "z-root-metadata"][-1]
                elif phase == "retain-y":
                    self.require_complete("publish-y")
                    checks = [r for r in self.history() if r["event"] == "final-verified" and r["scope"] == "combined"]
                    if not checks or checks[-1]["issues"]:
                        raise ValueError("Final combined verification required before retaining Y originals")
                    if ops.hash_file(checks[-1]["report"]) != checks[-1]["sha256"]:
                        raise ValueError("Final verification receipt changed")
                    reports = [r for r in self.history() if r["event"] == "verify-finish" and r["role"] == "y"]
                    self.validate_report(reports[-1], "y")
                    tops = set()
                    with open(reports[-1]["report"], encoding="utf-8") as stream:
                        for line in stream:
                            row = json.loads(line)
                            if row["status"] != "checked" or row["path"] == ".":
                                continue
                            name = ops.relative(row["path"].removeprefix("./"))
                            tops.add(name.split("/")[0])
                            with root.parent(name) as (fd, leaf):
                                value = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                            actual = [str(v) for v in (value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)]
                            if actual != row["source_generation"][1:]:
                                raise ValueError("Original Y entry changed since copy: " + name)
                    if set(root.names(".")) - {"Print", ".household-retained"} != tops:
                        raise ValueError("Y top-level namespace changed since copy")
                    base = ".household-retained"
                    for path in (base, base + "/" + self.config["session"]):
                        with root.parent(path) as (fd, leaf):
                            try:
                                os.mkdir(leaf, mode=0o700, dir_fd=fd); os.fsync(fd)
                            except FileExistsError:
                                info = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                                if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077:
                                    raise ValueError("Unexpected retention directory")
                    retained = base + "/" + self.config["session"]
                    if root.names(retained):
                        raise ValueError("Retention directory already contains data")
                    moves = [(name, retained + "/" + name) for name in sorted(tops)]
                elif phase == "flatten-print":
                    self.require_complete("retain-y")
                    moves = [("Print/" + name, name) for name in root.names("Print")]
                else:
                    raise ValueError("Unknown phase")
                # Refuse Windows case aliases against existing destination names.
                for source, dest in moves:
                    parent, leaf = str(Path(dest).parent), Path(dest).name
                    if any(n.casefold() == leaf.casefold() for n in root.names(parent)):
                        raise ValueError("Destination collision: " + dest)
                return ops.prepare(root, self.state / phase, moves, metadata, report, evidence_target)
            finally:
                root.close()

    def require_complete(self, phase):
        path = self.state / phase / "journal.jsonl"
        history = ops.events(path)
        if not history or history[-1]["event"] not in {"complete", "activated", "wrapper-removed"}:
            raise ValueError("Required phase is incomplete: " + phase)

    def apply_phase(self, phase, reverse=False, interrupt_after=None):
        with self.locked():
            activations = {r.get("phase") for r in self.history() if r["event"] == "activated"}
            block = {"publish-z", "publish-y", "flatten-print"} if phase in {"flatten-z", "publish-z"} else {"publish-y", "flatten-print"}
            if reverse and activations & block:
                raise ValueError("Live activation closes automatic rollback")
            if reverse:
                order = PHASES
                for later in order[order.index(phase)+1:]:
                    if (self.state / later).exists() and not any(
                            r["event"] == "rolled-back" for r in ops.events(self.state / later / "journal.jsonl")):
                        raise ValueError("Roll back later phases first")
            root = self.open_root("y" if phase in {"retain-y", "flatten-print"} else "target")
            try:
                ops.apply(root, self.state / phase, reverse, interrupt_after)
            finally:
                root.close()

    def remove_print_wrapper(self):
        with self.locked():
            root = self.open_root("y")
            try:
                ops.remove_empty_wrapper(root, self.state / "flatten-print", "Print")
            finally:
                root.close()

    def activate(self, phase):
        with self.locked():
            self.require_complete(phase)
            if phase != "flatten-print":
                scope = "z" if phase == "publish-z" else "combined"
                checks = [r for r in self.history() if r["event"] == "final-verified" and r["scope"] == scope]
                if not checks or checks[-1]["issues"]:
                    raise ValueError("Final mapped verification required before activation")
                if ops.hash_file(checks[-1]["report"]) != checks[-1]["sha256"]:
                    raise ValueError("Final verification receipt changed")
            self.event("activated", phase=phase)
            ops.append_event(self.state / phase / "journal.jsonl", {"event": "activated"})

    def final_verify(self, scope):
        with self.locked():
            if scope not in {"z", "combined"}:
                raise ValueError("Unknown final verification scope")
            self.require_complete("publish-z" if scope == "z" else "publish-y")
            target = self.open_root("target")
            try:
                receipts = []
                for role in (["z"] if scope == "z" else ["z", "y"]):
                    live = [r for r in self.history() if r["event"] == "live-baseline"] if role == "z" and scope == "combined" else []
                    if live:
                        if live[-1]["issues"] or ops.hash_file(live[-1]["report"]) != live[-1]["sha256"]:
                            raise ValueError("Failed or changed live baseline")
                        receipts.append(("Z", live[-1]["report"])); continue
                    rows = [r for r in self.history() if r["event"] == "verify-finish" and r["role"] == role]
                    if not rows or rows[-1]["issues"]:
                        raise ValueError("Missing successful staged receipt")
                    self.validate_report(rows[-1], role)
                    receipts.append((role.upper(), rows[-1]["report"]))
                name = "final-" + scope + "-" + uuid_module.uuid4().hex
                report = self.state / (name + ".jsonl")
                sealed = [quarantine.validate(target, r["seal"], self.config["prefix"])
                          for r in self.history() if r["event"] == "reconcile-finish"]
                result = verify_layout.verify(target, receipts, self.state / (name + ".sqlite"), report, sealed)
                self.event("final-verified", scope=scope, report=str(report), sha256=ops.hash_file(report), **result)
                return {"report": str(report), **result}
            finally:
                target.close()

    def check_original_z(self):
        with self.locked():
            rows = [r for r in self.history() if r["event"] == "verify-finish" and r["role"] == "z"]
            if not rows or rows[-1]["issues"]:
                raise ValueError("No successful Z copy receipt")
            self.validate_report(rows[-1], "z")
            source = self.open_root("z")
            try:
                count = 0
                with open(rows[-1]["report"], encoding="utf-8") as stream:
                    for line in stream:
                        row = json.loads(line)
                        if row["status"] != "checked":
                            continue
                        name = row["path"].removeprefix("./")
                        if name == ".":
                            value = os.fstat(source.fd)
                        else:
                            with source.parent(ops.relative(name)) as (fd, leaf):
                                value = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                        actual = [str(v) for v in (value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)]
                        if actual != row["source_generation"][1:]:
                            raise ValueError("Original Z changed after the verified copy: " + name)
                        count += 1
                self.event("original-z-unchanged", checked=count)
                return {"original_z_unchanged": True, "checked": count}
            finally:
                source.close()

    def snapshot_live_z(self):
        with self.locked():
            self.require_complete("publish-z")
            if not any(r["event"] == "activated" and r.get("phase") == "publish-z" for r in self.history()):
                raise ValueError("Live baseline is only for previously accepted/activated Z data")
            if (self.state / "publish-y").exists():
                raise ValueError("Y merge already sealed; do not replace its baseline")
            root = self.open_root("target")
            try:
                check_array(root, healthy=True)
                report = self.state / ("live-z-" + uuid_module.uuid4().hex + ".jsonl")
                result = snapshot_live.snapshot(root, report)
                self.event("live-baseline", report=str(report), sha256=ops.hash_file(report),
                           root_metadata=root.meta("."), **result)
                return {"report": str(report), **result}
            finally:
                root.close()

    def reconcile_extras(self, role):
        with self.locked():
            if (self.state / ("flatten-z" if role == "z" else "publish-y")).exists():
                raise ValueError("Staging layout already sealed for transformation")
            source, target = self.open_root(role), self.open_root("target")
            try:
                self.check_stage(target, role)
                history = self.history()
                pending = [r for r in history if r.get("role") == role and r["event"] in {"reconcile-start", "reconcile-finish"}]
                if pending and pending[-1]["event"] == "reconcile-start":
                    plan_name, prefix = pending[-1]["plan"], pending[-1]["prefix"]
                else:
                    extras = []
                    def scan(source_path, staged_path):
                        for name in target.names(staged_path):
                            if role == "y" and source_path == "." and name == "Print":
                                raise ValueError("Print in Y staging is foreign data; manual review required")
                            a = name if source_path == "." else source_path + "/" + name
                            b = staged_path + "/" + name
                            original, copied = source.info(a), target.info(b)
                            if original is None or original["kind"] != copied["kind"]:
                                extras.append((b, a))
                            elif original["kind"] == stat.S_IFDIR:
                                scan(a, b)
                    scan(".", self.stage(role))
                    if not extras:
                        return {"quarantined": 0}
                    token = uuid_module.uuid4().hex
                    plan_name = "reconcile-" + role + "-" + token
                    prefix = self.config["prefix"] + "/quarantine-" + role + "-" + token
                    def mkdirs(path):
                        current = []
                        for name in path.split("/"):
                            current.append(name)
                            rel = "/".join(current)
                            if target.info(rel) is None:
                                with target.parent(rel) as (fd, leaf):
                                    os.mkdir(leaf, mode=0o700, dir_fd=fd); os.fsync(fd)
                    mkdirs(prefix)
                    moves = []
                    for before, after in extras:
                        destination = prefix + "/" + after
                        mkdirs(str(Path(destination).parent))
                        moves.append((before, destination))
                    ops.prepare(target, self.state / plan_name, moves)
                    self.event("reconcile-start", role=role, plan=plan_name, prefix=prefix)
                ops.apply(target, self.state / plan_name)
                report = self.state / (plan_name + "-seal-" + uuid_module.uuid4().hex + ".jsonl")
                sealed = quarantine.seal(target, prefix, report)
                self.event("reconcile-finish", role=role, plan=plan_name, seal=sealed)
                # A cold copy must restore directory metadata and fill changed
                # source types before this staging generation can be verified.
                self.event("copy-start", role=role, reason="reconciliation requires a new cold final sync")
                return {"quarantined_entries": sealed["entries"], "prefix": prefix}
            finally:
                source.close(); target.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--y-root", required=True); init.add_argument("--z-root", required=True)
    init.add_argument("--target-root", required=True); init.add_argument("--target-uuid", required=True)
    init.add_argument("--session", required=True)
    copy = commands.add_parser("copy"); copy.add_argument("role", choices=["z", "y"])
    copy.add_argument("--execute", action="store_true")
    copy.add_argument("--final", action="store_true")
    copy.add_argument("--checksum-repair", action="store_true")
    check = commands.add_parser("verify"); check.add_argument("role", choices=["z", "y"])
    final = commands.add_parser("final-verify")
    final.add_argument("scope", choices=["z", "combined"])
    reconcile = commands.add_parser("reconcile-extras")
    reconcile.add_argument("role", choices=["z", "y"])
    for name in ("prepare", "apply", "rollback"):
        command = commands.add_parser(name)
        command.add_argument("phase", choices=PHASES)
    live = commands.add_parser("activate")
    live.add_argument("phase", choices=["publish-z", "publish-y", "flatten-print"])
    commands.add_parser("remove-print-wrapper")
    commands.add_parser("check-original-z")
    commands.add_parser("snapshot-live-z")
    parser.add_argument("--writers-stopped", action="store_true")
    args = parser.parse_args()
    if os.name != "posix" or os.geteuid() != 0:
        parser.error("Run as root on OMV Linux")
    if args.command not in {"init", "copy"} and not args.writers_stopped:
        parser.error("Stop affected external writers before verification or namespace changes")
    if args.command == "copy" and args.execute and args.final and not args.writers_stopped:
        parser.error("Cold final copy requires stopped external writers")
    if args.command == "init":
        if not args.target_uuid or args.target_uuid in {Y_UUID, Z_UUID}:
            parser.error("A new target array filesystem UUID is required")
        result = create_session(args.state, args.y_root, args.z_root, args.target_root, args.session,
                                [Y_UUID, Z_UUID, args.target_uuid])
    else:
        session = Session(args.state)
        if args.command == "copy": result = session.copy(args.role, args.execute, args.final, args.checksum_repair)
        elif args.command == "verify": result = session.verify_stage(args.role)
        elif args.command == "final-verify": result = session.final_verify(args.scope)
        elif args.command == "prepare": result = session.prepare_phase(args.phase)
        elif args.command in {"apply", "rollback"}:
            result = session.apply_phase(args.phase, args.command == "rollback")
        elif args.command == "activate": result = session.activate(args.phase)
        elif args.command == "check-original-z": result = session.check_original_z()
        elif args.command == "snapshot-live-z": result = session.snapshot_live_z()
        elif args.command == "reconcile-extras": result = session.reconcile_extras(args.role)
        else: result = session.remove_print_wrapper()
    print(json.dumps(result, indent=2))
    return 2 if isinstance(result, dict) and result.get("issues", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
