import httpx

from app.config import get_settings
from app.tools.base import Tool

OPENWEATHER_URL_API = "http://api.openweathermap.org/data/2.5"
settings = get_settings()


class WeatherTool(Tool):
    name = "get_weather"
    description = "Получить текущую погоду и прогноз в указанном городе"
    parameters = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Название города"},
            "days": {
                "type": "integer",
                "description": "Количество дней прогноза (1-5)",
            },
        },
        "required": ["city"],
    }

    async def execute(self, city: str, days: int = 1) -> str:
        base_params = {
            "units": "metric",
            "lang": "ru",
            "q": city,
            "appid": settings.openweather_api_key.get_secret_value(),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f"{OPENWEATHER_URL_API}/weather",
                    params=base_params,
                )
                response.raise_for_status()
                current = response.json()

                answer = (
                    f"Погода в {city}:\n"
                    f"Сейчас: {current['main']['temp']}°C "
                    f"(ощущается {current['main']['feels_like']}°C), "
                    f"{current['weather'][0]['description']}, "
                    f"влажность {current['main']['humidity']}%, "
                    f"ветер {current['wind']['speed']} м/с"
                )

                if days > 1:
                    response = await client.get(
                        url=f"{OPENWEATHER_URL_API}/forecast",
                        params=base_params,
                    )
                    response.raise_for_status()
                    forecast = response.json()

                    daily = [d for d in forecast["list"] if "12:00:00" in d["dt_txt"]][
                        :days
                    ]
                    answer += "\n\nПрогноз:"
                    for day in daily:
                        date = day["dt_txt"].split(" ")[0]
                        answer += (
                            f"\n{date}: {day['main']['temp']}°C, "
                            f"{day['weather'][0]['description']}, "
                            f"ветер {day['wind']['speed']} м/с"
                        )

                return answer

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return "Город не найден"

            if exc.response.status_code == 401:
                return "Ошибка авторизации OpenWeatherMap"

            if exc.response.status_code == 429:
                return "Превышен лимит запросов к OpenWeatherMap"

            return f"Ошибка API погоды: {exc.response.status_code}"
