"""Tests for SIGNAL-VALIDATION-D3 evidence matrix schema."""

from __future__ import annotations

import pytest

from apps.signal_validation_app.evidence_matrix import (
    ALLOWED_EVIDENCE_LAYERS,
    build_evidence_matrix,
    build_evidence_row,
    infer_overall_validation_status,
    validate_evidence_matrix_payload,
)


def test_signal_validation_d3_builds_supported_evidence_matrix() -> None:
    rows = [
        build_evidence_row(
            layer_id="STOCK-APP-1",
            evidence_state="SUPPORTED",
            source_id="ranked_watchlist",
            source_status="AVAILABLE",
            reason_codes=["SCORE_BREAKDOWN_PRESENT"],
        ),
        build_evidence_row(
            layer_id="BACKTEST-REVIEW-APP-1",
            evidence_state="SUPPORTED",
            source_id="backtest_review_packet",
            source_status="AVAILABLE",
            risk_flags=["HISTORICAL_LIMITATION_ACKNOWLEDGED"],
        ),
    ]

    matrix = build_evidence_matrix(
        matrix_id="matrix-001",
        candidate_id="candidate-001",
        evidence_rows=rows,
        notes=["paper review only"],
    )
    payload = matrix.to_dict()

    assert payload["matrix_id"] == "matrix-001"
    assert payload["candidate_id"] == "candidate-001"
    assert payload["overall_validation_status"] == "EVIDENCE_COMPLETE"
    assert payload["operator_review_required"] is True
    assert payload["trade_action_enabled"] is False
    assert payload["real_execution_allowed"] is False
    assert payload["automatic_position_sizing_allowed"] is False
    assert payload["future_return_prediction_allowed"] is False


def test_signal_validation_d3_conflict_sets_conflict_status() -> None:
    rows = [
        build_evidence_row(
            layer_id="AI-CONTEXT-1",
            evidence_state="SUPPORTED",
            source_id="explanation_report",
            source_status="AVAILABLE",
        ),
        build_evidence_row(
            layer_id="DATA-QUALITY-OPS-APP-1",
            evidence_state="CONFLICT",
            source_id="quality_issue_list",
            source_status="AVAILABLE",
            conflicts=["HIGH_SCORE_WITH_DATA_QUALITY_ISSUE"],
        ),
    ]

    assert infer_overall_validation_status(rows) == "CONFLICT_DETECTED"


def test_signal_validation_d3_missing_or_partial_sets_partial_status() -> None:
    rows = [
        build_evidence_row(
            layer_id="MARKET-SCENARIO-APP-1",
            evidence_state="PARTIAL",
            source_id="scenario_packet",
            source_status="AVAILABLE",
        )
    ]

    assert infer_overall_validation_status(rows) == "EVIDENCE_PARTIAL"


def test_signal_validation_d3_blocked_sets_blocked_status() -> None:
    rows = [
        build_evidence_row(
            layer_id="BACKTEST-REVIEW-APP-1",
            evidence_state="BLOCKED",
            source_id="backtest_review_packet",
            source_status="MISSING_REQUIRED",
        )
    ]

    assert infer_overall_validation_status(rows) == "VALIDATION_BLOCKED"


def test_signal_validation_d3_rejects_unsupported_layer() -> None:
    assert "UNKNOWN-LAYER" not in ALLOWED_EVIDENCE_LAYERS

    with pytest.raises(ValueError):
        build_evidence_row(
            layer_id="UNKNOWN-LAYER",
            evidence_state="SUPPORTED",
            source_id="bad",
            source_status="AVAILABLE",
        )


def test_signal_validation_d3_rejects_unsupported_state() -> None:
    with pytest.raises(ValueError):
        build_evidence_row(
            layer_id="STOCK-APP-1",
            evidence_state="BUY_NOW",
            source_id="bad",
            source_status="AVAILABLE",
        )


def test_signal_validation_d3_schema_validation_rejects_trade_fields() -> None:
    row = build_evidence_row(
        layer_id="STOCK-APP-1",
        evidence_state="SUPPORTED",
        source_id="ranked_watchlist",
        source_status="AVAILABLE",
    )
    payload = build_evidence_matrix(
        matrix_id="matrix-002",
        candidate_id="candidate-002",
        evidence_rows=[row],
    ).to_dict()

    payload["buy_instruction"] = "forbidden"

    validation = validate_evidence_matrix_payload(payload)

    assert validation["is_valid"] is False
    assert validation["forbidden_fields_present"] == ["buy_instruction"]
    assert validation["trade_action_enabled"] is False
    assert validation["real_execution_allowed"] is False


def test_signal_validation_d3_schema_validation_accepts_safe_payload() -> None:
    row = build_evidence_row(
        layer_id="OPERATOR-REVIEW-APP-1",
        evidence_state="REVIEW_REQUIRED",
        source_id="operator_review_record",
        source_status="AVAILABLE",
    )
    payload = build_evidence_matrix(
        matrix_id="matrix-003",
        candidate_id="candidate-003",
        evidence_rows=[row],
    ).to_dict()

    validation = validate_evidence_matrix_payload(payload)

    assert validation["is_valid"] is True
    assert validation["missing_fields"] == []
    assert validation["forbidden_fields_present"] == []
    assert validation["operator_review_required"] is True
