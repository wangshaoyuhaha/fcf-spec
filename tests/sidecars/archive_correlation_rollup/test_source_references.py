import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.archive_correlation_rollup import (
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_artifact_reference,
    build_reference_index,
    validate_artifact_reference,
)


def test_build_artifact_reference_is_read_only_metadata_only():
    reference = build_artifact_reference(
        link_type="data_snapshot",
        artifact_id="snapshot-1",
        artifact_path="runtime/archive/snapshot-1.json",
        correlation_id="corr-1",
        status="PRESENT",
        source_stage="DATA-APP-1",
        checksum_sha256="abc",
        notes=["existing artifact only"],
    )

    assert reference["link_type"] == "data_snapshot"
    assert reference["correlation_id"] == "corr-1"
    assert reference["read_only"] is True
    assert reference["source_mutation_allowed"] is False
    assert reference["evidence_backfill_allowed"] is False
    assert reference["correlation_id_auto_fill_allowed"] is False
    assert reference["placeholder_generation_allowed"] is False


def test_present_reference_requires_existing_correlation_id():
    try:
        build_artifact_reference(
            link_type="candidate",
            artifact_id="candidate-1",
            artifact_path="runtime/archive/candidate-1.json",
            correlation_id=None,
            status="PRESENT",
        )
    except ValueError as exc:
        assert "PRESENT reference requires correlation_id" in str(exc)
    else:
        raise AssertionError("missing correlation_id should fail")


def test_artifact_reference_rejects_unknown_link_type():
    try:
        build_artifact_reference(
            link_type="unknown",
            artifact_id="x",
            artifact_path="runtime/archive/x.json",
            correlation_id="corr-1",
            status="PRESENT",
        )
    except ValueError_repair_allowed"] is False


def test_build_reference_index_marks_missing_chain_incomplete():
    references = [
        build_artifact_reference(
            link_type="data_snapshot",
            artifact_id="snapshot-1",
            artifact_path="runtime/archive/snapshot-1.json",
            correlation_id="corr-1",
            status="PRESENT",
        )
    ]

    index = build_reference_index(references)

    assert index["rollup_status"] == "INCOMPLETE"
    assert "candidate" in index["missing_link_types"]
    assert index["read_only"] is True
    assert index["index_only"] is True
    assert index["source_mutation_allowed"] is False
    assert index["evidence_backfill_allowed"] is False
    assert index["correlation_id_auto_fill_allowed"] is False
    assert index["placeholder_generation_allowed"] is False
    assert index["operator_review_required"] is True


def test_build_reference_index_complete_when_all_required_links_present():
    references = [
        build_artifact_reference(
            link_type=link_type,
            artifact_id=f"{link_type}-1",
            artifact_path=f"runtime/archive/{link_type}-1.json",
            correlation_id="corr-1",
            status="PRESENT",
        )
        for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS
    ]

    index = build_reference_index(references)

    assert index["rollup_status"] == "COMPLETE"
    assert index["missing_link_types"] == []
    assert len(index["validation_results"]) == len(CORRELATION_ROLLUP_REQUIRED_LINKS)


def test_build_reference_index_marks_invalid_present_as_unresolved():
    references = [
        {
            "link_type": link_type,
            "artifact_id": f"{link_type}-1",
            "artifact_path": f"runtime/archive/{link_type}-1.json",
            "correlation_id": "corr-1",
            "status": "PRESENT",
            "source_mutation_allowed": False,
            "evidence_backfill_allowed": False,
            "correlation_id_auto_fill_allowed": False,
            "placeholder_generation_allowed": False,
        }
        for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS
    ]
    references[3]["correlation_id"] = None

    index = build_reference_index(references)

    assert index["rollup_status"] == "UNRESOLVED"
    assert index["missing_link_types"] == []
    assert any(
        "PRESENT_WITHOUT_CORRELATION_ID" in result["issues"]
        for result in index["validation_results"]
    )
