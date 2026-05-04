import asyncio

from sqlalchemy import select

from app.agent.loop import agent_loop
from app.database import async_session
from app.llm.gigachat import GigaChatProvider
from app.llm.ollama import OllamaProvider
from app.llm.yandex import YandexGPTProvider
from app.models.conversation import Conversation
from app.models.user import User
from app.repositories.user import create_user
from app.tools.currency import CurrencyTool
from app.tools.notes import CreateNoteTool, DeleteNoteTool, ListNoteTool
from app.tools.registry import ToolRegistry
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool

SCENARIOS = [
    "Привет, кто ты?",
    "Какая погода в Петербурге?",
    "Сколько будет 100 долларов в рублях?",
    "Запомни: купить молоко",
    "Что я просил запомнить?",
    "Какая погода в ыловрапро?",
]

PROVIDERS = [
    ("GigaChat", GigaChatProvider()),
    ("YandexGPT", YandexGPTProvider()),
    ("Ollama", OllamaProvider()),
]


async def main():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == 123456))
        user = result.scalar_one_or_none()
        if not user:
            user = await create_user(session, telegram_id=123456, username="test")
            await session.commit()

        for provider_name, llm in PROVIDERS:
            async with async_session() as session:
                # ... весь код провайдера внутри своей сессии
                print(f"\n{'#' * 60}")
                print(f"ПРОВАЙДЕР: {provider_name}")
                print(f"{'#' * 60}")

                conversation = Conversation(user_id=user.id)
                session.add(conversation)
                await session.commit()

                registry = ToolRegistry()
                registry.register(WebSearchTool())
                registry.register(WeatherTool())
                registry.register(CurrencyTool())
                registry.register(CreateNoteTool(session=session, user_id=user.id))
                registry.register(ListNoteTool(session=session, user_id=user.id))
                registry.register(DeleteNoteTool(session=session, user_id=user.id))

                for scenario in SCENARIOS:
                    print(f"\n{'=' * 60}")
                    print(f"ВОПРОС: {scenario}")
                    print(f"{'=' * 60}")

                    try:
                        async for event in agent_loop(
                            session=session,
                            user_message=scenario,
                            conversation_id=conversation.id,
                            llm_provider=llm,
                            registry=registry,
                        ):
                            if event.type == "tool_call":
                                print(
                                    f"  🔧 Вызов: {event.data['name']}({event.data['arguments']})"
                                )
                            elif event.type == "tool_result":
                                print(f"  📋 Результат: {event.data['result'][:200]}")
                            elif event.type == "text":
                                print(f"  💬 Ответ: {event.data['content']}")
                            elif event.type == "error":
                                print(f"  ❌ Ошибка: {event.data['content']}")

                        await session.commit()

                    except Exception as e:
                        print(f"  ❌ ПРОВАЙДЕР УПАЛ: {e}")
                        await session.rollback()


if __name__ == "__main__":
    asyncio.run(main())
