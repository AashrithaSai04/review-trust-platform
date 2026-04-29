"""
Centralized configuration for the ML service.
All environment variables are read here.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


def _default_model_dir() -> str:
    """Choose a sensible default model path in the repo."""
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "ml-pipeline" / "my_model",
        repo_root / "ml-pipeline" / "models" / "distilbert-review-classifier",
    ]
    for path in candidates:
        if path.exists():
            return str(path)
    return str(candidates[0])


def _default_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:5173"]


@dataclass
class Settings:
    # Model
    model_dir: str = os.getenv(
        "MODEL_DIR",
        _default_model_dir(),
    )
    max_length: int = int(os.getenv("MAX_LENGTH", "256"))
    device: str = os.getenv("DEVICE", "cpu")  # "cuda" or "cpu"

    # MongoDB
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str = os.getenv("MONGO_DB", "review_trust_db")
    mongo_collection: str = os.getenv("MONGO_COLLECTION", "predictions")

    # Service
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    cors_origins: list[str] = field(default_factory=_default_cors_origins)

    # Trust Score thresholds (fake_probability ranges)
    high_risk_threshold: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.7"))
    medium_risk_threshold: float = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.4"))
    verified_review_probability_discount: float = float(
        os.getenv("VERIFIED_REVIEW_PROBABILITY_DISCOUNT", "0.2")
    )

    # XAI
    top_k_attention_tokens: int = int(os.getenv("TOP_K_TOKENS", "10"))


settings = Settings()