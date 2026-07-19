from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


def require_identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def normalize_identifiers(
    values: tuple[str, ...], field_name: str
) -> tuple[str, ...]:
    return tuple(
        sorted({require_identifier(value, field_name) for value in tuple(values)})
    )


def require_utc_timestamp(value: object, field_name: str) -> str:
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


def parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _optional_non_negative_int(value: int | None, field_name: str) -> int | None:
    if value is not None and (not isinstance(value, int) or value < 0):
        raise ValueError(f"{field_name} must be a non-negative integer or none")
    return value


class EntitlementEvidenceState(str, Enum):
    REGISTERED = "REGISTERED"
    MISSING = "MISSING"
    NOT_RESEARCHED = "NOT_RESEARCHED"


class ExpiryKind(str, Enum):
    DATE_BOUND = "DATE_BOUND"
    PERPETUAL = "PERPETUAL"
    NOT_RESEARCHED = "NOT_RESEARCHED"


class RevocationState(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    NOT_RESEARCHED = "NOT_RESEARCHED"


class ReadinessStatus(str, Enum):
    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


class FindingSeverity(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    DEGRADED = "DEGRADED"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class EntitlementReviewRequest:
    request_id: str
    correlation_id: str
    source_id: str
    evaluated_at_utc: str
    intended_use_id: str
    required_field_ids: tuple[str, ...]
    peer_host: str = "127.0.0.1"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "request_id",
            "correlation_id",
            "source_id",
            "intended_use_id",
        ):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "evaluated_at_utc",
            require_utc_timestamp(self.evaluated_at_utc, "evaluated_at_utc"),
        )
        fields = normalize_identifiers(self.required_field_ids, "required_field_id")
        if not fields:
            raise ValueError("required_field_ids must not be empty")
        object.__setattr__(self, "required_field_ids", fields)
        if self.peer_host != "127.0.0.1":
            raise ValueError("entitlement review peer must be exactly 127.0.0.1")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class SourceEntitlementRecord:
    record_id: str
    record_version: str
    source_id: str
    evidence_state: EntitlementEvidenceState
    market_scope_ids: tuple[str, ...] = ()
    field_ids: tuple[str, ...] = ()
    permitted_use_ids: tuple[str, ...] = ()
    rights_evidence_ids: tuple[str, ...] = ()
    lineage_evidence_ids: tuple[str, ...] = ()
    retention_evidence_ids: tuple[str, ...] = ()
    service_level_evidence_ids: tuple[str, ...] = ()
    cost_evidence_ids: tuple[str, ...] = ()
    expiry_evidence_ids: tuple[str, ...] = ()
    revocation_evidence_ids: tuple[str, ...] = ()
    retention_days: int | None = None
    freshness_objective_seconds: int | None = None
    latency_objective_ms: int | None = None
    monthly_cost_minor_units: int | None = None
    currency_code: str | None = None
    expiry_kind: ExpiryKind = ExpiryKind.NOT_RESEARCHED
    expires_at_utc: str | None = None
    revocation_state: RevocationState = RevocationState.NOT_RESEARCHED
    evidence_ids: tuple[str, ...] = ()
    operator_review_required: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in ("record_id", "record_version", "source_id"):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        for field_name, enum_type in (
            ("evidence_state", EntitlementEvidenceState),
            ("expiry_kind", ExpiryKind),
            ("revocation_state", RevocationState),
        ):
            try:
                object.__setattr__(self, field_name, enum_type(getattr(self, field_name)))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{field_name} is invalid") from exc
        for field_name in (
            "market_scope_ids",
            "field_ids",
            "permitted_use_ids",
            "rights_evidence_ids",
            "lineage_evidence_ids",
            "retention_evidence_ids",
            "service_level_evidence_ids",
            "cost_evidence_ids",
            "expiry_evidence_ids",
            "revocation_evidence_ids",
            "evidence_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                normalize_identifiers(getattr(self, field_name), field_name),
            )
        for field_name in (
            "retention_days",
            "freshness_objective_seconds",
            "latency_objective_ms",
            "monthly_cost_minor_units",
        ):
            object.__setattr__(
                self,
                field_name,
                _optional_non_negative_int(getattr(self, field_name), field_name),
            )
        if self.monthly_cost_minor_units is None:
            if self.currency_code is not None:
                raise ValueError("currency_code requires monthly_cost_minor_units")
        else:
            normalized_currency = str(self.currency_code or "").strip().upper()
            if _CURRENCY_PATTERN.fullmatch(normalized_currency) is None:
                raise ValueError("currency_code must be a three-letter code")
            object.__setattr__(self, "currency_code", normalized_currency)
        if self.expiry_kind is ExpiryKind.DATE_BOUND:
            if self.expires_at_utc is None:
                raise ValueError("date-bound rights require expires_at_utc")
            object.__setattr__(
                self,
                "expires_at_utc",
                require_utc_timestamp(self.expires_at_utc, "expires_at_utc"),
            )
        elif self.expires_at_utc is not None:
            raise ValueError("expires_at_utc is only valid for date-bound rights")
        if self.evidence_state is EntitlementEvidenceState.REGISTERED:
            if not self.evidence_ids:
                raise ValueError("registered entitlement requires evidence_ids")
        else:
            populated = (
                self.market_scope_ids,
                self.field_ids,
                self.permitted_use_ids,
                self.rights_evidence_ids,
                self.lineage_evidence_ids,
                self.retention_evidence_ids,
                self.service_level_evidence_ids,
                self.cost_evidence_ids,
                self.expiry_evidence_ids,
                self.revocation_evidence_ids,
                self.evidence_ids,
            )
            if any(populated):
                raise ValueError("unregistered entitlement cannot assert evidence")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.phase_authorization_allowed is not False:
            raise ValueError("phase_authorization_allowed must be false")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "currency_code": self.currency_code,
                "cost_evidence_ids": self.cost_evidence_ids,
                "evidence_ids": self.evidence_ids,
                "evidence_state": self.evidence_state.value,
                "expires_at_utc": self.expires_at_utc,
                "expiry_evidence_ids": self.expiry_evidence_ids,
                "expiry_kind": self.expiry_kind.value,
                "field_ids": self.field_ids,
                "freshness_objective_seconds": self.freshness_objective_seconds,
                "latency_objective_ms": self.latency_objective_ms,
                "lineage_evidence_ids": self.lineage_evidence_ids,
                "market_scope_ids": self.market_scope_ids,
                "monthly_cost_minor_units": self.monthly_cost_minor_units,
                "operator_review_required": self.operator_review_required,
                "permitted_use_ids": self.permitted_use_ids,
                "phase_authorization_allowed": self.phase_authorization_allowed,
                "record_id": self.record_id,
                "record_version": self.record_version,
                "retention_days": self.retention_days,
                "retention_evidence_ids": self.retention_evidence_ids,
                "revocation_state": self.revocation_state.value,
                "revocation_evidence_ids": self.revocation_evidence_ids,
                "rights_evidence_ids": self.rights_evidence_ids,
                "service_level_evidence_ids": self.service_level_evidence_ids,
                "source_id": self.source_id,
            }
        )


@dataclass(frozen=True)
class ReadinessFinding:
    code: str
    severity: FindingSeverity
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", require_identifier(self.code, "code"))
        try:
            object.__setattr__(self, "severity", FindingSeverity(self.severity))
        except (TypeError, ValueError) as exc:
            raise ValueError("severity is invalid") from exc
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers(self.evidence_ids, "evidence_id"),
        )

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "code": self.code,
                "evidence_ids": self.evidence_ids,
                "severity": self.severity.value,
            }
        )
