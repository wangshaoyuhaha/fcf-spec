from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_app_1 import (
    reconcile_same_calendar_cross_source_coverage,
)
from apps.fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_app_1 import (
    ClockDeltaSummary,
    NumericDeltaSummary,
    build_same_calendar_cross_source_field_delta_diagnostic,
)
from tests.fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_app_1.test_d1_d6 import (
    _calendar,
    _policy,
    _role,
)


def _diagnostic(tmp_path: Path, **independent_changes: object):
    qmt = _role("QMT_LOCAL_EXPORT", "qmt")
    independent = _role(
        "INDEPENDENT_REFERENCE",
        "independent",
        **independent_changes,
    )
    coverage = reconcile_same_calendar_cross_source_coverage(
        qmt,
        independent,
        _calendar(tmp_path),
        _policy(),
    )
    return (
        build_same_calendar_cross_source_field_delta_diagnostic(
            qmt,
            independent,
            coverage,
        ),
        qmt,
        independent,
        coverage,
    )


def _numeric(result, name: str) -> NumericDeltaSummary:
    return next(item for item in result.numeric_summaries if item.field_name == name)


def _clock(result, name: str) -> ClockDeltaSummary:
    return next(item for item in result.clock_summaries if item.field_name == name)


def test_identical_sources_produce_zero_delta_diagnostic(tmp_path: Path) -> None:
    result, _, _, coverage = _diagnostic(tmp_path)

    assert result.coverage_result_hash == coverage.result_hash
    assert result.artifact_independence_proof_hash == (
        coverage.artifact_independence.proof_hash
    )
    assert result.overlap_key_count == 3
    assert all(item.nonzero_count == 0 for item in result.numeric_summaries)
    assert all(item.nonzero_count == 0 for item in result.clock_summaries)
    assert result.factor_missing_pair_count == 0
    assert result.factor_version_mismatch_count == 0
    assert result.trading_status_mismatch_count == 0
    assert result.operator_review_required is True
    assert result.threshold_set is False
    assert result.source_ranked is False
    assert result.source_selected is False


def test_exact_numeric_deltas_are_summarized_without_thresholds(
    tmp_path: Path,
) -> None:
    result, _, _, coverage = _diagnostic(
        tmp_path,
        raw_close=Decimal("11.5"),
        volume=1100,
        amount=Decimal("10600"),
    )

    close = _numeric(result, "raw_close")
    volume = _numeric(result, "volume")
    amount = _numeric(result, "amount")
    assert coverage.quality_state == "QUARANTINE_REVIEW_REQUIRED"
    assert (close.observation_count, close.nonzero_count) == (3, 3)
    assert (close.total_abs_delta, close.max_abs_delta) == (
        Decimal("1.5"),
        Decimal("0.5"),
    )
    assert (volume.total_abs_delta, volume.max_abs_delta) == (
        Decimal("300"),
        Decimal("100"),
    )
    assert (amount.total_abs_delta, amount.max_abs_delta) == (
        Decimal("300"),
        Decimal("100"),
    )
    assert result.threshold_set is False


def test_missing_adjustment_factors_remain_visible(tmp_path: Path) -> None:
    result, _, _, _ = _diagnostic(
        tmp_path,
        adjustment_factor=None,
        factor_version=None,
        factor_available_at_utc=None,
    )

    factor = _numeric(result, "adjustment_factor")
    factor_clock = _clock(result, "factor_available_at_utc")
    assert result.factor_missing_pair_count == 3
    assert factor.observation_count == 0
    assert factor_clock.observation_count == 0


def test_factor_versions_and_registered_clocks_are_diagnostic_fields(
    tmp_path: Path,
) -> None:
    result, _, _, _ = _diagnostic(
        tmp_path,
        factor_version="factor-v2",
        available_at_utc="2026-07-21T08:01:30Z",
        first_tradable_at_utc="2026-07-21T08:01:30Z",
        ingested_at_utc="2026-07-21T08:02:30Z",
        revision_at_utc="2026-07-21T09:00:30Z",
    )

    assert result.factor_version_mismatch_count == 3
    assert _clock(result, "available_at_utc").total_abs_seconds > 0
    assert _clock(result, "first_tradable_at_utc").total_abs_seconds > 0
    assert _clock(result, "revision_at_utc").total_abs_seconds > 0


def test_trading_status_mismatch_is_counted(tmp_path: Path) -> None:
    result, _, _, _ = _diagnostic(
        tmp_path,
        raw_open=Decimal("10"),
        raw_high=Decimal("10"),
        raw_low=Decimal("10"),
        raw_close=Decimal("10"),
        volume=0,
        amount=Decimal("0"),
        trading_status="OBSERVED_SUSPENDED",
    )

    assert result.trading_status_mismatch_count == 3


def test_coverage_and_role_lineage_cannot_be_mixed(tmp_path: Path) -> None:
    _, qmt, independent, coverage = _diagnostic(tmp_path)
    changed_independent = _role(
        "INDEPENDENT_REFERENCE",
        "independent",
        raw_close=Decimal("11.5"),
    )

    with pytest.raises(ValueError, match="role lineage disagrees"):
        build_same_calendar_cross_source_field_delta_diagnostic(
            qmt,
            changed_independent,
            coverage,
        )


def test_diagnostic_is_deterministic(tmp_path: Path) -> None:
    first, qmt, independent, coverage = _diagnostic(tmp_path)

    assert first == build_same_calendar_cross_source_field_delta_diagnostic(
        qmt,
        independent,
        coverage,
    )


def test_diagnostic_authority_boundary_is_immutable(tmp_path: Path) -> None:
    result, _, _, _ = _diagnostic(tmp_path)

    with pytest.raises(ValueError, match="diagnostic state is immutable"):
        replace(result, diagnostic_state="SOURCE_SELECTED")
    with pytest.raises(ValueError, match="cannot decide or select"):
        replace(result, operator_review_required=False)
    with pytest.raises(ValueError, match="cannot decide or select"):
        replace(result, threshold_set=True)
    with pytest.raises(ValueError, match="cannot decide or select"):
        replace(result, source_ranked=True)
    with pytest.raises(ValueError, match="cannot decide or select"):
        replace(result, source_selected=True)


def test_summary_contracts_reject_inconsistent_magnitudes() -> None:
    with pytest.raises(ValueError, match="magnitudes are inconsistent"):
        NumericDeltaSummary(
            field_name="raw_close",
            observation_count=3,
            nonzero_count=0,
            total_abs_delta=Decimal("1"),
            max_abs_delta=Decimal("1"),
        )
    with pytest.raises(ValueError, match="zero state is inconsistent"):
        ClockDeltaSummary(
            field_name="available_at_utc",
            observation_count=3,
            nonzero_count=1,
            total_abs_seconds=0,
            max_abs_seconds=0,
        )
