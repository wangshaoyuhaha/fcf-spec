from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from apps.fcp_0080_a_share_open_candidate_provider_compatibility_profile_app_1 import (
    ADJUSTMENT_STATES,
    BLOCKERS,
    CANONICAL_FIELDS,
    CLOCK_STATES,
    PROFILE_STATES,
    PROVIDERS,
    RIGHTS_STATES,
    CandidateProviderCompatibilityProfile,
    FieldMapping,
    build_augmented_coverage_matrix,
    candidate_provider_profiles,
    provider_profile_implementation_evidence,
    provider_profile_set_hash,
)


ROOT = Path(__file__).resolve().parents[2]
EVALUATED = "2026-07-23T05:00:00Z"


def test_d1_vocabularies_are_closed_and_exact():
    assert PROVIDERS == ("AKSHARE", "BAOSTOCK", "TUSHARE")
    assert CANONICAL_FIELDS == (
        "amount",
        "close",
        "high",
        "instrument_id",
        "low",
        "open",
        "trade_date",
        "volume",
    )
    assert PROFILE_STATES == ("DECLARED_UNVERIFIED_BLOCKED",)
    assert RIGHTS_STATES == ("UNRESOLVED",)
    assert ADJUSTMENT_STATES == ("UNRESOLVED_BLOCKED",)
    assert CLOCK_STATES == ("SOURCE_DATE_ONLY_NO_AVAILABILITY_CLOCK",)
    assert BLOCKERS == tuple(sorted(BLOCKERS))


def test_d2_profiles_cover_exact_candidates_in_deterministic_order():
    profiles = candidate_provider_profiles()
    assert tuple(item.provider for item in profiles) == PROVIDERS
    assert len({item.profile_id for item in profiles}) == 3
    assert len({item.profile_hash for item in profiles}) == 3


def test_d2_profile_schemas_cover_exact_canonical_fields_once():
    for profile in candidate_provider_profiles():
        assert tuple(item.source_field for item in profile.field_mappings) == profile.source_columns
        assert tuple(sorted(item.canonical_field for item in profile.field_mappings)) == CANONICAL_FIELDS
        assert len(set(item.canonical_field for item in profile.field_mappings)) == len(CANONICAL_FIELDS)


def test_d2_profiles_are_immutable_and_hash_stable():
    first = candidate_provider_profiles()
    second = candidate_provider_profiles()
    assert tuple(item.profile_hash for item in first) == tuple(item.profile_hash for item in second)
    with pytest.raises(FrozenInstanceError):
        first[0].provider = "TUSHARE"


def test_d3_every_profile_is_local_blocked_and_non_authorizing():
    for profile in candidate_provider_profiles():
        assert profile.profile_state == "DECLARED_UNVERIFIED_BLOCKED"
        assert profile.rights_state == "UNRESOLVED"
        assert profile.adjustment_state == "UNRESOLVED_BLOCKED"
        assert profile.clock_state == "SOURCE_DATE_ONLY_NO_AVAILABILITY_CLOCK"
        assert profile.blockers == BLOCKERS
        assert profile.access_mode == "REGISTERED_LOCAL_ARTIFACT"
        assert profile.local_artifact_only is True
        assert profile.sdk_invocation_allowed is False
        assert profile.network_access_allowed is False
        assert profile.credentials_allowed is False
        assert profile.provider_selected is False
        assert profile.fallback_allowed is False
        assert profile.promotion_ready is False
        assert profile.promotes_candidate_data is False
        assert profile.claims_data_authority is False
        assert profile.operator_review_required is True


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("local_artifact_only", False),
        ("sdk_invocation_allowed", True),
        ("network_access_allowed", True),
        ("credentials_allowed", True),
        ("provider_selected", True),
        ("fallback_allowed", True),
        ("promotion_ready", True),
        ("promotes_candidate_data", True),
        ("claims_data_authority", True),
        ("operator_review_required", False),
    ),
)
def test_d3_profiles_reject_scope_escalation(field, value):
    with pytest.raises(ValueError, match="non-authorizing"):
        replace(candidate_provider_profiles()[0], **{field: value})


def test_d3_profile_rejects_provider_or_schema_drift():
    profile = candidate_provider_profiles()[0]
    with pytest.raises(ValueError, match="provider"):
        replace(profile, provider="UNKNOWN")
    with pytest.raises(ValueError, match="exact source schema"):
        replace(profile, source_columns=tuple(reversed(profile.source_columns)))


def test_d3_profile_rejects_incomplete_or_duplicate_mapping():
    profile = candidate_provider_profiles()[0]
    with pytest.raises(ValueError, match="exact canonical schema"):
        replace(profile, field_mappings=profile.field_mappings[:-1], source_columns=profile.source_columns[:-1])
    duplicate = replace(profile.field_mappings[-1], canonical_field="close")
    with pytest.raises(ValueError, match="exact canonical schema"):
        replace(profile, field_mappings=profile.field_mappings[:-1] + (duplicate,))


def test_d4_field_mapping_rejects_unknown_contract_values():
    with pytest.raises(ValueError):
        FieldMapping("field", "unknown", "DATE_TEXT", "ISO_DATE", "DATE_TO_ISO")
    with pytest.raises(ValueError):
        FieldMapping("field", "trade_date", "UNKNOWN", "ISO_DATE", "DATE_TO_ISO")
    with pytest.raises(ValueError):
        FieldMapping("field", "trade_date", "DATE_TEXT", "UNKNOWN", "DATE_TO_ISO")
    with pytest.raises(ValueError):
        FieldMapping("field", "trade_date", "DATE_TEXT", "ISO_DATE", "UNKNOWN")


def test_d4_profile_set_hash_is_deterministic_and_order_sensitive():
    profiles = candidate_provider_profiles()
    assert provider_profile_set_hash(profiles) == provider_profile_set_hash(candidate_provider_profiles())
    with pytest.raises(ValueError, match="provider order"):
        provider_profile_set_hash(tuple(reversed(profiles)))


def test_d5_implementation_evidence_is_exact_and_non_authorizing():
    evidence = provider_profile_implementation_evidence(ROOT, observed_at_utc=EVALUATED)
    assert evidence.gap_id == "V2-FR-GAP-093"
    assert evidence.capabilities == (
        "PROVIDER_PROFILE_AKSHARE",
        "PROVIDER_PROFILE_BAOSTOCK",
        "PROVIDER_PROFILE_TUSHARE",
    )
    assert evidence.claims_data_authority is False
    assert evidence.closes_gap is False


def test_d5_augmented_matrix_covers_provider_profile_foundation_only():
    matrix = build_augmented_coverage_matrix(ROOT, evaluated_at_utc=EVALUATED)
    row = {item.requirement.gap_id: item for item in matrix.rows}["V2-FR-GAP-093"]
    assert row.missing_capabilities == ()
    assert row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert all(item.gap_open is True for item in matrix.rows)
    assert all(item.authority_established is False for item in matrix.rows)
    assert matrix.changes_gap_status is False
    assert matrix.promotes_candidate_data is False
    assert matrix.provider_selected is False


def test_d5_augmented_matrix_is_deterministic():
    first = build_augmented_coverage_matrix(ROOT, evaluated_at_utc=EVALUATED)
    second = build_augmented_coverage_matrix(ROOT, evaluated_at_utc=EVALUATED)
    assert first.matrix_hash == second.matrix_hash


def test_d6_profiles_never_contain_credentials_or_endpoints():
    forbidden = ("TOKEN", "PASSWORD", "SECRET", "HTTP://", "HTTPS://", "TCP://")
    for profile in candidate_provider_profiles():
        serialized = str(profile.payload()).upper()
        assert not any(term in serialized for term in forbidden)
