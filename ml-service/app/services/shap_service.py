"""SHAP Service — token-level SHAP attributions for text explanations."""

from collections.abc import Callable
from typing import Any

import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Common function words that usually do not improve human interpretability.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "to", "of", "in",
    "on", "for", "at", "by", "with", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "it", "its", "this", "that", "these", "those", "i", "you", "he",
    "she", "we", "they", "me", "my", "mine", "your", "yours", "our", "ours", "their",
    "theirs", "him", "her", "them", "do", "does", "did", "not", "no", "yes", "so",
    "very", "can", "could", "would", "should", "will", "just", "only", "also",
}


def _clean_token(token: Any) -> str:
    """Normalize etokenizer artifacts into display-friendly tokens."""
    if token is None:
        return ""
    cleaned = str(token).strip()
    cleaned = cleaned.replace("##", "")  # BERT wordpiece suffix marker
    cleaned = cleaned.lstrip("Ġ")          # byte-level BPE whitespace marker
    return cleaned.strip()


def _is_valid_token(token: str) -> bool:
    """Keep informative tokens and drop punctuation/stopword artifacts."""
    if not token:
        return False

    lower = token.lower()
    if lower in STOPWORDS:
        return False

    # Keep tokens with at least one alphanumeric char and length > 1
    if len(lower) <= 1:
        return False
    return any(ch.isalnum() for ch in lower)


def compute_shap_values(
    text: str,
    predict_proba_fn: Callable[[list[str]], np.ndarray],
    tokenizer: Any,
    top_k: int = 10,
    class_index: int = 1,
) -> list[list]:
    """
    Compute token-level SHAP importance for one review.

    Args:
        text: Review text to explain.
        predict_proba_fn: Callable that accepts list[str] and returns probabilities
            shaped (N, num_classes).
        tokenizer: Hugging Face tokenizer used to build a text masker.
        top_k: Number of tokens to return.
        class_index: Class index to explain (1 = FAKE probability in this project).

    Returns:
        List of [token, normalized_abs_shap_score] sorted descending.
    """
    if not text or not isinstance(text, str):
        return []

    try:
        import shap  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("SHAP package is not installed. Install `shap` to use this method.") from exc

    if tokenizer is None:
        raise RuntimeError("Tokenizer is unavailable; cannot compute SHAP explanations.")

    masker = shap.maskers.Text(tokenizer)
    explainer = shap.Explainer(predict_proba_fn, masker)
    shap_values = explainer([text])

    values = np.array(shap_values.values)
    if values.ndim == 3:
        token_scores = values[0, :, class_index]
    elif values.ndim == 2:
        token_scores = values[0]
    else:
        raise RuntimeError(f"Unexpected SHAP values shape: {values.shape}")

    tokens = shap_values.data[0]
    pairs: list[tuple[str, float]] = []
    for tok, score in zip(tokens, token_scores):
        cleaned = _clean_token(tok)
        if _is_valid_token(cleaned):
            pairs.append((cleaned, float(abs(score))))

    if not pairs:
        return []

    max_score = max(score for _, score in pairs)
    if max_score <= 0:
        return []

    normalized = [(tok, round(score / max_score, 4)) for tok, score in pairs]
    ranked = sorted(normalized, key=lambda item: item[1], reverse=True)
    return [[tok, score] for tok, score in ranked[:top_k]]


def is_shap_available() -> bool:
    """Check if shap package is installed."""
    try:
        import shap  # noqa: F401  # type: ignore[import-not-found]
        return True
    except ImportError:
        return False