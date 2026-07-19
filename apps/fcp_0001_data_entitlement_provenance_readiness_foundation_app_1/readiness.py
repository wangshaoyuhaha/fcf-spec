from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .contracts import (
    ExpiryKind,
    FindingSeverity,
    ReadinessFinding,
    RevocationState,
    parse_utc_timestamp,
)
from .registry import EntitlementCoverageAssessment


EXPIRY_WARNING_DAYS = 30


@dataclass(frozen=True)
class OperationalReadinessAssessment:
    coverage: EntitlementCoverageAssessment
    findings: tuple[ReadinessFinding, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.coverage, EntitlementCoverageAssessment):
            raise TypeError("coverage must be an EntitlementCoverageAssessment")
        normalized = tuple(sorted(tuple(self.findings), key=lambda item: item.code))
        if not all(isinstance(item, ReadinessFinding) for item in normalized):
            raise TypeError("findings must contain ReadinessFinding values")
        if len({item.code for item in normalized}) != len(normalized):
            raise ValueError("operational assessment contains duplicate findings")
        object.__setattr__(self, "findings", normalized)


def _finding(
    code: str,
    severity: FindingSeverity,
    evidence_ids: tuple[str, ...] = (),
) -> ReadinessFinding:
    return ReadinessFinding(code, severity, evidence_ids)


def evaluate_operational_readiness(
    coverage: EntitlementCoverageAssessment,
) -> OperationalReadinessAssessment:
    if not isinstance(coverage, EntitlementCoverageAssessment):
        raise TypeError("coverage must be an EntitlementCoverageAssessment")
    record = coverage.record
    findings: list[ReadinessFinding] = []

    if record.retention_days is not None and not record.retention_evidence_ids:
        findings.append(
            _finding("retention-evidence-missing", FindingSeverity.BLOCKING)
        )
    if record.freshness_objective_seconds is None:
        findings.append(
            _finding("freshness-objective-not-researched", FindingSeverity.BLOCKING)
        )
    if record.latency_objective_ms is None:
        findings.append(
            _finding("latency-objective-not-researched", FindingSeverity.BLOCKING)
        )
    if (
        record.freshness_objective_seconds is not None
        or record.latency_objective_ms is not None
    ) and not record.service_level_evidence_ids:
        findings.append(
            _finding("service-level-evidence-missing", FindingSeverity.BLOCKING)
        )
    if record.monthly_cost_minor_units is None:
        findings.append(_finding("cost-not-researched", FindingSeverity.BLOCKING))
    elif not record.cost_evidence_ids:
        findings.append(_finding("cost-evidence-missing", FindingSeverity.BLOCKING))

    if record.expiry_kind is ExpiryKind.NOT_RESEARCHED:
        findings.append(_finding("expiry-not-researched", FindingSeverity.BLOCKING))
    elif not record.expiry_evidence_ids:
        findings.append(_finding("expiry-evidence-missing", FindingSeverity.BLOCKING))
    if record.expiry_kind is ExpiryKind.DATE_BOUND:
        expires_at = parse_utc_timestamp(record.expires_at_utc or "")
        evaluated_at = parse_utc_timestamp(coverage.request.evaluated_at_utc)
        if expires_at <= evaluated_at:
            findings.append(_finding("entitlement-expired", FindingSeverity.BLOCKING))
        elif expires_at <= evaluated_at + timedelta(days=EXPIRY_WARNING_DAYS):
            findings.append(
                _finding(
                    "entitlement-expiry-approaching",
                    FindingSeverity.DEGRADED,
                    record.expiry_evidence_ids,
                )
            )

    if record.revocation_state is RevocationState.NOT_RESEARCHED:
        findings.append(
            _finding("revocation-not-researched", FindingSeverity.BLOCKING)
        )
    elif record.revocation_state is RevocationState.REVOKED:
        findings.append(_finding("entitlement-revoked", FindingSeverity.BLOCKING))
    if (
        record.revocation_state is not RevocationState.NOT_RESEARCHED
        and not record.revocation_evidence_ids
    ):
        findings.append(
            _finding("revocation-evidence-missing", FindingSeverity.BLOCKING)
        )

    if not findings:
        findings.append(
            _finding(
                "operational-evidence-complete",
                FindingSeverity.INFORMATIONAL,
                record.evidence_ids,
            )
        )
    return OperationalReadinessAssessment(coverage, tuple(findings))
