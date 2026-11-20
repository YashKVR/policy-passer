import os
from typing import cast

import httpx
from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage

from agent.model import build_model
from agent.tools import make_tools
from backend.records import CheckOut

DEFAULT_API_BASE = "http://127.0.0.1:8000"
CONFLICT = 409


def run(
    check_id: str,
    thread_id: str,
    model: BaseChatModel | None = None,
) -> CheckOut:
    """Review one check and store the decision."""
    with httpx.Client(base_url=_api_base(), timeout=10) as client:
        started = client.post(f"/api/checks/{check_id}/start")
        if started.status_code == CONFLICT:
            return _check(client, check_id)
        started.raise_for_status()
        chosen = build_model() if model is None else model
        agent = create_agent(
            chosen,
            make_tools(client, check_id),
            system_prompt=(
                "Decide only from the policy copy. Do not submit the papers. "
                f"This review is thread {thread_id}."
            ),
        )
        agent.invoke({"messages": [HumanMessage(content=f"Review check {check_id}.")]})
        return _check(client, check_id)


def _api_base() -> str:
    return os.environ.get("API_BASE", DEFAULT_API_BASE)


def _check(client: httpx.Client, check_id: str) -> CheckOut:
    response = client.get(f"/api/checks/{check_id}")
    response.raise_for_status()
    return cast(CheckOut, response.json())
