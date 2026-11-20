from typing import TypedDict


class Mistake(TypedDict):
    mistake: str
    reason: str


class CheckRecord(TypedDict):
    id: str
    title: str
    status: str
    policy_copy: str
    claim_papers: str
    outcome: str
    explanation: str
    policy_section: str
    mistakes: list[Mistake]
    activity: list[str]


class CheckSummary(TypedDict):
    id: str
    title: str
    status: str


class CheckOut(TypedDict):
    id: str
    title: str
    status: str
    policy_copy: str
    claim_papers: str
    outcome: str
    explanation: str
    policy_section: str
    mistakes: list[Mistake]
