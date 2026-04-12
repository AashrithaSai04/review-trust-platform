"""
Preprocessing script for Review Trust Scoring Platform.
Cleans raw CSV dataset and prepares it for training.
"""

import pandas as pd
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_PATH = Path("../data/raw_reviews.csv")
CLEANED_DATA_PATH = Path("../data/cleaned_reviews.csv")

LABEL_MAP = {"OR": 0, "CG": 1}  # OR = Original/Real, CG = Computer-Generated/Fake
MAX_SAMPLE_ROWS = 5000


def load_data(path: Path) -> pd.DataFrame:
    logger.info(f"Loading dataset from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df)} rows, columns: {list(df.columns)}")
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names."""
    rename_map = {}
    for col in df.columns:
        if col.strip().lower() in ("text_", "review_text", "review"):
            rename_map[col] = "text"
        elif col.strip().lower() in ("label_", "class"):
            rename_map[col] = "label"
        elif col.strip().lower() == "category" and "label" not in df.columns:
            rename_map[col] = "label"
    if rename_map:
        df = df.rename(columns=rename_map)
        logger.info(f"Renamed columns: {rename_map}")
    return df


def map_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Map string labels to integers."""
    if "label" in df.columns and not isinstance(df["label"], pd.DataFrame) and df["label"].dtype == object:
        df["label"] = df["label"].str.strip().map(LABEL_MAP)
        logger.info(f"Label distribution after mapping:\n{df['label'].value_counts()}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove nulls, duplicates, and invalid rows."""
    original_len = len(df)

    df = df.dropna(subset=["text", "label"])
    df = df.drop_duplicates(subset=["text"])
    df = df[df["text"].str.strip().str.len() > 10]
    df["label"] = df["label"].astype(int)
    df = df[df["label"].isin([0, 1])]

    logger.info(f"Cleaned: {original_len} → {len(df)} rows ({original_len - len(df)} removed)")
    return df.reset_index(drop=True)


def save_data(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Saved cleaned dataset to {path}")


def main():
    if not RAW_DATA_PATH.exists():
        logger.warning(f"Raw data not found at {RAW_DATA_PATH}. Generating sample data for demo...")
        generate_sample_data(RAW_DATA_PATH)

    df = load_data(RAW_DATA_PATH)
    df = rename_columns(df)
    df = map_labels(df)
    df = clean_data(df)

    if len(df) > MAX_SAMPLE_ROWS:
        df = df.sample(n=MAX_SAMPLE_ROWS, random_state=42).reset_index(drop=True)
        logger.info(f"Sampled down to {len(df)} rows for fast local training")

    save_data(df, CLEANED_DATA_PATH)
    logger.info("Preprocessing complete.")


def generate_sample_data(path: Path):
    """Generate a small sample dataset for testing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = {
        "text_": [
            "This product is absolutely amazing! Best purchase I've ever made.",
            "Terrible quality. Broke after one day. Complete waste of money.",
            "Buy this now!!! Amazing deal!! 5 stars!!! Must have!!!",
            "Good product overall, does what it says. Shipping was fast.",
            "BEST PRODUCT EVER!!! Changed my life!!! Order immediately!!!",
            "Average product. Nothing special but works as expected.",
            "I love love love this product! Buy it now you won't regret!!",
            "Decent build quality. Had a minor issue but support was helpful.",
            "DO NOT BUY. Scam product. Fake reviews everywhere on this page.",
            "Works perfectly for my needs. Would recommend to friends.",
        ],
        "label_": ["OR", "OR", "CG", "OR", "CG", "OR", "CG", "OR", "OR", "OR"],
    }
    pd.DataFrame(sample).to_csv(path, index=False)
    logger.info(f"Sample data generated at {path}")


if __name__ == "__main__":
    main()