import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.run import run
from backend.decisions import decision_error
from backend.records import CheckOut, CheckSummary, DecisionWrite, Mistake, StepOut
from backend.seed import load_instructions
from backend.store import (
    check_by_id,
    connect,
    init_db,
    insert_step,
    list_steps,
    list_summaries,
    mark_in_progress,
    save_decision,
)


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


class StepIn(BaseModel):
    message: str


class MistakeIn(BaseModel):
    mistake: str
    reason: str


class DecisionIn(BaseModel):
    outcome: str
    explanation: str
    policy_section: str
    mistakes: list[MistakeIn]


class RunIn(BaseModel):
    thread_id: str


@app.post("/api/checks/{check_id}/start", operation_id="start_check")
def start_check(check_id: str) -> CheckOut:
    """Move a waiting check to in progress."""
    with connect() as connection:
        check = _load(connection, check_id)
        if check["status"] != "waiting":
            raise HTTPException(status_code=409, detail="Check is not waiting")
        mark_in_progress(connection, check_id)
        check["status"] = "in_progress"
        return check


@app.post("/api/checks/{check_id}/steps", operation_id="add_step")
def add_step(check_id: str, body: StepIn) -> list[StepOut]:
    """Record one step while a check is in progress."""
    with connect() as connection:
        check = _load(connection, check_id)
        if check["status"] != "in_progress":
            raise HTTPException(status_code=409, detail="Check is not in progress")
        insert_step(connection, check_id, body.message)
        return list_steps(connection, check_id)


@app.get("/api/checks/{check_id}/activity", operation_id="list_activity")
def list_activity(check_id: str) -> list[StepOut]:
    """List the steps recorded for a check, in order."""
    with connect() as connection:
        _load(connection, check_id)
        return list_steps(connection, check_id)


@app.post("/api/checks/{check_id}/decision", operation_id="record_decision")
def record_decision(check_id: str, body: DecisionIn) -> CheckOut:
    """Store the outcome of an in-progress check."""
    mistakes = [
        Mistake(mistake=item.mistake, reason=item.reason) for item in body.mistakes
    ]
    error = decision_error(
        body.outcome, body.explanation, body.policy_section, mistakes
    )
    if error is not None:
        raise HTTPException(status_code=422, detail=error)
    with connect() as connection:
        check = _load(connection, check_id)
        if check["status"] != "in_progress":
            raise HTTPException(status_code=409, detail="Check is not in progress")
        save_decision(
            connection,
            check_id,
            DecisionWrite(
                outcome=body.outcome,
                explanation=body.explanation,
                policy_section=body.policy_section,
                mistakes=mistakes,
            ),
        )
        check["status"] = "decided"
        check["outcome"] = body.outcome
        check["explanation"] = body.explanation
        check["policy_section"] = body.policy_section
        check["mistakes"] = mistakes
        return check


@app.post("/api/checks/{check_id}/run", operation_id="run_check")
def run_check(check_id: str, body: RunIn) -> CheckOut:
    """Decide one waiting check."""
    with connect() as connection:
        check = _load(connection, check_id)
        if check["status"] != "waiting":
            raise HTTPException(status_code=409, detail="Check is not waiting")
    return run(check_id, body.thread_id)


def _load(connection: sqlite3.Connection, check_id: str) -> CheckOut:
    check = check_by_id(connection, check_id)
    if check is None:
        raise HTTPException(status_code=404, detail="Check not found")
    return check
