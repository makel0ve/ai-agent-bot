from unittest.mock import AsyncMock, patch


async def test_returns_formatted_results(web_search_tool):
    fake_results = [
        {"title": "Title1", "body": "Body1", "href": "https://example.com/1"},
        {"title": "Title2", "body": "Body2", "href": "https://example.com/2"},
    ]
    with patch(
        "app.tools.web_search.asyncio.to_thread", new_callable=AsyncMock
    ) as mock_thread:
        mock_thread.return_value = fake_results
        result = await web_search_tool.execute(query="test")

    assert "Title1" in result
    assert "Body1" in result
    assert "https://example.com/1" in result


async def test_returns_nothing_found_when_empty(web_search_tool):
    with patch(
        "app.tools.web_search.asyncio.to_thread", new_callable=AsyncMock
    ) as mock_thread:
        mock_thread.return_value = []
        result = await web_search_tool.execute(query="blablabla")

    assert "Ничего не найдено" in result


async def test_returns_error_message_on_exception(web_search_tool):
    with patch(
        "app.tools.web_search.asyncio.to_thread", side_effect=Exception("network error")
    ):
        result = await web_search_tool.execute(query="fail")

    assert "Ошибка" in result


async def test_result_is_truncated_to_2000_chars(web_search_tool):
    fake_results = [{"title": "T", "body": "x" * 3000, "href": "https://example.com"}]
    with patch(
        "app.tools.web_search.asyncio.to_thread", new_callable=AsyncMock
    ) as mock_thread:
        mock_thread.return_value = fake_results
        result = await web_search_tool.execute(query="big")

    assert len(result) <= 2000
