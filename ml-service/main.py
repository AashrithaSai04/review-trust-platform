"""
Review Trust Scoring Platform — FastAPI ML Service
Entry point for the microservice.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.mongo import connect_mongo, close_mongo
from app.routes import predict, upload, moderation, explain   # noqa: E402
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle hooks."""
    logger.info("Starting Review Trust Scoring Platform...")
    connect_mongo()
    yield
    logger.info("Shutting down...")
    close_mongo()


app = FastAPI(
    title="Review Trust Scoring Platform",
    description="Transformer-based fake review detection with explainability and trust scoring.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ───────────────────────────────────────────────────────────
app.include_router(predict.router, prefix="/api/v1", tags=["Prediction"])
app.include_router(upload.router, prefix="/api/v1", tags=["Batch Processing"])
app.include_router(moderation.router, prefix="/api/v1", tags=["Moderation"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explainability"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Review Trust Scoring Platform", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}