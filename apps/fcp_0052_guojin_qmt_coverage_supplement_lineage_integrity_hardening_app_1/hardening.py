from __future__ import annotations

from apps.fcp_0036_guojin_qmt_registered_local_daily_batch_coverage_reconciliation_app_1 import (
    QmtBatchCoverageManifest,
)
from apps.fcp_0037_a_share_registered_expected_trading_date_artifact_profile_app_1 import (
    RegisteredExpectedTradingDateProfile,
)
from apps.fcp_0051_guojin_qmt_historical_coverage_completeness_gate_app_1 import (
    QmtHistoricalCoverageCompletenessEvidence,
    RegisteredCoverageSupplements,
)

from .contracts import (
    CoverageSupplementLineageBundle,
    PaginationBehaviorEvidence,
    PointInTimeSupplementEvidence,
    RowCapResolutionEvidence,
)


def build_coverage_supplement_lineage_bundle(
    *,
    gate: QmtHistoricalCoverageCompletenessEvidence,
    calendar: RegisteredExpectedTradingDateProfile,
    multi_batch_manifest: QmtBatchCoverageManifest,
    pagination: PaginationBehaviorEvidence,
    point_in_time: PointInTimeSupplementEvidence,
    row_cap_resolution: RowCapResolutionEvidence,
) -> CoverageSupplementLineageBundle:
    instrument = gate.instrument_id
    if any(
        value != instrument
        for value in (
            calendar.registration.instrument_id,
            multi_batch_manifest.instrument_id,
            pagination.instrument_id,
            point_in_time.instrument_id,
            row_cap_resolution.instrument_id,
        )
    ):
        raise ValueError("supplement instruments disagree")
    requested_range = (gate.requested_start_date, gate.requested_end_date)
    if any(
        value != requested_range
        for value in (
            (pagination.requested_start_date, pagination.requested_end_date),
            (row_cap_resolution.requested_start_date, row_cap_resolution.requested_end_date),
        )
    ):
        raise ValueError("supplement requested ranges disagree")
    if not (
        calendar.manifest.start_date <= gate.requested_start_date
        and calendar.manifest.end_date >= gate.requested_end_date
    ):
        raise ValueError("calendar does not cover the requested range")
    if not (
        point_in_time.coverage_start_date <= gate.requested_start_date
        and point_in_time.coverage_end_date >= gate.requested_end_date
    ):
        raise ValueError("point-in-time evidence does not cover the requested range")
    if multi_batch_manifest.expected_date_set_hash != calendar.manifest.date_set_hash:
        raise ValueError("multi-batch and calendar date-set hashes disagree")
    if multi_batch_manifest.expected_artifact_sha256 != calendar.manifest.artifact_sha256:
        raise ValueError("multi-batch and calendar artifact hashes disagree")
    if multi_batch_manifest.expected_date_count != calendar.manifest.date_count:
        raise ValueError("multi-batch and calendar date counts disagree")
    batch_count = len(multi_batch_manifest.ordered_batch_hashes)
    if batch_count < 2:
        raise ValueError("coverage supplements require at least two registered batches")
    if pagination.batch_count != batch_count:
        raise ValueError("pagination batch count disagrees with multi-batch evidence")
    if row_cap_resolution.pagination_evidence_hash != pagination.evidence_hash:
        raise ValueError("row-cap resolution pagination lineage disagrees")
    if row_cap_resolution.multi_batch_manifest_hash != multi_batch_manifest.manifest_hash:
        raise ValueError("row-cap resolution batch lineage disagrees")
    if gate.row_cap_state == "AT_REGISTERED_CAP" and (
        row_cap_resolution.observed_row_cap != gate.row_count
    ):
        raise ValueError("row-cap resolution disagrees with the registered gate cap")
    supplements = RegisteredCoverageSupplements(
        expected_date_set_hash=calendar.manifest.date_set_hash,
        pagination_evidence_hash=pagination.evidence_hash,
        multi_batch_manifest_hash=multi_batch_manifest.manifest_hash,
        missing_date_count=len(multi_batch_manifest.missing_dates),
        unexpected_date_count=len(multi_batch_manifest.unexpected_dates),
        conflict_date_count=len(multi_batch_manifest.conflict_dates),
        point_in_time_supplement_hash=point_in_time.evidence_hash,
        row_cap_resolution_hash=row_cap_resolution.evidence_hash,
    )
    return CoverageSupplementLineageBundle(
        gate=gate,
        calendar=calendar,
        multi_batch_manifest=multi_batch_manifest,
        pagination=pagination,
        point_in_time=point_in_time,
        row_cap_resolution=row_cap_resolution,
        supplements=supplements,
    )
