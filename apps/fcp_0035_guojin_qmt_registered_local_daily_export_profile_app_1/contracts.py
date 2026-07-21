from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    digest,
    identifier,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    LocalDailyExportProfile,
    RegisteredLocalDailyExport,
)


QMT_SOURCE_COLUMNS = (
    "timetag",
    "open",
    "high",
    "low",
    "close",
    "volumn",
    "amount",
)
NORMALIZED_COLUMNS = (
    "code",
    "exchange",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
)
_INSTRUMENT = re.compile(r"^(?P<code>[0-9]{6})\.(?P<exchange>XSHG|XSHE)$")


@dataclass(frozen=True)
class QmtLocalDailyExportProfile:
    profile_id: str
    source_id: str
    instrument_id: str
    requested_start_date: str
    requested_end_date: str
    volume_lot_size: int = 100
    adjustment_mode: str = "RAW"
    operator_registered: bool = True
    provider_selected: bool = False
    profile_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", identifier(self.profile_id, "profile_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        try:
            start = date.fromisoformat(self.requested_start_date)
            end = date.fromisoformat(self.requested_end_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("requested coverage dates must be ISO dates") from exc
        if start > end:
            raise ValueError("requested coverage dates are reversed")
        if self.volume_lot_size != 100:
            raise ValueError("QMT daily export volume lot size must be 100 shares")
        mode = str(self.adjustment_mode).strip().upper()
        if mode != "RAW":
            raise ValueError("canonical QMT normalization accepts RAW prices only")
        object.__setattr__(self, "adjustment_mode", mode)
        if self.operator_registered is not True or self.provider_selected is not False:
            raise ValueError("QMT profile must remain Operator-registered and unselected")
        object.__setattr__(
            self,
            "profile_hash",
            canonical_sha256(
                {
                    "adjustment_mode": mode,
                    "instrument_id": instrument,
                    "operator_registered": True,
                    "profile_id": self.profile_id,
                    "provider_selected": False,
                    "requested_end_date": self.requested_end_date,
                    "requested_start_date": self.requested_start_date,
                    "source_columns": QMT_SOURCE_COLUMNS,
                    "source_id": self.source_id,
                    "volume_lot_size": self.volume_lot_size,
                }
            ),
        )

    @property
    def code(self) -> str:
        match = _INSTRUMENT.fullmatch(self.instrument_id)
        if match is None:
            raise RuntimeError("validated instrument identity was lost")
        return match.group("code")

    @property
    def exchange(self) -> str:
        match = _INSTRUMENT.fullmatch(self.instrument_id)
        if match is None:
            raise RuntimeError("validated instrument identity was lost")
        return match.group("exchange")

    def bridge_profile(self) -> LocalDailyExportProfile:
        return LocalDailyExportProfile(
            profile_id=f"{self.profile_id}-normalized",
            source_id=self.source_id,
            source_columns=NORMALIZED_COLUMNS,
            canonical_to_source={
                "instrument_code": "code",
                "exchange": "exchange",
                "trade_date": "date",
                "raw_open": "open",
                "raw_high": "high",
                "raw_low": "low",
                "raw_close": "close",
                "volume": "volume",
                "amount": "amount",
            },
            instrument_format="CODE_EXCHANGE",
        )


@dataclass(frozen=True)
class QmtLocalDailyNormalizationManifest:
    source_artifact_sha256: str
    profile_hash: str
    normalized_artifact_sha256: str
    row_count: int
    actual_start_date: str
    actual_end_date: str
    finding_codes: tuple[str, ...]
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "source_artifact_sha256",
            "profile_hash",
            "normalized_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int):
            raise ValueError("row_count must be an integer")
        if self.row_count <= 0:
            raise ValueError("row_count must be positive")
        for name in ("actual_start_date", "actual_end_date"):
            try:
                date.fromisoformat(getattr(self, name))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be an ISO date") from exc
        if self.actual_start_date > self.actual_end_date:
            raise ValueError("actual coverage dates are reversed")
        findings = tuple(sorted(set(self.finding_codes)))
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_sha256(
                {
                    "actual_end_date": self.actual_end_date,
                    "actual_start_date": self.actual_start_date,
                    "finding_codes": findings,
                    "normalized_artifact_sha256": self.normalized_artifact_sha256,
                    "profile_hash": self.profile_hash,
                    "row_count": self.row_count,
                    "source_artifact_sha256": self.source_artifact_sha256,
                }
            ),
        )


@dataclass(frozen=True)
class QmtLocalDailyNormalizationResult:
    normalized_csv: bytes
    normalized_registration: RegisteredLocalDailyExport
    bridge_profile: LocalDailyExportProfile
    manifest: QmtLocalDailyNormalizationManifest
    quality_state: str
    finding_codes: tuple[str, ...]
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.normalized_csv, bytes) or not self.normalized_csv:
            raise ValueError("normalized_csv must be immutable nonempty bytes")
        if self.quality_state != "BLOCKED_PENDING_SUPPLEMENTS":
            raise ValueError("QMT local export must remain blocked pending supplements")
        findings = tuple(sorted(set(self.finding_codes)))
        if not findings:
            raise ValueError("blocked QMT normalization requires findings")
        if findings != self.manifest.finding_codes:
            raise ValueError("result and manifest findings disagree")
        normalized_sha256 = digest(
            hashlib.sha256(self.normalized_csv).hexdigest(),
            "normalized_csv_sha256",
        )
        if self.normalized_registration.artifact_sha256 != normalized_sha256:
            raise ValueError("normalized registration SHA-256 mismatch")
        if self.normalized_registration.byte_length != len(self.normalized_csv):
            raise ValueError("normalized registration byte length mismatch")
        if self.manifest.normalized_artifact_sha256 != normalized_sha256:
            raise ValueError("normalization manifest SHA-256 mismatch")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain mandatory")
        object.__setattr__(self, "finding_codes", findings)


@dataclass(frozen=True)
class QmtFrontAdjustmentReference:
    raw_artifact_sha256: str
    front_artifact_sha256: str
    profile_hash: str
    row_count: int
    boundary_dates: tuple[str, ...]
    latest_cash_offset: Decimal
    adjustment_semantics: str = "ADDITIVE_PRICE_REFERENCE_ONLY"
    factor_authority: bool = False
    operator_review_required: bool = True
    reference_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("raw_artifact_sha256", "front_artifact_sha256", "profile_hash"):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int):
            raise ValueError("row_count must be an integer")
        if self.row_count <= 0:
            raise ValueError("row_count must be positive")
        boundaries = tuple(self.boundary_dates)
        for value in boundaries:
            date.fromisoformat(value)
        object.__setattr__(self, "boundary_dates", boundaries)
        if self.adjustment_semantics != "ADDITIVE_PRICE_REFERENCE_ONLY":
            raise ValueError("QMT front reference semantics are closed")
        if self.factor_authority is not False or self.operator_review_required is not True:
            raise ValueError("front reference cannot become factor authority")
        object.__setattr__(
            self,
            "reference_hash",
            canonical_sha256(
                {
                    "adjustment_semantics": self.adjustment_semantics,
                    "boundary_dates": boundaries,
                    "factor_authority": False,
                    "front_artifact_sha256": self.front_artifact_sha256,
                    "latest_cash_offset": canonical_decimal(self.latest_cash_offset),
                    "profile_hash": self.profile_hash,
                    "raw_artifact_sha256": self.raw_artifact_sha256,
                    "row_count": self.row_count,
                }
            ),
        )
