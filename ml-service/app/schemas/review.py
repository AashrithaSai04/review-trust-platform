"""
Pydantic schemas for request validation and response serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Request Schemas ────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000, description="Review text to analyze")

    model_config = {"json_schema_extra": {"example": {"text": "This product is absolutely amazing!"}}}


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    method: str = Field(default="attention", description="XAI method: 'attention' | 'shap' | 'lime'")


# ── Response Schemas ───────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    text: str
    fake_probability: float = Field(..., ge=0.0, le=1.0)
    trust_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="'Low Risk' | 'Medium Risk' | 'High Risk'")
    important_words: list[list] = Field(
        default_factory=list,
        description="List of [token, score] pairs sorted by importance"
    )
    prediction_id: Optional[str] = Field(None, description="MongoDB document ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Best product ever!!!",
                "fake_probability": 0.82,
                "trust_score": 18,
                "risk_level": "High Risk",
                "important_words": [["best", 0.91], ["ever", 0.85], ["product", 0.72]],
                "prediction_id": "64abc123def456",
            }
        }
    }


class BatchSummary(BaseModel):
    total_processed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_trust_score: float
    results: list[PredictionResponse]


class ExplainResponse(BaseModel):
    text: str
    method: str
    important_words: list[list]
    explanation_note: str


class ModerationItem(BaseModel):
    id: str
    text: str
    fake_probability: float
    trust_score: int
    risk_level: str
    important_words: list[list]


class ModerationResponse(BaseModel):
    total: int
    risk_level_filter: str
    items: list[ModerationItem]