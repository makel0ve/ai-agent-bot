import pytest

from app.tools.currency import CurrencyTool
from app.tools.notes import CreateNoteTool, DeleteNoteTool, ListNoteTool
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool


@pytest.fixture
def weather_tool():
    return WeatherTool()


@pytest.fixture
def currency_tool():
    return CurrencyTool()


@pytest.fixture
def web_search_tool():
    return WebSearchTool()


@pytest.fixture
def create_note_tool(mock_session):
    return CreateNoteTool(session=mock_session, user_id=1)


@pytest.fixture
def list_note_tool(mock_session):
    return ListNoteTool(session=mock_session, user_id=1)


@pytest.fixture
def delete_note_tool(mock_session):
    return DeleteNoteTool(session=mock_session, user_id=1)
