from typing import Any, Self

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedModel(BaseChatModel):
    responses: list[AIMessage]
    cursor: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> Self:
        del tools, kwargs
        return self

    def _generate(
        self,
        messages: list[Any],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        del messages, stop, run_manager, kwargs
        message = self.responses[self.cursor]
        self.cursor += 1
        return ChatResult(generations=[ChatGeneration(message=message)])


def rejection() -> ScriptedModel:
    return ScriptedModel(
        responses=[
            _call("get_check", {}, "1"),
            _call("get_instructions", {}, "2"),
            _call(
                "add_step",
                {
                    "message": (
                        "Compared the incident date and the receipt with the policy."
                    )
                },
                "3",
            ),
            _call(
                "record_decision",
                {
                    "outcome": "rejected",
                    "explanation": (
                        "Treatment on 5 Jul 2026 is outside the policy period, "
                        "and no receipt is attached. The claim would be rejected."
                    ),
                    "policy_section": "Emergency medical care",
                    "mistakes": [
                        {
                            "mistake": "Treatment is outside the policy period",
                            "reason": (
                                "The policy covers treatment only from "
                                "1 Jun 2026 through 30 Jun 2026."
                            ),
                        },
                        {
                            "mistake": "No receipt is attached",
                            "reason": "The policy requires an itemized receipt.",
                        },
                    ],
                },
                "4",
            ),
            AIMessage(content="Decision recorded."),
        ]
    )


def _call(name: str, args: dict[str, object], call_id: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args, "id": call_id, "type": "tool_call"}],
    )
