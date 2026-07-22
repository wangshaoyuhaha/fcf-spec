from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from apps.fcp_0078_a_share_publication_availability_clock_contract_app_1 import (
    PUBLICATION_STATES,
    RESOLUTION_STATES,
    REVISION_STATES,
    SUBJECT_TYPES,
    PublicationAvailabilityClock,
    PublicationClockResolution,
    RegisteredPublicationSource,
    build_augmented_coverage_matrix,
    publication_clock_implementation_evidence,
    resolve_publication_clock,
)


ROOT = Path(__file__).resolve().parents[2]
SHA = "a" * 64


def source(**overrides):
    values = {
        "source_id": "official-announcement-source",
        "registered_artifact_id": "artifact-announcement-v1",
        "artifact_sha256": SHA,
        "registered_at_utc": "2026-07-22T00:00:00Z",
        "rights_state": "DECLARED_LOCAL_RESEARCH",
        "retention_state": "LOCAL_DERIVED_ONLY",
    }
    values.update(overrides)
    return RegisteredPublicationSource(**values)


def exact_clock(**overrides):
    values = {
        "record_id": "clock-record-v1",
        "subject_id": "600000.XSHG-announcement-v1",
        "subject_type": "EARNINGS_DISCLOSURE",
        "market": "CN-A",
        "publication_state": "EXACT_OBSERVED",
        "publication_at_utc": "2026-07-22T00:00:00Z",
        "publication_date": None,
        "first_legally_available_at_utc": "2026-07-22T00:00:01Z",
        "retrieved_at_utc": "2026-07-22T00:01:00Z",
        "ingested_at_utc": "2026-07-22T00:02:00Z",
        "first_tradable_at_utc": "2026-07-22T01:30:00Z",
        "revision_at_utc": "2026-07-22T00:03:00Z",
        "source": source(),
    }
    values.update(overrides)
    return PublicationAvailabilityClock(**values)


def test_d1_vocabularies_are_closed_and_exact():
    assert SUBJECT_TYPES == (
        "CORPORATE_ACTION",
        "EARNINGS_DISCLOSURE",
        "MARKET_DATA",
        "POLICY_RELEASE",
        "TRADING_CALENDAR",
    )
    assert PUBLICATION_STATES == (
        "DATE_ONLY_BLOCKED",
        "EXACT_OBSERVED",
        "UNKNOWN_BLOCKED",
    )
    assert REVISION_STATES == ("CANCELLED", "ORIGINAL", "REVISED")
    assert RESOLUTION_STATES == (
        "BLOCKED_CANCELLED",
        "BLOCKED_DATE_ONLY",
        "BLOCKED_UNKNOWN",
        "EXACT_AVAILABLE",
        "NOT_YET_OBSERVABLE",
    )


def test_d2_source_is_immutable_deterministic_and_non_authorizing():
    left = source()
    right = source()
    assert left.source_hash == right.source_hash
    assert left.network_retrieval_allowed is False
    assert left.provider_selected is False
    assert left.claims_data_authority is False
    with pytest.raises(FrozenInstanceError):
        left.source_id = "changed"


@pytest.mark.parametrize(
    "overrides",
    (
        {"network_retrieval_allowed": True},
        {"provider_selected": True},
        {"claims_data_authority": True},
        {"operator_registered": False},
        {"local_artifact_only": False},
    ),
)
def test_d2_source_rejects_authority_expansion(overrides):
    with pytest.raises(ValueError):
        source(**overrides)


def test_d2_exact_clock_is_immutable_and_hash_stable():
    left = exact_clock()
    right = exact_clock()
    assert left.record_hash == right.record_hash
    assert left.exact_time_usable is True
    assert left.payload()["claims_data_authority"] is False
    with pytest.raises(FrozenInstanceError):
        left.market = "OTHER"


@pytest.mark.parametrize(
    "overrides",
    (
        {"publication_at_utc": "2026-07-22T00:02:00+08:00"},
        {"first_legally_available_at_utc": None},
        {"publication_date": "2026-07-22"},
        {"retrieved_at_utc": "2026-07-21T23:59:59Z"},
        {"ingested_at_utc": "2026-07-22T00:00:30Z"},
        {"first_tradable_at_utc": "2026-07-21T23:59:59Z"},
        {"claims_data_authority": True},
        {"closes_gap": True},
    ),
)
def test_d3_exact_clock_rejects_unsafe_semantics(overrides):
    with pytest.raises(ValueError):
        exact_clock(**overrides)


def test_d3_date_only_and_unknown_are_explicitly_blocked():
    date_only = exact_clock(
        publication_state="DATE_ONLY_BLOCKED",
        publication_at_utc=None,
        publication_date="2026-07-22",
        first_legally_available_at_utc=None,
        first_tradable_at_utc=None,
    )
    unknown = exact_clock(
        publication_state="UNKNOWN_BLOCKED",
        publication_at_utc=None,
        publication_date=None,
        first_legally_available_at_utc=None,
        first_tradable_at_utc=None,
    )
    assert date_only.exact_time_usable is False
    assert unknown.exact_time_usable is False


@pytest.mark.parametrize(
    "overrides",
    (
        {
            "publication_state": "DATE_ONLY_BLOCKED",
            "publication_date": None,
            "publication_at_utc": None,
            "first_legally_available_at_utc": None,
            "first_tradable_at_utc": None,
        },
        {
            "publication_state": "UNKNOWN_BLOCKED",
            "publication_date": "2026-07-22",
            "publication_at_utc": None,
            "first_legally_available_at_utc": None,
            "first_tradable_at_utc": None,
        },
        {
            "publication_state": "DATE_ONLY_BLOCKED",
            "publication_date": "2026-07-22",
            "publication_at_utc": "2026-07-22T00:00:00Z",
            "first_legally_available_at_utc": None,
            "first_tradable_at_utc": None,
        },
    ),
)
def test_d3_blocked_publication_cannot_claim_exact_time(overrides):
    with pytest.raises(ValueError):
        exact_clock(**overrides)


def test_d4_resolution_is_point_in_time_safe():
    record = exact_clock()
    before = resolve_publication_clock(
        (record,),
        subject_id=record.subject_id,
        evaluated_at_utc="2026-07-22T00:01:59Z",
    )
    after = resolve_publication_clock(
        (record,),
        subject_id=record.subject_id,
        evaluated_at_utc="2026-07-22T00:03:00Z",
    )
    assert before.resolution_state == "NOT_YET_OBSERVABLE"
    assert after.resolution_state == "EXACT_AVAILABLE"
    assert after.selected_record == record
    assert after.claims_data_authority is False
    assert after.closes_gap is False


def test_d4_resolution_waits_for_source_registration():
    record = exact_clock(
        source=source(registered_at_utc="2026-07-22T00:10:00Z")
    )
    before = resolve_publication_clock(
        (record,),
        subject_id=record.subject_id,
        evaluated_at_utc="2026-07-22T00:09:59Z",
    )
    after = resolve_publication_clock(
        (record,),
        subject_id=record.subject_id,
        evaluated_at_utc="2026-07-22T00:10:00Z",
    )
    assert before.resolution_state == "NOT_YET_OBSERVABLE"
    assert after.resolution_state == "EXACT_AVAILABLE"


def test_d4_resolution_rejects_state_or_hash_mismatch():
    record = exact_clock()
    with pytest.raises(ValueError, match="disagrees"):
        PublicationClockResolution(
            subject_id=record.subject_id,
            evaluated_at_utc="2026-07-22T00:03:00Z",
            resolution_state="BLOCKED_UNKNOWN",
            selected_record=record,
            observed_record_hashes=(record.record_hash,),
        )
    with pytest.raises(ValueError, match="observed hashes"):
        PublicationClockResolution(
            subject_id=record.subject_id,
            evaluated_at_utc="2026-07-22T00:03:00Z",
            resolution_state="EXACT_AVAILABLE",
            selected_record=record,
            observed_record_hashes=("b" * 64,),
        )


def test_d4_latest_revision_supersedes_predecessor():
    original = exact_clock()
    revised = exact_clock(
        record_id="clock-record-v2",
        publication_at_utc="2026-07-22T00:00:30Z",
        first_legally_available_at_utc="2026-07-22T00:00:31Z",
        retrieved_at_utc="2026-07-22T00:04:00Z",
        ingested_at_utc="2026-07-22T00:05:00Z",
        revision_at_utc="2026-07-22T00:06:00Z",
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )
    resolution = resolve_publication_clock(
        (revised, original),
        subject_id=original.subject_id,
        evaluated_at_utc="2026-07-22T00:06:00Z",
    )
    assert resolution.resolution_state == "EXACT_AVAILABLE"
    assert resolution.selected_record == revised
    assert resolution.observed_record_hashes == tuple(
        sorted((original.record_hash, revised.record_hash))
    )


def test_d4_cancelled_revision_remains_blocked():
    original = exact_clock()
    cancelled = exact_clock(
        record_id="clock-record-cancelled",
        retrieved_at_utc="2026-07-22T00:04:00Z",
        ingested_at_utc="2026-07-22T00:05:00Z",
        revision_at_utc="2026-07-22T00:06:00Z",
        revision_number=1,
        revision_state="CANCELLED",
        revises_record_hash=original.record_hash,
    )
    resolution = resolve_publication_clock(
        (original, cancelled),
        subject_id=original.subject_id,
        evaluated_at_utc="2026-07-22T00:06:00Z",
    )
    assert resolution.resolution_state == "BLOCKED_CANCELLED"
    assert resolution.selected_record.exact_time_usable is False


def test_d4_rejects_missing_or_cross_subject_predecessor():
    original = exact_clock()
    revised = exact_clock(
        record_id="clock-record-v2",
        retrieved_at_utc="2026-07-22T00:04:00Z",
        ingested_at_utc="2026-07-22T00:05:00Z",
        revision_at_utc="2026-07-22T00:06:00Z",
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )
    with pytest.raises(ValueError, match="predecessor is not registered"):
        resolve_publication_clock(
            (revised,),
            subject_id=revised.subject_id,
            evaluated_at_utc="2026-07-22T00:06:00Z",
        )
    other = replace(original, record_id="other-record", subject_id="other-subject")
    bad = replace(revised, revises_record_hash=other.record_hash)
    with pytest.raises(ValueError, match="another subject"):
        resolve_publication_clock(
            (other, bad),
            subject_id=bad.subject_id,
            evaluated_at_utc="2026-07-22T00:06:00Z",
        )


def test_d5_implementation_evidence_is_exact_and_non_authorizing():
    evidence = publication_clock_implementation_evidence(
        ROOT,
        observed_at_utc="2026-07-22T18:30:00Z",
    )
    assert evidence.gap_id == "V2-FR-GAP-088"
    assert evidence.capabilities == ("PUBLICATION_CLOCK",)
    assert evidence.claims_data_authority is False
    assert evidence.closes_gap is False


def test_d5_augmented_matrix_covers_foundation_but_preserves_every_gap():
    matrix = build_augmented_coverage_matrix(
        ROOT,
        evaluated_at_utc="2026-07-22T18:30:00Z",
    )
    rows = {row.requirement.gap_id: row for row in matrix.rows}
    row = rows["V2-FR-GAP-088"]
    assert row.missing_capabilities == ()
    assert row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert all(item.gap_open is True for item in matrix.rows)
    assert all(item.authority_established is False for item in matrix.rows)
    assert matrix.changes_gap_status is False
    assert matrix.promotes_candidate_data is False
    assert matrix.provider_selected is False


def test_d5_augmented_matrix_is_deterministic():
    first = build_augmented_coverage_matrix(
        ROOT,
        evaluated_at_utc="2026-07-22T18:30:00Z",
    )
    second = build_augmented_coverage_matrix(
        ROOT,
        evaluated_at_utc="2026-07-22T18:30:00Z",
    )
    assert first.matrix_hash == second.matrix_hash
