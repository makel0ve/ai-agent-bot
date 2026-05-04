import base64
import json
import time
import uuid

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random

from app.config import get_settings
from app.llm.base import LLMProvider, LLMResponse, ToolCall

GIGACHAT_OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1"


class GigaChatProvider(LLMProvider):
    def __init__(self):
        self.settings = get_settings()
        self._access_token = None
        self._token_expires_at = 0

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random(1, 3),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def get_token(self, force: bool = False):
        if force or self._token_expires_at - 60_000 <= round(time.time() * 1000):
            payload = "scope=GIGACHAT_API_PERS"
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
            headers["RqUID"] = str(uuid.uuid4())
            credentials = f"{self.settings.gigachat_client_id.get_secret_value()}:{self.settings.gigachat_client_secret.get_secret_value()}"
            headers["Authorization"] = (
                f"Basic {base64.b64encode(credentials.encode()).decode()}"
            )

            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    url=GIGACHAT_OAUTH_URL, headers=headers, data=payload
                )
                response.raise_for_status()

            answer = response.json()
            self._access_token = answer["access_token"]
            self._token_expires_at = answer["expires_at"]

            return answer["access_token"]

        return self._access_token

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_random(1, 3),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def chat(self, messages, tools=None):
        try:
            token = await self.get_token(force=False)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                token = await self.get_token(force=True)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers["Authorization"] = f"Bearer {token}"
        payload = {"model": "GigaChat-2-Max", "messages": messages, "stream": False}
        if tools:
            payload["function_call"] = "auto"
            payload["functions"] = tools

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                url=f"{GIGACHAT_API_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        answer = response.json()

        finish_reason = answer["choices"][0]["finish_reason"]
        message = answer["choices"][0]["message"]

        if finish_reason == "function_call":
            function_call = message["function_call"]
            tool_calls = [
                ToolCall(
                    id=function_call.get("name", ""),
                    name=function_call.get("name"),
                    arguments=json.loads(function_call["arguments"])
                    if isinstance(function_call["arguments"], str)
                    else function_call["arguments"],
                )
            ]

            return LLMResponse(
                content=None, tool_calls=tool_calls, finish_reason=finish_reason
            )

        else:
            return LLMResponse(
                content=message["content"], tool_calls=[], finish_reason=finish_reason
            )

    async def chat_stream(self, messages):
        try:
            token = await self.get_token(force=False)

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                token = await self.get_token(force=True)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers["Authorization"] = f"Bearer {token}"
        payload = {"model": "GigaChat-2-Max", "messages": messages, "stream": True}

        async with httpx.AsyncClient(verify=False) as client:
            async with client.stream(
                "POST",
                url=f"{GIGACHAT_API_URL}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data = line[len("data: ") :]
                    if data == "[DONE]":
                        break

                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")

                    if content:
                        yield content

    def format_tool_call_message(self, tool_call: ToolCall) -> dict:
        return {
            "role": "assistant",
            "content": "",
            "function_call": {"name": tool_call.name, "arguments": tool_call.arguments},
        }

    def format_tool_result_message(self, tool_call: ToolCall, result: str) -> dict:
        return {
            "role": "function",
            "name": tool_call.name,
            "content": json.dumps({"result": result}, ensure_ascii=False),
        }

    def format_tools_schema(self, tools: list[dict]) -> list[dict]:
        return tools

    def format_history_message(self, msg) -> dict:
        if msg.role == "assistant" and msg.tool_name:
            arguments = json.loads(msg.tool_arguments) if msg.tool_arguments else {}
            return {
                "role": "assistant",
                "content": "",
                "function_call": {"name": msg.tool_name, "arguments": arguments},
            }

        if msg.role == "tool":
            return {
                "role": "function",
                "name": msg.tool_name,
                "content": json.dumps({"result": msg.content}, ensure_ascii=False)
                if msg.content
                else "{}",
            }

        return {"role": msg.role, "content": msg.content or ""}
