import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis import analyze_paper_market, assert_paper_market_analysis
from btc_finance_platform.paper_input import validate_paper_input
from btc_finance_platform.report_renderer import render_paper_report


def test_validate_paper_input():
    validated = validate_paper_input({"symbol": "btcusdt", "price": 65000, "reference_price": 64000})
    assert validated["symbol"] == "BTCUSDT"
    assert validated["paper_only"] is True
    assert validated["real_exchange_api"] is False


def test_paper_market_analysis_upside():
    validated = validate_paper_input({"symbol": "BTCUSDT", "price": 66000, "reference_price": 64000})
    analysis = analyze_paper_market(validated)
    assert analysis["scenario"] == "PAPER_UPSIDE_MOVE"
    assert assert_paper_market_analysis(analysis) is True


def test_paper_market_analysis_downside():
    validated = validate_paper_input({"symbol": "BTCUSDT", "price": 62000, "reference_price": 64000})
    analysis = analyze_paper_market(validated)
    assert analysis["scenario"] == "PAPER_DOWNSIDE_MOVE"
    assert analysis["real_execution"] is False


def test_paper_market_analysis_range():
    validated = validate_paper_input({"symbol": "BTCUSDT", "price": 64100, "reference_price": 64000})
    analysis = analyze_paper_market(validated)
    assert analysis["scenario"] == "PAPER_RANGE_MOVE"
    assert analysis["real_money_impact"] is False


def test_report_renderer_outputs_safety_text():
    validated = validate_paper_input({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000})
    analysis = analyze_paper_market(validated)
    report = render_paper_report(analysis)

    assert "PAPER_ONLY_REVIEW_REQUIRED" in report
    assert "NO_LIVE_ACTION" in report
    assert "no real exchange API" in report
    assert "operator review required" in report


def test_validate_paper_input_rejects_bad_price():
    try:
        validate_paper_input({"symbol": "BTCUSDT", "price": 0})
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
