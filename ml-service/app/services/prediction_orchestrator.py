"""
Prediction Orchestrator — ties together model, trust, XAI, and DB services.
"""

import re

from app.services.model_service import model_service
from app.services.trust_service import build_trust_result
from app.services.xai_service import explain
from app.database.mongo import save_prediction
from app.schemas.review import PredictionResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _risk_to_label(risk_level: str) -> str:
    return risk_level.replace(" Risk", "").strip()


def _build_feature_contributions(important_words: list[list], max_items: int = 8) -> dict[str, float]:
    merged: dict[str, tuple[str, float]] = {}
    for item in important_words:
        if not isinstance(item, list) or len(item) < 2:
            continue

        token = str(item[0]).strip()
        if not token:
            continue

        try:
            score = float(item[1])
        except (TypeError, ValueError):
            continue

        key = token.lower()
        current = merged.get(key)
        if current is None or score > current[1]:
            merged[key] = (token, score)

    ranked = sorted(merged.values(), key=lambda value: value[1], reverse=True)[:max_items]
    return {token: round(score, 4) for token, score in ranked}


def _build_important_phrases(text: str, important_words: list[list], max_phrases: int = 5) -> list[str]:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]
    if not sentences:
        return []

    phrases: list[str] = []
    for item in important_words:
        if len(phrases) >= max_phrases:
            break
        if not isinstance(item, list) or len(item) < 1:
            continue

        token = str(item[0]).strip()
        if not token:
            continue

        pattern = re.compile(re.escape(token), flags=re.IGNORECASE)
        matched_sentence = next((s for s in sentences if pattern.search(s)), None)
        if matched_sentence is None:
            continue
        if matched_sentence in phrases:
            continue
        phrases.append(matched_sentence[:180])

    return phrases


def _build_explanation(
    label: str,
    score: int,
    fake_probability: float,
    xai_method: str,
    verified_purchase: bool,
    is_mock: bool,
    feature_contributions: dict[str, float],
) -> str:
    top_features = list(feature_contributions.keys())[:3]
    signals = ", ".join(top_features) if top_features else "language patterns"
    verification_note = " Verified-purchase calibration was applied." if verified_purchase else ""
    runtime_note = " Running in mock mode, so explanation quality may be limited." if is_mock else ""

    return (
        f"{label} risk with score {score}/100. "
        f"Raw fake probability is {fake_probability:.4f}, with key signals: {signals}."
        f" XAI method: {xai_method}.{verification_note}{runtime_note}"
    ).strip()


def run_prediction(
    text: str,
    xai_method: str = "attention",
    verified_purchase: bool = False,
) -> PredictionResponse:
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
    trust = build_trust_result(fake_prob, verified_purchase=verified_purchase)

    # 3. Explainability
    xai_result = explain(text=text, model_output=model_output, method=xai_method)
    important_words = xai_result.get("important_words", [])
    feature_contributions = _build_feature_contributions(important_words)
    important_phrases = _build_important_phrases(text=text, important_words=important_words)
    score = trust["trust_score"]
    label = _risk_to_label(trust["risk_level"])
    explanation = _build_explanation(
        label=label,
        score=score,
        fake_probability=fake_prob,
        xai_method=xai_method,
        verified_purchase=verified_purchase,
        is_mock=is_mock,
        feature_contributions=feature_contributions,
    )

    # 4. Persist
    record = {
        "text": text,
        "fake_probability": round(fake_prob, 4),
        "calibrated_fake_probability": trust["effective_fake_probability"],
        "trust_score": trust["trust_score"],
        "risk_level": trust["risk_level"],
        "score": score,
        "label": label,
        "feature_contributions": feature_contributions,
        "important_phrases": important_phrases,
        "explanation": explanation,
        "important_words": important_words,
        "xai_method": xai_method,
        "verified_purchase": verified_purchase,
        "is_mock_prediction": is_mock,
    }
    prediction_id = save_prediction(record)

    # 5. Return
    return PredictionResponse(
        text=text,
        fake_probability=round(fake_prob, 4),
        calibrated_fake_probability=trust["effective_fake_probability"],
        trust_score=trust["trust_score"],
        risk_level=trust["risk_level"],
        score=score,
        label=label,
        feature_contributions=feature_contributions,
        important_phrases=important_phrases,
        explanation=explanation,
        important_words=important_words,
        xai_method=xai_method,
        verified_purchase=verified_purchase,
        prediction_id=prediction_id,
        is_mock_prediction=is_mock,
    )