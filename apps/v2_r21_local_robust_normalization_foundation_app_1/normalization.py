import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence

from .contracts import NormalizationPolicy, RegisteredFactorSeries


def _median(values: tuple[Decimal, ...]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / Decimal(2)


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class NormalizationEvidence:
    normalization_id: str
    normalization_version: str
    factor_definition_ref: str
    series_id: str
    target_point_id: str
    state: str
    missing_state: str
    available_sample_count: int
    minimum_samples: int
    median: Decimal | None
    mad: Decimal | None
    winsorized_value: Decimal | None
    robust_z_score: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str


def build_normalization(series: RegisteredFactorSeries, registry: FactorRegistryEvidence, policy: NormalizationPolicy, *, as_of_utc: str) -> NormalizationEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    target = next((point for point in series.points if point.point_id == policy.target_point_id), None)
    available = tuple(point.value for point in series.points if point.missing_state == "AVAILABLE" and point.value is not None)
    reasons: list[str] = []
    median = mad = winsorized = robust_z = None
    missing_state = target.missing_state if target is not None else "MISSING"
    if registry.state != "REGISTRY_READY": reasons.append("REGISTRY_NOT_READY")
    elif registry.registry_id != policy.registry_id or registry.registry_version != policy.registry_version: reasons.append("REGISTRY_IDENTITY_MISMATCH")
    elif policy.factor_definition_ref not in registry.definition_keys: reasons.append("FACTOR_DEFINITION_NOT_REGISTERED")
    elif series.factor_definition_ref != policy.factor_definition_ref: reasons.append("SERIES_FACTOR_MISMATCH")
    elif target is None: reasons.append("TARGET_POINT_NOT_REGISTERED")
    elif any(instant(point.observed_at_utc) > as_of for point in series.points): reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif any(instant(point.available_at_utc) > as_of for point in series.points): reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif target.missing_state != "AVAILABLE": reasons.append(f"TARGET_{target.missing_state}")
    elif len(available) < policy.minimum_samples: reasons.append("INSUFFICIENT_AVAILABLE_SAMPLES")
    else:
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            raw_median = _median(available)
            raw_mad = _median(tuple(abs(value - raw_median) for value in available))
            lower = raw_median - policy.mad_clip_multiplier * raw_mad
            upper = raw_median + policy.mad_clip_multiplier * raw_mad
            raw_winsorized = min(max(target.value, lower), upper)  # type: ignore[arg-type]
            raw_robust_z = Decimal(0) if raw_mad == 0 else (raw_winsorized - raw_median) / raw_mad
            median = raw_median.quantize(quantum, rounding=ROUND_HALF_EVEN)
            mad = raw_mad.quantize(quantum, rounding=ROUND_HALF_EVEN)
            winsorized = raw_winsorized.quantize(quantum, rounding=ROUND_HALF_EVEN)
            robust_z = raw_robust_z.quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_ROBUST_NORMALIZATION_READY")
    state = "NORMALIZATION_READY" if reasons[-1].endswith("READY") else ("MISSING_STATE_RECORDED" if reasons[-1].startswith("TARGET_") and reasons[-1] != "TARGET_POINT_NOT_REGISTERED" else "BLOCKED")
    payload = {"available_sample_count": len(available), "evaluated_at_utc": evaluated, "factor_definition_ref": policy.factor_definition_ref, "mad": _text(mad), "median": _text(median), "minimum_samples": policy.minimum_samples, "missing_state": missing_state, "normalization_id": policy.normalization_id, "normalization_version": policy.normalization_version, "reason_codes": reasons, "registry_evidence_hash": registry.evidence_hash, "robust_z_score": _text(robust_z), "series_id": series.series_id, "state": state, "target_point_id": policy.target_point_id, "winsorized_value": _text(winsorized)}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return NormalizationEvidence(policy.normalization_id, policy.normalization_version, policy.factor_definition_ref, series.series_id, policy.target_point_id, state, missing_state, len(available), policy.minimum_samples, median, mad, winsorized, robust_z, tuple(reasons), evaluated, True, digest)
