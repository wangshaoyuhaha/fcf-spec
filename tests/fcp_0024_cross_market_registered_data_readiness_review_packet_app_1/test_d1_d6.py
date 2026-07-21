from dataclasses import FrozenInstanceError

import pytest

from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationResult,
    CrossSourceQualityFinding,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceFinding,
    BTCCrossSourceReconciliationResult,
)
from apps.fcp_0024_cross_market_registered_data_readiness_review_packet_app_1 import (
    build_cross_market_data_readiness_review_packet,
)


AS_OF = "2026-07-21T03:00:00Z"


def a_share(blocked=False):
    findings = ()
    if blocked:
        findings = (CrossSourceQualityFinding("COVERAGE_GAP", "BLOCK", ("a-one", "a-two")),)
    return AShareCrossSourceReconciliationResult(
        ("a" * 64, "b" * 64), "c" * 64, 2, 1 if blocked else 2,
        findings, "QUARANTINE_REVIEW_REQUIRED" if blocked else "CONSISTENT",
        ("a-one", "a-two"),
    )


def btc(blocked=False):
    findings = ()
    if blocked:
        findings = (BTCCrossSourceFinding("VENUE_MISMATCH", "BLOCK", ("b-one", "b-two")),)
    return BTCCrossSourceReconciliationResult(
        ("d" * 64, "e" * 64), "f" * 64, 2, 1 if blocked else 2,
        findings, "QUARANTINE_REVIEW_REQUIRED" if blocked else "CONSISTENT",
        ("b-one", "b-two"),
    )


def packet(a_blocked=False, b_blocked=False):
    return build_cross_market_data_readiness_review_packet(
        a_share(a_blocked), btc(b_blocked), as_of_utc=AS_OF
    )


def test_consistent_markets_are_ready_only_for_operator_review():
    result = packet()
    assert result.aggregate_state == "READY_FOR_OPERATOR_REVIEW"
    assert tuple(item.market for item in result.rows) == ("A_SHARE", "BTC")
    assert result.operator_review_required is True
    assert result.source_selected is False


@pytest.mark.parametrize("a_blocked,b_blocked", [(True, False), (False, True), (True, True)])
def test_any_market_quarantine_blocks_aggregate_readiness(a_blocked, b_blocked):
    result = packet(a_blocked, b_blocked)
    assert result.aggregate_state == "QUARANTINE_REVIEW_REQUIRED"
    assert sum(row.blocking_finding_count for row in result.rows) == a_blocked + b_blocked


def test_market_semantics_and_counts_remain_isolated():
    result = packet(True, False)
    a_row, b_row = result.rows
    assert a_row.readiness_state == "QUARANTINE_REVIEW_REQUIRED"
    assert b_row.readiness_state == "READY_FOR_OPERATOR_REVIEW"
    assert a_row.dataset_hashes == ("a" * 64, "b" * 64)
    assert b_row.dataset_hashes == ("d" * 64, "e" * 64)


def test_packet_preserves_authority_boundaries():
    result = packet()
    assert result.calculation_authority == "DETERMINISTIC_ENGINE"
    assert result.evidence_authority == "REGISTERED_EVIDENCE"
    assert result.ai_role == "ADVISORY_ONLY"


def test_packet_is_deterministic_and_hashes_typed_evidence():
    first = packet()
    second = packet()
    assert first.packet_hash == second.packet_hash
    assert first.rows[0].reconciliation_result_hash == a_share().result_hash
    assert first.rows[1].reconciliation_result_hash == btc().result_hash


def test_packet_and_rows_are_immutable():
    result = packet()
    with pytest.raises(FrozenInstanceError):
        result.aggregate_state = "changed"
    with pytest.raises(FrozenInstanceError):
        result.rows[0].market = "BTC"


def test_builder_rejects_untyped_or_swapped_market_evidence():
    with pytest.raises(TypeError, match="A-share"):
        build_cross_market_data_readiness_review_packet(btc(), btc(), as_of_utc=AS_OF)
    with pytest.raises(TypeError, match="BTC"):
        build_cross_market_data_readiness_review_packet(a_share(), a_share(), as_of_utc=AS_OF)


def test_builder_rejects_invalid_as_of_clock():
    with pytest.raises(ValueError):
        build_cross_market_data_readiness_review_packet(a_share(), btc(), as_of_utc="not-utc")


def test_no_row_or_packet_can_select_a_source():
    result = packet(True, True)
    assert all(row.source_selected is False for row in result.rows)
    assert result.source_selected is False
