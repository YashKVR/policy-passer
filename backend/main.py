from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from backend.records import CheckOut, CheckSummary
from backend.seed import load_instructions
from backend.store import check_by_id, connect, init_db, list_summaries


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    with connect() as connection:
        init_db(connection)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/health", operation_id="health")
def health() -> dict[str, str]:
    """Report that the backend is running."""
    return {"status": "ok"}


@app.get("/api/checks", operation_id="list_checks")
def list_checks() -> list[CheckSummary]:
    """List each check with its status."""
    with connect() as connection:
        return list_summaries(connection)


@app.get("/api/checks/{check_id}", operation_id="get_check")
def get_check(check_id: str) -> CheckOut:
    """Return one check, including its policy copy and papers."""
    with connect() as connection:
        check = check_by_id(connection, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")
    return check


@app.get("/api/instructions", operation_id="get_instructions")
def get_instructions() -> dict[str, str]:
    """Return the read-only instructions."""
    return {"instructions": load_instructions()}
