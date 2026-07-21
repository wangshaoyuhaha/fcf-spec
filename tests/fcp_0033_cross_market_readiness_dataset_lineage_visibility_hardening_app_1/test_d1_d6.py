from dataclasses import replace

import pytest

from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationResult,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationResult,
)
from apps.fcp_0024_cross_market_registered_data_readiness_review_packet_app_1 import (
    MarketDataReadinessRow,
    build_cross_market_data_readiness_review_packet,
)


AS_OF = "2026-07-21T08:00:00Z"


def a_share():
    return AShareCrossSourceReconciliationResult(
        ("a" * 64, "b" * 64),
        "c" * 64,
        2,
        2,
        (),
        "CONSISTENT",
        ("a-one", "a-two"),
    )


def btc():
    return BTCCrossSourceReconciliationResult(
        ("d" * 64, "e" * 64),
        "f" * 64,
        2,
        2,
        (),
        "CONSISTENT",
        ("b-one", "b-two"),
    )


def packet():
    return build_cross_market_data_readiness_review_packet(
        a_share(), btc(), as_of_utc=AS_OF
    )


def test_packet_exposes_exact_market_isolated_dataset_lineage():
    result = packet()
    assert result.rows[0].dataset_ids == ("a-one", "a-two")
    assert result.rows[0].dataset_hashes == ("a" * 64, "b" * 64)
    assert result.rows[1].dataset_ids == ("b-one", "b-two")
    assert result.rows[1].dataset_hashes == ("d" * 64, "e" * 64)


@pytest.mark.parametrize(
    "dataset_ids",
    [
        ("a-one",),
        ("a-one", "a-one"),
        ("a-two", "a-one"),
    ],
)
def test_row_rejects_nonpaired_or_noncanonical_dataset_ids(dataset_ids):
    with pytest.raises(ValueError, match="ordered dataset identity and digest pairs"):
        replace(packet().rows[0], dataset_ids=dataset_ids)


@pytest.mark.parametrize("dataset_ids", [("bad id", "safe-id"), (1, "safe-id")])
def test_row_rejects_invalid_dataset_identifiers(dataset_ids):
    with pytest.raises(ValueError):
        replace(packet().rows[0], dataset_ids=dataset_ids)


def test_row_hash_commits_to_dataset_identity_and_digest_pairs():
    original = packet().rows[0]
    changed = replace(original, dataset_ids=("z-one", "z-two"))
    assert changed.dataset_hashes == original.dataset_hashes
    assert changed.row_hash != original.row_hash


def test_packet_hash_commits_to_visible_row_lineage():
    first = packet()
    second_row = replace(first.rows[0], dataset_ids=("z-one", "z-two"))
    second = replace(first, rows=(second_row, first.rows[1]))
    assert second.packet_hash != first.packet_hash


def test_authority_and_review_boundaries_remain_exact():
    result = packet()
    assert result.operator_review_required is True
    assert result.source_selected is False
    assert result.calculation_authority == "DETERMINISTIC_ENGINE"
    assert result.evidence_authority == "REGISTERED_EVIDENCE"
    assert result.ai_role == "ADVISORY_ONLY"
