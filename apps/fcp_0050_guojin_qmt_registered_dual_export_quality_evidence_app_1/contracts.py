from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    digest,
    identifier,
    utc,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)


REQUIRED_BLOCKING_FINDINGS = frozenset(
    {
        "ADJUSTMENT_FACTOR_MISSING",
        "EXPECTED_TRADING_CALENDAR_MISSING",
        "EXTERNAL_SDK_ENTITLEMENT_UNRESOLVED",
        "HISTORICAL_COMPLETENESS_UNPROVEN",
        "INDEPENDENT_SOURCE_RECONCILIATION_MISSING",
        "MULTI_BATCH_COVERAGE_MISSING",
        "POINT_IN_TIME_SUPPLEMENTS_MISSING",
        "TRADING_STATUS_UNKNOWN",
    }
)


def signed_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, (bool, float)):
        raise ValueError(f"{name} must be an exact decimal")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be an exact decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class QmtRegisteredRowCapObservation:
    observation_id: str
    observed_cap_rows: int
    observed_at_utc: str
    observation_basis: str = "OPERATOR_REGISTERED_LOCAL_EXPORT_BEHAVIOR"
    operator_registered: bool = True
    pagination_authority: bool = False
    completeness_authority: bool = False
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "observation_id", identifier(self.observation_id, "observation_id")
        )
        if (
            isinstance(self.observed_cap_rows, bool)
            or not isinstance(self.observed_cap_rows, int)
            or not 1 <= self.observed_cap_rows <= 1_000_000
        ):
            raise ValueError("observed_cap_rows must be a bounded positive integer")
        object.__setattr__(
            self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc")
        )
        if self.observation_basis != "OPERATOR_REGISTERED_LOCAL_EXPORT_BEHAVIOR":
            raise ValueError("row-cap observation basis is closed")
        if (
            self.operator_registered is not True
            or self.pagination_authority is not False
            or self.completeness_authority is not False
        ):
            raise ValueError("row-cap observation grants no pagination or completeness authority")
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "completeness_authority": False,
                    "observation_basis": self.observation_basis,
                    "observation_id": self.observation_id,
                    "observed_at_utc": self.observed_at_utc,
                    "observed_cap_rows": self.observed_cap_rows,
                    "operator_registered": True,
                    "pagination_authority": False,
                }
            ),
        )


@dataclass(frozen=True)
class QmtAdjustmentOffsetEntry:
    trade_date: str
    raw_minus_front_cash_offset: Decimal
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        offset = signed_decimal(
            self.raw_minus_front_cash_offset, "raw_minus_front_cash_offset"
        )
        object.__setattr__(self, "raw_minus_front_cash_offset", offset)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "raw_minus_front_cash_offset": canonical_decimal(offset),
                    "trade_date": self.trade_date,
                }
            ),
        )


@dataclass(frozen=True)
class QmtDualExportQualityEvidence:
    evidence_id: str
    raw_registration: RegisteredLocalDailyExport
    front_registration: RegisteredLocalDailyExport
    profile_hash: str
    normalization_manifest_hash: str
    front_reference_hash: str
    normalized_artifact_sha256: str
    instrument_id: str
    requested_start_date: str
    requested_end_date: str
    actual_start_date: str
    actual_end_date: str
    row_cap_observation: QmtRegisteredRowCapObservation
    offset_entries: tuple[QmtAdjustmentOffsetEntry, ...]
    boundary_dates: tuple[str, ...]
    finding_codes: tuple[str, ...]
    as_of_utc: str
    row_count: int
    volume_lot_size: int = 100
    lot_size_consistency_state: str = "CONSISTENT_WITH_100_SHARE_LOTS"
    raw_front_parity_state: str = "DATE_VOLUME_AMOUNT_EXACT"
    row_cap_state: str = "AT_REGISTERED_CAP"
    quality_state: str = "BLOCKED_PENDING_SUPPLEMENTS"
    operator_review_required: bool = True
    adjustment_factor_authority: bool = False
    historical_completeness_claimed: bool = False
    provider_selected: bool = False
    gap_closed: bool = False
    sdk_used: bool = False
    network_used: bool = False
    raw_provider_bytes_committed: bool = False
    local_paths_committed: bool = False
    row_ledger_sha256: str = field(init=False)
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", identifier(self.evidence_id, "evidence_id"))
        if not isinstance(self.raw_registration, RegisteredLocalDailyExport):
            raise TypeError("raw_registration must be RegisteredLocalDailyExport")
        if not isinstance(self.front_registration, RegisteredLocalDailyExport):
            raise TypeError("front_registration must be RegisteredLocalDailyExport")
        if self.raw_registration.source_id != self.front_registration.source_id:
            raise ValueError("raw and front source lineage disagree")
        if self.raw_registration.artifact_sha256 == self.front_registration.artifact_sha256:
            raise ValueError("raw and front artifacts must be distinct")
        for name in (
            "profile_hash",
            "normalization_manifest_hash",
            "front_reference_hash",
            "normalized_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        instrument = str(self.instrument_id).strip().upper()
        if not (
            len(instrument) == 11
            and instrument[:6].isdigit()
            and instrument[6:] in {".XSHG", ".XSHE"}
        ):
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        for name in (
            "requested_start_date",
            "requested_end_date",
            "actual_start_date",
            "actual_end_date",
        ):
            try:
                date.fromisoformat(getattr(self, name))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be an ISO date") from exc
        if self.requested_start_date > self.requested_end_date:
            raise ValueError("requested date range is reversed")
        if self.actual_start_date > self.actual_end_date:
            raise ValueError("actual date range is reversed")
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int):
            raise ValueError("row_count must be an integer")
        if self.row_count <= 0 or self.row_count > self.row_cap_observation.observed_cap_rows:
            raise ValueError("row_count is outside the registered cap")
        if self.volume_lot_size != 100:
            raise ValueError("QMT evidence requires 100-share lots")
        if self.lot_size_consistency_state not in {
            "CONSISTENT_WITH_100_SHARE_LOTS",
            "CONSISTENT_WITH_100_SHARE_LOTS_WITH_ZERO_VOLUME_ROWS",
        }:
            raise ValueError("lot-size consistency state is closed")
        if self.raw_front_parity_state != "DATE_VOLUME_AMOUNT_EXACT":
            raise ValueError("raw/front parity state is closed")
        expected_cap_state = (
            "AT_REGISTERED_CAP"
            if self.row_count == self.row_cap_observation.observed_cap_rows
            else "BELOW_REGISTERED_CAP"
        )
        if self.row_cap_state != expected_cap_state:
            raise ValueError("row-cap state disagrees with registered observation")
        entries = tuple(self.offset_entries)
        if len(entries) != self.row_count:
            raise ValueError("offset ledger row count mismatch")
        dates = tuple(entry.trade_date for entry in entries)
        if dates != tuple(sorted(set(dates))):
            raise ValueError("offset ledger dates must be unique and ordered")
        if dates[0] != self.actual_start_date or dates[-1] != self.actual_end_date:
            raise ValueError("offset ledger coverage mismatch")
        derived_boundaries = tuple(
            current.trade_date
            for previous, current in zip(entries, entries[1:])
            if previous.raw_minus_front_cash_offset
            != current.raw_minus_front_cash_offset
        )
        if tuple(self.boundary_dates) != derived_boundaries:
            raise ValueError("adjustment boundary dates disagree with the offset ledger")
        findings = tuple(sorted(set(self.finding_codes)))
        if findings != tuple(self.finding_codes):
            raise ValueError("finding_codes must be unique and ordered")
        if not REQUIRED_BLOCKING_FINDINGS.issubset(findings):
            raise ValueError("required blocking findings are missing")
        if self.quality_state != "BLOCKED_PENDING_SUPPLEMENTS":
            raise ValueError("QMT dual-export evidence must remain blocked")
        if (
            self.operator_review_required is not True
            or self.adjustment_factor_authority is not False
            or self.historical_completeness_claimed is not False
            or self.provider_selected is not False
            or self.gap_closed is not False
            or self.sdk_used is not False
            or self.network_used is not False
            or self.raw_provider_bytes_committed is not False
            or self.local_paths_committed is not False
        ):
            raise ValueError("quality evidence cannot gain source, factor, runtime, or GAP authority")
        as_of = utc(self.as_of_utc, "as_of_utc")
        as_of_instant = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        for registered_at in (
            self.raw_registration.registered_at_utc,
            self.front_registration.registered_at_utc,
            self.row_cap_observation.observed_at_utc,
        ):
            if datetime.fromisoformat(registered_at.replace("Z", "+00:00")) > as_of_instant:
                raise ValueError("quality evidence cannot precede registered inputs")
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "offset_entries", entries)
        object.__setattr__(self, "boundary_dates", derived_boundaries)
        object.__setattr__(self, "finding_codes", findings)
        ledger_hash = canonical_sha256([entry.entry_hash for entry in entries])
        object.__setattr__(self, "row_ledger_sha256", ledger_hash)
        distribution = Counter(
            canonical_decimal(entry.raw_minus_front_cash_offset) for entry in entries
        )
        distribution_rows = [
            {"raw_minus_front_cash_offset": value, "row_count": distribution[value]}
            for value in sorted(distribution, key=Decimal)
        ]
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "actual_end_date": self.actual_end_date,
                    "actual_start_date": self.actual_start_date,
                    "adjustment_factor_authority": False,
                    "as_of_utc": as_of,
                    "boundary_dates": derived_boundaries,
                    "evidence_id": self.evidence_id,
                    "finding_codes": findings,
                    "front_artifact_sha256": self.front_registration.artifact_sha256,
                    "front_reference_hash": self.front_reference_hash,
                    "historical_completeness_claimed": False,
                    "instrument_id": instrument,
                    "lot_size_consistency_state": self.lot_size_consistency_state,
                    "network_used": False,
                    "normalization_manifest_hash": self.normalization_manifest_hash,
                    "normalized_artifact_sha256": self.normalized_artifact_sha256,
                    "offset_distribution": distribution_rows,
                    "operator_review_required": True,
                    "profile_hash": self.profile_hash,
                    "quality_state": self.quality_state,
                    "raw_artifact_sha256": self.raw_registration.artifact_sha256,
                    "raw_front_parity_state": self.raw_front_parity_state,
                    "requested_end_date": self.requested_end_date,
                    "requested_start_date": self.requested_start_date,
                    "row_cap_observation_hash": self.row_cap_observation.observation_hash,
                    "row_cap_state": self.row_cap_state,
                    "row_count": self.row_count,
                    "row_ledger_sha256": ledger_hash,
                    "sdk_used": False,
                    "volume_lot_size": 100,
                }
            ),
        )

    @property
    def offset_distribution(self) -> tuple[tuple[str, int], ...]:
        counts = Counter(
            canonical_decimal(entry.raw_minus_front_cash_offset)
            for entry in self.offset_entries
        )
        return tuple((value, counts[value]) for value in sorted(counts, key=Decimal))
