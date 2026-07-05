import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.closeout import build_data_app_1_closeout_summary


def test_data_app_1_closeout_marks_stage_completed():
    result = build_data_app_1_closeout_summary()

    assert result["app"] == "DATA-APP"
    assert result["stage"] == "DATA-APP-1"
    assert result["status"] == "completed"
    assert result["baseline_tests"] == 1066
    assert result["ready_for_stock_app"] is True


def test_data_app_1_closeout_lists_all_completed_steps():
    result = build_data_app_1_closeout_summary()

    assert len(result["completed_steps"]) == 6
    assert "D1 sidecar boundary" in result["completed_steps"]
    assert "D6 clean universe and quarantine report" in result["completed_steps"]
    assert "quarantine_report" in result["outputs"]


def test_data_app_1_closeout_blocks_merge_release_deploy_by_default():
    result = build_data_app_1_closeout_summary()

    assert result["ready_for_merge_review"] is True
    assert result["auto_merge_allowed"] is False
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False


def test_data_app_1_closeout_preserves_safety_boundary():
    result = build_data_app_1_closeout_summary()

    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["operator_review_required"] is True
    assert result["core_mutation_allowed"] is False
    assert result["p48_core_expansion"] is False
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_balance_allowed"] is False
    assert result["real_position_allowed"] is False
    assert result["real_money_impact_allowed"] is False
