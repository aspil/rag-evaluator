from src.evaluators import register_evaluator
from src.evaluators.base import BaseEvaluator
from src.models.response import ConcisenessResponse
from src.models.score_enum import ConcisenessScore


@register_evaluator("conciseness")
class ConcisenessEvaluator(BaseEvaluator):
    score_enum = ConcisenessScore
    response_format = ConcisenessResponse
    use_history = False
    use_fragments = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are evaluating the conciseness of the assistant’s answer.\n"
            "Judge whether the response is unnecessarily long, repetitive, or could be more succinct while preserving its meaning.\n"
            "Focus only on brevity and efficiency of language, ignore clarity, correctness, relevance, or tone.\n\n"
        ) + super().system_prompt
