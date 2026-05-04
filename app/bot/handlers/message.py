from aiogram import F, Router
from aiogram.types import Message

from app.agent.loop import agent_loop
from app.bot.updater import MessageUpdater
from app.constants import MODELS, TOOL_MESSAGES
from app.database import async_session
from app.llm.factory import get_llm_provider
from app.repositories.conversation import get_or_create_conversation
from app.repositories.user import get_user
from app.tools.setup import create_registry

router_message = Router()


@router_message.message(F.text)
async def handle_message(message: Message):
    async with async_session() as session:
        user = await get_user(session=session, telegram_id=message.from_user.id)
        conversation = await get_or_create_conversation(
            session=session, user_id=user.id
        )
        llm_provider = get_llm_provider(user.preferred_provider)

        registry = create_registry(session=session, user_id=user.id)

        status_message = await message.answer(
            f"{MODELS.get(user.preferred_provider)} | ⏳ Думаю..."
        )

        updater = MessageUpdater(status_message)
        await updater.start()

        try:
            full_text = ""
            async for event in agent_loop(
                session=session,
                user_message=message.text,
                conversation_id=conversation.id,
                llm_provider=llm_provider,
                registry=registry,
            ):
                if event.type == "tool_call":
                    updater.update(
                        f"{MODELS.get(user.preferred_provider)} | {TOOL_MESSAGES.get(event.data['name'], '⚙️ Обрабатываю...')}"
                    )

                elif event.type == "chat_stream":
                    full_text += event.data["chunk"]
                    updater.update(full_text, parse_mode="HTML")

                elif event.type == "error":
                    updater.update(f"❌ {event.data['content']}")

            await session.commit()

        except Exception:
            updater.update("❌ Произошла ошибка, попробуй ещё раз")

        finally:
            await updater.flush()
