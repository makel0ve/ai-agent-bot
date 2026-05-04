from abc import ABC, abstractmethod


class Tool(ABC):
    name: str
    description: str
    parameters: dict

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Выполняет вызов функции, возвращает ответ
        """

    def to_function_schema(self) -> dict:
        """
        Конвертирует данные в формат function calling для LLM
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
