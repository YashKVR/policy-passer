import os

import httpx
from langchain_core.tools import tool

DEFAULT_API_BASE = "http://127.0.0.1:8000"


@tool
def backend_health() -> str:
    """Call the backend health route."""
    response = httpx.get(f"{_api_base()}/api/health", timeout=10)
    response.raise_for_status()
    payload = response.json()
    return str(payload["status"])


def run(check_id: str, thread_id: str) -> dict[str, str]:
    """Confirm the backend for one check and thread."""
    return {
        "check_id": check_id,
        "thread_id": thread_id,
        "status": str(backend_health.invoke({})),
    }


def _api_base() -> str:
    return os.environ.get("API_BASE", DEFAULT_API_BASE)
