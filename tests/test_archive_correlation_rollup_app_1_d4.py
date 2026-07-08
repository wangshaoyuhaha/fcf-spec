import pytest

from sidecars.archive_correlation_rollup_app_1 import (
    CorrelationRollupRecord,
    build_trace_summaries,
    build_trace_summary,
    infer_summary_state,
)


def _record(path, artifact_type, scope, trace_state="trace_ready"):
    return CorrelationRollupRecord(
        correlation_id="CORR-ARCHIVE-ROLLUP-D4",
        artifact_path=path,
        artifact_type=artifact_type,
        source_app="ARCHIVE-CORRELATION-ROLLUP-APP-1",
        source_phase="D4",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
        rollup_scope=scope,
        trace_state=trace_state,
    )


def test_d4_infers_complete_summary_state():
    assert infer_summary_state(["trace_ready"]) == "complete"


def test_d4_infers_partial_summary_state():
    assert infer_summary_state(["trace_ready", "trace_partial"]) == "partial"


def test_d4_infers_blocked_summary_state():
    assert infer_summary_state(["trace_ready", "trace_blocked"]) == "blocked"


def test_d4_builds_trace_summary_for_multiple_artifacts():
    records = [
        _record(
            "FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
            "final_current_state",
            "final_current_state",
        ),
        _record(
            "docs/FCF_PROJECT_CONTROL_CENTER.md",
            "control_center",
            "control_center",
        ),
    ]

    summary = build_trace_summary("CORR-ARCHIVE-ROLLUP-D4", records)

    assert summary.correlation_id == "CORR-ARCHIVE-ROLLUP-D4"
    assert summary.record_count == 2
    assert summary.artifact_types == ("control_center", "final_current_state")
    assert summary.rollup_scopes == ("control_center", "final_current_state")
    assert summary.trace_states == ("trace_ready",)
    assert summary.operator_review_required is True
    assert summary.summary_state == "complete"


def test_d4_builds_grouped_trace_summaries():
    first = _record(
        "FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        "final_current_state",
        "final_current_state",
    )
    second = CorrelationRollupRecord(
        correlation_id="CORR-ARCHIVE-ROLLUP-D4-BLOCKED",
        artifact_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        artifact_type="control_center",
        source_app="ARCHIVE-CORRELATION-ROLLUP-APP-1",
        source_phase="D4",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
        rollup_scope="control_center",
        trace_state="trace_blocked",
    )

    summaries = build_trace_summaries([second, first])

    assert tuple(summaries.keys()) == (
        "CORR-ARCHIVE-ROLLUP-D4",
        "CORR-ARCHIVE-ROLLUP-D4-BLOCKED",
    )
    assert summaries["CORR-ARCHIVE-ROLLUP-D4-BLOCKED"].summary_state == "blocked"
    assert summaries["CORR-ARCHIVE-ROLLUP-D4-BLOCKED"].has_blocked_trace is True


def test_d4_rejects_empty_trace_summary():
    with pytest.raises(ValueError, match="empty_rollup_records"):
        build_trace_summary("CORR-EMPTY", [])


def test_d4_rejects_correlation_id_mismatch():
    record = _record(
        "FCF_CURRENT_STATE_UI_RISK_FLAG_VISIBILITY_APP_1_FINAL.md",
        "final_current_state",
        "final_current_state",
    )

    with pytest.raises(ValueError, match="correlation_id_mismatch"):
        build_trace_summary("CORR-OTHER", [record])
