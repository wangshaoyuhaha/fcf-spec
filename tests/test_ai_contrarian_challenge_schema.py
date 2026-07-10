import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    APP_ID,
    CHALLENGE_CATEGORIES,
    CHALLENGE_SEVERITIES,
    CHALLENGE_STATUSES,
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_EVIDENCE_FIELDS,
    SCHEMA_VERSION,
    SOURCE_ARTIFACT_TYPES,
    build_challenge_evidence_record,
    validate_challenge_evidence_record,
)


def make_record(
    *,
    category: str = "UNSUPPORTED_CLAIM",
    evidence_references: list[str] | None = None,
) -> dict:
    if evidence_references is None:
        evidence_references = [
            "evidence/context-001.json"
        ]

    return build_challenge_evidence_record(
        challenge_evidence_id="challenge-001",
        source_artifact_id="context-001",
        source_artifact_type="AI_CONTEXT",
        source_artifact_reference=(
            "artifacts/ai-context/context-001.json"
        ),
        claim_reference="claims/claim-001",
        source_conclusion="The signal is supported.",
        challenge_category=category,
        challenge_severity="MEDIUM",
        challenge_statement=(
            "The registered evidence does not fully support "
            "the conclusion."
        ),
        evidence_references=evidence_references,
        risk_flags=["EVIDENCE_GAP"],
        challenge_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T04:20:00+00:00",
    )


def test_challenge_evidence_record_is_valid() -> None:
    record = make_record()

    assert record["app_id"] == APP_ID
    assert record["schema_version"] == SCHEMA_VERSION
    assert tuple(record) == REQUIRED_EVIDENCE_FIELDS
    assert validate_challenge_evidence_record(record) == []


def test_schema_supports_source_artifact_types() -> None:
    for source_type in SOURCE_ARTIFACT_TYPES:
        record = make_record()
        record["source_artifact_type"] = source_type

        assert validate_challenge_evidence_record(record) == []


def test_schema_supports_challenge_categories() -> None:
    for category in CHALLENGE_CATEGORIES:
        references = (
            []
            if category == "MISSING_EVIDENCE"
            else ["evidence/context-001.json"]
        )
        record = make_record(
            category=category,
            evidence_references=references,
        )

        assert validate_challenge_evidence_record(record) == []


def test_schema_supports_challenge_severities() -> None:
    for severity in CHALLENGE_SEVERITIES:
        record = make_record()
        record["challenge_severity"] = severity

        assert validate_challenge_evidence_record(record) == []


def test_schema_supports_challenge_statuses() -> None:
    for status in CHALLENGE_STATUSES:
        record = make_record()
        record["challenge_status"] = status

        assert validate_challenge_evidence_record(record) == []


def test_schema_supports_operator_review_statuses() -> None:
    for status in OPERATOR_REVIEW_STATUSES:
        record = make_record()
        record["operator_review_status"] = status

        assert validate_challenge_evidence_record(record) == []


def test_schema_rejects_missing_field() -> None:
    record = make_record()
    record.pop("source_artifact_id")

    assert "missing_field:source_artifact_id" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_unexpected_field() -> None:
    record = make_record()
    record["automatic_truth_decision"] = True

    assert "unexpected_field:automatic_truth_decision" in (
        validate_challenge_evidence_record(record)
    )


def test_missing_evidence_category_requires_empty_references() -> None:
    record = make_record(
        category="MISSING_EVIDENCE",
        evidence_references=["evidence/unexpected.json"],
    )

    assert (
        "missing_evidence_category_has_evidence"
        in validate_challenge_evidence_record(record)
    )


def test_other_categories_require_evidence_references() -> None:
    record = make_record(evidence_references=[])

    assert "evidence_references_required" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_duplicate_references() -> None:
    record = make_record(
        evidence_references=[
            "evidence/context-001.json",
            "evidence/context-001.json",
        ]
    )

    assert "evidence_references_duplicate" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_duplicate_risk_flags() -> None:
    record = make_record()
    record["risk_flags"] = [
        "EVIDENCE_GAP",
        "EVIDENCE_GAP",
    ]

    assert "risk_flags_duplicate" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_naive_timestamp() -> None:
    record = make_record()
    record["created_at_utc"] = "2026-07-11T04:20:00"

    assert "created_at_utc_invalid" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_invalid_category() -> None:
    record = make_record()
    record["challenge_category"] = "AUTO_WINNER"

    assert "challenge_category_invalid" in (
        validate_challenge_evidence_record(record)
    )


def test_schema_rejects_forbidden_outcome() -> None:
    record = make_record()
    record["challenge_status"] = "AUTO_TRUE"

    errors = validate_challenge_evidence_record(record)

    assert "challenge_status_invalid" in errors
    assert "forbidden_challenge_outcome:AUTO_TRUE" in errors


def test_schema_rejects_safety_boundary_mutation() -> None:
    record = make_record()
    record["original_conclusion_preserved"] = False
    record["automatic_truth_decision_allowed"] = True
    record["source_artifact_mutation_allowed"] = True
    record["trade_action_allowed"] = True

    errors = validate_challenge_evidence_record(record)

    assert "original_conclusion_preserved_must_be_true" in errors
    assert (
        "automatic_truth_decision_allowed_must_be_false"
        in errors
    )
    assert (
        "source_artifact_mutation_allowed_must_be_false"
        in errors
    )
    assert "trade_action_allowed_must_be_false" in errors


def test_schema_is_deterministic_and_non_mutating() -> None:
    record = make_record()
    before = deepcopy(record)

    first = validate_challenge_evidence_record(record)
    second = validate_challenge_evidence_record(record)

    assert first == second
    assert first == sorted(first)
    assert record == before


def test_schema_rejects_non_mapping() -> None:
    assert validate_challenge_evidence_record([]) == [
        "record_not_mapping"
    ]