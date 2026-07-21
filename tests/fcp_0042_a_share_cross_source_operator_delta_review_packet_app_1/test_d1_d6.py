from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1 import (
    build_cross_source_operator_delta_review_packet,
)
from apps.fcp_0042_a_share_cross_source_operator_delta_review_packet_app_1.contracts import (
    FieldReviewFact,
)
from tests.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1.test_d1_d6 import (
    _ledger,
)


def _packet(tmp_path: Path, **changes: object):
    ledger, diagnostic, qmt, independent, coverage = _ledger(tmp_path, **changes)
    return (
        build_cross_source_operator_delta_review_packet(ledger),
        ledger,
        diagnostic,
        qmt,
        independent,
        coverage,
    )


def _fact(packet, field_name: str) -> FieldReviewFact:
    return next(item for item in packet.field_facts if item.field_name == field_name)


def test_exact_parity_requires_operator_confirmation(tmp_path: Path) -> None:
    packet, ledger, _, _, _, _ = _packet(tmp_path)

    assert packet.ledger_hash == ledger.ledger_hash
    assert packet.finding_codes == (
        "ROW_DELTA_LEDGER_REVIEWED",
        "EXACT_CROSS_SOURCE_PARITY_OBSERVED",
    )
    assert packet.review_state == "OPERATOR_CONFIRMATION_REQUIRED"
    assert all(item.exact_match_count == 3 for item in packet.field_facts)
    assert all(item.affected_dates == () for item in packet.field_facts)
    assert packet.operator_review_required is True


def test_numeric_deltas_produce_exact_nonseverity_facts(tmp_path: Path) -> None:
    packet, _, _, _, _, _ = _packet(tmp_path, raw_close=Decimal("11.5"))
    fact = _fact(packet, "raw_close")

    assert packet.finding_codes == (
        "ROW_DELTA_LEDGER_REVIEWED",
        "NUMERIC_DELTAS_PRESENT",
    )
    assert packet.review_state == "OPERATOR_REVIEW_REQUIRED"
    assert (fact.exact_match_count, fact.delta_count, fact.incomplete_count) == (
        0,
        3,
        0,
    )
    assert fact.affected_dates == (
        "2026-07-17",
        "2026-07-20",
        "2026-07-21",
    )
    assert packet.severity_assigned is False
    assert packet.recommendation_generated is False


def test_text_and_clock_findings_use_closed_order(tmp_path: Path) -> None:
    packet, _, _, _, _, _ = _packet(
        tmp_path,
        factor_version="factor-v2",
        available_at_utc="2026-07-21T08:01:30Z",
        first_tradable_at_utc="2026-07-21T08:01:30Z",
        ingested_at_utc="2026-07-21T08:02:30Z",
        revision_at_utc="2026-07-21T09:00:30Z",
    )

    assert packet.finding_codes == (
        "ROW_DELTA_LEDGER_REVIEWED",
        "TEXT_DELTAS_PRESENT",
        "CLOCK_DELTAS_PRESENT",
    )
    assert _fact(packet, "factor_version").delta_count == 3
    assert _fact(packet, "available_at_utc").delta_count == 3


def test_incomplete_pairs_remain_explicit(tmp_path: Path) -> None:
    packet, _, _, _, _, _ = _packet(
        tmp_path,
        adjustment_factor=None,
        factor_version=None,
        factor_available_at_utc=None,
    )

    assert packet.finding_codes == (
        "ROW_DELTA_LEDGER_REVIEWED",
        "INCOMPLETE_PAIRS_PRESENT",
    )
    assert _fact(packet, "adjustment_factor").incomplete_count == 3
    assert _fact(packet, "factor_version").incomplete_count == 3
    assert _fact(packet, "factor_available_at_utc").incomplete_count == 3


def test_packet_preserves_complete_upstream_lineage(tmp_path: Path) -> None:
    packet, ledger, diagnostic, qmt, independent, coverage = _packet(tmp_path)

    assert packet.diagnostic_hash == diagnostic.diagnostic_hash
    assert packet.coverage_result_hash == coverage.result_hash
    assert packet.artifact_independence_proof_hash == (
        coverage.artifact_independence.proof_hash
    )
    assert packet.qmt_role_hash == qmt.role_hash
    assert packet.independent_role_hash == independent.role_hash
    assert packet.ledger_hash == ledger.ledger_hash


def test_packet_is_deterministic(tmp_path: Path) -> None:
    first, ledger, _, _, _, _ = _packet(tmp_path)

    assert first == build_cross_source_operator_delta_review_packet(ledger)


def test_fact_contract_rejects_count_and_date_disagreement() -> None:
    with pytest.raises(ValueError, match="affected dates exceed"):
        FieldReviewFact(
            field_name="raw_close",
            exact_match_count=3,
            delta_count=0,
            incomplete_count=0,
            affected_dates=("2026-07-21",),
        )


def test_packet_rejects_fact_and_finding_disagreement(tmp_path: Path) -> None:
    packet, _, _, _, _, _ = _packet(tmp_path)

    with pytest.raises(ValueError, match="counts disagree with overlap"):
        replace(
            packet,
            field_facts=(
                replace(packet.field_facts[0], exact_match_count=2),
                *packet.field_facts[1:],
            ),
        )
    with pytest.raises(ValueError, match="finding codes disagree"):
        replace(packet, finding_codes=("ROW_DELTA_LEDGER_REVIEWED",))


def test_packet_authority_boundary_is_immutable(tmp_path: Path) -> None:
    packet, _, _, _, _, _ = _packet(tmp_path)

    for changes in (
        {"operator_review_required": False},
        {"severity_assigned": True},
        {"recommendation_generated": True},
        {"threshold_set": True},
        {"source_ranked": True},
        {"source_selected": True},
        {"evidence_replaced": True},
    ):
        with pytest.raises(ValueError, match="cannot decide, recommend, or select"):
            replace(packet, **changes)
