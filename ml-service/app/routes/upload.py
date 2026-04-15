"""
/upload — Batch CSV processing endpoint.
"""

import io
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from app.schemas.review import BatchSummary, PredictionResponse
from app.services.prediction_orchestrator import run_prediction
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

MAX_BATCH_SIZE = 500


def get_text_column(df: pd.DataFrame) -> pd.Series:
    """Return the first matching text column from a CSV upload."""
    possible_cols = [
        "text",
        "review",
        "review_text",
        "summary",
        "reviews.text",
        "reviews.title",
    ]

    for col in possible_cols:
        if col in df.columns:
            return df[col]

    raise ValueError(f"No valid text column found. Available: {df.columns.tolist()}")


@router.post("/upload", response_model=BatchSummary, summary="Batch process a CSV of reviews")
async def upload_csv(
    file: UploadFile = File(..., description="CSV file with a 'text' column"),
    text_column: str = Query(default="text", description="Column name containing review text"),
) -> BatchSummary:
    """
    Upload a CSV file and get trust scores for all reviews.

    The CSV must have at least one column containing review text (default: `text`).
    Optionally set `text_column` query param to match your CSV's actual column name.

    **Limits**: Up to 500 rows per request.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    raw_bytes = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

    if text_column not in df.columns:
        try:
            texts_series = get_text_column(df)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
    else:
        texts_series = df[text_column]

    texts = texts_series.dropna().astype(str).tolist()
    if len(texts) == 0:
        raise HTTPException(status_code=422, detail="No valid text rows found in CSV.")

    if len(texts) > MAX_BATCH_SIZE:
        logger.warning(f"CSV has {len(texts)} rows; truncating to {MAX_BATCH_SIZE}.")
        texts = texts[:MAX_BATCH_SIZE]

    logger.info(f"Processing batch of {len(texts)} reviews...")

    results: list[PredictionResponse] = []
    for text in texts:
        try:
            result = run_prediction(text=text, xai_method="attention")
            results.append(result)
        except Exception as e:
            logger.error(f"Skipping row due to error: {e}")

    # ── Summary stats ──────────────────────────────────────────────────────────
    high = sum(1 for r in results if r.risk_level == "High Risk")
    medium = sum(1 for r in results if r.risk_level == "Medium Risk")
    low = sum(1 for r in results if r.risk_level == "Low Risk")
    avg_trust = round(sum(r.trust_score for r in results) / len(results), 2) if results else 0.0

    return BatchSummary(
        total_processed=len(results),
        high_risk_count=high,
        medium_risk_count=medium,
        low_risk_count=low,
        average_trust_score=avg_trust,
        results=results,
    )