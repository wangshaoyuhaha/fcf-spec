from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,159}$")


def identifier(value: object, name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return normalized


def utc(value: object, name: str) -> str:
    normalized = str(value).strip()
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    if parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return parsed.isoformat().replace("+00:00", "Z")


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def decimal_value(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class DataRightsDeclaration:
    license_id: str
    permitted_use: str
    retention_days: int
    operator_confirmed: bool = True
    local_artifact_only: bool = True
    redistribution_allowed: bool = False
    network_retrieval_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "license_id", identifier(self.license_id, "license_id"))
        object.__setattr__(
            self, "permitted_use", identifier(self.permitted_use, "permitted_use")
        )
        if self.permitted_use.upper() in {"NONE", "DENIED", "PROHIBITED"}:
            raise ValueError("permitted_use denies historical research")
        if isinstance(self.retention_days, bool) or self.retention_days <= 0:
            raise ValueError("retention_days must be positive")
        if self.operator_confirmed is not True or self.local_artifact_only is not True:
            raise ValueError("local data rights require Operator confirmation")
        if self.redistribution_allowed or self.network_retrieval_allowed:
            raise ValueError("V2-R2 data rights exceed local-only scope")


@dataclass(frozen=True)
class HistoricalObservation:
    observation_id: str
    instrument_id: str
    field_id: str
    event_at_utc: str
    available_at_utc: str
    value: Decimal
    quality_status: str
    source_id: str
    registered_artifact_id: str
    timezone_id: str
    calendar_id: str
    adjustment_policy: str
    missing_policy: str
    duplicate_policy: str
    suspension_policy: str
    rights: DataRightsDeclaration

    def __post_init__(self) -> None:
        for name in (
            "observation_id",
            "instrument_id",
            "field_id",
            "quality_status",
            "source_id",
            "registered_artifact_id",
            "timezone_id",
            "calendar_id",
            "adjustment_policy",
            "missing_policy",
            "duplicate_policy",
            "suspension_policy",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        event_at = utc(self.event_at_utc, "event_at_utc")
        available_at = utc(self.available_at_utc, "available_at_utc")
        if instant(available_at) < instant(event_at):
            raise ValueError("available_at_utc cannot precede event_at_utc")
        object.__setattr__(self, "event_at_utc", event_at)
        object.__setattr__(self, "available_at_utc", available_at)
        object.__setattr__(self, "value", decimal_value(self.value, "value"))
        if not isinstance(self.rights, DataRightsDeclaration):
            raise ValueError("rights must be DataRightsDeclaration")
        allowed_policies = {
            "adjustment_policy": {"none", "operator-declared", "point-in-time-adjusted"},
            "missing_policy": {"abstain", "preserve-missing"},
            "duplicate_policy": {"reject"},
            "suspension_policy": {"preserve-missing", "explicit-suspension"},
        }
        for name, allowed in allowed_policies.items():
            if getattr(self, name) not in allowed:
                raise ValueError(f"{name} is not allowed")
