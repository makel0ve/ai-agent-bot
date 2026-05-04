import json

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from app.config import get_settings
from app.llm.base import LLMProvider, LLMResponse, ToolCall


class OllamaProvider(LLMProvider):
    def __init__(self):
        self._settings = get_settings()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random(1, 3),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def chat(self, messages, tools=None):
        payload = {
            "model": self._settings.ollama_chat_model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url=f"{self._settings.ollama_url}/api/chat", json=payload
            )
            response.raise_for_status()

            answer = response.json()
            message = answer["message"]
            raw_tool_calls = message.get("tool_calls", [])

            if raw_tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc["function"]["name"],
                        name=tc["function"]["name"],
                        arguments=tc["function"].get("arguments", {}),
                    )
                    for tc in raw_tool_calls
                ]
                return LLMResponse(
                    content=None, tool_calls=tool_calls, finish_reason="tool_calls"
                )

            else:
                return LLMResponse(
                    content=message.get("content"), tool_calls=[], finish_reason="stop"
                )

    async def chat_stream(self, messages):
        payload = {
            "model": self._settings.ollama_chat_model,
            "messages": messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST", url=f"{self._settings.ollama_url}/api/chat", json=payload
            ) as response:
                async for line in response.aiter_lines():
                    data = json.loads(line)

                    if data.get("done"):
                        break

                    message = data.get("message")
                    if message:
                        content = message.get("content")

                        if content:
                            yield content

    def format_tool_call_message(self, tool_call: ToolCall) -> dict:
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": tool_call.name, "arguments": tool_call.arguments}}
            ],
        }

    def format_tool_result_message(self, tool_call: ToolCall, result: str) -> dict:
        return {"role": "tool", "content": result}

    def format_tools_schema(self, tools: list[dict]) -> list[dict]:
        return [{"type": "function", "function": tool} for tool in tools]

    def format_history_message(self, msg) -> dict:
        if msg.role == "assistant" and msg.tool_name:
            arguments = json.loads(msg.tool_arguments) if msg.tool_arguments else {}
            return {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": msg.tool_name, "arguments": arguments}}
                ],
            }

        if msg.role == "tool":
            return {"role": "tool", "content": msg.content or ""}

        return {"role": msg.role, "content": msg.content or ""}
