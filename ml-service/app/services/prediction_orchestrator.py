"""
Prediction Orchestrator — ties together model, trust, XAI, and DB services.
"""

from app.services.model_service import model_service
from app.services.trust_service import build_trust_result
from app.services.xai_service import explain
from app.database.mongo import save_prediction
from app.schemas.review import PredictionResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_prediction(text: str, xai_method: str = "attention") -> PredictionResponse:
    """
    Full prediction pipeline for a single review:
        1. Model inference
        2. Trust score calculation
        3. Attention-based explanation
        4. Persist to MongoDB
        5. Return structured response
    """
    # 1. Inference
    model_output = model_service.predict(text)
    fake_prob = model_output["fake_probability"]
    is_mock = model_output.get("is_mock", False)

    # 2. Trust + risk
    trust = build_trust_result(fake_prob)

    # 3. Explainability
    xai_result = explain(text=text, model_output=model_output, method=xai_method)
    important_words = xai_result.get("important_words", [])

    # 4. Persist
    record = {
        "text": text,
        "fake_probability": round(fake_prob, 4),
        "trust_score": trust["trust_score"],
        "risk_level": trust["risk_level"],
        "important_words": important_words,
        "xai_method": xai_method,
        "is_mock_prediction": is_mock,
    }
    prediction_id = save_prediction(record)

    # 5. Return
    return PredictionResponse(
        text=text,
        fake_probability=round(fake_prob, 4),
        trust_score=trust["trust_score"],
        risk_level=trust["risk_level"],
        important_words=important_words,
        prediction_id=prediction_id,
        is_mock_prediction=is_mock,
    )