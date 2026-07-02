import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_closeout import build_p7_closeout_package
from btc_finance_platform.paper_operator_console_closeout import get_p7_operator_console_capabilities
from btc_finance_platform.paper_operator_console_closeout import get_p7_safety_acceptance
from btc_finance_platform.paper_operator_console_closeout import get_p7_to_p8_transition_anchor

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_p7_operator_console_capabilities_marks_p7_completed():
    result = get_p7_operator_console_capabilities()
    assert result["ok"] is True
    assert result["type"] == "p7_operator_console_capabilities"
    assert result["phase"] == "P7"
    assert result["status"] == "completed"
    assert len(result["completed_scope"]) == 15

def test_p7_capabilities_include_ui_manifest_and_acceptance_gate():
    result = get_p7_operator_console_capabilities()
    assert "operator console UI manifest" in result["capabilities"]
    assert "operator console page registry" in result["capabilities"]
    assert "operator console UI acceptance gate" in result["capabilities"]
    assert "static UI handoff readiness" in result["capabilities"]

def test_p7_safety_acceptance_passes_all_checks():
    result = get_p7_safety_acceptance()
    assert result["ok"] is True
    assert result["type"] == "p7_safety_acceptance"
    assert result["decision"] == "P7 accepted for paper-only operator console closeout"
    assert all(result["checks"].values())

def test_p7_safety_acceptance_preserves_no_real_world_effects():
    result = get_p7_safety_acceptance()
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

def test_p7_to_p8_transition_anchor_names_learning_phase():
    result = get_p7_to_p8_transition_anchor()
    assert result["ok"] is True
    assert result["type"] == "p7_to_p8_transition_anchor"
    assert result["from_phase"] == "P7 UI and operator console preparation"
    assert result["to_phase"] == "P8 learning memory and feedback dataset"
    assert "paper analysis memory schema" in result["p8_candidate_scope"]

def test_p7_to_p8_transition_anchor_forbids_self_trading_loop():
    result = get_p7_to_p8_transition_anchor()
    assert result["forbidden_learning_loop"] == ["observe", "self_learn", "self_trade"]
    assert "no automatic live trading" in result["must_preserve"]
    assert "no bypassing operator review" in result["must_preserve"]

def test_build_p7_closeout_package():
    result = build_p7_closeout_package(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "p7_closeout_package"
    assert result["phase"] == "P7"
    assert result["status"] == "completed"
    assert result["next_phase"] == "P8 learning memory and feedback dataset"
    assert result["decision"] == "P7_closed_paper_only_ready_for_P8"

def test_p7_closeout_package_preserves_safety_flags():
    result = build_p7_closeout_package(MULTI_MARKET_FIXTURE)
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
