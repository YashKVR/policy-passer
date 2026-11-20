import os
import sqlite3
from pathlib import Path

from backend.records import CheckOut, CheckRecord, CheckSummary, DecisionWrite, StepOut
from backend.seed import load_checks

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    policy_copy TEXT NOT NULL,
    claim_papers TEXT NOT NULL,
    outcome TEXT NOT NULL,
    explanation TEXT NOT NULL,
    policy_section TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mistakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_id TEXT NOT NULL,
    mistake TEXT NOT NULL,
    reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    message TEXT NOT NULL
);
"""


def database_path() -> Path:
    return Path(os.environ.get("DATABASE_PATH", "backend/policypasser.db"))


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(database_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    for check in load_checks():
        found = connection.execute(
            "SELECT id FROM checks WHERE id = ?", (check["id"],)
        ).fetchone()
        if found is None:
            _insert_check(connection, check)
    connection.commit()


def list_summaries(connection: sqlite3.Connection) -> list[CheckSummary]:
    rows = connection.execute(
        "SELECT id, title, status FROM checks ORDER BY id"
    ).fetchall()
    return [
        CheckSummary(id=row["id"], title=row["title"], status=row["status"])
        for row in rows
    ]


def check_by_id(connection: sqlite3.Connection, check_id: str) -> CheckOut | None:
    row = connection.execute(
        "SELECT * FROM checks WHERE id = ?", (check_id,)
    ).fetchone()
    if row is None:
        return None
    mistakes = connection.execute(
        "SELECT mistake, reason FROM mistakes WHERE check_id = ? ORDER BY id",
        (check_id,),
    ).fetchall()
    return CheckOut(
        id=row["id"],
        title=row["title"],
        status=row["status"],
        policy_copy=row["policy_copy"],
        claim_papers=row["claim_papers"],
        outcome=row["outcome"],
        explanation=row["explanation"],
        policy_section=row["policy_section"],
        mistakes=[
            {"mistake": item["mistake"], "reason": item["reason"]} for item in mistakes
        ],
    )


def list_steps(connection: sqlite3.Connection, check_id: str) -> list[StepOut]:
    rows = connection.execute(
        "SELECT message FROM steps WHERE check_id = ? ORDER BY position, id",
        (check_id,),
    ).fetchall()
    return [StepOut(message=row["message"]) for row in rows]


def mark_in_progress(connection: sqlite3.Connection, check_id: str) -> None:
    connection.execute(
        "UPDATE checks SET status = ? WHERE id = ?",
        ("in_progress", check_id),
    )


def insert_step(connection: sqlite3.Connection, check_id: str, message: str) -> None:
    row = connection.execute(
        "SELECT COALESCE(MAX(position), 0) AS position FROM steps WHERE check_id = ?",
        (check_id,),
    ).fetchone()
    position = int(row["position"]) + 1 if row is not None else 1
    connection.execute(
        "INSERT INTO steps (check_id, position, message) VALUES (?, ?, ?)",
        (check_id, position, message),
    )


def save_decision(
    connection: sqlite3.Connection,
    check_id: str,
    decision: DecisionWrite,
) -> None:
    connection.execute("DELETE FROM mistakes WHERE check_id = ?", (check_id,))
    connection.execute(
        """
        UPDATE checks
        SET status = ?, outcome = ?, explanation = ?, policy_section = ?
        WHERE id = ?
        """,
        (
            "decided",
            decision["outcome"],
            decision["explanation"],
            decision["policy_section"],
            check_id,
        ),
    )
    for mistake in decision["mistakes"]:
        connection.execute(
            "INSERT INTO mistakes (check_id, mistake, reason) VALUES (?, ?, ?)",
            (check_id, mistake["mistake"], mistake["reason"]),
        )


def _insert_check(connection: sqlite3.Connection, check: CheckRecord) -> None:
    connection.execute(
        """
        INSERT INTO checks (
            id, title, status, policy_copy, claim_papers,
            outcome, explanation, policy_section
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            check["id"],
            check["title"],
            check["status"],
            check["policy_copy"],
            check["claim_papers"],
            check["outcome"],
            check["explanation"],
            check["policy_section"],
        ),
    )
    for mistake in check["mistakes"]:
        connection.execute(
            "INSERT INTO mistakes (check_id, mistake, reason) VALUES (?, ?, ?)",
            (check["id"], mistake["mistake"], mistake["reason"]),
        )
    for position, message in enumerate(check["activity"], start=1):
        connection.execute(
            "INSERT INTO steps (check_id, position, message) VALUES (?, ?, ?)",
            (check["id"], position, message),
        )
