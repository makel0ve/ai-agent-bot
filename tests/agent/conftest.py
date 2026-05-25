from unittest.mock import AsyncMock, MagicMock

import pytest

from app.llm.base import LLMResponse, ToolCall
from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class MockTool(Tool):
    name = "mock_tool"
    description = "Фейковый инструмент для тестов агента"
    parameters = {}

    async def execute(self, **kwargs) -> str:
        return "результат mock_tool"


@pytest.fixture
def mock_registry():
    registry = ToolRegistry()
    registry.register(MockTool())

    return registry


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.format_tools_schema.return_value = []
    llm.format_tool_call_message.return_value = {}
    llm.format_tool_result_message.return_value = {}

    return llm


@pytest.fixture
def mock_llm_with_text_response(mock_llm):
    async def stream():
        yield "Привет!"

    mock_llm.chat = AsyncMock(
        return_value=LLMResponse(tool_calls=[], finish_reason="stop")
    )
    mock_llm.chat_stream.return_value = stream()

    return mock_llm


@pytest.fixture
def mock_llm_with_tool_call(mock_llm):
    tool_call = ToolCall(id="c1", name="mock_tool", arguments={})

    async def stream():
        yield "Готово!"

    mock_llm.chat = AsyncMock(
        side_effect=[
            LLMResponse(tool_calls=[tool_call], finish_reason="tool_calls"),
            LLMResponse(tool_calls=[], finish_reason="stop"),
        ]
    )
    mock_llm.chat_stream.return_value = stream()
    
    return mock_llm
