"""
Training script for DistilBERT fake review classifier.
LOCAL COLAB VERSION (epochs fixed to 2).
"""

import logging
import pandas as pd
import numpy as np
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PIPELINE_ROOT / "data" / "cleaned_reviews.csv"
MODEL_DIR = PIPELINE_ROOT / "my_model"


@dataclass
class Config:
    max_length: int = 256
    batch_size: int = 8
    epochs: int = 2   # ✅ FIXED AS YOU SAID
    lr: float = 2e-5


class ReviewDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)

    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    acc = accuracy_score(labels, preds)

    return {"accuracy": acc, "f1": f1}


def train():
    cfg = Config()

    logger.info(f"Loading data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        stratify=df["label"],
        random_state=42
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame({"text": X_test, "label": y_test}).to_csv(
        MODEL_DIR / "test_data.csv",
        index=False
    )

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=2
    )

    train_enc = tokenizer(
        list(X_train),
        truncation=True,
        padding=True,
        max_length=cfg.max_length
    )

    test_enc = tokenizer(
        list(X_test),
        truncation=True,
        padding=True,
        max_length=cfg.max_length
    )

    train_ds = ReviewDataset(train_enc, list(y_train))
    test_ds = ReviewDataset(test_enc, list(y_test))

    args = TrainingArguments(
        output_dir=str(MODEL_DIR / "checkpoints"),
        per_device_train_batch_size=cfg.batch_size,
        per_device_eval_batch_size=cfg.batch_size,
        num_train_epochs=cfg.epochs,

        eval_strategy="steps",
        eval_steps=200,
        save_steps=200,

        save_total_limit=2,
        load_best_model_at_end=True,
        logging_steps=50,
        fp16=torch.cuda.is_available(),
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(2)]
    )

    logger.info("Starting training...")
    trainer.train()

    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    logger.info("✅ Training complete & model saved")


if __name__ == "__main__":
    train()