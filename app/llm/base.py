from abc import ABC, abstractmethod
from typing import AsyncGenerator

from pydantic import BaseModel


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = []
    finish_reason: str


class LLMProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[dict]) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def format_tool_call_message(self, tool_call: ToolCall) -> dict:
        pass

    @abstractmethod
    def format_tool_result_message(self, tool_call: ToolCall, result: str) -> dict:
        pass

    @abstractmethod
    def format_tools_schema(self, tools: list[dict]) -> list[dict]:
        pass

    @abstractmethod
    def format_history_message(self, msg) -> dict:
        pass
