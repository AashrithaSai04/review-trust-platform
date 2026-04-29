"""
Trust Score Service — converts model output into a human-readable trust score.
"""

from app.config import settings


def calibrate_probability(fake_probability: float, verified_purchase: bool = False) -> float:
    """
    Apply lightweight calibration before trust/risk mapping.

    Verified-purchase reviews receive a small downward adjustment so they are
    less likely to be over-flagged when text alone appears promotional.
    """
    bounded = max(0.0, min(1.0, float(fake_probability)))
    if not verified_purchase:
        return bounded

    adjusted = bounded - settings.verified_review_probability_discount
    return max(0.0, min(1.0, adjusted))


def calculate_trust_score(fake_probability: float) -> int:
    """
    Convert fake_probability [0, 1] → trust_score [0, 100].

    A higher fake_probability → lower trust score.
    Uses a non-linear (sigmoid-like) curve so moderate probabilities
    don't cluster around 50.
    """
    trust = int(round((1.0 - fake_probability) * 100))
    return max(0, min(92, trust))


def get_risk_level(fake_probability: float) -> str:
    """
    Map fake_probability to a risk tier.

    Thresholds are configurable via environment variables.
    """
    if fake_probability >= settings.high_risk_threshold:
        return "High Risk"
    elif fake_probability >= settings.medium_risk_threshold:
        return "Medium Risk"
    else:
        return "Low Risk"


def build_trust_result(fake_probability: float, verified_purchase: bool = False) -> dict:
    """Convenience: returns trust_score + risk_level together."""
    effective_probability = calibrate_probability(
        fake_probability=fake_probability,
        verified_purchase=verified_purchase,
    )

    return {
        "effective_fake_probability": round(effective_probability, 4),
        "trust_score": calculate_trust_score(effective_probability),
        "risk_level": get_risk_level(effective_probability),
    }