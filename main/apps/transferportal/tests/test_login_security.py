from fastapi.testclient import TestClient
from transferportal.app import create_app


def test_login_rejects_cross_origin_and_originless_requests(monkeypatch):
    monkeypatch.setenv("TRANSFERPORTAL_ADMIN_PASSWORD", "test-password")
    with TestClient(create_app()) as client:
        for headers in ({}, {"Origin": "https://attacker.invalid"}, {"Origin": "http://[invalid"}):
            assert client.post("/login", data={"username": "admin", "password": "test-password"}, headers=headers).status_code == 403


def test_login_throttles_failures_and_success_clears_counter(monkeypatch):
    monkeypatch.setenv("TRANSFERPORTAL_ADMIN_PASSWORD", "test-password")
    with TestClient(create_app(), headers={"Origin": "http://testserver"}) as client:
        assert client.post("/login", data={"username": "admin", "password": "bad"}).status_code == 401
        assert client.post("/login", data={"username": "admin", "password": "test-password"}, follow_redirects=False).status_code == 303
        for _ in range(5):
            assert client.post("/login", data={"username": "admin", "password": "bad"}).status_code == 401
        response = client.post("/login", data={"username": "admin", "password": "bad"})
        assert response.status_code == 429
        assert response.headers["Retry-After"] == "300"
