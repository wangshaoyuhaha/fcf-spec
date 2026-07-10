import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    build_validation_baseline_snapshot,
    build_validation_baseline_snapshot_index,
    build_validation_run_record,
)


def _record(result="PASS", pass_count=2057, baseline_status="REGISTERED"):
    return build_validation_run_record(
        validation_id="validation-1",
        command="python -m pytest -q",
        result=result,
        pass_count=pass_count,
        git_branch="main",
        git_head="cb1c134",
        git_status="clean",
        origin_status="synced",
        output_summary="2057 passed",
        baseline_status=baseline_status,
    )


def test_snapshot_is_read_only_snapshot_only():
    snapshot = build_validation_baseline_snapshot(_record())

    assert snapshot["validation_id"] == "validation-1"
    assert snapshot["result_status"] == "VERIFIED"
    assert snapshot["read_only"] is True
    assert snapshot["index_only"] is True
    assert snapshot["snapshot_only"] is True
    assert snapshot["validation_result_fabrication_allowed"] is False
    assert snapshot["pass_count_fabrication_allowed"] is False
    assert snapshot["source_artifact_mutation_allowed"] is False
    assert snapshot["evidence_backfill_allowed"] is False
    assert snapshot["auto_pass_allowed"] is False
    assert snapshot["operator_review_required"] is True


def test_snapshot_marks_missing_output_unresolved_without_fabrication():
    record = _record()
    record["output_summary"] = ""

    snapshot = build_validation_baseline_snapshot(record)

    assert snapshot["result_status"] == "UNRESOLVED"
    assert "MISSING_OUTPUT_SUMMARY" in snapshot["validation"]["issues"]
    assert snapshot["validation_result_fabrication_allowed"] is False
    assert snapshot["pass_count_fabrication_allowed"] is False


def test_snapshot_index_marks_stale_before_incomplete():
    packet = build_validation_baseline_snapshot_index(
        [
            _record(result="PASS", baseline_status="REGISTERED"),
            _record(result="FAIL", pass_count=0, baseline_status="INCOMPLETE"),
            _record(result="FAIL", pass_count=0, baseline_status="STALE"),
        ]
    )

    assert packet["stage"] == "D3"
    assert packet["snapshot_index_status"] == "STALE"
    assert packet["snapshot_count"] == 3
    assert packet["status_counts"]["VERIFIED"] == 1
    assert packet["status_counts"]["INCOMPLETE"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["snapshot_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False


def test_snapshot_index_unresolved_has_highest_priority():
    bad = _record()
    bad["pass_count_fabrication_allowed"] = True

    packet = build_validation_baseline_snapshot_index(
        [
            _record(result="FAIL", pass_count=0, baseline_status="STALE"),
            bad,
        ]
    )

    assert packet["snapshot_index_status"] == "UNRESOLVED"
    assert packet["status_counts"]["UNRESOLVED"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["validation_result_fabrication_allowed"] is False
    assert packet["pass_count_fabrication_allowed"] is False


def test_snapshot_index_verified_when_all_records_pass():
    packet = build_validation_baseline_snapshot_index(
        [
            _record(result="PASS", pass_count=2057),
            _record(result="PASS", pass_count=2058),
        ]
    )

    assert packet["snapshot_index_status"] == "VERIFIED"
    assert packet["snapshot_count"] == 2
    assert packet["status_counts"]["VERIFIED"] == 2
    assert packet["source_artifact_mutation_allowed"] is False
