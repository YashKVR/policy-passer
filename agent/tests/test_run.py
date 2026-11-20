import httpx
import pytest

from agent.run import run


def test_run_reports_backend_health(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, timeout: int) -> httpx.Response:
        assert url == "http://127.0.0.1:8000/api/health"
        assert timeout == 10
        request = httpx.Request("GET", url)
        return httpx.Response(200, json={"status": "ok"}, request=request)

    monkeypatch.setattr("agent.run.httpx.get", fake_get)
    assert run("CHK-1001", "thread-1") == {
        "check_id": "CHK-1001",
        "thread_id": "thread-1",
        "status": "ok",
    }


def test_run_uses_api_base(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_get(url: str, timeout: int) -> httpx.Response:
        del timeout
        seen.append(url)
        request = httpx.Request("GET", url)
        return httpx.Response(200, json={"status": "ok"}, request=request)

    monkeypatch.setenv("API_BASE", "http://api.test")
    monkeypatch.setattr("agent.run.httpx.get", fake_get)
    assert run("CHK-1001", "thread-1")["status"] == "ok"
    assert seen == ["http://api.test/api/health"]
