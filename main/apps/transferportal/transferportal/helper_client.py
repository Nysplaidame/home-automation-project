from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class HelperError(RuntimeError):
    """Raised when the root helper rejects or fails a request."""


@dataclass(frozen=True)
class HelperClient:
    helper_path: Path

    def request(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps({"action": action, "params": params}, sort_keys=True)
        command = ["sudo", "-n", str(self.helper_path)]
        result = subprocess.run(command, input=payload, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or f"helper exited {result.returncode}"
            raise HelperError(detail)
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise HelperError("helper returned invalid JSON") from exc
        if not response.get("ok"):
            raise HelperError(str(response.get("error") or "helper rejected request"))
        return response

