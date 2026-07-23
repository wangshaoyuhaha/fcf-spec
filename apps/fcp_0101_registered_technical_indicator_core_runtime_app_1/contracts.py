from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from types import MappingProxyType


RUNTIME_SCHEMA_VERSION = "fcf-registered-technical-indicator-core-runtime-v1"
INDICATOR_KINDS = ("SMA", "EMA", "BOLLINGER", "RSI", "ATR", "VWAP")
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")
_DIGEST = re.compile(r"^[a-f0-9]{64}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def digest(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if _DIGEST.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be SHA-256")
    return normalized


def utc(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
        or parsed.utcoffset().total_seconds() != 0
    ):
        raise ValueError(f"{field_name} must be UTC")
    return normalized


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def decimal_value(value: object, field_name: str) -> Decimal:
    if type(value) is not str:
        raise ValueError(f"{field_name} must be a decimal string")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class RegisteredMarketArtifact:
    artifact_id: str
    artifact_hash: str
    byte_length: int
    rights_id: str
    registered_at_utc: str
    operator_registered: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_hash", digest(self.artifact_hash, "artifact_hash"))
        if isinstance(self.byte_length, bool) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        object.__setattr__(self, "rights_id", identifier(self.rights_id, "rights_id"))
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.operator_registered is not True:
            raise ValueError("market artifact must be Operator-registered")


@dataclass(frozen=True)
class RegisteredBar:
    timestamp_utc: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    amount: Decimal
    is_suspended: bool

    def __post_init__(self) -> None:
        timestamp = utc(self.timestamp_utc, "timestamp_utc")
        prices = (self.open, self.high, self.low, self.close)
        if any(value <= 0 or not value.is_finite() for value in prices):
            raise ValueError("OHLC prices must be positive finite decimals")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high price violates OHLC ordering")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low price violates OHLC ordering")
        if self.volume < 0 or self.amount < 0:
            raise ValueError("volume and amount must be nonnegative")
        if type(self.is_suspended) is not bool:
            raise ValueError("is_suspended must be boolean")
        if self.is_suspended != (self.volume == 0 and self.amount == 0):
            raise ValueError("suspension must match zero volume and amount")
        object.__setattr__(self, "timestamp_utc", timestamp)


@dataclass(frozen=True)
class RegisteredIndicatorRequest:
    request_id: str
    factor_id: str
    factor_version: str
    indicator_kind: str
    window: int
    multiplier_bps: int
    suspension_policy: str

    def __post_init__(self) -> None:
        for name in ("request_id", "factor_id", "factor_version"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        kind = str(self.indicator_kind).strip().upper()
        if kind not in INDICATOR_KINDS:
            raise ValueError("indicator_kind is not registered")
        if isinstance(self.window, bool) or not 1 <= self.window <= 10000:
            raise ValueError("window must be an integer between 1 and 10000")
        if isinstance(self.multiplier_bps, bool) or self.multiplier_bps < 0:
            raise ValueError("multiplier_bps must be nonnegative")
        if kind == "BOLLINGER":
            if self.multiplier_bps <= 0:
                raise ValueError("BOLLINGER requires a positive multiplier")
        elif self.multiplier_bps != 0:
            raise ValueError("only BOLLINGER may use multiplier_bps")
        policy = str(self.suspension_policy).strip().upper()
        if policy != "EXCLUDE":
            raise ValueError("only registered EXCLUDE suspension policy is allowed")
        object.__setattr__(self, "indicator_kind", kind)
        object.__setattr__(self, "suspension_policy", policy)


@dataclass(frozen=True)
class RegisteredIndicatorSnapshot:
    artifact_id: str
    artifact_hash: str
    dataset_id: str
    dataset_version: str
    result_values: Mapping[str, Mapping[str, str]]
    result_hashes: Mapping[str, str]
    source_last_timestamp_utc: str
    as_of_utc: str
    operator_review_required: bool = True
    read_only: bool = True
    deterministic_engine_authority: bool = True
    scoring_authority: bool = False
    recommendation_authority: bool = False
    account_authority: bool = False
    execution_authority: bool = False
    schema_version: str = RUNTIME_SCHEMA_VERSION
    snapshot_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        dataset_id = identifier(self.dataset_id, "dataset_id")
        dataset_version = identifier(self.dataset_version, "dataset_version")
        as_of = utc(self.as_of_utc, "as_of_utc")
        last_timestamp = utc(
            self.source_last_timestamp_utc, "source_last_timestamp_utc"
        )
        values = {
            request_id: MappingProxyType(dict(sorted(result.items())))
            for request_id, result in sorted(self.result_values.items())
        }
        hashes = dict(sorted(self.result_hashes.items()))
        if set(values) != set(hashes) or not values:
            raise ValueError("result values and hashes must cover the same requests")
        if (
            self.operator_review_required is not True
            or self.read_only is not True
            or self.deterministic_engine_authority is not True
            or any(
                (
                    self.scoring_authority,
                    self.recommendation_authority,
                    self.account_authority,
                    self.execution_authority,
                )
            )
        ):
            raise ValueError("indicator snapshot exceeds deterministic authority")
        if self.schema_version != RUNTIME_SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "dataset_id", dataset_id)
        object.__setattr__(self, "dataset_version", dataset_version)
        object.__setattr__(self, "result_values", MappingProxyType(values))
        object.__setattr__(self, "result_hashes", MappingProxyType(hashes))
        object.__setattr__(self, "source_last_timestamp_utc", last_timestamp)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "snapshot_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "as_of_utc": as_of,
                    "dataset_id": dataset_id,
                    "dataset_version": dataset_version,
                    "result_hashes": hashes,
                    "result_values": {
                        key: dict(value) for key, value in values.items()
                    },
                    "schema_version": self.schema_version,
                    "source_last_timestamp_utc": last_timestamp,
                }
            ),
        )
