import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    APP_ID,
    DRIFT_STATUSES,
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_EVIDENCE_FIELDS,
    SCHEMA_VERSION,
    SOURCE_COMPARISON_STATUSES,
    build_drift_evidence_record,
    validate_drift_evidence_record,
)


def make_record() -> dict:
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
        baseline_model_version="1.0.0",
        candidate_model_version="1.1.0",
        prompt_id="prompt-alpha",
        baseline_prompt_version="2.0.0",
        candidate_prompt_version="2.1.0",
        baseline_comparison_status="MATCHED",
        candidate_comparison_status="PARTIAL_MATCH",
        drift_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T00:00:00+00:00",
    )


def test_drift_evidence_record_is_valid() -> None:
    record = make_record()

    assert record["app_id"] == APP_ID
    assert record["schema_version"] == SCHEMA_VERSION
    assert tuple(record) == REQUIRED_EVIDENCE_FIELDS
    assert validate_drift_evidence_record(record) == []


def test_schema_supports_registered_drift_statuses() -> None:
    for status in DRIFT_STATUSES:
        record = make_record()
        record["drift_status"] = status

        assert validate_drift_evidence_record(record) == []


def test_schema_supports_source_comparison_statuses() -> None:
    for status in SOURCE_COMPARISON_STATUSES:
        record = make_record()
        record["baseline_comparison_status"] = status
        record["candidate_comparison_status"] = status

        assert validate_drift_evidence_record(record) == []


def test_schema_supports_operator_review_statuses() -> None:
    for status in OPERATOR_REVIEW_STATUSES:
        record = make_record()
        record["operator_review_status"] = status

        assert validate_drift_evidence_record(record) == []


def test_schema_rejects_missing_required_field() -> None:
    record = make_record()
    record.pop("model_id")

    assert "missing_field:model_id" in (
        validate_drift_evidence_record(record)
    )


def test_schema_rejects_unexpected_field() -> None:
    record = make_record()
    record["automatic_model_switch"] = True

    assert "unexpected_field:automatic_model_switch" in (
        validate_drift_evidence_record(record)
    )


def test_schema_requires_distinct_references() -> None:
    record = make_record()
    record["candidate_reference"] = record[
        "baseline_reference"
    ]

    assert (
        "baseline_candidate_reference_must_differ"
        in validate_drift_evidence_record(record)
    )


def test_schema_rejects_naive_timestamp() -> None:
    record = make_record()
    record["baseline_created_at_utc"] = (
        "2026-07-01T00:00:00"
    )

    assert "baseline_created_at_utc_invalid" in (
        validate_drift_evidence_record(record)
    )


def test_schema_requires_candidate_after_baseline() -> None:
    record = make_record()
    record["candidate_created_at_utc"] = (
        "2026-06-30T00:00:00+00:00"
    )

    assert (
        "candidate_created_at_utc_must_follow_baseline"
        in validate_drift_evidence_record(record)
    )


def test_schema_requires_record_time_after_candidate() -> None:
    record = make_record()
    record["created_at_utc"] = (
        "2026-07-09T00:00:00+00:00"
    )

    assert (
        "created_at_utc_must_not_precede_candidate"
        in validate_drift_evidence_record(record)
    )


def test_schema_rejects_invalid_source_status() -> None:
    record = make_record()
    record["candidate_comparison_status"] = "UNKNOWN"

    assert "candidate_comparison_status_invalid" in (
        validate_drift_evidence_record(record)
    )


def test_schema_rejects_forbidden_drift_status() -> None:
    record = make_record()
    record["drift_status"] = "AUTO_APPROVED"

    errors = validate_drift_evidence_record(record)

    assert "drift_status_invalid" in errors
    assert "forbidden_drift_status:AUTO_APPROVED" in errors


def test_schema_rejects_safety_boundary_mutation() -> None:
    record = make_record()
    record["operator_review_required"] = False
    record["automatic_rollback_allowed"] = True
    record["automatic_model_switch_allowed"] = True
    record["trade_action_allowed"] = True

    errors = validate_drift_evidence_record(record)

    assert "operator_review_required_must_be_true" in errors
    assert "automatic_rollback_allowed_must_be_false" in errors
    assert (
        "automatic_model_switch_allowed_must_be_false"
        in errors
    )
    assert "trade_action_allowed_must_be_false" in errors


def test_schema_validation_is_deterministic() -> None:
    record = make_record()
    mutated = deepcopy(record)
    mutated["model_id"] = ""
    mutated["real_execution_allowed"] = True

    first = validate_drift_evidence_record(mutated)
    second = validate_drift_evidence_record(mutated)

    assert first == second
    assert first == sorted(first)


def test_schema_does_not_mutate_record() -> None:
    record = make_record()
    before = deepcopy(record)

    validate_drift_evidence_record(record)

    assert record == before


def test_schema_rejects_non_mapping() -> None:
    assert validate_drift_evidence_record([]) == [
        "record_not_mapping"
    ]