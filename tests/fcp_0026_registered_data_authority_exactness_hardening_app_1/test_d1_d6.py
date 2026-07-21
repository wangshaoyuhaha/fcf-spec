import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    digest,
)
from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationResult,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationPolicy,
    BTCCrossSourceReconciliationResult,
)
from apps.fcp_0024_cross_market_registered_data_readiness_review_packet_app_1.contracts import (
    CrossMarketDataReadinessPacket,
    MarketDataReadinessRow,
)


def a_share_result(**updates):
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
    return AShareCrossSourceReconciliationResult(**values)


def btc_result(**updates):
    values = {
        "dataset_ids": ("dataset-a", "dataset-b"),
        "dataset_hashes": ("d" * 64, "e" * 64),
        "policy_hash": "f" * 64,
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
        "reconciliation_result_hash": "1" * 64,
        "dataset_hashes": (first * 64, second * 64),
        "quality_state": "CONSISTENT",
        "blocking_finding_count": 0,
        "warning_finding_count": 0,
        "union_key_count": 1,
        "overlap_key_count": 1,
        "readiness_state": "READY_FOR_OPERATOR_REVIEW",
    }
    values.update(updates)
    return MarketDataReadinessRow(**values)


@pytest.mark.parametrize("value", ["A" * 64, " " + "a" * 64, b"a" * 64])
def test_shared_a_share_digest_rejects_nonexact_inputs(value):
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        digest(value, "digest")


@pytest.mark.parametrize("field", ["union_key_count", "overlap_key_count"])
def test_a_share_result_rejects_boolean_counts(field):
    with pytest.raises(ValueError, match="nonnegative integers"):
        a_share_result(**{field: True})


def test_a_share_result_requires_exact_false_source_selection():
    with pytest.raises(ValueError, match="cannot bypass"):
        a_share_result(source_selected=0)


@pytest.mark.parametrize("field", ["dataset_hashes", "policy_hash"])
def test_btc_result_rejects_uppercase_digests(field):
    update = {field: ("D" * 64, "e" * 64) if field == "dataset_hashes" else "F" * 64}
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        btc_result(**update)


@pytest.mark.parametrize("field", ["union_key_count", "overlap_key_count"])
def test_btc_result_rejects_boolean_counts(field):
    with pytest.raises(ValueError, match="nonnegative integers"):
        btc_result(**{field: True})


@pytest.mark.parametrize(
    "field,value",
    [
        ("calculation_authority", "UNTRUSTED"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION"),
    ],
)
def test_btc_result_rejects_authority_override(field, value):
    with pytest.raises(ValueError, match="authority identities"):
        btc_result(**{field: value})


def test_btc_policy_rejects_untyped_clock_and_false_like_selection():
    with pytest.raises(ValueError, match="clock_tolerance_seconds"):
        BTCCrossSourceReconciliationPolicy("policy", clock_tolerance_seconds="0")
    with pytest.raises(ValueError, match="cannot select"):
        BTCCrossSourceReconciliationPolicy("policy", source_selection_allowed=0)


def test_readiness_row_requires_exact_false_source_selection():
    with pytest.raises(ValueError, match="cannot select"):
        row("A_SHARE", "a", "b", source_selected=0)


@pytest.mark.parametrize(
    "updates",
    [
        {"source_selected": 0},
        {"calculation_authority": "UNTRUSTED"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "DECISION"},
    ],
)
def test_packet_rejects_boundary_or_authority_override(updates):
    with pytest.raises(ValueError):
        CrossMarketDataReadinessPacket(
            (row("A_SHARE", "a", "b"), row("BTC", "c", "d")),
            "2026-07-21T00:00:00Z",
            "READY_FOR_OPERATOR_REVIEW",
            **updates,
        )


def test_exact_registered_values_remain_valid():
    a_share_result()
    btc_result()
    packet = CrossMarketDataReadinessPacket(
        (row("A_SHARE", "a", "b"), row("BTC", "c", "d")),
        "2026-07-21T00:00:00Z",
        "READY_FOR_OPERATOR_REVIEW",
    )
    assert packet.calculation_authority == "DETERMINISTIC_ENGINE"
    assert packet.evidence_authority == "REGISTERED_EVIDENCE"
    assert packet.ai_role == "ADVISORY_ONLY"
