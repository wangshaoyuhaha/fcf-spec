import pytest

from sidecars.archive_correlation_rollup_app_1 import (
    CorrelationRollupRecord,
    build_correlation_id,
    build_rollup_record,
    infer_rollup_scope,
    validate_rollup_record,
)


def test_d3_builds_stable_correlation_id():
    assert (
        build_correlation_id(
            "ARCHIVE-CORRELATION-ROLLUP-APP-1",
            "D3",
            "final_current_state",
        )
        == "CORR-ARCHIVE-CORRELATION-ROLLUP-APP-1-D3-FINAL-CURRENT-STATE"
    )


def test_d3_infers_scope_from_artifact_type():
    assert infer_rollup_scope("final_current_state") == "final_current_state"
    assert infer_rollup_scope("control_center") == "control_center"
    assert infer_rollup_scope("backend_handoff") == "handoff"


def test_d3_builds_rollup_record_from_final_current_state_path():
    record = build_rollup_record(
        artifact_path="FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        source_app="UI-RISK-FLAG-VISIBILITY-APP-1",
        source_phase="FINAL",
    )

    assert record.correlation_id == (
        "CORR-UI-RISK-FLAG-VISIBILITY-APP-1-FINAL-FINAL-CURRENT-STATE"
    )
    assert record.artifact_type == "final_current_state"
    assert record.rollup_scope == "final_current_state"
    assert record.trace_state == "trace_ready"


def test_d3_validates_control_center_record():
    record = build_rollup_record(
        artifact_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        source_app="CONTROL-CENTER-MAINTENANCE-APP-2",
        source_phase="FINAL",
    )

    valid, issues = validate_rollup_record(record)

    assert valid is True
    assert issues == ()


def test_d3_rejects_unknown_artifact_type():
    record = CorrelationRollupRecord(
        correlation_id="CORR-UNKNOWN",
        artifact_path="runtime/generated.json",
        artifact_type="unknown",
        source_app="ARCHIVE-CORRELATION-ROLLUP-APP-1",
        source_phase="D3",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
        rollup_scope="report",
        trace_state="trace_ready",
    )

    valid, issues = validate_rollup_record(record)

    assert valid is False
    assert "unknown_artifact_type" in issues


def test_d3_build_rollup_record_raises_for_unknown_path():
    with pytest.raises(ValueError):
        build_rollup_record(
            artifact_path="runtime/generated.json",
            source_app="ARCHIVE-CORRELATION-ROLLUP-APP-1",
            source_phase="D3",
        )
