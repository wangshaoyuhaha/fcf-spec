from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any

from apps.read_only_data_gateway_app_1 import NormalizedArtifactEnvelope


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def require_identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def require_utc(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be UTC")
    return normalized


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): freeze(item) for key, item in sorted(value.items())}
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("market adapter values must be JSON-compatible")


def thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [thaw(item) for item in value]
    return value


class MarketAdapterId(str, Enum):
    CHINA_A_SHARE = "CHINA-A-SHARE-MARKET-ADAPTER-APP-1"
    US_EQUITY = "US-EQUITY-MARKET-ADAPTER-APP-1"
    HONG_KONG_EQUITY = "HONG-KONG-EQUITY-MARKET-ADAPTER-APP-1"
    GOLD_COMMODITY = "GOLD-COMMODITY-MARKET-ADAPTER-APP-1"
    DIGITAL_ASSET = "DIGITAL-ASSET-MARKET-ADAPTER-APP-1"
    FUTURES = "FUTURES-MARKET-ADAPTER-APP-1"


class FindingStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"


class AdapterStatus(str, Enum):
    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class MarketRuleProfile:
    adapter_id: MarketAdapterId
    profile_id: str
    version: str
    effective_from_utc: str
    evidence_ids: tuple[str, ...]
    rules: Mapping[str, Any]
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "adapter_id", MarketAdapterId(self.adapter_id))
        for field_name in ("profile_id", "version"):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "effective_from_utc",
            require_utc(self.effective_from_utc, "effective_from_utc"),
        )
        evidence_ids = tuple(
            sorted({require_identifier(item, "evidence_id") for item in self.evidence_ids})
        )
        if not evidence_ids:
            raise ValueError("profile evidence_ids must not be empty")
        object.__setattr__(self, "evidence_ids", evidence_ids)
        if not isinstance(self.rules, Mapping) or not self.rules:
            raise ValueError("profile rules must not be empty")
        object.__setattr__(self, "rules", freeze(self.rules))
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.automatic_activation_allowed is not False:
            raise ValueError("automatic_activation_allowed must be false")


@dataclass(frozen=True)
class MarketAdapterRequest:
    request_id: str
    correlation_id: str
    adapter_id: MarketAdapterId
    as_of_utc: str
    profile: MarketRuleProfile
    artifact: NormalizedArtifactEnvelope
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in ("request_id", "correlation_id"):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        adapter_id = MarketAdapterId(self.adapter_id)
        object.__setattr__(self, "adapter_id", adapter_id)
        object.__setattr__(self, "as_of_utc", require_utc(self.as_of_utc, "as_of_utc"))
        if self.profile.adapter_id is not adapter_id:
            raise ValueError("request and profile adapter linkage mismatch")
        if not isinstance(self.artifact, NormalizedArtifactEnvelope):
            raise TypeError("artifact must be a NormalizedArtifactEnvelope")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class AdapterRecordFinding:
    record_index: int
    symbol: str
    status: FindingStatus
    reason_codes: tuple[str, ...]
    derived_values: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.record_index < 0:
            raise ValueError("record_index must be non-negative")
        object.__setattr__(self, "symbol", require_identifier(self.symbol, "symbol"))
        object.__setattr__(self, "status", FindingStatus(self.status))
        reasons = tuple(sorted({require_identifier(item, "reason_code") for item in self.reason_codes}))
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "derived_values", freeze(self.derived_values))
        if self.status is FindingStatus.PASS and reasons:
            raise ValueError("passing finding cannot contain reason codes")
        if self.status is not FindingStatus.PASS and not reasons:
            raise ValueError("non-passing finding requires a reason code")


@dataclass(frozen=True)
class MarketAdapterOutcome:
    request_id: str
    correlation_id: str
    adapter_id: MarketAdapterId
    profile_id: str
    profile_version: str
    evidence_id: str
    artifact_sha256: str
    normalized_records_sha256: str
    status: AdapterStatus
    findings: tuple[AdapterRecordFinding, ...]
    reason_codes: tuple[str, ...]
    original_records: tuple[Mapping[str, Any], ...]
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "adapter_id", MarketAdapterId(self.adapter_id))
        object.__setattr__(self, "status", AdapterStatus(self.status))
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        if not all(isinstance(item, MappingProxyType) for item in self.original_records):
            raise TypeError("original records must remain immutable")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.automatic_activation_allowed is not False:
            raise ValueError("automatic_activation_allowed must be false")


@dataclass(frozen=True)
class MarketAdapterReviewPacket:
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", freeze(self.payload))
