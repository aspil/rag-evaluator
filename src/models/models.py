import json
import os
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from src.constants import REQUIRED_COLUMNS
from src.llm_client import LLM_CLIENT_REGISTRY


class RAGEntry(BaseModel):
    current_user_question: str
    conversation_history: Optional[str] = None
    fragment_texts: str
    assistant_answer: str


class ScoreDetail(BaseModel):
    score: float
    normalized_score: float
    explanation: str


class EvaluationResult(BaseModel):
    scores: dict[str, ScoreDetail]
    composite: float


class EvaluationConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    csv: pd.DataFrame = Field(..., description="Path to input CSV")
    model_provider: str = Field(
        default="ollama",
        description=f"Provider of the Large Language Model judge. Currently implemented clients: {list(LLM_CLIENT_REGISTRY.keys())}",
    )
    model_name: str = Field(..., description="Name of the model")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="Temperature for the model")
    seed: int = Field(default=42, description="Random seed for reproducibility")
    api_key: Optional[str] = Field(None, description="API key for the model provider")

    @field_validator("csv", mode="before")
    def validate_csv(cls, v: str) -> pd.DataFrame:
        if not v.endswith(".csv"):
            raise ValueError(f"Invalid file extension: {v}")
        if not os.path.exists(v):
            raise FileNotFoundError(f"CSV file not found: {v}")
        try:
            df = pd.read_csv(v)
        except Exception as e:
            raise ValueError(f"Failed to load CSV: {e}")

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        return df

    @field_validator("model_provider")
    def validate_model_provider(cls, v: str):
        if v not in ["mistral", "ollama"]:
            raise ValueError(f"Invalid model provider: {v}")
        return v

    @field_validator("api_key")
    def validate_api_key(cls, v: Optional[str], info: ValidationInfo):
        # Only check api key for mistral, if other providers require api key they should be added in the list below.
        api_requiring_providers = ["mistral"]
        if info.data["model_provider"] in api_requiring_providers:
            if v is None:
                v = os.getenv("API_KEY")
                if not v:
                    raise ValueError(
                        f"{info.data['model_provider']} requires an API key. Please provide it via command line or API_KEY environment variable."
                    )
            return v

        return None
