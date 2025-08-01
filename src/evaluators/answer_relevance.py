from src.evaluators import register_evaluator
from src.evaluators.base import BaseEvaluator
from src.models.response import AnswerRelevanceResponse
from src.models.score_enum import AnswerRelevanceScore


@register_evaluator("answer_relevance")
class AnswerRelevanceEvaluator(BaseEvaluator):
    """
    Evaluates how relevant the assistant's answer is to the user query, considering the retrieved context.
    """

    score_enum = AnswerRelevanceScore
    response_format = AnswerRelevanceResponse
    use_history = False
    use_fragments = False

    @property
    def system_prompt(self) -> str:
        return (
            "You are a judge assessing how relevant the assistant’s answer is to the user’s question only.\n\n"
            "Evaluate how directly and effectively the answer addresses the user's information need, based on the content provided.\n\n"
        ) + super().system_prompt
