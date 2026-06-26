from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_status(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print("usage: job_runner <status-path> <log-path> <command-json>", file=sys.stderr)
        return 2
    status_path = Path(args[0])
    log_path = Path(args[1])
    command = json.loads(args[2])
    if not isinstance(command, list) or not command or command[0] != "rsync":
        print("command must be an rsync argument array", file=sys.stderr)
        return 2

    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_status(status_path, {"state": "running", "pid": os.getpid(), "started_at": now(), "command": command})
    with log_path.open("ab") as log_file:
        process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)

        def terminate(signum: int, _frame: object) -> None:
            if process.poll() is None:
                process.terminate()
            write_status(
                status_path,
                {
                    "state": "interrupted",
                    "pid": os.getpid(),
                    "child_pid": process.pid,
                    "signal": signum,
                    "exit_code": -signum,
                    "ended_at": now(),
                    "command": command,
                },
            )

        signal.signal(signal.SIGTERM, terminate)
        signal.signal(signal.SIGINT, terminate)
        exit_code = process.wait()

    state = "completed" if exit_code == 0 else "failed"
    if exit_code < 0:
        state = "interrupted"
    write_status(
        status_path,
        {
            "state": state,
            "pid": os.getpid(),
            "child_pid": process.pid,
            "exit_code": exit_code,
            "ended_at": now(),
            "command": command,
        },
    )
    return 0 if exit_code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

