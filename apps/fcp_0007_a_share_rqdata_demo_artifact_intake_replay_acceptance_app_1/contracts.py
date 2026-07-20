from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Mapping


REQUIRED_COLUMNS = (
    "order_book_id",
    "date",
    "low",
    "open",
    "high",
    "limit_down",
    "num_trades",
    "close",
    "limit_up",
    "volume",
    "total_turnover",
)
OBSERVED_FCP_0006_FIELDS = (
    "close",
    "high",
    "instrument-id",
    "limit-down-price",
    "limit-up-price",
    "low",
    "notional",
    "open",
    "trading-date",
    "volume",
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")


def identifier(value: object, name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return normalized


def sha256_digest(value: object, name: str) -> str:
    normalized = str(value).strip().lower()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


def utc(value: object, name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return parsed.isoformat().replace("+00:00", "Z")


def decimal_value(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def canonical_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RegisteredRQDataDemoArtifact:
    artifact_id: str
    source_id: str
    artifact_sha256: str
    byte_length: int
    registered_at_utc: str
    source_kind: str = "OFFICIAL_PROVIDER_DEMO"
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    entitlement_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    local_artifact_only: bool = True
    raw_repository_storage_allowed: bool = False
    redistribution_allowed: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "artifact_sha256",
            sha256_digest(self.artifact_sha256, "artifact_sha256"),
        )
        if isinstance(self.byte_length, bool) or not 1 <= self.byte_length <= 5_000_000:
            raise ValueError("byte_length must be within the bounded demo limit")
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.source_kind != "OFFICIAL_PROVIDER_DEMO":
            raise ValueError("source_kind must remain official provider demo")
        if self.usage_scope != "LOCAL_EVALUATION_ONLY":
            raise ValueError("usage_scope must remain local evaluation only")
        if self.entitlement_state != "UNRESOLVED" or self.retention_state != "UNRESOLVED":
            raise ValueError("demo rights must remain unresolved")
        if self.local_artifact_only is not True:
            raise ValueError("demo artifact must remain local only")
        if (
            self.raw_repository_storage_allowed
            or self.redistribution_allowed
            or self.provider_selected
        ):
            raise ValueError("demo artifact cannot grant repository or provider authority")


@dataclass(frozen=True)
class AShareDailyBar:
    row_number: int
    instrument_id: str
    trade_date: str
    low: Decimal
    open: Decimal
    high: Decimal
    limit_down: Decimal
    num_trades: int
    close: Decimal
    limit_up: Decimal
    volume: int
    total_turnover: Decimal
    source_artifact_sha256: str

    def __post_init__(self) -> None:
        if isinstance(self.row_number, bool) or self.row_number < 2:
            raise ValueError("row_number must identify a CSV data row")
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an RQData A-share identifier")
        object.__setattr__(self, "instrument_id", instrument)
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        for field_name in (
            "low",
            "open",
            "high",
            "limit_down",
            "close",
            "limit_up",
            "total_turnover",
        ):
            object.__setattr__(
                self,
                field_name,
                decimal_value(getattr(self, field_name), field_name),
            )
        for field_name in ("num_trades", "volume"):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a nonnegative integer")
        prices = (
            self.low,
            self.open,
            self.high,
            self.limit_down,
            self.close,
            self.limit_up,
        )
        if any(value <= 0 for value in prices):
            raise ValueError("daily-bar prices must be positive")
        if self.total_turnover < 0:
            raise ValueError("total_turnover must be nonnegative")
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("daily-bar OHLC invariant failed")
        if self.low > self.high:
            raise ValueError("daily-bar low exceeds high")
        if self.limit_down > self.low or self.limit_up < self.high:
            raise ValueError("daily-bar price-limit invariant failed")
        object.__setattr__(
            self,
            "source_artifact_sha256",
            sha256_digest(self.source_artifact_sha256, "source_artifact_sha256"),
        )

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "close": canonical_decimal(self.close),
                "high": canonical_decimal(self.high),
                "instrument_id": self.instrument_id,
                "limit_down": canonical_decimal(self.limit_down),
                "limit_up": canonical_decimal(self.limit_up),
                "low": canonical_decimal(self.low),
                "num_trades": self.num_trades,
                "open": canonical_decimal(self.open),
                "row_number": self.row_number,
                "total_turnover": canonical_decimal(self.total_turnover),
                "trade_date": self.trade_date,
                "volume": self.volume,
            }
        )


@dataclass(frozen=True)
class RQDataDemoLoadResult:
    artifact: RegisteredRQDataDemoArtifact
    columns: tuple[str, ...]
    rows: tuple[AShareDailyBar, ...]
    repeated_bom_count: int
    normalized_csv_sha256: str
    rowset_sha256: str
    replay_sha256: str

    def __post_init__(self) -> None:
        if self.columns != REQUIRED_COLUMNS:
            raise ValueError("loaded demo columns do not match the registered schema")
        if not self.rows:
            raise ValueError("loaded demo must contain rows")
        if len(self.rows) > 100_000:
            raise ValueError("loaded demo exceeds bounded row count")
        if isinstance(self.repeated_bom_count, bool) or self.repeated_bom_count < 0:
            raise ValueError("repeated_bom_count must be nonnegative")
        for field_name in ("normalized_csv_sha256", "rowset_sha256", "replay_sha256"):
            object.__setattr__(
                self,
                field_name,
                sha256_digest(getattr(self, field_name), field_name),
            )
        if any(
            row.source_artifact_sha256 != self.artifact.artifact_sha256
            for row in self.rows
        ):
            raise ValueError("loaded rows are not linked to the registered artifact")


@dataclass(frozen=True)
class RQDataDemoAcceptanceResult:
    schema_state: str
    product_evidence_state: str
    row_count: int
    instrument_ids: tuple[str, ...]
    date_min: str
    date_max: str
    observed_field_ids: tuple[str, ...]
    missing_required_field_ids: tuple[str, ...]
    finding_codes: tuple[str, ...]
    source_artifact_sha256: str
    normalized_csv_sha256: str
    rowset_sha256: str
    replay_sha256: str
    result_sha256: str
    fcp_0005_readiness_claimed: bool = False
    provider_selection_claimed: bool = False
    product_phase_authorized: bool = False

    def __post_init__(self) -> None:
        if self.schema_state != "READY_FOR_LOCAL_SCHEMA_REPLAY":
            raise ValueError("schema_state must remain local schema replay ready")
        if self.product_evidence_state != "BLOCKED":
            raise ValueError("product evidence must remain blocked")
        if self.row_count <= 0 or not self.instrument_ids:
            raise ValueError("acceptance result requires observed rows")
        if not self.finding_codes or not self.missing_required_field_ids:
            raise ValueError("acceptance result must expose incomplete evidence")
        for field_name in (
            "source_artifact_sha256",
            "normalized_csv_sha256",
            "rowset_sha256",
            "replay_sha256",
            "result_sha256",
        ):
            object.__setattr__(
                self,
                field_name,
                sha256_digest(getattr(self, field_name), field_name),
            )
        if (
            self.fcp_0005_readiness_claimed
            or self.provider_selection_claimed
            or self.product_phase_authorized
        ):
            raise ValueError("demo acceptance cannot claim product authority")
