import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.integrated_report import render_integrated_report
from btc_finance_platform.paper_analysis import analyze_paper_market
from btc_finance_platform.paper_input import validate_paper_input
from btc_finance_platform.risk_score import score_paper_risk
from btc_finance_platform.strategy_draft import create_strategy_draft


def test_risk_score_low():
    analysis = analyze_paper_market(validate_paper_input({"symbol": "BTCUSDT", "price": 64100, "reference_price": 64000}))
    risk = score_paper_risk(analysis)
    assert risk["risk_level"] == "LOW"
    assert risk["paper_only"] is True
    assert risk["real_order"] is False


def test_risk_score_medium():
    analysis = analyze_paper_market(validate_paper_input({"symbol": "BTCUSDT", "price": 66000, "reference_price": 64000}))
    risk = score_paper_risk(analysis)
    assert risk["risk_level"] == "MEDIUM"


def test_risk_score_high():
    analysis = analyze_paper_market(validate_paper_input({"symbol": "BTCUSDT", "price": 70000, "reference_price": 64000}))
    risk = score_paper_risk(analysis)
    assert risk["risk_level"] == "HIGH"


def test_strategy_draft_review_only_for_high_risk():
    analysis = analyze_paper_market(validate_paper_input({"symbol": "BTCUSDT", "price": 70000, "reference_price": 64000}))
    risk = score_paper_risk(analysis)
    strategy = create_strategy_draft(analysis, risk)

    assert strategy["stance"] == "REVIEW_ONLY"
    assert strategy["action"] == "NO_LIVE_ACTION"
    assert strategy["real_execution"] is False


def test_integrated_report_contains_safety_lines():
    analysis = analyze_paper_market(validate_paper_input({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000}))
    risk = score_paper_risk(analysis)
    strategy = create_strategy_draft(analysis, risk)
    report = render_integrated_report(analysis, risk, strategy)

    assert "PAPER_ONLY_REVIEW_REQUIRED" in report
    assert "NO_LIVE_ACTION" in report
    assert "no real exchange API" in report
    assert "operator review required" in report
