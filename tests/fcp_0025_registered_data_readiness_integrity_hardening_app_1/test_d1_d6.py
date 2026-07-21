import hashlib
from decimal import Decimal

import pytest

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCObservationHeader,
    BTCRegisteredArtifact,
    BTCTradeObservation,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationPolicy,
    BTCCrossSourceReconciliationResult,
    RegisteredCanonicalBTCObservationSet,
    reconcile_canonical_btc_observation_sets,
)
from apps.fcp_0024_cross_market_registered_data_readiness_review_packet_app_1.contracts import (
    CrossMarketDataReadinessPacket,
    MarketDataReadinessRow,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def result(**updates):
    values = {
        "dataset_ids": ("dataset-a", "dataset-b"),
        "dataset_hashes": ("a" * 64, "b" * 64),
        "policy_hash": "c" * 64,
        "union_key_count": 1,
        "overlap_key_count": 1,
        "findings": (),
        "quality_state": "CONSISTENT",
    }
    values.update(updates)
    return BTCCrossSourceReconciliationResult(**values)


def row(market, first, second, **updates):
    values = {
        "market": market,
        "reconciliation_result_hash": "d" * 64,
        "dataset_hashes": (first * 64, second * 64),
        "dataset_ids": (f"{market.lower()}-{first}", f"{market.lower()}-{second}"),
        "quality_state": "CONSISTENT",
        "blocking_finding_count": 0,
        "warning_finding_count": 0,
        "union_key_count": 1,
        "overlap_key_count": 1,
        "readiness_state": "READY_FOR_OPERATOR_REVIEW",
    }
    values.update(updates)
    return MarketDataReadinessRow(**values)


def dataset(source, semantics):
    content = (source + "\n").encode("ascii")
    artifact = BTCRegisteredArtifact(
        f"artifact-{source}", hashlib.sha256(content).hexdigest(), len(content),
        LocalEventRights("synthetic-test", "local-paper-research", 30)
    )
    header = BTCObservationHeader(
        f"trade-{source}", artifact.artifact_id, "venue-a", "BTC-USDT",
        "PERPETUAL", "TRADE", 1, "2026-07-21T00:00:00Z",
        "2026-07-21T00:00:01Z", "2026-07-21T00:00:01Z"
    )
    trade = BTCTradeObservation(header, Decimal("1"), Decimal("1"), "BUY")
    return RegisteredCanonicalBTCObservationSet(
        f"dataset-{source}", f"source-{source}", artifact, (trade,),
        "2026-07-21T00:00:02Z", semantics
    )


def test_policy_normalizes_invalid_decimal_input_to_value_error():
    with pytest.raises(ValueError, match="decimal-compatible"):
        BTCCrossSourceReconciliationPolicy("policy", price_tolerance="not-decimal")


@pytest.mark.parametrize("field", ["dataset_hashes", "policy_hash"])
def test_btc_result_rejects_invalid_digest_lineage(field):
    updates = {field: ("bad", "b" * 64) if field == "dataset_hashes" else "bad"}
    with pytest.raises(ValueError, match="SHA-256"):
        result(**updates)


def test_btc_result_rejects_untyped_findings():
    with pytest.raises(ValueError, match="typed"):
        result(findings=("unsafe",))


def test_reconciliation_exposes_venue_semantics_conflict():
    reconciled = reconcile_canonical_btc_observation_sets(
        (dataset("a", "semantics-a"), dataset("b", "semantics-b")),
        BTCCrossSourceReconciliationPolicy("policy"),
    )
    assert "VENUE_SEMANTICS_MISMATCH" in {item.code for item in reconciled.findings}
    assert reconciled.quality_state == "QUARANTINE_REVIEW_REQUIRED"


def test_readiness_row_rejects_invalid_result_and_dataset_hashes():
    with pytest.raises(ValueError, match="SHA-256"):
        row("A_SHARE", "a", "b", reconciliation_result_hash="bad")
    with pytest.raises(ValueError, match="SHA-256"):
        row("A_SHARE", "a", "b", dataset_hashes=("bad", "b" * 64))


@pytest.mark.parametrize("field", ["blocking_finding_count", "warning_finding_count", "union_key_count", "overlap_key_count"])
def test_readiness_row_rejects_boolean_count_substitution(field):
    with pytest.raises(ValueError, match="nonnegative"):
        row("A_SHARE", "a", "b", **{field: True})


def test_readiness_row_requires_distinct_dataset_hashes():
    with pytest.raises(ValueError, match="distinct"):
        row("A_SHARE", "a", "a")


def test_packet_rejects_untyped_rows_fail_closed():
    with pytest.raises(ValueError, match="typed readiness rows"):
        CrossMarketDataReadinessPacket(("unsafe", "unsafe"), "2026-07-21T00:00:00Z", "READY_FOR_OPERATOR_REVIEW")


def test_valid_typed_rows_still_form_a_review_only_packet():
    packet = CrossMarketDataReadinessPacket(
        (row("A_SHARE", "a", "b"), row("BTC", "c", "d")),
        "2026-07-21T00:00:00Z",
        "READY_FOR_OPERATOR_REVIEW",
    )
    assert packet.operator_review_required is True
    assert packet.source_selected is False
