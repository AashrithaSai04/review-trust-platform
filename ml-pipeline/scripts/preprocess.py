"""
Preprocessing script for Review Trust Scoring Platform.
Robust version (handles multiple label formats).
"""

import pandas as pd
import logging
from pathlib import Path
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_SAMPLE_ROWS = 10000


def load_data(path):
    logger.info(f"Loading dataset from {path}")
    return pd.read_csv(path)


def rename_columns(df):
    rename_map = {}

    for col in df.columns:
        c = col.lower().strip()

        if c in ["text_", "review", "review_text"]:
            rename_map[col] = "text"

        elif c in ["label_", "class"]:
            rename_map[col] = "label"

        # ✅ IMPORTANT: use category if label is bad
        elif c == "category" and "label" not in df.columns:
            rename_map[col] = "label"

    df = df.rename(columns=rename_map)
    df = df.loc[:, ~df.columns.duplicated()]

    return df


def map_labels(df):
    if "label" not in df.columns:
        raise ValueError("No label column found")

    if isinstance(df["label"], pd.DataFrame):
        df["label"] = df["label"].iloc[:, 0]

    unique_vals = df["label"].dropna().unique()
    logger.info(f"Unique label values: {unique_vals}")

    # ✅ Case 1: already numeric
    if pd.api.types.is_numeric_dtype(df["label"]):
        logger.info("Label is numeric → using as is")
        return df

    # ✅ Case 2: OR / CG
    label_map = {
        "OR": 0, "CG": 1,
        "REAL": 0, "FAKE": 1,
        "real": 0, "fake": 1,
        "0": 0, "1": 1
    }

    df["label"] = df["label"].astype(str).str.strip().map(label_map)

    if df["label"].isnull().all():
        raise ValueError(
            f"Label mapping failed. Found values: {unique_vals}"
        )

    if df["label"].isnull().any():
        logger.warning("Some labels unmapped → dropping")

    return df.dropna(subset=["label"])


def clean_data(df):
    if "text" not in df.columns:
        raise ValueError("Column 'text' not found")

    df = df.dropna(subset=["text"])
    df = df.drop_duplicates(subset=["text"])

    df["text"] = df["text"].astype(str).str.lower().str.strip()
    df = df[df["text"].str.len() > 10]

    df["label"] = df["label"].astype(int)

    return df


def main():
    parser = argparse.ArgumentParser()

    pipeline_root = Path(__file__).resolve().parents[1]
    default_input = pipeline_root / "data" / "raw_reviews.csv"
    default_output = pipeline_root / "data" / "cleaned_reviews.csv"

    parser.add_argument("--input", default=str(default_input))
    parser.add_argument("--output", default=str(default_output))
    parser.add_argument("--sample", action="store_true")

    args = parser.parse_args()

    df = load_data(args.input)

    logger.info(f"Columns BEFORE rename: {list(df.columns)}")

    df = rename_columns(df)

    logger.info(f"Columns AFTER rename: {list(df.columns)}")

    df = map_labels(df)
    df = clean_data(df)

    if args.sample and len(df) > MAX_SAMPLE_ROWS:
        df = df.groupby("label").apply(
            lambda x: x.sample(min(len(x), MAX_SAMPLE_ROWS // 2), random_state=42)
        ).reset_index(drop=True)

        logger.info(f"Sampled dataset → {len(df)} rows")

    df.to_csv(args.output, index=False)

    logger.info(f"Saved cleaned data → {args.output}")
    logger.info(f"Final dataset size: {len(df)} rows")


if __name__ == "__main__":
    main()