"""
Training script for DistilBERT-based fake review classifier.
Uses Hugging Face Transformers Trainer API.
"""

import os
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

import torch
from torch.utils.data import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_PATH = Path("../data/cleaned_reviews.csv")
MODEL_OUTPUT_DIR = Path("../models/distilbert-review-classifier")
BASE_MODEL = "distilbert-base-uncased"

# ── Config ─────────────────────────────────────────────────────────────────────
@dataclass
class TrainingConfig:
    max_length: int = 256
    batch_size: int = 8
    num_epochs: int = 1
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    test_size: float = 0.2
    seed: int = 42
    fp16: bool = torch.cuda.is_available()


# ── Dataset ────────────────────────────────────────────────────────────────────
class ReviewDataset(Dataset):
    def __init__(self, encodings: dict, labels: list):
        self.encodings = encodings
        self.labels = labels

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> dict:
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


# ── Metrics ────────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred) -> dict:
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, average="binary", zero_division=0
    )
    accuracy = accuracy_score(labels, predictions)
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


# ── Training Pipeline ──────────────────────────────────────────────────────────
def load_and_split_data(config: TrainingConfig) -> tuple:
    logger.info(f"Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    texts = df["text"].tolist()
    labels = df["label"].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=config.test_size, random_state=config.seed, stratify=labels
    )
    logger.info(f"Train: {len(X_train)} | Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def tokenize(texts: list, tokenizer, config: TrainingConfig) -> dict:
    return tokenizer(
        texts,
        truncation=True,
        padding="max_length",
        max_length=config.max_length,
        return_tensors=None,
    )


def build_trainer(
    model,
    tokenizer,
    train_dataset: ReviewDataset,
    eval_dataset: ReviewDataset,
    config: TrainingConfig,
) -> Trainer:
    args = TrainingArguments(
        output_dir=str(MODEL_OUTPUT_DIR / "checkpoints"),
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        eval_strategy="epoch",
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_dir=str(MODEL_OUTPUT_DIR / "logs"),
        logging_steps=50,
        fp16=config.fp16,
        seed=config.seed,
        report_to="none",
    )

    return Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )


def train():
    config = TrainingConfig()
    logger.info(f"Training config: {config}")

    resume_from_checkpoint = os.getenv("RESUME_FROM_CHECKPOINT", "false").lower() in ("1", "true", "yes")

    # Load data
    X_train, X_test, y_train, y_test = load_and_split_data(config)

    # Load tokenizer and model
    logger.info(f"Loading tokenizer and model: {BASE_MODEL}")
    tokenizer = DistilBertTokenizerFast.from_pretrained(BASE_MODEL)
    model = DistilBertForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=2,
        id2label={0: "REAL", 1: "FAKE"},
        label2id={"REAL": 0, "FAKE": 1},
        output_attentions=True,  # Required for XAI attention extraction
    )

    # Tokenize
    logger.info("Tokenizing datasets...")
    train_encodings = tokenize(X_train, tokenizer, config)
    test_encodings = tokenize(X_test, tokenizer, config)

    train_dataset = ReviewDataset(train_encodings, y_train)
    eval_dataset = ReviewDataset(test_encodings, y_test)

    # Train
    trainer = build_trainer(model, tokenizer, train_dataset, eval_dataset, config)
    logger.info("Starting training...")
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)

    # Evaluate
    logger.info("Evaluating on test set...")
    results = trainer.evaluate(eval_dataset)
    logger.info(f"Final evaluation results: {results}")

    # Save model and tokenizer
    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)
    logger.info(f"Model and tokenizer saved to {MODEL_OUTPUT_DIR}")

    # Save evaluation results
    results_path = MODEL_OUTPUT_DIR / "eval_results.json"
    import json
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Evaluation results saved to {results_path}")


if __name__ == "__main__":
    train()