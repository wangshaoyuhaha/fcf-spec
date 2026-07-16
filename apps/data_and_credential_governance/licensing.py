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
    normalize_identifiers,
    require_identifier,
)


class LicenseType(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    PROHIBITED = "PROHIBITED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class LicensePolicy:
    source_id: str
    source_evidence_id: str
    identity: PolicyIdentity
    license_type: LicenseType
    allowed_uses: tuple[str, ...]
    cloud_processing_allowed: bool = False
    redistribution_allowed: bool = False
    training_allowed: bool = False
    retention_days: int | None = None
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", require_identifier(self.source_id, "source_id"))
        object.__setattr__(self, "source_evidence_id", require_identifier(self.source_evidence_id, "source_evidence_id"))
        if not isinstance(self.identity, PolicyIdentity):
            raise TypeError("identity must be a PolicyIdentity")
        try:
            object.__setattr__(self, "license_type", LicenseType(self.license_type))
        except (TypeError, ValueError) as exc:
            raise ValueError("license_type is invalid") from exc
        uses = tuple(item.upper() for item in normalize_identifiers(tuple(self.allowed_uses), "allowed_use"))
        object.__setattr__(self, "allowed_uses", tuple(sorted(set(uses))))
        if self.retention_days is not None and (
            not isinstance(self.retention_days, int) or self.retention_days < 1
        ):
            raise ValueError("retention_days must be a positive integer or none")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.license_type in {LicenseType.PROHIBITED, LicenseType.UNKNOWN} and any(
            (self.cloud_processing_allowed, self.redistribution_allowed, self.training_allowed)
        ):
            raise ValueError("prohibited or unknown license cannot grant external usage")
        if self.license_type is LicenseType.PROHIBITED and self.allowed_uses:
            raise ValueError("prohibited license cannot allow a use")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType({
            "allowed_uses": self.allowed_uses,
            "cloud_processing_allowed": self.cloud_processing_allowed,
            "identity": self.identity.as_payload(),
            "license_type": self.license_type.value,
            "operator_review_required": self.operator_review_required,
            "redistribution_allowed": self.redistribution_allowed,
            "retention_days": self.retention_days,
            "source_evidence_id": self.source_evidence_id,
            "source_id": self.source_id,
            "training_allowed": self.training_allowed,
        })


class LicensePolicyRegistry:
    def __init__(self, policies: Iterable[LicensePolicy]) -> None:
        supplied = tuple(policies)
        if not supplied:
            raise ValueError("license policy registry must not be empty")
        if not all(isinstance(item, LicensePolicy) for item in supplied):
            raise TypeError("license registry entries must be LicensePolicy values")
        records = tuple(sorted(supplied, key=lambda item: item.source_id))
        source_ids = tuple(item.source_id for item in records)
        policy_ids = tuple(item.identity.policy_id for item in records)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate license policy source_id")
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("duplicate license policy policy_id")
        self._policies = records
        self._by_source_id: Mapping[str, LicensePolicy] = MappingProxyType(
            {item.source_id: item for item in records}
        )

    @property
    def policies(self) -> tuple[LicensePolicy, ...]:
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

    def get(self, source_id: str) -> LicensePolicy | None:
        return self._by_source_id.get(source_id)

    def require(self, source_id: str) -> LicensePolicy:
        policy = self.get(source_id)
        if policy is None:
            raise KeyError(f"missing license policy for source_id: {source_id}")
        return policy


_MISSING_LICENSE_POLICY = PolicyIdentity(
    "missing-license-policy", "v1", "missing-license-policy-evidence"
)


def evaluate_source_license(request: GovernanceRequest, registry: LicensePolicyRegistry) -> GovernanceDecision:
    if not isinstance(request, GovernanceRequest):
        raise TypeError("request must be a GovernanceRequest")
    if not isinstance(registry, LicensePolicyRegistry):
        raise TypeError("registry must be a LicensePolicyRegistry")
    policy = registry.get(request.source_id)
    if policy is None:
        return GovernanceDecision(
            GovernanceDomain.SOURCE_LICENSE,
            request.source_id,
            _MISSING_LICENSE_POLICY,
            GovernanceDecisionStatus.BLOCKED,
            blocking_reasons=("license-policy-missing",),
        )

    blocked: list[str] = []
    degraded: list[str] = []
    if policy.license_type is LicenseType.PROHIBITED:
        blocked.append("license-prohibited")
    if request.intended_use not in policy.allowed_uses:
        blocked.append("intended-use-not-licensed")
    if request.intended_use == "CLOUD_PROCESSING" and not policy.cloud_processing_allowed:
        blocked.append("cloud-processing-not-licensed")
    if request.intended_use == "REDISTRIBUTION" and not policy.redistribution_allowed:
        blocked.append("redistribution-not-licensed")
    if request.intended_use == "MODEL_TRAINING" and not policy.training_allowed:
        blocked.append("training-not-licensed")
    if policy.license_type is LicenseType.UNKNOWN:
        degraded.append("license-unknown")
    if policy.license_type is LicenseType.RESTRICTED:
        degraded.append("license-restricted")
    if policy.retention_days is None:
        degraded.append("retention-policy-restricted")
    if blocked:
        status = GovernanceDecisionStatus.BLOCKED
        degraded = []
    elif degraded:
        status = GovernanceDecisionStatus.DEGRADED
    else:
        status = GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
    return GovernanceDecision(
        GovernanceDomain.SOURCE_LICENSE,
        request.source_id,
        policy.identity,
        status,
        blocking_reasons=tuple(blocked),
        degradation_reasons=tuple(degraded),
        evidence_ids=(policy.source_evidence_id, policy.identity.evidence_id),
    )
