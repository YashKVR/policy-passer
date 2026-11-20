import httpx
import pytest

from agent.tests.scripted import rejection


def test_run_endpoint_rejects_with_the_stub(
    api_base: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("agent.run.build_model", rejection)
    response = httpx.post(
        f"{api_base}/api/checks/CHK-1002/run",
        json={"thread_id": "thread-1"},
        timeout=30,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "decided"
    assert body["outcome"] == "rejected"
    assert len(body["mistakes"]) == 2
    activity = httpx.get(f"{api_base}/api/checks/CHK-1002/activity", timeout=10)
    assert activity.status_code == 200
    assert activity.json()


def test_run_endpoint_rejects_a_decided_check(api_base: str) -> None:
    response = httpx.post(
        f"{api_base}/api/checks/CHK-1003/run",
        json={"thread_id": "thread-1"},
        timeout=10,
    )
    assert response.status_code == 409
