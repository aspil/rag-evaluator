from abc import ABC, abstractmethod
from typing import Optional, Type

from mistralai.extra import CustomPydanticModel


class BaseLLMClient(ABC):
    """
    Abstract interface for communicating with an LLM backend.
    """
    def __init__(
        self,
        model: str,
        temperature: float,
        seed: int,
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.temperature = temperature
        self.seed = seed
        self.api_key = api_key

    @abstractmethod
    def chat(self, message: str, system_prompt: str, response_format: Type[CustomPydanticModel]):
        raise NotImplementedError("Subclasses must implement the chat method")

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model}, temperature={self.temperature}, seed={self.seed})"
