import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence

from .contracts import RegisteredOHLCSeries, VolatilityIndicatorPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def _true_ranges(series: RegisteredOHLCSeries) -> tuple[Decimal, ...]:
    result: list[Decimal] = []
    previous_close: Decimal | None = None
    for point in series.points:
        candidates = [point.high - point.low]
        if previous_close is not None:
            candidates.extend(
                (abs(point.high - previous_close), abs(point.low - previous_close))
            )
        result.append(max(candidates))
        previous_close = point.close
    return tuple(result)


@dataclass(frozen=True)
class VolatilityIndicatorEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    required_samples: int
    sample_count: int
    true_range: Decimal | None
    average_true_range: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"VOLATILITY_READY", "BLOCKED"}:
            raise ValueError("invalid volatility indicator evidence state")
        if self.operator_review_required is not True:
            raise ValueError("volatility evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_volatility_indicator(
    series: RegisteredOHLCSeries,
    registry: FactorRegistryEvidence,
    policy: VolatilityIndicatorPolicy,
    *,
    as_of_utc: str,
) -> VolatilityIndicatorEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    true_range = average_true_range = None
    required_samples = 1 if policy.indicator_type == "TRUE_RANGE" else policy.window
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
        reasons.append("INSUFFICIENT_WINDOW_BLOCKED")
    else:
        ranges = _true_ranges(series)
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            if policy.indicator_type == "TRUE_RANGE":
                true_range = ranges[-1].quantize(quantum, rounding=ROUND_HALF_EVEN)
            else:
                raw_atr = sum(ranges[: policy.window], Decimal("0")) / Decimal(
                    policy.window
                )
                for value in ranges[policy.window :]:
                    raw_atr = (
                        raw_atr * Decimal(policy.window - 1) + value
                    ) / Decimal(policy.window)
                average_true_range = raw_atr.quantize(
                    quantum, rounding=ROUND_HALF_EVEN
                )
        reasons.append("REGISTERED_LOCAL_VOLATILITY_INDICATOR_READY")
    state = "VOLATILITY_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {
        "average_true_range": _text(average_true_range),
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "required_samples": required_samples,
        "sample_count": len(series.points),
        "series_id": series.series_id,
        "state": state,
        "true_range": _text(true_range),
        "window": policy.window,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return VolatilityIndicatorEvidence(
        policy.indicator_id,
        policy.indicator_version,
        policy.indicator_type,
        policy.factor_definition_ref,
        series.series_id,
        state,
        policy.window,
        required_samples,
        len(series.points),
        true_range,
        average_true_range,
        tuple(reasons),
        evaluated,
        True,
        digest,
    )
