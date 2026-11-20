import httpx
from langchain_core.tools import BaseTool, tool


def make_tools(client: httpx.Client, check_id: str) -> list[BaseTool]:
    @tool
    def get_check() -> str:
        """Read the policy copy and the claim papers."""
        response = client.get(f"/api/checks/{check_id}")
        response.raise_for_status()
        return response.text

    @tool
    def get_instructions() -> str:
        """Read the instructions for the check."""
        response = client.get("/api/instructions")
        response.raise_for_status()
        return response.text

    @tool
    def add_step(message: str) -> str:
        """Record one step of the review."""
        response = client.post(
            f"/api/checks/{check_id}/steps",
            json={"message": message},
        )
        response.raise_for_status()
        return response.text

    @tool
    def record_decision(
        outcome: str,
        explanation: str,
        policy_section: str,
        mistakes: list[dict[str, str]],
    ) -> str:
        """Record whether the papers would be approved or rejected."""
        response = client.post(
            f"/api/checks/{check_id}/decision",
            json={
                "outcome": outcome,
                "explanation": explanation,
                "policy_section": policy_section,
                "mistakes": mistakes,
            },
        )
        response.raise_for_status()
        return response.text

    return [get_check, get_instructions, add_step, record_decision]
