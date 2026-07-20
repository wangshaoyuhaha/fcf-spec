from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1.contracts import (
    normalize_identifiers,
    require_identifier,
)
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1.contracts import (
    OBSERVATION_KINDS,
    REQUIRED_FIELDS,
)


EVIDENCE_CATEGORIES = (
    "cost-quota",
    "freshness-latency",
    "lineage",
    "permitted-use",
    "retention",
    "rights",
    "schema",
    "timestamp-revision",
)


class AccessApplicationState(str, Enum):
    UNKNOWN = "UNKNOWN"
    NOT_APPLIED = "NOT_APPLIED"
    PENDING = "PENDING"
    APPROVED_DECLARATION_ONLY = "APPROVED_DECLARATION_ONLY"
    REJECTED = "REJECTED"


def _plain_name(value: object) -> str:
    normalized = str(value).strip()
    if not normalized or len(normalized) > 80:
        raise ValueError("display_name must contain 1 to 80 characters")
    if any(ord(char) < 32 or ord(char) == 127 for char in normalized):
        raise ValueError("display_name must not contain control characters")
    return normalized


def _canonical_digest(value: object) -> str:
    if isinstance(value, Mapping):
        value = dict(value)
    payload = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class CandidateSourceProfile:
    candidate_id: str
    display_name: str
    access_application_state: AccessApplicationState = AccessApplicationState.UNKNOWN
    declared_market_ids: tuple[str, ...] = ()
    declared_canonical_fields: Mapping[str, tuple[str, ...]] = field(
        default_factory=dict
    )
    evidence_by_category: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    source_evidence_ids: tuple[str, ...] = ()
    secret_material_present: bool = False
    provider_selection_state: str = "UNSELECTED"
    network_state: str = "DISABLED"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "candidate_id", require_identifier(self.candidate_id, "candidate_id")
        )
        object.__setattr__(self, "display_name", _plain_name(self.display_name))
        try:
            state = AccessApplicationState(self.access_application_state)
        except (TypeError, ValueError) as exc:
            raise ValueError("access_application_state is invalid") from exc
        object.__setattr__(self, "access_application_state", state)
        object.__setattr__(
            self,
            "declared_market_ids",
            normalize_identifiers(self.declared_market_ids, "declared_market_id"),
        )
        normalized_fields: dict[str, tuple[str, ...]] = {}
        for kind, fields in dict(self.declared_canonical_fields).items():
            normalized_kind = str(kind).strip().upper()
            if normalized_kind not in OBSERVATION_KINDS:
                raise ValueError("declared observation kind is not canonical")
            normalized_fields[normalized_kind] = normalize_identifiers(
                tuple(fields), "declared_canonical_field"
            )
        object.__setattr__(
            self,
            "declared_canonical_fields",
            MappingProxyType(dict(sorted(normalized_fields.items()))),
        )
        evidence: dict[str, tuple[str, ...]] = {}
        for category, evidence_ids in dict(self.evidence_by_category).items():
            normalized_category = require_identifier(category, "evidence_category")
            if normalized_category not in EVIDENCE_CATEGORIES:
                raise ValueError("evidence category is not registered")
            evidence[normalized_category] = normalize_identifiers(
                tuple(evidence_ids), "evidence_id"
            )
        object.__setattr__(
            self,
            "evidence_by_category",
            MappingProxyType(dict(sorted(evidence.items()))),
        )
        object.__setattr__(
            self,
            "source_evidence_ids",
            normalize_identifiers(self.source_evidence_ids, "source_evidence_id"),
        )
        if self.secret_material_present is not False:
            raise ValueError("secret material is forbidden")
        if self.provider_selection_state != "UNSELECTED":
            raise ValueError("FCP-0011 cannot select a provider")
        if self.network_state != "DISABLED":
            raise ValueError("FCP-0011 network must remain disabled")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class CandidateSourceReviewPacket:
    candidate_id: str
    documentary_status: str
    compatibility_status: str
    missing_evidence_categories: tuple[str, ...]
    missing_fields_by_kind: Mapping[str, tuple[str, ...]]
    access_application_state: str
    external_activation_state: str = "BLOCKED"
    provider_selection_state: str = "UNSELECTED"
    credential_state: str = "ABSENT"
    network_state: str = "DISABLED"
    entitlement_state: str = "UNRESOLVED"
    operator_review_required: bool = True
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "candidate_id", require_identifier(self.candidate_id, "candidate_id")
        )
        missing_categories = tuple(sorted(set(self.missing_evidence_categories)))
        if not set(missing_categories).issubset(EVIDENCE_CATEGORIES):
            raise ValueError("missing evidence category is not registered")
        object.__setattr__(self, "missing_evidence_categories", missing_categories)
        missing_fields = {
            kind: tuple(sorted(set(fields)))
            for kind, fields in dict(self.missing_fields_by_kind).items()
        }
        if not set(missing_fields).issubset(OBSERVATION_KINDS):
            raise ValueError("missing field kind is not canonical")
        object.__setattr__(
            self,
            "missing_fields_by_kind",
            MappingProxyType(dict(sorted(missing_fields.items()))),
        )
        if self.documentary_status not in {
            "COMPLETE_PENDING_OPERATOR_REVIEW",
            "INCOMPLETE",
        }:
            raise ValueError("documentary_status is invalid")
        if self.compatibility_status not in {"COMPLETE", "INCOMPLETE"}:
            raise ValueError("compatibility_status is invalid")
        fixed = (
            self.external_activation_state == "BLOCKED",
            self.provider_selection_state == "UNSELECTED",
            self.credential_state == "ABSENT",
            self.network_state == "DISABLED",
            self.entitlement_state == "UNRESOLVED",
            self.operator_review_required is True,
        )
        if not all(fixed):
            raise ValueError("candidate review boundary cannot be weakened")
        object.__setattr__(
            self,
            "packet_hash",
            _canonical_digest(self.as_payload(include_hash=False)),
        )

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        payload: dict[str, object] = {
            "access_application_state": self.access_application_state,
            "candidate_id": self.candidate_id,
            "compatibility_status": self.compatibility_status,
            "credential_state": self.credential_state,
            "documentary_status": self.documentary_status,
            "entitlement_state": self.entitlement_state,
            "external_activation_state": self.external_activation_state,
            "missing_evidence_categories": self.missing_evidence_categories,
            "missing_fields_by_kind": dict(self.missing_fields_by_kind),
            "network_state": self.network_state,
            "operator_review_required": self.operator_review_required,
            "provider_selection_state": self.provider_selection_state,
        }
        if include_hash:
            payload["packet_hash"] = self.packet_hash
        return MappingProxyType(payload)


def required_canonical_fields() -> Mapping[str, tuple[str, ...]]:
    return MappingProxyType(
        {kind: tuple(REQUIRED_FIELDS[kind]) for kind in OBSERVATION_KINDS}
    )
