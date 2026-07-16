from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    GovernanceDecision,
    GovernanceDecisionStatus,
    GovernanceDomain,
    GovernanceRequest,
    PolicyIdentity,
    parse_utc_timestamp,
    require_identifier,
    require_utc_timestamp,
)


class FreshnessBand(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    FUTURE_DATED = "FUTURE_DATED"
    UNKNOWN = "UNKNOWN"


class StaleAction(str, Enum):
    DEGRADE = "DEGRADE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class FreshnessPolicy:
    source_id: str
    source_evidence_id: str
    identity: PolicyIdentity
    fresh_for_seconds: int
    aging_for_seconds: int
    stale_action: StaleAction = StaleAction.BLOCK
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", require_identifier(self.source_id, "source_id"))
        object.__setattr__(self, "source_evidence_id", require_identifier(self.source_evidence_id, "source_evidence_id"))
        if not isinstance(self.identity, PolicyIdentity):
            raise TypeError("identity must be a PolicyIdentity")
        for field_name in ("fresh_for_seconds", "aging_for_seconds"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")
        if self.aging_for_seconds < self.fresh_for_seconds:
            raise ValueError("aging_for_seconds must not be less than fresh_for_seconds")
        try:
            object.__setattr__(self, "stale_action", StaleAction(self.stale_action))
        except (TypeError, ValueError) as exc:
            raise ValueError("stale_action is invalid") from exc
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType({
            "aging_for_seconds": self.aging_for_seconds,
            "fresh_for_seconds": self.fresh_for_seconds,
            "identity": self.identity.as_payload(),
            "operator_review_required": self.operator_review_required,
            "source_evidence_id": self.source_evidence_id,
            "source_id": self.source_id,
            "stale_action": self.stale_action.value,
        })


class FreshnessPolicyRegistry:
    def __init__(self, policies: Iterable[FreshnessPolicy]) -> None:
        supplied = tuple(policies)
        if not supplied:
            raise ValueError("freshness policy registry must not be empty")
        if not all(isinstance(item, FreshnessPolicy) for item in supplied):
            raise TypeError("freshness registry entries must be FreshnessPolicy values")
        records = tuple(sorted(supplied, key=lambda item: item.source_id))
        source_ids = tuple(item.source_id for item in records)
        policy_ids = tuple(item.identity.policy_id for item in records)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate freshness policy source_id")
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("duplicate freshness policy policy_id")
        self._policies = records
        self._by_source_id: Mapping[str, FreshnessPolicy] = MappingProxyType(
            {item.source_id: item for item in records}
        )

    @property
    def policies(self) -> tuple[FreshnessPolicy, ...]:
        return self._policies

    @property
    def registry_sha256(self) -> str:
        payload = []
        for item in self._policies:
            record = dict(item.as_payload())
            record["identity"] = dict(item.identity.as_payload())
            payload.append(record)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()

    def get(self, source_id: str) -> FreshnessPolicy | None:
        return self._by_source_id.get(source_id)


_MISSING_FRESHNESS_POLICY = PolicyIdentity(
    "missing-freshness-policy", "v1", "missing-freshness-policy-evidence"
)


def evaluate_data_freshness(
    request: GovernanceRequest,
    published_at_utc: str,
    registry: FreshnessPolicyRegistry,
) -> tuple[FreshnessBand, GovernanceDecision]:
    if not isinstance(request, GovernanceRequest):
        raise TypeError("request must be a GovernanceRequest")
    if not isinstance(registry, FreshnessPolicyRegistry):
        raise TypeError("registry must be a FreshnessPolicyRegistry")
    policy = registry.get(request.source_id)
    if policy is None:
        return FreshnessBand.UNKNOWN, GovernanceDecision(
            GovernanceDomain.DATA_FRESHNESS,
            request.source_id,
            _MISSING_FRESHNESS_POLICY,
            GovernanceDecisionStatus.BLOCKED,
            blocking_reasons=("freshness-policy-missing",),
        )
    published = parse_utc_timestamp(require_utc_timestamp(published_at_utc, "published_at_utc"))
    evaluated = parse_utc_timestamp(request.evaluated_at_utc)
    age_seconds = int((evaluated - published).total_seconds())
    if age_seconds < 0:
        band = FreshnessBand.FUTURE_DATED
        status = GovernanceDecisionStatus.BLOCKED
        blocked = ("source-future-dated",)
        degraded: tuple[str, ...] = ()
    elif age_seconds <= policy.fresh_for_seconds:
        band = FreshnessBand.FRESH
        status = GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
        blocked = ()
        degraded = ()
    elif age_seconds <= policy.aging_for_seconds:
        band = FreshnessBand.AGING
        status = GovernanceDecisionStatus.DEGRADED
        blocked = ()
        degraded = ("source-aging",)
    elif policy.stale_action is StaleAction.BLOCK:
        band = FreshnessBand.STALE
        status = GovernanceDecisionStatus.BLOCKED
        blocked = ("source-stale",)
        degraded = ()
    else:
        band = FreshnessBand.STALE
        status = GovernanceDecisionStatus.DEGRADED
        blocked = ()
        degraded = ("source-stale",)
    return band, GovernanceDecision(
        GovernanceDomain.DATA_FRESHNESS,
        request.source_id,
        policy.identity,
        status,
        blocking_reasons=blocked,
        degradation_reasons=degraded,
        evidence_ids=(policy.source_evidence_id, policy.identity.evidence_id),
    )
