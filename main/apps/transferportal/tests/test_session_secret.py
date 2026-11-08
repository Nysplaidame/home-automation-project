from types import SimpleNamespace

import pytest

from transferportal.app import _session_secret


def test_missing_secret_fails_closed(tmp_path, monkeypatch):
    monkeypatch.delenv("TRANSFERPORTAL_SESSION_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="session secret"):
        _session_secret(SimpleNamespace(session_secret_file=tmp_path / "missing"))


@pytest.mark.parametrize("value", ["", "   ", "dev-only-change-me", "short"])
def test_weak_environment_secret_rejected(tmp_path, monkeypatch, value):
    monkeypatch.setenv("TRANSFERPORTAL_SESSION_SECRET", value)
    with pytest.raises(RuntimeError, match="session secret"):
        _session_secret(SimpleNamespace(session_secret_file=tmp_path / "missing"))


def test_empty_file_does_not_fall_back_to_environment(tmp_path, monkeypatch):
    secret_file = tmp_path / "secret"
    secret_file.write_text("\n")
    monkeypatch.setenv("TRANSFERPORTAL_SESSION_SECRET", "a" * 64)
    with pytest.raises(RuntimeError, match="session secret"):
        _session_secret(SimpleNamespace(session_secret_file=secret_file))


def test_valid_file_and_environment(tmp_path, monkeypatch):
    secret_file = tmp_path / "secret"
    config = SimpleNamespace(session_secret_file=secret_file)
    monkeypatch.setenv("TRANSFERPORTAL_SESSION_SECRET", "a" * 64)
    assert _session_secret(config) == "a" * 64
    secret_file.write_text("b" * 64 + "\n")
    assert _session_secret(config) == "b" * 64
