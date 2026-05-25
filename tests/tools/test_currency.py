from unittest.mock import AsyncMock, MagicMock, patch

import httpx

CURRENCY_RESPONSE = {
    "conversion_result": 1100.50,
    "conversion_rate": 11.005,
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


async def test_returns_conversion_result(currency_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(200, CURRENCY_RESPONSE)

    with patch("app.tools.currency.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await currency_tool.execute(
            amount=100, from_currency="USD", to_currency="RUB"
        )

    assert "100" in result
    assert "USD" in result
    assert "RUB" in result
    assert "1100.5" in result


async def test_uses_default_currencies(currency_tool):
    mock_client = AsyncMock()
    mock_client.get.return_value = make_response(200, CURRENCY_RESPONSE)

    with patch("app.tools.currency.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await currency_tool.execute(amount=50)

    assert "RUB" in result
    assert "USD" in result


async def test_returns_error_message_on_exception(currency_tool):
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("connection timeout")

    with patch("app.tools.currency.httpx.AsyncClient") as mock_cls:
        mock_cls.return_value.__aenter__.return_value = mock_client
        result = await currency_tool.execute(amount=10)

    assert "Ошибка" in result
