from src.evaluators import register_evaluator
from src.evaluators.base import BaseEvaluator
from src.models.response import ClarityResponse
from src.models.score_enum import ClarityScore


@register_evaluator("clarity")
class ClarityEvaluator(BaseEvaluator):
    score_enum = ClarityScore
    response_format = ClarityResponse
    use_history = False
    use_fragments = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are evaluating the clarity of the assistant’s answer.\n"
            "Focus on how clearly the message is communicated, consider grammar, fluency, readability, and structural coherence.\n"
            "Disregard the factual accuracy, safety, or appropriateness of the content.\n\n"
        ) + super().system_prompt
