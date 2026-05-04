import json

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from app.config import get_settings
from app.llm.base import LLMProvider, LLMResponse, ToolCall

YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1"


class YandexGPTProvider(LLMProvider):
    def __init__(self):
        self._settings = get_settings()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random(1, 3),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def chat(self, messages, tools):
        headers = {
            "Content-Type": "application/json",
        }
        headers["Authorization"] = (
            f"Api-Key {self._settings.yandex_api_key.get_secret_value()}"
        )
        headers["x-folder-id"] = f"{self._settings.yandex_folder_id.get_secret_value()}"
        payload = {
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "2000",
            },
            "messages": [
                {"role": m["role"], "text": m.get("content") or m.get("text", "")}
                if "toolCallList" not in m and "toolResultList" not in m
                else m
                for m in messages
            ],
        }
        payload["modelUri"] = (
            f"gpt://{self._settings.yandex_folder_id.get_secret_value()}/yandexgpt/rc"
        )
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{YANDEX_API_URL}/completion", headers=headers, json=payload
            )
            response.raise_for_status()

        answer = response.json()
        message = answer["result"]["alternatives"][0]["message"]
        tool_call_list = message.get("toolCallList", "")

        if tool_call_list:
            raw_tool_calls = tool_call_list.get("toolCalls", [])
            tool_calls = [
                ToolCall(
                    id=tool_call["functionCall"].get("name", ""),
                    name=tool_call["functionCall"]["name"],
                    arguments=tool_call["functionCall"].get("arguments", {}),
                )
                for tool_call in raw_tool_calls
            ]

            return LLMResponse(
                content=None, tool_calls=tool_calls, finish_reason="tool_calls"
            )

        else:
            return LLMResponse(
                content=message["text"], tool_calls=[], finish_reason="stop"
            )

    async def chat_stream(self, messages):
        headers = {
            "Content-Type": "application/json",
        }
        headers["Authorization"] = (
            f"Api-Key {self._settings.yandex_api_key.get_secret_value()}"
        )
        payload = {
            "completionOptions": {
                "stream": True,
                "temperature": 0.3,
                "maxTokens": "2000",
            },
            "messages": [{"role": m["role"], "text": m["content"]} for m in messages],
        }
        payload["modelUri"] = (
            f"gpt://{self._settings.yandex_folder_id.get_secret_value()}/yandexgpt/rc"
        )

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url=f"{YANDEX_API_URL}/completion",
                headers=headers,
                json=payload,
            ) as response:
                text_pass = ""
                async for line in response.aiter_lines():
                    data = json.loads(line)
                    text_current = data["result"]["alternatives"][0]["message"]["text"][
                        len(text_pass) :
                    ]
                    text_pass += text_current

                    yield text_current

    def format_tool_call_message(self, tool_call: ToolCall) -> dict:
        return {
            "role": "assistant",
            "text": "",
            "toolCallList": {
                "toolCalls": [
                    {
                        "functionCall": {
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        }
                    }
                ]
            },
        }

    def format_tool_result_message(self, tool_call: ToolCall, result: str) -> dict:
        return {
            "role": "tool",
            "toolResultList": {
                "toolResults": [
                    {"functionCall": {"name": tool_call.name}, "content": result}
                ]
            },
        }

    def format_tools_schema(self, tools: list[dict]) -> list[dict]:
        return [{"function": tool} for tool in tools]

    def format_history_message(self, msg) -> dict:
        if msg.role == "assistant" and msg.tool_name:
            arguments = json.loads(msg.tool_arguments) if msg.tool_arguments else {}
            return {
                "role": "assistant",
                "text": "",
                "toolCallList": {
                    "toolCalls": [
                        {
                            "functionCall": {
                                "name": msg.tool_name,
                                "arguments": arguments,
                            }
                        }
                    ]
                },
            }

        if msg.role == "tool":
            return {
                "role": "tool",
                "toolResultList": {
                    "toolResults": [
                        {
                            "functionCall": {"name": msg.tool_name},
                            "content": msg.content or "",
                        }
                    ]
                },
            }

        return {"role": msg.role, "text": msg.content or ""}
