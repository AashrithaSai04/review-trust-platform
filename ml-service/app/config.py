"""
Centralized configuration for the ML service.
All environment variables are read here.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Settings:
    # Model
    model_dir: str = os.getenv(
        "MODEL_DIR",
        str(Path(__file__).resolve().parents[2] / "ml-pipeline" / "models" / "distilbert-review-classifier"),
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

    # Trust Score thresholds (fake_probability ranges)
    high_risk_threshold: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.7"))
    medium_risk_threshold: float = float(os.getenv("MEDIUM_RISK_THRESHOLD", "0.4"))

    # XAI
    top_k_attention_tokens: int = int(os.getenv("TOP_K_TOKENS", "10"))


settings = Settings()