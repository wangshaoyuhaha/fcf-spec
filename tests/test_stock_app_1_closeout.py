import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.stock_app_closeout import build_stock_app_1_boundary_summary
from stock_app.contracts.stock_app_closeout import build_stock_app_1_completion_summary
from stock_app.contracts.stock_app_closeout import build_stock_app_1_handoff_packet


def test_stock_app_1_completion_summary_marks_all_steps_complete():
    result = build_stock_app_1_completion_summary()
    assert result["stage"] == "STOCK-APP-1"
    assert result["status"] == "completed"
    assert result["baseline_before_closeout"] == 1109
    assert len(result["completed_steps"]) == 6
    assert "D6 ranked watchlist handoff" in result["completed_steps"]


def test_stock_app_1_outputs_include_required_candidate_fields():
    result = build_stock_app_1_completion_summary()
    assert "score_breakdown" in result["outputs"]
    assert "reason_codes" in result["outputs"]
    assert "risk_flags" in result["outputs"]
    assert "data_quality_state" in result["outputs"]
    assert "operator_review_required" in result["outputs"]


def test_stock_app_1_boundary_blocks_core_and_real_actions():
    result = build_stock_app_1_boundary_summary()
    assert result["sidecar_only"] is True
    assert result["core_import_allowed"] is False
    assert result["core_modified"] is False
    assert result["p48_core_expansion"] is False
    assert result["real_trading_allowed"] is False
    assert result["real_order_allowed"] is False


def test_stock_app_1_boundary_blocks_trading_claims():
    result = build_stock_app_1_boundary_summary()
    assert result["buy_instruction_allowed"] is False
    assert result["sell_instruction_allowed"] is False
    assert result["guaranteed_limit_up_claim_allowed"] is False
    assert result["operator_review_required"] is True


def test_stock_app_1_handoff_requires_operator_merge_review():
    result = build_stock_app_1_handoff_packet()
    assert result["handoff_status"] == "ready_for_operator_review"
    assert result["ready_for_merge_review"] is True
    assert result["auto_merge_allowed"] is False
    assert result["auto_tag_allowed"] is False
    assert result["auto_release_allowed"] is False
    assert result["auto_deploy_allowed"] is False
