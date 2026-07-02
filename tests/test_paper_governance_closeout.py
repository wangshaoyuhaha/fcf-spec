import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_closeout import build_p5_closeout_package
from btc_finance_platform.paper_governance_closeout import get_p5_governance_layer_capabilities
from btc_finance_platform.paper_governance_closeout import get_p5_safety_acceptance
from btc_finance_platform.paper_governance_closeout import get_p5_to_p6_transition_anchor


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_p5_governance_layer_capabilities_marks_p5_completed():
    result = get_p5_governance_layer_capabilities()

    assert result["ok"] is True
    assert result["type"] == "p5_governance_layer_capabilities"
    assert result["phase"] == "P5"
    assert result["status"] == "completed"
    assert len(result["completed_scope"]) == 15


def test_p5_capabilities_include_governor_policy_audit_and_ui_contract():
    result = get_p5_governance_layer_capabilities()

    assert "risk governor decision baseline" in result["capabilities"]
    assert "policy gate over paper signals" in result["capabilities"]
    assert "governance audit trail" in result["capabilities"]
    assert "governance UI contract" in result["capabilities"]
    assert result["broader_goal"] == "general FCF-style finance platform for stocks and other markets"


def test_p5_safety_acceptance_passes_all_checks():
    result = get_p5_safety_acceptance()

    assert result["ok"] is True
    assert result["type"] == "p5_safety_acceptance"
    assert result["decision"] == "P5 accepted for paper-only governance-layer closeout"
    assert all(result["checks"].values())


def test_p5_safety_acceptance_preserves_no_real_world_effects():
    result = get_p5_safety_acceptance()

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


def test_p5_to_p6_transition_anchor_names_next_phase():
    result = get_p5_to_p6_transition_anchor()

    assert result["ok"] is True
    assert result["type"] == "p5_to_p6_transition_anchor"
    assert result["from_phase"] == "P5 risk governance and regime layer"
    assert result["to_phase"] == "P6 multi-market architecture preparation"
    assert "market adapter interface baseline" in result["p6_candidate_scope"]


def test_p5_to_p6_transition_anchor_preserves_multi_market_safety():
    result = get_p5_to_p6_transition_anchor()

    assert "no real exchange API" in result["must_preserve"]
    assert "no real brokerage API" in result["must_preserve"]
    assert "no real orders" in result["must_preserve"]
    assert "BTC remains first implementation line not final platform boundary" in result["must_preserve"]


def test_build_p5_closeout_package():
    result = build_p5_closeout_package(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "p5_closeout_package"
    assert result["phase"] == "P5"
    assert result["status"] == "completed"
    assert result["next_phase"] == "P6 multi-market architecture preparation"
    assert result["decision"] == "P5_closed_paper_only_ready_for_P6"


def test_p5_closeout_package_preserves_safety_flags():
    result = build_p5_closeout_package(SOURCES)

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
