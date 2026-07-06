"""Tests for MODEL-GOVERNANCE-D5 governance review packet."""

from __future__ import annotations

from apps.model_governance_app.governance_review import (
    build_governance_review_packet,
    infer_governance_review_status,
    summarize_governance_review_packet,
    validate_governance_review_packet,
)


def _source_summary(status: str = "ALL_CONFIGURED_SOURCES_AVAILABLE") -> dict:
    return {
        "loader_status": status,
        "source_count": 8,
        "available_count": 8,
        "missing_required_count": 0,
        "missing_optional_count": 0,
    }


def _registry_summary(status: str = "GOVERNANCE_READY_FOR_OPERATOR_REVIEW") -> dict:
    return {
        "registry_status": status,
        "rule_count": 2,
        "snapshot_count": 1,
        "blocked_rules": [],
        "review_required_rules": [],
    }


def _coverage_summary(status: str = "GOVERNANCE_COVERAGE_READY_FOR_OPERATOR_REVIEW") -> dict:
    return {
        "packet_status": status,
        "reason_code_uncovered_count": 0,
        "risk_flag_uncovered_count": 0,
    }


def test_model_governance_d5_ready_packet() -> None:
    packet = build_governance_review_packet(
        packet_id="governance-review-001",
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )
    validation = validate_governance_review_packet(packet)
    summary = summarize_governance_review_packet(packet)

    assert packet["app_id"] == "MODEL-GOVERNANCE-APP-1"
    assert packet["stage_id"] == "MODEL-GOVERNANCE-D5"
    assert packet["packet_status"] == "GOVERNANCE_READY_FOR_OPERATOR_REVIEW"
    assert packet["operator_review_required"] is True
    assert packet["operator_review_bypass_allowed"] is False
    assert validation["is_valid"] is True
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False


def test_model_governance_d5_review_required_for_partial_source() -> None:
    status = infer_governance_review_status(
        source_manifest_summary=_source_summary("PARTIAL_SOURCE_AVAILABLE"),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )

    assert status == "GOVERNANCE_REVIEW_REQUIRED"


def test_model_governance_d5_review_required_for_registry_review_status() -> None:
    status = infer_governance_review_status(
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary("GOVERNANCE_REVIEW_REQUIRED"),
        coverage_summary=_coverage_summary(),
    )

    assert status == "GOVERNANCE_REVIEW_REQUIRED"


def test_model_governance_d5_review_required_for_partial_coverage() -> None:
    status = infer_governance_review_status(
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary("GOVERNANCE_COVERAGE_PARTIAL"),
    )

    assert status == "GOVERNANCE_REVIEW_REQUIRED"


def test_model_governance_d5_blocked_for_missing_required_source() -> None:
    packet = build_governance_review_packet(
        packet_id="governance-review-002",
        source_manifest_summary=_source_summary("BLOCKED_MISSING_REQUIRED_SOURCE"),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )

    assert packet["packet_status"] == "GOVERNANCE_BLOCKED"
    assert packet["operator_review_packet"]["no_execution_receipt_required"] is True


def test_model_governance_d5_blocked_for_blocked_registry() -> None:
    status = infer_governance_review_status(
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary("GOVERNANCE_BLOCKED"),
        coverage_summary=_coverage_summary(),
    )

    assert status == "GOVERNANCE_BLOCKED"


def test_model_governance_d5_packet_blocks_all_execution_paths() -> None:
    packet = build_governance_review_packet(
        packet_id="governance-review-003",
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )

    assert packet["score_mutation_allowed"] is False
    assert packet["reason_code_mutation_allowed"] is False
    assert packet["risk_flag_deletion_allowed"] is False
    assert packet["trade_action_enabled"] is False
    assert packet["buy_button_enabled"] is False
    assert packet["sell_button_enabled"] is False
    assert packet["order_button_enabled"] is False
    assert packet["real_trading_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["automatic_position_sizing_allowed"] is False
    assert packet["automatic_portfolio_action_allowed"] is False


def test_model_governance_d5_packet_blocks_predictions_and_guarantees() -> None:
    packet = build_governance_review_packet(
        packet_id="governance-review-004",
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )

    assert packet["future_return_prediction_allowed"] is False
    assert packet["guaranteed_performance_claim_allowed"] is False
    assert "governance_packet_is_not_a_trade_instruction" in packet["limitations"]


def test_model_governance_d5_validation_rejects_unsafe_packet() -> None:
    packet = build_governance_review_packet(
        packet_id="governance-review-005",
        source_manifest_summary=_source_summary(),
        rule_registry_summary=_registry_summary(),
        coverage_summary=_coverage_summary(),
    )
    packet["trade_action_enabled"] = True

    validation = validate_governance_review_packet(packet)

    assert validation["is_valid"] is False
    assert validation["unsafe_true_fields"] == ["trade_action_enabled"]
