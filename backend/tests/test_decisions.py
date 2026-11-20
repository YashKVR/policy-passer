from fastapi.testclient import TestClient

APPROVED = {
    "outcome": "approved",
    "explanation": (
        "The incident is inside the policy period and the receipt is attached. "
        "The papers are ready to submit."
    ),
    "policy_section": "Emergency medical care",
    "mistakes": [],
}


def test_start_moves_a_waiting_check(client: TestClient) -> None:
    first = client.post("/api/checks/CHK-1001/start")
    assert first.status_code == 200
    assert first.json()["status"] == "in_progress"
    assert client.post("/api/checks/CHK-1001/start").status_code == 409


def test_step_is_stored_in_order(client: TestClient) -> None:
    client.post("/api/checks/CHK-1001/start")
    created = client.post(
        "/api/checks/CHK-1001/steps",
        json={"message": "Read the policy copy."},
    )
    assert created.status_code == 200
    listed = client.get("/api/checks/CHK-1001/activity")
    assert listed.json() == [{"message": "Read the policy copy."}]
    seeded = client.get("/api/checks/CHK-1003/activity").json()
    assert [item["message"] for item in seeded] == [
        "Read the baggage section of the policy.",
        "Checked the papers for a police report filed within 24 hours.",
    ]


def test_step_on_a_decided_check_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/checks/CHK-1003/steps",
        json={"message": "Look again."},
    )
    assert response.status_code == 409


def test_step_requires_a_message(client: TestClient) -> None:
    client.post("/api/checks/CHK-1001/start")
    assert client.post("/api/checks/CHK-1001/steps", json={}).status_code == 422


def test_rejection_without_mistakes_stays_in_progress(client: TestClient) -> None:
    client.post("/api/checks/CHK-1001/start")
    response = client.post(
        "/api/checks/CHK-1001/decision",
        json={
            "outcome": "rejected",
            "explanation": "The papers are incomplete.",
            "policy_section": "Emergency medical care",
            "mistakes": [],
        },
    )
    assert response.status_code == 422
    assert client.get("/api/checks/CHK-1001").json()["status"] == "in_progress"


def test_approval_must_say_the_papers_are_ready(client: TestClient) -> None:
    client.post("/api/checks/CHK-1001/start")
    response = client.post(
        "/api/checks/CHK-1001/decision",
        json={
            "outcome": "approved",
            "explanation": "The receipt is attached.",
            "policy_section": "Emergency medical care",
            "mistakes": [],
        },
    )
    assert response.status_code == 422


def test_approval_is_stored(client: TestClient) -> None:
    client.post("/api/checks/CHK-1001/start")
    response = client.post("/api/checks/CHK-1001/decision", json=APPROVED)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "decided"
    assert body["outcome"] == "approved"
    assert "ready to submit" in body["explanation"]


def test_rejection_is_stored(client: TestClient) -> None:
    client.post("/api/checks/CHK-1002/start")
    response = client.post(
        "/api/checks/CHK-1002/decision",
        json={
            "outcome": "rejected",
            "explanation": (
                "Treatment falls outside the policy period and no receipt is attached. "
                "The claim would be rejected."
            ),
            "policy_section": "Emergency medical care",
            "mistakes": [
                {
                    "mistake": "Treatment is outside the policy period",
                    "reason": "Coverage ends on 30 Jun 2026.",
                },
                {
                    "mistake": "No receipt is attached",
                    "reason": "The policy requires an itemized receipt.",
                },
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "decided"
    assert len(body["mistakes"]) == 2


def test_blank_rejection_fields_are_rejected(client: TestClient) -> None:
    client.post("/api/checks/CHK-1002/start")
    for payload in (
        {
            "outcome": "rejected",
            "explanation": "   ",
            "policy_section": "Emergency medical care",
            "mistakes": [
                {"mistake": "Missing receipt", "reason": "A receipt is required."}
            ],
        },
        {
            "outcome": "rejected",
            "explanation": "The receipt is missing.",
            "policy_section": " ",
            "mistakes": [
                {"mistake": "Missing receipt", "reason": "A receipt is required."}
            ],
        },
        {
            "outcome": "maybe",
            "explanation": "The papers are ready to submit.",
            "policy_section": "Emergency medical care",
            "mistakes": [],
        },
        {
            "outcome": "approved",
            "explanation": "The papers are ready to submit.",
            "policy_section": "Emergency medical care",
            "mistakes": [{"mistake": "None", "reason": "None."}],
        },
    ):
        assert (
            client.post("/api/checks/CHK-1002/decision", json=payload).status_code
            == 422
        )


def test_decision_on_a_waiting_check_is_rejected(client: TestClient) -> None:
    response = client.post("/api/checks/CHK-1001/decision", json=APPROVED)
    assert response.status_code == 409


def test_missing_check_is_not_found(client: TestClient) -> None:
    assert client.post("/api/checks/CHK-404/start").status_code == 404
    assert client.get("/api/checks/CHK-404/activity").status_code == 404


def test_openapi_has_no_submit_or_pay(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    paths = " ".join(spec["paths"])
    operation_ids = [
        method["operationId"]
        for path in spec["paths"].values()
        for method in path.values()
        if isinstance(method, dict) and "operationId" in method
    ]
    assert "submit" not in paths
    assert "pay" not in paths
    assert "submit" not in " ".join(operation_ids)
    assert "pay" not in " ".join(operation_ids)
