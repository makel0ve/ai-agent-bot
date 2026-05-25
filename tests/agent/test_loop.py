from unittest.mock import AsyncMock

from app.agent.loop import EventType, agent_loop
from app.llm.base import LLMResponse, ToolCall


def make_mock_history(monkeypatch):
    mock_save = AsyncMock()
    monkeypatch.setattr("app.agent.loop.get_history", AsyncMock(return_value=[]))
    monkeypatch.setattr("app.agent.loop.save_message", mock_save)
    monkeypatch.setattr("app.agent.loop.trim_history", lambda msgs: msgs)
    monkeypatch.setattr(
        "app.agent.loop.build_messages",
        lambda history, user_message, llm_provider: [
            {"role": "user", "content": user_message}
        ],
    )

    return mock_save


async def test_direct_text_response_yields_chat_stream_event(
    mock_llm_with_text_response, mock_registry, mock_session, monkeypatch
):
    make_mock_history(monkeypatch)

    events = []
    async for event in agent_loop(
        session=mock_session,
        user_message="Привет",
        conversation_id=1,
        llm_provider=mock_llm_with_text_response,
        registry=mock_registry,
    ):
        events.append(event)

    stream_events = [e for e in events if e.type == EventType.CHAT_STREAM]
    assert len(stream_events) > 0
    assert stream_events[0].data["chunk"] == "Привет!"


async def test_tool_call_yields_tool_call_and_result_events(
    mock_llm_with_tool_call, mock_registry, mock_session, monkeypatch
):
    make_mock_history(monkeypatch)

    events = []
    async for event in agent_loop(
        session=mock_session,
        user_message="используй инструмент",
        conversation_id=1,
        llm_provider=mock_llm_with_tool_call,
        registry=mock_registry,
    ):
        events.append(event)

    types_seen = {e.type for e in events}
    assert EventType.TOOL_CALL in types_seen
    assert EventType.TOOL_RESULT in types_seen

    tool_result_event = next(e for e in events if e.type == EventType.TOOL_RESULT)
    assert tool_result_event.data["result"] == "результат mock_tool"


async def test_unknown_tool_yields_error_in_result(
    mock_llm, mock_registry, mock_session, monkeypatch
):
    make_mock_history(monkeypatch)

    tool_call = ToolCall(id="c2", name="nonexistent_tool", arguments={})

    async def stream():
        yield "Ответ"

    mock_llm.chat = AsyncMock(
        side_effect=[
            LLMResponse(tool_calls=[tool_call], finish_reason="tool_calls"),
            LLMResponse(tool_calls=[], finish_reason="stop"),
        ]
    )
    mock_llm.chat_stream.return_value = stream()

    events = []
    async for event in agent_loop(
        session=mock_session,
        user_message="вызови несуществующий",
        conversation_id=1,
        llm_provider=mock_llm,
        registry=mock_registry,
    ):
        events.append(event)

    result_events = [e for e in events if e.type == EventType.TOOL_RESULT]
    assert len(result_events) > 0
    assert "не найден" in result_events[0].data["result"]


async def test_max_steps_exceeded_yields_error_event(
    mock_llm, mock_registry, mock_session, monkeypatch
):
    make_mock_history(monkeypatch)

    tool_call = ToolCall(id="c3", name="mock_tool", arguments={})
    mock_llm.chat = AsyncMock(
        return_value=LLMResponse(tool_calls=[tool_call], finish_reason="tool_calls")
    )

    events = []
    async for event in agent_loop(
        session=mock_session,
        user_message="зациклись",
        conversation_id=1,
        llm_provider=mock_llm,
        registry=mock_registry,
        max_steps=2,
    ):
        events.append(event)

    error_events = [e for e in events if e.type == EventType.ERROR]
    assert len(error_events) == 1
    assert "лимит" in error_events[0].data["content"]


async def test_user_message_is_saved_to_db(
    mock_llm_with_text_response, mock_registry, mock_session, monkeypatch
):
    mock_save = make_mock_history(monkeypatch)

    async for _ in agent_loop(
        session=mock_session,
        user_message="сохрани меня",
        conversation_id=42,
        llm_provider=mock_llm_with_text_response,
        registry=mock_registry,
    ):
        pass

    mock_save.assert_awaited()
    first_call = mock_save.call_args_list[0].kwargs
    assert first_call["role"] == "user"
    assert first_call["content"] == "сохрани меня"
    assert first_call["conversation_id"] == 42
