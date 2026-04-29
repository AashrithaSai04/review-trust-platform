"""
/upload — Batch CSV processing endpoint.
"""

import io
import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile, File, Query

from app.schemas.review import BatchSummary, PredictionResponse
from app.services.prediction_orchestrator import run_prediction
from app.services.xai_service import ExplainerRegistry
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

MAX_BATCH_SIZE = 500

VERIFIED_COLUMNS = [
    "verified_purchase",
    "is_verified",
    "verified",
    "amazon_verified",
]


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


def _to_bool(value) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    normalized = str(value).strip().lower()
    return normalized in {"1", "true", "yes", "y", "verified"}


def get_verified_column(df: pd.DataFrame) -> pd.Series:
    for col in VERIFIED_COLUMNS:
        if col in df.columns:
            return df[col]
    return pd.Series([False] * len(df), index=df.index)


@router.post("/upload", response_model=BatchSummary, summary="Batch process a CSV of reviews")
async def upload_csv(
    file: UploadFile = File(..., description="CSV file with a 'text' column"),
    text_column: str = Query(default="text", description="Column name containing review text"),
    xai_method: str = Query(default="attention", description="XAI method: 'attention' | 'shap' | 'lime'"),
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

    verified_series = get_verified_column(df)

    records = []
    for idx, value in texts_series.items():
        if pd.isna(value):
            continue
        records.append(
            {
                "text": str(value),
                "verified_purchase": _to_bool(verified_series.loc[idx]) if idx in verified_series.index else False,
            }
        )

    if len(records) == 0:
        raise HTTPException(status_code=422, detail="No valid text rows found in CSV.")

    if len(records) > MAX_BATCH_SIZE:
        logger.warning(f"CSV has {len(records)} rows; truncating to {MAX_BATCH_SIZE}.")
        records = records[:MAX_BATCH_SIZE]

    available = ExplainerRegistry.available()
    if xai_method not in available:
        raise HTTPException(
            status_code=422,
            detail=f"Method '{xai_method}' not available. Choose from: {available}",
        )

    logger.info(f"Processing batch of {len(records)} reviews with xai_method='{xai_method}'...")

    results: list[PredictionResponse] = []
    failed_rows = 0
    first_error: str | None = None

    for idx, record in enumerate(records, start=1):
        try:
            result = run_prediction(
                text=record["text"],
                xai_method=xai_method,
                verified_purchase=record["verified_purchase"],
            )
            results.append(result)
        except Exception as e:
            failed_rows += 1
            if first_error is None:
                first_error = str(e)
            logger.error(f"Skipping row {idx} due to error: {e}", exc_info=True)

    if not results:
        detail = "All rows failed during processing."
        if first_error:
            detail = f"{detail} First error: {first_error}"
        raise HTTPException(status_code=500, detail=detail)

    if failed_rows:
        logger.warning(
            f"Processed {len(results)} rows successfully; {failed_rows} rows failed."
        )

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