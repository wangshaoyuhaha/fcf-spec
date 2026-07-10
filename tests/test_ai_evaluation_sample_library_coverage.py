import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.coverage_checks import (
    COVERAGE_SCHEMA_VERSION,
    COVERAGE_STAGE_ID,
    build_evaluation_sample_coverage_report,
    validate_evaluation_sample_coverage_report,
)
from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    build_evaluation_sample_registry,
)
from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    EVALUATION_DIMENSIONS,
    build_evaluation_sample_record,
)


def make_record(
    dimension: str,
    *,
    review_status: str = "APPROVED",
) -> dict:
    sample_id = f"sample-{dimension}"

    return build_evaluation_sample_record(
        sample_id=sample_id,
        sample_version="1.0.0",
        title=f"Evaluation sample for {dimension}",
        evaluation_dimension=dimension,
        input_payload_ref=f"local://samples/{sample_id}.json",
        expected_outcome="PASS",
        expected_summary="Expected governance result.",
        expected_reason_codes=("REASON_PRESENT",),
        expected_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{dimension}",),
        registry_entry_ids=(f"registry-{dimension}",),
        created_at_utc="2026-07-10T12:00:00Z",
        review_status=review_status,
    )


def make_registry(
    *,
    review_status: str = "APPROVED",
) -> dict:
    records = tuple(
        make_record(
            dimension,
            review_status=review_status,
        )
        for dimension in EVALUATION_DIMENSIONS
    )

    return build_evaluation_sample_registry(
        registry_id="evaluation-library-coverage",
        records=records,
        created_at_utc="2026-07-10T13:00:00Z",
    )


def test_coverage_report_identity() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )

    assert report["stage_id"] == COVERAGE_STAGE_ID
    assert report["schema_version"] == COVERAGE_SCHEMA_VERSION
    assert (
        report["source_registry_id"]
        == "evaluation-library-coverage"
    )


def test_complete_approved_library_passes() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )

    assert report["coverage_status"] == "PASS"
    assert report["missing_dimensions"] == []
    assert report["pending_review_keys"] == []


def test_dimension_counts_cover_all_dimensions() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )

    assert report["dimension_counts"] == {
        dimension: 1
        for dimension in EVALUATION_DIMENSIONS
    }


def test_pending_samples_require_review() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry(review_status="REVIEW_REQUIRED")
    )

    assert report["coverage_status"] == "REVIEW_REQUIRED"
    assert len(report["pending_review_keys"]) == len(
        EVALUATION_DIMENSIONS
    )


def test_missing_dimension_fails() -> None:
    registry = make_registry()
    removed_dimension = registry["entries"][-1][
        "evaluation_dimension"
    ]
    registry["entries"] = registry["entries"][:-1]

    report = build_evaluation_sample_coverage_report(registry)

    assert report["coverage_status"] == "FAIL"
    assert removed_dimension in report["missing_dimensions"]

def test_invalid_dimension_fails() -> None:
    registry = make_registry()
    registry["entries"][0]["evaluation_dimension"] = (
        "trade_execution"
    )

    report = build_evaluation_sample_coverage_report(registry)

    assert report["coverage_status"] == "FAIL"
    assert report["invalid_dimension_keys"]


def test_duplicate_sample_key_fails() -> None:
    registry = make_registry()
    registry["entries"].append(
        deepcopy(registry["entries"][0])
    )

    report = build_evaluation_sample_coverage_report(registry)

    assert report["coverage_status"] == "FAIL"
    assert report["duplicate_sample_keys"]


def test_missing_evidence_fails() -> None:
    registry = make_registry()
    registry["entries"][0]["evidence_refs"] = []

    report = build_evaluation_sample_coverage_report(registry)

    assert report["coverage_status"] == "FAIL"
    assert report["evidence_missing_keys"]


def test_missing_registry_reference_fails() -> None:
    registry = make_registry()
    registry["entries"][0][
        "prompt_model_registry_entry_ids"
    ] = []

    report = build_evaluation_sample_coverage_report(registry)

    assert report["coverage_status"] == "FAIL"
    assert report["registry_reference_missing_keys"]


def test_coverage_report_blocks_execution() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )

    assert report["operator_review_required"] is True
    assert report["operator_review_bypass_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["orchestrator_execution_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False


def test_coverage_report_validation_passes() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )

    assert (
        validate_evaluation_sample_coverage_report(report)
        == []
    )


def test_validation_detects_status_mismatch() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )
    report["coverage_status"] = "REVIEW_REQUIRED"

    errors = validate_evaluation_sample_coverage_report(
        report
    )

    assert "coverage_status_mismatch" in errors


def test_validation_detects_count_mismatch() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )
    report["sample_count"] = 999

    errors = validate_evaluation_sample_coverage_report(
        report
    )

    assert "sample_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    report = build_evaluation_sample_coverage_report(
        make_registry()
    )
    report["operator_review_bypass_allowed"] = True
    report["model_invocation_allowed"] = True

    errors = validate_evaluation_sample_coverage_report(
        report
    )

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_sample_coverage_report(
        []
    ) == ["report_not_mapping"]