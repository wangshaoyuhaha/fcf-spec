import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry_readiness import build_paper_model_registry_readiness_report
from btc_finance_platform.paper_model_registry_readiness import evaluate_paper_model_registry_readiness


def approved_card():
    return {
        "model_id": "paper-btc-model-v1",
        "paper_only": True,
        "operator_review_required": True,
        "operator_approved": True,
        "real_world_actions_allowed": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
    }


def safe_report():
    return {
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def test_operator_approved_card_allows_paper_deployment_only():
    result = evaluate_paper_model_registry_readiness(approved_card(), registry_report=safe_report())

    assert result["gate_status"] == "ready"
    assert result["paper_deployment_allowed_now"] is True
    assert result["deployment_allowed_now"] is False
    assert result["real_world_actions_allowed"] is False


def test_unapproved_card_blocks_paper_deployment():
    card = approved_card()
    card["operator_approved"] = False

    result = evaluate_paper_model_registry_readiness(card, registry_report=safe_report())

    assert result["gate_status"] == "blocked"
    assert "check_failed:operator_approval_recorded" in result["blocked_reasons"]
    assert result["paper_deployment_allowed_now"] is False


def test_real_world_action_flag_blocks_even_when_operator_approved():
    card = approved_card()
    card["real_world_actions_allowed"] = True

    result = evaluate_paper_model_registry_readiness(card, registry_report=safe_report())

    assert result["gate_status"] == "blocked"
    assert "check_failed:paper_only_boundary" in result["blocked_reasons"]
    assert result["real_order"] is False
    assert result["real_execution"] is False


def test_bypass_operator_review_blocks_readiness():
    card = approved_card()
    card["bypass_operator_review"] = True

    result = evaluate_paper_model_registry_readiness(card, registry_report=safe_report())

    assert result["gate_status"] == "blocked"
    assert "check_failed:bypass_operator_review_blocked" in result["blocked_reasons"]


def test_unsafe_registry_report_blocks_readiness():
    report = safe_report()
    report["deployment_allowed_now"] = True

    result = evaluate_paper_model_registry_readiness(approved_card(), registry_report=report)

    assert result["gate_status"] == "blocked"
    assert "check_failed:registry_report_safe" in result["blocked_reasons"]
    assert result["parameter_update_allowed_now"] is False


def test_parameter_update_request_is_still_paper_only():
    result = evaluate_paper_model_registry_readiness(
        approved_card(),
        requested_action="paper_parameter_update",
        registry_report=safe_report(),
    )

    assert result["gate_status"] == "ready"
    assert result["paper_parameter_update_allowed_now"] is True
    assert result["parameter_update_allowed_now"] is False


def test_readiness_report_counts_ready_and_blocked_models():
    blocked = approved_card()
    blocked["model_id"] = "paper-btc-model-v2"
    blocked["operator_approved"] = False

    result = build_paper_model_registry_readiness_report([approved_card(), blocked], safe_report())

    assert result["ok"] is True
    assert result["type"] == "paper_model_registry_readiness_report"
    assert result["report_status"] == "blocked"
    assert result["total_models"] == 2
    assert result["ready_count"] == 1
    assert result["blocked_count"] == 1
    assert result["real_world_actions_allowed"] is False


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError, match="model_card must be a dict"):
        evaluate_paper_model_registry_readiness(None)

    with pytest.raises(ValueError, match="model_cards must not be empty"):
        build_paper_model_registry_readiness_report([])
