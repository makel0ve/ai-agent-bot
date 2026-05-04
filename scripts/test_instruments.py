import asyncio

from app.database import async_session
from app.tools.currency import CurrencyTool
from app.tools.notes import CreateNoteTool, DeleteNoteTool, ListNoteTool
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool


async def main():
    print("=== Web Search ===")
    search = WebSearchTool()
    result = await search.execute(query="Python 3.12 новые возможности")
    print(result)

    print("\n=== Weather ===")
    weather = WeatherTool()
    result = await weather.execute(city="Москва")
    print(result)

    print("\n=== Weather Forecast ===")
    result = await weather.execute(city="Москва", days=3)
    print(result)

    print("\n=== Currency ===")
    currency = CurrencyTool()
    result = await currency.execute(amount=100, from_currency="USD", to_currency="RUB")
    print(result)

    print("\n=== Notes ===")
    async with async_session() as session:
        # Нужен реальный user_id из БД, используем 1 для теста
        user_id = 1

        create = CreateNoteTool(session=session, user_id=user_id)
        result = await create.execute(title="Тест", content="Тестовая заметка")
        print(f"Create: {result}")

        list_tool = ListNoteTool(session=session, user_id=user_id)
        result = await list_tool.execute()
        print(f"List: {result}")

        delete = DeleteNoteTool(session=session, user_id=user_id)
        result = await delete.execute(title="Тест")
        print(f"Delete: {result}")

        await session.commit()

    print("\n=== Schemas ===")
    for tool in [search, weather, currency, create, list_tool, delete]:
        print(f"{tool.name}: {tool.to_function_schema()}")


if __name__ == "__main__":
    asyncio.run(main())
