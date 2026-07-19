from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    FindingSeverity,
    ReadinessFinding,
    SourceEntitlementRecord,
    require_identifier,
)


class SourceEntitlementRegistry:
    def __init__(self, records: Iterable[SourceEntitlementRecord]) -> None:
        supplied = tuple(records)
        if not supplied:
            raise ValueError("source entitlement registry must not be empty")
        if not all(isinstance(item, SourceEntitlementRecord) for item in supplied):
            raise TypeError("registry entries must be SourceEntitlementRecord values")
        normalized = tuple(sorted(supplied, key=lambda item: item.source_id))
        source_ids = tuple(item.source_id for item in normalized)
        record_ids = tuple(item.record_id for item in normalized)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate source entitlement source_id")
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("duplicate source entitlement record_id")
        self._records = normalized
        self._by_source_id: Mapping[str, SourceEntitlementRecord] = MappingProxyType(
            {item.source_id: item for item in normalized}
        )

    @property
    def records(self) -> tuple[SourceEntitlementRecord, ...]:
        return self._records

    @property
    def registry_sha256(self) -> str:
        payload = [dict(record.as_payload()) for record in self._records]
        canonical = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()

    def get(self, source_id: str) -> SourceEntitlementRecord | None:
        return self._by_source_id.get(require_identifier(source_id, "source_id"))


@dataclass(frozen=True)
class EntitlementCoverageAssessment:
    request: EntitlementReviewRequest
    record: SourceEntitlementRecord
    findings: tuple[ReadinessFinding, ...]
    registry_sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.request, EntitlementReviewRequest):
            raise TypeError("request must be an EntitlementReviewRequest")
        if not isinstance(self.record, SourceEntitlementRecord):
            raise TypeError("record must be a SourceEntitlementRecord")
        if self.request.source_id != self.record.source_id:
            raise ValueError("coverage assessment source linkage mismatch")
        normalized = tuple(sorted(tuple(self.findings), key=lambda item: item.code))
        if not all(isinstance(item, ReadinessFinding) for item in normalized):
            raise TypeError("findings must contain ReadinessFinding values")
        if len({item.code for item in normalized}) != len(normalized):
            raise ValueError("coverage assessment contains duplicate findings")
        object.__setattr__(self, "findings", normalized)
        digest = str(self.registry_sha256).strip().lower()
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("registry_sha256 must be a lowercase SHA-256 digest")
        object.__setattr__(self, "registry_sha256", digest)


def _finding(
    code: str,
    severity: FindingSeverity,
    evidence_ids: tuple[str, ...] = (),
) -> ReadinessFinding:
    return ReadinessFinding(code, severity, evidence_ids)


def evaluate_entitlement_coverage(
    request: EntitlementReviewRequest,
    registry: SourceEntitlementRegistry,
) -> EntitlementCoverageAssessment:
    if not isinstance(request, EntitlementReviewRequest):
        raise TypeError("request must be an EntitlementReviewRequest")
    if not isinstance(registry, SourceEntitlementRegistry):
        raise TypeError("registry must be a SourceEntitlementRegistry")
    record = registry.get(request.source_id)
    if record is None:
        record = SourceEntitlementRecord(
            record_id=f"missing-{request.source_id}",
            record_version="v1",
            source_id=request.source_id,
            evidence_state=EntitlementEvidenceState.MISSING,
        )
        findings = (
            _finding("entitlement-record-missing", FindingSeverity.BLOCKING),
        )
        return EntitlementCoverageAssessment(
            request,
            record,
            findings,
            registry.registry_sha256,
        )

    findings: list[ReadinessFinding] = []
    if record.evidence_state is EntitlementEvidenceState.NOT_RESEARCHED:
        findings.append(
            _finding("entitlement-not-researched", FindingSeverity.BLOCKING)
        )
    elif record.evidence_state is EntitlementEvidenceState.MISSING:
        findings.append(
            _finding("entitlement-evidence-missing", FindingSeverity.BLOCKING)
        )

    missing_fields = tuple(sorted(set(request.required_field_ids) - set(record.field_ids)))
    if missing_fields:
        findings.append(
            _finding("required-fields-missing", FindingSeverity.BLOCKING)
        )
    if request.intended_use_id not in record.permitted_use_ids:
        findings.append(
            _finding("intended-use-not-permitted", FindingSeverity.BLOCKING)
        )
    if not record.market_scope_ids:
        findings.append(
            _finding("market-scope-not-researched", FindingSeverity.BLOCKING)
        )
    if not record.rights_evidence_ids:
        findings.append(
            _finding("rights-evidence-missing", FindingSeverity.BLOCKING)
        )
    if not record.lineage_evidence_ids:
        findings.append(
            _finding("lineage-evidence-missing", FindingSeverity.BLOCKING)
        )
    if record.retention_days is None:
        findings.append(
            _finding("retention-not-researched", FindingSeverity.BLOCKING)
        )
    if not record.evidence_ids:
        findings.append(
            _finding("registered-evidence-missing", FindingSeverity.BLOCKING)
        )
    if not findings:
        findings.append(
            _finding(
                "entitlement-coverage-complete",
                FindingSeverity.INFORMATIONAL,
                record.evidence_ids,
            )
        )
    return EntitlementCoverageAssessment(
        request,
        record,
        tuple(findings),
        registry.registry_sha256,
    )
