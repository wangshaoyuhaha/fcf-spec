"""Tests for SIGNAL-VALIDATION-D4 conflict detector."""

from __future__ import annotations

from apps.signal_validation_app.conflict_detector import (
    detect_signal_conflicts,
    summarize_conflict_detection,
)
from apps.signal_validation_app.evidence_matrix import (
    build_evidence_matrix,
    build_evidence_row,
)


def test_signal_validation_d4_detects_data_quality_vs_stock_conflict() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-001",
        candidate_id="candidate-d4-001",
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

    report = detect_signal_conflicts(matrix)

    assert report["detection_status"] == "CONFLICT_DETECTED"
    assert report["high_conflict_count"] == 1
    assert any(
        conflict["conflict_type"] == "HIGH_SCORE_WITH_DATA_QUALITY_ISSUE"
        for conflict in report["conflicts"]
    )
    assert report["trade_action_enabled"] is False
    assert report["real_execution_allowed"] is False


def test_signal_validation_d4_detects_scenario_backtest_mismatch() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-002",
        candidate_id="candidate-d4-002",
        evidence_rows=[
            build_evidence_row(
                layer_id="MARKET-SCENARIO-APP-1",
                evidence_state="SUPPORTED",
                source_id="scenario_packet",
                source_status="AVAILABLE",
            ),
            build_evidence_row(
                layer_id="BACKTEST-REVIEW-APP-1",
                evidence_state="PARTIAL",
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

    report = detect_signal_conflicts(matrix)

    assert any(
        conflict["conflict_type"] == "SCENARIO_BACKTEST_MISMATCH"
        for conflict in report["conflicts"]
    )
    assert report["operator_review_required"] is True


def test_signal_validation_d4_blocks_when_operator_review_missing() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-003",
        candidate_id="candidate-d4-003",
        evidence_rows=[
            build_evidence_row(
                layer_id="STOCK-APP-1",
                evidence_state="SUPPORTED",
                source_id="ranked_watchlist",
                source_status="AVAILABLE",
            )
        ],
    )

    report = detect_signal_conflicts(matrix)

    assert report["detection_status"] == "VALIDATION_BLOCKED"
    assert report["blocking_conflict_count"] == 1
    assert any(
        conflict["conflict_type"] == "OPERATOR_REVIEW_MISSING"
        for conflict in report["conflicts"]
    )


def test_signal_validation_d4_detects_partial_sources() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-004",
        candidate_id="candidate-d4-004",
        evidence_rows=[
            build_evidence_row(
                layer_id="BACKTEST-REVIEW-APP-1",
                evidence_state="MISSING",
                source_id="backtest_review_packet",
                source_status="MISSING_REQUIRED",
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )

    report = detect_signal_conflicts(matrix)

    assert any(
        conflict["conflict_type"] == "SOURCE_MISSING_OR_PARTIAL"
        for conflict in report["conflicts"]
    )
    assert "backtest_review_packet" in [
        ref
        for conflict in report["conflicts"]
        for ref in conflict["evidence_refs"]
    ]


def test_signal_validation_d4_detects_archive_integrity_gap() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-005",
        candidate_id="candidate-d4-005",
        evidence_rows=[
            build_evidence_row(
                layer_id="REPORT-ARCHIVE-APP-1",
                evidence_state="SUPPORTED",
                source_id="archive_manifest",
                source_status="AVAILABLE",
                risk_flags=["CHECKSUM_MISSING"],
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )

    report = detect_signal_conflicts(matrix)

    assert any(
        conflict["conflict_type"] == "ARCHIVE_INTEGRITY_GAP"
        for conflict in report["conflicts"]
    )


def test_signal_validation_d4_no_conflict_for_clean_supported_matrix() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-006",
        candidate_id="candidate-d4-006",
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

    report = detect_signal_conflicts(matrix)
    summary = summarize_conflict_detection(report)

    assert report["detection_status"] == "NO_CONFLICT_DETECTED"
    assert report["conflict_count"] == 0
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False


def test_signal_validation_d4_ai_positive_with_risk_requires_review() -> None:
    matrix = build_evidence_matrix(
        matrix_id="matrix-d4-007",
        candidate_id="candidate-d4-007",
        evidence_rows=[
            build_evidence_row(
                layer_id="AI-CONTEXT-1",
                evidence_state="SUPPORTED",
                source_id="explanation_report",
                source_status="AVAILABLE",
            ),
            build_evidence_row(
                layer_id="BACKTEST-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="backtest_review_packet",
                source_status="AVAILABLE",
                risk_flags=["HISTORICAL_LIMITATION"],
            ),
            build_evidence_row(
                layer_id="OPERATOR-REVIEW-APP-1",
                evidence_state="SUPPORTED",
                source_id="operator_review_record",
                source_status="AVAILABLE",
            ),
        ],
    )

    report = detect_signal_conflicts(matrix)

    assert any(
        conflict["conflict_type"] == "POSITIVE_EXPLANATION_WITH_RISK_FLAG"
        for conflict in report["conflicts"]
    )
    assert report["future_return_prediction_allowed"] is False
    assert report["guaranteed_performance_claim_allowed"] is False
