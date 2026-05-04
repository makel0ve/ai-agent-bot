from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


async def get_or_create_conversation(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.flush()

    return conversation


async def create_conversation(session: AsyncSession, user_id: int) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.flush()

    return conversation
