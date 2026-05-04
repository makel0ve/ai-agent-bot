import asyncio

from ddgs import DDGS

from app.tools.base import Tool


class WebSearchTool(Tool):
    name = "web_search"
    description = "Поиск актуальной информации в интернете. Используй когда нужны свежие данные, новости, факты, которых ты можешь не знать."
    parameters = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "Поисковый запрос"}},
        "required": ["query"],
    }

    async def execute(self, query: str) -> str:
        try:
            results = await asyncio.to_thread(DDGS().text, query, max_results=5)

        except Exception as exc:
            return f"Ошибка поиска: {exc}"

        if not results:
            return "Ничего не найдено"

        formatted = []
        for result in results:
            formatted.append(f"{result['title']}\n{result['body']}\n{result['href']}")

        return "\n\n".join(formatted)[:2000]
