from backend.records import Mistake

READY_TO_SUBMIT = "ready to submit"


def decision_error(
    outcome: str,
    explanation: str,
    policy_section: str,
    mistakes: list[Mistake],
) -> str | None:
    if outcome not in {"approved", "rejected"}:
        return "Outcome must be approved or rejected"
    if outcome == "rejected":
        return _rejection_error(explanation, policy_section, mistakes)
    if mistakes:
        return "An approval has no mistakes"
    if READY_TO_SUBMIT not in explanation.lower():
        return "An approval must say the papers are ready to submit"
    return None


def _rejection_error(
    explanation: str,
    policy_section: str,
    mistakes: list[Mistake],
) -> str | None:
    if mistakes and explanation.strip() and policy_section.strip():
        return None
    return "A rejection needs the mistakes, the explanation, and the policy section"
