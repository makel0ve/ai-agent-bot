import asyncio

from app.llm.gigachat import GigaChatProvider
from app.llm.ollama import OllamaProvider
from app.llm.yandex import YandexGPTProvider

TEST_TOOLS_GIGACHAT = [
    {
        "name": "get_weather",
        "description": "Получить текущую погоду в указанном городе",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Название города"}
            },
            "required": ["city"],
        },
    }
]

TEST_TOOLS_OLLAMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Получить текущую погоду в указанном городе",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города"}
                },
                "required": ["city"],
            },
        },
    }
]

TEST_TOOLS_YANDEX = [
    {
        "function": {
            "name": "get_weather",
            "description": "Получить текущую погоду в указанном городе",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Название города"}
                },
                "required": ["city"],
            },
        }
    }
]

MESSAGES_TOOL = [{"role": "user", "content": "Какая погода в Москве?"}]
MESSAGES_TEXT = [{"role": "user", "content": "Привет, как дела?"}]


async def test_provider(name, provider, tools):
    print(f"\n{'=' * 50}")
    print(f"Тестируем: {name}")
    print(f"{'=' * 50}")

    print("\n--- Запрос с tool call ---")
    response = await provider.chat(MESSAGES_TOOL, tools=tools)
    print(f"finish_reason: {response.finish_reason}")
    print(f"tool_calls: {response.tool_calls}")
    print(f"content: {response.content}")

    print("\n--- Запрос без tool call ---")
    response = await provider.chat(MESSAGES_TEXT, tools=tools)
    print(f"finish_reason: {response.finish_reason}")
    print(f"tool_calls: {response.tool_calls}")
    print(f"content: {response.content}")


async def main():
    await test_provider("GigaChat", GigaChatProvider(), TEST_TOOLS_GIGACHAT)
    await test_provider("YandexGPT", YandexGPTProvider(), TEST_TOOLS_YANDEX)
    await test_provider("Ollama", OllamaProvider(), TEST_TOOLS_OLLAMA)


if __name__ == "__main__":
    asyncio.run(main())
