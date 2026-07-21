from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1 import (
    build_cross_source_row_delta_evidence_ledger,
)
from apps.fcp_0041_a_share_cross_source_row_delta_evidence_ledger_app_1.contracts import (
    LEDGER_FIELDS,
)
from tests.fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_app_1.test_d1_d6 import (
    _diagnostic,
)


def _ledger(tmp_path: Path, **changes: object):
    diagnostic, qmt, independent, coverage = _diagnostic(tmp_path, **changes)
    return (
        build_cross_source_row_delta_evidence_ledger(
            qmt,
            independent,
            coverage,
            diagnostic,
        ),
        diagnostic,
        qmt,
        independent,
        coverage,
    )


def test_identical_sources_produce_complete_exact_match_ledger(
    tmp_path: Path,
) -> None:
    ledger, diagnostic, _, _, coverage = _ledger(tmp_path)

    assert ledger.coverage_result_hash == coverage.result_hash
    assert ledger.diagnostic_hash == diagnostic.diagnostic_hash
    assert ledger.artifact_independence_proof_hash == (
        coverage.artifact_independence.proof_hash
    )
    assert ledger.overlap_key_count == 3
    assert len(ledger.entries) == 3 * len(LEDGER_FIELDS)
    assert ledger.mismatch_entry_count == 0
    assert ledger.incomplete_entry_count == 0
    assert all(item.comparison_state == "EXACT_MATCH" for item in ledger.entries)
    assert ledger.operator_review_required is True
    assert ledger.threshold_set is False
    assert ledger.source_ranked is False
    assert ledger.source_selected is False
    assert ledger.evidence_replaced is False


def test_numeric_delta_is_addressable_by_instrument_date_and_field(
    tmp_path: Path,
) -> None:
    ledger, _, _, _, _ = _ledger(tmp_path, raw_close=Decimal("11.5"))
    entries = [item for item in ledger.entries if item.field_name == "raw_close"]

    assert len(entries) == 3
    assert ledger.mismatch_entry_count == 3
    assert all(item.instrument_id == "600036.XSHG" for item in entries)
    assert [item.trade_date for item in entries] == [
        "2026-07-17",
        "2026-07-20",
        "2026-07-21",
    ]
    assert all(item.qmt_value == "11" for item in entries)
    assert all(item.independent_value == "11.5" for item in entries)
    assert all(item.delta_value == "0.5" for item in entries)
    assert all(item.comparison_state == "DELTA_PRESENT" for item in entries)


def test_missing_factor_lineage_remains_row_addressable(tmp_path: Path) -> None:
    ledger, _, _, _, _ = _ledger(
        tmp_path,
        adjustment_factor=None,
        factor_version=None,
        factor_available_at_utc=None,
    )
    incomplete = [
        item for item in ledger.entries if item.comparison_state == "PAIR_INCOMPLETE"
    ]

    assert ledger.incomplete_entry_count == 9
    assert {item.field_name for item in incomplete} == {
        "adjustment_factor",
        "factor_available_at_utc",
        "factor_version",
    }


def test_text_and_clock_deltas_preserve_exact_source_values(tmp_path: Path) -> None:
    ledger, _, _, _, _ = _ledger(
        tmp_path,
        factor_version="factor-v2",
        available_at_utc="2026-07-21T08:01:30Z",
        first_tradable_at_utc="2026-07-21T08:01:30Z",
        ingested_at_utc="2026-07-21T08:02:30Z",
        revision_at_utc="2026-07-21T09:00:30Z",
    )
    versions = [item for item in ledger.entries if item.field_name == "factor_version"]
    clocks = [item for item in ledger.entries if item.field_name == "available_at_utc"]

    assert all(item.qmt_value == "factor-v1" for item in versions)
    assert all(item.independent_value == "factor-v2" for item in versions)
    assert all(item.delta_value is None for item in versions)
    assert all(item.delta_kind == "ABS_SECONDS" for item in clocks)
    assert all(int(item.delta_value or "0") > 0 for item in clocks)


def test_entry_order_is_key_then_closed_field_order(tmp_path: Path) -> None:
    ledger, _, _, _, _ = _ledger(tmp_path)

    for offset in range(0, len(ledger.entries), len(LEDGER_FIELDS)):
        block = ledger.entries[offset : offset + len(LEDGER_FIELDS)]
        assert tuple(item.field_name for item in block) == LEDGER_FIELDS


def test_mixed_diagnostic_lineage_is_rejected(tmp_path: Path) -> None:
    _, _, qmt, independent, coverage = _ledger(tmp_path)
    _, changed_diagnostic, _, _, _ = _ledger(
        tmp_path,
        raw_close=Decimal("11.5"),
    )

    with pytest.raises(ValueError, match="disagree with FCP-0040"):
        build_cross_source_row_delta_evidence_ledger(
            qmt,
            independent,
            coverage,
            changed_diagnostic,
        )


def test_ledger_is_deterministic(tmp_path: Path) -> None:
    first, diagnostic, qmt, independent, coverage = _ledger(tmp_path)

    assert first == build_cross_source_row_delta_evidence_ledger(
        qmt,
        independent,
        coverage,
        diagnostic,
    )


def test_ledger_authority_boundary_is_immutable(tmp_path: Path) -> None:
    ledger, _, _, _, _ = _ledger(tmp_path)

    with pytest.raises(ValueError, match="ledger state is immutable"):
        replace(ledger, ledger_state="SOURCE_SELECTED")
    with pytest.raises(ValueError, match="cannot decide, select, or replace"):
        replace(ledger, operator_review_required=False)
    with pytest.raises(ValueError, match="cannot decide, select, or replace"):
        replace(ledger, threshold_set=True)
    with pytest.raises(ValueError, match="cannot decide, select, or replace"):
        replace(ledger, source_ranked=True)
    with pytest.raises(ValueError, match="cannot decide, select, or replace"):
        replace(ledger, source_selected=True)
    with pytest.raises(ValueError, match="cannot decide, select, or replace"):
        replace(ledger, evidence_replaced=True)


def test_ledger_rejects_entry_count_and_state_count_disagreement(
    tmp_path: Path,
) -> None:
    ledger, _, _, _, _ = _ledger(tmp_path)

    with pytest.raises(ValueError, match="entry count disagrees"):
        replace(ledger, entries=ledger.entries[:-1])
    with pytest.raises(ValueError, match="state counts disagree"):
        replace(ledger, mismatch_entry_count=1)
