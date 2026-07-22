from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from apps.fcp_0079_a_share_corporate_action_query_policy_lineage_contract_app_1 import (
    ACTION_TYPES,
    PRICE_VIEWS,
    RESOLUTION_STATES,
    REVISION_STATES,
    AdjustmentFactorRevision,
    CorporateActionRevision,
    PriceQueryPolicy,
    RawPriceReference,
    build_augmented_coverage_matrix,
    price_lineage_implementation_evidence,
    resolve_price_lineage,
)


ROOT = Path(__file__).resolve().parents[2]
SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def action(**overrides):
    values = {
        "record_id": "action-record-v1",
        "action_id": "600000.XSHG-dividend-2026",
        "instrument_id": "600000.XSHG",
        "action_type": "CASH_DIVIDEND",
        "publication_clock_hash": SHA_A,
        "publication_at_utc": "2026-06-01T08:00:00Z",
        "effective_date": "2026-06-10",
        "action_payload_sha256": SHA_B,
        "source_artifact_sha256": SHA_C,
        "observable_at_utc": "2026-06-01T08:01:00Z",
    }
    values.update(overrides)
    return CorporateActionRevision(**values)


def factor(action_record=None, **overrides):
    record = action_record or action()
    values = {
        "record_id": "factor-record-v1",
        "factor_id": "600000.XSHG-2026-06-10-forward",
        "instrument_id": "600000.XSHG",
        "trade_date": "2026-06-10",
        "factor_value": "0.98",
        "action_record_hashes": (record.record_hash,),
        "factor_available_at_utc": "2026-06-01T08:02:00Z",
        "source_artifact_sha256": SHA_C,
    }
    values.update(overrides)
    return AdjustmentFactorRevision(**values)


def raw(**overrides):
    values = {
        "observation_sha256": SHA_A,
        "instrument_id": "600000.XSHG",
        "trade_date": "2026-06-10",
        "revision_at_utc": "2026-06-10T08:00:00Z",
    }
    values.update(overrides)
    return RawPriceReference(**values)


def policy(view="FORWARD_ADJUSTED", **overrides):
    values = {"policy_id": f"price-policy-{view.lower()}", "price_view": view}
    values.update(overrides)
    return PriceQueryPolicy(**values)


def test_d1_vocabularies_are_closed_and_exact():
    assert ACTION_TYPES == ("BONUS_SHARE", "CASH_DIVIDEND", "RIGHTS_ISSUE", "STOCK_SPLIT")
    assert PRICE_VIEWS == ("FORWARD_ADJUSTED", "RAW")
    assert REVISION_STATES == ("CANCELLED", "ORIGINAL", "REVISED")
    assert RESOLUTION_STATES == (
        "ACTION_LINEAGE_MISMATCH",
        "ADJUSTED_RESOLVED",
        "FACTOR_NOT_OBSERVABLE",
        "RAW_RESOLVED",
    )


def test_d2_action_is_immutable_hash_stable_and_non_authorizing():
    left = action()
    right = action()
    assert left.record_hash == right.record_hash
    assert left.claims_data_authority is False
    assert left.closes_gap is False
    with pytest.raises(FrozenInstanceError):
        left.action_id = "changed"


@pytest.mark.parametrize(
    "overrides",
    (
        {"publication_at_utc": "2026-06-01T08:00:00+08:00"},
        {"observable_at_utc": "2026-06-01T07:59:59Z"},
        {"effective_date": "2026-05-31"},
        {"action_type": "UNKNOWN"},
        {"observed_not_inferred": False},
        {"operator_review_required": False},
        {"claims_data_authority": True},
        {"closes_gap": True},
    ),
)
def test_d2_action_rejects_unsafe_semantics(overrides):
    with pytest.raises(ValueError):
        action(**overrides)


def test_d2_action_revision_requires_exact_predecessor_shape():
    original = action()
    revised = action(
        record_id="action-record-v2",
        observable_at_utc="2026-06-01T09:00:00Z",
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )
    assert revised.revision_number == 1
    with pytest.raises(ValueError):
        action(revision_number=1, revision_state="REVISED")


def test_d3_factor_is_exact_immutable_and_binds_action_revisions():
    item = factor()
    assert str(item.factor_value) == "0.98"
    assert item.provider_default_used is False
    assert item.claims_official_factor is False
    with pytest.raises(FrozenInstanceError):
        item.factor_id = "changed"


@pytest.mark.parametrize(
    "overrides",
    (
        {"factor_value": "0"},
        {"factor_value": 0.98},
        {"action_record_hashes": ()},
        {"provider_default_used": True},
        {"claims_official_factor": True},
    ),
)
def test_d3_factor_rejects_unsafe_semantics(overrides):
    with pytest.raises(ValueError):
        factor(**overrides)


def test_d4_query_policy_is_explicit_and_fail_closed():
    item = policy()
    assert item.price_view == "FORWARD_ADJUSTED"
    assert item.factor_selection == "LATEST_OBSERVABLE_AS_OF"
    assert item.source_prices_immutable is True
    assert item.unspecified_view_allowed is False
    assert item.future_revisions_allowed is False


@pytest.mark.parametrize(
    "overrides",
    (
        {"price_view": "PROVIDER_DEFAULT"},
        {"factor_selection": "LATEST_CURRENT"},
        {"source_prices_immutable": False},
        {"unspecified_view_allowed": True},
        {"future_revisions_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d4_query_policy_rejects_unsafe_defaults(overrides):
    values = {"price_view": "RAW"}
    values.update(overrides)
    with pytest.raises(ValueError):
        PriceQueryPolicy(policy_id="policy-v1", **values)


def test_d4_raw_resolution_never_selects_or_applies_a_factor():
    event = action()
    result = resolve_price_lineage(
        (event,),
        (factor(event),),
        raw_price=raw(),
        policy=policy("RAW"),
        evaluated_at_utc="2026-06-10T08:00:00Z",
    )
    assert result.resolution_state == "RAW_RESOLVED"
    assert result.selected_factor is None
    assert result.selected_action_hashes == (event.record_hash,)


def test_d4_adjusted_resolution_selects_only_observable_exact_lineage():
    event = action()
    item = factor(event)
    result = resolve_price_lineage(
        (event,),
        (item,),
        raw_price=raw(),
        policy=policy(),
        evaluated_at_utc="2026-06-10T08:00:00Z",
    )
    assert result.resolution_state == "ADJUSTED_RESOLVED"
    assert result.selected_factor == item
    assert result.claims_data_authority is False
    assert result.closes_gap is False


def test_d4_future_factor_is_not_observable():
    event = action()
    item = factor(event, factor_available_at_utc="2026-06-10T08:00:01Z")
    result = resolve_price_lineage(
        (event,),
        (item,),
        raw_price=raw(),
        policy=policy(),
        evaluated_at_utc="2026-06-10T08:00:00Z",
    )
    assert result.resolution_state == "FACTOR_NOT_OBSERVABLE"
    assert result.selected_factor is None


def test_d4_action_factor_mismatch_fails_closed():
    event = action()
    item = factor(event, action_record_hashes=(SHA_A,))
    result = resolve_price_lineage(
        (event,),
        (item,),
        raw_price=raw(),
        policy=policy(),
        evaluated_at_utc="2026-06-10T08:00:00Z",
    )
    assert result.resolution_state == "ACTION_LINEAGE_MISMATCH"
    assert result.selected_factor is None


def test_d4_latest_observable_action_revision_is_required():
    original = action()
    revised = action(
        record_id="action-record-v2",
        observable_at_utc="2026-06-02T08:00:00Z",
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )
    stale_factor = factor(original)
    result = resolve_price_lineage(
        (original, revised),
        (stale_factor,),
        raw_price=raw(),
        policy=policy(),
        evaluated_at_utc="2026-06-10T08:00:00Z",
    )
    assert result.resolution_state == "ACTION_LINEAGE_MISMATCH"
    assert result.selected_action_hashes == (revised.record_hash,)


def test_d4_revision_chain_rejects_missing_or_cross_identity_predecessor():
    original = action()
    revised = action(
        record_id="action-record-v2",
        observable_at_utc="2026-06-02T08:00:00Z",
        revision_number=1,
        revision_state="REVISED",
        revises_record_hash=original.record_hash,
    )
    with pytest.raises(ValueError, match="predecessor is not registered"):
        resolve_price_lineage(
            (revised,),
            (),
            raw_price=raw(),
            policy=policy("RAW"),
            evaluated_at_utc="2026-06-10T08:00:00Z",
        )
    other = replace(original, record_id="other-record", action_id="other-action")
    bad = replace(revised, revises_record_hash=other.record_hash)
    with pytest.raises(ValueError, match="another identity"):
        resolve_price_lineage(
            (other, bad),
            (),
            raw_price=raw(),
            policy=policy("RAW"),
            evaluated_at_utc="2026-06-10T08:00:00Z",
        )


def test_d4_raw_revision_cannot_leak_from_the_future():
    with pytest.raises(ValueError, match="raw price revision"):
        resolve_price_lineage(
            (),
            (),
            raw_price=raw(revision_at_utc="2026-06-10T08:00:01Z"),
            policy=policy("RAW"),
            evaluated_at_utc="2026-06-10T08:00:00Z",
        )


def test_d5_implementation_evidence_is_exact_and_non_authorizing():
    evidence = price_lineage_implementation_evidence(
        ROOT,
        observed_at_utc="2026-07-23T03:30:00Z",
    )
    assert evidence.gap_id == "V2-FR-GAP-089"
    assert evidence.capabilities == ("CORPORATE_ACTION_LINEAGE", "QUERY_POLICY_LINEAGE")
    assert evidence.claims_data_authority is False
    assert evidence.closes_gap is False


def test_d5_augmented_matrix_covers_price_lineage_foundation_only():
    matrix = build_augmented_coverage_matrix(
        ROOT,
        evaluated_at_utc="2026-07-23T03:30:00Z",
    )
    row = {item.requirement.gap_id: item for item in matrix.rows}["V2-FR-GAP-089"]
    assert row.missing_capabilities == ()
    assert row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert all(item.gap_open is True for item in matrix.rows)
    assert all(item.authority_established is False for item in matrix.rows)
    assert matrix.changes_gap_status is False
    assert matrix.promotes_candidate_data is False
    assert matrix.provider_selected is False


def test_d5_augmented_matrix_is_deterministic():
    first = build_augmented_coverage_matrix(ROOT, evaluated_at_utc="2026-07-23T03:30:00Z")
    second = build_augmented_coverage_matrix(ROOT, evaluated_at_utc="2026-07-23T03:30:00Z")
    assert first.matrix_hash == second.matrix_hash
