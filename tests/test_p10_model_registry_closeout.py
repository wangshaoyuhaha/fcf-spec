import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p10_model_registry_closeout import build_p10_model_registry_closeout_summary
from btc_finance_platform.p10_model_registry_closeout import evaluate_p10_model_registry_closeout


def safe_report():
    return {
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }


def all_days():
    return [f"P10-D{i}" for i in range(1, 16)]


def test_p10_closeout_completes_when_all_guards_are_safe():
    result = evaluate_p10_model_registry_closeout(safe_report(), safe_report(), all_days())

    assert result["closeout_status"] == "completed"
    assert result["p10_completed"] is True
    assert result["next_stage_allowed"] is True
    assert result["next_stage"] == "P11"
    assert result["real_world_actions_allowed"] is False


def test_p10_closeout_blocks_when_a_day_is_missing():
    days = all_days()[:-1]

    result = evaluate_p10_model_registry_closeout(safe_report(), safe_report(), days)

    assert result["closeout_status"] == "blocked"
    assert "P10-D15" in result["missing_days"]
    assert "check_failed:all_p10_days_completed" in result["blocked_reasons"]


def test_p10_closeout_blocks_when_registry_report_lacks_required_false_field():
    report = safe_report()
    report.pop("real_world_actions_allowed")

    result = evaluate_p10_model_registry_closeout(report, safe_report(), all_days())

    assert result["closeout_status"] == "blocked"
    assert "check_failed:registry_report_no_real_world_allowance" in result["blocked_reasons"]


def test_p10_closeout_blocks_when_readiness_report_allows_real_deployment():
    report = safe_report()
    report["deployment_allowed_now"] = True

    result = evaluate_p10_model_registry_closeout(safe_report(), report, all_days())

    assert result["closeout_status"] == "blocked"
    assert "check_failed:readiness_report_no_real_world_allowance" in result["blocked_reasons"]
    assert result["deployment_allowed_now"] is False


def test_p10_closeout_blocks_bypass_flags():
    report = safe_report()
    report["bypass_operator_review"] = True

    result = evaluate_p10_model_registry_closeout(report, safe_report(), all_days())

    assert result["closeout_status"] == "blocked"
    assert "check_failed:registry_report_no_bypass_operator_review" in result["blocked_reasons"]


def test_p10_closeout_summary_keeps_paper_only_boundary():
    closeout = evaluate_p10_model_registry_closeout(safe_report(), safe_report(), all_days())
    summary = build_p10_model_registry_closeout_summary(closeout)

    assert summary["status"] == "completed"
    assert summary["p10_completed"] is True
    assert summary["paper_only"] is True
    assert summary["real_world_actions_allowed"] is False
    assert summary["operator_review_required"] is True


def test_p10_closeout_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="registry_report must be a dict"):
        evaluate_p10_model_registry_closeout(None, safe_report(), all_days())

    with pytest.raises(ValueError, match="completed_days must be a list"):
        evaluate_p10_model_registry_closeout(safe_report(), safe_report(), "P10-D1")
