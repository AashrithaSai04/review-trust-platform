"""
XAI Service — attention-based word importance extraction.

Architecture is designed so SHAP/LIME can be plugged in later
via the ExplainerRegistry without changing the API layer.
"""

import re
import numpy as np
from app.config import settings
from app.services.model_service import model_service
from app.services.shap_service import compute_shap_values, is_shap_available
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Tokens to filter out of explanations
SPECIAL_TOKENS = {"[CLS]", "[SEP]", "[PAD]", "[UNK]", "<s>", "</s>"}
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "to", "of", "in",
    "on", "for", "at", "by", "with", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "it", "its", "this", "that", "these", "those", "i", "you", "he",
    "she", "we", "they", "me", "my", "mine", "your", "yours", "our", "ours", "their",
    "theirs", "him", "her", "them", "do", "does", "did", "not", "no", "yes", "so",
    "very", "can", "could", "would", "should", "will", "just", "only", "also", "any",
}


def _is_meaningful_token(token: str) -> bool:
    """Keep tokens that are informative and not common stopwords."""
    if not token or not re.search(r"[A-Za-z0-9]", token):
        return False

    normalized = token.lower().strip()
    if normalized in STOPWORDS:
        return False

    # Keep single-char tokens only if they are numeric (e.g., rating stars like "3")
    if len(normalized) == 1 and not normalized.isdigit():
        return False

    return True


def extract_important_words(
    tokens: list[str],
    attention_weights: list[float],
    top_k: int = None,
) -> list[list]:
    """
    Extract top-k most attended tokens and their normalized importance scores.

    Args:
        tokens: Tokenizer output tokens (including special tokens)
        attention_weights: Per-token attention scores (from CLS row)
        top_k: Number of top tokens to return (defaults to settings.top_k_attention_tokens)

    Returns:
        List of [token, score] pairs sorted by score descending.
    """
    if top_k is None:
        top_k = settings.top_k_attention_tokens

    if len(tokens) != len(attention_weights):
        logger.warning("Token/attention length mismatch — truncating to min length.")
        min_len = min(len(tokens), len(attention_weights))
        tokens = tokens[:min_len]
        attention_weights = attention_weights[:min_len]

    # Filter special tokens, sub-word markers, punctuation artifacts, and stopwords.
    filtered = []
    for tok, score in zip(tokens, attention_weights):
        clean_tok = tok.replace("##", "").strip()
        if tok in SPECIAL_TOKENS or tok.startswith("["):
            continue
        if not _is_meaningful_token(clean_tok):
            continue
        filtered.append((clean_tok, float(score)))

    if not filtered:
        return []

    # Merge duplicate tokens by keeping the maximum attention score per token.
    merged_by_token: dict[str, tuple[str, float]] = {}
    for tok, score in filtered:
        key = tok.lower()
        current = merged_by_token.get(key)
        if current is None or score > current[1]:
            merged_by_token[key] = (tok, score)

    merged = list(merged_by_token.values())

    # Normalize scores to [0, 1]
    scores = np.array([s for _, s in merged], dtype=float)
    score_max = scores.max()
    if score_max > 0:
        scores = scores / score_max

    # Sort by importance and return top-k
    ranked = sorted(
        [(tok, round(float(sc), 4)) for (tok, _), sc in zip(merged, scores)],
        key=lambda x: x[1],
        reverse=True,
    )
    return [list(pair) for pair in ranked[:top_k]]


# ── Explainer Registry ─────────────────────────────────────────────────────────
# New explainers can be registered here without touching routes or services.

class ExplainerRegistry:
    _registry: dict = {}

    @classmethod
    def register(cls, name: str):
        def decorator(fn):
            cls._registry[name] = fn
            return fn
        return decorator

    @classmethod
    def get(cls, name: str):
        return cls._registry.get(name)

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._registry.keys())


@ExplainerRegistry.register("attention")
def attention_explainer(text: str, model_output: dict, top_k: int = None) -> dict:
    """Attention-based explanation (available now)."""
    important_words = extract_important_words(
        tokens=model_output["tokens"],
        attention_weights=model_output["attention_weights"],
        top_k=top_k,
    )
    return {
        "method": "attention",
        "important_words": important_words,
        "explanation_note": (
            "Token importance derived from averaged attention weights across all "
            "DistilBERT layers and heads (CLS token attending to each input token)."
        ),
    }


@ExplainerRegistry.register("shap")
def shap_explainer(text: str, model_output: dict, top_k: int = None) -> dict:
    """SHAP-based explanation (fully implemented when `shap` is installed)."""
    if top_k is None:
        top_k = settings.top_k_attention_tokens

    if not is_shap_available():
        return {
            "method": "shap",
            "important_words": [],
            "explanation_note": (
                "SHAP package is not installed in this environment. "
                "Install `shap` in ml-service to enable SHAP explanations."
            ),
        }

    model_service.load()
    if model_service._tokenizer is None:
        return {
            "method": "shap",
            "important_words": [],
            "explanation_note": (
                "Tokenizer/model unavailable. SHAP requires the trained transformer model "
                "to be loaded successfully."
            ),
        }

    important_words = compute_shap_values(
        text=text,
        predict_proba_fn=model_service.predict_proba,
        tokenizer=model_service._tokenizer,
        top_k=top_k,
        class_index=1,
    )

    return {
        "method": "shap",
        "important_words": important_words,
        "explanation_note": (
            "Token importance derived from SHAP values for the FAKE class probability. "
            "Scores are absolute SHAP contributions normalized to [0, 1]."
        ),
    }


@ExplainerRegistry.register("lime")
def lime_explainer(text: str, model_output: dict, top_k: int = None) -> dict:
    """
    LIME-based explanation — placeholder for future integration.

    To implement:
        pip install lime
        explainer = LimeTextExplainer(class_names=["REAL", "FAKE"])
        exp = explainer.explain_instance(text, predict_fn, num_features=top_k)
        # Extract lime feature importances
    """
    return {
        "method": "lime",
        "important_words": [],
        "explanation_note": (
            "LIME integration is scaffolded but not yet implemented. "
            "Install `lime` and implement the lime_explainer function in xai_service.py."
        ),
    }


def explain(text: str, model_output: dict, method: str = "attention", top_k: int = None) -> dict:
    """
    Dispatch explanation request to the appropriate registered explainer.

    Args:
        text: Raw review text
        model_output: Output dict from model_service.predict()
        method: One of 'attention', 'shap', 'lime'
        top_k: Number of important words to return

    Returns:
        Explanation dict with 'method', 'important_words', 'explanation_note'
    """
    explainer_fn = ExplainerRegistry.get(method)
    if explainer_fn is None:
        available = ExplainerRegistry.available()
        raise ValueError(f"Unknown explainer '{method}'. Available: {available}")

    return explainer_fn(text=text, model_output=model_output, top_k=top_k)