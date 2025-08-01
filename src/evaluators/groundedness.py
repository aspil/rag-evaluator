from src.evaluators import register_evaluator
from src.evaluators.base import BaseEvaluator
from src.models.response import GroundednessResponse
from src.models.score_enum import GroundednessScore


@register_evaluator("groundedness")
class GroundednessEvaluator(BaseEvaluator):
    score_enum = GroundednessScore
    response_format = GroundednessResponse
    use_history = False
    use_fragments = True

    @property
    def system_prompt(self) -> str:
        return (
            "You are evaluating the groundedness of the assistant's answer.\n"
            "Determine to what extent the answer is supported by the retrieved context fragments.\n"
            "Ignore factual correctness, clarity, or relevance, your focus is only on whether the claims made are verifiable using the provided context.\n\n"
        ) + super().system_prompt
