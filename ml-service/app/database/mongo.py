"""
MongoDB connection management and CRUD helpers.
Uses PyMongo with a module-level client (singleton pattern).
"""

from typing import Optional
from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_client: Optional[MongoClient] = None
_collection: Optional[Collection] = None


def connect_mongo() -> None:
    global _client, _collection
    try:
        _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=5000)
        _client.admin.command("ping")
        db = _client[settings.mongo_db]
        _collection = db[settings.mongo_collection]

        # Indexes for common queries
        _collection.create_index([("risk_level", ASCENDING)])
        _collection.create_index([("trust_score", ASCENDING)])
        _collection.create_index([("created_at", ASCENDING)])

        logger.info(f"MongoDB connected: {settings.mongo_uri} → {settings.mongo_db}")
    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. Running without persistence.")
        _client = None
        _collection = None


def close_mongo() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB connection closed.")


def get_collection() -> Optional[Collection]:
    return _collection


def save_prediction(record: dict) -> Optional[str]:
    """Insert a prediction record and return its string ID."""
    col = get_collection()
    if col is None:
        return None
    try:
        from datetime import datetime, timezone
        record["created_at"] = datetime.now(timezone.utc)
        result = col.insert_one(record)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Failed to save prediction: {e}")
        return None


def fetch_by_risk_level(risk_level: str, limit: int = 100) -> list[dict]:
    """Fetch predictions filtered by risk level."""
    col = get_collection()
    if col is None:
        return []
    try:
        cursor = col.find({"risk_level": risk_level}).sort("trust_score", ASCENDING).limit(limit)
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results
    except Exception as e:
        logger.error(f"Failed to fetch predictions: {e}")
        return []


def fetch_all_low_trust(threshold: int = 30, limit: int = 100) -> list[dict]:
    """Fetch all predictions below a trust score threshold."""
    col = get_collection()
    if col is None:
        return []
    try:
        cursor = (
            col.find({"trust_score": {"$lte": threshold}})
            .sort("trust_score", ASCENDING)
            .limit(limit)
        )
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results
    except Exception as e:
        logger.error(f"Failed to fetch low-trust predictions: {e}")
        return []