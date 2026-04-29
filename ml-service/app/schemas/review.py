"""
Pydantic schemas for request validation and response serialization.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Request Schemas ────────────────────────────────────────────────────────────

class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000, description="Review text to analyze")
    verified_purchase: bool = Field(
        default=False,
        description="Whether the review is from a verified purchase source.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "This product is absolutely amazing!",
                "verified_purchase": True,
            }
        }
    }


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    method: str = Field(default="attention", description="XAI method: 'attention' | 'shap' | 'lime'")


# ── Response Schemas ───────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    text: str
    fake_probability: float = Field(..., ge=0.0, le=1.0)
    calibrated_fake_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Effective fake probability after calibration rules"
    )
    trust_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="'Low Risk' | 'Medium Risk' | 'High Risk'")
    score: int = Field(..., ge=0, le=100, description="Human-readable score used for moderation")
    label: str = Field(..., description="Short risk label: 'Low' | 'Medium' | 'High'")
    feature_contributions: dict[str, float] = Field(
        default_factory=dict,
        description="Top token/feature contributions sorted by importance",
    )
    important_phrases: list[str] = Field(
        default_factory=list,
        description="Top contextual phrases supporting the prediction",
    )
    explanation: str = Field(..., description="Human-readable explanation summary")
    important_words: list[list] = Field(
        default_factory=list,
        description="List of [token, score] pairs sorted by importance"
    )
    xai_method: str = Field(default="attention", description="XAI method used for explanation")
    verified_purchase: bool = Field(default=False, description="Whether verified purchase calibration was applied")
    prediction_id: Optional[str] = Field(None, description="MongoDB document ID")
    is_mock_prediction: bool = Field(
        default=False,
        description="True if prediction is from fallback mock model (Torch/Transformers not available). False = real trained classifier."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "This product works great and arrived quickly!",
                "fake_probability": 0.18,
                "calibrated_fake_probability": 0.08,
                "trust_score": 82,
                "risk_level": "Low Risk",
                "score": 82,
                "label": "Low",
                "feature_contributions": {"great": 0.89, "quickly": 0.81, "product": 0.72},
                "important_phrases": [
                    "works great and arrived quickly",
                    "This product works great",
                ],
                "explanation": "Low risk with high trust due to balanced, product-specific wording.",
                "important_words": [["great", 0.89], ["quickly", 0.81], ["product", 0.72]],
                "xai_method": "attention",
                "verified_purchase": True,
                "prediction_id": "64abc123def456",
                "is_mock_prediction": False,
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