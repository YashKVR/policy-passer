import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
import uvicorn

from backend.main import app


class QuietServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        return


@pytest.fixture
def api_base(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    database = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(database))
    port = _free_port()
    server = QuietServer(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    _wait_until_ready(base)
    monkeypatch.setenv("API_BASE", base)
    yield base
    server.should_exit = True
    thread.join(timeout=5)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


OK = 200


def _wait_until_ready(base: str) -> None:
    for _ in range(50):
        try:
            response = httpx.get(f"{base}/api/health", timeout=0.2)
        except httpx.HTTPError:
            time.sleep(0.05)
            continue
        if response.status_code == OK:
            return
        time.sleep(0.05)
    message = "The check API did not start"
    raise RuntimeError(message)
