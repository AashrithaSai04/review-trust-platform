"""
SHAP Service — structured placeholder for SHAP-based explanations.

This module is intentionally separate from xai_service.py so it can
be developed and tested in isolation before being wired into the registry.

Installation:
    pip install shap transformers-interpret

Usage (once implemented):
    from app.services.shap_service import compute_shap_values
    shap_words = compute_shap_values(text, pipeline)
"""

from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


def compute_shap_values(
    text: str,
    pipeline=None,
    top_k: int = 10,
) -> list[list]:
    """
    Compute SHAP token attributions for a given review text.

    Args:
        text: Review text to explain
        pipeline: Hugging Face text-classification pipeline (inject from model_service)
        top_k: Number of top important tokens to return

    Returns:
        List of [token, shap_score] pairs sorted by absolute importance

    Implementation steps:
        1. import shap
        2. Create a masker: shap.maskers.Text(tokenizer)
        3. Create explainer: shap.Explainer(pipeline, masker)
        4. Compute: shap_values = explainer([text])
        5. Extract token-level values from shap_values[0].values
        6. Normalize and return top_k pairs
    """
    logger.warning("SHAP service is not yet implemented. Returning empty explanations.")
    return []


def is_shap_available() -> bool:
    """Check if shap package is installed."""
    try:
        import shap  # noqa: F401
        return True
    except ImportError:
        return False