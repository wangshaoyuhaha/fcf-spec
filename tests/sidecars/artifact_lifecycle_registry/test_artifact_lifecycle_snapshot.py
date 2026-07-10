import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    build_artifact_state_snapshot,
    build_artifact_state_snapshot_index,
)


def _record(status="REGISTERED"):
    return {
        "artifact_id": "artifact-1",
        "artifact_type": "archive_packet",
        "artifact_path": "runtime/archive/artifact-1.json",
        "lifecycle_status": status,
    }


def test_snapshot_is_read_only_snapshot_only():
    snapshot = build_artifact_state_snapshot(_record())

    assert snapshot["artifact_id"] == "artifact-1"
    assert snapshot["result_status"] == "OBSERVED"
    assert snapshot["read_only"] is True
    assert snapshot["index_only"] is True
    assert snapshot["snapshot_only"] is True
    assert snapshot["source_artifact_mutation_allowed"] is False
    assert snapshot["artifact_status_auto_repair_allowed"] is False
    assert snapshot["evidence_backfill_allowed"] is False
    assert snapshot["correlation_id_auto_fill_allowed"] is False
    assert snapshot["placeholder_review_allowed"] is False
    assert snapshot["auto_pass_allowed"] is False
    assert snapshot["operator_review_required"] is True


def test_snapshot_marks_missing_artifact_unresolved_without_repair():
    record = _record()
    record["artifact_id"] = ""

    snapshot = build_artifact_state_snapshot(record)

    assert snapshot["result_status"] == "UNRESOLVED"
    assert "MISSING_ARTIFACT_ID" in snapshot["validation"]["issues"]
    assert snapshot["artifact_status_auto_repair_allowed"] is False
    assert snapshot["source_artifact_mutation_allowed"] is False


def test_snapshot_index_marks_stale_before_incomplete():
    records = [
        _record(status="REGISTERED"),
        _record(status="INCOMPLETE"),
        _record(status="STALE"),
    ]

    packet = build_artifact_state_snapshot_index(records)

    assert packet["stage"] == "D3"
    assert packet["snapshot_index_status"] == "STALE"
    assert packet["snapshot_count"] == 3
    assert packet["status_counts"]["OBSERVED"] == 1
    assert packet["status_counts"]["INCOMPLETE"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["snapshot_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False


def test_snapshot_index_unresolved_has_highest_priority():
    bad = _record(status="REGISTERED")
    bad["artifact_path"] = ""

    packet = build_artifact_state_snapshot_index(
        [
            _record(status="STALE"),
            bad,
        ]
    )

    assert packet["snapshot_index_status"] == "UNRESOLVED"
    assert packet["status_counts"]["UNRESOLVED"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["artifact_status_auto_repair_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False


def test_snapshot_index_observed_when_all_records_valid():
    packet = build_artifact_state_snapshot_index(
        [
            _record(status="REGISTERED"),
            _record(status="OBSERVED"),
        ]
    )

    assert packet["snapshot_index_status"] == "OBSERVED"
    assert packet["snapshot_count"] == 2
    assert packet["status_counts"]["OBSERVED"] == 2
    assert packet["source_artifact_mutation_allowed"] is False
