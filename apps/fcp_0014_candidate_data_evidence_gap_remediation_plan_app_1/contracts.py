from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1.contracts import (
    require_identifier,
)
from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    canonical_json_sha256,
)


PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
BLOCKER_KINDS = frozenset({"COST", "COVERAGE", "GOVERNANCE", "QUALITY"})


@dataclass(frozen=True)
class EvidenceGapRemediationRequirement:
    requirement_id: str
    category: str
    priority: str
    blocker_kind: str
    acceptance_criteria: tuple[str, ...]
    dependency_ids: tuple[str, ...] = ()
    required_fields: tuple[str, ...] = ()
    evidence_state: str = "MISSING"
    action_state: str = "OPERATOR_INPUT_REQUIRED"
    completion_state: str = "OPEN"

    def __post_init__(self) -> None:
        object.__setattr__(self, "requirement_id", require_identifier(self.requirement_id, "requirement_id"))
        object.__setattr__(self, "category", require_identifier(self.category, "category"))
        if self.priority not in PRIORITY_ORDER:
            raise ValueError("priority must be P0, P1, or P2")
        if self.blocker_kind not in BLOCKER_KINDS:
            raise ValueError("blocker_kind is not registered")
        for field_name in ("acceptance_criteria", "dependency_ids", "required_fields"):
            values = tuple(getattr(self, field_name))
            if values != tuple(sorted(set(values))):
                raise ValueError(f"{field_name} must be sorted and unique")
            for value in values:
                require_identifier(value, field_name)
        if not self.acceptance_criteria:
            raise ValueError("acceptance criteria are required")
        if (
            self.evidence_state != "MISSING"
            or self.action_state != "OPERATOR_INPUT_REQUIRED"
            or self.completion_state != "OPEN"
        ):
            raise ValueError("remediation requirement cannot close itself")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "acceptance_criteria": self.acceptance_criteria,
                "action_state": self.action_state,
                "blocker_kind": self.blocker_kind,
                "category": self.category,
                "completion_state": self.completion_state,
                "dependency_ids": self.dependency_ids,
                "evidence_state": self.evidence_state,
                "priority": self.priority,
                "required_fields": self.required_fields,
                "requirement_id": self.requirement_id,
            }
        )


@dataclass(frozen=True)
class CandidateEvidenceGapRemediationPlan:
    candidate_id: str
    source_packet_sha256: str
    requirements: tuple[EvidenceGapRemediationRequirement, ...]
    plan_state: str = "EVIDENCE_GAPS_OPEN"
    external_activation_state: str = "BLOCKED"
    provider_selection_state: str = "UNSELECTED"
    network_state: str = "DISABLED"
    operator_review_required: bool = True
    plan_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", require_identifier(self.candidate_id, "candidate_id"))
        if len(self.source_packet_sha256) != 64 or any(
            char not in "0123456789abcdef" for char in self.source_packet_sha256
        ):
            raise ValueError("source_packet_sha256 must be a SHA-256 digest")
        expected = tuple(
            sorted(
                self.requirements,
                key=lambda item: (PRIORITY_ORDER[item.priority], item.requirement_id),
            )
        )
        if not expected or expected != self.requirements:
            raise ValueError("requirements must be non-empty and deterministically sorted")
        ids = {item.requirement_id for item in self.requirements}
        if len(ids) != len(self.requirements):
            raise ValueError("requirement identities must be unique")
        if any(dependency not in ids for item in self.requirements for dependency in item.dependency_ids):
            raise ValueError("requirement dependency is not registered in the plan")
        if (
            self.plan_state != "EVIDENCE_GAPS_OPEN"
            or self.external_activation_state != "BLOCKED"
            or self.provider_selection_state != "UNSELECTED"
            or self.network_state != "DISABLED"
            or self.operator_review_required is not True
        ):
            raise ValueError("remediation plan cannot authorize external state")
        object.__setattr__(self, "plan_sha256", canonical_json_sha256(self.as_payload(include_hash=False)))

    def as_payload(self, *, include_hash: bool = True) -> Mapping[str, object]:
        counts = {
            priority: sum(item.priority == priority for item in self.requirements)
            for priority in PRIORITY_ORDER
        }
        payload: dict[str, object] = {
            "candidate_id": self.candidate_id,
            "external_activation_state": self.external_activation_state,
            "network_state": self.network_state,
            "open_count": len(self.requirements),
            "operator_review_required": self.operator_review_required,
            "plan_state": self.plan_state,
            "priority_counts": counts,
            "provider_selection_state": self.provider_selection_state,
            "requirements": tuple(dict(item.as_payload()) for item in self.requirements),
            "source_packet_sha256": self.source_packet_sha256,
        }
        if include_hash:
            payload["plan_sha256"] = self.plan_sha256
        return MappingProxyType(payload)
