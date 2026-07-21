from __future__ import annotations

from dataclasses import replace

import pytest

from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationPolicy,
    reconcile_canonical_btc_observation_sets,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1.contracts import (
    comparison_key,
)
from apps.fcp_0045_btc_cross_source_exact_observation_delta_evidence_ledger_app_1 import (
    build_btc_cross_source_exact_observation_delta_evidence_ledger,
    ledger_fields,
)
from tests.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1.test_d1_d6 import (
    dataset,
    delta,
    funding,
    reference,
    snapshot,
    trade,
)


def _ordered(*observations):
    return tuple(sorted(observations, key=comparison_key))


def _ledger(left_observations=None, right_observations=None, names=("a", "b")):
    left_rows = left_observations or (trade(names[0]),)
    right_rows = right_observations or (trade(names[1]),)
    datasets = (
        dataset(names[0], _ordered(*left_rows)),
        dataset(names[1], _ordered(*right_rows)),
    )
    policy = BTCCrossSourceReconciliationPolicy("ledger-policy-v1")
    result = reconcile_canonical_btc_observation_sets(datasets, policy)
    return (
        build_btc_cross_source_exact_observation_delta_evidence_ledger(
            datasets,
            policy,
            result,
        ),
        datasets,
        policy,
        result,
    )


def test_exact_trade_pair_preserves_complete_closed_field_evidence():
    ledger, datasets, policy, result = _ledger()

    assert tuple(item.dataset_id for item in ledger.dataset_lineage) == (
        "dataset-a",
        "dataset-b",
    )
    assert ledger.policy_hash == policy.policy_hash
    assert ledger.reconciliation_result_hash == result.result_hash
    assert ledger.dataset_pair_count == 1
    assert ledger.pair_key_count == 1
    assert len(ledger.entries) == len(ledger_fields("TRADE"))
    assert ledger.incomplete_entry_count == 0
    assert ledger.operator_review_required is True
    assert ledger.source_selected is False
    assert ledger.dataset_lineage[0].dataset_hash == datasets[0].dataset_hash


def test_trade_decimal_text_clock_and_hash_deltas_are_row_addressable():
    right = trade(
        "b",
        price="65002",
        quantity="2",
        side="SELL",
        source_sequence=2,
        received_at_utc="2026-07-21T00:00:12Z",
        ingested_at_utc="2026-07-21T00:00:13Z",
    )
    ledger, *_ = _ledger(right_observations=(right,))
    by_field = {item.field_name: item for item in ledger.entries}

    assert by_field["price"].left_value == "65000"
    assert by_field["price"].right_value == "65002"
    assert by_field["price"].delta_value == "2"
    assert by_field["quantity"].delta_value == "1"
    assert by_field["source_sequence"].delta_value == "1"
    assert by_field["received_at_utc"].delta_value == "2"
    assert by_field["aggressor_side"].delta_value is None
    assert by_field["observation_hash"].comparison_state == "DELTA_PRESENT"


@pytest.mark.parametrize(
    ("left", "right", "kind", "field_name", "left_value", "right_value"),
    (
        (snapshot("a"), snapshot("b", bid="64999"), "BOOK_SNAPSHOT", "bids", '[["65000","1"]]', '[["64999","1"]]'),
        (delta("a"), delta("b", bid_quantity="3"), "BOOK_DELTA", "bid_updates", '[["65000","2"]]', '[["65000","3"]]'),
        (reference("a"), reference("b", mark="65002"), "REFERENCE_PRICE", "mark_price", "65000", "65002"),
        (funding("a"), funding("b", rate="0.0002"), "FUNDING", "funding_rate", "0.0001", "0.0002"),
    ),
)
def test_every_btc_observation_kind_has_exact_closed_field_evidence(
    left,
    right,
    kind,
    field_name,
    left_value,
    right_value,
):
    ledger, *_ = _ledger((left,), (right,))
    fields = tuple(item.field_name for item in ledger.entries)
    target = next(item for item in ledger.entries if item.field_name == field_name)

    assert fields == ledger_fields(kind)
    assert target.left_value == left_value
    assert target.right_value == right_value
    assert target.comparison_state == "DELTA_PRESENT"


def test_pair_coverage_gap_preserves_incomplete_values_without_filling():
    ledger, *_ = _ledger(
        left_observations=(reference("a"), trade("a")),
        right_observations=(trade("b"),),
    )
    reference_entries = [
        item for item in ledger.entries if item.observation_kind == "REFERENCE_PRICE"
    ]

    assert ledger.pair_key_count == 2
    assert len(reference_entries) == len(ledger_fields("REFERENCE_PRICE"))
    assert all(item.left_value is not None for item in reference_entries)
    assert all(item.right_value is None for item in reference_entries)
    assert all(item.comparison_state == "PAIR_INCOMPLETE" for item in reference_entries)
    assert ledger.incomplete_entry_count == len(reference_entries)


def test_three_sources_generate_all_ordered_pairs_deterministically():
    datasets = tuple(dataset(name, (trade(name),)) for name in ("c", "a", "b"))
    policy = BTCCrossSourceReconciliationPolicy("three-source-v1")
    result = reconcile_canonical_btc_observation_sets(datasets, policy)
    first = build_btc_cross_source_exact_observation_delta_evidence_ledger(
        datasets,
        policy,
        result,
    )
    second = build_btc_cross_source_exact_observation_delta_evidence_ledger(
        tuple(reversed(datasets)),
        policy,
        result,
    )

    assert first == second
    assert first.dataset_pair_count == 3
    assert first.pair_key_count == 3
    assert {(item.left_dataset_id, item.right_dataset_id) for item in first.entries} == {
        ("dataset-a", "dataset-b"),
        ("dataset-a", "dataset-c"),
        ("dataset-b", "dataset-c"),
    }


def test_mixed_reconciliation_result_lineage_is_rejected():
    _, datasets, policy, _ = _ledger()
    changed = (datasets[0], dataset("b", (trade("b", price="65002"),)))
    foreign_result = reconcile_canonical_btc_observation_sets(changed, policy)

    with pytest.raises(ValueError, match="disagree with FCP-0023"):
        build_btc_cross_source_exact_observation_delta_evidence_ledger(
            datasets,
            policy,
            foreign_result,
        )


def test_ledger_rejects_entry_and_count_mutation():
    ledger, *_ = _ledger()

    with pytest.raises(ValueError, match="field coverage disagrees"):
        replace(ledger, entries=ledger.entries[:-1])
    with pytest.raises(ValueError, match="state counts disagree"):
        replace(ledger, delta_entry_count=ledger.delta_entry_count + 1)
    with pytest.raises(ValueError, match="pair count disagrees"):
        replace(ledger, dataset_pair_count=2)


def test_ledger_authority_boundary_is_immutable():
    ledger, *_ = _ledger()

    for changes in (
        {"operator_review_required": False},
        {"tolerance_changed": True},
        {"severity_changed": True},
        {"quality_state_changed": True},
        {"source_ranked": True},
        {"source_selected": True},
        {"evidence_replaced": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot decide, mutate, select, replace, or close"):
            replace(ledger, **changes)


def test_ledger_hash_commits_to_exact_entry_values():
    baseline, *_ = _ledger()
    changed, *_ = _ledger(right_observations=(trade("b", price="65000.1"),))

    assert baseline.ledger_hash != changed.ledger_hash
