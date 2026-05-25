from app.tools.base import Tool
from app.tools.registry import ToolRegistry


class FakeTool(Tool):
    name = "fake"
    description = "Фейковый инструмент для тестов"
    parameters = {}

    async def execute(self, **kwargs) -> str:
        return "ok"


class AnotherFakeTool(Tool):
    name = "fake"
    description = "Другой фейковый инструмент"
    parameters = {}

    async def execute(self, **kwargs) -> str:
        return "another"


def test_registered_tool_is_retrievable():
    registry = ToolRegistry()
    registry.register(FakeTool())
    assert registry.get("fake") is not None


def test_missing_tool_returns_none():
    registry = ToolRegistry()
    assert registry.get("nonexistent") is None


def test_schema_contains_all_registered_tools():
    registry = ToolRegistry()
    registry.register(FakeTool())
    schemas = registry.get_all_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "fake"


def test_registering_same_name_overwrites_previous():
    registry = ToolRegistry()
    registry.register(FakeTool())
    registry.register(AnotherFakeTool())
    assert registry.get("fake").description == "Другой фейковый инструмент"
