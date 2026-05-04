from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.currency import CurrencyTool
from app.tools.notes import CreateNoteTool, DeleteNoteTool, ListNoteTool
from app.tools.registry import ToolRegistry
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool


def create_registry(
    session: AsyncSession | None = None, user_id: int | None = None
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(WebSearchTool())
    registry.register(WeatherTool())
    registry.register(CurrencyTool())

    if session and user_id:
        registry.register(CreateNoteTool(session=session, user_id=user_id))
        registry.register(ListNoteTool(session=session, user_id=user_id))
        registry.register(DeleteNoteTool(session=session, user_id=user_id))

    return registry
