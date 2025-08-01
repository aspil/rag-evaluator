from enum import Enum


class BaseScoreEnum(str, Enum):
    @classmethod
    def min(cls) -> int:
        return int(min(cls, key=lambda e: int(e.value)))
    @classmethod
    def max(cls) -> int:
        return int(max(cls, key=lambda e: int(e.value)))


class AnswerRelevanceScore(BaseScoreEnum):
    no_relevance = "0"
    low_relevance = "1"
    medium_relevance = "2"
    high_relevance = "3"


class ClarityScore(BaseScoreEnum):
    very_unclear = "1"
    unclear = "2"
    average = "3"
    clear = "4"
    very_clear = "5"


class CompletenessScore(BaseScoreEnum):
    incomplete = "0"
    partially_complete = "1"
    complete = "2"


class ConcisenessScore(BaseScoreEnum):
    verbose = "-2"
    slightly_wordy = "-1"
    appropriate = "0"
    concise = "1"
    very_concise = "2"


class GroundednessScore(BaseScoreEnum):
    hallucinated = "0"
    partially_grounded = "1"
    fully_grounded = "2"


class HarmfulnessScore(BaseScoreEnum):
    harmful = "0"
    questionable = "1"
    safe = "2"
