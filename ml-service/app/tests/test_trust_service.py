import pytest

from app.services.trust_service import calibrate_probability, build_trust_result


def test_calibrate_probability_no_verified_purchase() -> None:
	assert calibrate_probability(0.55, verified_purchase=False) == 0.55


def test_calibrate_probability_with_verified_purchase() -> None:
	# Default discount is 0.2 in app.config.Settings
	assert calibrate_probability(0.55, verified_purchase=True) == pytest.approx(0.35)


def test_calibrate_probability_clamped_lower_bound() -> None:
	assert calibrate_probability(0.02, verified_purchase=True) == 0.0


def test_build_trust_result_promotes_verified_review() -> None:
	unverified = build_trust_result(0.45, verified_purchase=False)
	verified = build_trust_result(0.45, verified_purchase=True)

	assert unverified["risk_level"] == "Medium Risk"
	assert unverified["effective_fake_probability"] == pytest.approx(0.45)
	assert verified["risk_level"] == "Low Risk"
	assert verified["effective_fake_probability"] == pytest.approx(0.25)
	assert verified["trust_score"] > unverified["trust_score"]
