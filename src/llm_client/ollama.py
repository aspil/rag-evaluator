import json
import sys
from typing import Optional, Type

from loguru import logger
from mistralai.extra import CustomPydanticModel
from ollama import chat

from src.llm_client import register_llm_client
from src.llm_client.base import BaseLLMClient


@register_llm_client("ollama")
class OllamaClient(BaseLLMClient):
    def __init__(
        self,
        model: str,
        temperature: float,
        seed: int,
        api_key: Optional[str] = None,
    ):
        super().__init__(model, temperature, seed, api_key)

    def chat(
        self,
        message: str,
        system_prompt: str,
        response_format: Type[CustomPydanticModel],
    ) -> CustomPydanticModel:
        try:
            response = chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                model=self.model,
                options={"temperature": self.temperature, "seed": self.seed},
                format="json",
                tools=[{"parameters": response_format}],
            )

            # force score as string because sometimes the model returns integer
            raw = response.message.content
            data = json.loads(raw)

            if "score" in data and not isinstance(data["score"], str):
                data["score"] = str(data["score"])

            return response_format.model_validate(data)

        except Exception as e:
            logger.error(f"Failed to chat with Ollama or process the response: {e}")
            sys.exit(1)
