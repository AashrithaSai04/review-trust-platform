"""
Model Service — loads the trained DistilBERT model and runs inference.
Singleton pattern ensures the model is loaded once at startup.
"""

from pathlib import Path
from typing import Optional

import numpy as np

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ModelService:
    """Singleton wrapper around the trained DistilBERT model."""

    _instance: Optional["ModelService"] = None

    def __new__(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tokenizer = None
            cls._instance._model = None
            cls._instance._loaded = False
            cls._instance._is_mock = False
        return cls._instance

    def load(self) -> None:
        if self._loaded:
            return

        try:
            import torch
            from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
        except ImportError as exc:
            logger.warning(
                f"Model dependencies are not installed ({exc}). Using mock predictions."
            )
            self._tokenizer = None
            self._model = None
            self._is_mock = True
            self._loaded = True
            return

        model_path = Path(settings.model_dir)
        if not model_path.exists():
            logger.warning(
                f"Model not found at {model_path}. "
                "Using mock predictions. Run ml-pipeline/scripts/train.py first."
            )
            self._tokenizer = None
            self._model = None
            self._is_mock = True
            self._loaded = True
            return

        logger.info(f"Loading tokenizer from {model_path}")
        self._tokenizer = DistilBertTokenizerFast.from_pretrained(str(model_path))

        logger.info(f"Loading model from {model_path}")
        self._model = DistilBertForSequenceClassification.from_pretrained(
            str(model_path), output_attentions=True
        )
        self._device = torch.device(settings.device)
        self._model.to(self._device)
        self._model.eval()
        self._is_mock = False
        self._loaded = True
        logger.info(f"Model loaded on {self._device}")

    def predict(self, text: str) -> dict:
        """
        Run inference on a single review text.

        Returns:
            dict with keys:
              - fake_probability (float)
              - attention_weights (list[float]) — per-token attention scores
              - tokens (list[str])
              - is_mock (bool) — True if using fallback mock model
        """
        self.load()

        if self._model is None:
            result = self._mock_predict(text)
            result["is_mock"] = True
            return result

        inputs = self._tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=settings.max_length,
            return_tensors="pt",
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)

        # ── Probabilities ──────────────────────────────────────────────────────
        probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
        fake_probability = float(probs[1])

        # ── Attention Extraction ───────────────────────────────────────────────
        # outputs.attentions: tuple of (num_layers,) each shape (1, heads, seq, seq)
        # We average over all layers and all heads, then take the CLS row
        attention_tensors = torch.stack(outputs.attentions)         # (L, 1, H, S, S)
        avg_attention = attention_tensors.mean(dim=[0, 1, 2])[0]   # (S,) — CLS attending to tokens
        attention_weights = avg_attention.cpu().numpy().tolist()

        tokens = self._tokenizer.convert_ids_to_tokens(
            inputs["input_ids"][0].cpu().numpy()
        )

        return {
            "fake_probability": fake_probability,
            "attention_weights": attention_weights,
            "tokens": tokens,
            "is_mock": False,
        }

    def _mock_predict(self, text: str) -> dict:
        """Fallback mock when model is not trained yet."""
        import random
        random.seed(len(text))
        fake_prob = random.uniform(0.1, 0.95)
        seq_len = min(len(text.split()) + 2, 20)
        tokens = ["[CLS]"] + text.split()[:seq_len - 2] + ["[SEP]"]
        weights = [random.uniform(0.01, 0.15) for _ in tokens]
        return {
            "fake_probability": fake_prob,
            "attention_weights": weights,
            "tokens": tokens,
        }


# Module-level singleton
model_service = ModelService()