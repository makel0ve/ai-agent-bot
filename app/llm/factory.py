from app.llm.gigachat import GigaChatProvider
from app.llm.ollama import OllamaProvider
from app.llm.yandex import YandexGPTProvider

_providers = {
    "gigachat": GigaChatProvider(),
    "yandexgpt": YandexGPTProvider(),
    "ollama": OllamaProvider(),
}


def get_llm_provider(provider_name: str):
    provider = _providers.get(provider_name)

    if not provider:
        raise ValueError(f"Неизвестный провайдер: {provider_name}")

    return provider
