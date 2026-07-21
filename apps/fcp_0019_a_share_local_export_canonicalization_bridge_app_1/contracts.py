from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    RegisteredDailyArtifact,
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    identifier,
    instant,
    utc,
)


REQUIRED_PRICE_SEMANTICS = (
    "trade_date",
    "raw_open",
    "raw_high",
    "raw_low",
    "raw_close",
    "volume",
    "amount",
)
INSTRUMENT_FORMATS = ("CANONICAL", "CODE_EXCHANGE")
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")


@dataclass(frozen=True)
class RegisteredLocalDailyExport:
    artifact_id: str
    source_id: str
    artifact_sha256: str
    byte_length: int
    registered_at_utc: str
    rights_state: str
    retention_state: str
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    operator_registered: bool = True
    local_artifact_only: bool = True
    raw_repository_storage_allowed: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self, "artifact_sha256", digest(self.artifact_sha256, "artifact_sha256")
        )
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or not 1 <= self.byte_length <= 50_000_000
        ):
            raise ValueError("byte_length exceeds the bounded local export limit")
        object.__setattr__(
            self, "registered_at_utc", utc(self.registered_at_utc, "registered_at_utc")
        )
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {"UNRESOLVED", "SESSION_ONLY", "LOCAL_DERIVED_ONLY"}:
            raise ValueError("retention_state is not registered")
        if self.usage_scope != "LOCAL_EVALUATION_ONLY":
            raise ValueError("usage_scope must remain local evaluation only")
        if self.operator_registered is not True or self.local_artifact_only is not True:
            raise ValueError("export requires Operator-registered local bytes")
        if (
            self.raw_repository_storage_allowed is not False
            or self.provider_selected is not False
        ):
            raise ValueError("export registration cannot grant storage or provider authority")


@dataclass(frozen=True)
class LocalDailyExportProfile:
    profile_id: str
    source_id: str
    source_columns: tuple[str, ...]
    canonical_to_source: Mapping[str, str]
    instrument_format: str = "CANONICAL"
    delimiter: str = ","
    encoding: str = "UTF-8"
    operator_registered: bool = True
    provider_selected: bool = False
    profile_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", identifier(self.profile_id, "profile_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        columns = tuple(identifier(value, "source column") for value in self.source_columns)
        if not columns or len(columns) != len(set(columns)):
            raise ValueError("source_columns must be nonempty and unique")
        object.__setattr__(self, "source_columns", columns)
        mapping = {
            identifier(key, "canonical semantic"): identifier(value, "source field")
            for key, value in self.canonical_to_source.items()
        }
        instrument_format = str(self.instrument_format).strip().upper()
        if instrument_format not in INSTRUMENT_FORMATS:
            raise ValueError("instrument_format is not registered")
        required = set(REQUIRED_PRICE_SEMANTICS)
        required.update(
            {"instrument_id"}
            if instrument_format == "CANONICAL"
            else {"instrument_code", "exchange"}
        )
        if set(mapping) != required:
            raise ValueError("profile must map the closed local-export semantic schema")
        if set(mapping.values()) - set(columns):
            raise ValueError("profile references an undeclared source column")
        if len(set(mapping.values())) != len(mapping):
            raise ValueError("profile source fields must be unique")
        if self.delimiter != "," or self.encoding != "UTF-8":
            raise ValueError("bridge supports only UTF-8 comma-delimited exports")
        if self.operator_registered is not True or self.provider_selected is not False:
            raise ValueError("profile must remain Operator-registered and provider-unselected")
        object.__setattr__(self, "canonical_to_source", MappingProxyType(mapping))
        object.__setattr__(self, "instrument_format", instrument_format)
        object.__setattr__(
            self,
            "profile_hash",
            canonical_sha256(
                {
                    "canonical_to_source": mapping,
                    "encoding": self.encoding,
                    "instrument_format": instrument_format,
                    "profile_id": self.profile_id,
                    "source_columns": columns,
                    "source_id": self.source_id,
                }
            ),
        )


@dataclass(frozen=True)
class AShareDailyRowSupplement:
    instrument_id: str
    trade_date: str
    event_at_utc: str
    available_at_utc: str
    first_tradable_at_utc: str
    ingested_at_utc: str
    revision_at_utc: str
    trading_status: str
    adjustment_factor: Decimal | None
    factor_version: str | None
    factor_available_at_utc: str | None
    operator_registered: bool = True
    supplement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        for name in (
            "event_at_utc",
            "available_at_utc",
            "first_tradable_at_utc",
            "ingested_at_utc",
            "revision_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        event = instant(self.event_at_utc, "event_at_utc")
        available = instant(self.available_at_utc, "available_at_utc")
        tradable = instant(self.first_tradable_at_utc, "first_tradable_at_utc")
        ingested = instant(self.ingested_at_utc, "ingested_at_utc")
        revision = instant(self.revision_at_utc, "revision_at_utc")
        if not (event <= available <= tradable and available <= ingested <= revision):
            raise ValueError("supplement clocks are not monotonic")
        status = str(self.trading_status).strip().upper()
        if status not in {"OBSERVED_TRADING", "OBSERVED_SUSPENDED", "UNKNOWN"}:
            raise ValueError("trading_status is not registered")
        object.__setattr__(self, "trading_status", status)
        factor = self.adjustment_factor
        if factor is not None:
            factor = decimal_value(factor, "adjustment_factor", positive=True)
            if self.factor_version is None or self.factor_available_at_utc is None:
                raise ValueError("factor value requires explicit version and availability")
            version = identifier(self.factor_version, "factor_version")
            factor_available = utc(
                self.factor_available_at_utc, "factor_available_at_utc"
            )
            if not event <= instant(factor_available, "factor_available_at_utc") <= revision:
                raise ValueError("factor availability is outside row lineage")
            object.__setattr__(self, "adjustment_factor", factor)
            object.__setattr__(self, "factor_version", version)
            object.__setattr__(self, "factor_available_at_utc", factor_available)
        elif self.factor_version is not None or self.factor_available_at_utc is not None:
            raise ValueError("factor lineage cannot exist without adjustment_factor")
        if self.operator_registered is not True:
            raise ValueError("supplement requires Operator registration")
        object.__setattr__(
            self,
            "supplement_hash",
            canonical_sha256(
                {
                    "adjustment_factor": (
                        canonical_decimal(factor) if factor is not None else None
                    ),
                    "available_at_utc": self.available_at_utc,
                    "event_at_utc": self.event_at_utc,
                    "factor_available_at_utc": self.factor_available_at_utc,
                    "factor_version": self.factor_version,
                    "first_tradable_at_utc": self.first_tradable_at_utc,
                    "ingested_at_utc": self.ingested_at_utc,
                    "instrument_id": instrument,
                    "revision_at_utc": self.revision_at_utc,
                    "trade_date": self.trade_date,
                    "trading_status": status,
                }
            ),
        )

    @property
    def key(self) -> tuple[str, str]:
        return self.instrument_id, self.trade_date


@dataclass(frozen=True)
class LocalDailyExportBridgeManifest:
    source_artifact_sha256: str
    profile_hash: str
    supplement_set_hash: str
    canonical_artifact_sha256: str
    row_count: int
    warning_codes: tuple[str, ...]
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "source_artifact_sha256",
            "profile_hash",
            "supplement_set_hash",
            "canonical_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if (
            isinstance(self.row_count, bool)
            or not isinstance(self.row_count, int)
            or self.row_count <= 0
        ):
            raise ValueError("row_count must be a positive integer")
        warnings = tuple(sorted(set(self.warning_codes)))
        object.__setattr__(self, "warning_codes", warnings)
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_sha256(
                {
                    "canonical_artifact_sha256": self.canonical_artifact_sha256,
                    "profile_hash": self.profile_hash,
                    "row_count": self.row_count,
                    "source_artifact_sha256": self.source_artifact_sha256,
                    "supplement_set_hash": self.supplement_set_hash,
                    "warning_codes": warnings,
                }
            ),
        )


@dataclass(frozen=True)
class LocalDailyExportBridgeResult:
    canonical_csv: bytes
    canonical_registration: RegisteredDailyArtifact
    manifest: LocalDailyExportBridgeManifest
    quality_state: str
    finding_codes: tuple[str, ...]
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.canonical_csv, bytes) or not self.canonical_csv:
            raise ValueError("canonical_csv must be immutable nonempty bytes")
        if not isinstance(self.canonical_registration, RegisteredDailyArtifact):
            raise ValueError("canonical_registration is invalid")
        if not isinstance(self.manifest, LocalDailyExportBridgeManifest):
            raise ValueError("manifest is invalid")
        canonical_hash = hashlib.sha256(self.canonical_csv).hexdigest()
        if self.canonical_registration.artifact_sha256 != canonical_hash:
            raise ValueError("canonical registration digest disagrees with bytes")
        if self.canonical_registration.byte_length != len(self.canonical_csv):
            raise ValueError("canonical registration byte length disagrees with bytes")
        if self.manifest.canonical_artifact_sha256 != canonical_hash:
            raise ValueError("bridge manifest digest disagrees with canonical bytes")
        row_count = len(self.canonical_csv.splitlines()) - 1
        if row_count <= 0 or self.manifest.row_count != row_count:
            raise ValueError("bridge manifest row count disagrees with canonical bytes")
        findings = tuple(sorted(set(self.finding_codes)))
        if self.quality_state not in {"READY_FOR_CALIBRATION", "BLOCKED"}:
            raise ValueError("quality_state is not registered")
        if (self.quality_state == "READY_FOR_CALIBRATION") == bool(findings):
            raise ValueError("quality state and findings disagree")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain mandatory")
        object.__setattr__(self, "finding_codes", findings)
