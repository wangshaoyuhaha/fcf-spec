"""Tests for SIGNAL-VALIDATION-D1 contract boundary."""

from __future__ import annotations

from apps.signal_validation_app.contract import (
    SIGNAL_VALIDATION_APP_ID,
    SIGNAL_VALIDATION_STAGE_ID,
    build_signal_validation_contract,
    summarize_signal_validation_contract,
)


def test_signal_validation_d1_identity() -> None:
    contract = build_signal_validation_contract()

    assert SIGNAL_VALIDATION_APP_ID == "SIGNAL-VALIDATION-APP-1"
    assert SIGNAL_VALIDATION_STAGE_ID == "SIGNAL-VALIDATION-D1"
    assert contract["app_id"] == SIGNAL_VALIDATION_APP_ID
    assert contract["stage_id"] == SIGNAL_VALIDATION_STAGE_ID
    assert contract["purpose"] == "paper_only_signal_evidence_validation"


def test_signal_validation_d1_reads_existing_sidecar_layers() -> None:
    contract = build_signal_validation_contract()

    required_layers = {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "UI-APP-1",
        "OPERATOR-REVIEW-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "DATA-QUALITY-OPS-APP-1",
        "MARKET-SCENARIO-APP-1",
        "BACKTEST-REVIEW-APP-1",
    }

    assert required_layers.issubset(set(contract["source_layers"]))


def test_signal_validation_d1_outputs_review_artifacts_only() -> None:
    contract = build_signal_validation_contract()

    expected_outputs = {
        "signal_validation_contract",
        "signal_evidence_matrix",
        "signal_conflict_report",
        "signal_validation_status_packet",
        "operator_review_handoff",
    }

    assert set(contract["output_contracts"]) == expected_outputs


def test_signal_validation_d1_core_and_source_boundaries_are_closed() -> None:
    contract = build_signal_validation_contract()

    assert contract["core_boundary"]["p1_p47_core_mutation_allowed"] is False
    assert contract["core_boundary"]["p48_core_expansion_allowed"] is False
    assert contract["source_boundary"]["source_content_mutation_allowed"] is False
    assert contract["source_boundary"]["source_deletion_allowed"] is False
    assert contract["source_boundary"]["source_overwrite_allowed"] is False


def test_signal_validation_d1_execution_boundaries_are_closed() -> None:
    contract = build_signal_validation_contract()
    execution_boundary = contract["execution_boundary"]

    assert execution_boundary["real_trading_allowed"] is False
    assert execution_boundary["real_execution_allowed"] is False
    assert execution_boundary["broker_connection_allowed"] is False
    assert execution_boundary["exchange_connection_allowed"] is False
    assert execution_boundary["trade_action_enabled"] is False
    assert execution_boundary["automatic_position_sizing_allowed"] is False
    assert execution_boundary["automatic_portfolio_action_allowed"] is False


def test_signal_validation_d1_claim_and_operator_boundaries() -> None:
    contract = build_signal_validation_contract()

    assert contract["claim_boundary"]["future_return_prediction_allowed"] is False
    assert contract["claim_boundary"]["guaranteed_performance_claim_allowed"] is False
    assert contract["operator_boundary"]["operator_review_required"] is True
    assert contract["operator_boundary"]["operator_review_bypass_allowed"] is False
    assert contract["operator_boundary"]["validation_status_is_trade_instruction"] is False


def test_signal_validation_d1_summary_is_safe() -> None:
    summary = summarize_signal_validation_contract()

    assert summary["app_id"] == "SIGNAL-VALIDATION-APP-1"
    assert summary["stage_id"] == "SIGNAL-VALIDATION-D1"
    assert summary["source_layer_count"] == 9
    assert summary["operator_review_required"] is True
    assert summary["real_execution_allowed"] is False
    assert summary["p1_p47_core_mutation_allowed"] is False
    assert summary["source_content_mutation_allowed"] is False
