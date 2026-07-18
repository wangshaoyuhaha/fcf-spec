import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence
from apps.v2_r15_local_volatility_indicator_foundation_app_1 import (
    RegisteredOHLCPoint,
    RegisteredOHLCSeries,
)

from .contracts import DirectionalStrengthPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def _movement(previous: RegisteredOHLCPoint, current: RegisteredOHLCPoint) -> tuple[Decimal, Decimal, Decimal]:
    true_range = max(
        current.high - current.low,
        abs(current.high - previous.close),
        abs(current.low - previous.close),
    )
    upward = current.high - previous.high
    downward = previous.low - current.low
    positive = upward if upward > downward and upward > 0 else Decimal("0")
    negative = downward if downward > upward and downward > 0 else Decimal("0")
    return true_range, positive, negative


def _directional_metrics(
    smoothed_true_range: Decimal,
    smoothed_positive: Decimal,
    smoothed_negative: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    if smoothed_true_range == 0:
        return Decimal("0"), Decimal("0"), Decimal("0")
    positive_di = smoothed_positive / smoothed_true_range * Decimal("100")
    negative_di = smoothed_negative / smoothed_true_range * Decimal("100")
    total = positive_di + negative_di
    dx = (
        Decimal("0")
        if total == 0
        else abs(positive_di - negative_di) / total * Decimal("100")
    )
    return positive_di, negative_di, dx


@dataclass(frozen=True)
class DirectionalStrengthEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    required_samples: int
    sample_count: int
    positive_di: Decimal | None
    negative_di: Decimal | None
    dx: Decimal | None
    adx: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"DIRECTIONAL_STRENGTH_READY", "BLOCKED"}:
            raise ValueError("invalid directional strength evidence state")
        if self.operator_review_required is not True:
            raise ValueError("directional strength evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_directional_strength(
    series: RegisteredOHLCSeries,
    registry: FactorRegistryEvidence,
    policy: DirectionalStrengthPolicy,
    *,
    as_of_utc: str,
) -> DirectionalStrengthEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    required_samples = policy.window * 2
    reasons: list[str] = []
    positive_di = negative_di = dx = adx = None
    if registry.state != "REGISTRY_READY":
        reasons.append("REGISTRY_NOT_READY")
    elif (
        registry.registry_id != policy.registry_id
        or registry.registry_version != policy.registry_version
    ):
        reasons.append("REGISTRY_IDENTITY_MISMATCH")
    elif policy.factor_definition_ref not in registry.definition_keys:
        reasons.append("FACTOR_DEFINITION_NOT_REGISTERED")
    elif (
        series.instrument_id != policy.instrument_id
        or series.interval_id != policy.interval_id
    ):
        reasons.append("SERIES_IDENTITY_MISMATCH")
    elif any(instant(point.observed_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif any(instant(point.available_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif len(series.points) < required_samples:
        reasons.append("INSUFFICIENT_HISTORY_BLOCKED")
    else:
        movements = tuple(
            _movement(previous, current)
            for previous, current in zip(series.points, series.points[1:])
        )
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        period = Decimal(policy.window)
        with localcontext() as context:
            context.prec = 96
            initial = movements[: policy.window]
            smoothed_true_range = sum((item[0] for item in initial), Decimal("0"))
            smoothed_positive = sum((item[1] for item in initial), Decimal("0"))
            smoothed_negative = sum((item[2] for item in initial), Decimal("0"))
            raw_positive, raw_negative, raw_dx = _directional_metrics(
                smoothed_true_range, smoothed_positive, smoothed_negative
            )
            dx_values = [raw_dx]
            for true_range, positive, negative in movements[policy.window :]:
                smoothed_true_range = (
                    smoothed_true_range - smoothed_true_range / period + true_range
                )
                smoothed_positive = (
                    smoothed_positive - smoothed_positive / period + positive
                )
                smoothed_negative = (
                    smoothed_negative - smoothed_negative / period + negative
                )
                raw_positive, raw_negative, raw_dx = _directional_metrics(
                    smoothed_true_range, smoothed_positive, smoothed_negative
                )
                dx_values.append(raw_dx)
            raw_adx = sum(dx_values[: policy.window], Decimal("0")) / period
            for value in dx_values[policy.window :]:
                raw_adx = ((period - 1) * raw_adx + value) / period
            positive_di = raw_positive.quantize(quantum, rounding=ROUND_HALF_EVEN)
            negative_di = raw_negative.quantize(quantum, rounding=ROUND_HALF_EVEN)
            dx = raw_dx.quantize(quantum, rounding=ROUND_HALF_EVEN)
            adx = raw_adx.quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_DIRECTIONAL_STRENGTH_READY")
    state = (
        "DIRECTIONAL_STRENGTH_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    )
    payload = {
        "adx": _text(adx),
        "dx": _text(dx),
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "negative_di": _text(negative_di),
        "positive_di": _text(positive_di),
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "required_samples": required_samples,
        "sample_count": len(series.points),
        "series_id": series.series_id,
        "state": state,
        "window": policy.window,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return DirectionalStrengthEvidence(
        policy.indicator_id,
        policy.indicator_version,
        policy.indicator_type,
        policy.factor_definition_ref,
        series.series_id,
        state,
        policy.window,
        required_samples,
        len(series.points),
        positive_di,
        negative_di,
        dx,
        adx,
        tuple(reasons),
        evaluated,
        True,
        digest,
    )
