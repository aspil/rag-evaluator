from functools import cached_property

from loguru import logger
from pydantic import BaseModel

from src.llm_client.base import BaseLLMClient
from src.models.models import RAGEntry, ScoreDetail
from src.models.score_enum import BaseScoreEnum
from src.utils import format_history, format_retrieved_context


class BaseEvaluator:
    """
    Base class for all evaluation dimension classes.

    Includes shared logic for input formatting, prompt construction, score normalization,
    and evaluation logic using a plug-in LLM client.

    Subclasses must define:
    - `score_enum`: Enum with string values and `min()` / `max()` methods, which refers to the dimension's score range.
    - `response_format`: Pydantic model with `score` and `explanation` used for the LLM's output format.
    - `use_history`: Whether to include conversation history.
    - `use_fragments`: Whether to include retrieved context fragments.

    Also, each evaluator overrides the `system_prompt` property to inject
    dimension-specific instructions while leveraging shared prompt logic.
    """

    score_enum: type[BaseScoreEnum]
    response_format: type[BaseModel]
    use_history: bool
    use_fragments: bool

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def score(self, entry: RAGEntry) -> ScoreDetail:
        prompt = self.format_eval_input(entry)
        response = self.llm_client.chat(
            message=prompt,
            system_prompt=self.system_prompt,
            response_format=self.response_format,
        )
        return ScoreDetail(
            score=float(response.score),
            normalized_score=self.normalize_score(int(response.score)),
            explanation=response.explanation,
        )

    def normalize_score(self, score: int) -> float:
        return (score - self.score_enum.min()) / (self.score_enum.max() - self.score_enum.min())

    @cached_property
    def system_prompt(self) -> str:
        return (
            f"{self.input_description_prompt}"
            "Use the scale below to guide your score selection:\n"
            f"{self.response_format.model_fields['score'].description}\n\n"
            "Respond in the following JSON format (note: score must be a string):\n"
            f'{{\n  "score": "<string from {self.score_enum.min()} to {self.score_enum.max()}>",\n  "explanation": "<your reasoning>"\n}}\n\n'
            "Return only the JSON object."
        )

    @cached_property
    def input_description_prompt(self) -> str:
        input_description = [
            "You will be given:",
            "- The user’s question",
            "- The assistant’s answer",
        ]
        if self.use_history:
            input_description.append("- The conversation history")
        if self.use_fragments:
            input_description.append("- The retrieved context fragments")

        return "\n".join(input_description) + "\n\n"

    def format_eval_input(self, entry: RAGEntry) -> str:
        def format_block(title: str, content: str) -> str:
            return f"{title}:\n{content}"

        parts = [format_block("User Question", entry.current_user_question.strip())]

        if self.use_history:
            parts.append(format_block("Conversation History", format_history(entry.conversation_history)))

        if self.use_fragments:
            parts.append(format_block("Retrieved Fragments", format_retrieved_context(entry.fragment_texts)))

        parts.append(format_block("Assistant Answer", entry.assistant_answer.strip()))

        return "\n\n".join(parts)

    def __repr__(self):
        return f"{self.__class__.__name__}(llm_client={self.llm_client})"
