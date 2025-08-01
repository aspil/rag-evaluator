from typing import Type

from mistralai import Mistral
from mistralai.extra import CustomPydanticModel

from src.llm_client import register_llm_client
from src.llm_client.base import BaseLLMClient


@register_llm_client("mistral")
class MistralClient(BaseLLMClient):
    def __init__(
        self,
        model: str,
        temperature: float,
        seed: int,
        api_key: str,
    ):
        super().__init__(model, temperature, seed, api_key)
        assert self.api_key, "Mistral API key is required"
        self.client = Mistral(api_key=self.api_key)

    def chat(
        self,
        message: str,
        system_prompt: str,
        response_format: Type[CustomPydanticModel],
    ) -> CustomPydanticModel:
        # try:
        response = self.client.chat.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=self.temperature,
            random_seed=self.seed,
            response_format=response_format,
        )
        return response.choices[0].message.parsed
