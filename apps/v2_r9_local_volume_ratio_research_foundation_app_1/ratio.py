from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r8_local_same_time_baseline_foundation_app_1 import (
    SameTimeBaselineEvidence,
)

from .contracts import MAX_VOLUME, RegisteredCurrentVolumeObservation, VolumeRatioPolicy


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class VolumeRatioEvidence:
    ratio_id: str
    ratio_version: str
    observation_id: str
    baseline_evidence_hash: str
    state: str
    volume_basis: str
    baseline_statistic: str
    current_volume: Decimal
    baseline_value: Decimal | None
    ratio: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"VOLUME_RATIO_READY", "BLOCKED"}:
            raise ValueError("invalid volume-ratio evidence state")
        if self.operator_review_required is not True:
            raise ValueError("volume-ratio evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_volume_ratio(
    observation: RegisteredCurrentVolumeObservation,
    baseline: SameTimeBaselineEvidence,
    policy: VolumeRatioPolicy,
    *,
    as_of_utc: str,
) -> VolumeRatioEvidence:
    evaluated_at = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated_at)
    reasons: list[str] = []
    state = "BLOCKED"
    ratio: Decimal | None = None
    baseline_value = (
        baseline.mean if policy.baseline_statistic == "MEAN" else baseline.median
    )

    if instant(observation.observed_at_utc) > as_of:
        reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif instant(observation.available_at_utc) > as_of:
        reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif instant(baseline.evaluated_at_utc) > as_of:
        reasons.append("FUTURE_BASELINE_BLOCKED")
    elif baseline.state != "BASELINE_READY":
        reasons.append("BASELINE_NOT_READY")
    elif (
        baseline.baseline_id != policy.baseline_id
        or baseline.baseline_version != policy.baseline_version
    ):
        reasons.append("BASELINE_IDENTITY_MISMATCH")
    elif baseline.target_session_evidence_hash != observation.session_evidence_hash:
        reasons.append("SESSION_EVIDENCE_MISMATCH")
    elif observation.feature_id != policy.feature_id:
        reasons.append("FEATURE_MISMATCH")
    elif observation.phase != policy.phase:
        reasons.append("SESSION_PHASE_MISMATCH")
    elif observation.interval_id != policy.interval_id:
        reasons.append("INTERVAL_MISMATCH")
    elif observation.slot_index != policy.slot_index:
        reasons.append("SLOT_MISMATCH")
    elif observation.regime_id != policy.regime_id:
        reasons.append("REGIME_MISMATCH")
    elif observation.volume_basis != policy.volume_basis:
        reasons.append("VOLUME_BASIS_MISMATCH")
    elif baseline_value is None:
        reasons.append("BASELINE_STATISTIC_UNAVAILABLE")
    elif baseline_value <= 0:
        reasons.append("ZERO_OR_NEGATIVE_BASELINE_BLOCKED")
    elif baseline_value > MAX_VOLUME:
        reasons.append("BASELINE_VALUE_OUT_OF_BOUNDS")
    else:
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            ratio = (observation.volume / baseline_value).quantize(
                quantum,
                rounding=ROUND_HALF_EVEN,
            )
        state = "VOLUME_RATIO_READY"
        reasons.append("REGISTERED_LOCAL_VOLUME_RATIO_READY")

    payload = {
        "baseline_evidence_hash": baseline.evidence_hash,
        "baseline_statistic": policy.baseline_statistic,
        "baseline_value": _decimal_text(baseline_value),
        "current_volume": _decimal_text(observation.volume),
        "evaluated_at_utc": evaluated_at,
        "observation_id": observation.observation_id,
        "ratio": _decimal_text(ratio),
        "ratio_id": policy.ratio_id,
        "ratio_version": policy.ratio_version,
        "reason_codes": reasons,
        "state": state,
        "volume_basis": policy.volume_basis,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return VolumeRatioEvidence(
        ratio_id=policy.ratio_id,
        ratio_version=policy.ratio_version,
        observation_id=observation.observation_id,
        baseline_evidence_hash=baseline.evidence_hash,
        state=state,
        volume_basis=policy.volume_basis,
        baseline_statistic=policy.baseline_statistic,
        current_volume=observation.volume,
        baseline_value=baseline_value,
        ratio=ratio,
        reason_codes=tuple(reasons),
        evaluated_at_utc=evaluated_at,
        operator_review_required=True,
        evidence_hash=digest,
    )
