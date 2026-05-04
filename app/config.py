from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gigachat_client_id: SecretStr
    gigachat_client_secret: SecretStr
    yandex_api_key: SecretStr
    yandex_folder_id: SecretStr
    ollama_url: str = "http://ollama:11434"
    ollama_chat_model: str = "qwen3:8b"
    llm_provider: str = "gigachat"
    database_url: SecretStr
    redis_url: str
    telegram_token: SecretStr
    openweather_api_key: SecretStr
    max_tool_calls: int = 5
    exchangerate_api_key: SecretStr | None = None
    rate_limit_requests: int = 10
    rate_limit_window: int = 60
    webhook_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
