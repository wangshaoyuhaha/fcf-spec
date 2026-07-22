from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
)
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


def _instrument(value: str) -> str:
    normalized = str(value).strip().upper()
    if not (
        len(normalized) == 11
        and normalized[:6].isdigit()
        and normalized[6:] in {".XSHG", ".XSHE"}
    ):
        raise ValueError("instrument_id must be an A-share exchange identifier")
    return normalized


def _range(start_value: str, end_value: str) -> tuple[str, str]:
    try:
        start = date.fromisoformat(start_value)
        end = date.fromisoformat(end_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("coverage range must use ISO dates") from exc
    if start > end:
        raise ValueError("coverage range is reversed")
    return start.isoformat(), end.isoformat()


def _authority_flags(values: tuple[bool, ...]) -> None:
    if values != (True, False, False, False, False):
        raise ValueError("supplement evidence cannot gain runtime or provider authority")


@dataclass(frozen=True)
class PaginationBehaviorEvidence:
    evidence_id: str
    instrument_id: str
    requested_start_date: str
    requested_end_date: str
    behavior: str
    batch_count: int
    maximum_rows_per_batch: int
    operator_registered: bool = True
    provider_selected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    inferred: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", identifier(self.evidence_id, "evidence_id"))
        instrument = _instrument(self.instrument_id)
        start, end = _range(self.requested_start_date, self.requested_end_date)
        if self.behavior != "EXPLICIT_MULTI_EXPORT":
            raise ValueError("pagination behavior must be explicit multi-export")
        for name, minimum in (("batch_count", 2), ("maximum_rows_per_batch", 1)):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"{name} is below its registered minimum")
        _authority_flags(
            (
                self.operator_registered,
                self.provider_selected,
                self.sdk_used,
                self.network_used,
                self.inferred,
            )
        )
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "requested_start_date", start)
        object.__setattr__(self, "requested_end_date", end)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "batch_count": self.batch_count,
                    "behavior": self.behavior,
                    "evidence_id": self.evidence_id,
                    "inferred": False,
                    "instrument_id": instrument,
                    "maximum_rows_per_batch": self.maximum_rows_per_batch,
                    "network_used": False,
                    "operator_registered": True,
                    "provider_selected": False,
                    "requested_end_date": end,
                    "requested_start_date": start,
                    "sdk_used": False,
                }
            ),
        )


@dataclass(frozen=True)
class PointInTimeSupplementEvidence:
    evidence_id: str
    instrument_id: str
    coverage_start_date: str
    coverage_end_date: str
    adjustment_lineage_hash: str
    trading_status_lineage_hash: str
    availability_lineage_hash: str
    revision_lineage_hash: str
    first_tradable_lineage_hash: str
    operator_registered: bool = True
    provider_selected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    inferred: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", identifier(self.evidence_id, "evidence_id"))
        instrument = _instrument(self.instrument_id)
        start, end = _range(self.coverage_start_date, self.coverage_end_date)
        hashes = {}
        for name in (
            "adjustment_lineage_hash",
            "trading_status_lineage_hash",
            "availability_lineage_hash",
            "revision_lineage_hash",
            "first_tradable_lineage_hash",
        ):
            hashes[name] = digest(getattr(self, name), name)
            object.__setattr__(self, name, hashes[name])
        _authority_flags(
            (
                self.operator_registered,
                self.provider_selected,
                self.sdk_used,
                self.network_used,
                self.inferred,
            )
        )
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "coverage_start_date", start)
        object.__setattr__(self, "coverage_end_date", end)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    **hashes,
                    "coverage_end_date": end,
                    "coverage_start_date": start,
                    "evidence_id": self.evidence_id,
                    "inferred": False,
                    "instrument_id": instrument,
                    "network_used": False,
                    "operator_registered": True,
                    "provider_selected": False,
                    "sdk_used": False,
                }
            ),
        )


@dataclass(frozen=True)
class RowCapResolutionEvidence:
    evidence_id: str
    instrument_id: str
    requested_start_date: str
    requested_end_date: str
    observed_row_cap: int
    pagination_evidence_hash: str
    multi_batch_manifest_hash: str
    resolution_method: str = "EXPLICIT_MULTI_BATCH_RECONCILIATION"
    operator_registered: bool = True
    provider_selected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    inferred: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", identifier(self.evidence_id, "evidence_id"))
        instrument = _instrument(self.instrument_id)
        start, end = _range(self.requested_start_date, self.requested_end_date)
        if (
            isinstance(self.observed_row_cap, bool)
            or not isinstance(self.observed_row_cap, int)
            or self.observed_row_cap <= 0
        ):
            raise ValueError("observed_row_cap must be a positive integer")
        if self.resolution_method != "EXPLICIT_MULTI_BATCH_RECONCILIATION":
            raise ValueError("row-cap resolution method is not registered")
        pagination_hash = digest(self.pagination_evidence_hash, "pagination_evidence_hash")
        batch_hash = digest(self.multi_batch_manifest_hash, "multi_batch_manifest_hash")
        _authority_flags(
            (
                self.operator_registered,
                self.provider_selected,
                self.sdk_used,
                self.network_used,
                self.inferred,
            )
        )
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "requested_start_date", start)
        object.__setattr__(self, "requested_end_date", end)
        object.__setattr__(self, "pagination_evidence_hash", pagination_hash)
        object.__setattr__(self, "multi_batch_manifest_hash", batch_hash)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "evidence_id": self.evidence_id,
                    "inferred": False,
                    "instrument_id": instrument,
                    "multi_batch_manifest_hash": batch_hash,
                    "network_used": False,
                    "observed_row_cap": self.observed_row_cap,
                    "operator_registered": True,
                    "pagination_evidence_hash": pagination_hash,
                    "provider_selected": False,
                    "requested_end_date": end,
                    "requested_start_date": start,
                    "resolution_method": self.resolution_method,
                    "sdk_used": False,
                }
            ),
        )


@dataclass(frozen=True)
class CoverageSupplementLineageBundle:
    gate: QmtHistoricalCoverageCompletenessEvidence
    calendar: RegisteredExpectedTradingDateProfile
    multi_batch_manifest: QmtBatchCoverageManifest
    pagination: PaginationBehaviorEvidence
    point_in_time: PointInTimeSupplementEvidence
    row_cap_resolution: RowCapResolutionEvidence
    supplements: RegisteredCoverageSupplements
    operator_review_required: bool = True
    provider_selected: bool = False
    gap_closed: bool = False
    bundle_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.gate, QmtHistoricalCoverageCompletenessEvidence):
            raise TypeError("gate must be FCP-0051 evidence")
        if not isinstance(self.calendar, RegisteredExpectedTradingDateProfile):
            raise TypeError("calendar must be an FCP-0037 profile")
        if not isinstance(self.multi_batch_manifest, QmtBatchCoverageManifest):
            raise TypeError("multi_batch_manifest must be an FCP-0036 manifest")
        if not isinstance(self.pagination, PaginationBehaviorEvidence):
            raise TypeError("pagination must be typed evidence")
        if not isinstance(self.point_in_time, PointInTimeSupplementEvidence):
            raise TypeError("point_in_time must be typed evidence")
        if not isinstance(self.row_cap_resolution, RowCapResolutionEvidence):
            raise TypeError("row_cap_resolution must be typed evidence")
        if not isinstance(self.supplements, RegisteredCoverageSupplements):
            raise TypeError("supplements must be FCP-0051 supplements")
        if (
            self.operator_review_required is not True
            or self.provider_selected is not False
            or self.gap_closed is not False
        ):
            raise ValueError("bundle cannot gain decision, provider, or GAP authority")
        object.__setattr__(
            self,
            "bundle_hash",
            canonical_sha256(
                {
                    "calendar_manifest_hash": self.calendar.manifest.manifest_hash,
                    "gap_closed": False,
                    "gate_evidence_hash": self.gate.evidence_hash,
                    "multi_batch_manifest_hash": self.multi_batch_manifest.manifest_hash,
                    "operator_review_required": True,
                    "pagination_evidence_hash": self.pagination.evidence_hash,
                    "point_in_time_evidence_hash": self.point_in_time.evidence_hash,
                    "provider_selected": False,
                    "row_cap_resolution_hash": self.row_cap_resolution.evidence_hash,
                    "supplement_hash": self.supplements.supplement_hash,
                }
            ),
        )
