import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    ALLOWED_VALIDATION_RESULTS,
    build_validation_run_index,
    build_validation_run_record,
    validate_validation_run_record,
)


def _record(result="PASS", pass_count=2049, baseline_status="REGISTERED"):
    return build_validation_run_record(
        validation_id="validation-1",
        command="python -m pytest -q",
        result=result,
        pass_count=pass_count,
        git_branch="main",
        git_head="c6dcae0",
        git_status="clean",
        origin_status="synced",
        output_summary="2049 passed",
        baseline_status=baseline_status,
    )


def test_allowed_validation_results_are_explicit():
    assert "PASS" in ALLOWED_VALIDATION_RESULTS
    assert "FAIL" in ALLOWED_VALIDATION_RESULTS
    assert "INCOMPLETE" in ALLOWED_VALIDATION_RESULTS
    assert "STALE" in ALLOWED_VALIDATION_RESULTS
    assert "UNRESOLVED" in ALLOWED_VALIDATION_RESULTS


def test_build_validation_run_record_is_read_only():
    record = _record()

    assert record["result"] == "PASS"
    assert record["pass_count"] == 2049
    assert record["read_only"] is True
    assert record["index_only"] is True
    assert record["validation_result_fabrication_allowed"] is False
    assert record["pass_count_fabrication_allowed"] is False
    assert record["source_artifact_mutation_allowed"] is False
    assert record["evidence_backfill_allowed"] is False
    assert record["auto_pass_allowed"] is False
    assert record["operator_review_required"] is True


def test_build_validation_run_record_rejects_unknown_result():
    try:
        build_validation_run_record(
            validation_id="validation-1",
            command="python -m pytest -q",
            result="MADE_UP",
            pass_count=2049,
            git_branch="main",
            git_head="c6dcae0",
            git_status="clean",
            origin_status="synced",
            output_summary="2049 passed",
        )
    except ValueError as exc:
        assert "unsupported validation result" in str(exc)
    else:
        raise AssertionError("unknown result should fail")


def test_validate_run_record_pass_is_verified_without_fabrication():
    result = validate_validation_run_record(_record())

    assert result["valid"] is True
    assert result["result_status"] == "VERIFIED"
    assert result["validation_result_fabrication_allowed"] is False
    assert result["pass_count_fabrication_allowed"] is False
    assert result["auto_pass_allowed"] is False


def test_validate_run_record_missing_summary_unresolved():
    record = _record()
    record["output_summary"] = ""

    result = validate_validation_run_record(record)

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "MISSING_OUTPUT_SUMMARY" in result["issues"]


def test_validate_run_record_pass_without_count_unresolved():
    result = validate_validation_run_record(_record(pass_count=0))

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "PASS_WITHOUT_PASS_COUNT" in result["issues"]


def test_validation_run_index_marks_stale_and_incomplete():
    packet = build_validation_run_index(
        [
            _record(result="PASS", baseline_status="REGISTERED"),
            _record(result="FAIL", pass_count=0, baseline_status="STALE"),
            _record(result="INCOMPLETE", pass_count=0, baseline_status="INCOMPLETE"),
        ]
    )

    assert packet["stage"] == "D2"
    assert packet["run_index_status"] == "STALE"
    assert packet["record_count"] == 3
    assert packet["status_counts"]["VERIFIED"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["status_counts"]["INCOMPLETE"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["auto_pass_allowed"] is False


def test_validation_run_index_unresolved_has_highest_priority():
    bad = _record()
    bad["pass_count_fabrication_allowed"] = True

    packet = build_validation_run_index([_record(), bad])

    assert packet["run_index_status"] == "UNRESOLVED"
    assert packet["status_counts"]["UNRESOLVED"] == 1
    assert packet["validation_result_fabrication_allowed"] is False
    assert packet["pass_count_fabrication_allowed"] is False
