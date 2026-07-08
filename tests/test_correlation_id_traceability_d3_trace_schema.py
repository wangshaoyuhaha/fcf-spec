from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D3_trace_schema.md"


def test_correlation_id_traceability_d3_trace_schema_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "D3 Trace Schema",
        "trace_record_id",
        "correlation_id",
        "trace_schema_version",
        "source_stage",
        "source_artifact_id",
        "source_artifact_path",
        "source_artifact_checksum",
        "parent_correlation_id",
        "child_correlation_ids",
        "validation_state",
        "review_state",
        "risk_flags_present",
        "reason_codes_present",
        "ui_reference",
        "archive_reference",
        "dify_handoff_reference",
        "trace_created_at_utc",
        "operator_review_required",
        "DATA",
        "VALIDATION",
        "OPERATOR_REVIEW",
        "UI_REPORT",
        "ARCHIVE",
        "DIFY_HANDOFF",
        "must preserve failure states",
        "must not be hidden or downgraded",
        "paper-only, local-only, read-only, sidecar-only",
    ]
    for item in required:
        assert item in text

