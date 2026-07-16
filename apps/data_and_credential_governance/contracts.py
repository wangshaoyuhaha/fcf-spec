from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def require_identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


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


def normalize_identifiers(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    return tuple(sorted({require_identifier(value, field_name) for value in values}))


class GovernanceDomain(str, Enum):
    SOURCE_LICENSE = "SOURCE_LICENSE"
    DATA_FRESHNESS = "DATA_FRESHNESS"
    CREDENTIAL_REFERENCE = "CREDENTIAL_REFERENCE"


class GovernanceDecisionStatus(str, Enum):
    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class PolicyIdentity:
    policy_id: str
    policy_version: str
    evidence_id: str

    def __post_init__(self) -> None:
        for field_name in ("policy_id", "policy_version", "evidence_id"):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )

    def as_payload(self) -> Mapping[str, str]:
        return MappingProxyType(
            {
                "evidence_id": self.evidence_id,
                "policy_id": self.policy_id,
                "policy_version": self.policy_version,
            }
        )


@dataclass(frozen=True)
class GovernanceRequest:
    request_id: str
    correlation_id: str
    source_id: str
    evaluated_at_utc: str
    intended_use: str
    peer_host: str = "127.0.0.1"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in ("request_id", "correlation_id", "source_id"):
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
        object.__setattr__(
            self,
            "intended_use",
            require_identifier(self.intended_use, "intended_use").upper(),
        )
        if self.peer_host != "127.0.0.1":
            raise ValueError("governance request peer must be exactly 127.0.0.1")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class GovernanceDecision:
    domain: GovernanceDomain
    source_id: str
    policy: PolicyIdentity
    status: GovernanceDecisionStatus
    blocking_reasons: tuple[str, ...] = ()
    degradation_reasons: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        try:
            object.__setattr__(self, "domain", GovernanceDomain(self.domain))
            object.__setattr__(self, "status", GovernanceDecisionStatus(self.status))
        except (TypeError, ValueError) as exc:
            raise ValueError("governance decision enum value is invalid") from exc
        object.__setattr__(
            self, "source_id", require_identifier(self.source_id, "source_id")
        )
        if not isinstance(self.policy, PolicyIdentity):
            raise TypeError("policy must be a PolicyIdentity")
        for field_name in ("blocking_reasons", "degradation_reasons", "evidence_ids"):
            object.__setattr__(
                self,
                field_name,
                normalize_identifiers(getattr(self, field_name), field_name),
            )
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.automatic_activation_allowed is not False:
            raise ValueError("automatic_activation_allowed must be false")
        if self.status is GovernanceDecisionStatus.BLOCKED:
            if not self.blocking_reasons:
                raise ValueError("blocked governance decision requires a reason")
        elif self.blocking_reasons:
            raise ValueError("non-blocked governance decision cannot contain blocking reasons")
        if self.status is GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW:
            if self.degradation_reasons:
                raise ValueError("ready governance decision cannot contain degradation reasons")


@dataclass(frozen=True)
class GovernanceAuditRecord:
    request: GovernanceRequest
    decisions: tuple[GovernanceDecision, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.request, GovernanceRequest):
            raise TypeError("request must be a GovernanceRequest")
        decisions = tuple(self.decisions)
        if not decisions or not all(isinstance(item, GovernanceDecision) for item in decisions):
            raise ValueError("audit record requires governance decisions")
        domains = tuple(item.domain for item in decisions)
        if len(domains) != len(set(domains)):
            raise ValueError("audit record contains duplicate governance domains")
        if any(item.source_id != self.request.source_id for item in decisions):
            raise ValueError("audit record source linkage mismatch")
        object.__setattr__(self, "decisions", tuple(sorted(decisions, key=lambda item: item.domain.value)))

    @property
    def overall_status(self) -> GovernanceDecisionStatus:
        statuses = {item.status for item in self.decisions}
        if GovernanceDecisionStatus.BLOCKED in statuses:
            return GovernanceDecisionStatus.BLOCKED
        if GovernanceDecisionStatus.DEGRADED in statuses:
            return GovernanceDecisionStatus.DEGRADED
        return GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
