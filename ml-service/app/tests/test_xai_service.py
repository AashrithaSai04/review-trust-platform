from app.services.xai_service import extract_important_words


def test_extract_important_words_filters_stopwords() -> None:
	tokens = ["[CLS]", "the", "I", "inverter", "cooling", "[SEP]"]
	weights = [0.9, 0.8, 0.7, 0.95, 0.85, 0.1]

	result = extract_important_words(tokens, weights, top_k=5)
	words = [item[0].lower() for item in result]

	assert "the" not in words
	assert "i" not in words
	assert "inverter" in words
	assert "cooling" in words


def test_extract_important_words_merges_duplicate_tokens() -> None:
	tokens = ["[CLS]", "godrej", "Godrej", "inverter", "[SEP]"]
	weights = [0.1, 0.3, 0.9, 0.7, 0.1]

	result = extract_important_words(tokens, weights, top_k=5)
	godrej_items = [item for item in result if item[0].lower() == "godrej"]

	assert len(godrej_items) == 1


def test_extract_important_words_keeps_numeric_semantic_tokens() -> None:
	tokens = ["[CLS]", "3", "star", "1.5", "the", "[SEP]"]
	weights = [0.1, 0.9, 0.85, 0.88, 0.95, 0.1]

	result = extract_important_words(tokens, weights, top_k=5)
	words = [item[0].lower() for item in result]

	assert "3" in words
	assert "1.5" in words
	assert "the" not in words
