"""Tests for MODEL-GOVERNANCE-D4 coverage reports."""

from __future__ import annotations

import pytest

from apps.model_governance_app.coverage import (
    build_governance_coverage_packet,
    build_reason_code_coverage_report,
    build_risk_flag_coverage_report,
    build_coverage_report,
    infer_coverage_status,
    summarize_governance_coverage_packet,
    validate_governance_coverage_packet,
)


def test_model_governance_d4_reason_code_coverage_complete() -> None:
    report = build_reason_code_coverage_report(
        report_id="reason-report-001",
        observed_reason_codes=["A", "B", "A"],
        governed_reason_codes=["A", "B", "C"],
        source_layers=["STOCK-APP-1"],
    )

    assert report["item_type"] == "REASON_CODE"
    assert report["coverage_status"] == "COVERAGE_COMPLETE"
    assert report["observed_count"] == 2
    assert report["covered_count"] == 2
    assert report["uncovered_count"] == 0
    assert report["score_mutation_allowed"] is False
    assert report["reason_code_mutation_allowed"] is False


def test_model_governance_d4_risk_flag_coverage_partial() -> None:
    report = build_risk_flag_coverage_report(
        report_id="risk-report-001",
        observed_risk_flags=["RISK_A", "RISK_B"],
        governed_risk_flags=["RISK_A"],
        source_layers=["SIGNAL-VALIDATION-APP-1"],
    )

    assert report["item_type"] == "RISK_FLAG"
    assert report["coverage_status"] == "COVERAGE_PARTIAL"
    assert report["covered_items"] == ["RISK_A"]
    assert report["uncovered_items"] == ["RISK_B"]
    assert report["risk_flag_deletion_allowed"] is False
    assert report["real_execution_allowed"] is False


def test_model_governance_d4_coverage_review_required_when_none_governed() -> None:
    status = infer_coverage_status(
        observed_items=["A", "B"],
        governed_items=[],
    )

    assert status == "COVERAGE_REVIEW_REQUIRED"


def test_model_governance_d4_coverage_missing_when_no_observed_items() -> None:
    status = infer_coverage_status(
        observed_items=[],
        governed_items=["A", "B"],
    )

    assert status == "COVERAGE_MISSING"


def test_model_governance_d4_coverage_blocked_when_blocked_items_present() -> None:
    report = build_reason_code_coverage_report(
        report_id="reason-report-002",
        observed_reason_codes=["A"],
        governed_reason_codes=["A"],
        blocked_reason_codes=["A"],
    )

    assert report["coverage_status"] == "COVERAGE_BLOCKED"
    assert report["blocked_items"] == ["A"]


def test_model_governance_d4_combined_packet_ready() -> None:
    reason_report = build_reason_code_coverage_report(
        report_id="reason-report-003",
        observed_reason_codes=["REASON_A"],
        governed_reason_codes=["REASON_A"],
    )
    risk_report = build_risk_flag_coverage_report(
        report_id="risk-report-003",
        observed_risk_flags=["RISK_A"],
        governed_risk_flags=["RISK_A"],
    )

    packet = build_governance_coverage_packet(
        packet_id="coverage-packet-001",
        reason_code_report=reason_report,
        risk_flag_report=risk_report,
    )
    validation = validate_governance_coverage_packet(packet)
    summary = summarize_governance_coverage_packet(packet)

    assert packet["packet_status"] == "GOVERNANCE_COVERAGE_READY_FOR_OPERATOR_REVIEW"
    assert validation["is_valid"] is True
    assert summary["reason_code_uncovered_count"] == 0
    assert summary["risk_flag_uncovered_count"] == 0
    assert summary["trade_action_enabled"] is False


def test_model_governance_d4_combined_packet_requires_review_for_partial() -> None:
    reason_report = build_reason_code_coverage_report(
        report_id="reason-report-004",
        observed_reason_codes=["REASON_A", "REASON_B"],
        governed_reason_codes=["REASON_A"],
    )
    risk_report = build_risk_flag_coverage_report(
        report_id="risk-report-004",
        observed_risk_flags=["RISK_A"],
        governed_risk_flags=["RISK_A"],
    )

    packet = build_governance_coverage_packet(
        packet_id="coverage-packet-002",
        reason_code_report=reason_report,
        risk_flag_report=risk_report,
    )

    assert packet["packet_status"] == "GOVERNANCE_COVERAGE_PARTIAL"
    assert packet["operator_review_required"] is True
    assert packet["reason_code_mutation_allowed"] is False


def test_model_governance_d4_combined_packet_blocks_for_blocked_report() -> None:
    reason_report = build_reason_code_coverage_report(
        report_id="reason-report-005",
        observed_reason_codes=["REASON_A"],
        governed_reason_codes=["REASON_A"],
        blocked_reason_codes=["REASON_A"],
    )
    risk_report = build_risk_flag_coverage_report(
        report_id="risk-report-005",
        observed_risk_flags=["RISK_A"],
        governed_risk_flags=["RISK_A"],
    )

    packet = build_governance_coverage_packet(
        packet_id="coverage-packet-003",
        reason_code_report=reason_report,
        risk_flag_report=risk_report,
    )

    assert packet["packet_status"] == "GOVERNANCE_COVERAGE_BLOCKED"
    assert packet["real_execution_allowed"] is False
    assert packet["future_return_prediction_allowed"] is False


def test_model_governance_d4_validation_rejects_unsafe_packet() -> None:
    reason_report = build_reason_code_coverage_report(
        report_id="reason-report-006",
        observed_reason_codes=["A"],
        governed_reason_codes=["A"],
    )
    risk_report = build_risk_flag_coverage_report(
        report_id="risk-report-006",
        observed_risk_flags=["R"],
        governed_risk_flags=["R"],
    )
    packet = build_governance_coverage_packet(
        packet_id="coverage-packet-004",
        reason_code_report=reason_report,
        risk_flag_report=risk_report,
    )
    packet["risk_flag_deletion_allowed"] = True

    validation = validate_governance_coverage_packet(packet)

    assert validation["is_valid"] is False
    assert validation["unsafe_true_fields"] == ["risk_flag_deletion_allowed"]


def test_model_governance_d4_rejects_bad_item_type() -> None:
    with pytest.raises(ValueError):
        build_coverage_report(
            report_id="bad-report",
            item_type="TRADE_ACTION",
            observed_items=["A"],
            governed_items=["A"],
        )
