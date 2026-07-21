from __future__ import annotations

from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationPolicy,
    reconcile_canonical_a_share_daily_datasets,
)
from apps.fcp_0037_a_share_registered_expected_trading_date_artifact_profile_app_1 import (
    RegisteredExpectedTradingDateProfile,
)

from .contracts import SameCalendarCrossSourceCoverageResult, SourceRoleDataset


def _instrument_and_dates(source: SourceRoleDataset) -> tuple[str, set[str]]:
    instruments = {item.instrument_id for item in source.dataset.observations}
    if len(instruments) != 1:
        raise ValueError("source dataset must target exactly one instrument")
    return next(iter(instruments)), {
        item.trade_date for item in source.dataset.observations
    }


def reconcile_same_calendar_cross_source_coverage(
    qmt: SourceRoleDataset,
    independent: SourceRoleDataset,
    calendar: RegisteredExpectedTradingDateProfile,
    policy: AShareCrossSourceReconciliationPolicy,
) -> SameCalendarCrossSourceCoverageResult:
    if not isinstance(qmt, SourceRoleDataset) or qmt.role != "QMT_LOCAL_EXPORT":
        raise ValueError("qmt input must have QMT_LOCAL_EXPORT role")
    if (
        not isinstance(independent, SourceRoleDataset)
        or independent.role != "INDEPENDENT_REFERENCE"
    ):
        raise ValueError("independent input must have INDEPENDENT_REFERENCE role")
    if not isinstance(calendar, RegisteredExpectedTradingDateProfile):
        raise TypeError("calendar must be RegisteredExpectedTradingDateProfile")
    if qmt.dataset.source_id == independent.dataset.source_id:
        raise ValueError("cross-source roles require distinct source identities")
    qmt_instrument, qmt_dates = _instrument_and_dates(qmt)
    independent_instrument, independent_dates = _instrument_and_dates(independent)
    if not (
        qmt_instrument
        == independent_instrument
        == calendar.registration.instrument_id
    ):
        raise ValueError("datasets and calendar instrument identities disagree")
    expected = set(calendar.dates)
    qmt_missing = tuple(sorted(expected - qmt_dates))
    qmt_unexpected = tuple(sorted(qmt_dates - expected))
    independent_missing = tuple(sorted(expected - independent_dates))
    independent_unexpected = tuple(sorted(independent_dates - expected))
    cross = reconcile_canonical_a_share_daily_datasets(
        (qmt.dataset, independent.dataset), policy
    )
    findings = {"SAME_REGISTERED_CALENDAR_COMPARED"}
    for present, code in (
        (qmt_missing, "QMT_EXPECTED_DATES_MISSING"),
        (qmt_unexpected, "QMT_UNEXPECTED_DATES_PRESENT"),
        (independent_missing, "INDEPENDENT_EXPECTED_DATES_MISSING"),
        (independent_unexpected, "INDEPENDENT_UNEXPECTED_DATES_PRESENT"),
    ):
        if present:
            findings.add(code)
    if cross.quality_state != "CONSISTENT":
        findings.add("CROSS_SOURCE_QUALITY_QUARANTINED")
    if calendar.manifest.quality_state != "REGISTERED_EXPECTED_DATES_READY":
        findings.add("CALENDAR_AUTHORITY_REVIEW_REQUIRED")
    blocked = any(
        (qmt_missing, qmt_unexpected, independent_missing, independent_unexpected)
    ) or cross.quality_state != "CONSISTENT" or (
        calendar.manifest.quality_state != "REGISTERED_EXPECTED_DATES_READY"
    )
    return SameCalendarCrossSourceCoverageResult(
        instrument_id=qmt_instrument,
        calendar_manifest_hash=calendar.manifest.manifest_hash,
        calendar_quality_state=calendar.manifest.quality_state,
        qmt_role_hash=qmt.role_hash,
        independent_role_hash=independent.role_hash,
        qmt_missing_dates=qmt_missing,
        qmt_unexpected_dates=qmt_unexpected,
        independent_missing_dates=independent_missing,
        independent_unexpected_dates=independent_unexpected,
        cross_source_result=cross,
        finding_codes=tuple(findings),
        quality_state=("QUARANTINE_REVIEW_REQUIRED" if blocked else "CONSISTENT"),
    )
