"""Keep import-time app initialization away from real service paths/secrets."""
import os
import tempfile
from pathlib import Path

_test_state = tempfile.TemporaryDirectory(prefix="transferportal-tests-")
_config = Path(_test_state.name) / "config.yaml"
_config.write_text(
    f"database_path: {Path(_test_state.name).as_posix()}/jobs.sqlite\n",
    encoding="utf-8",
)
_old_config = os.environ.get("TRANSFERPORTAL_CONFIG")
_old_secret = os.environ.get("TRANSFERPORTAL_SESSION_SECRET")
os.environ["TRANSFERPORTAL_CONFIG"] = str(_config)
os.environ["TRANSFERPORTAL_SESSION_SECRET"] = "isolated-tests-only-" + "x" * 48


def pytest_unconfigure(config):
    for name, value in (("TRANSFERPORTAL_CONFIG", _old_config), ("TRANSFERPORTAL_SESSION_SECRET", _old_secret)):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    _test_state.cleanup()
