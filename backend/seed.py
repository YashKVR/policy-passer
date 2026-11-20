import json
from pathlib import Path
from typing import cast

from backend.records import CheckRecord

DATA = Path(__file__).resolve().parents[1] / "data"


def load_checks(data_dir: Path | None = None) -> list[CheckRecord]:
    root = DATA if data_dir is None else data_dir
    checks: list[CheckRecord] = []
    for path in sorted((root / "checks").glob("*.json")):
        checks.append(cast(CheckRecord, json.loads(path.read_text(encoding="utf-8"))))
    return checks


def load_instructions(data_dir: Path | None = None) -> str:
    root = DATA if data_dir is None else data_dir
    return (root / "instructions.md").read_text(encoding="utf-8")
