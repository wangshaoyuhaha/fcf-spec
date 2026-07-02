import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_closeout import build_p6_closeout_package
from btc_finance_platform.paper_multi_market_closeout import get_p6_multi_market_capabilities
from btc_finance_platform.paper_multi_market_closeout import get_p6_safety_acceptance
from btc_finance_platform.paper_multi_market_closeout import get_p6_to_p7_transition_anchor

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_p6_multi_market_capabilities_marks_p6_completed():
    result = get_p6_multi_market_capabilities()
    assert result["ok"] is True
    assert result["type"] == "p6_multi_market_capabilities"
    assert result["phase"] == "P6"
    assert result["status"] == "completed"
    assert len(result["completed_scope"]) == 15

def test_p6_capabilities_include_multi_market_registry_and_readiness():
    result = get_p6_multi_market_capabilities()
    assert "multi-market adapter registry" in result["capabilities"]
    assert "multi-market readiness gate" in result["capabilities"]
    assert "crypto stock ETF FX commodity architecture baseline" in result["capabilities"]
    assert result["broader_goal"] == "general FCF-style finance platform for stocks and other markets"

def test_p6_safety_acceptance_passes_all_checks():
    result = get_p6_safety_acceptance()
    assert result["ok"] is True
    assert result["type"] == "p6_safety_acceptance"
    assert result["decision"] == "P6 accepted for paper-only multi-market architecture closeout"
    assert all(result["checks"].values())

def test_p6_safety_acceptance_preserves_no_real_market_connections():
    result = get_p6_safety_acceptance()
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_p6_to_p7_transition_anchor_names_next_phase():
    result = get_p6_to_p7_transition_anchor()
    assert result["ok"] is True
    assert result["type"] == "p6_to_p7_transition_anchor"
    assert result["from_phase"] == "P6 multi-market architecture preparation"
    assert result["to_phase"] == "P7 UI and operator console preparation"
    assert "local operator console contract" in result["p7_candidate_scope"]

def test_p6_to_p7_transition_anchor_preserves_safety_boundary():
    result = get_p6_to_p7_transition_anchor()
    assert "no real exchange API" in result["must_preserve"]
    assert "no real brokerage API" in result["must_preserve"]
    assert "no real orders" in result["must_preserve"]
    assert "paper-only boundary" in result["must_preserve"]

def test_build_p6_closeout_package():
    result = build_p6_closeout_package(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "p6_closeout_package"
    assert result["phase"] == "P6"
    assert result["status"] == "completed"
    assert result["next_phase"] == "P7 UI and operator console preparation"
    assert result["decision"] == "P6_closed_paper_only_ready_for_P7"

def test_p6_closeout_package_preserves_safety_flags():
    result = build_p6_closeout_package(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
