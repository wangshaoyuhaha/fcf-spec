from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .contracts import (
    EntitlementReviewRequest,
    FindingSeverity,
    ReadinessFinding,
    ReadinessStatus,
    SourceEntitlementRecord,
)
from .readiness import evaluate_operational_readiness
from .registry import SourceEntitlementRegistry, evaluate_entitlement_coverage


@dataclass(frozen=True)
class EntitlementReadinessOutcome:
    request: EntitlementReviewRequest
    record: SourceEntitlementRecord
    findings: tuple[ReadinessFinding, ...]
    status: ReadinessStatus
    registry_sha256: str
    outcome_sha256: str
    proposal_id: str = "FCF-FCP-0001"
    proposal_status: str = "NEEDS_RESEARCH"
    operator_review_required: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.request, EntitlementReviewRequest):
            raise TypeError("request must be an EntitlementReviewRequest")
        if not isinstance(self.record, SourceEntitlementRecord):
            raise TypeError("record must be a SourceEntitlementRecord")
        if self.request.source_id != self.record.source_id:
            raise ValueError("readiness outcome source linkage mismatch")
        normalized = tuple(sorted(tuple(self.findings), key=lambda item: item.code))
        if not normalized or not all(
            isinstance(item, ReadinessFinding) for item in normalized
        ):
            raise ValueError("readiness outcome requires findings")
        if len({item.code for item in normalized}) != len(normalized):
            raise ValueError("readiness outcome contains duplicate findings")
        object.__setattr__(self, "findings", normalized)
        try:
            object.__setattr__(self, "status", ReadinessStatus(self.status))
        except (TypeError, ValueError) as exc:
            raise ValueError("status is invalid") from exc
        for field_name in ("registry_sha256", "outcome_sha256"):
            value = str(getattr(self, field_name)).strip().lower()
            if len(value) != 64 or any(
                character not in "0123456789abcdef" for character in value
            ):
                raise ValueError(f"{field_name} must be a lowercase SHA-256 digest")
            object.__setattr__(self, field_name, value)
        if self.proposal_id != "FCF-FCP-0001":
            raise ValueError("proposal_id must remain FCF-FCP-0001")
        if self.proposal_status != "NEEDS_RESEARCH":
            raise ValueError("proposal_status must remain NEEDS_RESEARCH")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.phase_authorization_allowed is not False:
            raise ValueError("phase_authorization_allowed must be false")


def _status_for(findings: tuple[ReadinessFinding, ...]) -> ReadinessStatus:
    severities = {item.severity for item in findings}
    if FindingSeverity.BLOCKING in severities:
        return ReadinessStatus.BLOCKED
    if FindingSeverity.DEGRADED in severities:
        return ReadinessStatus.DEGRADED
    return ReadinessStatus.READY_FOR_OPERATOR_REVIEW


def _outcome_digest(
    request: EntitlementReviewRequest,
    record: SourceEntitlementRecord,
    findings: tuple[ReadinessFinding, ...],
    status: ReadinessStatus,
    registry_sha256: str,
) -> str:
    payload = {
        "findings": [dict(item.as_payload()) for item in findings],
        "proposal_id": "FCF-FCP-0001",
        "proposal_status": "NEEDS_RESEARCH",
        "record": dict(record.as_payload()),
        "registry_sha256": registry_sha256,
        "request": {
            "correlation_id": request.correlation_id,
            "evaluated_at_utc": request.evaluated_at_utc,
            "intended_use_id": request.intended_use_id,
            "operator_review_required": request.operator_review_required,
            "peer_host": request.peer_host,
            "request_id": request.request_id,
            "required_field_ids": request.required_field_ids,
            "source_id": request.source_id,
        },
        "status": status.value,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def evaluate_source_readiness(
    request: EntitlementReviewRequest,
    registry: SourceEntitlementRegistry,
) -> EntitlementReadinessOutcome:
    coverage = evaluate_entitlement_coverage(request, registry)
    operational = evaluate_operational_readiness(coverage)
    findings_by_code = {
        item.code: item for item in coverage.findings + operational.findings
    }
    findings = tuple(sorted(findings_by_code.values(), key=lambda item: item.code))
    status = _status_for(findings)
    digest = _outcome_digest(
        request,
        coverage.record,
        findings,
        status,
        coverage.registry_sha256,
    )
    return EntitlementReadinessOutcome(
        request=request,
        record=coverage.record,
        findings=findings,
        status=status,
        registry_sha256=coverage.registry_sha256,
        outcome_sha256=digest,
    )
