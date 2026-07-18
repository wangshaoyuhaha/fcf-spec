from __future__ import annotations

from apps.v2_r35_local_evidence_integrity_foundation_app_1 import EvidenceIntegritySnapshot
from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import FactorLifecycleSnapshot
from apps.v2_r37_local_factor_validation_evidence_foundation_app_1 import FactorValidationSnapshot

from .contracts import GovernanceProjectionField, OperatorFactorGovernanceProjection


_MISSING_EVIDENCE_STATES = {"FUTURE_ONLY", "MISSING"}
_INTEGRITY_BLOCK_STATES = {"NOT_EFFECTIVE", "STALE"}
_MISSING_LIFECYCLE_STATES = {"FUTURE_ONLY", "MISSING"}
_TERMINAL_LIFECYCLE_STATES = {
    "DEFERRED",
    "EXPIRED",
    "REJECTED",
    "RETIRED",
    "REVOKED",
    "SUPERSEDED",
}


def build_governance_projection(
    *,
    projection_id: str,
    evidence: EvidenceIntegritySnapshot,
    lifecycle: FactorLifecycleSnapshot,
    validation: FactorValidationSnapshot,
) -> OperatorFactorGovernanceProjection:
    if not isinstance(evidence, EvidenceIntegritySnapshot):
        raise ValueError("projection requires an R35 evidence snapshot")
    if not isinstance(lifecycle, FactorLifecycleSnapshot):
        raise ValueError("projection requires an R36 lifecycle snapshot")
    if not isinstance(validation, FactorValidationSnapshot):
        raise ValueError("projection requires an R37 validation snapshot")
    if lifecycle.candidate_id != validation.candidate_id:
        raise ValueError("projection candidate identities do not match")
    evaluated = {
        evidence.evaluated_at_utc,
        lifecycle.evaluated_at_utc,
        validation.evaluated_at_utc,
    }
    if len(evaluated) != 1:
        raise ValueError("projection snapshots must share one as-of instant")
    candidate = lifecycle.candidate
    factor_id = "unavailable-factor" if candidate is None else candidate.factor_definition.factor_id
    source_hashes = (
        evidence.snapshot_hash,
        lifecycle.snapshot_hash,
        validation.snapshot_hash,
    )
    if evidence.state in _MISSING_EVIDENCE_STATES or lifecycle.state in _MISSING_LIFECYCLE_STATES:
        state = "BLOCKED_MISSING"
        confidence = "UNAVAILABLE"
        reasons = ("REGISTERED_PROJECTION_INPUT_MISSING",)
    elif evidence.state in _INTEGRITY_BLOCK_STATES:
        state = "BLOCKED_INTEGRITY"
        confidence = "LOW"
        reasons = ("EVIDENCE_INTEGRITY_NOT_CURRENT",)
    elif lifecycle.state in _TERMINAL_LIFECYCLE_STATES:
        state = "BLOCKED_LIFECYCLE"
        confidence = "LOW"
        reasons = ("TERMINAL_LIFECYCLE_STATE_PRESERVED",)
    elif validation.state == "FAILED":
        state = "BLOCKED_VALIDATION"
        confidence = "LOW"
        reasons = ("REGISTERED_VALIDATION_FAILURE_PRESERVED",)
    elif validation.state == "PASSED_REVIEW_REQUIRED":
        state = "REVIEW_REQUIRED"
        confidence = "HIGH"
        reasons = ("OPERATOR_REVIEW_REQUIRED", "NO_FACTOR_ACTIVATION")
    else:
        state = "INCOMPLETE"
        confidence = "MEDIUM"
        reasons = ("REGISTERED_GOVERNANCE_EVIDENCE_INCOMPLETE",)
    evidence_origin = "UNAVAILABLE" if evidence.record is None else evidence.record.origin
    fields = (
        GovernanceProjectionField(
            "evidence-origin",
            evidence_origin,
            "OBSERVED",
            confidence,
            (evidence.snapshot_hash,),
        ),
        GovernanceProjectionField(
            "evidence-state",
            evidence.state,
            "INFERRED",
            confidence,
            (evidence.snapshot_hash,),
        ),
        GovernanceProjectionField(
            "lifecycle-state",
            lifecycle.state,
            "INFERRED",
            confidence,
            (lifecycle.snapshot_hash,),
        ),
        GovernanceProjectionField(
            "validation-state",
            validation.state,
            "INFERRED",
            confidence,
            (validation.snapshot_hash,),
        ),
        GovernanceProjectionField(
            "projection-state",
            state,
            "INFERRED",
            confidence,
            source_hashes,
        ),
    )
    return OperatorFactorGovernanceProjection(
        projection_id=projection_id,
        candidate_id=lifecycle.candidate_id,
        factor_id=factor_id,
        evidence_series_id=evidence.evidence_series_id,
        market=evidence.market,
        evaluated_at_utc=evidence.evaluated_at_utc,
        state=state,
        confidence=confidence,
        fields=fields,
        reason_codes=reasons,
    )
