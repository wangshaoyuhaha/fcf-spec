import pytest

from btc_finance_platform.paper_analysis_logic import analyze_paper_batch
from btc_finance_platform.paper_analysis_logic import calculate_price_deviation
from btc_finance_platform.paper_analysis_logic import calculate_simple_momentum
from btc_finance_platform.paper_analysis_logic import classify_deviation_magnitude
from btc_finance_platform.paper_analysis_logic import draft_paper_signal
from btc_finance_platform.paper_analysis_logic import estimate_paper_risk_score


def test_calculate_price_deviation_above_reference():
    result = calculate_price_deviation(65000, 64000)

    assert result["ok"] is True
    assert result["type"] == "price_deviation_analysis"
    assert result["direction"] == "above_reference"
    assert round(result["deviation_pct"], 6) == round(1000 / 64000, 6)
    assert result["paper_only"] is True


def test_calculate_price_deviation_rejects_zero_price():
    with pytest.raises(ValueError, match="price must be a positive number"):
        calculate_price_deviation(0, 64000)


def test_classify_deviation_magnitude_thresholds():
    assert classify_deviation_magnitude(0.001) == "tiny"
    assert classify_deviation_magnitude(0.01) == "small"
    assert classify_deviation_magnitude(0.03) == "medium"
    assert classify_deviation_magnitude(0.08) == "large"


def test_calculate_simple_momentum_up_direction():
    result = calculate_simple_momentum([63000, 64000, 65000])

    assert result["ok"] is True
    assert result["available"] is True
    assert result["direction"] == "up"
    assert result["momentum_pct"] > 0
    assert result["real_execution"] is False


def test_estimate_paper_risk_score_high_for_large_move():
    result = estimate_paper_risk_score(0.08, 0.04)

    assert result["ok"] is True
    assert result["level"] == "high"
    assert result["paper_only"] is True
    assert result["operator_review_required"] is True


def test_draft_paper_signal_is_review_only_when_high_risk():
    result = draft_paper_signal("BTCUSDT", 70000, 64000, [64000, 70000])

    assert result["ok"] is True
    assert result["symbol"] == "BTCUSDT"
    assert result["signal"] == "paper_review_only_high_risk"
    assert result["decision"] == "no_real_trade_paper_signal_only"


def test_draft_paper_signal_preserves_safety_flags():
    result = draft_paper_signal("ethusdt", 3500, 3600)

    assert result["symbol"] == "ETHUSDT"
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_analyze_paper_batch_returns_symbols_and_count():
    result = analyze_paper_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])

    assert result["ok"] is True
    assert result["type"] == "paper_batch_analysis_baseline"
    assert result["count"] == 2
    assert result["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert result["decision"] == "batch_analysis_paper_only_no_real_trade"
    assert result["real_money_impact"] is False
