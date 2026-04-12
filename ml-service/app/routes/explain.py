"""
/explain — Explainability endpoint supporting multiple XAI methods.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.review import ExplainRequest, ExplainResponse
from app.services.model_service import model_service
from app.services.xai_service import explain, ExplainerRegistry
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Get word-level importance explanation for a review",
)
async def explain_review(request: ExplainRequest) -> ExplainResponse:
    """
    Return token-level importance scores for a review using the requested XAI method.

    **Available methods**:
    - `attention` — Attention-weight-based (default, available now)
    - `shap` — SHAP-based (scaffolded, requires `shap` package)
    - `lime` — LIME-based (scaffolded, requires `lime` package)
    """
    available = ExplainerRegistry.available()
    if request.method not in available:
        raise HTTPException(
            status_code=422,
            detail=f"Method '{request.method}' not available. Choose from: {available}",
        )

    try:
        model_output = model_service.predict(request.text)
        result = explain(text=request.text, model_output=model_output, method=request.method)
    except Exception as e:
        logger.error(f"Explain failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")

    return ExplainResponse(
        text=request.text,
        method=result["method"],
        important_words=result["important_words"],
        explanation_note=result["explanation_note"],
    )


@router.get("/explain/methods", summary="List available XAI methods")
async def list_methods():
    """Return the list of registered explanation methods."""
    return {"available_methods": ExplainerRegistry.available()}