from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCBookDelta,
    BTCBookLevel,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCObservationHeader,
    BTCReferencePriceObservation,
    BTCRegisteredArtifact,
    BTCTradeObservation,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationPolicy,
    RegisteredCanonicalBTCObservationSet,
    reconcile_canonical_btc_observation_sets,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


AS_OF = "2026-07-21T00:00:20Z"


def artifact(name: str) -> BTCRegisteredArtifact:
    content = (name + "\n").encode("ascii")
    return BTCRegisteredArtifact(
        artifact_id=name,
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=LocalEventRights("synthetic-test", "local-paper-research", 30),
    )


def header(source: str, kind: str, sequence: int = 1, **updates) -> BTCObservationHeader:
    values = {
        "observation_id": f"{source}-{kind.lower()}",
        "artifact_id": f"artifact-{source}",
        "venue_id": "venue-a",
        "instrument_id": "BTC-USDT",
        "instrument_kind": "PERPETUAL",
        "observation_kind": kind,
        "source_sequence": sequence,
        "event_at_utc": "2026-07-21T00:00:09Z",
        "received_at_utc": "2026-07-21T00:00:10Z",
        "ingested_at_utc": "2026-07-21T00:00:10Z",
    }
    values.update(updates)
    return BTCObservationHeader(**values)


def level(price: str, quantity: str) -> BTCBookLevel:
    return BTCBookLevel(Decimal(price), Decimal(quantity))


def trade(source: str, price="65000", quantity="1", side="BUY", **header_updates):
    return BTCTradeObservation(
        header(source, "TRADE", **header_updates), Decimal(price), Decimal(quantity), side
    )


def snapshot(source: str, bid="65000", ask="65001", **header_updates):
    return BTCBookSnapshot(
        header(source, "BOOK_SNAPSHOT", 100, **header_updates),
        (level(bid, "1"),),
        (level(ask, "1"),),
    )


def delta(source: str, bid_quantity="2", previous=100, sequence=101):
    return BTCBookDelta(
        header(source, "BOOK_DELTA", sequence),
        previous,
        (level("65000", bid_quantity),),
        (),
    )


def reference(source: str, mark="65000", index="64999"):
    return BTCReferencePriceObservation(
        header(source, "REFERENCE_PRICE"), Decimal(mark), Decimal(index)
    )


def funding(source: str, rate="0.0001", start="2026-07-20T16:00:00Z"):
    return BTCFundingObservation(
        header(source, "FUNDING"),
        Decimal(rate),
        start,
        "2026-07-21T00:00:10Z",
    )


def dataset(source: str, observations, **updates):
    values = {
        "dataset_id": f"dataset-{source}",
        "source_id": f"source-{source}",
        "artifact": artifact(f"artifact-{source}"),
        "observations": tuple(observations),
        "as_of_utc": AS_OF,
        "venue_semantics_id": "btc-usdt-perpetual-v1",
    }
    values.update(updates)
    return RegisteredCanonicalBTCObservationSet(**values)


def codes(result):
    return {item.code for item in result.findings}


def test_consistent_registered_sources_remain_review_only():
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (trade("a"),)), dataset("b", (trade("b"),))),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert result.quality_state == "CONSISTENT"
    assert result.union_key_count == result.overlap_key_count == 1
    assert result.source_selected is False
    assert result.operator_review_required is True
    assert result.calculation_authority == "DETERMINISTIC_ENGINE"
    assert result.evidence_authority == "REGISTERED_EVIDENCE"
    assert result.ai_role == "ADVISORY_ONLY"


def test_trade_price_quantity_and_side_conflicts_are_quarantined():
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (trade("a"),)), dataset("b", (trade("b", "65002", "2", "SELL"),))),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert codes(result) >= {"PRICE_MISMATCH", "QUANTITY_MISMATCH", "SIDE_MISMATCH"}
    assert result.quality_state == "QUARANTINE_REVIEW_REQUIRED"


def test_registered_tolerances_are_exact_and_bounded():
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (trade("a"),)), dataset("b", (trade("b", "65000.1", "1.1"),))),
        BTCCrossSourceReconciliationPolicy("bounded-v1", Decimal("0.1"), Decimal("0.1")),
    )
    assert result.quality_state == "CONSISTENT"
    with pytest.raises(ValueError, match="exact decimal"):
        BTCCrossSourceReconciliationPolicy("unsafe", 0.1)


def test_coverage_gap_is_explicit_and_never_filled():
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (reference("a"), trade("a"))), dataset("b", (trade("b"),))),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert "COVERAGE_GAP" in codes(result)
    assert result.union_key_count == 2
    assert result.overlap_key_count == 1


def test_venue_clock_and_sequence_conflicts_are_explicit():
    other = trade(
        "b",
        venue_id="venue-b",
        source_sequence=2,
        received_at_utc="2026-07-21T00:00:12Z",
        ingested_at_utc="2026-07-21T00:00:13Z",
    )
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (trade("a"),)), dataset("b", (other,))),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert codes(result) >= {"VENUE_MISMATCH", "CLOCK_MISMATCH", "SEQUENCE_MISMATCH"}


def test_policy_can_register_cross_venue_comparability_without_auto_trust():
    other = trade("b", venue_id="venue-b")
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (trade("a"),)), dataset("b", (other,))),
        BTCCrossSourceReconciliationPolicy("cross-venue-v1", require_same_venue=False),
    )
    assert "VENUE_MISMATCH" not in codes(result)
    assert result.source_selected is False


def test_book_snapshot_and_delta_conflicts_are_quarantined():
    left = dataset("a", (delta("a"), snapshot("a")))
    right = dataset("b", (delta("b", "3", previous=99), snapshot("b", "64999", "65001")))
    result = reconcile_canonical_btc_observation_sets(
        (left, right), BTCCrossSourceReconciliationPolicy("exact-v1")
    )
    assert codes(result) >= {"BOOK_MISMATCH", "BOOK_DELTA_MISMATCH", "PREVIOUS_SEQUENCE_MISMATCH"}


def test_reference_price_conflicts_are_quarantined():
    result = reconcile_canonical_btc_observation_sets(
        (dataset("a", (reference("a"),)), dataset("b", (reference("b", "65002", "65001"),))),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert codes(result) >= {"MARK_PRICE_MISMATCH", "INDEX_PRICE_MISMATCH"}


def test_funding_rate_and_interval_conflicts_are_quarantined():
    result = reconcile_canonical_btc_observation_sets(
        (
            dataset("a", (funding("a"),)),
            dataset("b", (funding("b", "0.0002", "2026-07-20T17:00:00Z"),)),
        ),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert codes(result) >= {"FUNDING_RATE_MISMATCH", "FUNDING_INTERVAL_MISMATCH"}


def test_unresolved_rights_and_retention_are_blocking_evidence():
    result = reconcile_canonical_btc_observation_sets(
        (
            dataset("a", (trade("a"),), rights_state="UNRESOLVED"),
            dataset("b", (trade("b"),), retention_state="UNRESOLVED"),
        ),
        BTCCrossSourceReconciliationPolicy("exact-v1"),
    )
    assert codes(result) >= {"RIGHTS_UNRESOLVED", "RETENTION_UNRESOLVED"}


def test_dataset_requires_unique_sorted_keys_and_exact_artifact_lineage():
    with pytest.raises(ValueError, match="unique deterministic"):
        dataset("a", (trade("a"), trade("a")))
    with pytest.raises(ValueError, match="lineage mismatch"):
        dataset("a", (trade("b"),))


def test_dataset_rejects_future_knowledge_and_provider_selection():
    future = trade("a", ingested_at_utc="2026-07-21T00:00:30Z", received_at_utc="2026-07-21T00:00:30Z")
    with pytest.raises(ValueError, match="knowledge after"):
        dataset("a", (future,))
    with pytest.raises(ValueError, match="provider-unselected"):
        dataset("a", (trade("a"),), provider_selected=True)


def test_reconciliation_requires_two_distinct_typed_sources():
    one = dataset("a", (trade("a"),))
    with pytest.raises(ValueError, match="at least two"):
        reconcile_canonical_btc_observation_sets((one,), BTCCrossSourceReconciliationPolicy("p"))
    with pytest.raises(ValueError, match="identities must be unique"):
        reconcile_canonical_btc_observation_sets((one, one), BTCCrossSourceReconciliationPolicy("p"))


def test_three_source_pairwise_reconciliation_is_deterministic():
    items = tuple(dataset(name, (trade(name),)) for name in ("c", "a", "b"))
    first = reconcile_canonical_btc_observation_sets(items, BTCCrossSourceReconciliationPolicy("p"))
    second = reconcile_canonical_btc_observation_sets(tuple(reversed(items)), BTCCrossSourceReconciliationPolicy("p"))
    assert first.result_hash == second.result_hash
    assert first.dataset_hashes == second.dataset_hashes


def test_contracts_and_finding_details_are_immutable():
    item = dataset("a", (trade("a"),))
    with pytest.raises(FrozenInstanceError):
        item.source_id = "changed"
    result = reconcile_canonical_btc_observation_sets(
        (item, dataset("b", (trade("b", "65001"),))),
        BTCCrossSourceReconciliationPolicy("p"),
    )
    with pytest.raises(TypeError):
        result.findings[0].detail["new"] = "unsafe"


def test_dataset_hash_covers_registered_artifact_and_observations():
    left = dataset("a", (trade("a"),))
    changed = dataset("b", (trade("b", "65001"),))
    assert left.dataset_hash != changed.dataset_hash
    assert len(left.dataset_hash) == 64
