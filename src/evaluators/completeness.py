from src.evaluators import register_evaluator
from src.evaluators.base import BaseEvaluator
from src.models.response import CompletenessResponse
from src.models.score_enum import CompletenessScore


@register_evaluator("completeness")
class CompletenessEvaluator(BaseEvaluator):
    score_enum = CompletenessScore
    response_format = CompletenessResponse
    use_history = True
    use_fragments = True

    @property
    def system_prompt(self) -> str:
        return (
            "You are evaluating the completeness of the assistant’s answer.\n"
            "Judge whether the assistant addressed all necessary aspects of the user’s question.\n"
            "Do not consider whether the answer is factually accurate, appropriate, or grounded, assume the assistant intended to give a correct and safe answer.\n"
            "Focus only on whether the response fully covers what a complete answer should include.\n\n"
        ) + super().system_prompt
