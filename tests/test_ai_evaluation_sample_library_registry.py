import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    REGISTRY_SCHEMA_VERSION,
    REGISTRY_STAGE_ID,
    build_evaluation_sample_registry,
    validate_evaluation_sample_registry,
    validate_registry_source_records,
)
from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    build_evaluation_sample_record,
)


def make_record(
    sample_id: str,
    sample_version: str = "1.0.0",
) -> dict:
    return build_evaluation_sample_record(
        sample_id=sample_id,
        sample_version=sample_version,
        title=f"Evaluation sample {sample_id}",
        evaluation_dimension="evidence_grounding",
        input_payload_ref=f"local://samples/{sample_id}.json",
        expected_outcome="PASS",
        expected_summary="Evidence remains traceable.",
        expected_reason_codes=("EVIDENCE_PRESENT",),
        expected_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{sample_id}",),
        registry_entry_ids=(f"registry-{sample_id}",),
        created_at_utc="2026-07-10T12:00:00Z",
    )


def make_registry() -> dict:
    return build_evaluation_sample_registry(
        registry_id="evaluation-library-001",
        records=(
            make_record("sample-002"),
            make_record("sample-001"),
        ),
        created_at_utc="2026-07-10T13:00:00Z",
    )


def test_registry_identity() -> None:
    registry = make_registry()

    assert registry["stage_id"] == REGISTRY_STAGE_ID
    assert registry["schema_version"] == REGISTRY_SCHEMA_VERSION
    assert registry["registry_id"] == "evaluation-library-001"


def test_registry_entries_are_sorted() -> None:
    registry = make_registry()

    assert registry["sample_keys"] == [
        "sample-001@1.0.0",
        "sample-002@1.0.0",
    ]
    assert [
        entry["sample_id"]
        for entry in registry["entries"]
    ] == ["sample-001", "sample-002"]


def test_registry_count_matches_entries() -> None:
    registry = make_registry()

    assert registry["sample_count"] == 2
    assert len(registry["entries"]) == 2


def test_registry_preserves_evidence_references() -> None:
    registry = make_registry()
    first = registry["entries"][0]

    assert first["evidence_refs"] == [
        "evidence-sample-001"
    ]
    assert first["prompt_model_registry_entry_ids"] == [
        "registry-sample-001"
    ]


def test_registry_blocks_execution_capabilities() -> None:
    registry = make_registry()

    assert registry["operator_review_required"] is True
    assert registry["operator_review_bypass_allowed"] is False
    assert registry["model_invocation_allowed"] is False
    assert registry["prompt_execution_allowed"] is False
    assert registry["orchestrator_execution_allowed"] is False
    assert registry["trade_action_allowed"] is False
    assert registry["real_execution_allowed"] is False


def test_registry_validation_passes() -> None:
    assert validate_evaluation_sample_registry(
        make_registry()
    ) == []


def test_registry_validation_detects_duplicate_key() -> None:
    registry = build_evaluation_sample_registry(
        registry_id="evaluation-library-duplicate",
        records=(
            make_record("sample-001"),
            make_record("sample-001"),
        ),
        created_at_utc="2026-07-10T13:00:00Z",
    )

    errors = validate_evaluation_sample_registry(registry)

    assert "duplicate_sample_key" in errors


def test_registry_validation_detects_count_mismatch() -> None:
    registry = make_registry()
    registry["sample_count"] = 99

    errors = validate_evaluation_sample_registry(registry)

    assert "sample_count_mismatch" in errors


def test_registry_validation_detects_key_mismatch() -> None:
    registry = make_registry()
    registry["sample_keys"] = ["incorrect-key"]

    errors = validate_evaluation_sample_registry(registry)

    assert "sample_keys_mismatch" in errors


def test_registry_validation_detects_boundary_bypass() -> None:
    registry = make_registry()
    registry["operator_review_bypass_allowed"] = True
    registry["model_invocation_allowed"] = True

    errors = validate_evaluation_sample_registry(registry)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_registry_entries_are_independent() -> None:
    first = make_registry()
    second = make_registry()
    changed = deepcopy(first)

    changed["entries"][0]["evidence_refs"].append(
        "unexpected-evidence"
    )

    assert (
        "unexpected-evidence"
        not in second["entries"][0]["evidence_refs"]
    )


def test_source_record_validation_passes() -> None:
    records = (
        make_record("sample-001"),
        make_record("sample-002"),
    )

    assert validate_registry_source_records(records) == []


def test_source_record_validation_reports_index() -> None:
    invalid = make_record("sample-001")
    invalid["model_invocation_allowed"] = True

    errors = validate_registry_source_records((invalid,))

    assert (
        "source_record_0:"
        "model_invocation_allowed_must_be_false"
        in errors
    )


def test_registry_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_sample_registry([]) == [
        "registry_not_mapping"
    ]