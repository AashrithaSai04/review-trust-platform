from app.services.model_service import model_service
from app.services.prediction_orchestrator import (
	_build_explanation,
	_build_feature_contributions,
	_build_important_phrases,
)


def test_mock_predict_is_deterministic_for_same_text() -> None:
	text = "Great cooling and low noise for my room."

	a = model_service._mock_predict(text)
	b = model_service._mock_predict(text)

	assert a["fake_probability"] == b["fake_probability"]
	assert a["tokens"] == b["tokens"]
	assert a["attention_weights"] == b["attention_weights"]


def test_mock_predict_ignores_whitespace_variants() -> None:
	text_compact = "Great cooling and low noise for my room."
	text_spaced = "  Great   cooling and low noise\nfor my room.  "

	compact = model_service._mock_predict(text_compact)
	spaced = model_service._mock_predict(text_spaced)

	assert compact["fake_probability"] == spaced["fake_probability"]


def test_build_feature_contributions_merges_duplicates() -> None:
	important_words = [["AC", 0.4], ["ac", 0.9], ["cooling", 0.7]]

	result = _build_feature_contributions(important_words, max_items=5)

	assert result["ac"] == 0.9
	assert result["cooling"] == 0.7


def test_build_important_phrases_picks_context_sentences() -> None:
	text = "Cooling is very fast. The AC is quiet at night. Energy usage is stable."
	important_words = [["quiet", 0.8], ["energy", 0.7]]

	phrases = _build_important_phrases(text, important_words, max_phrases=3)

	assert any("quiet" in p.lower() for p in phrases)
	assert any("energy" in p.lower() for p in phrases)


def test_build_explanation_contains_key_signals() -> None:
	explanation = _build_explanation(
		label="Low",
		score=82,
		fake_probability=0.1823,
		xai_method="attention",
		verified_purchase=True,
		is_mock=False,
		feature_contributions={"cooling": 0.9, "quiet": 0.8},
	)

	assert "Low risk" in explanation
	assert "score 82/100" in explanation
	assert "cooling" in explanation
	assert "attention" in explanation
