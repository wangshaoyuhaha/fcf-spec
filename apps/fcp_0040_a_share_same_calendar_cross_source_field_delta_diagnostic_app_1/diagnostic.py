from __future__ import annotations

from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import instant
from apps.fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_app_1 import (
    SameCalendarCrossSourceCoverageResult,
    SourceRoleDataset,
)

from .contracts import (
    CLOCK_FIELDS,
    NUMERIC_FIELDS,
    ClockDeltaSummary,
    NumericDeltaSummary,
    SameCalendarCrossSourceFieldDeltaDiagnostic,
)


def _seconds(left: str, right: str) -> int:
    return round(abs((instant(left, "clock") - instant(right, "clock")).total_seconds()))


def build_same_calendar_cross_source_field_delta_diagnostic(
    qmt: SourceRoleDataset,
    independent: SourceRoleDataset,
    coverage: SameCalendarCrossSourceCoverageResult,
) -> SameCalendarCrossSourceFieldDeltaDiagnostic:
    if not isinstance(qmt, SourceRoleDataset) or qmt.role != "QMT_LOCAL_EXPORT":
        raise ValueError("qmt input must have QMT_LOCAL_EXPORT role")
    if not isinstance(independent, SourceRoleDataset) or independent.role != "INDEPENDENT_REFERENCE":
        raise ValueError("independent input must have INDEPENDENT_REFERENCE role")
    if not isinstance(coverage, SameCalendarCrossSourceCoverageResult):
        raise TypeError("coverage must be a typed FCP-0038 result")
    if coverage.qmt_role_hash != qmt.role_hash or coverage.independent_role_hash != independent.role_hash:
        raise ValueError("diagnostic role lineage disagrees with coverage")
    if (
        coverage.artifact_independence.qmt_source_artifact_hashes
        != qmt.source_artifact_hashes
        or coverage.artifact_independence.independent_source_artifact_hashes
        != independent.source_artifact_hashes
    ):
        raise ValueError("diagnostic artifact lineage disagrees with coverage")
    expected_datasets = {
        (qmt.dataset.dataset_id, qmt.dataset.dataset_hash),
        (independent.dataset.dataset_id, independent.dataset.dataset_hash),
    }
    observed_datasets = set(
        zip(
            coverage.cross_source_result.dataset_ids,
            coverage.cross_source_result.dataset_hashes,
            strict=True,
        )
    )
    if observed_datasets != expected_datasets:
        raise ValueError("diagnostic dataset lineage disagrees with coverage")
    qmt_rows = {(item.instrument_id, item.trade_date): item for item in qmt.dataset.observations}
    independent_rows = {
        (item.instrument_id, item.trade_date): item
        for item in independent.dataset.observations
    }
    overlap = tuple(sorted(set(qmt_rows) & set(independent_rows)))
    if not overlap or len(overlap) != coverage.cross_source_result.overlap_key_count:
        raise ValueError("diagnostic overlap disagrees with coverage")

    numeric_values: dict[str, list[Decimal]] = {name: [] for name in NUMERIC_FIELDS}
    clock_values: dict[str, list[int]] = {name: [] for name in CLOCK_FIELDS}
    factor_missing = 0
    factor_version_mismatch = 0
    status_mismatch = 0
    for key in overlap:
        left = qmt_rows[key]
        right = independent_rows[key]
        for name in ("raw_open", "raw_high", "raw_low", "raw_close", "amount"):
            numeric_values[name].append(abs(getattr(left, name) - getattr(right, name)))
        numeric_values["volume"].append(Decimal(abs(left.volume - right.volume)))
        if left.adjustment_factor is None or right.adjustment_factor is None:
            factor_missing += 1
        else:
            numeric_values["adjustment_factor"].append(
                abs(left.adjustment_factor - right.adjustment_factor)
            )
            if left.factor_version != right.factor_version:
                factor_version_mismatch += 1
        if left.trading_status != right.trading_status:
            status_mismatch += 1
        for name in ("available_at_utc", "first_tradable_at_utc", "revision_at_utc"):
            clock_values[name].append(_seconds(getattr(left, name), getattr(right, name)))
        if left.factor_available_at_utc is not None and right.factor_available_at_utc is not None:
            clock_values["factor_available_at_utc"].append(
                _seconds(left.factor_available_at_utc, right.factor_available_at_utc)
            )

    numeric = tuple(
        NumericDeltaSummary(
            field_name=name,
            observation_count=len(numeric_values[name]),
            nonzero_count=sum(value != 0 for value in numeric_values[name]),
            total_abs_delta=sum(numeric_values[name], Decimal(0)),
            max_abs_delta=max(numeric_values[name], default=Decimal(0)),
        )
        for name in NUMERIC_FIELDS
    )
    clocks = tuple(
        ClockDeltaSummary(
            field_name=name,
            observation_count=len(clock_values[name]),
            nonzero_count=sum(value != 0 for value in clock_values[name]),
            total_abs_seconds=sum(clock_values[name]),
            max_abs_seconds=max(clock_values[name], default=0),
        )
        for name in CLOCK_FIELDS
    )
    return SameCalendarCrossSourceFieldDeltaDiagnostic(
        coverage_result_hash=coverage.result_hash,
        qmt_role_hash=qmt.role_hash,
        independent_role_hash=independent.role_hash,
        artifact_independence_proof_hash=coverage.artifact_independence.proof_hash,
        overlap_key_count=len(overlap),
        numeric_summaries=numeric,
        clock_summaries=clocks,
        factor_missing_pair_count=factor_missing,
        factor_version_mismatch_count=factor_version_mismatch,
        trading_status_mismatch_count=status_mismatch,
    )
