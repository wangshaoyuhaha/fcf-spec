import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_comparison import (
    APP_ID,
    COMPARISON_MODES,
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_RECORD_FIELDS,
    RESULT_STATUSES,
    SCHEMA_VERSION,
    build_comparison_record,
    validate_comparison_record,
)


def make_record() -> dict:
    return build_comparison_record(
        comparison_id="comparison-001",
        comparison_mode="expected_vs_observed",
        evaluation_sample_id="sample-001",
        expected_result_reference="expected/sample-001.json",
        observed_result_reference="observed/result-001.json",
        model_id="model-alpha",
        model_version="1.0.0",
        prompt_id="prompt-alpha",
        prompt_version="2.0.0",
        context_evidence_reference="context/context-001.json",
        result_status="RECORDED",
        comparison_status="MATCHED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T02:30:00+00:00",
    )


def test_build_comparison_record_is_valid() -> None:
    record = make_record()

    assert record["app_id"] == APP_ID
    assert record["schema_version"] == SCHEMA_VERSION
    assert tuple(record) == REQUIRED_RECORD_FIELDS
    assert validate_comparison_record(record) == []


def test_schema_supports_all_comparison_modes() -> None:
    for mode in COMPARISON_MODES:
        record = make_record()
        record["comparison_mode"] = mode

        assert validate_comparison_record(record) == []


def test_schema_supports_registered_result_statuses() -> None:
    for status in RESULT_STATUSES:
        record = make_record()
        record["result_status"] = status

        assert validate_comparison_record(record) == []


def test_schema_supports_operator_review_statuses() -> None:
    for status in OPERATOR_REVIEW_STATUSES:
        record = make_record()
        record["operator_review_status"] = status

        assert validate_comparison_record(record) == []


def test_schema_rejects_missing_required_field() -> None:
    record = make_record()
    record.pop("model_id")

    errors = validate_comparison_record(record)

    assert "missing_field:model_id" in errors


def test_schema_rejects_unexpected_field() -> None:
    record = make_record()
    record["automatic_trade_action"] = True

    errors = validate_comparison_record(record)

    assert "unexpected_field:automatic_trade_action" in errors


def test_schema_rejects_forbidden_comparison_status() -> None:
    record = make_record()
    record["comparison_status"] = "AUTO_APPROVED"

    errors = validate_comparison_record(record)

    assert "comparison_status_invalid" in errors
    assert (
        "forbidden_comparison_status:AUTO_APPROVED"
        in errors
    )


def test_schema_rejects_invalid_timestamp() -> None:
    record = make_record()
    record["created_at_utc"] = "2026-07-11T02:30:00"

    errors = validate_comparison_record(record)

    assert "created_at_utc_invalid" in errors


def test_schema_rejects_safety_boundary_mutation() -> None:
    record = make_record()
    record["operator_review_required"] = False
    record["model_invocation_allowed"] = True
    record["trade_action_allowed"] = True

    errors = validate_comparison_record(record)

    assert "operator_review_required_must_be_true" in errors
    assert "model_invocation_allowed_must_be_false" in errors
    assert "trade_action_allowed_must_be_false" in errors


def test_schema_validation_is_deterministic() -> None:
    record = make_record()
    mutated = deepcopy(record)
    mutated["model_version"] = ""
    mutated["real_execution_allowed"] = True

    first = validate_comparison_record(mutated)
    second = validate_comparison_record(mutated)

    assert first == second
    assert first == sorted(first)


def test_schema_rejects_non_mapping() -> None:
    assert validate_comparison_record([]) == [
        "record_not_mapping"
    ]