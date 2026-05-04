from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message


async def get_conversation_history(session: AsyncSession, conversation_id: int):
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    return messages


async def save_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    tool_name: str | None,
    tool_call_id: str | None,
    tool_arguments: str | None = None,
    content: str | None = None,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
        tool_call_id=tool_call_id,
        tool_arguments=tool_arguments,
    )

    session.add(message)
    await session.flush()

    return message


async def get_user_message_counts(
    session: AsyncSession, user_id: int
) -> tuple[int, int]:
    result_total = await session.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user_id)
    )
    total_messages = result_total.scalar()

    result_tool_call = await session.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user_id)
        .where(Message.tool_name.isnot(None))
    )
    tool_call = result_tool_call.scalar()

    return total_messages, tool_call
