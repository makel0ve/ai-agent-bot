from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dotenv import load_dotenv

load_dotenv(".env.test")


@pytest.fixture(autouse=True)
def mock_settings():
    settings = MagicMock()
    settings.openweather_api_key.get_secret_value.return_value = "test_key"
    settings.exchangerate_api_key.get_secret_value.return_value = "test_key"
    settings.max_tool_calls = 5

    with patch("app.config.get_settings", return_value=settings):
        yield settings


@pytest.fixture
def mock_session():
    return AsyncMock()
