import os

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

DEFAULT_MODEL = "openai/gpt-6-luna"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"


def model_name() -> str:
    return os.environ.get("MODEL_NAME", DEFAULT_MODEL)


def build_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=model_name(),
        api_key=SecretStr(os.environ.get("OPENROUTER_API_KEY", "not-used")),
        base_url=OPENROUTER_BASE,
        reasoning_effort="low",
    )
