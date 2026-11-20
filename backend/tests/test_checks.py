from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.seed import load_checks, load_instructions
from backend.store import connect, database_path, init_db


def test_list_checks(client: TestClient) -> None:
    response = client.get("/api/checks")
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body] == ["CHK-1001", "CHK-1002", "CHK-1003"]
    assert [item["status"] for item in body] == ["waiting", "waiting", "decided"]
    assert "CHK-9001" not in {item["id"] for item in body}
    assert set(body[0]) == {"id", "title", "status"}


def test_get_waiting_check(client: TestClient) -> None:
    response = client.get("/api/checks/CHK-1001")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "waiting"
    assert body["mistakes"] == []
    assert "Maya Chen" in body["claim_papers"]
    assert "$480.00" in body["claim_papers"]
    assert "Emergency medical care" in body["policy_copy"]


def test_get_decided_check(client: TestClient) -> None:
    body = client.get("/api/checks/CHK-1003").json()
    assert body["outcome"] == "rejected"
    assert body["policy_section"] == "Baggage"
    assert body["mistakes"] == [
        {
            "mistake": "No police report for a theft of $300.00",
            "reason": "The policy requires a police report filed within 24 hours.",
        }
    ]


def test_held_out_check_is_not_served(client: TestClient) -> None:
    response = client.get("/api/checks/CHK-9001")
    assert response.status_code == 404


def test_instructions(client: TestClient) -> None:
    response = client.get("/api/instructions")
    assert response.status_code == 200
    assert response.json() == {"instructions": load_instructions()}


def test_load_checks_skips_evals(tmp_path: Path) -> None:
    checks = tmp_path / "checks"
    checks.mkdir()
    (checks / "CHK-1.json").write_text('{"id": "CHK-1"}', encoding="utf-8")
    evals = tmp_path / "evals"
    evals.mkdir()
    (evals / "CHK-9001.json").write_text('{"id": "CHK-9001"}', encoding="utf-8")
    assert [item["id"] for item in load_checks(tmp_path)] == ["CHK-1"]


def test_seed_does_not_duplicate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with connect() as connection:
        init_db(connection)
        init_db(connection)
        count = connection.execute("SELECT COUNT(*) FROM checks").fetchone()
    assert count is not None
    assert count[0] == 3


def test_default_database_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    assert database_path() == Path("backend/policypasser.db")
