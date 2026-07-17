from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r7_local_market_session_registry_foundation_app_1 import (
    SessionResolutionEvidence,
)

from .contracts import RegisteredBaselineObservation, SameTimeBaselinePolicy


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class SameTimeBaselineEvidence:
    baseline_id: str
    baseline_version: str
    target_session_evidence_hash: str
    state: str
    sample_count: int
    mean: Decimal | None
    median: Decimal | None
    minimum: Decimal | None
    maximum: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"BASELINE_READY", "BLOCKED"}:
            raise ValueError("invalid same-time baseline state")
        if self.operator_review_required is not True:
            raise ValueError("same-time baseline requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_same_time_baseline(
    target_session: SessionResolutionEvidence,
    policy: SameTimeBaselinePolicy,
    observations: tuple[RegisteredBaselineObservation, ...],
    *,
    as_of_utc: str,
) -> SameTimeBaselineEvidence:
    evaluated_at = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated_at)
    sample = tuple(observations)
    if not 1 <= len(sample) <= 1000:
        raise ValueError("baseline sample count is outside bounded scope")
    if len({item.observation_id for item in sample}) != len(sample):
        raise ValueError("duplicate baseline observation id is prohibited")

    reasons: list[str] = []
    state = "BLOCKED"
    mean: Decimal | None = None
    median: Decimal | None = None
    minimum: Decimal | None = None
    maximum: Decimal | None = None
    target_time = instant(target_session.observed_at_utc)
    if target_session.state != "RESOLVED":
        reasons.append("TARGET_SESSION_NOT_RESOLVED")
    elif target_session.phase != policy.phase or target_session.interval_id != policy.interval_id:
        reasons.append("TARGET_SESSION_POLICY_MISMATCH")
    elif any(instant(item.available_at_utc) > as_of for item in sample):
        reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif any(instant(item.observed_at_utc) >= target_time for item in sample):
        reasons.append("NON_HISTORICAL_OBSERVATION_BLOCKED")
    elif any(item.feature_id != policy.feature_id for item in sample):
        reasons.append("FEATURE_MISMATCH")
    elif any(item.phase != policy.phase for item in sample):
        reasons.append("SESSION_PHASE_MISMATCH")
    elif any(item.interval_id != policy.interval_id for item in sample):
        reasons.append("INTERVAL_MISMATCH")
    elif any(item.slot_index != policy.slot_index for item in sample):
        reasons.append("SLOT_MISMATCH")
    elif any(item.regime_id != policy.regime_id for item in sample):
        reasons.append("REGIME_MISMATCH")
    elif len(sample) < policy.minimum_samples:
        reasons.append("INSUFFICIENT_SAMPLE")
    else:
        values = tuple(sorted(item.value for item in sample))
        with localcontext() as context:
            context.prec = 34
            mean = sum(values, Decimal("0")) / Decimal(len(values))
            middle = len(values) // 2
            median = (
                values[middle]
                if len(values) % 2
                else (values[middle - 1] + values[middle]) / Decimal("2")
            )
            minimum = values[0]
            maximum = values[-1]
        state = "BASELINE_READY"
        reasons.append("REGISTERED_SAME_TIME_BASELINE_READY")

    payload = {
        "baseline_id": policy.baseline_id,
        "baseline_version": policy.baseline_version,
        "evaluated_at_utc": evaluated_at,
        "maximum": _decimal_text(maximum),
        "mean": _decimal_text(mean),
        "median": _decimal_text(median),
        "minimum": _decimal_text(minimum),
        "reason_codes": reasons,
        "sample_count": len(sample),
        "state": state,
        "target_session_evidence_hash": target_session.evidence_hash,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return SameTimeBaselineEvidence(
        baseline_id=policy.baseline_id,
        baseline_version=policy.baseline_version,
        target_session_evidence_hash=target_session.evidence_hash,
        state=state,
        sample_count=len(sample),
        mean=mean,
        median=median,
        minimum=minimum,
        maximum=maximum,
        reason_codes=tuple(reasons),
        evaluated_at_utc=evaluated_at,
        operator_review_required=True,
        evidence_hash=digest,
    )
