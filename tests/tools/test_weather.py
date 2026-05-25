from unittest.mock import AsyncMock, MagicMock, patch

import httpx

CURRENT_WEATHER_RESPONSE = {
    "main": {"temp": 20.5, "feels_like": 18.0, "humidity": 65},
    "weather": [{"description": "облачно"}],
    "wind": {"speed": 3.5},
}

FORECAST_RESPONSE = {
    "list": [
        {
            "dt_txt": "2026-05-24 12:00:00",
            "main": {"temp": 22.0},
            "weather": [{"description": "ясно"}],
            "wind": {"speed": 2.0},
        },
        {
            "dt_txt": "2026-05-25 12:00:00",
            "main": {"temp": 19.0},
            "weather": [{"description": "дождь"}],
            "wind": {"speed": 5.0},
        },
    ]
}


def make_response(status_code: int, json_data: dict):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=resp,
        )

    else:
        resp.raise_for_status.return_value = None
        
    return resp


async def test_returns_current_weather_for_valid_city(weather_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(200, CURRENT_WEATHER_RESPONSE)

    with patch("app.tools.weather.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await weather_tool.execute(city="Москва")

    assert "Москва" in result
    assert "20.5" in result
    assert "облачно" in result


async def test_returns_error_when_city_not_found(weather_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(404, {})

    with patch("app.tools.weather.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await weather_tool.execute(city="НесуществующийГород")

    assert "не найден" in result


async def test_returns_error_on_unauthorized(weather_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(401, {})

    with patch("app.tools.weather.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await weather_tool.execute(city="Москва")

    assert "авторизации" in result


async def test_returns_error_on_rate_limit(weather_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(429, {})

    with patch("app.tools.weather.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await weather_tool.execute(city="Москва")

    assert "лимит" in result


async def test_returns_forecast_when_days_greater_than_one(weather_tool):
    mock_client = AsyncMock()
    mock_client.get.side_effect = [
        make_response(200, CURRENT_WEATHER_RESPONSE),
        make_response(200, FORECAST_RESPONSE),
    ]

    with patch("app.tools.weather.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await weather_tool.execute(city="Москва", days=2)

    assert "Прогноз" in result
    assert "2026-05-24" in result
