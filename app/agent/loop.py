import json
from enum import Enum
from typing import AsyncGenerator

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.history import get_history, save_message, trim_history
from app.agent.prompts import build_messages
from app.config import get_settings
from app.llm.base import LLMProvider
from app.tools.registry import ToolRegistry


class EventType(str, Enum):
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CHAT_STREAM = "chat_stream"
    ERROR = "error"


class AgentEvent(BaseModel):
    type: EventType
    data: dict


async def agent_loop(
    session: AsyncSession,
    user_message: str,
    conversation_id: int,
    llm_provider: LLMProvider,
    registry: ToolRegistry,
    max_steps: int | None = None,
) -> AsyncGenerator[AgentEvent, None]:
    if max_steps is None:
        max_steps = get_settings().max_tool_calls

    history = await get_history(
        session=session, conversation_id=conversation_id, limit=20
    )
    messages = build_messages(
        history=history, user_message=user_message, llm_provider=llm_provider
    )
    messages = trim_history(messages)

    await save_message(
        session=session,
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        tool_name=None,
        tool_call_id=None,
        tool_arguments=None,
    )

    for _ in range(max_steps):
        response = await llm_provider.chat(
            messages=messages,
            tools=llm_provider.format_tools_schema(registry.get_all_schemas()),
        )

        if response.tool_calls:
            for tool_call in response.tool_calls:
                yield AgentEvent(
                    type="tool_call",
                    data={"name": tool_call.name, "arguments": tool_call.arguments},
                )

                tool = registry.get(tool_call.name)
                if not tool:
                    result = f"Инструмент '{tool_call.name}' не найден"

                else:
                    try:
                        result = await tool.execute(**tool_call.arguments)

                    except Exception as exc:
                        result = f"Ошибка выполнения {tool_call.name}: {exc}"

                yield AgentEvent(
                    type="tool_result", data={"name": tool_call.name, "result": result}
                )

                messages.append(llm_provider.format_tool_call_message(tool_call))
                messages.append(
                    llm_provider.format_tool_result_message(tool_call, result)
                )

                await save_message(
                    session=session,
                    conversation_id=conversation_id,
                    role="assistant",
                    content=None,
                    tool_name=tool_call.name,
                    tool_call_id=tool_call.id,
                    tool_arguments=json.dumps(tool_call.arguments, ensure_ascii=False),
                )
                await save_message(
                    session=session,
                    conversation_id=conversation_id,
                    role="tool",
                    content=result,
                    tool_name=tool_call.name,
                    tool_call_id=tool_call.id,
                    tool_arguments=None,
                )

        else:
            full_text = ""
            async for chunk in llm_provider.chat_stream(messages=messages):
                full_text += chunk
                yield AgentEvent(type="chat_stream", data={"chunk": chunk})

            await save_message(
                session=session,
                conversation_id=conversation_id,
                role="assistant",
                content=full_text,
                tool_name=None,
                tool_call_id=None,
                tool_arguments=None,
            )
            return

    yield AgentEvent(type="error", data={"content": "Достигнут лимит шагов агента"})
