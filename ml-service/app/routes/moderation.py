"""
/moderation — Fetch flagged reviews from MongoDB for human review.
"""

from fastapi import APIRouter, Query, HTTPException

from app.schemas.review import ModerationResponse, ModerationItem
from app.database.mongo import fetch_by_risk_level, fetch_all_low_trust
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

VALID_RISK_LEVELS = {"High Risk", "Medium Risk", "Low Risk"}


@router.get(
    "/moderation",
    response_model=ModerationResponse,
    summary="Fetch reviews pending moderation",
)
async def get_moderation_queue(
    risk_level: str = Query(
        default="High Risk",
        description="Risk tier to filter: 'High Risk' | 'Medium Risk' | 'Low Risk'",
    ),
    limit: int = Query(default=50, ge=1, le=500, description="Max results to return"),
) -> ModerationResponse:
    """
    Retrieve stored predictions filtered by risk level for human moderation.

    Returns reviews ordered by trust score ascending (most suspicious first).
    Requires MongoDB to be running and connected.
    """
    if risk_level not in VALID_RISK_LEVELS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid risk_level '{risk_level}'. Choose from: {sorted(VALID_RISK_LEVELS)}",
        )

    raw = fetch_by_risk_level(risk_level=risk_level, limit=limit)

    items = []
    for doc in raw:
        try:
            items.append(
                ModerationItem(
                    id=doc.get("id", ""),
                    text=doc.get("text", ""),
                    fake_probability=doc.get("fake_probability", 0.0),
                    trust_score=doc.get("trust_score", 0),
                    risk_level=doc.get("risk_level", ""),
                    important_words=doc.get("important_words", []),
                )
            )
        except Exception as e:
            logger.warning(f"Skipping malformed doc: {e}")

    return ModerationResponse(
        total=len(items),
        risk_level_filter=risk_level,
        items=items,
    )


@router.get(
    "/moderation/low-trust",
    response_model=ModerationResponse,
    summary="Fetch all reviews below a trust score threshold",
)
async def get_low_trust_reviews(
    threshold: int = Query(default=30, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=500),
) -> ModerationResponse:
    """
    Retrieve all stored predictions with trust_score ≤ threshold.
    Useful for bulk moderation workflows.
    """
    raw = fetch_all_low_trust(threshold=threshold, limit=limit)

    items = []
    for doc in raw:
        try:
            items.append(
                ModerationItem(
                    id=doc.get("id", ""),
                    text=doc.get("text", ""),
                    fake_probability=doc.get("fake_probability", 0.0),
                    trust_score=doc.get("trust_score", 0),
                    risk_level=doc.get("risk_level", ""),
                    important_words=doc.get("important_words", []),
                )
            )
        except Exception as e:
            logger.warning(f"Skipping malformed doc: {e}")

    return ModerationResponse(
        total=len(items),
        risk_level_filter=f"trust_score ≤ {threshold}",
        items=items,
    )