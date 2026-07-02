import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis_logic import draft_paper_signal
from btc_finance_platform.paper_risk_governance import build_batch_risk_governance_report
from btc_finance_platform.paper_risk_governance import build_policy_gate_for_governor_decision
from btc_finance_platform.paper_risk_governance import build_risk_governor_decision
from btc_finance_platform.paper_risk_governance import classify_market_regime_from_item


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_classify_market_regime_from_high_risk_item():
    analysis = draft_paper_signal("BTCUSDT", 70000, 64000, [64000, 70000])
    result = classify_market_regime_from_item(analysis)

    assert result["ok"] is True
    assert result["type"] == "paper_market_regime_classification"
    assert result["symbol"] == "BTCUSDT"
    assert result["regime"] == "stressed"


def test_risk_governor_blocks_high_risk_escalation():
    analysis = draft_paper_signal("BTCUSDT", 70000, 64000, [64000, 70000])
    result = build_risk_governor_decision(analysis)

    assert result["ok"] is True
    assert result["type"] == "risk_governor_decision"
    assert result["gate"] == "blocked_for_escalation"
    assert result["allowed_action"] == "paper_review_only"
    assert "high_risk_requires_manual_review_only" in result["blocked_reasons"]


def test_risk_governor_allows_low_risk_paper_review():
    analysis = draft_paper_signal("ETHUSDT", 3500, 3490, [3480, 3500])
    result = build_risk_governor_decision(analysis)

    assert result["ok"] is True
    assert result["gate"] == "paper_allowed_with_operator_review"
    assert result["allowed_action"] == "paper_analysis_review"
    assert result["decision"] == "governor_paper_only_no_real_trade"


def test_policy_gate_passes_paper_only_governor_decision():
    analysis = draft_paper_signal("ETHUSDT", 3500, 3490, [3480, 3500])
    governor = build_risk_governor_decision(analysis)
    result = build_policy_gate_for_governor_decision(governor)

    assert result["ok"] is True
    assert result["type"] == "policy_gate_decision"
    assert result["gate"] == "pass"
    assert "real_order" in result["blocked_real_world_actions"]
    assert result["decision"] == "policy_gate_paper_only"


def test_policy_gate_rejects_bad_decision_type():
    with pytest.raises(ValueError, match="governor_decision type is invalid"):
        build_policy_gate_for_governor_decision({"type": "bad"})


def test_batch_risk_governance_report_connects_pipeline_to_policy_gate():
    result = build_batch_risk_governance_report(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "batch_risk_governance_report"
    assert result["count"] == 6
    assert len(result["governor_decisions"]) == 6
    assert len(result["policy_gates"]) == 6
    assert result["decision"] == "batch_governance_paper_only_no_real_trade"


def test_batch_risk_governance_report_preserves_safety_flags():
    result = build_batch_risk_governance_report(SOURCES)

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


def test_batch_risk_governance_report_has_gate_and_regime_counts():
    result = build_batch_risk_governance_report(SOURCES)

    assert isinstance(result["gate_counts"], dict)
    assert isinstance(result["regime_counts"], dict)
    assert sum(result["gate_counts"].values()) == result["count"]
    assert sum(result["regime_counts"].values()) == result["count"]
