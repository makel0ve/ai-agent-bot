from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.message import get_conversation_history
from app.repositories.message import save_message as repo_save_message


async def get_history(
    session: AsyncSession, conversation_id: int, limit: int = 20
) -> list:
    history = await get_conversation_history(
        session=session, conversation_id=conversation_id
    )

    return history[-limit:]


async def save_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    tool_name: str | None = None,
    tool_call_id: str | None = None,
    tool_arguments: str | None = None,
    content: str | None = None,
):
    result = await repo_save_message(
        session=session,
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        tool_arguments=tool_arguments,
    )

    return result


def trim_history(messages: list[dict], max_tokens: int = 4000) -> list[dict]:
    max_chars = max_tokens * 4

    def msg_len(m: dict) -> int:
        return len(m.get("content", "") or "")

    total = sum(msg_len(m) for m in messages)

    while total > max_chars and len(messages) > 2:
        candidate = messages[1]

        if (
            candidate.get("role") == "assistant"
            and (candidate.get("function_call") or candidate.get("tool_calls"))
            and len(messages) > 3
            and messages[2].get("role") in ("tool", "function")
        ):
            total -= msg_len(messages.pop(1))
            total -= msg_len(messages.pop(1))

        else:
            total -= msg_len(messages.pop(1))

    return messages
