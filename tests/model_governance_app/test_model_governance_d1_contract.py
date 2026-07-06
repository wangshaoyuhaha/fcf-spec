"""Tests for MODEL-GOVERNANCE-D1 contract boundary."""

from __future__ import annotations

from apps.model_governance_app.contract import (
    MODEL_GOVERNANCE_APP_ID,
    MODEL_GOVERNANCE_STAGE_ID,
    build_model_governance_contract,
    summarize_model_governance_contract,
)


def test_model_governance_d1_identity() -> None:
    contract = build_model_governance_contract()

    assert MODEL_GOVERNANCE_APP_ID == "MODEL-GOVERNANCE-APP-1"
    assert MODEL_GOVERNANCE_STAGE_ID == "MODEL-GOVERNANCE-D1"
    assert contract["app_id"] == MODEL_GOVERNANCE_APP_ID
    assert contract["stage_id"] == MODEL_GOVERNANCE_STAGE_ID
    assert contract["purpose"] == "paper_only_model_rule_governance"


def test_model_governance_d1_reads_completed_sidecar_layers() -> None:
    contract = build_model_governance_contract()

    required_layers = {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "OPERATOR-REVIEW-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "DATA-QUALITY-OPS-APP-1",
        "MARKET-SCENARIO-APP-1",
        "BACKTEST-REVIEW-APP-1",
        "SIGNAL-VALIDATION-APP-1",
    }

    assert required_layers.issubset(set(contract["source_layers"]))


def test_model_governance_d1_outputs_governance_artifacts_only() -> None:
    contract = build_model_governance_contract()

    expected_outputs = {
        "model_governance_contract",
        "model_rule_registry",
        "scoring_policy_snapshot",
        "reason_code_coverage_report",
        "risk_flag_coverage_report",
        "governance_review_packet",
        "final_workflow_handoff",
    }

    assert set(contract["output_contracts"]) == expected_outputs


def test_model_governance_d1_does_not_mutate_scores_or_flags() -> None:
    contract = build_model_governance_contract()
    scope = contract["governance_scope"]

    assert scope["scoring_policy_snapshot_allowed"] is True
    assert scope["model_rule_registry_allowed"] is True
    assert scope["score_mutation_allowed"] is False
    assert scope["reason_code_mutation_allowed"] is False
    assert scope["risk_flag_deletion_allowed"] is False


def test_model_governance_d1_core_and_source_boundaries_are_closed() -> None:
    contract = build_model_governance_contract()

    assert contract["core_boundary"]["p1_p47_core_mutation_allowed"] is False
    assert contract["core_boundary"]["p48_core_expansion_allowed"] is False
    assert contract["source_boundary"]["source_content_mutation_allowed"] is False
    assert contract["source_boundary"]["source_deletion_allowed"] is False
    assert contract["source_boundary"]["source_overwrite_allowed"] is False


def test_model_governance_d1_execution_and_claim_boundaries_are_closed() -> None:
    contract = build_model_governance_contract()
    execution = contract["execution_boundary"]
    claim = contract["claim_boundary"]

    assert execution["real_trading_allowed"] is False
    assert execution["real_execution_allowed"] is False
    assert execution["broker_connection_allowed"] is False
    assert execution["exchange_connection_allowed"] is False
    assert execution["trade_action_enabled"] is False
    assert execution["automatic_position_sizing_allowed"] is False
    assert execution["automatic_portfolio_action_allowed"] is False
    assert claim["future_return_prediction_allowed"] is False
    assert claim["guaranteed_performance_claim_allowed"] is False


def test_model_governance_d1_operator_boundary_is_required() -> None:
    contract = build_model_governance_contract()

    assert contract["operator_boundary"]["operator_review_required"] is True
    assert contract["operator_boundary"]["operator_review_bypass_allowed"] is False
    assert contract["operator_boundary"]["governance_status_is_trade_instruction"] is False


def test_model_governance_d1_summary_is_safe() -> None:
    summary = summarize_model_governance_contract()

    assert summary["app_id"] == "MODEL-GOVERNANCE-APP-1"
    assert summary["stage_id"] == "MODEL-GOVERNANCE-D1"
    assert summary["source_layer_count"] == 9
    assert summary["operator_review_required"] is True
    assert summary["score_mutation_allowed"] is False
    assert summary["risk_flag_deletion_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["p1_p47_core_mutation_allowed"] is False
