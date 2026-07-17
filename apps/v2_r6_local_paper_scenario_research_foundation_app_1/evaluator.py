from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r4_local_anomaly_radar_foundation_app_1 import AnomalyEvidence
from apps.v2_r5_local_cognitive_shield_foundation_app_1 import CognitiveShieldEvidence

from .contracts import PaperScenarioPolicy, RegisteredObservationPoint


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class PaperScenarioEvidence:
    scenario_id: str
    scenario_version: str
    anomaly_evidence_hash: str
    shield_evidence_hash: str
    state: str
    outcome: str
    raw_path_return: Decimal | None
    aligned_research_return: Decimal | None
    cost_adjusted_return: Decimal | None
    maximum_favorable_movement: Decimal | None
    maximum_adverse_movement: Decimal | None
    point_count: int
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"EVALUATED", "BLOCKED"}:
            raise ValueError("invalid Paper scenario evidence state")
        if self.operator_review_required is not True:
            raise ValueError("Paper scenario evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def evaluate_paper_scenario(
    anomaly: AnomalyEvidence,
    shield: CognitiveShieldEvidence,
    policy: PaperScenarioPolicy,
    points: tuple[RegisteredObservationPoint, ...],
    *,
    as_of_utc: str,
) -> PaperScenarioEvidence:
    if shield.anomaly_evidence_hash != anomaly.evidence_hash:
        raise ValueError("shield and anomaly evidence identity mismatch")
    path = tuple(points)
    if len(path) < policy.minimum_points or len(path) > 1000:
        raise ValueError("observation path does not meet bounded point policy")
    for previous, current in zip(path, path[1:]):
        if current.sequence != previous.sequence + 1:
            raise ValueError("observation path sequence must be contiguous")
        if instant(current.observed_at_utc) <= instant(previous.observed_at_utc):
            raise ValueError("observation time must increase")
    evaluated_at = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated_at)
    if any(instant(point.available_at_utc) > as_of for point in path):
        raise ValueError("observation path contains unavailable future evidence")
    anomaly_time = instant(anomaly.observed_at_utc)
    if instant(path[0].observed_at_utc) < anomaly_time:
        raise ValueError("observation path begins before anomaly evidence")
    elapsed = (instant(path[-1].observed_at_utc) - anomaly_time).total_seconds()
    if elapsed > policy.horizon_seconds:
        raise ValueError("observation path exceeds registered horizon")

    state = "BLOCKED"
    outcome = "NOT_EVALUATED"
    raw_return: Decimal | None = None
    aligned_return: Decimal | None = None
    adjusted_return: Decimal | None = None
    favorable: Decimal | None = None
    adverse: Decimal | None = None
    reasons: list[str] = []

    if anomaly.state == "DEGRADED":
        reasons.append("ANOMALY_EVIDENCE_DEGRADED")
    elif shield.shield_state in {"BLOCKED", "DEGRADED", "ABSTAIN_REVIEW_REQUIRED"}:
        reasons.append(f"SHIELD_{shield.shield_state}")
    else:
        with localcontext() as context:
            context.prec = 34
            reference = path[0].price
            returns = tuple((point.price - reference) / reference for point in path)
            raw_return = returns[-1]
            direction = Decimal("1") if policy.research_direction == "UP" else Decimal("-1")
            aligned = tuple(value * direction for value in returns)
            aligned_return = aligned[-1]
            adjusted_return = aligned_return - policy.cost_assumption_bps / Decimal("10000")
            favorable = max(Decimal("0"), max(aligned))
            adverse = max(Decimal("0"), -min(aligned))
        state = "EVALUATED"
        outcome = (
            "POSITIVE_OBSERVATION"
            if adjusted_return > 0
            else "NEGATIVE_OBSERVATION"
            if adjusted_return < 0
            else "NEUTRAL_OBSERVATION"
        )
        reasons.append("REGISTERED_PATH_EVALUATED")

    payload = {
        "aligned_research_return": _decimal_text(aligned_return),
        "anomaly_evidence_hash": anomaly.evidence_hash,
        "cost_adjusted_return": _decimal_text(adjusted_return),
        "evaluated_at_utc": evaluated_at,
        "maximum_adverse_movement": _decimal_text(adverse),
        "maximum_favorable_movement": _decimal_text(favorable),
        "outcome": outcome,
        "point_count": len(path),
        "raw_path_return": _decimal_text(raw_return),
        "reason_codes": reasons,
        "scenario_id": policy.scenario_id,
        "scenario_version": policy.scenario_version,
        "shield_evidence_hash": shield.shield_evidence_hash,
        "state": state,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return PaperScenarioEvidence(
        scenario_id=policy.scenario_id,
        scenario_version=policy.scenario_version,
        anomaly_evidence_hash=anomaly.evidence_hash,
        shield_evidence_hash=shield.shield_evidence_hash,
        state=state,
        outcome=outcome,
        raw_path_return=raw_return,
        aligned_research_return=aligned_return,
        cost_adjusted_return=adjusted_return,
        maximum_favorable_movement=favorable,
        maximum_adverse_movement=adverse,
        point_count=len(path),
        reason_codes=tuple(reasons),
        evaluated_at_utc=evaluated_at,
        operator_review_required=True,
        evidence_hash=digest,
    )
