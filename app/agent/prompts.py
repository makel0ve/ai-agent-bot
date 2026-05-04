from app.constants import SYSTEM_PROMPT
from app.llm.base import LLMProvider


def build_messages(
    history: list, user_message: str, llm_provider: LLMProvider
) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in history:
        messages.append(llm_provider.format_history_message(msg))

    messages.append({"role": "user", "content": user_message})

    return messages
