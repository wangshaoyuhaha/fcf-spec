import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    APP_ID,
    CLASSIFIER_VERSION,
    build_drift_evidence_record,
    classify_drift_evidence,
)


def make_record(
    *,
    baseline_status: str = "MATCHED",
    candidate_status: str = "MATCHED",
    baseline_model_version: str = "1.0.0",
    candidate_model_version: str = "1.0.0",
    baseline_prompt_version: str = "2.0.0",
    candidate_prompt_version: str = "2.0.0",
) -> dict:
    return build_drift_evidence_record(
        drift_evidence_id="drift-evidence-001",
        evaluation_sample_id="sample-001",
        baseline_reference="comparison/baseline-001.json",
        candidate_reference="comparison/candidate-001.json",
        baseline_created_at_utc=(
            "2026-07-01T00:00:00+00:00"
        ),
        candidate_created_at_utc=(
            "2026-07-10T00:00:00+00:00"
        ),
        model_id="model-alpha",
        baseline_model_version=baseline_model_version,
        candidate_model_version=candidate_model_version,
        prompt_id="prompt-alpha",
        baseline_prompt_version=baseline_prompt_version,
        candidate_prompt_version=candidate_prompt_version,
        baseline_comparison_status=baseline_status,
        candidate_comparison_status=candidate_status,
        drift_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T00:00:00+00:00",
    )


def test_classifier_returns_no_drift() -> None:
    report = classify_drift_evidence(make_record())

    assert report["app_id"] == APP_ID
    assert report["classifier_version"] == CLASSIFIER_VERSION
    assert report["drift_status"] == "NO_DRIFT"
    assert report["drift_severity"] == "NONE"
    assert report["reason_codes"] == ["NO_MATERIAL_CHANGE"]


def test_classifier_detects_model_version_change() -> None:
    report = classify_drift_evidence(
        make_record(candidate_model_version="1.1.0")
    )

    assert report["drift_status"] == "POTENTIAL_DRIFT"
    assert report["drift_severity"] == "LOW"
    assert report["changed_dimensions"] == [
        "model_version"
    ]
    assert "MODEL_VERSION_CHANGED" in report[
        "reason_codes"
    ]


def test_classifier_detects_prompt_version_change() -> None:
    report = classify_drift_evidence(
        make_record(candidate_prompt_version="2.1.0")
    )

    assert report["drift_status"] == "POTENTIAL_DRIFT"
    assert report["drift_severity"] == "LOW"
    assert report["changed_dimensions"] == [
        "prompt_version"
    ]


def test_classifier_marks_two_version_changes_medium() -> None:
    report = classify_drift_evidence(
        make_record(
            candidate_model_version="1.1.0",
            candidate_prompt_version="2.1.0",
        )
    )

    assert report["drift_status"] == "POTENTIAL_DRIFT"
    assert report["drift_severity"] == "MEDIUM"


def test_classifier_detects_confirmed_medium_drift() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="MATCHED",
            candidate_status="PARTIAL_MATCH",
        )
    )

    assert report["drift_status"] == "CONFIRMED_DRIFT"
    assert report["drift_severity"] == "MEDIUM"
    assert (
        "CANDIDATE_WORSE_THAN_BASELINE"
        in report["reason_codes"]
    )


def test_classifier_detects_confirmed_high_drift() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="MATCHED",
            candidate_status="MISMATCH",
        )
    )

    assert report["drift_status"] == "CONFIRMED_DRIFT"
    assert report["drift_severity"] == "HIGH"


def test_classifier_detects_candidate_improvement() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="MISMATCH",
            candidate_status="MATCHED",
        )
    )

    assert report["drift_status"] == "POTENTIAL_DRIFT"
    assert report["drift_severity"] == "LOW"
    assert (
        "CANDIDATE_IMPROVED_FROM_BASELINE"
        in report["reason_codes"]
    )


def test_classifier_marks_invalid_source_insufficient() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="INVALID",
            candidate_status="MATCHED",
        )
    )

    assert report["drift_status"] == (
        "INSUFFICIENT_EVIDENCE"
    )
    assert report["drift_severity"] == "MEDIUM"
    assert report["reason_codes"] == [
        "SOURCE_COMPARISON_NOT_COMPARABLE"
    ]


def test_classifier_marks_blocked_source_insufficient() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="MATCHED",
            candidate_status="BLOCKED",
        )
    )

    assert report["drift_status"] == (
        "INSUFFICIENT_EVIDENCE"
    )


def test_classifier_records_status_dimension_change() -> None:
    report = classify_drift_evidence(
        make_record(
            baseline_status="MATCHED",
            candidate_status="PARTIAL_MATCH",
        )
    )

    assert "comparison_status" in report[
        "changed_dimensions"
    ]
    assert "COMPARISON_STATUS_CHANGED" in report[
        "reason_codes"
    ]


def test_classifier_calculates_elapsed_seconds() -> None:
    report = classify_drift_evidence(make_record())

    assert report["elapsed_seconds"] == 777600


def test_classifier_rejects_invalid_record() -> None:
    record = make_record()
    record["candidate_reference"] = record[
        "baseline_reference"
    ]

    report = classify_drift_evidence(record)

    assert report["drift_status"] == "INVALID"
    assert report["result_status"] == "INVALID"
    assert (
        "baseline_candidate_reference_must_differ"
        in report["errors"]
    )


def test_classifier_rejects_non_mapping() -> None:
    report = classify_drift_evidence([])

    assert report["drift_status"] == "INVALID"
    assert report["errors"] == ["record_not_mapping"]


def test_classifier_preserves_safety_boundary() -> None:
    report = classify_drift_evidence(make_record())

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["operator_review_required"] is True
    assert report["deterministic_only"] is True
    assert report["registered_artifacts_only"] is True
    assert report["core_mutation_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["orchestrator_execution_allowed"] is False
    assert report["automatic_approval_allowed"] is False
    assert report["automatic_rejection_allowed"] is False
    assert report["automatic_rollback_allowed"] is False
    assert report["automatic_model_switch_allowed"] is False
    assert report["automatic_prompt_switch_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False


def test_classifier_does_not_mutate_record() -> None:
    record = make_record(
        candidate_model_version="1.1.0"
    )
    before = deepcopy(record)

    classify_drift_evidence(record)

    assert record == before


def test_classifier_is_deterministic() -> None:
    record = make_record(
        candidate_model_version="1.1.0",
        candidate_prompt_version="2.1.0",
        candidate_status="PARTIAL_MATCH",
    )

    first = classify_drift_evidence(record)
    second = classify_drift_evidence(record)

    assert first == second
    assert first["changed_dimensions"] == sorted(
        first["changed_dimensions"]
    )
    assert first["reason_codes"] == sorted(
        first["reason_codes"]
    )