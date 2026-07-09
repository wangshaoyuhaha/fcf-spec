import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.archive_correlation_rollup import (
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_artifact_reference,
    build_chain_coverage_matrix,
    build_trace_summary,
    classify_trace_summary,
)


def _present_reference(link_type, correlation_id="corr-1"):
    return build_artifact_reference(
        link_type=link_type,
        artifact_id=f"{link_type}-1",
        artifact_path=f"runtime/archive/{link_type}-1.json",
        correlation_id=correlation_id,
        status="PRESENT",
    )


def test_trace_summary_complete_remains_operator_review_required():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )
    summary = build_trace_summary(matrix)
    classification = classify_trace_summary(summary)

    assert summary["rollup_status"] == "COMPLETE"
    assert summary["covered_link_count"] == len(CORRELATION_ROLLUP_REQUIRED_LINKS)
    assert summary["read_only"] is True
    assert summary["index_only"] is True
    assert summary["summary_only"] is True
    assert summary["source_mutation_allowed"] is False
    assert summary["evidence_backfill_allowed"] is False
    assert summary["correlation_id_auto_fill_allowed"] is False
    assert summary["placeholder_review_allowed"] is False
    assert summary["auto_pass_allowed"] is False
    assert summary["operator_review_required"] is True
    assert classification["trace_action"] == "READY_FOR_OPERATOR_REVIEW"
    assert classification["auto_pass_allowed"] is False


def test_trace_summary_marks_incomplete_without_backfill():
    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=[_present_reference("data_snapshot")],
    )
    summary = build_trace_summary(matrix)
    classification = classify_trace_summary(summary)

    assert summary["rollup_status"] == "INCOMPLETE"
    assert summary["missing_link_count"] == len(CORRELATION_ROLLUP_REQUIRED_LINKS) - 1
    assert "candidate" in summary["missing_links"]
    assert summary["evidence_backfill_allowed"] is False
    assert classification["trace_action"] == "MARK_INCOMPLETE"
    assert classification["auto_repair_allowed"] is False


def test_trace_summary_marks_stale_without_placeholder_review():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    references[4] = build_artifact_reference(
        link_type="review_packet",
        artifact_id="review-stale",
        artifact_path="runtime/archive/review-stale.json",
        correlation_id="corr-1",
        status="STALE",
    )

    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )
    summary = build_trace_summary(matrix)
    classification = classify_trace_summary(summary)

    assert summary["rollup_status"] == "STALE"
    assert "review_packet" in summary["stale_links"]
    assert summary["placeholder_review_allowed"] is False
    assert classification["trace_action"] == "MARK_STALE"


def test_trace_summary_marks_unresolved_without_auto_fill():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    references[2] = _present_reference(
        "ai_explanation",
        correlation_id="corr-2",
    )

    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )
    summary = build_trace_summary(matrix)
    classification = classify_trace_summary(summary)

    assert summary["rollup_status"] == "UNRESOLVED"
    assert "CORRELATION_ID_MISMATCH" in summary["unresolved_issues"]
    assert summary["correlation_id_auto_fill_allowed"] is False
    assert classification["trace_action"] == "MARK_UNRESOLVED"


def test_trace_summary_requires_correlation_id():
    try:
        build_trace_summary(
            {
                "coverage_matrix": {},
                "rollup_status": "UNRESOLVED",
            }
        )
    except ValueError as exc:
        assert "correlation_id is required" in str(exc)
    else:
        raise AssertionError("missing correlation_id should fail")
