from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1.contracts import (
    require_identifier,
)


def canonical_json_sha256(value: object) -> str:
    if isinstance(value, Mapping):
        value = dict(value)
    raw = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def require_sha256(value: object, field_name: str) -> str:
    normalized = str(value).strip().lower()
    if len(normalized) != 64 or any(char not in "0123456789abcdef" for char in normalized):
        raise ValueError(f"{field_name} must be a SHA-256 digest")
    return normalized


def require_date(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    try:
        datetime.strptime(normalized, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc
    return normalized


@dataclass(frozen=True)
class RegisteredEvidenceReference:
    evidence_id: str
    candidate_id: str
    evidence_kind: str
    registry_path: str
    canonical_json_sha256: str
    observed_capabilities: tuple[str, ...]
    observed_from: str
    observed_to: str
    finding_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", require_identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "evidence_kind", require_identifier(self.evidence_kind, "evidence_kind"))
        if not self.registry_path.startswith("FCF_REGISTERED_EVIDENCE_") or not self.registry_path.endswith(".json"):
            raise ValueError("registry_path must reference registered evidence")
        object.__setattr__(self, "canonical_json_sha256", require_sha256(self.canonical_json_sha256, "canonical_json_sha256"))
        capabilities = tuple(sorted(set(self.observed_capabilities)))
        findings = tuple(sorted(set(self.finding_codes)))
        if not capabilities or capabilities != self.observed_capabilities:
            raise ValueError("observed_capabilities must be sorted and unique")
        if findings != self.finding_codes:
            raise ValueError("finding_codes must be sorted and unique")
        for value in capabilities + findings:
            require_identifier(value, "evidence code")
        start = require_date(self.observed_from, "observed_from")
        end = require_date(self.observed_to, "observed_to")
        if start > end:
            raise ValueError("evidence observation range is reversed")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "candidate_id": self.candidate_id,
                "canonical_json_sha256": self.canonical_json_sha256,
                "evidence_id": self.evidence_id,
                "evidence_kind": self.evidence_kind,
                "finding_codes": self.finding_codes,
                "observed_capabilities": self.observed_capabilities,
                "observed_from": self.observed_from,
                "observed_to": self.observed_to,
                "registry_path": self.registry_path,
            }
        )


@dataclass(frozen=True)
class CandidateEvidenceBundle:
    bundle_id: str
    evidence_id: str
    candidate_id: str
    references: tuple[RegisteredEvidenceReference, ...]
    missing_evidence_categories: tuple[str, ...]
    missing_fields_by_kind: Mapping[str, tuple[str, ...]]
    license_class: str
    remaining_days: int
    rights_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    provider_selection_state: str = "UNSELECTED"
    network_state: str = "DISABLED"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "bundle_id", require_identifier(self.bundle_id, "bundle_id"))
        object.__setattr__(self, "evidence_id", require_identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        if len(self.references) != 2 or tuple(sorted(self.references, key=lambda item: item.evidence_id)) != self.references:
            raise ValueError("bundle must contain two sorted registered references")
        if len({item.evidence_id for item in self.references}) != 2:
            raise ValueError("bundle evidence references must be unique")
        if any(item.candidate_id != self.candidate_id for item in self.references):
            raise ValueError("bundle candidate identities must match")
        categories = tuple(sorted(set(self.missing_evidence_categories)))
        if not categories:
            raise ValueError("bundle must preserve unresolved evidence categories")
        object.__setattr__(self, "missing_evidence_categories", categories)
        missing = {
            str(kind): tuple(sorted(set(values)))
            for kind, values in dict(self.missing_fields_by_kind).items()
        }
        if not missing:
            raise ValueError("bundle must preserve canonical field gaps")
        object.__setattr__(self, "missing_fields_by_kind", MappingProxyType(dict(sorted(missing.items()))))
        if self.license_class != "TRIAL" or not isinstance(self.remaining_days, int) or self.remaining_days < 0:
            raise ValueError("bundle trial observation is invalid")
        fixed = (
            self.rights_state == "UNRESOLVED",
            self.retention_state == "UNRESOLVED",
            self.provider_selection_state == "UNSELECTED",
            self.network_state == "DISABLED",
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("bundle authority boundary cannot be weakened")


@dataclass(frozen=True)
class CandidateEvidenceReconciliationPacket:
    candidate_id: str
    bundle_evidence_id: str
    source_evidence_ids: tuple[str, ...]
    observed_capabilities: tuple[str, ...]
    capability_overlap: tuple[str, ...]
    conflict_codes: tuple[str, ...]
    context_codes: tuple[str, ...]
    missing_evidence_categories: tuple[str, ...]
    missing_fields_by_kind: Mapping[str, tuple[str, ...]]
    readiness_delta: str = "EVIDENCE_EXPANDED_NOT_READY"
    external_activation_state: str = "BLOCKED"
    provider_selection_state: str = "UNSELECTED"
    entitlement_state: str = "UNRESOLVED"
    network_state: str = "DISABLED"
    operator_review_required: bool = True
    packet_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "bundle_evidence_id", require_identifier(self.bundle_evidence_id, "bundle_evidence_id"))
        for field_name in (
            "source_evidence_ids",
            "observed_capabilities",
            "capability_overlap",
            "conflict_codes",
            "context_codes",
            "missing_evidence_categories",
        ):
            values = tuple(getattr(self, field_name))
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{field_name} must be sorted and unique")
        if len(self.source_evidence_ids) != 2 or not self.observed_capabilities:
            raise ValueError("reconciliation requires both source evidence records")
        missing = {kind: tuple(values) for kind, values in dict(self.missing_fields_by_kind).items()}
        object.__setattr__(self, "missing_fields_by_kind", MappingProxyType(dict(sorted(missing.items()))))
        fixed = (
            self.readiness_delta == "EVIDENCE_EXPANDED_NOT_READY",
            self.external_activation_state == "BLOCKED",
            self.provider_selection_state == "UNSELECTED",
            self.entitlement_state == "UNRESOLVED",
            self.network_state == "DISABLED",
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("reconciliation cannot authorize product state")
        object.__setattr__(self, "packet_sha256", canonical_json_sha256(self.as_payload(include_hash=False)))

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        payload: dict[str, object] = {
            "bundle_evidence_id": self.bundle_evidence_id,
            "candidate_id": self.candidate_id,
            "capability_overlap": self.capability_overlap,
            "conflict_codes": self.conflict_codes,
            "context_codes": self.context_codes,
            "entitlement_state": self.entitlement_state,
            "external_activation_state": self.external_activation_state,
            "missing_evidence_categories": self.missing_evidence_categories,
            "missing_fields_by_kind": dict(self.missing_fields_by_kind),
            "network_state": self.network_state,
            "observed_capabilities": self.observed_capabilities,
            "operator_review_required": self.operator_review_required,
            "provider_selection_state": self.provider_selection_state,
            "readiness_delta": self.readiness_delta,
            "source_evidence_ids": self.source_evidence_ids,
        }
        if include_hash:
            payload["packet_sha256"] = self.packet_sha256
        return MappingProxyType(payload)
