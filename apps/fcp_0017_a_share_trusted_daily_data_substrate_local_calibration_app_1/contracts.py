from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Mapping


CANONICAL_COLUMNS = (
    "instrument_id",
    "trade_date",
    "raw_open",
    "raw_high",
    "raw_low",
    "raw_close",
    "volume",
    "amount",
    "adjustment_factor",
    "factor_version",
    "factor_available_at_utc",
    "event_at_utc",
    "available_at_utc",
    "first_tradable_at_utc",
    "ingested_at_utc",
    "revision_at_utc",
    "trading_status",
)
LAYERS = ("RAW", "NORMALIZED", "RESEARCH")
TRADING_STATUSES = ("OBSERVED_TRADING", "OBSERVED_SUSPENDED", "UNKNOWN")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")


def identifier(value: object, name: str) -> str:
    result = str(value).strip()
    if _SAFE_ID.fullmatch(result) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return result


def digest(value: object, name: str) -> str:
    result = str(value).strip().lower()
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return result


def instant(value: object, name: str) -> datetime:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return parsed


def utc(value: object, name: str) -> str:
    return instant(value, name).isoformat().replace("+00:00", "Z")


def decimal_value(value: object, name: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, (bool, float)):
        raise ValueError(f"{name} must be an exact decimal")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be an exact decimal") from exc
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise ValueError(f"{name} is outside its exact-value domain")
    return result


def canonical_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class RegisteredDailyArtifact:
    artifact_id: str
    source_id: str
    artifact_sha256: str
    byte_length: int
    registered_at_utc: str
    rights_state: str
    retention_state: str
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    operator_registered: bool = True
    raw_repository_storage_allowed: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(self, "artifact_sha256", digest(self.artifact_sha256, "artifact_sha256"))
        if isinstance(self.byte_length, bool) or not 1 <= self.byte_length <= 25_000_000:
            raise ValueError("byte_length exceeds the bounded local calibration limit")
        object.__setattr__(self, "registered_at_utc", utc(self.registered_at_utc, "registered_at_utc"))
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {"UNRESOLVED", "SESSION_ONLY", "LOCAL_DERIVED_ONLY"}:
            raise ValueError("retention_state is not registered")
        if self.usage_scope != "LOCAL_EVALUATION_ONLY":
            raise ValueError("usage_scope must remain local evaluation only")
        if self.operator_registered is not True:
            raise ValueError("artifact requires Operator registration")
        if self.raw_repository_storage_allowed or self.provider_selected:
            raise ValueError("local calibration cannot grant storage or provider authority")


@dataclass(frozen=True)
class AShareDailyObservation:
    instrument_id: str
    trade_date: str
    raw_open: Decimal
    raw_high: Decimal
    raw_low: Decimal
    raw_close: Decimal
    volume: int
    amount: Decimal
    adjustment_factor: Decimal | None
    factor_version: str | None
    factor_available_at_utc: str | None
    event_at_utc: str
    available_at_utc: str
    first_tradable_at_utc: str
    ingested_at_utc: str
    revision_at_utc: str
    trading_status: str
    source_artifact_sha256: str

    def __post_init__(self) -> None:
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        for name in ("raw_open", "raw_high", "raw_low", "raw_close"):
            object.__setattr__(self, name, decimal_value(getattr(self, name), name, positive=True))
        object.__setattr__(self, "amount", decimal_value(self.amount, "amount"))
        if isinstance(self.volume, bool) or not isinstance(self.volume, int) or self.volume < 0:
            raise ValueError("volume must be a nonnegative integer")
        if self.raw_low > min(self.raw_open, self.raw_close):
            raise ValueError("raw_low exceeds an opening or closing price")
        if self.raw_high < max(self.raw_open, self.raw_close) or self.raw_low > self.raw_high:
            raise ValueError("raw OHLC relationship is invalid")
        factor = self.adjustment_factor
        if factor is not None:
            factor = decimal_value(factor, "adjustment_factor", positive=True)
            object.__setattr__(self, "adjustment_factor", factor)
            object.__setattr__(self, "factor_version", identifier(self.factor_version, "factor_version"))
            if self.factor_available_at_utc is None:
                raise ValueError("factor availability is required with adjustment_factor")
            object.__setattr__(
                self,
                "factor_available_at_utc",
                utc(self.factor_available_at_utc, "factor_available_at_utc"),
            )
        elif self.factor_version is not None or self.factor_available_at_utc is not None:
            raise ValueError("factor lineage cannot exist without adjustment_factor")
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
        factor_available = (
            instant(self.factor_available_at_utc, "factor_available_at_utc")
            if self.factor_available_at_utc is not None
            else available
        )
        if not (
            event <= available
            and available <= tradable
            and available <= ingested <= revision
            and event <= factor_available <= revision
        ):
            raise ValueError("daily observation clocks are not monotonic")
        status = str(self.trading_status).strip().upper()
        if status not in TRADING_STATUSES:
            raise ValueError("trading_status is not registered")
        object.__setattr__(self, "trading_status", status)
        if status == "OBSERVED_TRADING" and self.volume <= 0:
            raise ValueError("observed trading requires positive volume")
        if status == "OBSERVED_SUSPENDED" and (
            self.volume != 0
            or len({self.raw_open, self.raw_high, self.raw_low, self.raw_close}) != 1
        ):
            raise ValueError("observed suspension requires zero volume and flat OHLC")
        object.__setattr__(
            self,
            "source_artifact_sha256",
            digest(self.source_artifact_sha256, "source_artifact_sha256"),
        )

    def raw_payload(self) -> Mapping[str, object]:
        return MappingProxyType(self._payload(adjusted=False))

    def research_payload(self) -> Mapping[str, object]:
        if self.adjustment_factor is None:
            raise ValueError("adjustment factor is unavailable")
        return MappingProxyType(self._payload(adjusted=True))

    def _payload(self, *, adjusted: bool) -> dict[str, object]:
        factor = self.adjustment_factor if adjusted else Decimal("1")
        if factor is None:
            raise ValueError("adjustment factor is unavailable")
        return {
            "amount": canonical_decimal(self.amount),
            "available_at_utc": self.available_at_utc,
            "close": canonical_decimal(self.raw_close * factor),
            "event_at_utc": self.event_at_utc,
            "factor_version": self.factor_version if adjusted else "RAW-V1",
            "factor_available_at_utc": self.factor_available_at_utc if adjusted else None,
            "first_tradable_at_utc": self.first_tradable_at_utc,
            "high": canonical_decimal(self.raw_high * factor),
            "ingested_at_utc": self.ingested_at_utc,
            "instrument_id": self.instrument_id,
            "low": canonical_decimal(self.raw_low * factor),
            "open": canonical_decimal(self.raw_open * factor),
            "price_view": "FORWARD_ADJUSTED" if adjusted else "RAW",
            "revision_at_utc": self.revision_at_utc,
            "trade_date": self.trade_date,
            "trading_status": self.trading_status,
            "volume": self.volume,
        }


@dataclass(frozen=True)
class DailyLayerManifest:
    layer: str
    artifact_id: str
    content_sha256: str
    parent_sha256: str
    record_count: int
    schema_version: str
    transform_id: str
    rights_state: str
    retention_state: str

    def __post_init__(self) -> None:
        layer = str(self.layer).strip().upper()
        if layer not in LAYERS:
            raise ValueError("layer is not registered")
        object.__setattr__(self, "layer", layer)
        for name in ("artifact_id", "schema_version", "transform_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("content_sha256", "parent_sha256"):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if isinstance(self.record_count, bool) or self.record_count < 0:
            raise ValueError("record_count must be nonnegative")


@dataclass(frozen=True)
class DailyCalibrationResult:
    observations: tuple[AShareDailyObservation, ...]
    manifests: tuple[DailyLayerManifest, ...]
    quality_state: str
    finding_codes: tuple[str, ...]
    as_of_utc: str
    result_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        manifests = tuple(self.manifests)
        findings = tuple(sorted(set(self.finding_codes)))
        if not observations or tuple(item.layer for item in manifests) != LAYERS:
            raise ValueError("calibration requires observations and all three layers")
        if self.quality_state not in {"READY_FOR_RESEARCH", "BLOCKED"}:
            raise ValueError("quality_state is not registered")
        if (self.quality_state == "READY_FOR_RESEARCH") == bool(findings):
            raise ValueError("quality state and findings disagree")
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "manifests", manifests)
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(self, "as_of_utc", utc(self.as_of_utc, "as_of_utc"))
        object.__setattr__(
            self,
            "result_sha256",
            canonical_sha256(
                {
                    "as_of_utc": self.as_of_utc,
                    "finding_codes": findings,
                    "manifests": [
                        {
                            "content_sha256": item.content_sha256,
                            "layer": item.layer,
                            "parent_sha256": item.parent_sha256,
                            "record_count": item.record_count,
                        }
                        for item in manifests
                    ],
                    "quality_state": self.quality_state,
                }
            ),
        )
