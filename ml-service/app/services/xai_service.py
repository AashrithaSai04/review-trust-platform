"""
XAI Service — attention-based word importance extraction.

Architecture is designed so SHAP/LIME can be plugged in later
via the ExplainerRegistry without changing the API layer.
"""

import re
import numpy as np
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Tokens to filter out of explanations
SPECIAL_TOKENS = {"[CLS]", "[SEP]", "[PAD]", "[UNK]", "<s>", "</s>"}


def _is_meaningful_token(token: str) -> bool:
    """Keep tokens that contain at least one alphanumeric character."""
    return bool(re.search(r"[A-Za-z0-9]", token))


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

    # Filter special tokens, sub-word markers, and punctuation-only artifacts.
    filtered = [
        (clean_tok, score)
        for tok, score in zip(tokens, attention_weights)
        for clean_tok in [tok.replace("##", "").strip()]
        if tok not in SPECIAL_TOKENS
        and not tok.startswith("[")
        and _is_meaningful_token(clean_tok)
    ]

    if not filtered:
        return []

    # Normalize scores to [0, 1]
    scores = np.array([s for _, s in filtered], dtype=float)
    score_max = scores.max()
    if score_max > 0:
        scores = scores / score_max

    # Sort by importance and return top-k
    ranked = sorted(
        [(tok, round(float(sc), 4)) for (tok, _), sc in zip(filtered, scores)],
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
    """
    SHAP-based explanation — placeholder for future integration.

    To implement:
        pip install shap
        explainer = shap.Explainer(model_pipeline)
        shap_values = explainer([text])
        # Extract token-level SHAP values and return ranked list
    """
    return {
        "method": "shap",
        "important_words": [],
        "explanation_note": (
            "SHAP integration is scaffolded but not yet implemented. "
            "Install `shap` and implement the shap_explainer function in xai_service.py."
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