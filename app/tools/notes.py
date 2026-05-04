from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.note import create_note, delete_note, get_notes
from app.tools.base import Tool


class CreateNoteTool(Tool):
    name = "create_note"
    description = "Создать заметку для пользователя"
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Заголовок заметки"},
            "content": {"type": "string", "description": "Содержимое заметки"},
        },
        "required": ["title", "content"],
    }

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def execute(self, title: str, content: str) -> str:
        note = await create_note(
            session=self.session, user_id=self.user_id, title=title, content=content
        )

        return f"Заметка '{note.title}' создана"


class ListNoteTool(Tool):
    name = "list_notes"
    description = "Получить все заметки пользователя"
    parameters = {"type": "object", "properties": {}, "required": []}

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def execute(self) -> str:
        notes = await get_notes(session=self.session, user_id=self.user_id)

        if not notes:
            return "У вас нет заметок"

        return "\n".join(f"- {note.title}: {note.content[:200]}" for note in notes)


class DeleteNoteTool(Tool):
    name = "delete_note"
    description = "Удалить заметку пользователя"
    parameters = {
        "type": "object",
        "properties": {"title": {"type": "string", "description": "Заголовок заметки"}},
        "required": ["title"],
    }

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def execute(self, title: str) -> str:
        deleted = await delete_note(
            session=self.session, user_id=self.user_id, title=title
        )

        if deleted:
            return f"Заметка '{title}' удалена"

        return f"Заметка '{title}' не удалена"
