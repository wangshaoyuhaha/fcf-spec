"""Tests for SIGNAL-VALIDATION-D5 validation report packet."""

from __future__ import annotations

from apps.signal_validation_app.evidence_matrix import (
    build_evidence_matrix,
    build_evidence_row,
)
from apps.signal_validation_app.validation_report import (
    build_validation_report_packet,
    infer_validation_report_status,
    summarize_validation_report_packet,
    validate_validation_report_packet,
)


def test_signal_validation_d5_builds_ready_report_packet() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-001",
        candidate_id="candidate-d5-001",
        evidence_rows=[
            build_evidence_row(
                layer_id="STOCK-APP-1",
                evidence_state="SUPPORTED",
                source_id="ranked_watchlist",
                source_status="AVAILABLE",
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )

    packet = build_validation_report_packet(
        matrix=matrix,
        report_id="report-d5-001",
        source_manifest_summary={"loader_status": "ALL_CONFIGURED_SOURCES_AVAILABLE"},
    )
    summary = summarize_validation_report_packet(packet)
    validation = validate_validation_report_packet(packet)

    assert packet["app_id"] == "SIGNAL-VALIDATION-APP-1"
    assert packet["stage_id"] == "SIGNAL-VALIDATION-D5"
    assert packet["report_status"] == "VALIDATION_READY_FOR_OPERATOR_REVIEW"
    assert packet["operator_review_required"] is True
    assert packet["operator_review_bypass_allowed"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False
    assert validation["is_valid"] is True


def test_signal_validation_d5_builds_conflict_report_packet() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-002",
        candidate_id="candidate-d5-002",
        evidence_rows=[
            build_evidence_row(
                layer_id="STOCK-APP-1",
                evidence_state="SUPPORTED",
                source_id="ranked_watchlist",
                source_status="AVAILABLE",
            ),
            build_evidence_row(
                layer_id="DATA-QUALITY-OPS-APP-1",
                evidence_state="CONFLICT",
                source_id="data_quality_issue_list",
                source_status="AVAILABLE",
                risk_flags=["DATA_QUALITY_ISSUE"],
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )

    packet = build_validation_report_packet(matrix=matrix, report_id="report-d5-002")

    assert packet["report_status"] == "VALIDATION_CONFLICT_DETECTED"
    assert packet["conflict_summary"]["high_conflict_count"] == 1
    assert packet["trade_action_enabled"] is False
    assert packet["automatic_position_sizing_allowed"] is False


def test_signal_validation_d5_builds_blocked_report_when_operator_missing() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-003",
        candidate_id="candidate-d5-003",
        evidence_rows=[
            build_evidence_row(
                layer_id="STOCK-APP-1",
                evidence_state="SUPPORTED",
                source_id="ranked_watchlist",
                source_status="AVAILABLE",
            )
        ],
    )

    packet = build_validation_report_packet(matrix=matrix, report_id="report-d5-003")

    assert packet["report_status"] == "VALIDATION_BLOCKED"
    assert packet["conflict_summary"]["blocking_conflict_count"] == 1
    assert packet["operator_review_packet"]["no_execution_receipt_required"] is True


def test_signal_validation_d5_infer_report_status() -> None:
    assert infer_validation_report_status({"detection_status": "VALIDATION_BLOCKED"}) == "VALIDATION_BLOCKED"
    assert infer_validation_report_status({"detection_status": "CONFLICT_DETECTED"}) == "VALIDATION_CONFLICT_DETECTED"
    assert infer_validation_report_status({"detection_status": "NO_CONFLICT_DETECTED"}) == "VALIDATION_READY_FOR_OPERATOR_REVIEW"
    assert infer_validation_report_status({"detection_status": "REVIEW_REQUIRED"}) == "VALIDATION_REVIEW_REQUIRED"


def test_signal_validation_d5_rejects_unsafe_packet_field() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-004",
        candidate_id="candidate-d5-004",
        evidence_rows=[
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            )
        ],
    )
    packet = build_validation_report_packet(matrix=matrix, report_id="report-d5-004")
    packet["real_execution_allowed"] = True

    validation = validate_validation_report_packet(packet)

    assert validation["is_valid"] is False
    assert validation["unsafe_fields"] == ["real_execution_allowed"]


def test_signal_validation_d5_packet_blocks_prediction_and_guarantee_claims() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-005",
        candidate_id="candidate-d5-005",
        evidence_rows=[
            build_evidence_row(
                layer_id="BACKTEST-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="backtest_review_packet",
                source_status="AVAILABLE",
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )
    packet = build_validation_report_packet(matrix=matrix, report_id="report-d5-005")

    assert packet["future_return_prediction_allowed"] is False
    assert packet["guaranteed_performance_claim_allowed"] is False
    assert packet["limitations"]
    assert "validation_status_is_not_a_trade_instruction" in packet["limitations"]


def test_signal_validation_d5_summary_is_compact_and_safe() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d5-006",
        candidate_id="candidate-d5-006",
        evidence_rows=[
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            )
        ],
    )
    packet = build_validation_report_packet(matrix=matrix, report_id="report-d5-006")
    summary = summarize_validation_report_packet(packet)

    assert summary["report_id"] == "report-d5-006"
    assert summary["operator_review_required"] is True
    assert summary["trade_action_enabled"] is False
    assert summary["future_return_prediction_allowed"] is False
    assert summary["guaranteed_performance_claim_allowed"] is False
