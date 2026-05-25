from unittest.mock import AsyncMock, MagicMock, patch


async def test_create_note_returns_confirmation(create_note_tool):
    note_mock = MagicMock()
    note_mock.title = "Тестовая заметка"

    with patch("app.tools.notes.create_note", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = note_mock
        result = await create_note_tool.execute(
            title="Тестовая заметка", content="Содержимое"
        )

    assert "Тестовая заметка" in result
    assert "создана" in result


async def test_list_notes_returns_all_titles(list_note_tool):
    note1, note2 = MagicMock(), MagicMock()
    note1.title, note1.content = "Заметка 1", "Текст первой"
    note2.title, note2.content = "Заметка 2", "Текст второй"

    with patch("app.tools.notes.get_notes", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [note1, note2]
        result = await list_note_tool.execute()

    assert "Заметка 1" in result
    assert "Заметка 2" in result


async def test_list_notes_returns_message_when_empty(list_note_tool):
    with patch("app.tools.notes.get_notes", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        result = await list_note_tool.execute()

    assert "нет заметок" in result


async def test_delete_existing_note_returns_confirmation(delete_note_tool):
    with patch("app.tools.notes.delete_note", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        result = await delete_note_tool.execute(title="Старая заметка")

    assert "удалена" in result
    assert "Старая заметка" in result


async def test_delete_missing_note_returns_not_deleted(delete_note_tool):
    with patch("app.tools.notes.delete_note", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = False
        result = await delete_note_tool.execute(title="Несуществующая")

    assert "не удалена" in result
