import httpx

from app.config import get_settings
from app.tools.base import Tool

settings = get_settings()


class CurrencyTool(Tool):
    name = "convert_currency"
    description = "Конвертировать сумму из одной валюты в другую по текущему курсу"
    parameters = {
        "type": "object",
        "properties": {
            "to_currency": {
                "type": "string",
                "description": "Конечная валюта",
            },
            "from_currency": {
                "type": "string",
                "description": "Изначальная валюта",
            },
            "amount": {"type": "integer", "description": "Количество начальной валюты"},
        },
        "required": ["amount"],
    }

    async def execute(
        self, amount: int, from_currency: str = "RUB", to_currency: str = "USD"
    ) -> str:
        url = (
            "https://v6.exchangerate-api.com/v6/"
            f"{settings.exchangerate_api_key.get_secret_value()}/pair/{from_currency}/{to_currency}/{amount}"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url)
                response.raise_for_status()

                result = response.json()
                answer = (
                    f"{amount} {from_currency} = {result['conversion_result']} {to_currency} "
                    f"(курс: 1 {from_currency} = {result['conversion_rate']} {to_currency})"
                )

                return answer

        except Exception as exc:
            return f"Ошибка конвертации из одной валюты в другую: {exc}"
