"""
/predict — Single review prediction endpoint.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.review import ReviewRequest, PredictionResponse
from app.services.prediction_orchestrator import run_prediction
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, summary="Predict single review")
async def predict(request: ReviewRequest) -> PredictionResponse:
    """
    Analyze a single review text and return:
    - **fake_probability**: likelihood the review is fake (0–1)
    - **trust_score**: human-readable trust score (0–100)
    - **risk_level**: Low / Medium / High Risk
    - **important_words**: top tokens driving the prediction
    """
    try:
        result = run_prediction(text=request.text, xai_method="attention")
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")