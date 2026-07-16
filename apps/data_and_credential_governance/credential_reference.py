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


class CredentialReferenceStatus(str, Enum):
    DECLARED_AVAILABLE = "DECLARED_AVAILABLE"
    DECLARED_UNAVAILABLE = "DECLARED_UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CredentialReferenceMetadata:
    reference_id: str
    source_id: str
    provider_id: str
    purpose: str
    identity: PolicyIdentity
    status: CredentialReferenceStatus
    observed_at_utc: str
    expires_at_utc: str | None = None
    credential_material_present: bool = False
    retrieval_locator_present: bool = False
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in ("reference_id", "source_id", "provider_id", "purpose"):
            value = require_identifier(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, value)
        if not isinstance(self.identity, PolicyIdentity):
            raise TypeError("identity must be a PolicyIdentity")
        try:
            object.__setattr__(self, "status", CredentialReferenceStatus(self.status))
        except (TypeError, ValueError) as exc:
            raise ValueError("credential reference status is invalid") from exc
        object.__setattr__(self, "observed_at_utc", require_utc_timestamp(self.observed_at_utc, "observed_at_utc"))
        if self.expires_at_utc is not None:
            object.__setattr__(self, "expires_at_utc", require_utc_timestamp(self.expires_at_utc, "expires_at_utc"))
            if parse_utc_timestamp(self.expires_at_utc) <= parse_utc_timestamp(self.observed_at_utc):
                raise ValueError("expires_at_utc must be after observed_at_utc")
        if self.credential_material_present is not False:
            raise ValueError("credential material must never be present")
        if self.retrieval_locator_present is not False:
            raise ValueError("credential retrieval locator must never be present")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType({
            "credential_material_present": self.credential_material_present,
            "expires_at_utc": self.expires_at_utc,
            "identity": self.identity.as_payload(),
            "observed_at_utc": self.observed_at_utc,
            "operator_review_required": self.operator_review_required,
            "provider_id": self.provider_id,
            "purpose": self.purpose,
            "reference_id": self.reference_id,
            "retrieval_locator_present": self.retrieval_locator_present,
            "source_id": self.source_id,
            "status": self.status.value,
        })


class CredentialReferenceRegistry:
    def __init__(self, references: Iterable[CredentialReferenceMetadata]) -> None:
        supplied = tuple(references)
        if not supplied:
            raise ValueError("credential reference registry must not be empty")
        if not all(isinstance(item, CredentialReferenceMetadata) for item in supplied):
            raise TypeError("credential registry entries must be CredentialReferenceMetadata values")
        records = tuple(sorted(supplied, key=lambda item: (item.source_id, item.reference_id)))
        source_ids = tuple(item.source_id for item in records)
        reference_ids = tuple(item.reference_id for item in records)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate credential reference source_id")
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("duplicate credential reference reference_id")
        self._references = records
        self._by_source_id: Mapping[str, CredentialReferenceMetadata] = MappingProxyType(
            {item.source_id: item for item in records}
        )

    @property
    def references(self) -> tuple[CredentialReferenceMetadata, ...]:
        return self._references

    @property
    def registry_sha256(self) -> str:
        payload = []
        for item in self._references:
            record = dict(item.as_payload())
            record["identity"] = dict(item.identity.as_payload())
            payload.append(record)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()

    def get(self, source_id: str) -> CredentialReferenceMetadata | None:
        return self._by_source_id.get(source_id)


_MISSING_REFERENCE_POLICY = PolicyIdentity(
    "missing-credential-reference", "v1", "missing-credential-reference-evidence"
)


def evaluate_credential_reference(
    request: GovernanceRequest,
    registry: CredentialReferenceRegistry,
    *,
    credential_reference_required: bool,
) -> GovernanceDecision:
    if not isinstance(request, GovernanceRequest):
        raise TypeError("request must be a GovernanceRequest")
    if not isinstance(registry, CredentialReferenceRegistry):
        raise TypeError("registry must be a CredentialReferenceRegistry")
    reference = registry.get(request.source_id)
    if not credential_reference_required:
        policy = reference.identity if reference is not None else _MISSING_REFERENCE_POLICY
        evidence = (policy.evidence_id,)
        return GovernanceDecision(
            GovernanceDomain.CREDENTIAL_REFERENCE,
            request.source_id,
            policy,
            GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW,
            evidence_ids=evidence,
        )
    if reference is None:
        return GovernanceDecision(
            GovernanceDomain.CREDENTIAL_REFERENCE,
            request.source_id,
            _MISSING_REFERENCE_POLICY,
            GovernanceDecisionStatus.BLOCKED,
            blocking_reasons=("credential-reference-missing",),
        )
    blocked: list[str] = []
    if reference.status is CredentialReferenceStatus.DECLARED_UNAVAILABLE:
        blocked.append("credential-reference-unavailable")
    if reference.status is CredentialReferenceStatus.UNKNOWN:
        blocked.append("credential-reference-status-unknown")
    if reference.expires_at_utc is not None and parse_utc_timestamp(reference.expires_at_utc) <= parse_utc_timestamp(request.evaluated_at_utc):
        blocked.append("credential-reference-expired")
    status = GovernanceDecisionStatus.BLOCKED if blocked else GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
    return GovernanceDecision(
        GovernanceDomain.CREDENTIAL_REFERENCE,
        request.source_id,
        reference.identity,
        status,
        blocking_reasons=tuple(blocked),
        evidence_ids=(reference.identity.evidence_id, reference.reference_id),
    )
