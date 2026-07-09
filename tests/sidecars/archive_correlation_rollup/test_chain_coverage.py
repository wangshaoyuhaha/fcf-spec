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
    summarize_chain_coverage,
)


def _present_reference(link_type, correlation_id="corr-1"):
    return build_artifact_reference(
        link_type=link_type,
        artifact_id=f"{link_type}-1",
        artifact_path=f"runtime/archive/{link_type}-1.json",
        correlation_id=correlation_id,
        status="PRESENT",
    )


def test_chain_coverage_complete_when_all_required_links_present():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    packet = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )

    assert packet["rollup_status"] == "COMPLETE"
    assert packet["missing_links"] == []
    assert packet["stale_links"] == []
    assert packet["unresolved_issues"] == []
    assert len(packet["covered_links"]) == len(CORRELATION_ROLLUP_REQUIRED_LINKS)
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["source_mutation_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["correlation_id_auto_fill_allowed"] is False
    assert packet["placeholder_review_allowed"] is False
    assert packet["auto_pass_allowed"] is False
    assert packet["operator_review_required"] is True


def test_chain_coverage_marks_missing_links_incomplete_without_backfill():
    references = [_present_reference("data_snapshot")]

    packet = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )

    candidate_row = packet["coverage_matrix"]["candidate"]

    assert packet["rollup_status"] == "INCOMPLETE"
    assert "candidate" in packet["missing_links"]
    assert candidate_row["covered"] is False
    assert candidate_row["status"] == "INCOMPLETE"
    assert "MISSING_LINK" in candidate_row["issues"]
    assert packet["evidence_backfill_allowed"] is False


def test_chain_coverage_marks_mismatched_correlation_id_unresolved():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    references[2] = _present_reference(
        "ai_explanation",
        correlation_id="corr-2",
    )

    packet = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )

    assert packet["rollup_status"] == "UNRESOLVED"
    assert "CORRELATION_ID_MISMATCH" in packet["unresolved_issues"]
    assert packet["coverage_matrix"]["ai_explanation"]["covered"] is False


def test_chain_coverage_marks_stale_reference_stale():
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

    packet = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )

    review_row = packet["coverage_matrix"]["review_packet"]

    assert packet["rollup_status"] == "STALE"
    assert "review_packet" in packet["stale_links"]
    assert review_row["status"] == "STALE"
    assert packet["auto_pass_allowed"] is False


def test_chain_coverage_requires_correlation_id():
    try:
        build_chain_coverage_matrix(correlation_id="", references=[])
    except ValueError as exc:
        assert "correlation_id is required" in str(exc)
    else:
        raise AssertionError("empty correlation_id should fail")


def test_summarize_chain_coverage_is_read_only_index_summary():
    references = [_present_reference("data_snapshot")]

    packet = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )

    summary = summarize_chain_coverage(packet)

    assert summary["correlation_id"] == "corr-1"
    assert summary["rollup_status"] == "INCOMPLETE"
    assert summary["total_required_links"] == len(CORRELATION_ROLLUP_REQUIRED_LINKS)
    assert summary["covered_link_count"] == 1
    assert summary["missing_link_count"] == len(CORRELATION_ROLLUP_REQUIRED_LINKS) - 1
    assert summary["coverage_ratio"] == 1 / len(CORRELATION_ROLLUP_REQUIRED_LINKS)
    assert summary["read_only"] is True
    assert summary["index_only"] is True
    assert summary["auto_pass_allowed"] is False
    assert summary["operator_review_required"] is True

