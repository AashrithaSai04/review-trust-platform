"""
Evaluation script for trained DistilBERT fake review classifier.
Generates classification report and confusion matrix.
"""

import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path

import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = Path("../data/cleaned_reviews.csv")
MODEL_DIR = Path("../models/distilbert-review-classifier")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MAX_LENGTH = 256
BATCH_SIZE = 32
TEST_SIZE = 0.2
SEED = 42


def load_model_and_tokenizer():
    logger.info(f"Loading model from {MODEL_DIR}")
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR, output_attentions=True)
    model.to(DEVICE)
    model.eval()
    return model, tokenizer


def predict_batch(texts: list, model, tokenizer) -> tuple[list, list]:
    """Run batch inference, returns (predictions, probabilities)."""
    all_preds, all_probs = [], []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        inputs = tokenizer(
            batch,
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH,
            return_tensors="pt",
        ).to(DEVICE)

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
            preds = np.argmax(probs, axis=-1)

        all_preds.extend(preds.tolist())
        all_probs.extend(probs[:, 1].tolist())  # prob of FAKE class

    return all_preds, all_probs


def evaluate():
    # Load test set (reproduce same split as training)
    df = pd.read_csv(DATA_PATH)
    _, X_test, _, y_test = train_test_split(
        df["text"].tolist(),
        df["label"].tolist(),
        test_size=TEST_SIZE,
        random_state=SEED,
        stratify=df["label"].tolist(),
    )

    model, tokenizer = load_model_and_tokenizer()

    logger.info(f"Running inference on {len(X_test)} test samples...")
    preds, probs = predict_batch(X_test, model, tokenizer)

    # Classification report
    report = classification_report(
        y_test, preds, target_names=["REAL (0)", "FAKE (1)"], output_dict=True
    )
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    print(classification_report(y_test, preds, target_names=["REAL (0)", "FAKE (1)"]))

    # Confusion matrix
    cm = confusion_matrix(y_test, preds)
    print("CONFUSION MATRIX")
    print("=" * 60)
    print(f"                Predicted REAL  Predicted FAKE")
    print(f"Actual REAL     {cm[0][0]:>14}  {cm[0][1]:>14}")
    print(f"Actual FAKE     {cm[1][0]:>14}  {cm[1][1]:>14}")
    print("=" * 60)

    # Save results
    results = {
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "test_samples": len(X_test),
        "device": str(DEVICE),
    }
    out_path = MODEL_DIR / "evaluation_report.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Evaluation report saved to {out_path}")

    # Sample predictions
    print("\nSAMPLE PREDICTIONS")
    print("=" * 60)
    for i in range(min(5, len(X_test))):
        label_str = "FAKE" if preds[i] == 1 else "REAL"
        true_str = "FAKE" if y_test[i] == 1 else "REAL"
        print(f"Text    : {X_test[i][:80]}...")
        print(f"True    : {true_str}  |  Predicted: {label_str}  |  Fake Prob: {probs[i]:.3f}")
        print("-" * 60)


if __name__ == "__main__":
    evaluate()