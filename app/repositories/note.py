from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


async def create_note(
    session: AsyncSession, user_id: int, title: str, content: str
) -> Note:
    note = Note(user_id=user_id, title=title, content=content)

    session.add(note)
    await session.flush()

    return note


async def get_notes(session: AsyncSession, user_id: int) -> list[Note]:
    results = await session.execute(
        select(Note).where(Note.user_id == user_id).order_by(Note.created_at.asc())
    )
    notes = results.scalars().all()

    return notes


async def delete_note(session: AsyncSession, user_id: int, title: str) -> bool:
    result = await session.execute(
        delete(Note).where(Note.user_id == user_id, Note.title == title)
    )

    return result.rowcount > 0


async def get_notes_count(session: AsyncSession, user_id: int) -> int:
    result = await session.execute(
        select(func.count(Note.id)).where(Note.user_id == user_id)
    )

    total_note = result.scalar()

    return total_note
