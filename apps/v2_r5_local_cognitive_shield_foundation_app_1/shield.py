from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r4_local_anomaly_radar_foundation_app_1 import AnomalyEvidence

from .contracts import (
    CognitiveTask,
    CognitiveTaskPolicy,
    RegisteredAdvisoryArtifact,
)


_SHIELD_STATES = {
    "SUPPORTED_REVIEW",
    "CONTRADICTION_REVIEW",
    "ABSTAIN_REVIEW_REQUIRED",
    "DEGRADED",
    "BLOCKED",
}


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class CognitiveShieldEvidence:
    task_id: str
    anomaly_evidence_hash: str
    anomaly_state: str
    shield_state: str
    advisory_stance: str
    advisory_confidence: Decimal | None
    uncertainty_state: str
    reason_codes: tuple[str, ...]
    deterministic_evidence_preserved: bool
    explanation_used: bool
    operator_review_required: bool
    evaluated_at_utc: str
    shield_evidence_hash: str

    def __post_init__(self) -> None:
        if self.shield_state not in _SHIELD_STATES:
            raise ValueError("invalid cognitive shield state")
        if self.deterministic_evidence_preserved is not True:
            raise ValueError("deterministic evidence must remain preserved")
        if self.operator_review_required is not True:
            raise ValueError("cognitive shield evidence requires Operator review")
        if len(self.shield_evidence_hash) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.shield_evidence_hash
        ):
            raise ValueError("shield_evidence_hash must be lowercase SHA-256")


def evaluate_cognitive_shield(
    anomaly: AnomalyEvidence,
    task: CognitiveTask,
    policy: CognitiveTaskPolicy,
    advisory: RegisteredAdvisoryArtifact | None,
    *,
    as_of_utc: str,
) -> CognitiveShieldEvidence:
    if not isinstance(anomaly, AnomalyEvidence):
        raise ValueError("cognitive shield accepts AnomalyEvidence only")
    if task.policy_id != policy.policy_id or task.policy_version != policy.policy_version:
        raise ValueError("task and policy identity mismatch")
    if task.anomaly_evidence_hash != anomaly.evidence_hash:
        raise ValueError("task and anomaly evidence identity mismatch")
    evaluated_at = utc(as_of_utc, "as_of_utc")
    now = instant(evaluated_at)
    requested = instant(task.requested_at_utc)
    deadline = instant(task.deadline_at_utc)
    if now < requested:
        raise ValueError("cognitive evaluation precedes task request")
    if (deadline - requested).total_seconds() > policy.max_task_seconds:
        raise ValueError("task deadline exceeds registered policy maximum")

    shield_state = "DEGRADED"
    advisory_stance = "NOT_PROVIDED"
    confidence: Decimal | None = None
    uncertainty_state = "INSUFFICIENT_EVIDENCE"
    reasons: list[str] = []
    explanation_used = False

    if anomaly.state == "DEGRADED":
        shield_state = "BLOCKED"
        uncertainty_state = "DATA_CONFLICT"
        reasons.append("ANOMALY_EVIDENCE_DEGRADED")
    elif now > instant(anomaly.expires_at_utc):
        shield_state = "BLOCKED"
        uncertainty_state = "STATE_EXPIRED"
        reasons.append("ANOMALY_EVIDENCE_EXPIRED")
    elif advisory is None:
        reasons.extend(("ADVISORY_NOT_AVAILABLE", policy.fallback))
    elif advisory.task_id != task.task_id:
        shield_state = "BLOCKED"
        uncertainty_state = "DATA_CONFLICT"
        reasons.append("ADVISORY_TASK_MISMATCH")
    elif advisory.anomaly_evidence_hash != anomaly.evidence_hash:
        shield_state = "BLOCKED"
        uncertainty_state = "DATA_CONFLICT"
        reasons.append("ADVISORY_EVIDENCE_MISMATCH")
    elif now > deadline or instant(advisory.produced_at_utc) > deadline:
        uncertainty_state = "INSUFFICIENT_EVIDENCE"
        reasons.extend(("COGNITIVE_TIMEOUT", policy.fallback))
    else:
        advisory_stance = advisory.stance
        confidence = advisory.confidence
        if confidence < policy.minimum_advisory_confidence:
            shield_state = "ABSTAIN_REVIEW_REQUIRED"
            uncertainty_state = "LOW_CONFIDENCE"
            reasons.append("ADVISORY_CONFIDENCE_BELOW_POLICY")
        elif advisory.stance in {"ABSTAIN", "UNCERTAIN"}:
            shield_state = "ABSTAIN_REVIEW_REQUIRED"
            uncertainty_state = "ABSTAIN_REVIEW_REQUIRED"
            reasons.append(f"ADVISORY_{advisory.stance}")
        elif advisory.stance == "CONTRADICT":
            shield_state = "CONTRADICTION_REVIEW"
            uncertainty_state = "DATA_CONFLICT"
            reasons.append("ADVISORY_CONTRADICTION")
            explanation_used = True
        else:
            shield_state = "SUPPORTED_REVIEW"
            uncertainty_state = "NONE"
            reasons.append("ADVISORY_SUPPORT")
            explanation_used = True
        reasons.extend(advisory.reason_codes)

    payload = {
        "advisory_confidence": _decimal_text(confidence),
        "advisory_stance": advisory_stance,
        "anomaly_evidence_hash": anomaly.evidence_hash,
        "anomaly_state": anomaly.state,
        "deterministic_evidence_preserved": True,
        "evaluated_at_utc": evaluated_at,
        "explanation_used": explanation_used,
        "operator_review_required": True,
        "policy_id": policy.policy_id,
        "policy_version": policy.policy_version,
        "reason_codes": reasons,
        "shield_state": shield_state,
        "task_id": task.task_id,
        "uncertainty_state": uncertainty_state,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return CognitiveShieldEvidence(
        task_id=task.task_id,
        anomaly_evidence_hash=anomaly.evidence_hash,
        anomaly_state=anomaly.state,
        shield_state=shield_state,
        advisory_stance=advisory_stance,
        advisory_confidence=confidence,
        uncertainty_state=uncertainty_state,
        reason_codes=tuple(reasons),
        deterministic_evidence_preserved=True,
        explanation_used=explanation_used,
        operator_review_required=True,
        evaluated_at_utc=evaluated_at,
        shield_evidence_hash=digest,
    )
