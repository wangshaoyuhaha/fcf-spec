from __future__ import annotations

from datetime import datetime
from itertools import combinations

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    AShareDailyObservation,
    canonical_decimal,
    instant,
)

from .contracts import (
    AShareCrossSourceReconciliationPolicy,
    AShareCrossSourceReconciliationResult,
    CrossSourceQualityFinding,
    RegisteredCanonicalDailyDataset,
)


def _difference(left: datetime, right: datetime) -> int:
    return int(abs((left - right).total_seconds()))


def _finding(
    code: str,
    datasets: tuple[RegisteredCanonicalDailyDataset, ...],
    *,
    row: AShareDailyObservation | None = None,
    field_name: str | None = None,
    detail: dict[str, str] | None = None,
) -> CrossSourceQualityFinding:
    return CrossSourceQualityFinding(
        code=code,
        severity="BLOCK",
        dataset_ids=tuple(item.dataset_id for item in datasets),
        instrument_id=row.instrument_id if row is not None else None,
        trade_date=row.trade_date if row is not None else None,
        field_name=field_name,
        detail=detail or {},
    )


def reconcile_canonical_a_share_daily_datasets(
    datasets: tuple[RegisteredCanonicalDailyDataset, ...],
    policy: AShareCrossSourceReconciliationPolicy,
) -> AShareCrossSourceReconciliationResult:
    dataset_rows = tuple(datasets)
    if len(dataset_rows) < 2 or not all(
        isinstance(item, RegisteredCanonicalDailyDataset) for item in dataset_rows
    ):
        raise ValueError("reconciliation requires at least two typed datasets")
    if not isinstance(policy, AShareCrossSourceReconciliationPolicy):
        raise TypeError("policy must be AShareCrossSourceReconciliationPolicy")
    dataset_ids = tuple(item.dataset_id for item in dataset_rows)
    source_ids = tuple(item.source_id for item in dataset_rows)
    if len(set(dataset_ids)) != len(dataset_ids) or len(set(source_ids)) != len(source_ids):
        raise ValueError("reconciliation dataset and source identities must be unique")
    ordered = tuple(sorted(dataset_rows, key=lambda item: item.dataset_id))
    maps = tuple(
        {(item.instrument_id, item.trade_date): item for item in dataset.observations}
        for dataset in ordered
    )
    union = set().union(*(set(item) for item in maps))
    overlap = set.intersection(*(set(item) for item in maps))
    findings: list[CrossSourceQualityFinding] = []
    for dataset in ordered:
        if dataset.rights_state == "UNRESOLVED":
            findings.append(_finding("RIGHTS_UNRESOLVED", (dataset,)))
        if dataset.retention_state == "UNRESOLVED":
            findings.append(_finding("RETENTION_UNRESOLVED", (dataset,)))
    for key in sorted(union):
        present = tuple(dataset for dataset, rows in zip(ordered, maps) if key in rows)
        missing = tuple(dataset for dataset, rows in zip(ordered, maps) if key not in rows)
        if missing:
            sample = next(rows[key] for rows in maps if key in rows)
            findings.append(
                _finding(
                    "COVERAGE_GAP",
                    ordered,
                    row=sample,
                    detail={"missing_dataset_ids": ":".join(item.dataset_id for item in missing)},
                )
            )
            continue
        rows = tuple(item[key] for item in maps)
        for left_index, right_index in combinations(range(len(rows)), 2):
            baseline = rows[left_index]
            candidate = rows[right_index]
            pair = (ordered[left_index], ordered[right_index])
            for field_name in ("raw_open", "raw_high", "raw_low", "raw_close"):
                left = getattr(baseline, field_name)
                right = getattr(candidate, field_name)
                if abs(left - right) > policy.price_tolerance:
                    findings.append(
                        _finding(
                            "PRICE_MISMATCH",
                            pair,
                            row=baseline,
                            field_name=field_name,
                            detail={"left": canonical_decimal(left), "right": canonical_decimal(right)},
                        )
                    )
            if abs(baseline.volume - candidate.volume) > policy.volume_tolerance:
                findings.append(
                    _finding(
                        "VOLUME_MISMATCH",
                        pair,
                        row=baseline,
                        field_name="volume",
                        detail={"left": str(baseline.volume), "right": str(candidate.volume)},
                    )
                )
            if abs(baseline.amount - candidate.amount) > policy.amount_tolerance:
                findings.append(
                    _finding(
                        "AMOUNT_MISMATCH",
                        pair,
                        row=baseline,
                        field_name="amount",
                        detail={
                            "left": canonical_decimal(baseline.amount),
                            "right": canonical_decimal(candidate.amount),
                        },
                    )
                )
            factor_left = baseline.adjustment_factor
            factor_right = candidate.adjustment_factor
            if factor_left is None or factor_right is None:
                findings.append(_finding("ADJUSTMENT_FACTOR_MISSING", pair, row=baseline))
            elif factor_left != factor_right or baseline.factor_version != candidate.factor_version:
                findings.append(_finding("ADJUSTMENT_FACTOR_MISMATCH", pair, row=baseline))
            if (
                baseline.factor_available_at_utc is not None
                and candidate.factor_available_at_utc is not None
                and _difference(
                    instant(baseline.factor_available_at_utc, "factor_available_at_utc"),
                    instant(candidate.factor_available_at_utc, "factor_available_at_utc"),
                )
                > policy.clock_tolerance_seconds
            ):
                findings.append(
                    _finding(
                        "CLOCK_MISMATCH",
                        pair,
                        row=baseline,
                        field_name="factor_available_at_utc",
                    )
                )
            if baseline.trading_status != candidate.trading_status:
                findings.append(_finding("TRADING_STATUS_MISMATCH", pair, row=baseline))
            for field_name in (
                "available_at_utc",
                "first_tradable_at_utc",
                "revision_at_utc",
            ):
                if _difference(
                    instant(getattr(baseline, field_name), field_name),
                    instant(getattr(candidate, field_name), field_name),
                ) > policy.clock_tolerance_seconds:
                    findings.append(
                        _finding("CLOCK_MISMATCH", pair, row=baseline, field_name=field_name)
                    )
    findings.sort(key=lambda item: item.finding_hash)
    return AShareCrossSourceReconciliationResult(
        dataset_ids=tuple(item.dataset_id for item in ordered),
        dataset_hashes=tuple(item.dataset_hash for item in ordered),
        policy_hash=policy.policy_hash,
        union_key_count=len(union),
        overlap_key_count=len(overlap),
        findings=tuple(findings),
        quality_state=("QUARANTINE_REVIEW_REQUIRED" if findings else "CONSISTENT"),
    )
