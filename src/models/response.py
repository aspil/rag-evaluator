from pydantic import BaseModel, Field

from src.constants import SCORE_DESCRIPTIONS
from src.models.score_enum import (
    AnswerRelevanceScore,
    ClarityScore,
    CompletenessScore,
    ConcisenessScore,
    GroundednessScore,
    HarmfulnessScore,
)


class AnswerRelevanceResponse(BaseModel):
    explanation: str = Field(
        ...,
        description="Reasoning explaining the relevance of the assistant's answer to the user question.",
    )
    score: AnswerRelevanceScore = Field(..., description=SCORE_DESCRIPTIONS["answer_relevance"])


class ClarityResponse(BaseModel):
    explanation: str = Field(
        ..., description="Reasoning describing how clear and understandable the assistant's answer is."
    )
    score: ClarityScore = Field(..., description=SCORE_DESCRIPTIONS["clarity"])


class CompletenessResponse(BaseModel):
    explanation: str = Field(..., description="Reasoning explaining how complete the assistant's answer is.")
    score: CompletenessScore = Field(..., description=SCORE_DESCRIPTIONS["completeness"])


class ConcisenessResponse(BaseModel):
    explanation: str = Field(..., description="Reasoning describing how concise the assistant's answer is.")
    score: ConcisenessScore = Field(..., description=SCORE_DESCRIPTIONS["conciseness"])


class GroundednessResponse(BaseModel):
    explanation: str = Field(
        ..., description="Reasoning explaining how well the assistant's answer is supported by the retrieved context."
    )
    score: GroundednessScore = Field(..., description=SCORE_DESCRIPTIONS["groundedness"])


class HarmfulnessResponse(BaseModel):
    explanation: str = Field(
        ...,
        description="Explain whether the assistant's answer violates any safety, ethical, or content guidelines, and why.",
    )
    score: HarmfulnessScore = Field(..., description=SCORE_DESCRIPTIONS["harmfulness"])
