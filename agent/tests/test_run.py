import builtins
from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from agent.model import DEFAULT_MODEL, build_model, model_name
from agent.run import run
from agent.tests.scripted import ScriptedModel, rejection


def test_run_rejects_outside_the_policy_period(api_base: str) -> None:
    with _guard_evals():
        result = run("CHK-1002", "thread-1", model=rejection())
    assert result["status"] == "decided"
    assert result["outcome"] == "rejected"
    assert [item["mistake"] for item in result["mistakes"]] == [
        "Treatment is outside the policy period",
        "No receipt is attached",
    ]
    activity = httpx.get(f"{api_base}/api/checks/CHK-1002/activity", timeout=10)
    assert activity.status_code == 200
    assert activity.json() == [
        {"message": "Compared the incident date and the receipt with the policy."}
    ]


def test_run_does_not_review_a_decided_check(api_base: str) -> None:
    del api_base
    result = run("CHK-1003", "thread-3", model=ScriptedModel(responses=[]))
    assert result["status"] == "decided"
    assert result["outcome"] == "rejected"


def test_run_builds_a_model_when_none_is_passed(
    api_base: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del api_base
    monkeypatch.setattr("agent.run.build_model", rejection)
    result = run("CHK-1002", "thread-2")
    assert result["outcome"] == "rejected"


def test_model_name_uses_the_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "openrouter/free")
    assert model_name() == "openrouter/free"


def test_model_name_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_NAME", raising=False)
    assert model_name() == DEFAULT_MODEL


def test_build_model_sets_low_reasoning(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setattr("agent.model.ChatOpenAI", FakeClient)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    build_model()
    assert captured["model"] == DEFAULT_MODEL
    assert captured["reasoning_effort"] == "low"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"


def _guard_evals() -> Any:
    real_open = builtins.open

    def guard(file: object, *args: object, **kwargs: object) -> object:
        if "evals" in str(file):
            message = f"opened {file}"
            raise AssertionError(message)
        return real_open(file, *args, **kwargs)  # type: ignore[arg-type]

    return _patched_open(guard)


def _patched_open(guard: Callable[..., object]) -> Any:
    return patch("builtins.open", guard)
