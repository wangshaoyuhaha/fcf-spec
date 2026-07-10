"""D2 tests for registered narrative source metadata."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.source_schema import (
    NarrativeSourceRecord,
    NarrativeSourceSchemaViolation,
    NarrativeSourceTrustLevel,
    assert_valid_source_record,
    validate_source_record,
)


def _record(
    trust_level: NarrativeSourceTrustLevel = (
        NarrativeSourceTrustLevel.LEVEL_1_PROJECT_ARCHIVED
    ),
) -> NarrativeSourceRecord:
    evidence_ids: tuple[str, ...] = ()

    if (
        trust_level
        is NarrativeSourceTrustLevel.LEVEL_3_EXTERNAL_REGISTERED
    ):
        evidence_ids = ("evidence:external:001",)

    return NarrativeSourceRecord(
        artifact_id="artifact:narrative:001",
        artifact_type="REGISTERED_MARKET_NARRATIVE",
        source_trust_level=trust_level,
        content_sha256="a" * 64,
        registered_at_utc="2026-07-11T05:00:00Z",
        correlation_id="correlation:001",
        research_run_id="research-run:001",
        evidence_reference_ids=evidence_ids,
    )


@pytest.mark.parametrize(
    "trust_level",
    tuple(NarrativeSourceTrustLevel),
)
def test_all_registered_trust_levels_are_supported(
    trust_level: NarrativeSourceTrustLevel,
) -> None:
    record = _record(trust_level)

    assert validate_source_record(record) == ()
    assert_valid_source_record(record)


def test_unregistered_artifact_type_is_rejected() -> None:
    record = replace(
        _record(),
        artifact_type="LIVE_NEWS_FEED",
    )

    assert validate_source_record(record) == (
        "UNREGISTERED_ARTIFACT_TYPE",
    )


def test_invalid_content_hash_is_rejected() -> None:
    record = replace(
        _record(),
        content_sha256="not-a-sha256",
    )

    assert validate_source_record(record) == (
        "INVALID_CONTENT_SHA256",
    )


def test_non_utc_registration_time_is_rejected() -> None:
    record = replace(
        _record(),
        registered_at_utc="2026-07-11T05:00:00+09:00",
    )

    assert validate_source_record(record) == (
        "INVALID_REGISTERED_AT_UTC",
    )


def test_external_source_requires_evidence_reference() -> None:
    record = replace(
        _record(
            NarrativeSourceTrustLevel.LEVEL_3_EXTERNAL_REGISTERED
        ),
        evidence_reference_ids=(),
    )

    assert validate_source_record(record) == (
        "EXTERNAL_SOURCE_EVIDENCE_REFERENCE_REQUIRED",
    )


def test_live_fetch_is_forbidden() -> None:
    record = replace(
        _record(),
        live_fetch_allowed=True,
    )

    assert validate_source_record(record) == (
        "LIVE_FETCH_FORBIDDEN",
    )


def test_automatic_truth_decision_is_forbidden() -> None:
    record = replace(
        _record(),
        automatic_truth_decision_allowed=True,
    )

    assert validate_source_record(record) == (
        "AUTOMATIC_TRUTH_DECISION_FORBIDDEN",
    )


def test_operator_review_cannot_be_disabled() -> None:
    record = replace(
        _record(),
        operator_review_required=False,
    )

    with pytest.raises(
        NarrativeSourceSchemaViolation,
        match="OPERATOR_REVIEW_REQUIRED",
    ):
        assert_valid_source_record(record)


def test_duplicate_evidence_references_are_rejected() -> None:
    record = replace(
        _record(),
        evidence_reference_ids=(
            "evidence:001",
            "evidence:001",
        ),
    )

    assert validate_source_record(record) == (
        "DUPLICATE_EVIDENCE_REFERENCE_ID",
    )


def test_serialization_is_deterministic() -> None:
    first = _record().to_dict()
    second = _record().to_dict()

    assert first == second
    assert first["source_trust_level"] == 1
    assert (
        first["source_trust_level_name"]
        == "LEVEL_1_PROJECT_ARCHIVED"
    )
    assert first["live_fetch_allowed"] is False
    assert first["automatic_truth_decision_allowed"] is False
